"""
Conversation API Endpoints

This module defines the API endpoints for managing conversations and messages.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.db import get_async_db
from app.api.dependencies.auth import get_current_user
from app.db.repositories.conversation import ConversationRepository, MessageRepository

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
    id: str
    conversation_id: str
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
    id: str
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
        user_id=current_user["id"],
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
        "user_id": current_user["id"]
    })
    
    return conversation


@router.get("/{conversation_id}", response_model=ConversationWithMessagesResponse)
async def get_conversation(
    conversation_id: str,
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
        user_id=current_user["id"]
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
    conversation_id: str,
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
        user_id=current_user["id"],
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
    conversation_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Delete a conversation.
    """
    repo = ConversationRepository(db)
    success = await repo.delete_conversation(
        conversation_id=conversation_id,
        user_id=current_user["id"]
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return {"success": True}


@router.post("/{conversation_id}/messages", response_model=MessageWithAssistantResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    conversation_id: str,
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
        user_id=current_user["id"]
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
        user_id=current_user["id"],
        data={}  # Empty dict will just update the updated_at timestamp
    )
    
    # In a future implementation, we would generate an assistant response here
    # For now, we'll just return the created message without an assistant response
    return {
        **message.to_dict(),
        "assistant_response": None
    }


@router.delete("/{conversation_id}/messages/{message_id}", response_model=SuccessResponse)
async def delete_message(
    conversation_id: str,
    message_id: str,
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
        user_id=current_user["id"]
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
