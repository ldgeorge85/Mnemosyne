"""
Conversation Repository

This module provides repository classes for conversation and message operations.
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, desc, func, text
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
        Get paginated conversations for a user.

        Args:
            user_id: The user ID to get conversations for.
            limit: The maximum number of conversations to return.
            offset: The offset to start from.

        Returns:
            Tuple containing the list of conversations and the total count
        """
        # Use raw SQL for count
        count_query = text("SELECT COUNT(*) FROM conversations WHERE user_id = :user_id")
        count_result = await self.session.execute(count_query, {"user_id": user_id})
        total = count_result.scalar() or 0
        
        # Get paginated conversations with raw SQL
        conv_query = text("""
            SELECT id, title, created_at, updated_at, user_id 
            FROM conversations 
            WHERE user_id = :user_id 
            ORDER BY updated_at DESC 
            LIMIT :limit OFFSET :offset
        """)
        conv_result = await self.session.execute(
            conv_query, 
            {"user_id": user_id, "limit": limit, "offset": offset}
        )
        
        # Convert to Conversation objects
        conversations = []
        for row in conv_result.fetchall():
            conv = Conversation(
                id=row.id,
                title=row.title,
                created_at=row.created_at,
                updated_at=row.updated_at,
                user_id=row.user_id,
                messages=[]
            )
            conversations.append(conv)
        
        # For each conversation, get the latest message
        for conv in conversations:
            msg_query = text("""
                SELECT id, content, role, created_at, updated_at, conversation_id 
                FROM messages 
                WHERE conversation_id = :conv_id 
                ORDER BY created_at DESC 
                LIMIT 1
            """)
            msg_result = await self.session.execute(msg_query, {"conv_id": conv.id})
            msg_row = msg_result.fetchone()
            if msg_row:
                msg = Message(
                    id=msg_row.id,
                    content=msg_row.content,
                    role=msg_row.role,
                    created_at=msg_row.created_at,
                    updated_at=msg_row.updated_at,
                    conversation_id=msg_row.conversation_id
                )
                conv.messages = [msg]
            
        return conversations, total

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
        # Create a new conversation instance
        conversation = Conversation()
        
        # Set attributes manually
        conversation.title = data.get('title')
        conversation.user_id = data.get('user_id')
        
        # Add to session and flush to generate ID and timestamps
        # but don't commit yet to avoid detaching the object
        self.session.add(conversation)
        await self.session.flush()
        
        # Create a dictionary copy of the conversation data to return
        # This avoids issues with detached objects after commit
        result = {
            "id": conversation.id,
            "title": conversation.title,
            "user_id": conversation.user_id,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at
        }
        
        # Now commit the transaction
        await self.session.commit()
        
        # Return the conversation data dictionary
        return Conversation(**result)

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
        Get paginated messages for a conversation.

        Args:
            conversation_id: The conversation ID to get messages for.
            limit: The maximum number of messages to return.
            offset: The offset to start from.

        Returns:
            Tuple containing the list of messages and the total count
        """
        # Use raw SQL for count with the correct table name
        count_query = text("SELECT COUNT(*) FROM messages WHERE conversation_id = :conversation_id")
        count_result = await self.session.execute(count_query, {"conversation_id": conversation_id})
        total = count_result.scalar() or 0
        
        # Get paginated messages with raw SQL using the correct table name
        msg_query = text("""
            SELECT id, content, role, created_at, updated_at, conversation_id 
            FROM messages 
            WHERE conversation_id = :conversation_id 
            ORDER BY created_at DESC 
            LIMIT :limit OFFSET :offset
        """)
        msg_result = await self.session.execute(
            msg_query, 
            {"conversation_id": conversation_id, "limit": limit, "offset": offset}
        )
        
        # Convert to Message objects
        messages = []
        for row in msg_result.fetchall():
            msg = Message(
                id=row.id,
                content=row.content,
                role=row.role,
                created_at=row.created_at,
                updated_at=row.updated_at,
                conversation_id=row.conversation_id
            )
            messages.append(msg)
            
        return messages, total

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
        
        # Create a dictionary copy of the message data to return
        # This avoids issues with detached objects after commit
        result = {
            "id": message.id,
            "content": message.content,
            "role": message.role,
            "conversation_id": message.conversation_id,
            "created_at": message.created_at,
            "updated_at": message.updated_at
        }
        
        # Now commit the transaction
        await self.session.commit()
        
        # Return the message data dictionary
        return Message(**result)

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
