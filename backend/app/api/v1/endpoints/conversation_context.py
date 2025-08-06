"""
Conversation Context API Endpoints

This module defines API endpoints for managing conversation contexts,
including retrieving context, managing context windows, and tracking conversation state.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.db import get_db
from app.api.dependencies.auth import get_current_user
from app.services.conversation import (
    ConversationContextManager, 
    ConversationSessionManager,
    ConversationWindowManager,
    WindowType
)

# Pydantic models for request and response
from pydantic import BaseModel, Field


class ContextMetadata(BaseModel):
    """Schema for context metadata"""
    key: str
    value: Any


class UpdateContextMetadataRequest(BaseModel):
    """Schema for updating context metadata"""
    metadata: List[ContextMetadata]


class ContextStatsResponse(BaseModel):
    """Schema for context window statistics"""
    message_count: int
    token_count: int
    user_messages: int
    assistant_messages: int
    system_messages: int
    oldest_message: Optional[str] = None
    newest_message: Optional[str] = None
    time_span_seconds: float


class ContextWindowResponse(BaseModel):
    """Schema for conversation context window response"""
    conversation_id: str
    title: str
    messages: List[Dict[str, Any]]
    window_type: str
    stats: ContextStatsResponse


class SessionStateResponse(BaseModel):
    """Schema for session state response"""
    conversation_id: str
    user_id: str
    last_active_time: str
    current_topic: Optional[str] = None
    metadata: Dict[str, Any] = {}
    is_active: bool


# Create router
router = APIRouter()


@router.get("/{conversation_id}/context", response_model=ContextWindowResponse)
async def get_conversation_context(
    conversation_id: str,
    max_messages: int = Query(20, ge=1, le=100),
    max_tokens: int = Query(4000, ge=100, le=8000),
    window_type: str = Query(WindowType.HYBRID, description="Window selection strategy: recent, relevant, or hybrid"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get the current context window for a conversation.
    """
    try:
        # Initialize services
        context_manager = ConversationContextManager(db)
        window_manager = ConversationWindowManager()
        
        # Get context
        context = await context_manager.get_conversation_context(
            conversation_id=conversation_id,
            user_id=current_user["id"],
            max_messages=max_messages,
            max_tokens=max_tokens
        )
        
        # Calculate window stats
        stats = window_manager.calculate_window_stats(context["messages"])
        
        return {
            "conversation_id": context["conversation_id"],
            "title": context["title"],
            "messages": context["messages"],
            "window_type": window_type,
            "stats": stats
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting context: {str(e)}"
        )


@router.post("/{conversation_id}/context/metadata", response_model=Dict[str, Any])
async def update_context_metadata(
    conversation_id: str,
    metadata_request: UpdateContextMetadataRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Update metadata for a conversation context.
    """
    try:
        # Convert metadata list to dictionary
        metadata = {item.key: item.value for item in metadata_request.metadata}
        
        # Initialize services
        context_manager = ConversationContextManager(db)
        
        # Save metadata
        success = await context_manager.save_context_metadata(
            conversation_id=conversation_id,
            user_id=current_user["id"],
            metadata=metadata
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        return {"success": True, "metadata": metadata}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating context metadata: {str(e)}"
        )


@router.get("/{conversation_id}/session", response_model=SessionStateResponse)
async def get_session_state(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get the current session state for a conversation.
    """
    try:
        # Initialize service
        session_manager = ConversationSessionManager(db)
        
        # Get or create session state
        state = await session_manager.get_active_conversation(
            conversation_id=conversation_id,
            user_id=current_user["id"]
        )
        
        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        return state.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting session state: {str(e)}"
        )


@router.post("/{conversation_id}/session/active", response_model=SessionStateResponse)
async def mark_session_active(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Mark a conversation session as active.
    """
    try:
        # Initialize service
        session_manager = ConversationSessionManager(db)
        
        # Mark as active
        state = await session_manager.mark_conversation_active(
            conversation_id=conversation_id,
            user_id=current_user["id"]
        )
        
        return state.to_dict()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marking session active: {str(e)}"
        )


@router.post("/{conversation_id}/session/inactive", response_model=Dict[str, bool])
async def mark_session_inactive(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Mark a conversation session as inactive.
    """
    try:
        # Initialize service
        session_manager = ConversationSessionManager(db)
        
        # Mark as inactive
        success = await session_manager.mark_conversation_inactive(
            conversation_id=conversation_id,
            user_id=current_user["id"]
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or already inactive"
            )
        
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marking session inactive: {str(e)}"
        )


@router.get("/active", response_model=List[SessionStateResponse])
async def get_active_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get all active conversation sessions for the current user.
    """
    try:
        # Initialize service
        session_manager = ConversationSessionManager(db)
        
        # Get active sessions
        active_sessions = await session_manager.get_active_conversations_for_user(
            user_id=current_user["id"]
        )
        
        return active_sessions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting active sessions: {str(e)}"
        )
