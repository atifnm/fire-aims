"""
FIRE-AIMS Configuration
Reads settings from environment variables (.env file). See .env.example.
"""
import os
from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "FIRE-AIMS"
    ENV: str = os.getenv("ENV", "development")

    # Database - defaults to local SQLite file for zero-config local runs.
    # For production, set DATABASE_URL to a PostgreSQL DSN, e.g.:
    # postgresql+psycopg2://fireaims:fireaims@db:5432/fireaims
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/fireaims.db")

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE_ME_IN_PRODUCTION_super_secret_key_fireaims")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

    # File storage
    STATIC_DIR: str = str(BASE_DIR / "static")
    UPLOAD_DIR: str = str(BASE_DIR / "static" / "uploads")
    QR_DIR: str = str(BASE_DIR / "static" / "qr")
    MAX_UPLOAD_SIZE_MB: int = 8
    ALLOWED_IMAGE_TYPES: tuple = ("image/jpeg", "image/png", "image/webp", "image/gif")

    # Business rule defaults (also configurable per-org via Settings table at runtime)
    DEFAULT_DUE_SOON_DAYS: int = 30
    DEFAULT_EXTINGUISHER_INSPECTION_INTERVAL_DAYS: int = 30
    DEFAULT_EXTINGUISHER_SERVICE_INTERVAL_DAYS: int = 365
    DEFAULT_HOSE_CABINET_INSPECTION_INTERVAL_DAYS: int = 90
    DEFAULT_MCP_TEST_INTERVAL_DAYS: int = 180

    # CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000", "*"]

    class Config:
        env_file = ".env"


settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.QR_DIR, exist_ok=True)
