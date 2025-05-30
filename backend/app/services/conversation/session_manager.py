"""
Conversation Session Manager

This module provides services for managing active conversation sessions,
including tracking active conversations and managing conversation states.
"""

import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.conversation import ConversationRepository
from app.utils.common import utc_now


class ConversationState:
    """
    Represents the state of an active conversation.
    This tracks metadata about the conversation session, such as
    when it was last active, what the current topic is, etc.
    """
    
    def __init__(self, conversation_id: str, user_id: str):
        """
        Initialize a conversation state.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user
        """
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.last_active_time = utc_now()
        self.current_topic = None
        self.metadata = {}
        self.is_active = True
    
    def update_activity(self):
        """Update the last active time to now."""
        self.last_active_time = utc_now()
    
    def set_topic(self, topic: str):
        """
        Set the current topic of the conversation.
        
        Args:
            topic: The current topic
        """
        self.current_topic = topic
    
    def add_metadata(self, key: str, value: Any):
        """
        Add metadata to the conversation state.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the state to a dictionary.
        
        Returns:
            Dictionary representation of the state
        """
        return {
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "last_active_time": self.last_active_time.isoformat(),
            "current_topic": self.current_topic,
            "metadata": self.metadata,
            "is_active": self.is_active
        }


class ConversationSessionManager:
    """
    Service for managing active conversation sessions.
    
    This class handles:
    1. Tracking which conversations are active
    2. Managing conversation state
    3. Session timeout management
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize the session manager with a database session.
        
        Args:
            db_session: SQLAlchemy async session for database operations
        """
        self.db_session = db_session
        self.conversation_repo = ConversationRepository(db_session)
        
        # Dictionary to store active conversation states
        # Key: conversation_id, Value: ConversationState
        self.active_conversations: Dict[str, ConversationState] = {}
        
        # Default session timeout (in minutes)
        self.session_timeout = 30
    
    async def get_active_conversation(
        self, 
        conversation_id: str, 
        user_id: str
    ) -> Optional[ConversationState]:
        """
        Get the state of an active conversation.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for access control)
            
        Returns:
            ConversationState if active, None otherwise
        """
        # Check if the conversation is in the active list
        state = self.active_conversations.get(conversation_id)
        
        # If not found or belongs to a different user, return None
        if not state or state.user_id != user_id:
            # Check if the conversation exists in the database
            conversation = await self.conversation_repo.get_conversation(conversation_id, user_id)
            if not conversation:
                return None
            
            # Create a new state for this conversation
            state = ConversationState(conversation_id, user_id)
            self.active_conversations[conversation_id] = state
        
        # Update the last active time
        state.update_activity()
        
        return state
    
    async def get_active_conversations_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all active conversations for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of active conversation states as dictionaries
        """
        # Filter conversations by user and check timeouts
        self._cleanup_inactive_sessions()
        
        active_states = [
            state.to_dict() 
            for state in self.active_conversations.values() 
            if state.user_id == user_id and state.is_active
        ]
        
        return active_states
    
    def _cleanup_inactive_sessions(self):
        """
        Clean up inactive sessions based on timeout.
        """
        current_time = utc_now()
        timeout_delta = timedelta(minutes=self.session_timeout)
        
        # Mark sessions as inactive if they've timed out
        for state in self.active_conversations.values():
            if (current_time - state.last_active_time) > timeout_delta:
                state.is_active = False
    
    async def mark_conversation_active(
        self, 
        conversation_id: str, 
        user_id: str
    ) -> ConversationState:
        """
        Mark a conversation as active or update its activity timestamp.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for access control)
            
        Returns:
            Updated ConversationState
        """
        # Check if the conversation exists
        conversation = await self.conversation_repo.get_conversation(conversation_id, user_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Get or create the state
        state = self.active_conversations.get(conversation_id)
        if not state or state.user_id != user_id:
            state = ConversationState(conversation_id, user_id)
            self.active_conversations[conversation_id] = state
        
        # Update activity
        state.update_activity()
        state.is_active = True
        
        return state
    
    async def mark_conversation_inactive(
        self, 
        conversation_id: str, 
        user_id: str
    ) -> bool:
        """
        Mark a conversation as inactive.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for access control)
            
        Returns:
            True if successful, False otherwise
        """
        state = self.active_conversations.get(conversation_id)
        if not state or state.user_id != user_id:
            return False
        
        state.is_active = False
        return True
    
    async def update_conversation_metadata(
        self,
        conversation_id: str,
        user_id: str,
        metadata: Dict[str, Any]
    ) -> Optional[ConversationState]:
        """
        Update metadata for a conversation.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for access control)
            metadata: Dictionary of metadata to update
            
        Returns:
            Updated ConversationState if successful, None otherwise
        """
        state = await self.get_active_conversation(conversation_id, user_id)
        if not state:
            return None
        
        # Update metadata
        for key, value in metadata.items():
            state.add_metadata(key, value)
        
        # If topic is provided, update it
        if "topic" in metadata:
            state.set_topic(metadata["topic"])
        
        return state
