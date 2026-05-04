from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import yaml
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "DropAI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # Database — Render provides postgres:// which needs converting for asyncpg
    DATABASE_URL: str = "postgresql+asyncpg://dropai:dropai_pass@localhost:5432/dropai_db"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_db_url(cls, v: str) -> str:
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        if v.startswith("postgresql://") and "+asyncpg" not in v:
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    # JWT
    SECRET_KEY: str = "change-this-super-secret-key-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS — accepts JSON array string from env var or a plain list
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://app.dropai.io",
    ]

    # Google Maps
    GOOGLE_MAPS_API_KEY: str = ""

    # WhatsApp (Twilio)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_FROM: str = "whatsapp:+14155238886"

    # Email (SendGrid)
    SENDGRID_API_KEY: str = ""
    EMAIL_FROM: str = "noreply@dropai.io"

    # Redis (optional — not required for core functionality)
    REDIS_URL: str = "redis://localhost:6379"

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


def load_api_config() -> dict:
    config_path = os.path.join(os.path.dirname(__file__), "../../config/apis.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}


api_config = load_api_config()
