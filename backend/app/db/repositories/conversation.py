"""
Conversation Repository

This module provides repository classes for conversation and message operations.
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.conversation import Conversation, Message


class ConversationRepository:
    """
    Repository for conversation operations.
    Handles data access and persistence for conversation entities.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            session: The SQLAlchemy async database session
        """
        self.session = session

    async def get_conversations(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> Tuple[List[Conversation], int]:
        """
        Get a paginated list of conversations for a user.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of items to return
            offset: Pagination offset
            
        Returns:
            Tuple containing the list of conversations and the total count
        """
        # Get total count
        count_query = select(func.count()).select_from(Conversation).where(
            Conversation.user_id == user_id
        )
        total = await self.session.scalar(count_query)
        
        # Get paginated conversations with last message
        query = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .options(
                selectinload(Conversation.messages).order_by(desc(Message.created_at)).limit(1)
            )
            .order_by(desc(Conversation.updated_at))
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.session.execute(query)
        conversations = result.scalars().all()
        
        return conversations, total or 0

    async def get_conversation(self, conversation_id: str, user_id: str) -> Optional[Conversation]:
        """
        Get a specific conversation by ID with its messages.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for authorization)
            
        Returns:
            The conversation or None if not found
        """
        query = (
            select(Conversation)
            .where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
            .options(selectinload(Conversation.messages))
        )
        
        result = await self.session.execute(query)
        return result.scalars().first()

    async def create_conversation(self, data: Dict[str, Any]) -> Conversation:
        """
        Create a new conversation.
        
        Args:
            data: Dictionary containing conversation data
            
        Returns:
            The created conversation
        """
        conversation = Conversation(**data)
        self.session.add(conversation)
        await self.session.flush()
        return conversation

    async def update_conversation(self, conversation_id: str, user_id: str, data: Dict[str, Any]) -> Optional[Conversation]:
        """
        Update a conversation.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for authorization)
            data: Dictionary containing updated conversation data
            
        Returns:
            The updated conversation or None if not found
        """
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            return None
        
        for key, value in data.items():
            setattr(conversation, key, value)
        
        await self.session.flush()
        return conversation

    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """
        Delete a conversation.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for authorization)
            
        Returns:
            True if deleted, False if not found
        """
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            return False
        
        await self.session.delete(conversation)
        await self.session.flush()
        return True


class MessageRepository:
    """
    Repository for message operations.
    Handles data access and persistence for message entities.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            session: The SQLAlchemy async database session
        """
        self.session = session

    async def get_messages(
        self, conversation_id: str, limit: int = 50, offset: int = 0
    ) -> Tuple[List[Message], int]:
        """
        Get a paginated list of messages for a conversation.
        
        Args:
            conversation_id: ID of the conversation
            limit: Maximum number of items to return
            offset: Pagination offset
            
        Returns:
            Tuple containing the list of messages and the total count
        """
        # Get total count
        count_query = select(func.count()).select_from(Message).where(
            Message.conversation_id == conversation_id
        )
        total = await self.session.scalar(count_query)
        
        # Get paginated messages
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.session.execute(query)
        messages = result.scalars().all()
        
        return messages, total or 0

    async def create_message(self, data: Dict[str, Any]) -> Message:
        """
        Create a new message.
        
        Args:
            data: Dictionary containing message data
            
        Returns:
            The created message
        """
        message = Message(**data)
        self.session.add(message)
        await self.session.flush()
        return message

    async def delete_message(self, message_id: str, conversation_id: str) -> bool:
        """
        Delete a message.
        
        Args:
            message_id: ID of the message
            conversation_id: ID of the conversation (for validation)
            
        Returns:
            True if deleted, False if not found
        """
        query = (
            select(Message)
            .where(
                Message.id == message_id,
                Message.conversation_id == conversation_id
            )
        )
        
        result = await self.session.execute(query)
        message = result.scalars().first()
        
        if not message:
            return False
        
        await self.session.delete(message)
        await self.session.flush()
        return True
