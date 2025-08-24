"""
API endpoints for memory reflection and importance scoring (Phase 3, Cognee integration).
"""
import logging
from fastapi import APIRouter, status, Path, Query
from typing import List, Dict, Any, Optional

# Import memory schemas for request/response validation
from app.schemas.memory import MemoryResponse, MemoryCreate, MemoryUpdate, MemoryWithChunksResponse, MemorySearchResponse, MemorySearchQuery, MemoryStatistics, MemoryChunkResponse, MemoryChunkCreate, MemoryChunkUpdate

from app.services.memory.reflection import MemoryReflectionService
from app.services.memory.embeddings import EmbeddingGenerator
from app.services.vector_store.qdrant_store import get_qdrant_store
from fastapi import Depends, HTTPException, APIRouter, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db
from app.core.auth.manager import get_current_user
from app.core.auth.base import AuthUser
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
    current_user: AuthUser = Depends(get_current_user)
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
    current_user: AuthUser = Depends(get_current_user)
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
    current_user: AuthUser = Depends(get_current_user)
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
    current_user: AuthUser = Depends(get_current_user)
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
    if memory_data.user_id != str(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create memories for yourself"
        )
    
    # Generate embedding for the memory content
    async with EmbeddingGenerator() as embedding_generator:
        embedding_result = await embedding_generator.generate_embedding(memory_data.content)
    
    # Add embedding data to memory
    memory_dict = memory_data.dict()
    memory_dict["embedding"] = embedding_result["embedding"]
    memory_dict["embedding_model"] = embedding_result["model"]
    memory_dict["embedding_dimension"] = embedding_result["dimension"]
    
    # Create memory in database
    memory_repo = MemoryRepository(db)
    memory = await memory_repo.create_memory(memory_dict)
    
    # Store embedding in Qdrant
    qdrant_store = get_qdrant_store()
    await qdrant_store.add_memory(
        memory_id=str(memory.id),
        embedding=embedding_result["embedding"],
        metadata={
            "user_id": str(memory.user_id),
            "title": memory.title,
            "tags": memory.tags,
            "importance": memory.importance,
            "source_type": memory.source_type,
            "embedding_model": embedding_result["model"],
        }
    )
    
    return memory


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: str = Path(..., description="The ID of the memory to retrieve"),
    include_chunks: bool = Query(False, description="Whether to include memory chunks"),
    db: AsyncSession = Depends(get_async_db),
    current_user: AuthUser = Depends(get_current_user)
) -> MemoryResponse:
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
    
    # Check user permission (compare as strings)
    if str(memory.user_id) != str(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this memory"
        )
    
    # Update access stats
    await memory_repo.update_access_stats(memory_id)
    
    # Convert SQLAlchemy model to Pydantic model
    # We need to handle the metadata field specially
    memory_dict = {
        "id": str(memory.id),
        "user_id": str(memory.user_id),
        "title": memory.title,
        "content": memory.content,
        "source": memory.source,
        "source_type": memory.source_type,
        "source_id": str(memory.source_id) if memory.source_id else None,
        "tags": memory.tags,
        "metadata": memory.memory_metadata,  # Map memory_metadata to metadata
        "importance": memory.importance,
        "created_at": memory.created_at,
        "updated_at": memory.updated_at,
        "last_accessed_at": memory.last_accessed_at,
        "access_count": memory.access_count,
        "is_active": memory.is_active,
        "embedding_model": memory.embedding_model,
        "has_embedding": memory.embedding is not None
    }
    
    return MemoryResponse(**memory_dict)


@router.get("/", response_model=List[MemoryResponse])
async def list_memories(
    limit: int = Query(50, description="Maximum number of memories to return"),
    offset: int = Query(0, description="Number of memories to skip for pagination"),
    include_inactive: bool = Query(False, description="Whether to include inactive memories"),
    db: AsyncSession = Depends(get_async_db),
    current_user: AuthUser = Depends(get_current_user)
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
    # Use the actual authenticated user's ID
    memory_repo = MemoryRepository(db)
    memories, _ = await memory_repo.get_memories_by_user_id(
        str(current_user.user_id), 
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
    current_user: AuthUser = Depends(get_current_user)
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
    if str(memory.user_id) != str(current_user.user_id):
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
    current_user: AuthUser = Depends(get_current_user)
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
    if str(memory.user_id) != str(current_user.user_id):
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
    current_user: AuthUser = Depends(get_current_user)
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
        str(current_user.user_id),
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
    current_user: AuthUser = Depends(get_current_user)
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
        if search_query.user_id != str(current_user.user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only search your own memories"
            )
        
        memory_repo = MemoryRepository(db)
        memories = await memory_repo.search_memories_by_text(
            str(current_user.user_id),
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
                memory_with_chunks = MemoryWithChunksResponse.model_validate(memory)
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


@router.post("/search/similar", response_model=MemorySearchResponse)
async def search_similar_memories(
    query: str = Body(..., description="Query text to find similar memories"),
    limit: int = Query(10, description="Maximum number of results to return"),
    score_threshold: Optional[float] = Query(None, description="Minimum similarity score threshold"),
    db: AsyncSession = Depends(get_async_db),
    current_user: AuthUser = Depends(get_current_user)
) -> MemorySearchResponse:
    """
    Search for similar memories using vector similarity search.
    
    This endpoint generates an embedding for the query text and searches
    for memories with similar embeddings using Qdrant vector database.
    
    Args:
        query: Query text to find similar memories
        limit: Maximum number of results to return
        score_threshold: Minimum similarity score threshold
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Search results with similarity scores
        
    Raises:
        HTTPException: If search fails
    """
    try:
        # Generate embedding for the query
        async with EmbeddingGenerator() as embedding_generator:
            query_embedding_result = await embedding_generator.generate_embedding(query)
        
        # Search in Qdrant
        qdrant_store = get_qdrant_store()
        similar_memories = await qdrant_store.search_similar(
            query_embedding=query_embedding_result["embedding"],
            limit=limit,
            score_threshold=score_threshold,
            filter_conditions={"user_id": str(current_user.user_id)}
        )
        
        # Fetch full memory data from database
        memory_repo = MemoryRepository(db)
        results = []
        
        for result in similar_memories:
            memory = await memory_repo.get_memory_by_id(result["memory_id"])
            if memory:
                # Add similarity score to metadata
                memory_response = MemoryResponse.model_validate(memory)
                results.append(memory_response)
        
        return MemorySearchResponse(
            query=query,
            results=results,
            total=len(results)
        )
        
    except Exception as e:
        logger.error(f"Error in search_similar_memories: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search similar memories: {str(e)}"
        )


# Memory Statistics endpoint

@router.get("/statistics", response_model=MemoryStatistics)
async def get_memory_statistics(
    db: AsyncSession = Depends(get_async_db),
    current_user: AuthUser = Depends(get_current_user)
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
        if "by_user" in raw_stats and str(current_user.user_id) in raw_stats["by_user"]:
            user_stats = raw_stats["by_user"][str(current_user.user_id)]
        
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
    current_user: AuthUser = Depends(get_current_user)
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
    
    if str(memory.user_id) != str(current_user.user_id):
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
    current_user: AuthUser = Depends(get_current_user)
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
    
    if str(memory.user_id) != str(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this memory chunk"
        )
    
    return chunk


@router.get("/memories/{memory_id}/chunks", response_model=List[MemoryChunkResponse])
async def get_memory_chunks(
    memory_id: str = Path(..., description="The ID of the memory to get chunks for"),
    db: AsyncSession = Depends(get_async_db),
    current_user: AuthUser = Depends(get_current_user)
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
    
    if str(memory.user_id) != str(current_user.user_id):
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
    current_user: AuthUser = Depends(get_current_user)
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
    
    if str(memory.user_id) != str(current_user.user_id):
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
    current_user: AuthUser = Depends(get_current_user)
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
    
    if str(memory.user_id) != str(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this memory chunk"
        )
    
    await chunk_repo.delete_chunk(chunk_id)
