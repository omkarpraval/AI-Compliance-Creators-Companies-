from functools import lru_cache
from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # --- App Environment ---
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # --- Database (PostgreSQL 16) ---
    DATABASE_URL: str = "postgresql+asyncpg://verifyd:verifyd@localhost:5432/verifyd"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DB_ECHO: bool = False

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError(
                f"DATABASE_URL must start with 'postgresql+asyncpg://', got: {v}. "
                "Verifyd requires PostgreSQL 16 with asyncpg driver."
            )
        return v

    # --- Redis & Celery ---
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # --- Security & Auth ---
    SECRET_KEY: str = "verifyd-dev-secret-key-change-in-production-2026-very-secure"
    FERNET_KEY: str = "z06nK9H_jG4yX9-J0s7b1Y5qN7P1l6G4yX9-J0s7b1Y="
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # --- Storage ---
    STORAGE_BACKEND: str = "local"  # 'local' | 's3'
    STORAGE_LOCAL_DIR: str = "./storage_data"
    S3_ENDPOINT_URL: Optional[str] = "http://localhost:9000"
    S3_ACCESS_KEY: Optional[str] = "minioadmin"
    S3_SECRET_KEY: Optional[str] = "minioadmin"
    S3_BUCKET: str = "verifyd-media"
    S3_REGION: str = "us-east-1"

    # --- Hosted AI Providers ---
    GEMINI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    BHASHINI_API_KEY: Optional[str] = None
    BHASHINI_USER_ID: Optional[str] = None

    # --- Verification & Pipeline Defaults ---
    DEFAULT_CONFIDENCE_THRESHOLD: float = 0.75
    MAX_VIDEO_DURATION_SECONDS: int = 600
    MAX_FILE_SIZE_MB: int = 500


@lru_cache()
def get_settings() -> Settings:
    return Settings()
