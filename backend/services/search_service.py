"""
Search service for Mnemosyne Protocol
Advanced vector search and retrieval
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import numpy as np

from backend.core.vectors import vector_store
from backend.core.redis_client import redis_manager
from backend.services.embedding import embedding_service, EmbeddingModel
from backend.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SearchResult:
    """Search result with score and metadata"""
    
    def __init__(
        self,
        id: str,
        content: str,
        score: float,
        metadata: Dict[str, Any],
        source: str = "vector"
    ):
        self.id = id
        self.content = content
        self.score = score
        self.metadata = metadata
        self.source = source
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'content': self.content,
            'score': self.score,
            'metadata': self.metadata,
            'source': self.source
        }


class VectorSearchService:
    """Service for vector-based search operations"""
    
    def __init__(self):
        self.cache_ttl = 300  # 5 minutes
        self.reranking_enabled = True
    
    async def search_similar(
        self,
        user_id: str,
        embedding: List[float],
        limit: int = 20,
        threshold: float = 0.5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar memories using vector similarity"""
        try:
            # Search in vector store
            results = await vector_store.search_memories(
                query_vector=embedding,
                user_id=user_id,
                limit=limit,
                score_threshold=threshold,
                filters=filters
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    async def hybrid_search(
        self,
        user_id: str,
        query: str,
        limit: int = 20,
        weights: Optional[Dict[str, float]] = None
    ) -> List[SearchResult]:
        """Perform hybrid search across multiple embedding spaces"""
        try:
            # Generate multiple embeddings for the query
            embeddings = await embedding_service.generate_multi_embeddings(query)
            
            # Default weights if not provided
            if weights is None:
                weights = {
                    'content': 0.5,
                    'semantic': 0.3,
                    'contextual': 0.2
                }
            
            # Perform hybrid search in vector store
            results = await vector_store.hybrid_search(
                query_vectors=embeddings,
                user_id=user_id,
                limit=limit * 2,  # Get more for reranking
                weights=weights
            )
            
            # Convert to SearchResult objects
            search_results = [
                SearchResult(
                    id=r['id'],
                    content=r.get('content', ''),
                    score=r.get('final_score', 0),
                    metadata=r,
                    source='hybrid'
                )
                for r in results
            ]
            
            # Rerank if enabled
            if self.reranking_enabled and search_results:
                search_results = await self.rerank_results(
                    query,
                    search_results,
                    limit
                )
            
            return search_results[:limit]
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return []
    
    async def rerank_results(
        self,
        query: str,
        results: List[SearchResult],
        limit: int
    ) -> List[SearchResult]:
        """Rerank search results for better relevance"""
        try:
            # Simple reranking based on multiple factors
            query_lower = query.lower()
            query_terms = set(query_lower.split())
            
            for result in results:
                # Factor 1: Exact match bonus
                content_lower = result.content.lower()
                if query_lower in content_lower:
                    result.score *= 1.5
                
                # Factor 2: Term overlap
                content_terms = set(content_lower.split())
                overlap = len(query_terms & content_terms) / len(query_terms)
                result.score *= (1 + overlap * 0.3)
                
                # Factor 3: Recency bonus
                if 'occurred_at' in result.metadata:
                    occurred_at = datetime.fromisoformat(result.metadata['occurred_at'])
                    days_old = (datetime.utcnow() - occurred_at).days
                    if days_old < 7:
                        result.score *= 1.2
                    elif days_old < 30:
                        result.score *= 1.1
                
                # Factor 4: Importance bonus
                importance = result.metadata.get('importance', 0.5)
                result.score *= (1 + importance * 0.2)
            
            # Sort by new scores
            results.sort(key=lambda x: x.score, reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            return results
    
    async def semantic_search(
        self,
        user_id: str,
        query: str,
        limit: int = 20,
        domains: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> List[SearchResult]:
        """Semantic search with advanced filtering"""
        try:
            # Build filters
            filters = {}
            if domains:
                filters['domains'] = domains
            if tags:
                filters['tags'] = tags
            if time_range:
                filters['occurred_at'] = {
                    'min': time_range[0].isoformat(),
                    'max': time_range[1].isoformat()
                }
            
            # Generate semantic embedding
            embedding = await embedding_service.generate_embedding(
                query,
                EmbeddingModel.SEMANTIC
            )
            
            # Search with filters
            results = await self.search_similar(
                user_id=user_id,
                embedding=embedding,
                limit=limit,
                threshold=0.4,  # Lower threshold for semantic search
                filters=filters
            )
            
            # Convert to SearchResult objects
            search_results = [
                SearchResult(
                    id=r['id'],
                    content=r.get('content', ''),
                    score=r.get('score', 0),
                    metadata=r,
                    source='semantic'
                )
                for r in results
            ]
            
            return search_results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    async def find_related_memories(
        self,
        memory_id: str,
        user_id: str,
        limit: int = 10
    ) -> List[SearchResult]:
        """Find memories related to a specific memory"""
        try:
            # Get the memory's embedding from vector store
            # This is a simplified version - in production would fetch from DB
            cache_key = f"memory_embedding:{memory_id}"
            embedding = await redis_manager.cache_get(cache_key)
            
            if not embedding:
                # Fetch from vector store or regenerate
                logger.warning(f"Embedding not cached for memory {memory_id}")
                return []
            
            # Search for similar memories
            results = await self.search_similar(
                user_id=user_id,
                embedding=embedding,
                limit=limit + 1,  # +1 to exclude self
                threshold=0.6
            )
            
            # Filter out the original memory
            results = [r for r in results if r['id'] != memory_id]
            
            # Convert to SearchResult objects
            search_results = [
                SearchResult(
                    id=r['id'],
                    content=r.get('content', ''),
                    score=r.get('score', 0),
                    metadata=r,
                    source='related'
                )
                for r in results[:limit]
            ]
            
            return search_results
            
        except Exception as e:
            logger.error(f"Related memory search failed: {e}")
            return []
    
    async def find_resonant_signals(
        self,
        user_id: str,
        signal_embedding: List[float],
        min_coherence: float = 0.5,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Find signals that resonate with user's signal"""
        try:
            # Search for resonant signals
            signals = await vector_store.find_resonant_signals(
                signal_embedding=signal_embedding,
                exclude_user_id=user_id,
                min_coherence=min_coherence,
                limit=limit
            )
            
            return signals
            
        except Exception as e:
            logger.error(f"Resonant signal search failed: {e}")
            return []


class SearchAggregator:
    """Aggregates search results from multiple sources"""
    
    def __init__(self, search_service: VectorSearchService):
        self.search_service = search_service
    
    async def multi_query_search(
        self,
        user_id: str,
        queries: List[str],
        limit_per_query: int = 10,
        total_limit: int = 20
    ) -> List[SearchResult]:
        """Search with multiple queries and aggregate results"""
        try:
            # Run searches concurrently
            tasks = [
                self.search_service.hybrid_search(
                    user_id=user_id,
                    query=query,
                    limit=limit_per_query
                )
                for query in queries
            ]
            
            all_results = await asyncio.gather(*tasks)
            
            # Aggregate and deduplicate
            seen_ids = set()
            aggregated = []
            
            for results in all_results:
                for result in results:
                    if result.id not in seen_ids:
                        aggregated.append(result)
                        seen_ids.add(result.id)
            
            # Sort by score
            aggregated.sort(key=lambda x: x.score, reverse=True)
            
            return aggregated[:total_limit]
            
        except Exception as e:
            logger.error(f"Multi-query search failed: {e}")
            return []
    
    async def contextual_search(
        self,
        user_id: str,
        query: str,
        context: Dict[str, Any],
        limit: int = 20
    ) -> List[SearchResult]:
        """Search with additional context"""
        try:
            # Enhance query with context
            enhanced_query = query
            
            if context.get('previous_queries'):
                # Add context from previous queries
                prev_context = ' '.join(context['previous_queries'][-3:])
                enhanced_query = f"{query} Context: {prev_context}"
            
            if context.get('current_domains'):
                # Add domain context
                domains = context['current_domains']
            else:
                domains = None
            
            if context.get('time_context'):
                # Add temporal context
                time_range = context['time_context']
            else:
                time_range = None
            
            # Perform semantic search with context
            results = await self.search_service.semantic_search(
                user_id=user_id,
                query=enhanced_query,
                limit=limit,
                domains=domains,
                time_range=time_range
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Contextual search failed: {e}")
            return []


class SearchCache:
    """Cache for search results"""
    
    def __init__(self, ttl: int = 300):
        self.ttl = ttl
    
    def _get_cache_key(
        self,
        user_id: str,
        query: str,
        search_type: str
    ) -> str:
        """Generate cache key for search"""
        import hashlib
        query_hash = hashlib.md5(f"{query}:{search_type}".encode()).hexdigest()
        return f"search:{user_id}:{query_hash}"
    
    async def get_cached_results(
        self,
        user_id: str,
        query: str,
        search_type: str
    ) -> Optional[List[SearchResult]]:
        """Get cached search results"""
        try:
            cache_key = self._get_cache_key(user_id, query, search_type)
            cached = await redis_manager.cache_get(cache_key)
            
            if cached:
                # Reconstruct SearchResult objects
                results = [
                    SearchResult(
                        id=r['id'],
                        content=r['content'],
                        score=r['score'],
                        metadata=r['metadata'],
                        source=r['source']
                    )
                    for r in cached
                ]
                return results
            
            return None
            
        except Exception as e:
            logger.debug(f"Cache retrieval failed: {e}")
            return None
    
    async def cache_results(
        self,
        user_id: str,
        query: str,
        search_type: str,
        results: List[SearchResult]
    ) -> None:
        """Cache search results"""
        try:
            cache_key = self._get_cache_key(user_id, query, search_type)
            
            # Convert to serializable format
            cache_data = [r.to_dict() for r in results]
            
            await redis_manager.cache_set(
                cache_key,
                cache_data,
                ttl=self.ttl
            )
            
        except Exception as e:
            logger.debug(f"Cache storage failed: {e}")


# Global search service instance
vector_search_service = VectorSearchService()
search_cache = SearchCache()


# Export classes
__all__ = [
    'SearchResult',
    'VectorSearchService',
    'SearchAggregator',
    'SearchCache',
    'vector_search_service',
    'search_cache',
]