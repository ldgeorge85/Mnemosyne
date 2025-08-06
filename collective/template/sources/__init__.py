"""
Data source registry for knowledge platform.

AI Agents: This is your starting point for discovering available sources.
Use list_sources() to see what's available.
Use get_source() to instantiate a source.

Example:
    from sources import list_sources, get_source
    
    # See available sources
    sources = list_sources()
    print(sources)
    
    # Get a specific source
    outline = get_source("outline")
"""

from typing import Dict, Type, Any
from .base import BaseSource
from .outline import OutlineSource


# Registry of available sources
SOURCE_REGISTRY: Dict[str, Type[BaseSource]] = {
    "outline": OutlineSource,
}


def list_sources() -> Dict[str, Dict[str, Any]]:
    """
    List all available data sources.
    
    Returns:
        Dictionary of source names to their configurations
        
    Example:
        sources = list_sources()
        # {
        #     "outline": {
        #         "description": "Team knowledge base and documentation",
        #         "auth_type": "api_key",
        #         "required_env_vars": ["OUTLINE_API_KEY", "OUTLINE_URL"],
        #         "available_queries": ["list_documents", "search", ...]
        #     }
        # }
    """
    sources = {}
    
    for name, source_class in SOURCE_REGISTRY.items():
        # Create temporary instance to get config
        try:
            temp_source = source_class(api_key="temp", base_url="http://temp")
            config = temp_source.get_config()
            
            sources[name] = {
                "description": config.description,
                "auth_type": config.auth_type,
                "required_env_vars": config.required_env_vars,
                "available_queries": temp_source.list_available_queries()
            }
        except:
            # If can't instantiate, get basic info
            sources[name] = {
                "description": f"{name} data source",
                "error": "Could not load source configuration"
            }
    
    return sources


def get_source(name: str, **kwargs) -> BaseSource:
    """
    Get a configured source instance.
    
    Args:
        name: Source name (e.g., "outline")
        **kwargs: Authentication parameters
        
    Returns:
        Configured source instance
        
    Example:
        outline = get_source("outline", 
                           api_key="your-key",
                           base_url="https://docs.company.com")
        
        # Or use environment variables
        outline = get_source("outline")  # Uses OUTLINE_API_KEY, OUTLINE_URL
    """
    if name not in SOURCE_REGISTRY:
        available = ", ".join(SOURCE_REGISTRY.keys())
        raise ValueError(f"Unknown source: {name}. Available: {available}")
    
    source_class = SOURCE_REGISTRY[name]
    return source_class(**kwargs)


def register_source(name: str, source_class: Type[BaseSource]):
    """
    Register a new source type.
    
    AI Agents: Use this to add custom sources.
    
    Example:
        from sources.base import BaseSource
        
        class MyCustomSource(BaseSource):
            # ... implementation ...
            
        register_source("custom", MyCustomSource)
    """
    SOURCE_REGISTRY[name] = source_class


# Convenience exports
__all__ = [
    "list_sources",
    "get_source", 
    "register_source",
    "BaseSource",
    "OutlineSource"
]