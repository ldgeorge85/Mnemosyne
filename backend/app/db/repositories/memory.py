"""
Memory repository for database operations related to memories and memory chunks.

This module provides classes for CRUD operations on memories and memory chunks,
allowing for efficient storage, retrieval, and management of the memory system.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import update, delete, func, select, or_, and_, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.memory import Memory, MemoryChunk
from app.db.repositories.base import BaseRepository


class MemoryRepository(BaseRepository):
    """
    Repository for memory-related database operations.
    
    This class handles CRUD operations for memories, including
    creation, retrieval, updating, and deletion.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize the memory repository with a database session.
        
        Args:
            session: The database session to use for operations
        """
        super().__init__(session, Memory)
    
    async def create_memory(self, memory_data: Dict[str, Any]) -> Memory:
        """
        Create a new memory in the database.
        
        Args:
            memory_data: Dictionary containing memory data fields
            
        Returns:
            The newly created Memory instance
        """
        memory = Memory(**memory_data)
        self.session.add(memory)
        await self.session.commit()
        await self.session.refresh(memory)
        return memory
    
    async def get_memory_by_id(self, memory_id: str) -> Optional[Memory]:
        """
        Retrieve a memory by its ID.
        
        Args:
            memory_id: The UUID of the memory to retrieve
            
        Returns:
            The Memory instance if found, None otherwise
        """
        query = select(Memory).where(Memory.id == memory_id)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_memories_by_user_id(
        self, 
        user_id, 
        limit: int = 100, 
        offset: int = 0,
        include_inactive: bool = False
    ) -> Tuple[List[Memory], int]:
        """
        Retrieve memories for a specific user.
        
        Args:
            user_id: The user ID (can be UUID object or string)
            limit: Maximum number of memories to return
            offset: Number of memories to skip for pagination
            include_inactive: Whether to include inactive memories
            
        Returns:
            Tuple of (list of Memory instances, total count)
        """
        # Convert user_id string to UUID for comparison
        import uuid
        if isinstance(user_id, str):
            user_uuid = uuid.UUID(user_id)
        else:
            user_uuid = user_id
        filters = [Memory.user_id == user_uuid]
        if not include_inactive:
            filters.append(Memory.is_active == True)
        
        # Get total count
        count_query = select(func.count(Memory.id)).where(and_(*filters))
        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar() or 0
        
        # Get actual records
        query = (
            select(Memory)
            .where(and_(*filters))
            .order_by(Memory.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        memories = result.scalars().all()
        
        return list(memories), total_count
    
    async def search_memories_by_text(
        self, 
        user_id: str, 
        search_text: str,
        limit: int = 20,
        include_inactive: bool = False
    ) -> List[Memory]:
        """
        Search memories by text content.
        
        Args:
            user_id: The user ID (can be UUID object or string)
            search_text: The text to search for
            limit: Maximum number of memories to return
            include_inactive: Whether to include inactive memories
            
        Returns:
            List of Memory instances matching the search
        """
        filters = [
            Memory.user_id.cast(String) == user_id,
            or_(
                Memory.title.ilike(f"%{search_text}%"),
                Memory.content.ilike(f"%{search_text}%"),
            )
        ]
        
        if not include_inactive:
            filters.append(Memory.is_active == True)
        
        # Use explicit column selection to avoid issues with schema mismatches
        query = (
            select(
                Memory.user_id,
                Memory.title,
                Memory.content,
                Memory.embedding,
                # Memory.embedding_model,  # Commented out to avoid schema mismatch
                Memory.source,
                Memory.source_type,
                Memory.source_id,
                Memory.memory_metadata,
                Memory.importance,
                Memory.last_accessed_at,
                Memory.access_count,
                Memory.is_active,
                Memory.tags,
                Memory.id,
                Memory.created_at,
                Memory.updated_at
            )
            .where(and_(*filters))
            .order_by(Memory.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update_memory(self, memory_id: str, memory_data: Dict[str, Any]) -> Optional[Memory]:
        """
        Update an existing memory.
        
        Args:
            memory_id: The UUID of the memory to update
            memory_data: Dictionary containing fields to update
            
        Returns:
            The updated Memory instance if found, None otherwise
        """
        memory = await self.get_memory_by_id(memory_id)
        if not memory:
            return None
        
        # Update only the provided fields
        for key, value in memory_data.items():
            if hasattr(memory, key):
                setattr(memory, key, value)
        
        # Update the last modified timestamp
        memory.updated_at = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(memory)
        return memory
    
    async def update_access_stats(self, memory_id: str) -> Optional[Memory]:
        """
        Update access statistics for a memory.
        
        Args:
            memory_id: The UUID of the memory to update
            
        Returns:
            The updated Memory instance if found, None otherwise
        """
        memory = await self.get_memory_by_id(memory_id)
        if not memory:
            return None
        
        memory.last_accessed_at = datetime.utcnow()
        memory.access_count += 1
        
        await self.session.commit()
        await self.session.refresh(memory)
        return memory
    
    async def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory by its ID.
        
        Args:
            memory_id: The UUID of the memory to delete
            
        Returns:
            True if the memory was deleted, False otherwise
        """
        memory = await self.get_memory_by_id(memory_id)
        if not memory:
            return False
        
        await self.session.delete(memory)
        await self.session.commit()
        return True
    
    async def soft_delete_memory(self, memory_id: str) -> Optional[Memory]:
        """
        Soft delete a memory by marking it as inactive.
        
        Args:
            memory_id: The UUID of the memory to soft delete
            
        Returns:
            The updated Memory instance if found, None otherwise
        """
        memory = await self.get_memory_by_id(memory_id)
        if not memory:
            return None
        
        memory.is_active = False
        memory.updated_at = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(memory)
        return memory
    
    async def get_memories_by_tag(
        self, 
        user_id: str, 
        tag: str,
        limit: int = 50,
        offset: int = 0,
        include_inactive: bool = False
    ) -> Tuple[List[Memory], int]:
        """
        Retrieve memories that have a specific tag.
        
        Args:
            user_id: The user ID (can be UUID object or string)
            tag: The tag to search for
            limit: Maximum number of memories to return
            offset: Number of memories to skip for pagination
            include_inactive: Whether to include inactive memories
            
        Returns:
            Tuple of (list of Memory instances, total count)
        """
        filters = [
            Memory.user_id.cast(String) == user_id,
            Memory.tags.contains([tag])
        ]
        
        if not include_inactive:
            filters.append(Memory.is_active == True)
        
        # Get total count
        count_query = select(func.count(Memory.id)).where(and_(*filters))
        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar() or 0
        
        # Get actual records
        query = (
            select(Memory)
            .where(and_(*filters))
            .order_by(Memory.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        memories = result.scalars().all()
        
        return list(memories), total_count


class MemoryChunkRepository(BaseRepository):
    """
    Repository for memory chunk-related database operations.
    
    This class handles CRUD operations for memory chunks, which are
    segments of memories used for efficient vector similarity search.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize the memory chunk repository with a database session.
        
        Args:
            session: The database session to use for operations
        """
        super().__init__(session, MemoryChunk)
    
    async def create_chunk(self, chunk_data: Dict[str, Any]) -> MemoryChunk:
        """
        Create a new memory chunk in the database.
        
        Args:
            chunk_data: Dictionary containing chunk data fields
            
        Returns:
            The newly created MemoryChunk instance
        """
        chunk = MemoryChunk(**chunk_data)
        self.session.add(chunk)
        await self.session.commit()
        await self.session.refresh(chunk)
        return chunk
    
    async def create_chunks_batch(self, chunks_data: List[Dict[str, Any]]) -> List[MemoryChunk]:
        """
        Create multiple memory chunks in a batch operation.
        
        Args:
            chunks_data: List of dictionaries containing chunk data
            
        Returns:
            List of the newly created MemoryChunk instances
        """
        chunks = [MemoryChunk(**data) for data in chunks_data]
        self.session.add_all(chunks)
        await self.session.commit()
        
        # Refresh all chunks
        for chunk in chunks:
            await self.session.refresh(chunk)
        
        return chunks
    
    async def get_chunk_by_id(self, chunk_id: str) -> Optional[MemoryChunk]:
        """
        Retrieve a memory chunk by its ID.
        
        Args:
            chunk_id: The UUID of the chunk to retrieve
            
        Returns:
            The MemoryChunk instance if found, None otherwise
        """
        query = select(MemoryChunk).where(MemoryChunk.id == chunk_id)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_chunks_by_memory_id(self, memory_id: str) -> List[MemoryChunk]:
        """
        Retrieve all chunks for a specific memory.
        
        Args:
            memory_id: The UUID of the memory
            
        Returns:
            List of MemoryChunk instances belonging to the memory
        """
        query = (
            select(MemoryChunk)
            .where(MemoryChunk.memory_id == memory_id)
            .order_by(MemoryChunk.chunk_index)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update_chunk(self, chunk_id: str, chunk_data: Dict[str, Any]) -> Optional[MemoryChunk]:
        """
        Update an existing memory chunk.
        
        Args:
            chunk_id: The UUID of the chunk to update
            chunk_data: Dictionary containing fields to update
            
        Returns:
            The updated MemoryChunk instance if found, None otherwise
        """
        chunk = await self.get_chunk_by_id(chunk_id)
        if not chunk:
            return None
        
        # Update only the provided fields
        for key, value in chunk_data.items():
            if hasattr(chunk, key):
                setattr(chunk, key, value)
        
        # Update the last modified timestamp
        chunk.updated_at = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(chunk)
        return chunk
    
    async def delete_chunk(self, chunk_id: str) -> bool:
        """
        Delete a memory chunk by its ID.
        
        Args:
            chunk_id: The UUID of the chunk to delete
            
        Returns:
            True if the chunk was deleted, False otherwise
        """
        chunk = await self.get_chunk_by_id(chunk_id)
        if not chunk:
            return False
        
        await self.session.delete(chunk)
        await self.session.commit()
        return True
    
    async def delete_chunks_by_memory_id(self, memory_id: str) -> int:
        """
        Delete all chunks for a specific memory.
        
        Args:
            memory_id: The UUID of the memory
            
        Returns:
            Number of chunks deleted
        """
        chunks = await self.get_chunks_by_memory_id(memory_id)
        count = len(chunks)
        
        for chunk in chunks:
            await self.session.delete(chunk)
        
        await self.session.commit()
        return count
