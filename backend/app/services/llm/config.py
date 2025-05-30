"""
LLM Configuration

This module provides configuration classes and utilities for LLM services.
It handles provider-specific settings and common configuration options.
"""

from enum import Enum, auto
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.core.config import settings


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    LOCAL = "local"
    MOCK = "mock"  # Used for testing


class LLMConfig(BaseModel):
    """
    Configuration for Language Model settings.
    
    This class centralizes all LLM configuration settings and provides
    methods to retrieve provider-specific configurations.
    """
    provider: LLMProvider = Field(
        default=LLMProvider.OPENAI,
        description="The LLM provider to use"
    )
    model_name: str = Field(
        default=settings.OPENAI_MODEL,
        description="The name of the model to use"
    )
    temperature: float = Field(
        default=0.7,
        description="Controls randomness in responses: 0.0=deterministic, 1.0=creative"
    )
    max_tokens: Optional[int] = Field(
        default=None,
        description="Maximum number of tokens to generate"
    )
    streaming: bool = Field(
        default=True,
        description="Whether to stream responses token by token"
    )
    timeout_seconds: int = Field(
        default=120,
        description="Timeout for LLM requests in seconds"
    )
    retry_attempts: int = Field(
        default=3,
        description="Number of retry attempts for failed requests"
    )
    additional_kwargs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional provider-specific parameters"
    )
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
    
    @classmethod
    def from_settings(cls) -> "LLMConfig":
        """
        Create a configuration instance from application settings.
        
        Returns:
            LLMConfig: Configuration initialized from app settings
        """
        # Determine provider from available API keys
        provider = LLMProvider.OPENAI
        if settings.OPENAI_API_KEY:
            provider = LLMProvider.OPENAI
        
        return cls(
            provider=provider,
            model_name=settings.OPENAI_MODEL,
            temperature=0.7,
            max_tokens=None,
            streaming=True,
        )
    
    def get_openai_config(self) -> Dict[str, Any]:
        """
        Get OpenAI-specific configuration.
        
        Returns:
            Dict[str, Any]: OpenAI configuration parameters
        """
        config = {
            "model": self.model_name,
            "temperature": self.temperature,
            "streaming": self.streaming,
        }
        
        if self.max_tokens:
            config["max_tokens"] = self.max_tokens
            
        if settings.OPENAI_API_KEY:
            config["openai_api_key"] = settings.OPENAI_API_KEY
            
        if settings.OPENAI_ORG_ID:
            config["openai_organization"] = settings.OPENAI_ORG_ID
            
        # Merge any additional kwargs
        config.update(self.additional_kwargs)
        
        return config
