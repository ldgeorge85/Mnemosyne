"""
Session storage interface for the Shadow AI system.

This module defines the abstract interface for session storage backends,
allowing for different implementations (in-memory, database, etc.).
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from models.session import ChatSession, ChatMessage


class SessionStore(ABC):
    """
    Abstract interface for session storage backends.
    
    This interface defines the required methods for storing and retrieving
    chat sessions and their messages. Implementations can use different
    storage mechanisms (in-memory, database, etc.).
    """
    
    @abstractmethod
    async def create_session(self, session: ChatSession) -> str:
        """
        Create a new chat session.
        
        Args:
            session: The session to create
            
        Returns:
            The ID of the created session
        """
        pass
    
    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """
        Retrieve a session by ID.
        
        Args:
            session_id: The ID of the session to retrieve
            
        Returns:
            The session if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def update_session(self, session: ChatSession) -> bool:
        """
        Update an existing session.
        
        Args:
            session: The session with updated fields
            
        Returns:
            True if the session was updated, False otherwise
        """
        pass
    
    @abstractmethod
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session by ID.
        
        Args:
            session_id: The ID of the session to delete
            
        Returns:
            True if the session was deleted, False otherwise
        """
        pass
    
    @abstractmethod
    async def list_user_sessions(self, user_id: str) -> List[ChatSession]:
        """
        List all sessions for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List of sessions belonging to the user
        """
        pass
    
    @abstractmethod
    async def add_message(self, session_id: str, message: ChatMessage) -> bool:
        """
        Add a message to a session.
        
        Args:
            session_id: The ID of the session
            message: The message to add
            
        Returns:
            True if the message was added, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_messages(self, session_id: str, limit: int = 100) -> List[ChatMessage]:
        """
        Get messages from a session.
        
        Args:
            session_id: The ID of the session
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of messages in the session
        """
        pass
