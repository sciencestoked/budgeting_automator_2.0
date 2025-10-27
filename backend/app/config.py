"""Configuration management using pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = "sqlite:///./budgeting.db"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True

    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = ""
    email_to: str = ""

    # Security
    secret_key: str = "dev-secret-key-change-in-production"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()
