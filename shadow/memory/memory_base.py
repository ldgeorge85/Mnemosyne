"""
Base Memory System for the Shadow platform.

This module defines the base interfaces and types for the memory systems used by
the Shadow AI agent platform, including vector storage, document storage, and
relational storage.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

# Configure logging
logger = logging.getLogger("shadow.memory")


class MemoryItem:
    """
    Base class for items stored in memory.
    """
    
    def __init__(
        self,
        content: str,
        metadata: Dict[str, Any] = None,
        item_id: Optional[str] = None
    ):
        """
        Initialize a memory item.
        
        Args:
            content: The text content of the memory
            metadata: Optional metadata for the memory item
            item_id: Optional ID for the memory item
        """
        self.content = content
        self.metadata = metadata or {}
        self.item_id = item_id
        self.created_at = datetime.now().isoformat()
        
        # Add creation time to metadata if not present
        if "created_at" not in self.metadata:
            self.metadata["created_at"] = self.created_at
            
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the memory item to a dictionary.
        
        Returns:
            Dict representation of the memory item
        """
        return {
            "content": self.content,
            "metadata": self.metadata,
            "id": self.item_id,
            "created_at": self.created_at
        }


class MemorySystem(ABC):
    """
    Abstract base class for memory storage systems.
    """
    
    def __init__(self, name: str):
        """
        Initialize a memory system.
        
        Args:
            name: Name of the memory system
        """
        self.name = name
        logger.info(f"Initializing {name} memory system")
    
    @abstractmethod
    def store(self, item: MemoryItem) -> str:
        """
        Store a memory item.
        
        Args:
            item: The memory item to store
            
        Returns:
            ID of the stored item
        """
        pass
    
    @abstractmethod
    def retrieve(self, item_id: str) -> Optional[MemoryItem]:
        """
        Retrieve a memory item by ID.
        
        Args:
            item_id: ID of the memory item to retrieve
            
        Returns:
            The retrieved memory item or None if not found
        """
        pass
    
    @abstractmethod
    def delete(self, item_id: str) -> bool:
        """
        Delete a memory item.
        
        Args:
            item_id: ID of the memory item to delete
            
        Returns:
            True if the item was deleted, False otherwise
        """
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """
        Clear all memory items.
        
        Returns:
            True if the memory was cleared, False otherwise
        """
        pass
    
    def __str__(self) -> str:
        """Return string representation of the memory system."""
        return f"{self.name} Memory System"


class SearchableMemorySystem(MemorySystem):
    """
    Abstract base class for memory systems that support search.
    """
    
    @abstractmethod
    def search(self, query: str, limit: int = 5) -> List[MemoryItem]:
        """
        Search for memory items matching a query.
        
        Args:
            query: The search query
            limit: Maximum number of items to return
            
        Returns:
            List of memory items matching the query
        """
        pass


class VectorMemorySystem(SearchableMemorySystem):
    """
    Abstract base class for vector-based memory systems.
    """
    
    @abstractmethod
    def store_with_embedding(self, item: MemoryItem, embedding: List[float]) -> str:
        """
        Store a memory item with a pre-computed embedding.
        
        Args:
            item: The memory item to store
            embedding: The pre-computed embedding vector
            
        Returns:
            ID of the stored item
        """
        pass
    
    @abstractmethod
    def search_by_vector(self, query_vector: List[float], limit: int = 5) -> List[Tuple[MemoryItem, float]]:
        """
        Search for memory items by vector similarity.
        
        Args:
            query_vector: The query vector
            limit: Maximum number of items to return
            
        Returns:
            List of tuples containing memory items and similarity scores
        """
        pass
