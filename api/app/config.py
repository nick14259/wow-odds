# api/app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import logging

class Settings(BaseSettings):
    # OAuth2 settings
    CLIENT_ID: str
    CLIENT_SECRET: str
    REDIRECT_URI: str = "http://localhost:8000/api/v1/oauth/callback"
    
    # Warcraft Logs API endpoints
    WARCRAFT_LOGS_TOKEN_URL: str = "https://www.warcraftlogs.com/oauth/token"
    WARCRAFT_LOGS_AUTH_URL: str = "https://www.warcraftlogs.com/oauth/authorize"
    WARCRAFT_LOGS_GRAPHQL_URL: str = "https://www.warcraftlogs.com/api/v2/client"
    
    # Application settings
    ENVIRONMENT: str = "development"
    BASE_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"
    LOG_LEVEL: str = "DEBUG"
    
    # Cache settings
    CACHE_EXPIRATION: int = 300  # 5 minutes in seconds
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

@lru_cache()
def get_settings() -> Settings:
    """
    Create and cache settings instance.
    Uses lru_cache to prevent reading the .env file on every request
    """
    return Settings()

# Initialize settings
settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)
