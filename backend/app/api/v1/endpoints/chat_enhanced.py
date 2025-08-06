"""
Enhanced Chat API Endpoints

This module provides chat endpoints with memory integration and
advanced features like streaming and conversation management.
"""

import logging
import json
from typing import Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.api.dependencies.auth import get_current_user_from_token_or_api_key
from app.api.dependencies.db import get_async_db
from app.db.models.conversation import Conversation, Message
from app.services.llm.llm_service_enhanced import EnhancedLLMService, EnhancedLLMConfig
from app.core.exceptions import NotFoundError, InternalServerError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["enhanced-chat"])


class ChatMessage(BaseModel):
    """Schema for a chat message."""
    role: str = Field(..., description="Role: user, assistant, or system")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Schema for chat completion request."""
    messages: list[ChatMessage] = Field(..., description="Conversation messages")
    conversation_id: Optional[UUID] = Field(None, description="Existing conversation ID")
    create_conversation: bool = Field(True, description="Create new conversation if ID not provided")
    extract_memories: bool = Field(True, description="Extract memories after response")
    extract_tasks: bool = Field(True, description="Extract tasks after response")
    stream: bool = Field(False, description="Stream the response")
    model: Optional[str] = Field(None, description="Model to use")
    temperature: Optional[float] = Field(None, description="Temperature (0-1)")
    max_tokens: Optional[int] = Field(None, description="Max tokens to generate")


class ChatResponse(BaseModel):
    """Schema for chat completion response."""
    conversation_id: UUID
    message_id: UUID
    content: str
    role: str = "assistant"
    created_at: datetime
    memories_extracted: bool = False
    tasks_extracted: bool = False


@router.post("/completions", response_model=ChatResponse)
async def create_chat_completion(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user_from_token_or_api_key)
) -> Any:
    """
    Create a chat completion with memory enhancement.
    
    This endpoint:
    1. Retrieves relevant memories for context
    2. Generates an AI response
    3. Stores the conversation
    4. Extracts new memories in the background
    
    Args:
        request: Chat request with messages and options
        background_tasks: FastAPI background tasks
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Chat response with generated content
    """
    user_id = UUID(current_user["id"])
    
    try:
        # Handle conversation creation/retrieval
        if request.conversation_id:
            # Verify conversation exists and belongs to user
            result = await db.execute(
                select(Conversation)
                .where(Conversation.id == request.conversation_id)
                .where(Conversation.user_id == user_id)
            )
            conversation = result.scalar_one_or_none()
            
            if not conversation:
                raise NotFoundError("Conversation", str(request.conversation_id))
        elif request.create_conversation:
            # Create new conversation
            conversation = Conversation(
                id=uuid4(),
                user_id=user_id,
                title=_generate_conversation_title(request.messages),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(conversation)
            await db.flush()  # Get the ID without committing
        else:
            conversation = None
        
        # Store user messages if we have a conversation
        if conversation:
            for msg in request.messages:
                if msg.role == "user":
                    user_message = Message(
                        id=uuid4(),
                        conversation_id=conversation.id,
                        role=msg.role,
                        content=msg.content,
                        created_at=datetime.utcnow()
                    )
                    db.add(user_message)
        
        # Initialize enhanced LLM service
        llm_config = EnhancedLLMConfig(
            model_name=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            streaming=request.stream,
            memory_enabled=True
        )
        
        llm_service = EnhancedLLMService(config=llm_config, db=db)
        
        # Convert messages to dict format
        messages_dict = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        # Generate response with memory context
        if request.stream:
            # Return streaming response
            return StreamingResponse(
                _stream_chat_response(
                    llm_service,
                    messages_dict,
                    user_id,
                    conversation.id if conversation else None,
                    db,
                    conversation
                ),
                media_type="text/event-stream"
            )
        else:
            # Generate non-streaming response
            response_content = await llm_service.chat_completion(
                messages=messages_dict,
                user_id=user_id,
                conversation_id=conversation.id if conversation else None,
                stream=False
            )
            
            # Store assistant response
            assistant_message = None
            if conversation:
                assistant_message = Message(
                    id=uuid4(),
                    conversation_id=conversation.id,
                    role="assistant",
                    content=response_content,
                    created_at=datetime.utcnow()
                )
                db.add(assistant_message)
                
                # Update conversation timestamp
                conversation.updated_at = datetime.utcnow()
            
            # Commit the conversation and messages
            await db.commit()
            
            # Schedule memory extraction in background
            if request.extract_memories and conversation:
                background_tasks.add_task(
                    extract_memories_task,
                    str(conversation.id),
                    str(user_id)
                )
            
            # Schedule task extraction in background
            if request.extract_tasks and conversation:
                background_tasks.add_task(
                    extract_tasks_task,
                    str(conversation.id),
                    str(user_id)
                )
            
            return ChatResponse(
                conversation_id=conversation.id if conversation else uuid4(),
                message_id=assistant_message.id if assistant_message else uuid4(),
                content=response_content,
                role="assistant",
                created_at=datetime.utcnow(),
                memories_extracted=request.extract_memories,
                tasks_extracted=request.extract_tasks
            )
            
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(
            f"Chat completion failed",
            extra={"user_id": str(user_id), "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate chat completion"
        )


async def _stream_chat_response(
    llm_service: EnhancedLLMService,
    messages: list[Dict[str, str]],
    user_id: UUID,
    conversation_id: Optional[UUID],
    db: AsyncSession,
    conversation: Optional[Conversation]
):
    """
    Stream chat response with Server-Sent Events format.
    
    Yields:
        SSE-formatted chunks of the response
    """
    try:
        # Generate streaming response
        response_chunks = []
        async for chunk in llm_service.chat_completion(
            messages=messages,
            user_id=user_id,
            conversation_id=conversation_id,
            stream=True
        ):
            response_chunks.append(chunk)
            # Send chunk as SSE
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        
        # Store complete response
        if conversation:
            complete_response = "".join(response_chunks)
            assistant_message = Message(
                id=uuid4(),
                conversation_id=conversation.id,
                role="assistant",
                content=complete_response,
                created_at=datetime.utcnow()
            )
            db.add(assistant_message)
            conversation.updated_at = datetime.utcnow()
            await db.commit()
            
            # Send completion event
            yield f"data: {json.dumps({'event': 'complete', 'conversation_id': str(conversation.id)})}\n\n"
        
    except Exception as e:
        logger.error(f"Streaming failed: {e}", exc_info=True)
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
    finally:
        yield "data: [DONE]\n\n"


def _generate_conversation_title(messages: list[ChatMessage]) -> str:
    """
    Generate a title for the conversation based on first user message.
    
    Args:
        messages: List of chat messages
        
    Returns:
        Generated title
    """
    # Find first user message
    for msg in messages:
        if msg.role == "user":
            # Take first 50 characters
            content = msg.content.strip()
            if len(content) > 50:
                return content[:47] + "..."
            return content
    
    return "New Conversation"


async def extract_memories_task(conversation_id: str, user_id: str):
    """
    Background task to extract memories from a conversation.
    
    Args:
        conversation_id: ID of the conversation
        user_id: ID of the user
    """
    try:
        from app.db.session import async_session_maker
        from app.services.memory.memory_service_enhanced import MemoryService
        
        async with async_session_maker() as db:
            memory_service = MemoryService(db)
            result = await memory_service.process_conversation(
                UUID(conversation_id),
                UUID(user_id)
            )
            
            logger.info(
                f"Background memory extraction completed",
                extra={
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "memories_created": result["memories_created"]
                }
            )
            
    except Exception as e:
        logger.error(
            f"Background memory extraction failed",
            extra={
                "conversation_id": conversation_id,
                "user_id": user_id,
                "error": str(e)
            },
            exc_info=True
        )


async def extract_tasks_task(conversation_id: str, user_id: str):
    """
    Background task to extract tasks from a conversation.
    
    Args:
        conversation_id: ID of the conversation
        user_id: ID of the user
    """
    try:
        from app.db.session import async_session_maker
        from app.services.task.task_intelligence import TaskIntelligenceService
        
        async with async_session_maker() as db:
            task_intelligence = TaskIntelligenceService(db)
            result = await task_intelligence.process_conversation_for_tasks(
                UUID(conversation_id),
                UUID(user_id),
                auto_create=True
            )
            
            logger.info(
                f"Background task extraction completed",
                extra={
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "tasks_extracted": result["extracted_count"],
                    "tasks_created": result["created_count"]
                }
            )
            
    except Exception as e:
        logger.error(
            f"Background task extraction failed",
            extra={
                "conversation_id": conversation_id,
                "user_id": user_id,
                "error": str(e)
            },
            exc_info=True
        )


@router.get("/conversations", response_model=list[Dict[str, Any]])
async def list_conversations(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user_from_token_or_api_key)
) -> Any:
    """
    List user's conversations with memory context.
    
    Args:
        skip: Number of conversations to skip
        limit: Maximum number of conversations to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of conversations with metadata
    """
    user_id = UUID(current_user["id"])
    
    try:
        from sqlalchemy import select, func
        
        # Get conversations with message count
        result = await db.execute(
            select(
                Conversation,
                func.count(Message.id).label("message_count")
            )
            .outerjoin(Message)
            .where(Conversation.user_id == user_id)
            .group_by(Conversation.id)
            .order_by(Conversation.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        conversations = []
        for row in result:
            conv = row[0]
            msg_count = row[1]
            
            conversations.append({
                "id": str(conv.id),
                "title": conv.title,
                "message_count": msg_count,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat()
            })
        
        return conversations
        
    except Exception as e:
        logger.error(f"Failed to list conversations", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations"
        )