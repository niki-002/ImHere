from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError, PyJWKClientError
from pwdlib import PasswordHash
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..core.config import get_settings
from ..db import get_db
from ..models import OAuthAccount, User, utc_now
from ..schemas import auth as auth_schema


settings = get_settings()
password_hasher = PasswordHash.recommended()
bearer_scheme = HTTPBearer(auto_error=False)
_jwk_clients: dict[str, PyJWKClient] = {}


def normalize_email(email: str | None) -> str | None:
    if email is None:
        return None
    normalized = email.strip().lower()
    return normalized or None


def normalize_username(username: str) -> str:
    return username.strip().lower()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hasher.verify(password, hashed_password)


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "typ": "access",
    }
    return jwt.encode(
        payload,
        settings.secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def user_to_login_response(user: User) -> auth_schema.LoginUserResponse:
    return auth_schema.LoginUserResponse(
        id=user.id,
        username=user.username,
        name=user.display_name,
        display_name=user.display_name,
        email=user.email,
        status=user.current_status,
        status_updated_at=user.status_updated_at,
    )


def build_login_token_response(user: User) -> auth_schema.LoginTokenResponse:
    return auth_schema.LoginTokenResponse(
        access_token=create_access_token(user.id),
        user=user_to_login_response(user),
    )


def get_user_by_email(db: Session, email: str | None) -> User | None:
    normalized = normalize_email(email)
    if normalized is None:
        return None
    return db.scalar(select(User).where(User.email == normalized))


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == normalize_username(username)))


def register_login_user(
    db: Session,
    payload: auth_schema.LoginRegister,
) -> auth_schema.LoginTokenResponse:
    email = normalize_email(payload.email)
    username = normalize_username(payload.username)
    display_name = (payload.display_name or payload.username).strip()

    if get_user_by_email(db, email) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このメールアドレスはすでに使われています",
        )

    if get_user_by_username(db, username) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このユーザー名はすでに使われています",
        )

    user = User(
        username=username,
        display_name=display_name,
        email=email,
        password_hash=hash_password(payload.password),
        current_status="ok",
        status_updated_at=utc_now(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return build_login_token_response(user)


def login_user(
    db: Session,
    payload: auth_schema.LoginRequest,
) -> auth_schema.LoginTokenResponse:
    user = get_user_by_email(db, payload.email)

    if (
        user is None
        or user.password_hash is None
        or not verify_password(payload.password, user.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが違います",
        )

    return build_login_token_response(user)


def _oauth_client(provider: auth_schema.OAuthProvider) -> PyJWKClient:
    if provider not in _jwk_clients:
        jwks_url = (
            settings.google_jwks_url
            if provider == "google"
            else settings.apple_jwks_url
        )
        if jwks_url is None:
            env_name = (
                "GOOGLE_JWKS_URL"
                if provider == "google"
                else "APPLE_JWKS_URL"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"{env_name} が設定されていません",
            )
        _jwk_clients[provider] = PyJWKClient(jwks_url)
    return _jwk_clients[provider]


def _provider_client_ids(provider: auth_schema.OAuthProvider) -> list[str]:
    if provider == "google":
        return settings.google_client_ids
    return settings.apple_client_ids


def verify_oauth_id_token(
    provider: auth_schema.OAuthProvider,
    id_token: str,
) -> dict[str, Any]:
    client_ids = _provider_client_ids(provider)
    if not client_ids:
        env_name = (
            "GOOGLE_CLIENT_IDS"
            if provider == "google"
            else "APPLE_CLIENT_IDS"
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{env_name} が設定されていません",
        )

    issuers = (
        {"https://accounts.google.com", "accounts.google.com"}
        if provider == "google"
        else {"https://appleid.apple.com"}
    )

    try:
        signing_key = _oauth_client(provider).get_signing_key_from_jwt(id_token)
        claims = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=client_ids,
            options={"verify_iss": False},
        )
    except (InvalidTokenError, PyJWKClientError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OAuth認証情報が不正です",
        ) from exc

    if claims.get("iss") not in issuers:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OAuth発行元が不正です",
        )

    if not claims.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OAuthユーザーIDが取得できません",
        )

    return claims


def _oauth_email_verified(claims: dict[str, Any]) -> bool:
    verified = claims.get("email_verified")
    if isinstance(verified, bool):
        return verified
    if isinstance(verified, str):
        return verified.lower() == "true"
    return False


def _unique_username(db: Session, preferred: str) -> str:
    base = normalize_username(preferred).replace(" ", "")
    if not base:
        base = "user"

    candidate = base[:50]
    suffix = 1
    while get_user_by_username(db, candidate) is not None:
        suffix_text = str(suffix)
        candidate = f"{base[: 50 - len(suffix_text)]}{suffix_text}"
        suffix += 1

    return candidate


def login_with_oauth(
    db: Session,
    provider: auth_schema.OAuthProvider,
    payload: auth_schema.OAuthLoginRequest,
) -> auth_schema.LoginTokenResponse:
    claims = verify_oauth_id_token(provider, payload.id_token)
    provider_user_id = str(claims["sub"])
    email = normalize_email(claims.get("email"))
    if email is not None and not _oauth_email_verified(claims):
        email = None

    account = db.scalar(
        select(OAuthAccount).where(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_user_id == provider_user_id,
        )
    )
    if account is not None:
        return build_login_token_response(account.user)

    user = get_user_by_email(db, email)
    if user is None:
        preferred_username = (
            payload.username
            or claims.get("preferred_username")
            or (email.split("@", 1)[0] if email else None)
            or f"{provider}_{provider_user_id[:8]}"
        )
        display_name = (
            payload.display_name
            or claims.get("name")
            or preferred_username
        )
        user = User(
            username=_unique_username(db, str(preferred_username)),
            display_name=str(display_name).strip()[:100],
            email=email,
            password_hash=None,
            current_status="ok",
            status_updated_at=utc_now(),
        )
        db.add(user)
        db.flush()

    account = OAuthAccount(
        user_id=user.id,
        provider=provider,
        provider_user_id=provider_user_id,
        email=email,
    )
    db.add(account)
    db.commit()
    db.refresh(user)

    return build_login_token_response(user)


def extract_access_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    if credentials and credentials.scheme.lower() == "bearer":
        return credentials.credentials

    for cookie_name in ("access_token", "login_token"):
        cookie_token = request.cookies.get(cookie_name)
        if cookie_token:
            return cookie_token

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="ログインが必要です",
    )


def get_user_from_token(db: Session, token: str) -> User:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
        )
        user_id = int(payload["sub"])
        if payload.get("typ") != "access":
            raise InvalidTokenError("invalid token type")
    except (InvalidTokenError, KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証情報が不正です",
        ) from exc

    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザーが存在しません",
        )
    return user


def get_current_login_user(
    token: str = Depends(extract_access_token),
    db: Session = Depends(get_db),
) -> User:
    return get_user_from_token(db, token)


def search_users_by_name(db: Session, name_query: str) -> list[User]:
    query = f"%{name_query.strip()}%"
    return list(
        db.scalars(
            select(User)
            .where(or_(User.username.ilike(query), User.display_name.ilike(query)))
            .order_by(User.username)
            .limit(20)
        )
    )
