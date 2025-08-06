"""
Conversation API Endpoints

This module defines the API endpoints for managing conversations and messages, including:
- Listing, creating, updating, and deleting conversations
- Adding and deleting messages
- Fetching a specific conversation with its messages
- Fetching paginated messages for a conversation (GET /conversations/{conversation_id}/messages)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List, Optional
from uuid import UUID
import json
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.db import get_async_db
from app.api.dependencies.auth import get_current_user
from app.db.repositories.conversation import ConversationRepository, MessageRepository
from app.services.agent.agent_manager import AgentManager

# Pydantic models for request and response
from pydantic import BaseModel, Field
from datetime import datetime


# Request and response models
class MessageBase(BaseModel):
    """Base schema for message data"""
    content: str
    role: str = Field(..., pattern="^(user|assistant|system)$")


class MessageCreate(MessageBase):
    """Schema for creating a new message"""
    pass


class MessageResponse(MessageBase):
    """Schema for message response"""
    id: UUID
    conversation_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


class ConversationBase(BaseModel):
    """Base schema for conversation data"""
    title: str


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation"""
    pass


class ConversationUpdate(ConversationBase):
    """Schema for updating a conversation"""
    pass


class ConversationResponse(ConversationBase):
    """Schema for conversation response"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ConversationDetailResponse(ConversationResponse):
    """Schema for detailed conversation response with messages"""
    messages: List[MessageResponse] = []

    class Config:
        orm_mode = True


class PaginatedConversationResponse(BaseModel):
    """Schema for paginated conversation list response"""
    total: int
    offset: int
    limit: int
    items: List[ConversationResponse]


class PaginatedMessageResponse(BaseModel):
    """Schema for paginated message list response"""
    total: int
    offset: int
    limit: int
    items: List[MessageResponse]


class ConversationWithMessagesResponse(ConversationResponse):
    """Schema for conversation with paginated messages"""
    messages: PaginatedMessageResponse


class MessageWithAssistantResponse(MessageResponse):
    """Schema for message response with assistant's response"""
    assistant_response: Optional[MessageResponse] = None


class SuccessResponse(BaseModel):
    """Simple success response"""
    success: bool = True


# Create router
router = APIRouter()


@router.get("/{conversation_id}/messages/", response_model=PaginatedMessageResponse)
async def get_conversation_messages(
    conversation_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get paginated messages for a specific conversation.

    Args:
        conversation_id: ID of the conversation
        limit: Maximum number of messages to return (default: 50)
        offset: Offset for pagination (default: 0)
        db: Async database session (injected)
        current_user: Authenticated user (injected)

    Returns:
        PaginatedMessageResponse: List of messages and pagination info
    """
    # Ensure the conversation exists and belongs to the user
    repo = ConversationRepository(db)
    conversation = await repo.get_conversation(conversation_id=conversation_id, user_id=current_user.id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    # Fetch messages
    message_repo = MessageRepository(db)
    messages, total = await message_repo.get_messages(conversation_id=conversation_id, limit=limit, offset=offset)
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "items": messages
    }



@router.get("/", response_model=PaginatedConversationResponse)
async def get_conversations(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get a list of the user's conversations.
    """
    repo = ConversationRepository(db)
    conversations, total = await repo.get_conversations(
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "items": conversations
    }


@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Create a new conversation.
    """
    repo = ConversationRepository(db)
    conversation = await repo.create_conversation({
        "title": conversation_data.title,
        "user_id": current_user.id
    })
    
    return conversation


@router.get("/{conversation_id}", response_model=ConversationWithMessagesResponse)
async def get_conversation(
    conversation_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get a specific conversation with its messages.
    """
    repo = ConversationRepository(db)
    conversation = await repo.get_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    message_repo = MessageRepository(db)
    messages, total = await message_repo.get_messages(
        conversation_id=conversation_id,
        limit=limit,
        offset=offset
    )
    
    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "messages": {
            "total": total,
            "offset": offset,
            "limit": limit,
            "items": messages
        }
    }


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: UUID,
    conversation_data: ConversationUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Update a conversation.
    """
    repo = ConversationRepository(db)
    conversation = await repo.update_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id,
        data={"title": conversation_data.title}
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return conversation


@router.delete("/{conversation_id}", response_model=SuccessResponse)
async def delete_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Delete a conversation.
    """
    repo = ConversationRepository(db)
    success = await repo.delete_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return {"success": True}


@router.post("/{conversation_id}/messages/", response_model=MessageWithAssistantResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    conversation_id: UUID,
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Add a new message to a conversation and get an assistant response.
    """
    # Verify conversation exists and belongs to user
    conv_repo = ConversationRepository(db)
    conversation = await conv_repo.get_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Create message
    message_repo = MessageRepository(db)
    message = await message_repo.create_message({
        "conversation_id": conversation_id,
        "content": message_data.content,
        "role": message_data.role
    })
    
    # Update conversation timestamp
    await conv_repo.update_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id,
        data={}  # Empty dict will just update the updated_at timestamp
    )
    
    # Generate assistant response if the user sent a message
    assistant_response = None
    if message_data.role == "user":
        try:
            # Import required services
            from app.services.llm.openai_client import OpenAIClient
            
            # Get conversation messages for context (excluding the message we just created)
            messages, _ = await message_repo.get_messages(conversation_id)
            
            # Filter out the message we just created and format for OpenAI API
            # Messages come newest first from DB, so reverse to get chronological order
            formatted_messages = []
            for msg in reversed(messages):
                # Skip the message we just created (it should be the newest)
                if msg.id != message.id:
                    formatted_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            # Add the current user message at the end
            formatted_messages.append({
                "role": message_data.role,
                "content": message_data.content
            })
            
            # Create a system message for the Mnemosyne assistant
            system_message = {
                "role": "system",
                "content": "You are Mnemosyne, an AI assistant that helps users with memory management, task organization, and knowledge retention. You are knowledgeable, helpful, and focused on helping users organize their thoughts and information effectively."
            }
            
            # Prepare messages with system context
            api_messages = [system_message] + formatted_messages
            
            # Generate response using OpenAI
            client = OpenAIClient()
            response_content = await client.chat_completion(
                messages=api_messages,
                max_tokens=500
            )
            
            # Create assistant message if we got a response
            if response_content:
                assistant_message = await message_repo.create_message({
                    "conversation_id": conversation_id,
                    "content": response_content,
                    "role": "assistant"
                })
                
                # Convert to MessageResponse object
                assistant_response = MessageResponse(
                    id=assistant_message.id,
                    conversation_id=assistant_message.conversation_id,
                    content=assistant_message.content,
                    role=assistant_message.role,
                    created_at=assistant_message.created_at
                )
                
                # Re-enable agent logging for chat interactions
                # Log the interaction with the agent system
                try:
                    agent_manager = AgentManager(db)
                    await agent_manager.assign_task(
                        agent_id="chat_assistant",  # Default chat agent ID
                        task={
                            "type": "chat_response",
                            "conversation_id": str(conversation_id),
                            "user_message": message_data.content,
                            "assistant_response": response_content,
                            "timestamp": str(message.created_at),
                            "metadata": {
                                "user_id": str(current_user.id),
                                "has_context": bool(formatted_messages),
                                "response_length": len(response_content)
                            }
                        }
                    )
                except Exception as agent_error:
                    # Log agent error but don't fail the chat response
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning("Agent integration failed: %s", str(agent_error))
                
        except Exception as e:
            # Log the error but don't fail the request
            import logging
            logger = logging.getLogger(__name__)
            logger.error("Failed to generate assistant response: %s", str(e))
    
    return MessageWithAssistantResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        content=message.content,
        role=message.role,
        created_at=message.created_at,
        assistant_response=assistant_response
    )


@router.post("/{conversation_id}/messages/stream/", status_code=status.HTTP_200_OK)
async def create_message_stream(
    conversation_id: UUID,
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Add a new message to a conversation and stream the assistant response.
    """
    # Verify conversation exists and belongs to user
    conv_repo = ConversationRepository(db)
    conversation = await conv_repo.get_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Create user message
    message_repo = MessageRepository(db)
    message = await message_repo.create_message({
        "conversation_id": conversation_id,
        "content": message_data.content,
        "role": message_data.role
    })
    
    # Update conversation timestamp
    await conv_repo.update_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id,
        data={}
    )
    
    async def generate_stream():
        """Generate streaming response"""
        try:
            # Send initial message data
            initial_data = {
                "type": "message",
                "data": {
                    "id": str(message.id),
                    "conversation_id": str(message.conversation_id),
                    "content": message.content,
                    "role": message.role,
                    "created_at": message.created_at.isoformat()
                }
            }
            yield f"data: {json.dumps(initial_data)}\n\n"
            
            if message_data.role == "user":
                # Import required services
                from app.services.llm.openai_client import OpenAIClient
                
                # Get conversation messages for context
                messages, _ = await message_repo.get_messages(conversation_id)
                
                # Format messages for OpenAI API
                formatted_messages = []
                for msg in reversed(messages):
                    if msg.id != message.id:
                        formatted_messages.append({
                            "role": msg.role,
                            "content": msg.content
                        })
                
                # Add the current user message
                formatted_messages.append({
                    "role": message_data.role,
                    "content": message_data.content
                })
                
                # Create system message
                system_message = {
                    "role": "system",
                    "content": "You are Mnemosyne, an AI assistant that helps users with memory management, task organization, and knowledge retention. You are knowledgeable, helpful, and focused on helping users organize their thoughts and information effectively."
                }
                
                # Prepare messages with system context
                api_messages = [system_message] + formatted_messages
                
                # Generate streaming response
                client = OpenAIClient()
                
                # Send assistant message start
                assistant_id = str(UUID("00000000-0000-0000-0000-000000000000"))  # Temporary ID
                assistant_start = {
                    "type": "assistant_start",
                    "data": {
                        "id": assistant_id,
                        "conversation_id": str(conversation_id),
                        "role": "assistant"
                    }
                }
                yield f"data: {json.dumps(assistant_start)}\n\n"
                
                # Stream the response
                full_response = ""
                async for chunk in await client.chat_completion(
                    messages=api_messages,
                    max_tokens=500,
                    stream=True
                ):
                    full_response += chunk
                    chunk_data = {
                        "type": "chunk",
                        "data": {
                            "content": chunk
                        }
                    }
                    yield f"data: {json.dumps(chunk_data)}\n\n"
                
                # Create the assistant message in the database
                if full_response:
                    assistant_message = await message_repo.create_message({
                        "conversation_id": conversation_id,
                        "content": full_response,
                        "role": "assistant"
                    })
                    
                    # Send final assistant message
                    assistant_final = {
                        "type": "assistant_complete",
                        "data": {
                            "id": str(assistant_message.id),
                            "conversation_id": str(assistant_message.conversation_id),
                            "content": full_response,
                            "role": "assistant",
                            "created_at": assistant_message.created_at.isoformat()
                        }
                    }
                    yield f"data: {json.dumps(assistant_final)}\n\n"
                    
                    # Re-enable agent logging for streaming chat
                    # Log with agent system
                    try:
                        agent_manager = AgentManager(db)
                        await agent_manager.assign_task(
                            agent_id="chat_assistant",
                            task={
                                "type": "chat_response_stream",
                                "conversation_id": str(conversation_id),
                                "user_message": message_data.content,
                                "assistant_response": full_response,
                                "timestamp": str(assistant_message.created_at),
                                "metadata": {
                                    "user_id": str(current_user.id),
                                    "streaming": True,
                                    "has_context": bool(formatted_messages),
                                    "response_length": len(full_response)
                                }
                            }
                        )
                    except Exception as agent_error:
                        # Log agent error but don't fail the streaming response
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning("Agent integration failed in streaming: %s", str(agent_error))
                    
        except Exception as e:
            error_data = {
                "type": "error",
                "data": {
                    "message": f"Failed to generate response: {str(e)}"
                }
            }
            yield f"data: {json.dumps(error_data)}\n\n"
        
        # Send completion signal
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )


@router.delete("/{conversation_id}/messages/{message_id}", response_model=SuccessResponse)
async def delete_message(
    conversation_id: UUID,
    message_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Delete a message from a conversation.
    """
    # Verify conversation exists and belongs to user
    conv_repo = ConversationRepository(db)
    conversation = await conv_repo.get_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Delete message
    message_repo = MessageRepository(db)
    success = await message_repo.delete_message(
        message_id=message_id,
        conversation_id=conversation_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    return {"success": True}
