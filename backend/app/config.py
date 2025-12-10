"""
Application configuration using Pydantic Settings.
All users are hardcoded to Asia/Singapore timezone.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import List, Any
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_WEBHOOK_SECRET: str = ""
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None
    
    # JWT
    JWT_SECRET_KEY: str
    API_SECRET_KEY: str = ""  # Alias for JWT_SECRET_KEY (set in validator)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    JWT_EXPIRE_MINUTES: int = 10080  # Alias for compatibility

    # API
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: str = '["http://localhost:3000"]'

    # Telegram Webhook
    TELEGRAM_WEBHOOK_URL: str = ""

    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Web App
    WEB_APP_URL: str = "http://localhost:3000"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Sentry (optional)
    SENTRY_DSN: str = ""
    
    # Timezone (hardcoded for all users)
    DEFAULT_TIMEZONE: str = "Asia/Singapore"
    
    # Default Goals
    DEFAULT_WATER_BOTTLES: float = 3.0
    DEFAULT_CARB_PORTIONS: float = 4.0
    DEFAULT_EXERCISE_SESSIONS: int = 6
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    @model_validator(mode='after')
    def set_defaults(self) -> 'Settings':
        """Set default values for aliased fields"""
        # Set API_SECRET_KEY from JWT_SECRET_KEY if not provided
        if not self.API_SECRET_KEY:
            self.API_SECRET_KEY = self.JWT_SECRET_KEY
        # Set JWT_EXPIRE_MINUTES from JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        if self.JWT_EXPIRE_MINUTES != self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES:
            self.JWT_EXPIRE_MINUTES = self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        return self

    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from JSON string"""
        try:
            return json.loads(self.BACKEND_CORS_ORIGINS)
        except:
            return ["http://localhost:3000"]

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == "production"


# Global settings instance
settings = Settings()

