"""
Memory Retrieval API endpoints.

This module provides API endpoints for retrieving memories using similarity search,
tag filtering, and hybrid search approaches.
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from app.db.session import get_async_db
from app.api.dependencies.auth import get_current_user
from app.services.memory import memory_retrieval_service
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()


class MemorySearchQuery(BaseModel):
    """Schema for a memory search query."""
    query: str = Field(..., description="Search query text")
    tags: Optional[List[str]] = Field(None, description="Optional tags to filter by")
    min_relevance_score: float = Field(0.7, ge=0.0, le=1.0, description="Minimum relevance score (0-1)")
    limit: int = Field(10, ge=1, le=50, description="Maximum number of results to return")


class MemoryTagSearchQuery(BaseModel):
    """Schema for a memory tag search query."""
    tags: List[str] = Field(..., min_items=1, description="Tags to search for")
    limit: int = Field(10, ge=1, le=50, description="Maximum number of results to return")
    offset: int = Field(0, ge=0, description="Offset for pagination")


class MemoryResponse(BaseModel):
    """Schema for a memory response."""
    id: str = Field(..., description="Memory ID")
    title: str = Field(..., description="Memory title")
    content: str = Field(..., description="Memory content")
    tags: List[str] = Field(default_factory=list, description="Memory tags")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    last_accessed_at: Optional[str] = Field(None, description="Last access timestamp")
    access_count: int = Field(0, description="Number of times the memory has been accessed")
    relevance_score: Optional[float] = Field(None, description="Relevance score for the search query")
    matching_content: Optional[str] = Field(None, description="Content that matched the query")


class MemoryListResponse(BaseModel):
    """Schema for a list of memory responses."""
    memories: List[MemoryResponse] = Field(..., description="List of memories")
    total_count: int = Field(..., description="Total number of matching memories")


@router.post("/search", response_model=MemoryListResponse)
async def search_memories(
    query: MemorySearchQuery,
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> MemoryListResponse:
    """
    Search for memories by similarity to the query text.
    
    Args:
        query: Search query parameters
        db: Database session
        current_user_id: ID of the authenticated user
        
    Returns:
        List of memories with relevance scores
    """
    # Perform hybrid search (vector similarity + tag filtering)
    memories = await memory_retrieval_service.retrieve_by_hybrid_search(
        query_text=query.query,
        tags=query.tags,
        user_id=current_user_id,
        db=db,
        limit=query.limit,
        min_relevance_score=query.min_relevance_score
    )
    
    if not memories:
        return MemoryListResponse(memories=[], total_count=0)
    
    # Format response
    memory_responses = [
        MemoryResponse(
            id=memory["id"],
            title=memory["title"],
            content=memory["content"],
            tags=memory.get("tags", []),
            created_at=memory["created_at"].isoformat(),
            updated_at=memory["updated_at"].isoformat(),
            last_accessed_at=memory["last_accessed_at"].isoformat() if memory.get("last_accessed_at") else None,
            access_count=memory.get("access_count", 0),
            relevance_score=memory.get("relevance_score"),
            matching_content=memory.get("matching_content")
        )
        for memory in memories
    ]
    
    return MemoryListResponse(
        memories=memory_responses,
        total_count=len(memory_responses)
    )


@router.post("/tags", response_model=MemoryListResponse)
async def search_memories_by_tags(
    query: MemoryTagSearchQuery,
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> MemoryListResponse:
    """
    Search for memories by tags.
    
    Args:
        query: Tag search query parameters
        db: Database session
        current_user_id: ID of the authenticated user
        
    Returns:
        List of memories matching the tags
    """
    # Search by tags
    memories = await memory_retrieval_service.retrieve_by_tags(
        tags=query.tags,
        user_id=current_user_id,
        db=db,
        limit=query.limit,
        offset=query.offset
    )
    
    if not memories:
        return MemoryListResponse(memories=[], total_count=0)
    
    # Format response
    memory_responses = [
        MemoryResponse(
            id=memory["id"],
            title=memory["title"],
            content=memory["content"],
            tags=memory.get("tags", []),
            created_at=memory["created_at"].isoformat(),
            updated_at=memory["updated_at"].isoformat(),
            last_accessed_at=memory["last_accessed_at"].isoformat() if memory.get("last_accessed_at") else None,
            access_count=memory.get("access_count", 0)
        )
        for memory in memories
    ]
    
    return MemoryListResponse(
        memories=memory_responses,
        total_count=len(memory_responses)
    )


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> MemoryResponse:
    """
    Get a memory by its ID.
    
    Args:
        memory_id: ID of the memory to retrieve
        db: Database session
        current_user_id: ID of the authenticated user
        
    Returns:
        Memory data
    """
    memory = await memory_retrieval_service.get_memory_by_id(
        memory_id=memory_id,
        user_id=current_user_id,
        db=db
    )
    
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory with ID {memory_id} not found"
        )
    
    return MemoryResponse(
        id=memory["id"],
        title=memory["title"],
        content=memory["content"],
        tags=memory.get("tags", []),
        created_at=memory["created_at"].isoformat(),
        updated_at=memory["updated_at"].isoformat(),
        last_accessed_at=memory["last_accessed_at"].isoformat() if memory.get("last_accessed_at") else None,
        access_count=memory.get("access_count", 0)
    )
