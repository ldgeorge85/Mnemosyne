"""
Streaming API Endpoints

This module defines API endpoints for response streaming,
including SSE endpoints, WebSocket endpoints, and streaming message responses.
"""

import asyncio
import uuid
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, Request
from starlette.responses import StreamingResponse

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.db import get_db
from app.api.dependencies.auth import get_current_user
from app.db.repositories.conversation import ConversationRepository
from app.services.conversation import (
    ResponseStreamer, 
    LLMResponseStreamer
)

# Import the streamer services
from app.services.conversation.response_streamer import ResponseStreamer
from app.services.conversation.llm_streamer import LLMResponseStreamer

# Pydantic models for request and response
from pydantic import BaseModel, Field


class StreamingRequest(BaseModel):
    """Schema for streaming request"""
    conversation_id: str
    message_content: str = Field(..., min_length=1, max_length=10000)
    streaming_type: str = Field("sse", pattern="^(sse|chunked)$")
    chunk_size: int = Field(100, gt=0, lt=1000)
    chunk_delay: float = Field(0.05, ge=0, le=1.0)


class StreamingStatusRequest(BaseModel):
    """Schema for streaming status request"""
    session_id: str


class StreamingStatusResponse(BaseModel):
    """Schema for streaming status response"""
    session_id: str
    is_active: bool
    progress: float = 0.0
    tokens_streamed: int = 0
    total_tokens: int = 0
    is_complete: bool = False
    error: Optional[str] = None


# Create router
router = APIRouter()


@router.post("/text")
async def stream_text_response(
    request: StreamingRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Stream a text response to the client using either SSE or chunked transfer.
    """
    try:
        # Verify the conversation exists and belongs to the user
        conversation_repo = ConversationRepository(db)
        conversation = await conversation_repo.get_conversation(
            request.conversation_id,
            current_user["id"]
        )
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Initialize the response streamer
        response_streamer = ResponseStreamer()
        
        # Create streaming response
        return await response_streamer.stream_message_creation(
            message_text=request.message_content,
            request=http_request,
            use_sse=(request.streaming_type == "sse"),
            chunk_size=request.chunk_size,
            chunk_delay=request.chunk_delay
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error streaming response: {str(e)}"
        )


@router.post("/llm")
async def stream_llm_response(
    request: StreamingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Stream an LLM-generated response to the client using SSE.
    This simulates an LLM generating a response token by token.
    """
    try:
        # Verify the conversation exists and belongs to the user
        conversation_repo = ConversationRepository(db)
        conversation = await conversation_repo.get_conversation(
            request.conversation_id,
            current_user["id"]
        )
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Initialize the LLM response streamer
        llm_streamer = LLMResponseStreamer()
        
        # Generate a session ID for this streaming session
        session_id = f"llm-{uuid.uuid4()}"
        
        # Create streaming response
        return llm_streamer.create_llm_sse_response(
            response_text=request.message_content,
            session_id=session_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error streaming LLM response: {str(e)}"
        )


@router.post("/status", response_model=StreamingStatusResponse)
async def get_streaming_status(
    request: StreamingStatusRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get the status of an ongoing streaming session.
    """
    try:
        # Initialize the LLM response streamer
        llm_streamer = LLMResponseStreamer()
        
        # Get session status
        status = llm_streamer.get_session_status(request.session_id)
        
        if not status:
            return {
                "session_id": request.session_id,
                "is_active": False,
                "progress": 0.0,
                "tokens_streamed": 0,
                "total_tokens": 0,
                "is_complete": False,
                "error": "Session not found"
            }
        
        # Calculate progress
        progress = status["streamed_tokens"] / status["total_tokens"] if status["total_tokens"] > 0 else 0
        
        return {
            "session_id": request.session_id,
            "is_active": True,
            "progress": progress,
            "tokens_streamed": status["streamed_tokens"],
            "total_tokens": status["total_tokens"],
            "is_complete": status["is_complete"],
            "error": status.get("error")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting streaming status: {str(e)}"
        )


@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for bi-directional streaming communication.
    This allows for more interactive streaming with client feedback.
    """
    await websocket.accept()
    
    try:
        # Create session ID
        session_id = f"ws-{uuid.uuid4()}"
        
        # Initialize the LLM response streamer
        llm_streamer = LLMResponseStreamer()
        
        # Get initial message from client
        data = await websocket.receive_json()
        message = data.get("message", "")
        
        if not message:
            await websocket.send_json({
                "error": "No message provided",
                "success": False
            })
            await websocket.close()
            return
        
        # Send acknowledgement
        await websocket.send_json({
            "message": "Streaming response...",
            "session_id": session_id,
            "success": True
        })
        
        # Stream response
        await llm_streamer.stream_llm_to_websocket(
            websocket=websocket,
            response_text=f"This is a simulated response to your message: '{message}'. In a real implementation, this would be generated by an LLM based on the conversation context.",
            session_id=session_id
        )
    except Exception as e:
        # Try to send error message
        try:
            await websocket.send_json({
                "error": f"Error during streaming: {str(e)}",
                "success": False
            })
        except:
            pass
        
        # Close the connection
        await websocket.close()
