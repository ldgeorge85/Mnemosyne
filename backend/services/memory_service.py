"""
Memory service for Mnemosyne Protocol
CRUD operations and memory management
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import uuid

from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models.memory import Memory, MemoryType, MemoryStatus
from backend.models.user import User
from backend.core.database import db_manager
from backend.core.vectors import vector_store
from backend.core.redis_client import redis_manager, publish_memory_event
from backend.pipelines.memory_capture import RawMemoryInput, MemoryCapturePipeline
from backend.pipelines.memory_process import MemoryProcessingPipeline
from backend.services.embedding import embedding_service

logger = logging.getLogger(__name__)


class MemoryService:
    """Service for memory CRUD operations"""
    
    def __init__(self):
        self.capture_pipeline = MemoryCapturePipeline()
        self.processing_pipeline = MemoryProcessingPipeline(
            embedding_service=embedding_service,
            search_service=None  # Will be injected later
        )
    
    async def create_memory(
        self,
        user_id: str,
        content: str,
        **kwargs
    ) -> Memory:
        """Create a new memory"""
        try:
            # Create raw memory input
            raw_memory = RawMemoryInput(
                user_id=user_id,
                content=content,
                source=kwargs.get('source', 'chat'),
                source_url=kwargs.get('source_url'),
                title=kwargs.get('title'),
                occurred_at=kwargs.get('occurred_at'),
                memory_type=kwargs.get('memory_type', MemoryType.CONVERSATION),
                metadata=kwargs.get('metadata', {}),
                tags=kwargs.get('tags', []),
                domains=kwargs.get('domains', []),
                importance=kwargs.get('importance'),
                parent_memory_id=kwargs.get('parent_memory_id')
            )
            
            # Run capture pipeline
            capture_result = await self.capture_pipeline.execute(raw_memory)
            if capture_result.status != 'completed' or not capture_result.data:
                raise Exception(f"Memory capture failed: {capture_result.error}")
            
            processed_memory = capture_result.data
            
            # Run processing pipeline
            processing_result = await self.processing_pipeline.execute(processed_memory)
            if processing_result.status != 'completed' or not processing_result.data:
                raise Exception(f"Memory processing failed: {processing_result.error}")
            
            storage_data = processing_result.data
            
            # Store in database
            async with db_manager.session() as session:
                db_record = storage_data['db_record']
                
                # Create Memory object
                memory = Memory(**db_record)
                
                # Add embeddings if available
                embeddings = storage_data['vector_record'].get('embeddings', {})
                if embeddings.get('content'):
                    memory.embedding_content = embeddings['content']
                if embeddings.get('semantic'):
                    memory.embedding_semantic = embeddings['semantic']
                if embeddings.get('contextual'):
                    memory.embedding_contextual = embeddings['contextual']
                
                session.add(memory)
                await session.commit()
                await session.refresh(memory)
                
                # Store in vector store
                await vector_store.store_memory(
                    storage_data['vector_record'],
                    embeddings
                )
                
                # Publish event
                await publish_memory_event('memory_created', {
                    'memory_id': str(memory.id),
                    'user_id': str(memory.user_id),
                    'memory_type': memory.memory_type.value
                })
                
                logger.info(f"Created memory {memory.id} for user {user_id}")
                return memory
                
        except Exception as e:
            logger.error(f"Failed to create memory: {e}")
            raise
    
    async def get_memory(
        self,
        memory_id: str,
        user_id: Optional[str] = None
    ) -> Optional[Memory]:
        """Get a memory by ID"""
        try:
            async with db_manager.session() as session:
                query = select(Memory).where(Memory.id == memory_id)
                
                if user_id:
                    query = query.where(Memory.user_id == user_id)
                
                result = await session.execute(query)
                memory = result.scalar_one_or_none()
                
                if memory:
                    # Update access tracking
                    memory.mark_accessed()
                    await session.commit()
                
                return memory
                
        except Exception as e:
            logger.error(f"Failed to get memory {memory_id}: {e}")
            return None
    
    async def get_user_memories(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        memory_type: Optional[MemoryType] = None,
        min_importance: Optional[float] = None,
        tags: Optional[List[str]] = None,
        domains: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        order_by: str = "occurred_at"
    ) -> List[Memory]:
        """Get memories for a user with filters"""
        try:
            async with db_manager.session() as session:
                query = select(Memory).where(Memory.user_id == user_id)
                
                # Apply filters
                if memory_type:
                    query = query.where(Memory.memory_type == memory_type)
                
                if min_importance is not None:
                    query = query.where(Memory.importance >= min_importance)
                
                if tags:
                    # Memory tags should contain any of the specified tags
                    query = query.where(
                        Memory.tags.op('@>')(func.cast(tags, type_=Memory.tags.type))
                    )
                
                if domains:
                    query = query.where(
                        Memory.domains.op('@>')(func.cast(domains, type_=Memory.domains.type))
                    )
                
                if start_date:
                    query = query.where(Memory.occurred_at >= start_date)
                
                if end_date:
                    query = query.where(Memory.occurred_at <= end_date)
                
                # Order and pagination
                if order_by == "occurred_at":
                    query = query.order_by(Memory.occurred_at.desc())
                elif order_by == "importance":
                    query = query.order_by(Memory.importance.desc())
                elif order_by == "created_at":
                    query = query.order_by(Memory.created_at.desc())
                
                query = query.limit(limit).offset(offset)
                
                result = await session.execute(query)
                memories = result.scalars().all()
                
                return list(memories)
                
        except Exception as e:
            logger.error(f"Failed to get user memories: {e}")
            return []
    
    async def update_memory(
        self,
        memory_id: str,
        user_id: str,
        **updates
    ) -> Optional[Memory]:
        """Update a memory"""
        try:
            async with db_manager.session() as session:
                # Get memory
                query = select(Memory).where(
                    and_(Memory.id == memory_id, Memory.user_id == user_id)
                )
                result = await session.execute(query)
                memory = result.scalar_one_or_none()
                
                if not memory:
                    return None
                
                # Update fields
                for field, value in updates.items():
                    if hasattr(memory, field):
                        setattr(memory, field, value)
                
                memory.updated_at = datetime.utcnow()
                
                await session.commit()
                await session.refresh(memory)
                
                # Update vector store if content changed
                if 'content' in updates or 'summary' in updates:
                    await vector_store.update_memory_metadata(
                        str(memory.id),
                        {
                            'content': memory.content,
                            'summary': memory.summary,
                            'updated_at': memory.updated_at.isoformat()
                        }
                    )
                
                # Publish event
                await publish_memory_event('memory_updated', {
                    'memory_id': str(memory.id),
                    'user_id': str(memory.user_id),
                    'updated_fields': list(updates.keys())
                })
                
                return memory
                
        except Exception as e:
            logger.error(f"Failed to update memory {memory_id}: {e}")
            return None
    
    async def delete_memory(
        self,
        memory_id: str,
        user_id: str,
        soft_delete: bool = True
    ) -> bool:
        """Delete a memory"""
        try:
            async with db_manager.session() as session:
                # Get memory
                query = select(Memory).where(
                    and_(Memory.id == memory_id, Memory.user_id == user_id)
                )
                result = await session.execute(query)
                memory = result.scalar_one_or_none()
                
                if not memory:
                    return False
                
                if soft_delete:
                    # Soft delete
                    memory.soft_delete()
                else:
                    # Hard delete
                    await session.delete(memory)
                    
                    # Remove from vector store
                    await vector_store.delete_memory(str(memory_id))
                
                await session.commit()
                
                # Publish event
                await publish_memory_event('memory_deleted', {
                    'memory_id': str(memory_id),
                    'user_id': str(user_id),
                    'soft_delete': soft_delete
                })
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False
    
    async def get_consolidation_candidates(
        self,
        user_id: str,
        min_age_hours: int = 24,
        max_memories: int = 100
    ) -> List[Memory]:
        """Get memories eligible for consolidation"""
        try:
            async with db_manager.session() as session:
                cutoff_time = datetime.utcnow() - timedelta(hours=min_age_hours)
                
                query = select(Memory).where(
                    and_(
                        Memory.user_id == user_id,
                        Memory.occurred_at <= cutoff_time,
                        Memory.consolidation_count < 3,  # Max 3 consolidations
                        Memory.status != MemoryStatus.ARCHIVED,
                        Memory.deleted_at.is_(None)
                    )
                )
                
                # Prioritize by importance and access patterns
                query = query.order_by(
                    Memory.importance.desc(),
                    Memory.access_count.desc()
                ).limit(max_memories)
                
                result = await session.execute(query)
                memories = result.scalars().all()
                
                # Filter for consolidation eligibility
                candidates = [m for m in memories if m.should_consolidate()]
                
                return candidates
                
        except Exception as e:
            logger.error(f"Failed to get consolidation candidates: {e}")
            return []
    
    async def mark_memories_consolidated(
        self,
        memory_ids: List[str],
        consolidation_group_id: str
    ) -> bool:
        """Mark memories as consolidated"""
        try:
            async with db_manager.session() as session:
                await session.execute(
                    update(Memory)
                    .where(Memory.id.in_(memory_ids))
                    .values(
                        consolidation_count=Memory.consolidation_count + 1,
                        consolidation_group_id=consolidation_group_id,
                        status=MemoryStatus.CONSOLIDATED,
                        updated_at=datetime.utcnow()
                    )
                )
                
                await session.commit()
                
                # Publish event
                await publish_memory_event('memories_consolidated', {
                    'memory_ids': memory_ids,
                    'consolidation_group_id': consolidation_group_id
                })
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to mark memories consolidated: {e}")
            return False
    
    async def get_memory_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get memory statistics for a user"""
        try:
            async with db_manager.session() as session:
                # Total memories
                total_query = select(func.count(Memory.id)).where(
                    and_(Memory.user_id == user_id, Memory.deleted_at.is_(None))
                )
                total_result = await session.execute(total_query)
                total_memories = total_result.scalar()
                
                # By type
                type_query = select(
                    Memory.memory_type,
                    func.count(Memory.id)
                ).where(
                    and_(Memory.user_id == user_id, Memory.deleted_at.is_(None))
                ).group_by(Memory.memory_type)
                
                type_result = await session.execute(type_query)
                memory_types = {
                    type.value: count 
                    for type, count in type_result.all()
                }
                
                # Average importance
                importance_query = select(func.avg(Memory.importance)).where(
                    and_(Memory.user_id == user_id, Memory.deleted_at.is_(None))
                )
                importance_result = await session.execute(importance_query)
                avg_importance = importance_result.scalar() or 0.0
                
                # Recent activity
                recent_cutoff = datetime.utcnow() - timedelta(days=7)
                recent_query = select(func.count(Memory.id)).where(
                    and_(
                        Memory.user_id == user_id,
                        Memory.created_at >= recent_cutoff,
                        Memory.deleted_at.is_(None)
                    )
                )
                recent_result = await session.execute(recent_query)
                recent_memories = recent_result.scalar()
                
                # Consolidation stats
                consolidated_query = select(func.count(Memory.id)).where(
                    and_(
                        Memory.user_id == user_id,
                        Memory.consolidation_count > 0,
                        Memory.deleted_at.is_(None)
                    )
                )
                consolidated_result = await session.execute(consolidated_query)
                consolidated_memories = consolidated_result.scalar()
                
                return {
                    'total_memories': total_memories,
                    'memory_types': memory_types,
                    'average_importance': float(avg_importance),
                    'recent_memories_7d': recent_memories,
                    'consolidated_memories': consolidated_memories,
                    'consolidation_rate': consolidated_memories / total_memories if total_memories > 0 else 0
                }
                
        except Exception as e:
            logger.error(f"Failed to get memory statistics: {e}")
            return {}


class MemorySearchService:
    """Service for searching memories"""
    
    def __init__(self, memory_service: MemoryService):
        self.memory_service = memory_service
    
    async def search_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 20,
        search_type: str = "hybrid"
    ) -> List[Memory]:
        """Search memories using various strategies"""
        try:
            if search_type == "text":
                return await self.text_search(user_id, query, limit)
            elif search_type == "vector":
                return await self.vector_search(user_id, query, limit)
            else:  # hybrid
                return await self.hybrid_search(user_id, query, limit)
                
        except Exception as e:
            logger.error(f"Memory search failed: {e}")
            return []
    
    async def text_search(
        self,
        user_id: str,
        query: str,
        limit: int = 20
    ) -> List[Memory]:
        """Text-based memory search"""
        try:
            async with db_manager.session() as session:
                # Simple text search using PostgreSQL
                query_lower = f"%{query.lower()}%"
                
                result = await session.execute(
                    select(Memory).where(
                        and_(
                            Memory.user_id == user_id,
                            or_(
                                func.lower(Memory.content).like(query_lower),
                                func.lower(Memory.summary).like(query_lower),
                                func.lower(Memory.title).like(query_lower)
                            ),
                            Memory.deleted_at.is_(None)
                        )
                    ).order_by(Memory.importance.desc()).limit(limit)
                )
                
                return list(result.scalars().all())
                
        except Exception as e:
            logger.error(f"Text search failed: {e}")
            return []
    
    async def vector_search(
        self,
        user_id: str,
        query: str,
        limit: int = 20
    ) -> List[Memory]:
        """Vector-based semantic search"""
        try:
            # Generate query embedding
            query_embedding = await embedding_service.generate_embedding(query)
            
            # Search in vector store
            results = await vector_store.search_memories(
                query_vector=query_embedding,
                user_id=user_id,
                limit=limit,
                score_threshold=0.5
            )
            
            # Fetch full memories from database
            memory_ids = [r['id'] for r in results]
            
            if memory_ids:
                async with db_manager.session() as session:
                    result = await session.execute(
                        select(Memory).where(Memory.id.in_(memory_ids))
                    )
                    memories = list(result.scalars().all())
                    
                    # Sort by vector search score
                    memory_dict = {str(m.id): m for m in memories}
                    sorted_memories = []
                    for r in results:
                        if r['id'] in memory_dict:
                            sorted_memories.append(memory_dict[r['id']])
                    
                    return sorted_memories
            
            return []
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    async def hybrid_search(
        self,
        user_id: str,
        query: str,
        limit: int = 20
    ) -> List[Memory]:
        """Hybrid text and vector search"""
        try:
            # Run both searches concurrently
            text_task = asyncio.create_task(
                self.text_search(user_id, query, limit)
            )
            vector_task = asyncio.create_task(
                self.vector_search(user_id, query, limit)
            )
            
            text_results, vector_results = await asyncio.gather(
                text_task,
                vector_task
            )
            
            # Merge and deduplicate results
            seen_ids = set()
            merged_results = []
            
            # Interleave results for balanced ranking
            for i in range(max(len(text_results), len(vector_results))):
                if i < len(vector_results):
                    memory = vector_results[i]
                    if memory.id not in seen_ids:
                        merged_results.append(memory)
                        seen_ids.add(memory.id)
                
                if i < len(text_results):
                    memory = text_results[i]
                    if memory.id not in seen_ids:
                        merged_results.append(memory)
                        seen_ids.add(memory.id)
                
                if len(merged_results) >= limit:
                    break
            
            return merged_results[:limit]
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return []


# Export classes
__all__ = [
    'MemoryService',
    'MemorySearchService',
]