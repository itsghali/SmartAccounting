from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "EasyAccounting"
    DEBUG: bool = False
    VERSION: str = "0.1.0"

    # Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://easy_app:easy_app@localhost:5432/easyaccounting"
    )
    AUTH_DATABASE_URL: str = (
        "postgresql+asyncpg://easy_auth:easy_auth@localhost:5432/easyaccounting"
    )
    ALEMBIC_DATABASE_URL: str = (
        "postgresql+asyncpg://easy_owner:easy_owner@localhost:5432/easyaccounting"
    )
    DATABASE_ECHO: bool = False

    # Auth / JWT
    SECRET_KEY: str = "CHANGE-ME-IN-PRODUCTION-USE-OPENSSL-RAND"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # MinIO / S3
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "easyaccounting"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
