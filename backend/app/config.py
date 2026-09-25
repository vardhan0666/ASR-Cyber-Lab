"""
Centralized application configuration.

All configuration is sourced from environment variables (or a local .env
file during development). No secrets are hard-coded. The application will
fail to start if required security-critical settings are missing or weak.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # --- General ---
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # --- Database ---
    DATABASE_URL: str = (
        "postgresql+psycopg2://asr_user:asr_password@localhost:5432/asr_cyber_lab"
    )

    # --- Security ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:5173"

    # --- Nmap ---
    NMAP_PATH: str = "nmap"
    NMAP_TIMEOUT_SECONDS: int = 600

    # --- AI (optional assistance only, never source of truth) ---
    AI_ENABLED: bool = False
    AI_PROVIDER: str = "none"
    AI_API_KEY: str = ""

    # --- Initial admin bootstrap (optional) ---
    # If both email and password are set AND the users table is empty at
    # startup, an initial administrator account is created automatically.
    # Leaving these unset disables the bootstrap entirely.
    INITIAL_ADMIN_EMAIL: Optional[str] = None
    INITIAL_ADMIN_PASSWORD: Optional[str] = None
    INITIAL_ADMIN_FULL_NAME: str = "Administrator"

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_be_strong(cls, value: str) -> str:
        if not value or len(value) < 16:
            raise ValueError(
                "SECRET_KEY must be set via environment variable and be at "
                "least 16 characters long."
            )
        return value

    @field_validator("ENVIRONMENT")
    @classmethod
    def environment_must_be_known(cls, value: str) -> str:
        allowed = {"development", "testing", "production"}
        if value not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return value

    @field_validator("INITIAL_ADMIN_PASSWORD")
    @classmethod
    def initial_admin_password_strength(cls, value: Optional[str]) -> Optional[str]:
        if value and len(value) < 8:
            raise ValueError(
                "INITIAL_ADMIN_PASSWORD must be at least 8 characters long if set."
            )
        return value

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor. Import and call this, never instantiate
    Settings() directly, so the whole app shares one validated instance."""
    return Settings()