"""
Embedding service for Mnemosyne Protocol
Multi-model embedding generation with fallbacks
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import hashlib
import numpy as np

import openai
from openai import AsyncOpenAI
import aiohttp

from ..core.config import get_settings
from ..core.redis_client import redis_manager

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingModel(str, Enum):
    """Available embedding models"""
    CONTENT = "content"  # Primary OpenAI model
    SEMANTIC = "semantic"  # Local semantic model
    CONTEXTUAL = "contextual"  # Lightweight context model


class EmbeddingService:
    """Service for generating and managing embeddings"""
    
    def __init__(self):
        self.openai_client: Optional[AsyncOpenAI] = None
        self.ollama_client: Optional[aiohttp.ClientSession] = None
        self.cache_enabled = True
        self.cache_ttl = 3600 * 24  # 24 hours
        
        # Model configurations
        self.model_configs = {
            EmbeddingModel.CONTENT: {
                'provider': 'openai',
                'model': settings.openai_embedding_model,
                'dimensions': 1536
            },
            EmbeddingModel.SEMANTIC: {
                'provider': 'ollama' if settings.use_local_models else 'openai',
                'model': settings.ollama_embedding_model if settings.use_local_models else 'text-embedding-3-small',
                'dimensions': 768
            },
            EmbeddingModel.CONTEXTUAL: {
                'provider': 'ollama' if settings.use_local_models else 'openai',
                'model': settings.ollama_embedding_model if settings.use_local_models else 'text-embedding-3-small',
                'dimensions': 384
            }
        }
    
    async def initialize(self):
        """Initialize embedding clients"""
        try:
            # Initialize OpenAI client
            if settings.openai_api_key:
                self.openai_client = AsyncOpenAI(
                    api_key=settings.openai_api_key.get_secret_value(),
                    base_url=settings.openai_api_base if settings.openai_api_base else None
                )
                logger.info("OpenAI embedding client initialized")
            
            # Initialize Ollama client session
            if settings.use_local_models:
                self.ollama_client = aiohttp.ClientSession()
                logger.info("Ollama embedding client initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding service: {e}")
            raise
    
    async def close(self):
        """Close client connections"""
        if self.ollama_client:
            await self.ollama_client.close()
    
    def _get_cache_key(self, text: str, model: EmbeddingModel) -> str:
        """Generate cache key for embedding"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"embedding:{model.value}:{text_hash}"
    
    async def _get_cached_embedding(self, text: str, model: EmbeddingModel) -> Optional[List[float]]:
        """Get embedding from cache"""
        if not self.cache_enabled:
            return None
        
        cache_key = self._get_cache_key(text, model)
        cached = await redis_manager.cache_get(cache_key, namespace="embeddings")
        
        if cached:
            logger.debug(f"Cache hit for embedding {model.value}")
            return cached
        
        return None
    
    async def _cache_embedding(self, text: str, model: EmbeddingModel, embedding: List[float]):
        """Cache embedding"""
        if not self.cache_enabled:
            return
        
        cache_key = self._get_cache_key(text, model)
        await redis_manager.cache_set(
            cache_key,
            embedding,
            ttl=self.cache_ttl,
            namespace="embeddings"
        )
    
    async def _generate_openai_embedding(self, text: str, model_name: str) -> List[float]:
        """Generate embedding using OpenAI"""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")
        
        try:
            response = await self.openai_client.embeddings.create(
                model=model_name,
                input=text,
                encoding_format="float"
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"OpenAI embedding generation failed: {e}")
            raise
    
    async def _generate_ollama_embedding(self, text: str, model_name: str) -> List[float]:
        """Generate embedding using Ollama"""
        if not self.ollama_client:
            raise ValueError("Ollama client not initialized")
        
        try:
            async with self.ollama_client.post(
                f"{settings.ollama_base_url}/api/embeddings",
                json={"model": model_name, "prompt": text}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["embedding"]
                else:
                    error = await response.text()
                    raise Exception(f"Ollama error: {error}")
                    
        except Exception as e:
            logger.error(f"Ollama embedding generation failed: {e}")
            raise
    
    async def generate_embedding(
        self,
        text: str,
        model: Union[EmbeddingModel, str] = EmbeddingModel.CONTENT
    ) -> List[float]:
        """Generate embedding for text"""
        if isinstance(model, str):
            model = EmbeddingModel(model)
        
        # Check cache
        cached = await self._get_cached_embedding(text, model)
        if cached:
            return cached
        
        # Get model configuration
        config = self.model_configs[model]
        provider = config['provider']
        model_name = config['model']
        dimensions = config['dimensions']
        
        # Generate embedding
        try:
            if provider == 'openai':
                embedding = await self._generate_openai_embedding(text, model_name)
            elif provider == 'ollama':
                embedding = await self._generate_ollama_embedding(text, model_name)
            else:
                raise ValueError(f"Unknown provider: {provider}")
            
            # Truncate or pad to expected dimensions
            if len(embedding) > dimensions:
                embedding = embedding[:dimensions]
            elif len(embedding) < dimensions:
                embedding = embedding + [0.0] * (dimensions - len(embedding))
            
            # Cache the embedding
            await self._cache_embedding(text, model, embedding)
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate {model.value} embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * dimensions
    
    async def generate_multi_embeddings(
        self,
        text: str,
        models: Optional[List[EmbeddingModel]] = None
    ) -> Dict[str, List[float]]:
        """Generate multiple embeddings for text"""
        if models is None:
            models = list(EmbeddingModel)
        
        # Generate embeddings concurrently
        tasks = {
            model.value: self.generate_embedding(text, model)
            for model in models
        }
        
        results = {}
        for model_name, task in tasks.items():
            try:
                results[model_name] = await task
            except Exception as e:
                logger.error(f"Failed to generate {model_name} embedding: {e}")
                # Use zero vector as fallback
                config = self.model_configs[EmbeddingModel(model_name)]
                results[model_name] = [0.0] * config['dimensions']
        
        return results
    
    async def batch_generate_embeddings(
        self,
        texts: List[str],
        model: EmbeddingModel = EmbeddingModel.CONTENT,
        batch_size: int = 10
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Generate embeddings for batch concurrently
            tasks = [self.generate_embedding(text, model) for text in batch]
            batch_embeddings = await asyncio.gather(*tasks)
            
            embeddings.extend(batch_embeddings)
            
            # Small delay between batches to avoid rate limiting
            if i + batch_size < len(texts):
                await asyncio.sleep(0.1)
        
        return embeddings
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between embeddings"""
        if not embedding1 or not embedding2:
            return 0.0
        
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
        
        # Clamp to [-1, 1] to handle floating point errors
        return max(-1.0, min(1.0, float(similarity)))
    
    def combine_embeddings(
        self,
        embeddings: List[List[float]],
        weights: Optional[List[float]] = None
    ) -> List[float]:
        """Combine multiple embeddings with optional weights"""
        if not embeddings:
            return []
        
        if weights is None:
            weights = [1.0] * len(embeddings)
        
        # Ensure weights sum to 1
        weight_sum = sum(weights)
        if weight_sum > 0:
            weights = [w / weight_sum for w in weights]
        
        # Weighted average of embeddings
        combined = np.zeros(len(embeddings[0]))
        for embedding, weight in zip(embeddings, weights):
            combined += np.array(embedding) * weight
        
        return combined.tolist()
    
    async def generate_contextual_embedding(
        self,
        text: str,
        context: Dict[str, Any]
    ) -> List[float]:
        """Generate embedding with context information"""
        # Build context string
        context_parts = []
        
        if context.get('tags'):
            context_parts.append(f"Tags: {', '.join(context['tags'])}")
        
        if context.get('domains'):
            context_parts.append(f"Domains: {', '.join(context['domains'])}")
        
        if context.get('summary'):
            context_parts.append(f"Summary: {context['summary']}")
        
        # Combine text with context
        contextual_text = f"{text}\n\nContext:\n" + "\n".join(context_parts)
        
        # Generate embedding
        return await self.generate_embedding(contextual_text, EmbeddingModel.CONTEXTUAL)


class EmbeddingPipeline:
    """Pipeline for processing embeddings"""
    
    def __init__(self, embedding_service: EmbeddingService):
        self.service = embedding_service
    
    async def process_memory_embeddings(self, memory_data: Dict[str, Any]) -> Dict[str, List[float]]:
        """Generate all embeddings for a memory"""
        content = memory_data.get('content', '')
        
        # Generate multi-embeddings
        embeddings = await self.service.generate_multi_embeddings(content)
        
        # Generate contextual embedding if context available
        if memory_data.get('tags') or memory_data.get('domains'):
            context = {
                'tags': memory_data.get('tags', []),
                'domains': memory_data.get('domains', []),
                'summary': memory_data.get('summary', '')
            }
            embeddings['contextual'] = await self.service.generate_contextual_embedding(
                content,
                context
            )
        
        return embeddings
    
    async def find_similar_embeddings(
        self,
        query_embedding: List[float],
        candidate_embeddings: List[Tuple[str, List[float]]],
        threshold: float = 0.7,
        top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """Find similar embeddings from candidates"""
        similarities = []
        
        for id, embedding in candidate_embeddings:
            similarity = self.service.calculate_similarity(query_embedding, embedding)
            if similarity >= threshold:
                similarities.append((id, similarity))
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]


# Global embedding service instance
embedding_service = EmbeddingService()


# Utility functions
async def init_embedding_service():
    """Initialize the embedding service"""
    await embedding_service.initialize()


async def close_embedding_service():
    """Close embedding service connections"""
    await embedding_service.close()


# Export classes and functions
__all__ = [
    'EmbeddingModel',
    'EmbeddingService',
    'EmbeddingPipeline',
    'embedding_service',
    'init_embedding_service',
    'close_embedding_service',
]