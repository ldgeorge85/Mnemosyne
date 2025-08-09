"""
API endpoints for memory reflection and importance scoring (Phase 3, Cognee integration).
"""
import logging
from fastapi import APIRouter, status, Path, Query
from typing import List, Dict, Any

# Import memory schemas for request/response validation
from app.schemas.memory import MemoryResponse, MemoryCreate, MemoryUpdate, MemoryWithChunksResponse, MemorySearchResponse, MemorySearchQuery, MemoryStatistics, MemoryChunkResponse, MemoryChunkCreate, MemoryChunkUpdate

from app.services.memory.reflection import MemoryReflectionService
from fastapi import Depends, HTTPException, APIRouter, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db
from app.api.dependencies.auth import get_current_user, get_current_user_from_token_or_api_key
from app.api.dependencies.auth_dev import get_current_user_dev
from app.core.config import settings
from app.db.session import async_session_maker
from app.db.repositories.memory import MemoryRepository, MemoryChunkRepository

logger = logging.getLogger(__name__)

router = APIRouter(tags=["memories"])

@router.post("/reflect")
async def reflect_memory(
    agent_id: str = Body(...), 
    memories: list = Body(...),
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user_dev if not settings.AUTH_REQUIRED else get_current_user_from_token_or_api_key)
):
    """
    Trigger memory reflection/scoring for an agent.
    
    Args:
        agent_id: ID of the agent to reflect memories for
        memories: List of memories to reflect on
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Reflection result
    """
    reflection_service = MemoryReflectionService(db)
    result = await reflection_service.reflect(agent_id, memories)
    return {"reflection": result}

@router.get("/importance")
async def get_importance(
    agent_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user_dev if not settings.AUTH_REQUIRED else get_current_user_from_token_or_api_key)
):
    """
    Retrieve importance scores for memories for a given agent.
    
    Args:
        agent_id: ID of the agent to get importance scores for
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Dictionary of importance scores
    """
    reflection_service = MemoryReflectionService(db)
    scores = await reflection_service.get_importance_scores(agent_id)
    return {"scores": scores}

@router.get("/hierarchy")
async def get_hierarchy(
    agent_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user_dev if not settings.AUTH_REQUIRED else get_current_user_from_token_or_api_key)
):
    """
    Get hierarchical organization of memories for a given agent.
    
    Args:
        agent_id: ID of the agent to get memory hierarchy for
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Hierarchical organization of memories
    """
    reflection_service = MemoryReflectionService(db)
    hierarchy = await reflection_service.get_hierarchy(agent_id)
    return hierarchy


@router.post("/", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(
    memory_data: MemoryCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user_dev if not settings.AUTH_REQUIRED else get_current_user_from_token_or_api_key)
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
    if memory_data.user_id != str(current_user.id):
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
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user_dev if not settings.AUTH_REQUIRED else get_current_user_from_token_or_api_key)
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
    if memory.user_id != str(current_user.id):
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
    db: AsyncSession = Depends(get_async_db)
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
    # For development, use a default user ID
    dev_user_id = "00000000-0000-0000-0000-000000000000"
    memory_repo = MemoryRepository(db)
    memories, _ = await memory_repo.get_memories_by_user_id(
        dev_user_id, 
        limit=limit,
        offset=offset,
        include_inactive=include_inactive
    )
    return memories


@router.put("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_data: MemoryUpdate,
    memory_id: str = Path(..., description="The ID of the memory to update"),
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user_dev if not settings.AUTH_REQUIRED else get_current_user_from_token_or_api_key)
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
    if memory.user_id != str(current_user.id):
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
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user_dev if not settings.AUTH_REQUIRED else get_current_user_from_token_or_api_key)
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
    if memory.user_id != str(current_user.id):
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
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user_dev if not settings.AUTH_REQUIRED else get_current_user_from_token_or_api_key)
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
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user_dev if not settings.AUTH_REQUIRED else get_current_user_from_token_or_api_key)
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
    try:
        # Ensure the user can only search their own memories
        if search_query.user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only search your own memories"
            )
        
        memory_repo = MemoryRepository(db)
        memories = await memory_repo.search_memories_by_text(
            str(current_user.id),
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
    except Exception as e:
        # Log the full exception details
        logger.error(f"Error in search_memories: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search memories: {str(e)}"
        )


# Memory Statistics endpoint

@router.get("/statistics", response_model=MemoryStatistics)
async def get_memory_statistics(
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user_dev if not settings.AUTH_REQUIRED else get_current_user_from_token_or_api_key)
) -> MemoryStatistics:
    """
    Get memory system statistics.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Memory system statistics
    """
    try:
        # Get memory statistics from database
        from app.services.memory.management import memory_management_service
        
        # Get raw statistics
        raw_stats = await memory_management_service._get_memory_statistics(db)
        
        # Extract user-specific stats
        user_stats = {}
        if "by_user" in raw_stats and str(current_user.id) in raw_stats["by_user"]:
            user_stats = raw_stats["by_user"][str(current_user.id)]
        
        # Extract total stats
        total_stats = raw_stats.get("total", {})
        
        # Build response
        return MemoryStatistics(
            total_memories=total_stats.get("memory_count", 0),
            total_chunks=0,  # This would need to be calculated
            active_memories=total_stats.get("memory_count", 0),  # Assuming all are active by default
            inactive_memories=0,  # This would need to be calculated
            avg_importance=0.5,  # Default value
            avg_chunks_per_memory=0.0,  # This would need to be calculated
            memories_by_source_type={},  # This would need to be calculated
            memories_by_tag={}  # This would need to be calculated
        )
    except Exception as e:
        # Log the error
        import logging
        logging.error(f"Error getting memory statistics: {str(e)}")
        
        # Return HTTP error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get memory statistics: {str(e)}"
        )


# Memory Chunk endpoints

@router.post("/chunks", response_model=MemoryChunkResponse, status_code=status.HTTP_201_CREATED)
async def create_memory_chunk(
    chunk_data: MemoryChunkCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user_dev if not settings.AUTH_REQUIRED else get_current_user_from_token_or_api_key)
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
    
    if memory.user_id != str(current_user.id):
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
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user_dev if not settings.AUTH_REQUIRED else get_current_user_from_token_or_api_key)
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
    
    if memory.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this memory chunk"
        )
    
    return chunk


@router.get("/memories/{memory_id}/chunks", response_model=List[MemoryChunkResponse])
async def get_memory_chunks(
    memory_id: str = Path(..., description="The ID of the memory to get chunks for"),
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user_dev if not settings.AUTH_REQUIRED else get_current_user_from_token_or_api_key)
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
    
    if memory.user_id != str(current_user.id):
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
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user_dev if not settings.AUTH_REQUIRED else get_current_user_from_token_or_api_key)
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
    
    if memory.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this memory chunk"
        )
    
    updated_chunk = await chunk_repo.update_chunk(chunk_id, chunk_data.dict(exclude_unset=True))
    return updated_chunk


@router.delete("/chunks/{chunk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory_chunk(
    chunk_id: str = Path(..., description="The ID of the memory chunk to delete"),
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user_dev if not settings.AUTH_REQUIRED else get_current_user_from_token_or_api_key)
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
    
    if memory.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this memory chunk"
        )
    
    await chunk_repo.delete_chunk(chunk_id)
