"""
Memory Context Service

This module provides context retrieval from user memories for RAG (Retrieval-Augmented Generation).
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.memory.embeddings import EmbeddingGenerator
from app.services.vector_store.qdrant_store import get_qdrant_store
from app.db.models.memory import Memory

logger = logging.getLogger(__name__)


class MemoryContextService:
    """
    Service for retrieving relevant memory context for chat interactions.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the memory context service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.qdrant_store = get_qdrant_store()
    
    async def get_relevant_memories(
        self,
        query: str,
        user_id: str,
        limit: int = 5,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Get relevant memories for a user query.
        
        Args:
            query: User's query text
            user_id: User ID to filter memories
            limit: Maximum number of memories to retrieve
            score_threshold: Minimum similarity score
            
        Returns:
            List of relevant memory dictionaries
        """
        try:
            # Generate embedding for the query
            async with EmbeddingGenerator() as embedding_generator:
                embedding_result = await embedding_generator.generate_embedding(query)
            
            # Search for similar memories in Qdrant
            search_results = await self.qdrant_store.search_similar(
                query_embedding=embedding_result["embedding"],
                limit=limit,
                score_threshold=score_threshold,
                filter_conditions={"user_id": user_id}
            )
            
            if not search_results:
                logger.info(f"No relevant memories found for user {user_id}")
                return []
            
            # Fetch full memory data from database
            memory_ids = [result["memory_id"] for result in search_results]
            
            stmt = select(Memory).where(
                Memory.id.in_(memory_ids),
                Memory.user_id == user_id,
                Memory.is_active == True
            )
            result = await self.db.execute(stmt)
            memories = result.scalars().all()
            
            # Create memory dict with scores
            memory_dict = {str(m.id): m for m in memories}
            
            # Combine memory data with scores
            relevant_memories = []
            for search_result in search_results:
                memory_id = search_result["memory_id"]
                if memory_id in memory_dict:
                    memory = memory_dict[memory_id]
                    relevant_memories.append({
                        "id": str(memory.id),
                        "title": memory.title,
                        "content": memory.content,
                        "tags": memory.tags,
                        "importance": memory.importance,
                        "score": search_result["score"],
                        "created_at": memory.created_at.isoformat() if memory.created_at else None
                    })
            
            logger.info(f"Retrieved {len(relevant_memories)} relevant memories for user {user_id}")
            return relevant_memories
            
        except Exception as e:
            logger.error(f"Error retrieving memory context: {e}")
            return []
    
    def format_memory_context(self, memories: List[Dict[str, Any]]) -> str:
        """
        Format memories into a context string for the LLM.
        
        Args:
            memories: List of memory dictionaries
            
        Returns:
            Formatted context string
        """
        if not memories:
            return ""
        
        context_parts = ["Based on your stored memories:\n"]
        
        for i, memory in enumerate(memories, 1):
            # Include title, content, and relevance score
            context_parts.append(f"\n{i}. {memory['title']} (relevance: {memory['score']:.2f})")
            context_parts.append(f"   {memory['content'][:200]}...")
            if memory.get('tags'):
                context_parts.append(f"   Tags: {', '.join(memory['tags'])}")
        
        context_parts.append("\n---\n")
        return "\n".join(context_parts)