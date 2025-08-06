"""
Session models for the Shadow AI system.

This module defines the data models for chat sessions and messages,
providing structured representations for session management.
"""

from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from uuid import uuid4


class ChatMessage(BaseModel):
    """
    Represents a single message in a chat session.
    
    Attributes:
        role: The role of the message sender ("user" or "assistant")
        content: The text content of the message
        agent: Optional name of the agent that generated the message
        timestamp: When the message was created
        metadata: Optional additional data about the message
    """
    role: str  # "user" or "assistant"
    content: str
    agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict] = None


class ChatSession(BaseModel):
    """
    Represents a chat session with multiple messages.
    
    Attributes:
        id: Unique identifier for the session
        user_id: Identifier for the user who owns the session
        title: Display title for the session
        created_at: When the session was created
        updated_at: When the session was last updated
        messages: List of messages in the session
        metadata: Optional additional data about the session
        is_active: Whether the session is active
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    title: str = "New Chat"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    messages: List[ChatMessage] = []
    metadata: Dict = {}
    is_active: bool = True
