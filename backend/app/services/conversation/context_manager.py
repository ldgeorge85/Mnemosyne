"""
Conversation Context Manager

This module provides services for managing conversation context,
including tracking conversation state and managing context windows.
"""

import json
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.conversation import ConversationRepository, MessageRepository
from app.db.models.conversation import Conversation, Message


class ConversationContextManager:
    """
    Service for managing conversation context.
    
    This class handles:
    1. Context tracking (what's being discussed)
    2. Conversation state management
    3. Context window management (limiting the size of conversation history)
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize the context manager with a database session.
        
        Args:
            db_session: SQLAlchemy async session for database operations
        """
        self.db_session = db_session
        self.conversation_repo = ConversationRepository(db_session)
        self.message_repo = MessageRepository(db_session)
        
        # Default maximum number of messages to include in context
        self.default_context_window_size = 20
        
        # Default maximum number of tokens to include in context
        # This is an approximation as actual token count depends on the tokenizer
        self.default_max_tokens = 4000
        
        # Approximate tokens per message (can be refined based on actual data)
        self.avg_tokens_per_char = 0.25
    
    async def get_conversation_context(
        self, 
        conversation_id: str, 
        user_id: str, 
        max_messages: Optional[int] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get the current context for a conversation.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for access control)
            max_messages: Maximum number of messages to include (defaults to default_context_window_size)
            max_tokens: Maximum tokens to include (defaults to default_max_tokens)
            
        Returns:
            Dictionary with conversation context information
        """
        # Use default values if not specified
        max_messages = max_messages or self.default_context_window_size
        max_tokens = max_tokens or self.default_max_tokens
        
        # Get conversation details
        conversation = await self.conversation_repo.get_conversation(conversation_id, user_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Get recent messages for context, ordered by created_at (newest first)
        messages, _ = await self.message_repo.get_messages(
            conversation_id=conversation_id,
            limit=max_messages,
            offset=0
        )
        
        # Reverse messages to get chronological order (oldest first)
        messages_in_order = list(reversed(messages))
        
        # Apply token limit by estimating token count
        messages_for_context = self._limit_context_by_tokens(messages_in_order, max_tokens)
        
        # Prepare context object
        context = {
            "conversation_id": conversation.id,
            "title": conversation.title,
            "messages": [msg.to_dict() for msg in messages_for_context],
            "message_count": len(messages_for_context),
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
        }
        
        return context
    
    def _limit_context_by_tokens(self, messages: List[Message], max_tokens: int) -> List[Message]:
        """
        Limit the context by token count, keeping the most recent messages.
        
        Args:
            messages: List of messages in chronological order (oldest first)
            max_tokens: Maximum number of tokens to include
            
        Returns:
            List of messages that fit within the token limit
        """
        # Start with most recent messages (at the end of the list)
        selected_messages = []
        estimated_tokens = 0
        
        # Go through messages from newest to oldest
        for message in reversed(messages):
            # Estimate tokens in this message
            message_tokens = self._estimate_tokens(message.content)
            
            # If adding this message would exceed the limit, stop
            if estimated_tokens + message_tokens > max_tokens and selected_messages:
                break
            
            # Add message and update token count
            selected_messages.insert(0, message)  # Insert at beginning to maintain chronological order
            estimated_tokens += message_tokens
        
        return selected_messages
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in a text.
        This is a simple approximation - a proper tokenizer would be more accurate.
        
        Args:
            text: The text to estimate tokens for
            
        Returns:
            Estimated number of tokens
        """
        return int(len(text) * self.avg_tokens_per_char)
    
    async def save_context_metadata(
        self, 
        conversation_id: str, 
        user_id: str, 
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Save context metadata for a conversation.
        This can be used to store information about the conversation context,
        such as detected topics, entities, or other contextual information.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for access control)
            metadata: Dictionary of metadata to store
            
        Returns:
            True if successful, False otherwise
        """
        # First, verify the conversation exists and belongs to the user
        conversation = await self.conversation_repo.get_conversation(conversation_id, user_id)
        if not conversation:
            return False
        
        # Create a system message to store the metadata
        message_data = {
            "conversation_id": conversation_id,
            "content": json.dumps(metadata),
            "role": "system"
        }
        
        # Save the metadata as a system message
        await self.message_repo.create_message(message_data)
        
        return True
    
    async def extract_context_metadata(self, conversation_id: str, user_id: str) -> Dict[str, Any]:
        """
        Extract metadata from a conversation's system messages.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for access control)
            
        Returns:
            Dictionary of metadata from system messages
        """
        # First, verify the conversation exists and belongs to the user
        conversation = await self.conversation_repo.get_conversation(conversation_id, user_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Get all system messages
        messages = [msg for msg in conversation.messages if msg.role == "system"]
        
        # Extract metadata from system messages
        metadata = {}
        for message in messages:
            try:
                message_metadata = json.loads(message.content)
                metadata.update(message_metadata)
            except json.JSONDecodeError:
                # If the message content is not valid JSON, skip it
                continue
        
        return metadata
