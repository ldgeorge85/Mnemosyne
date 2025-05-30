"""
Memory API endpoints.

This module provides API endpoints for creating, retrieving, updating,
and deleting memories, as well as searching and managing memory chunks.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.db.repositories.memory import MemoryRepository, MemoryChunkRepository
from app.schemas.memory import (
    MemoryCreate,
    MemoryUpdate,
    MemoryResponse,
    MemoryWithChunksResponse,
    MemoryChunkCreate,
    MemoryChunkUpdate,
    MemoryChunkResponse,
    MemorySearchQuery,
    MemorySearchResponse,
    MemoryStatistics
)

router = APIRouter()


@router.post("/", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(
    memory_data: MemoryCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user_id: str = Depends(deps.get_current_user_id)
) -> MemoryResponse:
    """
    Create a new memory.
    
    Args:
        memory_data: Data for creating the memory
        db: Database session
        current_user_id: ID of the current authenticated user
        
    Returns:
        The newly created memory
        
    Raises:
        HTTPException: If the user doesn't have permission to create memories
    """
    # Ensure the user can only create memories for themselves
    if memory_data.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create memories for yourself"
        )
    
    memory_repo = MemoryRepository(db)
    memory = await memory_repo.create_memory(memory_data.dict())
    return memory


@router.get("/{memory_id}", response_model=MemoryWithChunksResponse)
async def get_memory(
    memory_id: str = Path(..., description="The ID of the memory to retrieve"),
    include_chunks: bool = Query(False, description="Whether to include memory chunks"),
    db: AsyncSession = Depends(deps.get_db),
    current_user_id: str = Depends(deps.get_current_user_id)
) -> MemoryWithChunksResponse:
    """
    Get a memory by ID.
    
    Args:
        memory_id: ID of the memory to retrieve
        include_chunks: Whether to include memory chunks in the response
        db: Database session
        current_user_id: ID of the current authenticated user
        
    Returns:
        The requested memory
        
    Raises:
        HTTPException: If the memory doesn't exist or user doesn't have permission
    """
    memory_repo = MemoryRepository(db)
    memory = await memory_repo.get_memory_by_id(memory_id)
    
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory with ID {memory_id} not found"
        )
    
    # Check user permission
    if memory.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this memory"
        )
    
    # Update access stats
    await memory_repo.update_access_stats(memory_id)
    
    # Include chunks if requested
    if include_chunks:
        chunk_repo = MemoryChunkRepository(db)
        chunks = await chunk_repo.get_chunks_by_memory_id(memory_id)
        memory_response = MemoryWithChunksResponse.from_orm(memory)
        memory_response.chunks = chunks
        return memory_response
    
    return MemoryWithChunksResponse.from_orm(memory)


@router.get("/", response_model=List[MemoryResponse])
async def list_memories(
    limit: int = Query(50, description="Maximum number of memories to return"),
    offset: int = Query(0, description="Number of memories to skip for pagination"),
    include_inactive: bool = Query(False, description="Whether to include inactive memories"),
    db: AsyncSession = Depends(deps.get_db),
    current_user_id: str = Depends(deps.get_current_user_id)
) -> List[MemoryResponse]:
    """
    List memories for the current user.
    
    Args:
        limit: Maximum number of memories to return
        offset: Number of memories to skip for pagination
        include_inactive: Whether to include inactive memories
        db: Database session
        current_user_id: ID of the current authenticated user
        
    Returns:
        List of memories
    """
    memory_repo = MemoryRepository(db)
    memories, _ = await memory_repo.get_memories_by_user_id(
        current_user_id, 
        limit=limit,
        offset=offset,
        include_inactive=include_inactive
    )
    return memories


@router.put("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_data: MemoryUpdate,
    memory_id: str = Path(..., description="The ID of the memory to update"),
    db: AsyncSession = Depends(deps.get_db),
    current_user_id: str = Depends(deps.get_current_user_id)
) -> MemoryResponse:
    """
    Update a memory.
    
    Args:
        memory_data: Data for updating the memory
        memory_id: ID of the memory to update
        db: Database session
        current_user_id: ID of the current authenticated user
        
    Returns:
        The updated memory
        
    Raises:
        HTTPException: If the memory doesn't exist or user doesn't have permission
    """
    memory_repo = MemoryRepository(db)
    memory = await memory_repo.get_memory_by_id(memory_id)
    
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory with ID {memory_id} not found"
        )
    
    # Check user permission
    if memory.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this memory"
        )
    
    updated_memory = await memory_repo.update_memory(memory_id, memory_data.dict(exclude_unset=True))
    return updated_memory


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    memory_id: str = Path(..., description="The ID of the memory to delete"),
    permanent: bool = Query(False, description="Whether to permanently delete the memory"),
    db: AsyncSession = Depends(deps.get_db),
    current_user_id: str = Depends(deps.get_current_user_id)
) -> None:
    """
    Delete a memory.
    
    Args:
        memory_id: ID of the memory to delete
        permanent: Whether to permanently delete (True) or soft delete (False)
        db: Database session
        current_user_id: ID of the current authenticated user
        
    Raises:
        HTTPException: If the memory doesn't exist or user doesn't have permission
    """
    memory_repo = MemoryRepository(db)
    memory = await memory_repo.get_memory_by_id(memory_id)
    
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory with ID {memory_id} not found"
        )
    
    # Check user permission
    if memory.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this memory"
        )
    
    if permanent:
        await memory_repo.delete_memory(memory_id)
    else:
        await memory_repo.soft_delete_memory(memory_id)


@router.get("/tag/{tag}", response_model=List[MemoryResponse])
async def get_memories_by_tag(
    tag: str = Path(..., description="The tag to filter memories by"),
    limit: int = Query(50, description="Maximum number of memories to return"),
    offset: int = Query(0, description="Number of memories to skip for pagination"),
    include_inactive: bool = Query(False, description="Whether to include inactive memories"),
    db: AsyncSession = Depends(deps.get_db),
    current_user_id: str = Depends(deps.get_current_user_id)
) -> List[MemoryResponse]:
    """
    Get memories by tag.
    
    Args:
        tag: Tag to filter memories by
        limit: Maximum number of memories to return
        offset: Number of memories to skip for pagination
        include_inactive: Whether to include inactive memories
        db: Database session
        current_user_id: ID of the current authenticated user
        
    Returns:
        List of memories with the specified tag
    """
    memory_repo = MemoryRepository(db)
    memories, _ = await memory_repo.get_memories_by_tag(
        current_user_id,
        tag,
        limit=limit,
        offset=offset,
        include_inactive=include_inactive
    )
    return memories


@router.post("/search", response_model=MemorySearchResponse)
async def search_memories(
    search_query: MemorySearchQuery,
    db: AsyncSession = Depends(deps.get_db),
    current_user_id: str = Depends(deps.get_current_user_id)
) -> MemorySearchResponse:
    """
    Search memories by text.
    
    Args:
        search_query: Search parameters
        db: Database session
        current_user_id: ID of the current authenticated user
        
    Returns:
        Search results
        
    Raises:
        HTTPException: If the user doesn't have permission to search memories
    """
    # Ensure the user can only search their own memories
    if search_query.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only search your own memories"
        )
    
    memory_repo = MemoryRepository(db)
    memories = await memory_repo.search_memories_by_text(
        current_user_id,
        search_query.query,
        limit=search_query.limit,
        include_inactive=search_query.include_inactive
    )
    
    # Include chunks if requested
    if search_query.include_chunks and memories:
        chunk_repo = MemoryChunkRepository(db)
        results = []
        
        for memory in memories:
            chunks = await chunk_repo.get_chunks_by_memory_id(memory.id)
            memory_with_chunks = MemoryWithChunksResponse.from_orm(memory)
            memory_with_chunks.chunks = chunks
            results.append(memory_with_chunks)
    else:
        results = memories
    
    return MemorySearchResponse(
        query=search_query.query,
        results=results,
        total=len(results)
    )


# Memory Chunk endpoints

@router.post("/chunks", response_model=MemoryChunkResponse, status_code=status.HTTP_201_CREATED)
async def create_memory_chunk(
    chunk_data: MemoryChunkCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user_id: str = Depends(deps.get_current_user_id)
) -> MemoryChunkResponse:
    """
    Create a new memory chunk.
    
    Args:
        chunk_data: Data for creating the memory chunk
        db: Database session
        current_user_id: ID of the current authenticated user
        
    Returns:
        The newly created memory chunk
        
    Raises:
        HTTPException: If the parent memory doesn't exist or user doesn't have permission
    """
    # Check if parent memory exists and user has permission
    memory_repo = MemoryRepository(db)
    memory = await memory_repo.get_memory_by_id(chunk_data.memory_id)
    
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parent memory with ID {chunk_data.memory_id} not found"
        )
    
    if memory.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to add chunks to this memory"
        )
    
    chunk_repo = MemoryChunkRepository(db)
    chunk = await chunk_repo.create_chunk(chunk_data.dict())
    return chunk


@router.get("/chunks/{chunk_id}", response_model=MemoryChunkResponse)
async def get_memory_chunk(
    chunk_id: str = Path(..., description="The ID of the memory chunk to retrieve"),
    db: AsyncSession = Depends(deps.get_db),
    current_user_id: str = Depends(deps.get_current_user_id)
) -> MemoryChunkResponse:
    """
    Get a memory chunk by ID.
    
    Args:
        chunk_id: ID of the memory chunk to retrieve
        db: Database session
        current_user_id: ID of the current authenticated user
        
    Returns:
        The requested memory chunk
        
    Raises:
        HTTPException: If the chunk doesn't exist or user doesn't have permission
    """
    chunk_repo = MemoryChunkRepository(db)
    chunk = await chunk_repo.get_chunk_by_id(chunk_id)
    
    if not chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory chunk with ID {chunk_id} not found"
        )
    
    # Check if user has permission to access the parent memory
    memory_repo = MemoryRepository(db)
    memory = await memory_repo.get_memory_by_id(chunk.memory_id)
    
    if memory.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this memory chunk"
        )
    
    return chunk


@router.get("/memories/{memory_id}/chunks", response_model=List[MemoryChunkResponse])
async def get_memory_chunks(
    memory_id: str = Path(..., description="The ID of the memory to get chunks for"),
    db: AsyncSession = Depends(deps.get_db),
    current_user_id: str = Depends(deps.get_current_user_id)
) -> List[MemoryChunkResponse]:
    """
    Get all chunks for a memory.
    
    Args:
        memory_id: ID of the memory to get chunks for
        db: Database session
        current_user_id: ID of the current authenticated user
        
    Returns:
        List of memory chunks
        
    Raises:
        HTTPException: If the memory doesn't exist or user doesn't have permission
    """
    # Check if memory exists and user has permission
    memory_repo = MemoryRepository(db)
    memory = await memory_repo.get_memory_by_id(memory_id)
    
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory with ID {memory_id} not found"
        )
    
    if memory.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access chunks for this memory"
        )
    
    chunk_repo = MemoryChunkRepository(db)
    chunks = await chunk_repo.get_chunks_by_memory_id(memory_id)
    return chunks


@router.put("/chunks/{chunk_id}", response_model=MemoryChunkResponse)
async def update_memory_chunk(
    chunk_data: MemoryChunkUpdate,
    chunk_id: str = Path(..., description="The ID of the memory chunk to update"),
    db: AsyncSession = Depends(deps.get_db),
    current_user_id: str = Depends(deps.get_current_user_id)
) -> MemoryChunkResponse:
    """
    Update a memory chunk.
    
    Args:
        chunk_data: Data for updating the memory chunk
        chunk_id: ID of the memory chunk to update
        db: Database session
        current_user_id: ID of the current authenticated user
        
    Returns:
        The updated memory chunk
        
    Raises:
        HTTPException: If the chunk doesn't exist or user doesn't have permission
    """
    chunk_repo = MemoryChunkRepository(db)
    chunk = await chunk_repo.get_chunk_by_id(chunk_id)
    
    if not chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory chunk with ID {chunk_id} not found"
        )
    
    # Check if user has permission to access the parent memory
    memory_repo = MemoryRepository(db)
    memory = await memory_repo.get_memory_by_id(chunk.memory_id)
    
    if memory.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this memory chunk"
        )
    
    updated_chunk = await chunk_repo.update_chunk(chunk_id, chunk_data.dict(exclude_unset=True))
    return updated_chunk


@router.delete("/chunks/{chunk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory_chunk(
    chunk_id: str = Path(..., description="The ID of the memory chunk to delete"),
    db: AsyncSession = Depends(deps.get_db),
    current_user_id: str = Depends(deps.get_current_user_id)
) -> None:
    """
    Delete a memory chunk.
    
    Args:
        chunk_id: ID of the memory chunk to delete
        db: Database session
        current_user_id: ID of the current authenticated user
        
    Raises:
        HTTPException: If the chunk doesn't exist or user doesn't have permission
    """
    chunk_repo = MemoryChunkRepository(db)
    chunk = await chunk_repo.get_chunk_by_id(chunk_id)
    
    if not chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory chunk with ID {chunk_id} not found"
        )
    
    # Check if user has permission to access the parent memory
    memory_repo = MemoryRepository(db)
    memory = await memory_repo.get_memory_by_id(chunk.memory_id)
    
    if memory.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this memory chunk"
        )
    
    await chunk_repo.delete_chunk(chunk_id)
