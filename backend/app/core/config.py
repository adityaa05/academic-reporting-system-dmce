# backend/app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Application-wide configuration. Loads variables from environment and .env file.
    """
    # Application Metadata
    PROJECT_NAME: str = "Academic Reporting API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Google/Gemini API Configuration
    GOOGLE_API_KEY: Optional[str] = None
    DEFAULT_MODEL: str = "gemini-2.5-flash"

    # Database Configuration
    DATABASE_URL: str = "postgresql+asyncpg://adityaa:@localhost:5432/reporting_db"

    # Authentication Configuration
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days

    # Environment file loading
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # Ignore extra env vars to prevent validation errors
    )


settings = Settings()
