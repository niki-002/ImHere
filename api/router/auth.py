from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User
from ..schemas import auth as schema
from ..service import auth as service


router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=schema.LoginTokenResponse)
@router.post("/login/register", response_model=schema.LoginTokenResponse, include_in_schema=False)
def register(
    payload: schema.LoginRegister,
    db: Session = Depends(get_db),
) -> schema.LoginTokenResponse:
    return service.register_login_user(db, payload)


@router.post("/auth/login", response_model=schema.LoginTokenResponse)
@router.post("/login", response_model=schema.LoginTokenResponse, include_in_schema=False)
def login(
    payload: schema.LoginRequest,
    db: Session = Depends(get_db),
) -> schema.LoginTokenResponse:
    return service.login_user(db, payload)


@router.post("/auth/oauth/{provider}", response_model=schema.LoginTokenResponse)
def oauth_login(
    provider: schema.OAuthProvider,
    payload: schema.OAuthLoginRequest,
    db: Session = Depends(get_db),
) -> schema.LoginTokenResponse:
    return service.login_with_oauth(db, provider, payload)


@router.post("/auth/google", response_model=schema.LoginTokenResponse)
def google_login(
    payload: schema.OAuthLoginRequest,
    db: Session = Depends(get_db),
) -> schema.LoginTokenResponse:
    return service.login_with_oauth(db, "google", payload)


@router.post("/auth/apple", response_model=schema.LoginTokenResponse)
def apple_login(
    payload: schema.OAuthLoginRequest,
    db: Session = Depends(get_db),
) -> schema.LoginTokenResponse:
    return service.login_with_oauth(db, "apple", payload)


@router.get("/auth/me", response_model=schema.LoginUserResponse)
@router.get("/login/me", response_model=schema.LoginUserResponse, include_in_schema=False)
def read_current_login_user(
    current_user: User = Depends(service.get_current_login_user),
) -> schema.LoginUserResponse:
    return service.user_to_login_response(current_user)
