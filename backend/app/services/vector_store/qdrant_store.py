"""
Qdrant Vector Store Integration

This module provides integration with Qdrant vector database for
high-performance similarity search and vector storage.
"""

import logging
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchRequest,
    UpdateStatus,
    CollectionStatus,
)
from qdrant_client.http.exceptions import UnexpectedResponse

from app.core.config import settings

logger = logging.getLogger(__name__)


class QdrantStore:
    """
    Qdrant vector store for memory embeddings.
    
    This class provides methods for storing and retrieving memory embeddings
    using Qdrant vector database.
    """
    
    def __init__(
        self,
        collection_name: str = "memories",
        host: Optional[str] = None,
        port: Optional[int] = None,
        embedding_dimension: int = 1024,  # Default for embedding-inno1
        distance_metric: Distance = Distance.COSINE,
    ):
        """
        Initialize the Qdrant store.
        
        Args:
            collection_name: Name of the Qdrant collection
            host: Qdrant server host
            port: Qdrant server port
            embedding_dimension: Dimension of the embedding vectors
            distance_metric: Distance metric to use
        """
        self.collection_name = collection_name
        self.embedding_dimension = embedding_dimension
        self.distance_metric = distance_metric
        
        # Get connection params from settings or use defaults
        self.host = host or getattr(settings, "QDRANT_HOST", "localhost")
        self.port = port or getattr(settings, "QDRANT_PORT", 6333)
        
        # Initialize client
        self.client = QdrantClient(host=self.host, port=self.port)
        
        # Initialize collection
        self._initialize_collection()
    
    def _initialize_collection(self):
        """Initialize or verify the Qdrant collection."""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                # Create collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dimension,
                        distance=self.distance_metric,
                    ),
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                # Verify collection parameters
                collection_info = self.client.get_collection(self.collection_name)
                if collection_info.config.params.vectors.size != self.embedding_dimension:
                    logger.warning(
                        f"Collection {self.collection_name} has different dimension "
                        f"({collection_info.config.params.vectors.size}) than expected ({self.embedding_dimension})"
                    )
                logger.info(f"Using existing Qdrant collection: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Error initializing Qdrant collection: {e}")
            raise
    
    async def add_memory(
        self,
        memory_id: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Add a memory embedding to the vector store.
        
        Args:
            memory_id: Unique ID of the memory
            embedding: Embedding vector
            metadata: Optional metadata to store with the vector
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare metadata
            payload = metadata or {}
            payload["memory_id"] = memory_id
            payload["indexed_at"] = datetime.utcnow().isoformat()
            
            # Create point
            point = PointStruct(
                id=memory_id,
                vector=embedding,
                payload=payload,
            )
            
            # Upsert point
            result = self.client.upsert(
                collection_name=self.collection_name,
                points=[point],
            )
            
            if result.status == UpdateStatus.COMPLETED:
                logger.debug(f"Added memory {memory_id} to Qdrant")
                return True
            else:
                logger.error(f"Failed to add memory {memory_id} to Qdrant: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding memory to Qdrant: {e}")
            return False
    
    async def add_memories_batch(
        self,
        memories: List[Tuple[str, List[float], Optional[Dict[str, Any]]]],
    ) -> bool:
        """
        Add multiple memory embeddings to the vector store.
        
        Args:
            memories: List of tuples (memory_id, embedding, metadata)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            points = []
            for memory_id, embedding, metadata in memories:
                payload = metadata or {}
                payload["memory_id"] = memory_id
                payload["indexed_at"] = datetime.utcnow().isoformat()
                
                points.append(
                    PointStruct(
                        id=memory_id,
                        vector=embedding,
                        payload=payload,
                    )
                )
            
            # Batch upsert
            result = self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )
            
            if result.status == UpdateStatus.COMPLETED:
                logger.info(f"Added {len(memories)} memories to Qdrant")
                return True
            else:
                logger.error(f"Failed to add memories to Qdrant: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding memories batch to Qdrant: {e}")
            return False
    
    async def search_similar(
        self,
        query_embedding: List[float],
        limit: int = 10,
        score_threshold: Optional[float] = None,
        filter_conditions: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar memories based on embedding similarity.
        
        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score threshold
            filter_conditions: Optional filter conditions
            
        Returns:
            List of search results with memory IDs and scores
        """
        try:
            # Build filter if conditions provided
            filter_obj = None
            if filter_conditions:
                must_conditions = []
                for key, value in filter_conditions.items():
                    must_conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value),
                        )
                    )
                filter_obj = Filter(must=must_conditions)
            
            # Perform search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                query_filter=filter_obj,
                score_threshold=score_threshold,
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "memory_id": result.id,
                    "score": result.score,
                    "metadata": result.payload,
                })
            
            logger.debug(f"Found {len(formatted_results)} similar memories")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching similar memories: {e}")
            return []
    
    async def update_memory(
        self,
        memory_id: str,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Update a memory embedding in the vector store.
        
        Args:
            memory_id: ID of the memory to update
            embedding: New embedding vector (optional)
            metadata: New metadata (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get existing point
            existing = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[memory_id],
            )
            
            if not existing:
                logger.warning(f"Memory {memory_id} not found in Qdrant")
                return False
            
            # Prepare update
            if embedding is not None:
                # Update vector
                point = PointStruct(
                    id=memory_id,
                    vector=embedding,
                    payload=metadata or existing[0].payload,
                )
                result = self.client.upsert(
                    collection_name=self.collection_name,
                    points=[point],
                )
            elif metadata is not None:
                # Update metadata only
                result = self.client.set_payload(
                    collection_name=self.collection_name,
                    payload=metadata,
                    points=[memory_id],
                )
            else:
                return True  # Nothing to update
            
            if result.status == UpdateStatus.COMPLETED:
                logger.debug(f"Updated memory {memory_id} in Qdrant")
                return True
            else:
                logger.error(f"Failed to update memory {memory_id}: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating memory in Qdrant: {e}")
            return False
    
    async def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory from the vector store.
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.client.delete(
                collection_name=self.collection_name,
                points_selector=[memory_id],
            )
            
            if result.status == UpdateStatus.COMPLETED:
                logger.debug(f"Deleted memory {memory_id} from Qdrant")
                return True
            else:
                logger.error(f"Failed to delete memory {memory_id}: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting memory from Qdrant: {e}")
            return False
    
    async def delete_memories_batch(self, memory_ids: List[str]) -> bool:
        """
        Delete multiple memories from the vector store.
        
        Args:
            memory_ids: List of memory IDs to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.client.delete(
                collection_name=self.collection_name,
                points_selector=memory_ids,
            )
            
            if result.status == UpdateStatus.COMPLETED:
                logger.info(f"Deleted {len(memory_ids)} memories from Qdrant")
                return True
            else:
                logger.error(f"Failed to delete memories: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting memories batch from Qdrant: {e}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            
            return {
                "collection_name": self.collection_name,
                "vectors_count": collection_info.vectors_count,
                "indexed_vectors_count": collection_info.indexed_vectors_count,
                "points_count": collection_info.points_count,
                "segments_count": collection_info.segments_count,
                "status": collection_info.status,
                "config": {
                    "dimension": collection_info.config.params.vectors.size,
                    "distance": collection_info.config.params.vectors.distance,
                },
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}
    
    async def recreate_collection(self) -> bool:
        """
        Recreate the collection (will delete all data).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete existing collection
            self.client.delete_collection(collection_name=self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
            
            # Recreate collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dimension,
                    distance=self.distance_metric,
                ),
            )
            logger.info(f"Recreated collection: {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error recreating collection: {e}")
            return False


# Global instance for easy access
_qdrant_store = None


def get_qdrant_store() -> QdrantStore:
    """
    Get the global Qdrant store instance.
    
    Returns:
        QdrantStore instance
    """
    global _qdrant_store
    if _qdrant_store is None:
        _qdrant_store = QdrantStore(
            embedding_dimension=settings.MEMORY_VECTOR_DIMENSIONS
        )
    return _qdrant_store