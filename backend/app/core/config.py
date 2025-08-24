"""
Configuration Management

This module handles all application configuration, loading from environment variables
and providing typed configuration values to the rest of the application.
"""

import os
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables with validation.
    Default values are provided for development, but should be overridden in production.
    """
    
    # Application Settings
    APP_NAME: str = "Mnemosyne"
    APP_ENV: str = "development"  # development, testing, production
    APP_DEBUG: bool = True
    APP_VERSION: str = "0.1.0"
    APP_URL: str = "http://localhost"
    API_PREFIX: str = "/api/v1"
    DOCS_ENABLED: bool = True  # Enable/disable OpenAPI docs
    DOCS_LOGO_URL: str = "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"  # Placeholder
    DOCS_PRIMARY_COLOR: str = "#1f4287"  # Primary brand color
    AUTH_REQUIRED: bool = True  # Whether authentication is required for API access
    SECRET_KEY: str = Field(default="CHANGE-THIS-SECRET-KEY-IN-PRODUCTION", env="SECRET_KEY")  # SECURITY WARNING: Change this!
    
    # CORS settings
    CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = [
        "http://localhost:3000",  # React frontend
        "http://localhost:8000",  # API itself
        "http://localhost",       # Docker host
    ]
    
    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """
        Parse CORS origins from string or list of strings.
        
        Args:
            v: String or list of strings representing allowed origins
            
        Returns:
            Parsed list of origins
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database Settings
    DB_CONNECTION: str = "postgresql"
    DB_HOST: str = "postgres"
    DB_PORT: str = "5432"
    DB_DATABASE: str = "mnemosyne"
    DB_USERNAME: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_SCHEMA: str = "public"
    
    @property
    def DATABASE_URI(self) -> PostgresDsn:
        """
        Constructs the database URI from components.
        
        Returns:
            PostgreSQL connection URI
        """
        return f"{self.DB_CONNECTION}://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"
    
    # Redis Settings
    REDIS_HOST: str = "redis"
    REDIS_PORT: str = "6379"  # The internal port remains 6379 inside Docker network
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    @property
    def REDIS_URI(self) -> RedisDsn:
        """
        Constructs the Redis URI from components.
        
        Returns:
            Redis connection URI
        """
        auth_part = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth_part}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # Vector Database Settings
    VECTOR_DIMENSIONS: int = 1536
    VECTOR_INDEX_TYPE: str = "hnsw"
    VECTOR_DISTANCE_METRIC: str = "cosine"
    
    # Security Settings
    TOKEN_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_SECRET_KEY: str = Field(default="CHANGE-THIS-JWT-SECRET-IN-PRODUCTION", env="JWT_SECRET_KEY")  # SECURITY WARNING: Change this!
    JWT_ISSUER: str = "mnemosyne"
    
    # Track Configuration (Dual-Track System)
    TRACK: str = Field(default="production", env="TRACK")  # production or research
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")  # development, testing, production
    
    # W3C DID Settings
    W3C_DID_ENABLED: bool = Field(default=False, env="W3C_DID_ENABLED")
    W3C_DID_METHOD: str = Field(default="mnem", env="W3C_DID_METHOD")
    
    # OAuth Settings (optional)
    OAUTH_ENABLED: bool = Field(default=False, env="OAUTH_ENABLED")
    OAUTH_CLIENT_ID: Optional[str] = Field(default=None, env="OAUTH_CLIENT_ID")
    OAUTH_CLIENT_SECRET: Optional[str] = Field(default=None, env="OAUTH_CLIENT_SECRET")
    OAUTH_AUTH_URL: Optional[str] = Field(default=None, env="OAUTH_AUTH_URL")
    OAUTH_TOKEN_URL: Optional[str] = Field(default=None, env="OAUTH_TOKEN_URL")
    OAUTH_REDIRECT_URI: str = Field(default="http://localhost:3000/callback", env="OAUTH_REDIRECT_URI")
    
    # Qdrant Vector Database
    QDRANT_HOST: str = Field(default="qdrant", env="QDRANT_HOST")
    QDRANT_PORT: int = Field(default=6333, env="QDRANT_PORT")
    QDRANT_API_KEY: Optional[str] = Field(default=None, env="QDRANT_API_KEY")
    
    # Auth Configuration (can be overridden via environment)
    AUTH_CONFIG: dict = Field(default_factory=dict)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_ORG_ID: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 2048
    OPENAI_TEMPERATURE: float = 0.7
    
    # Embedding Settings (uses OpenAI-compatible endpoint by default)
    EMBEDDING_API_ENDPOINT: Optional[str] = None  # Override if different from OPENAI_BASE_URL/embeddings
    EMBEDDING_API_KEY: Optional[str] = None  # Uses OPENAI_API_KEY if not set
    MEMORY_EMBEDDING_MODEL: str = "embedding-inno1"  # Model name for embeddings (no 's')
    MEMORY_VECTOR_DIMENSIONS: int = 1024  # Dimension of embeddings
    EMBEDDING_FALLBACK_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_FALLBACK_DIMENSION: int = 384
    
    # Model config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Create a global settings object
settings = Settings()

# Function to get settings (for dependency injection)
def get_settings() -> Settings:
    """
    Get the settings instance.
    
    Returns:
        Settings: The application settings
    """
    return settings

# Export settings to be imported elsewhere
__all__ = ["settings", "get_settings"]
