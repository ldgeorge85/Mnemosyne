"""
Qdrant vector store integration for Mnemosyne
Multi-embedding support with async operations
"""

import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import uuid
import asyncio

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    Range,
    SearchRequest,
    UpdateStatus,
    NamedVector,
    SparseVector,
    SparseVectorParams,
    SparseIndexParams,
    VectorConfig,
    PayloadSchemaType,
    CollectionStatus,
    OptimizersConfigDiff,
    CreateCollection,
    CollectionInfo
)
from qdrant_client.async_qdrant_client import AsyncQdrantClient

from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class VectorStore:
    """Manages vector storage and retrieval with Qdrant"""
    
    def __init__(self):
        self.client: Optional[AsyncQdrantClient] = None
        self.sync_client: Optional[QdrantClient] = None
        self._initialized = False
        
        # Collection configurations
        self.collections = {
            "memories": {
                "vectors": {
                    "content": VectorParams(size=1536, distance=Distance.COSINE),      # OpenAI embeddings
                    "semantic": VectorParams(size=768, distance=Distance.COSINE),      # Local model embeddings
                    "contextual": VectorParams(size=384, distance=Distance.COSINE),    # Contextual embeddings
                },
                "sparse_vectors": {
                    "keywords": SparseVectorParams(
                        index=SparseIndexParams()
                    )
                }
            },
            "reflections": {
                "vectors": {
                    "content": VectorParams(size=1536, distance=Distance.COSINE)
                }
            },
            "signals": {
                "vectors": {
                    "identity": VectorParams(size=1536, distance=Distance.COSINE)
                }
            }
        }
    
    async def initialize(self) -> None:
        """Initialize Qdrant clients and collections"""
        if self._initialized:
            return
        
        try:
            # Create async client
            self.client = AsyncQdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
                api_key=settings.qdrant_api_key.get_secret_value() if settings.qdrant_api_key else None,
                https=settings.qdrant_https,
                timeout=30
            )
            
            # Create sync client for some operations
            self.sync_client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
                api_key=settings.qdrant_api_key.get_secret_value() if settings.qdrant_api_key else None,
                https=settings.qdrant_https,
                timeout=30
            )
            
            # Create collections
            await self._create_collections()
            
            self._initialized = True
            logger.info("Vector store initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    async def _create_collections(self) -> None:
        """Create Qdrant collections if they don't exist"""
        for collection_name, config in self.collections.items():
            try:
                # Check if collection exists
                collections = await self.client.get_collections()
                if any(c.name == collection_name for c in collections.collections):
                    logger.info(f"Collection {collection_name} already exists")
                    continue
                
                # Create collection with multiple vector fields
                await self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=config["vectors"],
                    sparse_vectors_config=config.get("sparse_vectors"),
                    optimizers_config=OptimizersConfigDiff(
                        indexing_threshold=20000,
                        memmap_threshold=50000
                    ),
                    on_disk_payload=False
                )
                
                # Create indexes for common search fields
                await self._create_indexes(collection_name)
                
                logger.info(f"Created collection: {collection_name}")
                
            except Exception as e:
                logger.error(f"Error creating collection {collection_name}: {e}")
                raise
    
    async def _create_indexes(self, collection_name: str) -> None:
        """Create payload indexes for efficient filtering"""
        index_fields = {
            "memories": ["user_id", "memory_type", "importance", "domains", "tags", "occurred_at"],
            "reflections": ["user_id", "memory_id", "agent_type", "confidence"],
            "signals": ["user_id", "visibility_level", "coherence", "fracture_index"]
        }
        
        fields = index_fields.get(collection_name, [])
        for field in fields:
            try:
                await self.client.create_payload_index(
                    collection_name=collection_name,
                    field_name=field,
                    field_schema=PayloadSchemaType.KEYWORD if field in ["user_id", "memory_type", "agent_type", "visibility_level"] else PayloadSchemaType.FLOAT
                )
            except Exception as e:
                logger.debug(f"Index for {field} might already exist: {e}")
    
    async def store_memory(self, memory_data: Dict[str, Any], embeddings: Dict[str, List[float]]) -> str:
        """Store a memory with multiple embeddings"""
        try:
            point_id = memory_data.get("id", str(uuid.uuid4()))
            
            # Prepare vectors
            vectors = {}
            if "content" in embeddings:
                vectors["content"] = embeddings["content"]
            if "semantic" in embeddings:
                vectors["semantic"] = embeddings["semantic"]
            if "contextual" in embeddings:
                vectors["contextual"] = embeddings["contextual"]
            
            # Store in Qdrant
            await self.client.upsert(
                collection_name="memories",
                points=[
                    PointStruct(
                        id=point_id,
                        vector=vectors,
                        payload=memory_data
                    )
                ]
            )
            
            logger.debug(f"Stored memory {point_id} with {len(vectors)} embeddings")
            return point_id
            
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            raise
    
    async def search_memories(
        self,
        query_vector: Union[List[float], Dict[str, List[float]]],
        user_id: Optional[str] = None,
        limit: int = 20,
        score_threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None,
        vector_name: str = "content"
    ) -> List[Dict[str, Any]]:
        """Search memories using vector similarity"""
        try:
            # Build filter conditions
            must_conditions = []
            
            if user_id:
                must_conditions.append(
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=user_id)
                    )
                )
            
            if filters:
                for key, value in filters.items():
                    if isinstance(value, dict) and "min" in value:
                        must_conditions.append(
                            FieldCondition(
                                key=key,
                                range=Range(gte=value["min"], lte=value.get("max"))
                            )
                        )
                    else:
                        must_conditions.append(
                            FieldCondition(
                                key=key,
                                match=MatchValue(value=value)
                            )
                        )
            
            # Prepare query vector
            if isinstance(query_vector, dict):
                search_vector = query_vector.get(vector_name, query_vector.get("content"))
            else:
                search_vector = query_vector
            
            # Search
            results = await self.client.search(
                collection_name="memories",
                query_vector=(vector_name, search_vector),
                query_filter=Filter(must=must_conditions) if must_conditions else None,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False
            )
            
            # Format results
            memories = []
            for result in results:
                memory = result.payload
                memory["score"] = result.score
                memory["id"] = result.id
                memories.append(memory)
            
            logger.debug(f"Found {len(memories)} memories matching query")
            return memories
            
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            raise
    
    async def hybrid_search(
        self,
        query_vectors: Dict[str, List[float]],
        user_id: str,
        limit: int = 20,
        weights: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """Perform hybrid search across multiple embedding spaces"""
        try:
            weights = weights or {"content": 0.5, "semantic": 0.3, "contextual": 0.2}
            
            # Search in each embedding space
            all_results = {}
            for vector_name, vector in query_vectors.items():
                if vector_name in weights:
                    results = await self.search_memories(
                        query_vector=vector,
                        user_id=user_id,
                        limit=limit * 2,  # Get more to allow for merging
                        vector_name=vector_name
                    )
                    
                    for result in results:
                        memory_id = result["id"]
                        if memory_id not in all_results:
                            all_results[memory_id] = result
                            all_results[memory_id]["scores"] = {}
                        all_results[memory_id]["scores"][vector_name] = result["score"]
            
            # Calculate weighted scores
            for memory_id, memory in all_results.items():
                weighted_score = 0
                for vector_name, weight in weights.items():
                    score = memory["scores"].get(vector_name, 0)
                    weighted_score += score * weight
                memory["final_score"] = weighted_score
            
            # Sort by final score and return top results
            sorted_results = sorted(
                all_results.values(),
                key=lambda x: x["final_score"],
                reverse=True
            )[:limit]
            
            return sorted_results
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            raise
    
    async def store_reflection(self, reflection_data: Dict[str, Any], embedding: List[float]) -> str:
        """Store an agent reflection"""
        try:
            point_id = reflection_data.get("id", str(uuid.uuid4()))
            
            await self.client.upsert(
                collection_name="reflections",
                points=[
                    PointStruct(
                        id=point_id,
                        vector={"content": embedding},
                        payload=reflection_data
                    )
                ]
            )
            
            return point_id
            
        except Exception as e:
            logger.error(f"Error storing reflection: {e}")
            raise
    
    async def store_signal(self, signal_data: Dict[str, Any], embedding: List[float]) -> str:
        """Store a Deep Signal"""
        try:
            point_id = signal_data.get("id", str(uuid.uuid4()))
            
            await self.client.upsert(
                collection_name="signals",
                points=[
                    PointStruct(
                        id=point_id,
                        vector={"identity": embedding},
                        payload=signal_data
                    )
                ]
            )
            
            return point_id
            
        except Exception as e:
            logger.error(f"Error storing signal: {e}")
            raise
    
    async def find_resonant_signals(
        self,
        signal_embedding: List[float],
        exclude_user_id: Optional[str] = None,
        min_coherence: float = 0.5,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Find signals that resonate with the given signal"""
        try:
            must_conditions = [
                FieldCondition(
                    key="coherence",
                    range=Range(gte=min_coherence)
                ),
                FieldCondition(
                    key="visibility_level",
                    match=MatchValue(value="public")
                )
            ]
            
            must_not_conditions = []
            if exclude_user_id:
                must_not_conditions.append(
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=exclude_user_id)
                    )
                )
            
            results = await self.client.search(
                collection_name="signals",
                query_vector=("identity", signal_embedding),
                query_filter=Filter(
                    must=must_conditions,
                    must_not=must_not_conditions if must_not_conditions else None
                ),
                limit=limit,
                score_threshold=0.6,
                with_payload=True
            )
            
            signals = []
            for result in results:
                signal = result.payload
                signal["resonance_score"] = result.score
                signal["id"] = result.id
                signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error finding resonant signals: {e}")
            raise
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory from vector store"""
        try:
            result = await self.client.delete(
                collection_name="memories",
                points_selector=[memory_id]
            )
            return result.status == UpdateStatus.COMPLETED
            
        except Exception as e:
            logger.error(f"Error deleting memory {memory_id}: {e}")
            return False
    
    async def update_memory_metadata(self, memory_id: str, metadata: Dict[str, Any]) -> bool:
        """Update memory metadata without changing vectors"""
        try:
            await self.client.set_payload(
                collection_name="memories",
                payload=metadata,
                points=[memory_id]
            )
            return True
            
        except Exception as e:
            logger.error(f"Error updating memory metadata: {e}")
            return False
    
    async def get_collection_info(self, collection_name: str) -> Optional[CollectionInfo]:
        """Get information about a collection"""
        try:
            return await self.client.get_collection(collection_name)
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return None
    
    async def health_check(self) -> bool:
        """Check if vector store is healthy"""
        try:
            collections = await self.client.get_collections()
            return len(collections.collections) > 0
        except Exception:
            return False
    
    async def close(self) -> None:
        """Close vector store connections"""
        if self.client:
            # Qdrant client doesn't need explicit closing
            self._initialized = False
            logger.info("Vector store connections closed")


# Global vector store instance
vector_store = VectorStore()


# Utility functions
async def init_vector_store() -> None:
    """Initialize the vector store"""
    await vector_store.initialize()


async def close_vector_store() -> None:
    """Close vector store connections"""
    await vector_store.close()


# Export key items
__all__ = [
    "VectorStore",
    "vector_store",
    "init_vector_store",
    "close_vector_store",
]