"""
Pydantic Settings configuration for Mnemosyne
Production-ready configuration with environment variables
"""

from typing import Optional, List, Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator, SecretStr
from functools import lru_cache
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = "Mnemosyne Protocol"
    app_version: str = "3.1.0"
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # API Configuration
    api_prefix: str = "/api/v1"
    docs_enabled: bool = Field(default=True, env="DOCS_ENABLED")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        env="CORS_ORIGINS"
    )
    
    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@postgres:5432/mnemosyne",
        env="DATABASE_URL"
    )
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=40, env="DATABASE_MAX_OVERFLOW")
    database_pool_timeout: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")
    
    # Redis
    redis_url: str = Field(
        default="redis://redis:6379/0",
        env="REDIS_URL"
    )
    redis_max_connections: int = Field(default=50, env="REDIS_MAX_CONNECTIONS")
    redis_decode_responses: bool = Field(default=True, env="REDIS_DECODE_RESPONSES")
    
    # Qdrant Vector Database
    qdrant_host: str = Field(default="qdrant", env="QDRANT_HOST")
    qdrant_port: int = Field(default=6333, env="QDRANT_PORT")
    qdrant_grpc_port: int = Field(default=6334, env="QDRANT_GRPC_PORT")
    qdrant_api_key: Optional[SecretStr] = Field(default=None, env="QDRANT_API_KEY")
    qdrant_https: bool = Field(default=False, env="QDRANT_HTTPS")
    qdrant_collection_name: str = Field(default="memories", env="QDRANT_COLLECTION")
    
    # Authentication
    jwt_secret_key: SecretStr = Field(env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE")
    jwt_refresh_token_expire_days: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE")
    
    # Encryption
    encryption_key: SecretStr = Field(env="ENCRYPTION_KEY")
    
    # OpenAI Configuration
    openai_api_key: Optional[SecretStr] = Field(default=None, env="OPENAI_API_KEY")
    openai_api_base: Optional[str] = Field(default=None, env="OPENAI_API_BASE")
    openai_model: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    openai_embedding_model: str = Field(default="text-embedding-3-small", env="OPENAI_EMBEDDING_MODEL")
    openai_max_tokens: int = Field(default=4000, env="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    
    # Local Model Configuration (Ollama)
    ollama_base_url: str = Field(default="http://ollama:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama2", env="OLLAMA_MODEL")
    ollama_embedding_model: str = Field(default="nomic-embed-text", env="OLLAMA_EMBEDDING_MODEL")
    use_local_models: bool = Field(default=False, env="USE_LOCAL_MODELS")
    
    # Agent Configuration
    max_concurrent_agents: int = Field(default=5, env="MAX_CONCURRENT_AGENTS")
    agent_timeout_seconds: int = Field(default=30, env="AGENT_TIMEOUT")
    agent_memory_limit_mb: int = Field(default=512, env="AGENT_MEMORY_LIMIT")
    
    # Memory Configuration
    memory_consolidation_interval_hours: int = Field(default=24, env="MEMORY_CONSOLIDATION_INTERVAL")
    memory_importance_threshold: float = Field(default=0.5, env="MEMORY_IMPORTANCE_THRESHOLD")
    memory_vector_dimensions: int = Field(default=1536, env="MEMORY_VECTOR_DIMENSIONS")
    max_memory_search_results: int = Field(default=20, env="MAX_MEMORY_SEARCH_RESULTS")
    
    # Deep Signal Configuration
    signal_cooldown_minutes: int = Field(default=15, env="SIGNAL_COOLDOWN")
    signal_min_entropy: float = Field(default=0.3, env="SIGNAL_MIN_ENTROPY")
    signal_decay_days: int = Field(default=30, env="SIGNAL_DECAY_DAYS")
    signal_reevaluation_threshold: float = Field(default=0.5, env="SIGNAL_REEVALUATION_THRESHOLD")
    
    # Privacy Configuration
    k_anonymity_threshold: int = Field(default=3, env="K_ANONYMITY_THRESHOLD")
    differential_privacy_epsilon: float = Field(default=1.0, env="DIFFERENTIAL_PRIVACY_EPSILON")
    
    # Collective Configuration
    collective_sharing_default_duration_days: int = Field(default=30, env="COLLECTIVE_SHARING_DURATION")
    collective_trust_stages: List[str] = Field(
        default=["signal_exchange", "domain_revelation", "capability_sharing", "memory_glimpse", "full_trust"],
        env="COLLECTIVE_TRUST_STAGES"
    )
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = Field(default=60, env="RATE_LIMIT_RPM")
    rate_limit_tokens_per_minute: int = Field(default=40000, env="RATE_LIMIT_TPM")
    
    # Monitoring
    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    structured_logging: bool = Field(default=True, env="STRUCTURED_LOGGING")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # File Storage
    upload_dir: Path = Field(default=Path("/tmp/mnemosyne/uploads"), env="UPLOAD_DIR")
    max_upload_size_mb: int = Field(default=100, env="MAX_UPLOAD_SIZE_MB")
    
    # Security
    allowed_hosts: List[str] = Field(default=["*"], env="ALLOWED_HOSTS")
    trusted_origins: List[str] = Field(default=[], env="TRUSTED_ORIGINS")
    secure_cookies: bool = Field(default=False, env="SECURE_COOKIES")
    
    # Performance
    async_pool_size: int = Field(default=100, env="ASYNC_POOL_SIZE")
    pipeline_batch_size: int = Field(default=10, env="PIPELINE_BATCH_SIZE")
    pipeline_max_workers: int = Field(default=4, env="PIPELINE_MAX_WORKERS")
    
    @validator("database_url")
    def validate_database_url(cls, v: str) -> str:
        """Ensure database URL uses asyncpg for async operations"""
        if "postgresql://" in v and "+asyncpg" not in v:
            v = v.replace("postgresql://", "postgresql+asyncpg://")
        return v
    
    @validator("upload_dir")
    def ensure_upload_dir_exists(cls, v: Path) -> Path:
        """Create upload directory if it doesn't exist"""
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v: Any) -> List[str]:
        """Parse CORS origins from comma-separated string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == "development"
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for migrations"""
        return self.database_url.replace("+asyncpg", "")
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration based on local/remote setting"""
        if self.use_local_models:
            return {
                "base_url": self.ollama_base_url,
                "model": self.ollama_model,
                "embedding_model": self.ollama_embedding_model,
                "temperature": self.openai_temperature,
                "max_tokens": self.openai_max_tokens,
            }
        else:
            config = {
                "model": self.openai_model,
                "embedding_model": self.openai_embedding_model,
                "temperature": self.openai_temperature,
                "max_tokens": self.openai_max_tokens,
            }
            if self.openai_api_key:
                config["api_key"] = self.openai_api_key.get_secret_value()
            if self.openai_api_base:
                config["base_url"] = self.openai_api_base
            return config
    
    def get_qdrant_url(self) -> str:
        """Get Qdrant connection URL"""
        protocol = "https" if self.qdrant_https else "http"
        return f"{protocol}://{self.qdrant_host}:{self.qdrant_port}"
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis connection configuration"""
        return {
            "url": self.redis_url,
            "max_connections": self.redis_max_connections,
            "decode_responses": self.redis_decode_responses,
            "health_check_interval": 30,
            "socket_connect_timeout": 5,
            "socket_timeout": 5,
        }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export commonly used settings
settings = get_settings()