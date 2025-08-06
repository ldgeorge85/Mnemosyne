"""
Session management API endpoints for the Shadow AI system.

This module provides FastAPI endpoints for managing chat sessions,
including creating, retrieving, updating, and deleting sessions.
"""

import logging
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from models.session import ChatSession, ChatMessage
from managers.session_manager import SessionManager, default_session_manager

# Configure logging
logger = logging.getLogger("shadow.api.sessions")

# Create router
router = APIRouter()

# Global reference to session manager
session_manager = None


def get_session_manager() -> SessionManager:
    """
    Get the global session manager instance.
    
    Returns:
        The global session manager
    """
    if session_manager is None:
        raise HTTPException(
            status_code=503,
            detail="Session manager not initialized"
        )
    return session_manager


def set_session_manager(manager: SessionManager):
    """
    Set the global session manager instance.
    
    Args:
        manager: The session manager to use
    """
    global session_manager
    session_manager = manager
    logger.info("Session manager set")


# Request and response models
class CreateSessionRequest(BaseModel):
    """Request model for creating a session."""
    user_id: str
    title: Optional[str] = None


class SessionResponse(BaseModel):
    """Response model for session operations."""
    id: str
    user_id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int
    is_active: bool


class SessionListResponse(BaseModel):
    """Response model for listing sessions."""
    sessions: List[SessionResponse]


class MessageRequest(BaseModel):
    """Request model for adding a message."""
    role: str
    content: str
    agent: Optional[str] = None
    metadata: Optional[Dict] = None


class MessageResponse(BaseModel):
    """Response model for message operations."""
    role: str
    content: str
    agent: Optional[str] = None
    timestamp: str
    metadata: Optional[Dict] = None


class MessageListResponse(BaseModel):
    """Response model for listing messages."""
    messages: List[MessageResponse]
    session_id: str


class UpdateSessionRequest(BaseModel):
    """Request model for updating a session."""
    title: Optional[str] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict] = None


# Session endpoints
@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    request: CreateSessionRequest,
    sm: SessionManager = Depends(get_session_manager)
):
    """
    Create a new chat session.
    
    Args:
        request: The create session request
        sm: The session manager
        
    Returns:
        The created session
    """
    try:
        session = await sm.create_session(request.user_id, request.title)
        return SessionResponse(
            id=session.id,
            user_id=session.user_id,
            title=session.title,
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat(),
            message_count=len(session.messages),
            is_active=session.is_active
        )
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create session: {str(e)}"
        )


@router.get("/sessions/{user_id}", response_model=SessionListResponse)
async def list_sessions(
    user_id: str,
    sm: SessionManager = Depends(get_session_manager)
):
    """
    List all sessions for a user.
    
    Args:
        user_id: The ID of the user
        sm: The session manager
        
    Returns:
        List of sessions belonging to the user
    """
    try:
        sessions = await sm.list_user_sessions(user_id)
        return SessionListResponse(
            sessions=[
                SessionResponse(
                    id=session.id,
                    user_id=session.user_id,
                    title=session.title,
                    created_at=session.created_at.isoformat(),
                    updated_at=session.updated_at.isoformat(),
                    message_count=len(session.messages),
                    is_active=session.is_active
                )
                for session in sessions
            ]
        )
    except Exception as e:
        logger.error(f"Error listing sessions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list sessions: {str(e)}"
        )


@router.get("/sessions/detail/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    sm: SessionManager = Depends(get_session_manager)
):
    """
    Get details of a session.
    
    Args:
        session_id: The ID of the session
        sm: The session manager
        
    Returns:
        The session details
    """
    try:
        session = await sm.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        return SessionResponse(
            id=session.id,
            user_id=session.user_id,
            title=session.title,
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat(),
            message_count=len(session.messages),
            is_active=session.is_active
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session: {str(e)}"
        )


@router.put("/sessions/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    request: UpdateSessionRequest,
    sm: SessionManager = Depends(get_session_manager)
):
    """
    Update a session.
    
    Args:
        session_id: The ID of the session
        request: The update session request
        sm: The session manager
        
    Returns:
        The updated session
    """
    try:
        # Get the existing session
        session = await sm.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        # Update the fields
        if request.title is not None:
            session.title = request.title
        
        if request.is_active is not None:
            session.is_active = request.is_active
        
        if request.metadata is not None:
            session.metadata.update(request.metadata)
        
        # Save the changes
        success = await sm.update_session(session)
        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update session {session_id}"
            )
        
        return SessionResponse(
            id=session.id,
            user_id=session.user_id,
            title=session.title,
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat(),
            message_count=len(session.messages),
            is_active=session.is_active
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update session: {str(e)}"
        )


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    sm: SessionManager = Depends(get_session_manager)
):
    """
    Delete a session.
    
    Args:
        session_id: The ID of the session
        sm: The session manager
        
    Returns:
        Success message
    """
    try:
        success = await sm.delete_session(session_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        return {"status": "success", "message": f"Session {session_id} deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete session: {str(e)}"
        )


# Message endpoints
@router.post("/sessions/{session_id}/messages")
async def add_message(
    session_id: str,
    message: MessageRequest,
    sm: SessionManager = Depends(get_session_manager)
):
    """
    Add a message to a session.
    
    Args:
        session_id: The ID of the session
        message: The message to add
        sm: The session manager
        
    Returns:
        Success message
    """
    try:
        success = await sm.add_message(
            session_id,
            message.role,
            message.content,
            message.agent,
            message.metadata
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        return {"status": "success", "message": "Message added to session"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add message: {str(e)}"
        )


@router.get("/sessions/{session_id}/messages", response_model=MessageListResponse)
async def get_messages(
    session_id: str,
    limit: int = 100,
    sm: SessionManager = Depends(get_session_manager)
):
    """
    Get messages from a session.
    
    Args:
        session_id: The ID of the session
        limit: Maximum number of messages to retrieve
        sm: The session manager
        
    Returns:
        List of messages in the session
    """
    try:
        messages = await sm.get_messages(session_id, limit)
        
        return MessageListResponse(
            messages=[
                MessageResponse(
                    role=message.role,
                    content=message.content,
                    agent=message.agent,
                    timestamp=message.timestamp.isoformat(),
                    metadata=message.metadata
                )
                for message in messages
            ],
            session_id=session_id
        )
    except Exception as e:
        logger.error(f"Error getting messages: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get messages: {str(e)}"
        )
