"""
Application configuration using Pydantic Settings.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/certify_intel"
    redis_url: str = "redis://localhost:6379/0"
    
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"
    openai_embedding_model: str = "text-embedding-3-large"
    
    # Bing Search
    bing_api_key: str = ""
    
    # Application
    secret_key: str = "dev-secret-key-change-in-production"
    debug: bool = True
    allowed_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Scraping
    scrape_timeout_ms: int = 30000
    scrape_user_agent: str = "CertifyIntelBot/1.0"
    
    # Alerts
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    alert_from_email: str = "alerts@certifyhealth.com"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
