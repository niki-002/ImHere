import os
from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv
from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    field_validator,
    model_validator,
)


load_dotenv()


JwtAlgorithm = Literal["HS256", "HS384", "HS512"]


def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings(BaseModel):
    app_name: str = Field(default="ImHere API", validation_alias="APP_NAME")
    app_env: str = Field(default="development", validation_alias="APP_ENV")
    database_url: str = Field(validation_alias="DATABASE_URL")
    secret_key: SecretStr = Field(validation_alias="SECRET_KEY")
    jwt_algorithm: JwtAlgorithm = Field(
        default="HS256",
        validation_alias=AliasChoices("JWT_ALGORITHM", "ALGORITHM"),
    )
    access_token_expire_minutes: int = Field(
        default=60 * 24 * 7,
        gt=0,
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    cors_origins: list[str] = Field(
        default_factory=list,
        validation_alias="CORS_ORIGINS",
    )
    frontend_url: str | None = Field(default=None, validation_alias="FRONTEND_URL")
    google_client_ids: list[str] = Field(
        default_factory=list,
        validation_alias="GOOGLE_CLIENT_IDS",
    )
    apple_client_ids: list[str] = Field(
        default_factory=list,
        validation_alias="APPLE_CLIENT_IDS",
    )
    google_jwks_url: str | None = Field(
        default=None,
        validation_alias="GOOGLE_JWKS_URL",
    )
    apple_jwks_url: str | None = Field(
        default=None,
        validation_alias="APPLE_JWKS_URL",
    )

    model_config = ConfigDict(extra="ignore")

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: object) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("DATABASE_URL is required")

        database_url = value.strip()
        if database_url.startswith("postgres://"):
            return database_url.replace("postgres://", "postgresql+psycopg2://", 1)
        if database_url.startswith("postgresql://"):
            return database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        if database_url.startswith(
            ("postgresql+psycopg2://", "sqlite://", "sqlite+pysqlite://")
        ):
            return database_url

        raise ValueError("DATABASE_URL must be a PostgreSQL or SQLite URL")

    @field_validator(
        "cors_origins",
        "google_client_ids",
        "apple_client_ids",
        mode="before",
    )
    @classmethod
    def parse_csv_list(cls, value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return _csv(value)
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        raise ValueError("value must be a comma separated string")

    @field_validator(
        "frontend_url",
        "google_jwks_url",
        "apple_jwks_url",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, value: object) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("value must be a string")

        stripped = value.strip()
        return stripped.rstrip("/") if stripped else None

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        if "*" in self.cors_origins:
            raise ValueError(
                "CORS_ORIGINS cannot contain '*' when credentials are enabled"
            )

        for jwks_url in (self.google_jwks_url, self.apple_jwks_url):
            if jwks_url is not None and not jwks_url.startswith("https://"):
                raise ValueError("OAuth JWKS URLs must use HTTPS")

        if self.google_client_ids and self.google_jwks_url is None:
            raise ValueError(
                "GOOGLE_JWKS_URL is required when GOOGLE_CLIENT_IDS is set"
            )
        if self.apple_client_ids and self.apple_jwks_url is None:
            raise ValueError("APPLE_JWKS_URL is required when APPLE_CLIENT_IDS is set")

        if self.app_env.lower() == "production":
            secret_length = len(self.secret_key.get_secret_value())
            if secret_length < 32:
                raise ValueError(
                    "SECRET_KEY must be at least 32 characters in production"
                )
            if self.database_url.startswith("sqlite"):
                raise ValueError("SQLite must not be used as the production database")
            if self.frontend_url is not None and not self.frontend_url.startswith(
                "https://"
            ):
                raise ValueError("FRONTEND_URL must use HTTPS in production")
            insecure_origins = [
                origin
                for origin in self.cors_origins
                if not origin.startswith("https://")
            ]
            if insecure_origins:
                raise ValueError("CORS_ORIGINS must use HTTPS in production")

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings.model_validate(dict(os.environ))
