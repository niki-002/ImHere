import os
import sys
from collections.abc import Generator
from pathlib import Path
from uuid import uuid4

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env", override=False)

database_url = os.environ.get("TEST_DATABASE_URL")
if not database_url:
    raise RuntimeError(
        "ImHere/.env に TEST_DATABASE_URL を設定してください。"
    )

os.environ["DATABASE_URL"] = database_url


def _set_default_env(key: str, value: str) -> None:
    if not os.environ.get(key):
        os.environ[key] = value


_set_default_env("APP_NAME", "ImHere Test")
_set_default_env("APP_ENV", "test")
_set_default_env("SECRET_KEY", "test-secret-key")
_set_default_env("ALGORITHM", "HS256")
_set_default_env("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
_set_default_env("CORS_ORIGINS", "http://localhost:3000")
_set_default_env("FRONTEND_URL", "http://localhost:3000")
_set_default_env("GOOGLE_CLIENT_IDS", "")
_set_default_env("GOOGLE_JWKS_URL", "https://example.com/google/jwks")
_set_default_env("APPLE_CLIENT_IDS", "")
_set_default_env("APPLE_JWKS_URL", "https://example.com/apple/jwks")

from api.core.config import get_settings  # noqa: E402
from api.db import get_db  # noqa: E402
from api.main import create_app  # noqa: E402
from api.models import Base  # noqa: E402


engine = create_engine(
    get_settings().database_url,
    pool_pre_ping=True,
)


@pytest.fixture(scope="session", autouse=True)
def prepare_database() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def db_connection() -> Generator[Connection, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    try:
        yield connection
    finally:
        transaction.rollback()
        connection.close()


@pytest.fixture(autouse=True)
def fast_password_hashing(monkeypatch: pytest.MonkeyPatch) -> None:
    from api.service import auth as auth_service

    monkeypatch.setattr(
        auth_service,
        "hash_password",
        lambda password: f"test-hash:{password}",
    )
    monkeypatch.setattr(
        auth_service,
        "verify_password",
        lambda password, hashed_password: hashed_password == f"test-hash:{password}",
    )


@pytest.fixture
def client(db_connection: Connection) -> Generator[TestClient, None, None]:
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        db = Session(
            bind=db_connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def register_user(client: TestClient):
    def _register_user(
        username: str,
        email: str | None = None,
        password: str = "password123",
        display_name: str | None = None,
    ) -> dict:
        payload = {
            "username": username,
            "email": email or f"{username}@example.com",
            "password": password,
        }
        if display_name is not None:
            payload["displayName"] = display_name

        response = client.post("/auth/register", json=payload)
        assert response.status_code == 200, response.text
        return response.json()

    return _register_user


@pytest.fixture
def auth_headers():
    def _auth_headers(token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    return _auth_headers


@pytest.fixture
def unique_username():
    def _unique_username(prefix: str = "user") -> str:
        return f"{prefix}_{uuid4().hex[:12]}".lower()

    return _unique_username


@pytest.fixture
def create_group(client: TestClient, auth_headers):
    def _create_group(
        token: str,
        name: str = "Family",
        emoji: str = "home",
        color: str = "bg-blue-50",
    ) -> dict:
        response = client.post(
            "/groups",
            headers=auth_headers(token),
            json={"name": name, "emoji": emoji, "color": color},
        )
        assert response.status_code == 200, response.text
        return response.json()

    return _create_group
