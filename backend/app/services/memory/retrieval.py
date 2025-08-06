"""
Memory Retrieval System

This module provides services for retrieving memories using vector similarity search,
filtering, and ranking to find the most relevant information for user queries.
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple, Union
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.vector_store import MemoryVectorStore
from app.services.vector_store.vector_index_manager import vector_index_manager
from app.services.llm import OpenAIClient
from app.core.config import settings


# Set up module logger
logger = logging.getLogger(__name__)


class MemoryRetrievalService:
    """
    Service for retrieving and searching memories.
    
    This service provides methods for retrieving memories using vector similarity search,
    filtering by relevance, and ranking results.
    """
    
    def __init__(self):
        """Initialize the memory retrieval service."""
        self.vector_store = vector_index_manager.get_store("memory")
        if not self.vector_store:
            logger.warning("Memory vector store not found, using default")
            self.vector_store = MemoryVectorStore()
            vector_index_manager.register_store("memory", self.vector_store)
        
        self.openai_client = OpenAIClient()
    
    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate an embedding vector for the given text.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            Embedding vector, or None if generation failed
        """
        try:
            embeddings = await self.openai_client.embeddings(text=text)
            if embeddings and len(embeddings) > 0:
                return embeddings[0]
            return None
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    async def retrieve_by_similarity(
        self,
        query_text: str,
        user_id: str,
        db: AsyncSession,
        limit: int = 10,
        min_relevance_score: float = 0.7,
        fetch_full_memories: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories by similarity to the query text.
        
        Args:
            query_text: Query text to compare memories against
            user_id: ID of the user whose memories to search
            db: Database session
            limit: Maximum number of results to return
            min_relevance_score: Minimum relevance score (0-1)
            fetch_full_memories: Whether to fetch the full memories for the chunks
            
        Returns:
            List of retrieved memories with relevance scores
        """
        # Generate embedding for the query text
        query_embedding = await self.generate_embedding(query_text)
        if not query_embedding:
            logger.error("Failed to generate embedding for query text")
            return []
            
        try:
            # Search for similar memory chunks
            memory_chunks = await self.vector_store.search_memories(
                query_embedding=query_embedding,
                user_id=user_id,
                db=db,
                limit=limit,
                min_relevance_score=min_relevance_score
            )
            
            if not memory_chunks:
                return []
                
            if not fetch_full_memories:
                return memory_chunks
                
            # Group chunks by parent memory and fetch complete memories
            memory_ids = {chunk["memory_id"] for chunk in memory_chunks}
            
            # Query to fetch the full memories
            query = """
                SELECT m.*, 
                       ARRAY_AGG(mc.id) as chunk_ids,
                       ARRAY_AGG(mc.content) as chunk_contents,
                       MAX(mc.relevance_score) as relevance_score
                FROM memories m
                JOIN memory_chunks mc ON m.id = mc.memory_id
                WHERE m.id IN :memory_ids
                AND m.user_id = :user_id
                GROUP BY m.id
                ORDER BY MAX(mc.relevance_score) DESC
            """
            
            result = await db.execute(
                query, 
                {"memory_ids": tuple(memory_ids), "user_id": user_id}
            )
            full_memories = [dict(row) for row in result]
            
            return full_memories
        except Exception as e:
            logger.error(f"Error retrieving memories by similarity: {e}")
            return []
    
    async def retrieve_by_tags(
        self,
        tags: List[str],
        user_id: str,
        db: AsyncSession,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories by tags.
        
        Args:
            tags: List of tags to search for
            user_id: ID of the user whose memories to search
            db: Database session
            limit: Maximum number of results to return
            offset: Offset for pagination
            
        Returns:
            List of retrieved memories
        """
        try:
            # Query to fetch memories by tags
            if not tags:
                return []
                
            # PostgreSQL array overlap operator: &&
            query = """
                SELECT m.*
                FROM memories m
                WHERE m.user_id = :user_id
                AND m.tags && :tags
                ORDER BY m.created_at DESC
                LIMIT :limit OFFSET :offset
            """
            
            result = await db.execute(
                query, 
                {"user_id": user_id, "tags": tags, "limit": limit, "offset": offset}
            )
            memories = [dict(row) for row in result]
            
            return memories
        except Exception as e:
            logger.error(f"Error retrieving memories by tags: {e}")
            return []
    
    async def retrieve_by_hybrid_search(
        self,
        query_text: str,
        tags: Optional[List[str]] = None,
        user_id: str = None,
        db: AsyncSession = None,
        limit: int = 10,
        min_relevance_score: float = 0.6
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories using hybrid search (vector similarity + filters).
        
        Args:
            query_text: Query text to compare memories against
            tags: Optional list of tags to filter by
            user_id: ID of the user whose memories to search
            db: Database session
            limit: Maximum number of results to return
            min_relevance_score: Minimum relevance score (0-1)
            
        Returns:
            List of retrieved memories with scores
        """
        # Generate embedding for the query text
        query_embedding = await self.generate_embedding(query_text)
        if not query_embedding:
            logger.error("Failed to generate embedding for query text")
            return []
            
        try:
            # Build the query based on parameters
            base_query = """
                WITH ranked_chunks AS (
                    SELECT 
                        mc.*,
                        1 - (mc.embedding <=> :query_embedding::vector) as relevance_score,
                        ROW_NUMBER() OVER (
                            PARTITION BY mc.memory_id 
                            ORDER BY 1 - (mc.embedding <=> :query_embedding::vector) DESC
                        ) as chunk_rank
                    FROM memory_chunks mc
                    WHERE mc.user_id = :user_id
                    AND 1 - (mc.embedding <=> :query_embedding::vector) >= :min_score
                )
                SELECT 
                    m.*,
                    rc.relevance_score,
                    rc.content as matching_content
                FROM memories m
                JOIN ranked_chunks rc ON m.id = rc.memory_id
                WHERE rc.chunk_rank = 1
            """
            
            # Add tag filtering if tags are provided
            if tags and len(tags) > 0:
                base_query += " AND m.tags && :tags"
                
            # Add order by and limit
            base_query += " ORDER BY rc.relevance_score DESC LIMIT :limit"
            
            # Prepare parameters
            params = {
                "query_embedding": query_embedding,
                "user_id": user_id,
                "min_score": min_relevance_score,
                "limit": limit
            }
            
            if tags and len(tags) > 0:
                params["tags"] = tags
                
            # Execute query
            result = await db.execute(base_query, params)
            memories = [dict(row) for row in result]
            
            return memories
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return []
    
    async def record_memory_access(
        self,
        memory_id: str,
        user_id: str,
        db: AsyncSession,
        query_text: Optional[str] = None
    ) -> bool:
        """
        Record an access to a memory for tracking purposes.
        
        Args:
            memory_id: ID of the accessed memory
            user_id: ID of the user who accessed the memory
            db: Database session
            query_text: Optional query text that led to this access
            
        Returns:
            True if the access was recorded successfully
        """
        try:
            # Insert into memory_accesses table
            query = """
                INSERT INTO memory_accesses 
                (memory_id, user_id, query_text, accessed_at)
                VALUES (:memory_id, :user_id, :query_text, NOW())
            """
            
            await db.execute(
                query, 
                {"memory_id": memory_id, "user_id": user_id, "query_text": query_text}
            )
            
            # Update last_accessed_at in memories table
            update_query = """
                UPDATE memories
                SET last_accessed_at = NOW(), access_count = access_count + 1
                WHERE id = :memory_id AND user_id = :user_id
            """
            
            await db.execute(
                update_query,
                {"memory_id": memory_id, "user_id": user_id}
            )
            
            await db.commit()
            return True
        except Exception as e:
            logger.error(f"Error recording memory access: {e}")
            await db.rollback()
            return False
    
    async def get_memory_by_id(
        self,
        memory_id: str,
        user_id: str,
        db: AsyncSession,
        record_access: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Get a memory by its ID.
        
        Args:
            memory_id: ID of the memory to retrieve
            user_id: ID of the user who owns the memory
            db: Database session
            record_access: Whether to record this access
            
        Returns:
            Memory data, or None if not found
        """
        try:
            # Query to get the memory with its chunks
            query = """
                SELECT 
                    m.*,
                    ARRAY_AGG(mc.id) as chunk_ids,
                    ARRAY_AGG(mc.content ORDER BY mc.sequence_num) as chunk_contents
                FROM memories m
                LEFT JOIN memory_chunks mc ON m.id = mc.memory_id
                WHERE m.id = :memory_id AND m.user_id = :user_id
                GROUP BY m.id
            """
            
            result = await db.execute(
                query, 
                {"memory_id": memory_id, "user_id": user_id}
            )
            memory = result.mappings().one_or_none()
            
            if memory and record_access:
                await self.record_memory_access(
                    memory_id=memory_id,
                    user_id=user_id,
                    db=db
                )
            
            return dict(memory) if memory else None
        except Exception as e:
            logger.error(f"Error getting memory by ID: {e}")
            return None


# Create global memory retrieval service instance
memory_retrieval_service = MemoryRetrievalService()
