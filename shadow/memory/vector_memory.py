"""
Vector Memory System Implementation for the Shadow platform.

This module provides a vector-based memory system for semantic search functionality,
with both in-memory implementation and extensibility for external vector databases.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
import numpy as np
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    logging.getLogger("shadow.memory.vector").debug("Loaded environment variables from .env file")
except ImportError:
    logging.getLogger("shadow.memory.vector").debug("python-dotenv not available")
except Exception as e:
    logging.getLogger("shadow.memory.vector").debug(f"Could not load .env file: {e}")

from memory.memory_base import MemoryItem, VectorMemorySystem

# Configure logging
logger = logging.getLogger("shadow.memory.vector")


class InMemoryVectorStore(VectorMemorySystem):
    """
    In-memory implementation of a vector-based memory system.
    
    This provides a simple vector store using numpy for vector operations,
    suitable for development and testing. For production use, this should
    be replaced with a proper vector database.
    """
    
    def __init__(self):
        """Initialize the in-memory vector store."""
        super().__init__("InMemoryVector")
        self.items: Dict[str, MemoryItem] = {}
        self.vectors: Dict[str, np.ndarray] = {}
    
    def store(self, item: MemoryItem) -> str:
        """
        Store a memory item (without embedding).
        
        In a real implementation, this would compute the embedding here.
        
        Args:
            item: The memory item to store
            
        Returns:
            ID of the stored item
        """
        # Generate an ID if one isn't provided
        if item.item_id is None:
            item.item_id = str(uuid.uuid4())
        
        # Store the item
        self.items[item.item_id] = item
        
        # In a real implementation, we would compute the embedding here
        # For now, we'll just store a random vector if vectors doesn't exist
        if item.item_id not in self.vectors:
            # Generate a random embedding (this is just a placeholder)
            # In production, this would use a real embedding model
            self.vectors[item.item_id] = np.random.randn(384)  # Common embedding dimension
        
        logger.info(f"Stored memory item with ID {item.item_id}")
        return item.item_id
    
    def store_with_embedding(self, item: MemoryItem, embedding: List[float]) -> str:
        """
        Store a memory item with a pre-computed embedding.
        
        Args:
            item: The memory item to store
            embedding: The pre-computed embedding vector
            
        Returns:
            ID of the stored item
        """
        # Generate an ID if one isn't provided
        if item.item_id is None:
            item.item_id = str(uuid.uuid4())
        
        # Store the item and its embedding
        self.items[item.item_id] = item
        self.vectors[item.item_id] = np.array(embedding, dtype=np.float32)
        
        logger.info(f"Stored memory item with ID {item.item_id} and pre-computed embedding")
        return item.item_id
    
    def retrieve(self, item_id: str) -> Optional[MemoryItem]:
        """
        Retrieve a memory item by ID.
        
        Args:
            item_id: ID of the memory item to retrieve
            
        Returns:
            The retrieved memory item or None if not found
        """
        return self.items.get(item_id)
    
    def delete(self, item_id: str) -> bool:
        """
        Delete a memory item.
        
        Args:
            item_id: ID of the memory item to delete
            
        Returns:
            True if the item was deleted, False otherwise
        """
        if item_id in self.items:
            del self.items[item_id]
            if item_id in self.vectors:
                del self.vectors[item_id]
            logger.info(f"Deleted memory item with ID {item_id}")
            return True
        
        logger.warning(f"Attempted to delete non-existent memory item with ID {item_id}")
        return False
    
    def clear(self) -> bool:
        """
        Clear all memory items.
        
        Returns:
            True if the memory was cleared, False otherwise
        """
        self.items.clear()
        self.vectors.clear()
        logger.info("Cleared all memory items")
        return True
    
    def search(self, query: str, limit: int = 5) -> List[MemoryItem]:
        """
        Search for memory items matching a query.
        
        In a real implementation, this would compute the query embedding
        and perform vector search. For now, this is a simple keyword match.
        
        Args:
            query: The search query
            limit: Maximum number of items to return
            
        Returns:
            List of memory items matching the query
        """
        # Simple keyword matching as a fallback
        results = []
        query_lower = query.lower()
        
        for item_id, item in self.items.items():
            if query_lower in item.content.lower():
                results.append(item)
            
            if len(results) >= limit:
                break
        
        return results
    
    def search_by_vector(self, query_vector: List[float], limit: int = 5) -> List[Tuple[MemoryItem, float]]:
        """
        Search for memory items by vector similarity.
        
        Args:
            query_vector: The query vector
            limit: Maximum number of items to return
            
        Returns:
            List of tuples containing memory items and similarity scores
        """
        query_vector_np = np.array(query_vector, dtype=np.float32)
        
        # Calculate cosine similarity for all vectors
        similarities = []
        for item_id, vector in self.vectors.items():
            # Compute cosine similarity
            similarity = np.dot(query_vector_np, vector) / (
                np.linalg.norm(query_vector_np) * np.linalg.norm(vector)
            )
            similarities.append((item_id, similarity))
        
        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return the top matching items
        results = []
        for item_id, similarity in similarities[:limit]:
            if item_id in self.items:
                results.append((self.items[item_id], similarity))
        
        return results
    

class EmbeddingService:
    """
    Service for generating embeddings using various providers.
    Supports configurable endpoints and OpenAI-compatible APIs.
    """
    
    def __init__(self, 
                 provider: str = "openai",
                 base_url: str = None,
                 api_key: str = None,
                 model_name: str = None):
        """
        Initialize the embedding service.
        
        Args:
            provider: The embedding provider to use (openai, mock)
            base_url: Base URL for API (defaults to EMBEDDING_BASE_URL env var)
            api_key: API key (defaults to EMBEDDING_API_KEY env var)
            model_name: Model name (defaults to EMBEDDING_MODEL_NAME env var)
        """
        self.provider = provider
        
        # Load configuration from environment variables with fallbacks
        self.base_url = base_url or os.environ.get("EMBEDDING_BASE_URL") or "https://api.openai.com/v1"
        self.api_key = api_key or os.environ.get("EMBEDDING_API_KEY") or os.environ.get("OPENAI_API_KEY")
        self.model_name = model_name or os.environ.get("EMBEDDING_MODEL_NAME") or "text-embedding-ada-002"
        
        # Log configuration (without exposing API key)
        logger.info(f"Initializing embedding service:")
        logger.info(f"  Provider: {provider}")
        logger.info(f"  Base URL: {self.base_url}")
        logger.info(f"  Model: {self.model_name}")
        logger.info(f"  API Key: {'*' * 8 + self.api_key[-4:] if self.api_key else 'Not set'}")
    
    def validate_api_key(self) -> bool:
        """Validate that the API key is set and not a placeholder."""
        return (self.api_key and 
                self.api_key != "your-openai-api-key-here" and 
                len(self.api_key.strip()) > 10)
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get an embedding for the given text.
        
        Args:
            text: The text to embed
            
        Returns:
            The embedding vector
        """
        if self.provider == "openai":
            # Use real OpenAI-compatible embeddings API
            try:
                import openai
                import os
                
                # Validate API key
                if not self.validate_api_key():
                    logger.error("API key not found or invalid")
                    raise ValueError("API key not configured or invalid")
                
                # Configure OpenAI client for custom endpoints
                client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
                
                # Get embedding from OpenAI-compatible API
                logger.info(f"Getting embedding for text: {text[:50]}...")
                response = client.embeddings.create(
                    input=text,
                    model=self.model_name
                )
                
                embedding = response.data[0].embedding
                logger.info(f"Successfully retrieved embedding with dimension {len(embedding)}")
                return embedding
                
            except ImportError:
                logger.error("OpenAI package not installed. Run 'pip install openai'")
                raise ImportError("OpenAI package required for embeddings")
            except Exception as e:
                logger.error(f"Error getting embedding: {str(e)}")
                raise e
        
        elif self.provider == "mock":
            # For testing, return a deterministic vector based on text hash
            import hashlib
            text_hash = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
            np.random.seed(text_hash)  # Make it deterministic for the same text
            embedding = list(np.random.randn(384))  # Common embedding dimension
            logger.info(f"Generated mock embedding for text: {text[:50]}...")
            return embedding
        
        # Add more providers as needed (Anthropic, etc.)
        
        # Default fallback
        logger.warning(f"Unknown embedding provider: {self.provider}, falling back to mock")
        return self.get_embedding_with_provider("mock", text)
    
    def get_embedding_with_provider(self, provider: str, text: str) -> List[float]:
        """Get embedding using a specific provider (for fallback scenarios)."""
        original_provider = self.provider
        self.provider = provider
        try:
            return self.get_embedding(text)
        finally:
            self.provider = original_provider
