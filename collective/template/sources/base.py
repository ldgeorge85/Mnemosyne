"""
Base interface for all data sources.

AI Agents: All sources inherit from this base class.
This ensures consistent interface across all data sources.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class SourceConfig:
    """Configuration for a data source."""
    name: str
    description: str
    auth_type: str  # 'api_key', 'token', 'oauth'
    required_env_vars: List[str]
    
    
@dataclass
class Collection:
    """Vector database collection configuration."""
    name: str
    description: str
    embedding_fields: List[str]  # Fields to embed
    metadata_fields: List[str]   # Fields to store as metadata
    

class BaseSource(ABC):
    """
    Base class for all data sources.
    
    AI Agents: When creating a new source:
    1. Inherit from this class
    2. Implement all abstract methods
    3. Add source-specific query methods
    4. Define prompt templates in prompts.py
    """
    
    @abstractmethod
    def __init__(self, **kwargs):
        """Initialize the source with authentication."""
        pass
    
    @abstractmethod
    def get_config(self) -> SourceConfig:
        """
        Return source configuration.
        
        Example:
            return SourceConfig(
                name="outline",
                description="Team knowledge base",
                auth_type="api_key",
                required_env_vars=["OUTLINE_API_KEY", "OUTLINE_URL"]
            )
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the source is properly configured and accessible."""
        pass
    
    @abstractmethod
    def get_collections(self) -> List[Collection]:
        """
        Define vector DB collections for this source.
        
        Example:
            return [
                Collection(
                    name="outline_docs",
                    description="Documentation pages",
                    embedding_fields=["title", "content"],
                    metadata_fields=["doc_id", "collection", "updated_at"]
                )
            ]
        """
        pass
    
    def list_available_queries(self) -> List[str]:
        """
        List all available query methods.
        
        AI Agents: This helps discover what queries are available.
        """
        methods = []
        for method_name in dir(self):
            method = getattr(self, method_name)
            if (callable(method) and 
                not method_name.startswith('_') and
                method_name not in ['get_config', 'test_connection', 
                                   'get_collections', 'list_available_queries']):
                methods.append(method_name)
        return methods