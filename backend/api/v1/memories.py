"""
Memory management endpoints for Mnemosyne Protocol
"""

from typing import List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import uuid

from api.deps import get_db, get_current_active_user
from models.user import User
from models.memory import Memory
from services.memory_service import MemoryService
from services.embedding import EmbeddingService
from core.vectors import VectorStore

router = APIRouter()


# Pydantic models
class MemoryCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)
    metadata: Optional[dict] = None
    importance: Optional[float] = Field(None, ge=0.0, le=1.0)
    domains: Optional[List[str]] = None


class MemoryUpdate(BaseModel):
    content: Optional[str] = Field(None, max_length=10000)
    metadata: Optional[dict] = None
    importance: Optional[float] = Field(None, ge=0.0, le=1.0)
    domains: Optional[List[str]] = None


class MemoryResponse(BaseModel):
    id: str
    content: str
    metadata: Optional[dict]
    importance: float
    domains: List[str]
    created_at: datetime
    last_accessed: Optional[datetime]
    consolidation_count: int
    
    class Config:
        from_attributes = True


class MemorySearch(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    limit: int = Field(10, ge=1, le=100)
    threshold: float = Field(0.7, ge=0.0, le=1.0)
    domains: Optional[List[str]] = None


class ConsolidationRequest(BaseModel):
    memory_ids: List[str] = Field(..., min_items=2, max_items=100)


@router.post("/", response_model=MemoryResponse)
async def create_memory(
    memory_data: MemoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create a new memory for the current user
    """
    # Initialize services
    memory_service = MemoryService(db)
    embedding_service = EmbeddingService()
    
    # Generate embedding
    embedding = await embedding_service.generate_embedding(memory_data.content)
    
    # Create memory
    memory = Memory(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        content=memory_data.content,
        embedding=embedding,
        metadata=memory_data.metadata or {},
        importance=memory_data.importance or 0.5,
        domains=memory_data.domains or [],
        consolidation_count=0
    )
    
    db.add(memory)
    await db.commit()
    await db.refresh(memory)
    
    # Store in vector database
    vector_store = await VectorStore.get_instance()
    await vector_store.store_memory(memory)
    
    return memory


@router.get("/", response_model=List[MemoryResponse])
async def list_memories(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get list of user's memories with pagination
    """
    result = await db.execute(
        select(Memory)
        .where(Memory.user_id == current_user.id)
        .order_by(desc(Memory.created_at))
        .offset(skip)
        .limit(limit)
    )
    memories = result.scalars().all()
    
    return memories


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get a specific memory by ID
    """
    memory = await db.get(Memory, memory_id)
    
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found"
        )
    
    if memory.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this memory"
        )
    
    # Update last accessed time
    memory.last_accessed = datetime.utcnow()
    await db.commit()
    
    return memory


@router.put("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: str,
    memory_update: MemoryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Update a memory
    """
    memory = await db.get(Memory, memory_id)
    
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found"
        )
    
    if memory.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this memory"
        )
    
    # Update fields
    if memory_update.content is not None:
        memory.content = memory_update.content
        # Regenerate embedding
        embedding_service = EmbeddingService()
        memory.embedding = await embedding_service.generate_embedding(memory_update.content)
    
    if memory_update.metadata is not None:
        memory.metadata = memory_update.metadata
    
    if memory_update.importance is not None:
        memory.importance = memory_update.importance
    
    if memory_update.domains is not None:
        memory.domains = memory_update.domains
    
    await db.commit()
    await db.refresh(memory)
    
    # Update in vector store
    vector_store = await VectorStore.get_instance()
    await vector_store.update_memory(memory)
    
    return memory


@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Delete a memory
    """
    memory = await db.get(Memory, memory_id)
    
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found"
        )
    
    if memory.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this memory"
        )
    
    # Delete from vector store
    vector_store = await VectorStore.get_instance()
    await vector_store.delete_memory(memory_id)
    
    # Delete from database
    await db.delete(memory)
    await db.commit()
    
    return {"message": "Memory deleted successfully"}


@router.post("/search", response_model=List[MemoryResponse])
async def search_memories(
    search_data: MemorySearch,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Search memories using vector similarity
    """
    vector_store = await VectorStore.get_instance()
    embedding_service = EmbeddingService()
    
    # Generate query embedding
    query_embedding = await embedding_service.generate_embedding(search_data.query)
    
    # Search in vector store
    results = await vector_store.search_memories(
        query_embedding=query_embedding,
        user_id=current_user.id,
        limit=search_data.limit,
        threshold=search_data.threshold,
        domains=search_data.domains
    )
    
    # Get full memory objects
    memory_ids = [r["id"] for r in results]
    if not memory_ids:
        return []
    
    result = await db.execute(
        select(Memory).where(Memory.id.in_(memory_ids))
    )
    memories = result.scalars().all()
    
    # Sort by similarity score
    memory_dict = {m.id: m for m in memories}
    sorted_memories = [memory_dict[r["id"]] for r in results if r["id"] in memory_dict]
    
    return sorted_memories


@router.post("/consolidate", response_model=MemoryResponse)
async def consolidate_memories(
    consolidation_data: ConsolidationRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Consolidate multiple memories into a new synthesized memory
    """
    # Get memories to consolidate
    result = await db.execute(
        select(Memory).where(
            Memory.id.in_(consolidation_data.memory_ids),
            Memory.user_id == current_user.id
        )
    )
    memories = result.scalars().all()
    
    if len(memories) != len(consolidation_data.memory_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some memories not found or not authorized"
        )
    
    # Perform consolidation
    memory_service = MemoryService(db)
    consolidated = await memory_service.consolidate_memories(memories, current_user.id)
    
    # Update consolidation count for source memories
    for memory in memories:
        memory.consolidation_count += 1
    
    await db.commit()
    
    return consolidated