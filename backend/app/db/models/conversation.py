"""
Conversation Models

This module defines the database models for conversations and messages.
"""

from sqlalchemy import Column, String, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_model import BaseModel


class Conversation(BaseModel):
    """
    Database model for a conversation.
    A conversation contains multiple messages and belongs to a user.
    """
    __tablename__ = "conversations"
    title = Column(String(255), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("ix_conversation_user_id", "user_id"),
    )


class Message(BaseModel):
    __tablename__ = "messages"
    """
    Database model for a message within a conversation.
    Messages can be from a user, assistant, or system.
    """
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    role = Column(String(10), nullable=False)  # 'user', 'assistant', or 'system'
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    # Indexes
    __table_args__ = (
        Index("ix_message_conversation_id", "conversation_id"),
        Index("ix_message_role", "role"),
    )
