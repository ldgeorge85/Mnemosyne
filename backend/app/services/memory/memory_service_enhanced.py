"""
Enhanced Memory Service

This module provides the main memory service that integrates extraction,
embedding generation, and storage with vector search capabilities.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from pgvector.sqlalchemy import Vector

from app.db.models.memory import Memory, MemoryChunk
from app.db.models.conversation import Conversation, Message
from app.services.memory.extraction import MemoryExtractor
from app.services.memory.embeddings import EmbeddingGenerator, EmbeddingConfig
from app.core.exceptions import NotFoundError, InternalServerError

logger = logging.getLogger(__name__)


class MemoryService:
    """
    Main service for memory operations including extraction, embedding, and retrieval.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the memory service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.extractor = MemoryExtractor()
        self.embedding_config = EmbeddingConfig()
    
    async def process_conversation(
        self,
        conversation_id: UUID,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Process a conversation to extract and store memories.
        
        Args:
            conversation_id: ID of the conversation to process
            user_id: ID of the user who owns the conversation
            
        Returns:
            Summary of extracted memories
        """
        # Get conversation with messages
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .where(Conversation.user_id == user_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise NotFoundError("Conversation", str(conversation_id))
        
        # Get messages
        messages_result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        messages = messages_result.scalars().all()
        
        # Prepare conversation data
        conversation_data = {
            "id": str(conversation.id),
            "title": conversation.title,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        }
        
        # Extract memories
        extracted = await self.extractor.extract_memories(conversation_data)
        
        # Create memories from extracted data
        created_memories = []
        
        async with EmbeddingGenerator(self.embedding_config) as embedder:
            # Process entities as memories
            for entity in extracted.get("entities", []):
                memory = await self._create_memory_from_entity(
                    entity, conversation_id, user_id, embedder
                )
                if memory:
                    created_memories.append(memory)
            
            # Process facts as memories
            for fact in extracted.get("facts", []):
                memory = await self._create_memory_from_fact(
                    fact, conversation_id, user_id, embedder
                )
                if memory:
                    created_memories.append(memory)
            
            # Process preferences as memories
            for preference in extracted.get("preferences", []):
                memory = await self._create_memory_from_preference(
                    preference, conversation_id, user_id, embedder
                )
                if memory:
                    created_memories.append(memory)
            
            # Process action items as memories
            for action in extracted.get("action_items", []):
                memory = await self._create_memory_from_action(
                    action, conversation_id, user_id, embedder
                )
                if memory:
                    created_memories.append(memory)
            
            # Process personal information
            personal_info = extracted.get("personal_info", {})
            for category, items in personal_info.items():
                for item in items:
                    memory = await self._create_memory_from_personal_info(
                        item, category, conversation_id, user_id, embedder
                    )
                    if memory:
                        created_memories.append(memory)
        
        # Commit all memories
        await self.db.commit()
        
        return {
            "conversation_id": str(conversation_id),
            "memories_created": len(created_memories),
            "extraction_summary": {
                "entities": len(extracted.get("entities", [])),
                "facts": len(extracted.get("facts", [])),
                "preferences": len(extracted.get("preferences", [])),
                "action_items": len(extracted.get("action_items", [])),
                "personal_info_items": sum(
                    len(items) for items in extracted.get("personal_info", {}).values()
                )
            }
        }
    
    async def _create_memory_from_entity(
        self,
        entity: Dict[str, Any],
        conversation_id: UUID,
        user_id: UUID,
        embedder: EmbeddingGenerator
    ) -> Optional[Memory]:
        """Create a memory from an extracted entity."""
        # Skip very common entities
        if entity["type"] in ["relative_date"] and entity["text"].lower() in ["today", "tomorrow", "yesterday"]:
            return None
        
        title = f"{entity['type'].title()}: {entity['text']}"
        content = f"Mentioned {entity['type']}: {entity['text']}"
        
        # Generate embedding
        embedding_result = await embedder.generate_embedding(content)
        
        memory = Memory(
            user_id=user_id,
            title=title,
            content=content,
            source="conversation",
            source_type="entity_extraction",
            source_id=conversation_id,
            embedding=embedding_result["embedding"],
            embedding_vector=embedding_result["embedding"],
            embedding_dimension=embedding_result["dimension"],
            embedding_model=embedding_result["model"],
            importance=entity.get("confidence", 0.5),
            memory_metadata={
                "entity_type": entity["type"],
                "original_text": entity["text"],
                "confidence": entity.get("confidence", 0.5)
            },
            tags=[entity["type"], "entity"]
        )
        
        self.db.add(memory)
        return memory
    
    async def _create_memory_from_fact(
        self,
        fact: Dict[str, Any],
        conversation_id: UUID,
        user_id: UUID,
        embedder: EmbeddingGenerator
    ) -> Optional[Memory]:
        """Create a memory from an extracted fact."""
        title = f"Fact: {fact['extracted_info'][:50]}..."
        content = fact["statement"]
        
        # Generate embedding
        embedding_result = await embedder.generate_embedding(content)
        
        # Calculate importance based on fact type
        importance_weights = {
            "health": 0.9,
            "employment": 0.8,
            "residence": 0.8,
            "education": 0.7,
            "personal_attribute": 0.7,
            "relationship": 0.8,
            "family": 0.8,
            "medication": 0.9,
            "possession": 0.5,
            "habit": 0.6,
            "preference": 0.6
        }
        
        importance = importance_weights.get(fact["type"], 0.6) * fact.get("confidence", 0.9)
        
        memory = Memory(
            user_id=user_id,
            title=title,
            content=content,
            source="conversation",
            source_type="fact_extraction",
            source_id=conversation_id,
            embedding=embedding_result["embedding"],
            embedding_vector=embedding_result["embedding"],
            embedding_dimension=embedding_result["dimension"],
            embedding_model=embedding_result["model"],
            importance=importance,
            memory_metadata={
                "fact_type": fact["type"],
                "extracted_info": fact["extracted_info"],
                "source": fact.get("source", "user"),
                "confidence": fact.get("confidence", 0.9)
            },
            tags=[fact["type"], "fact", fact.get("source", "user")]
        )
        
        self.db.add(memory)
        return memory
    
    async def _create_memory_from_preference(
        self,
        preference: Dict[str, Any],
        conversation_id: UUID,
        user_id: UUID,
        embedder: EmbeddingGenerator
    ) -> Optional[Memory]:
        """Create a memory from an extracted preference."""
        sentiment_emoji = {
            "positive": "👍",
            "negative": "👎",
            "neutral": "😐",
            "conditional": "🤔",
            "dietary": "🍽️",
            "dietary_restriction": "🚫"
        }
        
        emoji = sentiment_emoji.get(preference["sentiment"], "")
        title = f"Preference {emoji}: {preference['subject'][:50]}..."
        content = preference["statement"]
        
        # Generate embedding
        embedding_result = await embedder.generate_embedding(content)
        
        # Importance based on sentiment strength
        importance = 0.7 if preference["sentiment"] in ["positive", "negative"] else 0.5
        importance *= preference.get("confidence", 0.85)
        
        memory = Memory(
            user_id=user_id,
            title=title,
            content=content,
            source="conversation",
            source_type="preference_extraction",
            source_id=conversation_id,
            embedding=embedding_result["embedding"],
            embedding_vector=embedding_result["embedding"],
            embedding_dimension=embedding_result["dimension"],
            embedding_model=embedding_result["model"],
            importance=importance,
            memory_metadata={
                "sentiment": preference["sentiment"],
                "subject": preference["subject"],
                "confidence": preference.get("confidence", 0.85)
            },
            tags=[preference["sentiment"], "preference"]
        )
        
        self.db.add(memory)
        return memory
    
    async def _create_memory_from_action(
        self,
        action: Dict[str, Any],
        conversation_id: UUID,
        user_id: UUID,
        embedder: EmbeddingGenerator
    ) -> Optional[Memory]:
        """Create a memory from an extracted action item."""
        title = f"Action: {action['action'][:50]}..."
        content = action["statement"]
        
        # Generate embedding
        embedding_result = await embedder.generate_embedding(content)
        
        # High importance for action items
        importance = 0.8 * action.get("confidence", 0.8)
        
        memory = Memory(
            user_id=user_id,
            title=title,
            content=content,
            source="conversation",
            source_type="action_extraction",
            source_id=conversation_id,
            embedding=embedding_result["embedding"],
            embedding_vector=embedding_result["embedding"],
            embedding_dimension=embedding_result["dimension"],
            embedding_model=embedding_result["model"],
            importance=importance,
            memory_metadata={
                "action_type": action["type"],
                "action": action["action"],
                "deadline": action.get("deadline"),
                "confidence": action.get("confidence", 0.8)
            },
            tags=[action["type"], "action", "todo"]
        )
        
        self.db.add(memory)
        return memory
    
    async def _create_memory_from_personal_info(
        self,
        info: Dict[str, Any],
        category: str,
        conversation_id: UUID,
        user_id: UUID,
        embedder: EmbeddingGenerator
    ) -> Optional[Memory]:
        """Create a memory from extracted personal information."""
        title = f"{category.title()}: {info['detail'][:50]}..."
        content = info["text"]
        
        # Generate embedding
        embedding_result = await embedder.generate_embedding(content)
        
        # High importance for personal information
        importance_weights = {
            "health": 0.95,
            "finance": 0.9,
            "occupation": 0.8,
            "education": 0.75,
            "location": 0.7,
            "demographics": 0.7
        }
        
        importance = importance_weights.get(category, 0.7) * info.get("confidence", 0.85)
        
        memory = Memory(
            user_id=user_id,
            title=title,
            content=content,
            source="conversation",
            source_type="personal_info_extraction",
            source_id=conversation_id,
            embedding=embedding_result["embedding"],
            embedding_vector=embedding_result["embedding"],
            embedding_dimension=embedding_result["dimension"],
            embedding_model=embedding_result["model"],
            importance=importance,
            memory_metadata={
                "category": category,
                "detail": info["detail"],
                "confidence": info.get("confidence", 0.85)
            },
            tags=[category, "personal", "private"]
        )
        
        self.db.add(memory)
        return memory
    
    async def search_memories(
        self,
        user_id: UUID,
        query: str,
        limit: int = 10,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search memories using vector similarity.
        
        Args:
            user_id: User ID to search memories for
            query: Search query
            limit: Maximum number of results
            threshold: Minimum similarity threshold (0-1)
            
        Returns:
            List of matching memories with similarity scores
        """
        async with EmbeddingGenerator(self.embedding_config) as embedder:
            # Generate embedding for query
            query_embedding_result = await embedder.generate_embedding(query)
            query_embedding = query_embedding_result["embedding"]
            
            # Use pgvector for similarity search
            # Note: This uses cosine similarity via the <=> operator
            similarity_query = text("""
                SELECT 
                    id,
                    title,
                    content,
                    importance,
                    created_at,
                    memory_metadata,
                    tags,
                    1 - (embedding_vector <=> :query_embedding::vector) as similarity
                FROM memories
                WHERE 
                    user_id = :user_id
                    AND is_active = true
                    AND embedding_vector IS NOT NULL
                    AND 1 - (embedding_vector <=> :query_embedding::vector) >= :threshold
                ORDER BY 
                    similarity DESC,
                    importance DESC
                LIMIT :limit
            """)
            
            result = await self.db.execute(
                similarity_query,
                {
                    "query_embedding": query_embedding,
                    "user_id": user_id,
                    "threshold": threshold,
                    "limit": limit
                }
            )
            
            memories = []
            for row in result:
                memories.append({
                    "id": str(row.id),
                    "title": row.title,
                    "content": row.content,
                    "importance": row.importance,
                    "created_at": row.created_at.isoformat(),
                    "metadata": row.memory_metadata,
                    "tags": row.tags or [],
                    "similarity": row.similarity
                })
            
            return memories
    
    async def get_memory_statistics(self, user_id: UUID) -> Dict[str, Any]:
        """
        Get statistics about a user's memories.
        
        Args:
            user_id: User ID to get statistics for
            
        Returns:
            Dictionary of memory statistics
        """
        # Total memories
        total_result = await self.db.execute(
            select(func.count(Memory.id))
            .where(Memory.user_id == user_id)
            .where(Memory.is_active == True)
        )
        total_memories = total_result.scalar() or 0
        
        # Memories by type
        type_result = await self.db.execute(
            select(Memory.source_type, func.count(Memory.id))
            .where(Memory.user_id == user_id)
            .where(Memory.is_active == True)
            .group_by(Memory.source_type)
        )
        memories_by_type = {row[0]: row[1] for row in type_result}
        
        # Average importance
        importance_result = await self.db.execute(
            select(func.avg(Memory.importance))
            .where(Memory.user_id == user_id)
            .where(Memory.is_active == True)
        )
        avg_importance = importance_result.scalar() or 0.0
        
        # Most common tags
        tag_query = text("""
            SELECT tag, COUNT(*) as count
            FROM (
                SELECT unnest(tags) as tag
                FROM memories
                WHERE user_id = :user_id AND is_active = true
            ) t
            GROUP BY tag
            ORDER BY count DESC
            LIMIT 10
        """)
        
        tag_result = await self.db.execute(tag_query, {"user_id": user_id})
        top_tags = [{"tag": row[0], "count": row[1]} for row in tag_result]
        
        return {
            "total_memories": total_memories,
            "memories_by_type": memories_by_type,
            "average_importance": float(avg_importance),
            "top_tags": top_tags,
            "embedding_models_used": ["BAAI/bge-m3", "sentence-transformers/all-MiniLM-L6-v2"]
        }