from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings(BaseSettings):
    app_name: str
    app_env: str

    database_url: str
    test_database_url: str | None = None

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int = 60 * 24 * 7

    cors_origins: str
    frontend_url: str
    
    google_client_ids: str = ""
    google_jwks_url: str
    apple_client_ids: str = ""
    apple_jwks_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("database_url")
    @classmethod
    def normalize_postgres_url(cls, value: str) -> str:
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg2://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg2://", 1)
        if value.startswith("postgresql+psycopg2://"):
            return value
        raise ValueError("DATABASE_URL must be PostgreSQL.")

    @property
    def cors_origin_list(self) -> list[str]:
        return _csv(self.cors_origins)

    @property
    def google_client_id_list(self) -> list[str]:
        return _csv(self.google_client_ids)

    @property
    def apple_client_id_list(self) -> list[str]:
        return _csv(self.apple_client_ids)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
