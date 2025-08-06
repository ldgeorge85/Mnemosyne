"""
Memory Extraction API Endpoints

This module provides endpoints for extracting memories from conversations.
"""

import logging
from typing import Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user_from_token_or_api_key
from app.api.dependencies.db import get_async_db
from app.services.memory.memory_service_enhanced import MemoryService
from app.core.exceptions import NotFoundError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/memories", tags=["memory-extraction"])


@router.post("/extract/{conversation_id}", response_model=Dict[str, Any])
async def extract_memories_from_conversation(
    conversation_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user_from_token_or_api_key)
) -> Dict[str, Any]:
    """
    Extract memories from a conversation.
    
    This endpoint processes a conversation to extract entities, facts, preferences,
    action items, and personal information, then stores them as searchable memories.
    
    Args:
        conversation_id: ID of the conversation to process
        background_tasks: FastAPI background tasks
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Summary of extracted memories
    """
    user_id = UUID(current_user["id"])
    
    try:
        memory_service = MemoryService(db)
        result = await memory_service.process_conversation(conversation_id, user_id)
        
        logger.info(
            f"Extracted memories from conversation {conversation_id}",
            extra={
                "user_id": str(user_id),
                "conversation_id": str(conversation_id),
                "memories_created": result["memories_created"]
            }
        )
        
        return result
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            f"Failed to extract memories from conversation {conversation_id}",
            extra={"user_id": str(user_id), "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to extract memories from conversation"
        )


@router.post("/search", response_model=Dict[str, Any])
async def search_memories(
    query: str,
    limit: int = 10,
    threshold: float = 0.7,
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user_from_token_or_api_key)
) -> Dict[str, Any]:
    """
    Search memories using vector similarity.
    
    This endpoint searches through the user's memories using semantic similarity
    based on vector embeddings.
    
    Args:
        query: Search query text
        limit: Maximum number of results (default: 10)
        threshold: Minimum similarity threshold 0-1 (default: 0.7)
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of matching memories with similarity scores
    """
    user_id = UUID(current_user["id"])
    
    try:
        memory_service = MemoryService(db)
        memories = await memory_service.search_memories(
            user_id=user_id,
            query=query,
            limit=limit,
            threshold=threshold
        )
        
        return {
            "query": query,
            "results": memories,
            "count": len(memories)
        }
        
    except Exception as e:
        logger.error(
            f"Failed to search memories",
            extra={"user_id": str(user_id), "query": query, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search memories"
        )


@router.get("/stats", response_model=Dict[str, Any])
async def get_memory_statistics(
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user_from_token_or_api_key)
) -> Dict[str, Any]:
    """
    Get statistics about the user's memories.
    
    Returns various statistics including total memories, memories by type,
    average importance, and top tags.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Memory statistics
    """
    user_id = UUID(current_user["id"])
    
    try:
        memory_service = MemoryService(db)
        stats = await memory_service.get_memory_statistics(user_id)
        
        return stats
        
    except Exception as e:
        logger.error(
            f"Failed to get memory statistics",
            extra={"user_id": str(user_id), "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get memory statistics"
        )