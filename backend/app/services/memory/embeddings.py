"""
Embedding Generation Service

This module provides embedding generation using BAAI/bge-m3 API as primary
and sentence-transformers as fallback for memory vectorization.
"""

import asyncio
import hashlib
import json
import logging
from typing import List, Dict, Any, Optional, Union
import numpy as np

import httpx
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class EmbeddingConfig:
    """Configuration for embedding services."""
    
    def __init__(self):
        # Primary embedding service (OpenAI-compatible API)
        # Use the same base URL as LLM - OpenAI API already has /embeddings endpoint
        base_url = getattr(settings, "OPENAI_BASE_URL", None)
        if base_url:
            # Use base URL as-is for OpenAI-compatible endpoint
            self.primary_endpoint = base_url.rstrip('/')
        else:
            self.primary_endpoint = getattr(settings, "EMBEDDING_API_ENDPOINT", None)
        
        # Use the same API key as LLM or dedicated embedding key
        self.primary_api_key = getattr(settings, "EMBEDDING_API_KEY", None) or getattr(settings, "OPENAI_API_KEY", None)
        
        # Use configured model or default
        self.primary_model = getattr(settings, "MEMORY_EMBEDDING_MODEL", "embeddings-inno1")
        self.primary_dimension = getattr(settings, "MEMORY_VECTOR_DIMENSIONS", 1024)
        
        # Fallback embedding service (local sentence-transformers)
        self.fallback_model = "sentence-transformers/all-MiniLM-L6-v2"
        self.fallback_dimension = 384
        
        # General settings
        self.max_batch_size = 32
        self.max_text_length = 512
        self.cache_embeddings = True


class EmbeddingCache:
    """Simple in-memory cache for embeddings."""
    
    def __init__(self, max_size: int = 10000):
        self.cache: Dict[str, List[float]] = {}
        self.max_size = max_size
    
    def get_key(self, text: str, model: str) -> str:
        """Generate cache key from text and model."""
        content = f"{model}:{text}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get(self, text: str, model: str) -> Optional[List[float]]:
        """Get embedding from cache."""
        key = self.get_key(text, model)
        return self.cache.get(key)
    
    def set(self, text: str, model: str, embedding: List[float]):
        """Store embedding in cache."""
        if len(self.cache) >= self.max_size:
            # Simple FIFO eviction
            first_key = next(iter(self.cache))
            del self.cache[first_key]
        
        key = self.get_key(text, model)
        self.cache[key] = embedding


class EmbeddingGenerator:
    """
    Generates embeddings for text using BAAI/bge-m3 API with fallback.
    """
    
    def __init__(self, config: Optional[EmbeddingConfig] = None):
        """
        Initialize the embedding generator.
        
        Args:
            config: Embedding configuration
        """
        self.config = config or EmbeddingConfig()
        self.cache = EmbeddingCache() if self.config.cache_embeddings else None
        
        # Initialize fallback model lazily
        self._fallback_model = None
        
        # HTTP client for API calls
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
    
    def _get_fallback_model(self) -> SentenceTransformer:
        """Load fallback model lazily."""
        if self._fallback_model is None:
            logger.info(f"Loading fallback embedding model: {self.config.fallback_model}")
            self._fallback_model = SentenceTransformer(self.config.fallback_model)
        return self._fallback_model
    
    async def generate_embedding(
        self,
        text: str,
        use_fallback: bool = False
    ) -> Dict[str, Any]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            use_fallback: Force use of fallback model
            
        Returns:
            Dictionary with embedding and metadata
        """
        # Truncate text if too long
        if len(text) > self.config.max_text_length:
            text = text[:self.config.max_text_length]
        
        # Check cache first
        if self.cache:
            model = self.config.fallback_model if use_fallback else self.config.primary_model
            cached = self.cache.get(text, model)
            if cached:
                return {
                    "embedding": cached,
                    "model": model,
                    "dimension": len(cached),
                    "cached": True
                }
        
        # Try primary API first (unless fallback is forced)
        if not use_fallback and self.config.primary_endpoint:
            try:
                embedding = await self._generate_api_embedding(text)
                if self.cache:
                    self.cache.set(text, self.config.primary_model, embedding)
                return {
                    "embedding": embedding,
                    "model": self.config.primary_model,
                    "dimension": self.config.primary_dimension,
                    "cached": False
                }
            except Exception as e:
                logger.warning(f"Primary embedding API failed: {e}, falling back to local model")
        
        # Use fallback model
        embedding = await self._generate_fallback_embedding(text)
        if self.cache:
            self.cache.set(text, self.config.fallback_model, embedding)
        
        return {
            "embedding": embedding,
            "model": self.config.fallback_model,
            "dimension": self.config.fallback_dimension,
            "cached": False
        }
    
    async def generate_embeddings(
        self,
        texts: List[str],
        use_fallback: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Generate embeddings for multiple texts with batching.
        
        Args:
            texts: List of texts to embed
            use_fallback: Force use of fallback model
            
        Returns:
            List of embedding dictionaries
        """
        results = []
        
        # Process in batches
        for i in range(0, len(texts), self.config.max_batch_size):
            batch = texts[i:i + self.config.max_batch_size]
            
            # Check cache for each text
            batch_to_embed = []
            batch_indices = []
            
            for j, text in enumerate(batch):
                if self.cache:
                    model = self.config.fallback_model if use_fallback else self.config.primary_model
                    cached = self.cache.get(text, model)
                    if cached:
                        results.append({
                            "embedding": cached,
                            "model": model,
                            "dimension": len(cached),
                            "cached": True
                        })
                        continue
                
                batch_to_embed.append(text[:self.config.max_text_length])
                batch_indices.append(i + j)
            
            if not batch_to_embed:
                continue
            
            # Generate embeddings for uncached texts
            if not use_fallback and self.config.primary_endpoint:
                try:
                    embeddings = await self._generate_api_embeddings(batch_to_embed)
                    for text, embedding in zip(batch_to_embed, embeddings):
                        if self.cache:
                            self.cache.set(text, self.config.primary_model, embedding)
                        results.append({
                            "embedding": embedding,
                            "model": self.config.primary_model,
                            "dimension": self.config.primary_dimension,
                            "cached": False
                        })
                    continue
                except Exception as e:
                    logger.warning(f"Batch API embedding failed: {e}, falling back to local model")
            
            # Use fallback for this batch
            embeddings = await self._generate_fallback_embeddings(batch_to_embed)
            for text, embedding in zip(batch_to_embed, embeddings):
                if self.cache:
                    self.cache.set(text, self.config.fallback_model, embedding)
                results.append({
                    "embedding": embedding,
                    "model": self.config.fallback_model,
                    "dimension": self.config.fallback_dimension,
                    "cached": False
                })
        
        return results
    
    async def _generate_api_embedding(self, text: str) -> List[float]:
        """
        Generate embedding using the primary API.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        if not self.config.primary_endpoint:
            raise ValueError("Primary embedding API endpoint not configured")
        
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.config.primary_api_key:
            headers["Authorization"] = f"Bearer {self.config.primary_api_key}"
        
        data = {
            "input": text,
            "model": self.config.primary_model,
        }
        
        # Add /embeddings to the endpoint for OpenAI-compatible API
        endpoint = f"{self.config.primary_endpoint}/embeddings"
        
        response = await self.client.post(
            endpoint,
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            raise ExternalServiceError(
                service="Embedding API",
                message=f"API returned status {response.status_code}: {response.text}"
            )
        
        result = response.json()
        
        # Handle different response formats
        if "data" in result and isinstance(result["data"], list) and len(result["data"]) > 0:
            # OpenAI-style response
            embedding = np.array(result["data"][0]["embedding"])
            # Normalize to unit length
            embedding = embedding / np.linalg.norm(embedding)
            return embedding.tolist()
        elif "embedding" in result:
            # Direct embedding response
            embedding = np.array(result["embedding"])
            # Normalize to unit length
            embedding = embedding / np.linalg.norm(embedding)
            return embedding.tolist()
        else:
            raise ValueError(f"Unexpected API response format: {result}")
    
    async def _generate_api_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts using the primary API.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not self.config.primary_endpoint:
            raise ValueError("Primary embedding API endpoint not configured")
        
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.config.primary_api_key:
            headers["Authorization"] = f"Bearer {self.config.primary_api_key}"
        
        data = {
            "input": texts,
            "model": self.config.primary_model,
        }
        
        # Add /embeddings to the endpoint for OpenAI-compatible API
        endpoint = f"{self.config.primary_endpoint}/embeddings"
        
        response = await self.client.post(
            endpoint,
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            raise ExternalServiceError(
                service="Embedding API",
                message=f"API returned status {response.status_code}: {response.text}"
            )
        
        result = response.json()
        
        # Handle different response formats
        if "data" in result and isinstance(result["data"], list):
            # OpenAI-style response - normalize each embedding
            embeddings = []
            for item in result["data"]:
                embedding = np.array(item["embedding"])
                # Normalize to unit length
                embedding = embedding / np.linalg.norm(embedding)
                embeddings.append(embedding.tolist())
            return embeddings
        elif "embeddings" in result:
            # Direct embeddings response - normalize each
            embeddings = []
            for emb in result["embeddings"]:
                embedding = np.array(emb)
                embedding = embedding / np.linalg.norm(embedding)
                embeddings.append(embedding.tolist())
            return embeddings
        else:
            raise ValueError(f"Unexpected API response format: {result}")
    
    async def _generate_fallback_embedding(self, text: str) -> List[float]:
        """
        Generate embedding using the fallback model.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        model = self._get_fallback_model()
        
        embedding = await loop.run_in_executor(
            None,
            lambda: model.encode(text, convert_to_numpy=True).tolist()
        )
        
        return embedding
    
    async def _generate_fallback_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts using the fallback model.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        model = self._get_fallback_model()
        
        embeddings = await loop.run_in_executor(
            None,
            lambda: model.encode(texts, convert_to_numpy=True).tolist()
        )
        
        return embeddings
    
    def calculate_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Ensure result is in [0, 1] range
        return float(max(0.0, min(1.0, (similarity + 1) / 2)))