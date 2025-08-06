"""
LLM API endpoints.

This module provides API endpoints for interacting with language models,
including chat completions, embeddings, and other LLM-based operations.
"""
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.core.config import settings
from app.api.dependencies.db import get_db
from app.api.dependencies.auth import get_current_user
from app.services.llm import LangChainService, LLMConfig

logger = logging.getLogger(__name__)


router = APIRouter()


class ChatMessage(BaseModel):
    """Schema for a chat message."""
    role: str = Field(..., description="Role of the message sender (user, assistant, system)")
    content: str = Field(..., description="Content of the message")


class ChatCompletionRequest(BaseModel):
    """Schema for a chat completion request."""
    messages: List[ChatMessage] = Field(..., description="List of messages in the conversation")
    stream: bool = Field(True, description="Whether to stream the response")
    model: Optional[str] = Field(None, description="Model to use for completion")
    temperature: Optional[float] = Field(None, description="Temperature for sampling")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    conversation_id: Optional[str] = Field(None, description="ID of the conversation")


class ChatCompletionResponse(BaseModel):
    """Schema for a chat completion response."""
    role: str = Field("assistant", description="Role of the response (always assistant)")
    content: str = Field(..., description="Generated content")
    model: str = Field(..., description="Model used for generation")
    usage: Dict[str, int] = Field(default_factory=dict, description="Token usage information")


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
    request: ChatCompletionRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Any:
    """
    Generate a chat completion from the LLM.
    
    Args:
        request: Chat completion request
        background_tasks: FastAPI background tasks
        db: Database session
        current_user_id: ID of the authenticated user
        
    Returns:
        Generated completion response or streaming response
    """
    # Validate OpenAI API key
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service is not properly configured"
        )
    
    # Create service configuration
    config = LLMConfig(
        model_name=request.model or settings.OPENAI_MODEL,
        temperature=request.temperature or 0.7,
        max_tokens=request.max_tokens,
        streaming=request.stream
    )
    
    # Create LangChain service
    service = LangChainService(config=config)
    
    # Format messages
    messages = [msg.dict() for msg in request.messages]
    
    # Background task to log the completion
    def log_completion(completion: str, conversation_id: Optional[str] = None):
        # This would log the completion to the database or other monitoring system
        # For now, we'll just print it (this runs in the background)
        logger.info(f"Logged completion for conversation {conversation_id}: {completion[:50]}...")
    
    try:
        # Handle streaming response
        if request.stream:
            async def stream_response():
                async for chunk in service.chat_completion(
                    messages=messages,
                    stream=True,
                    conversation_id=request.conversation_id
                ):
                    yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"
            
            return StreamingResponse(
                stream_response(),
                media_type="text/event-stream"
            )
        
        # Handle regular response
        else:
            completion = await service.chat_completion(
                messages=messages,
                stream=False,
                conversation_id=request.conversation_id
            )
            
            # Log completion in the background
            background_tasks.add_task(
                log_completion,
                completion=completion,
                conversation_id=request.conversation_id
            )
            
            return ChatCompletionResponse(
                content=completion,
                model=config.model_name,
                usage={"total_tokens": 0}  # We would need to get actual usage from the callback handler
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating completion: {str(e)}"
        )
