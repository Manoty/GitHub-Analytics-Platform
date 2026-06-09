# backend/app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "GitHub Analytics Platform"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    secret_key: str = "change-me-in-production"

    # Database
    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_db: str = "github_analytics"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/github_analytics"
    database_url_sync: str = "postgresql+psycopg2://postgres:postgres@db:5432/github_analytics"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # GitHub OAuth
    github_client_id: str = ""
    github_client_secret: str = ""
    github_redirect_uri: str = "http://localhost:8000/api/v1/auth/callback"
    github_api_base_url: str = "https://api.github.com"

    # JWT
    jwt_secret_key: str = "change-me-jwt-secret"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 30

    # Frontend
    frontend_url: str = "http://localhost:5173"

    # Celery
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"

    # DuckDB
    duckdb_path: str = "/app/analytics/warehouse.duckdb"

    # Rate Limiting
    rate_limit_per_minute: int = 60

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()