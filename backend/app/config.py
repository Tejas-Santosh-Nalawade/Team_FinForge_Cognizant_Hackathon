import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


LOCAL_DATABASE_PATH = Path(__file__).resolve().parents[1] / "finforge_audit.db"


class Settings(BaseSettings):
    APP_NAME: str = "Apex Global Technologies Inc. - FP&A & Audit Assurance Suite"
    APP_VERSION: str = "3.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # API Prefix
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = f"sqlite:///{LOCAL_DATABASE_PATH.as_posix()}"

    # Local JWT authentication. Override the defaults outside of local demos.
    JWT_SECRET_KEY: str = "change-this-development-key-before-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    DEMO_USER_EMAIL: str = "auditor@apexglobal.com"
    DEMO_USER_PASSWORD: str = "FinForge!2026"

    # Cloudflare R2 Storage (S3 compatible)
    R2_ACCOUNT_ID: Optional[str] = None
    R2_ACCESS_KEY_ID: Optional[str] = None
    R2_SECRET_ACCESS_KEY: Optional[str] = None
    R2_BUCKET_NAME: str = "finforge-audit-vault"
    R2_ENDPOINT_URL: Optional[str] = None
    R2_PUBLIC_URL: Optional[str] = None

    # Google Gemini AI Studio
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-pro"

    # Qdrant Vector Search
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "regulatory_corpus"

    # Materiality & Threshold Defaults
    DEFAULT_OVERALL_MATERIALITY: float = 440000.0
    DEFAULT_PERFORMANCE_MATERIALITY: float = 330000.0
    DEFAULT_TRIVIAL_THRESHOLD: float = 22000.0
    DEFAULT_LIQUIDITY_RUNWAY_MONTHS_THRESHOLD: float = 12.0

    # Local Artifact Directory fallback
    LOCAL_STORAGE_DIR: str = "./result"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

# Older local .env files used a repository-root SQLite path that may be
# checked in read-only. Preserve all custom URLs, but transparently route that
# exact legacy default to the writable backend-local development database.
if settings.DATABASE_URL == "sqlite:///./finforge_audit.db":
    settings.DATABASE_URL = f"sqlite:///{LOCAL_DATABASE_PATH.as_posix()}"
