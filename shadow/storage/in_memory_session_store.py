"""
In-memory implementation of the session storage interface.

This module provides a simple in-memory implementation of the SessionStore
interface for testing and development purposes.
"""

from datetime import datetime
from typing import Dict, List, Optional
import copy

from models.session import ChatSession, ChatMessage
from storage.session_store import SessionStore


class InMemorySessionStore(SessionStore):
    """
    In-memory implementation of the SessionStore interface.
    
    This implementation stores sessions in a dictionary in memory.
    It's suitable for testing and development but not for production
    as sessions are lost when the server restarts.
    """
    
    def __init__(self):
        """Initialize an empty session store."""
        self.sessions: Dict[str, ChatSession] = {}
    
    async def create_session(self, session: ChatSession) -> str:
        """
        Create a new chat session.
        
        Args:
            session: The session to create
            
        Returns:
            The ID of the created session
        """
        # Store a deep copy to prevent external modifications
        self.sessions[session.id] = copy.deepcopy(session)
        return session.id
    
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """
        Retrieve a session by ID.
        
        Args:
            session_id: The ID of the session to retrieve
            
        Returns:
            The session if found, None otherwise
        """
        # Return a copy to prevent external modifications
        session = self.sessions.get(session_id)
        return copy.deepcopy(session) if session else None
    
    async def update_session(self, session: ChatSession) -> bool:
        """
        Update an existing session.
        
        Args:
            session: The session with updated fields
            
        Returns:
            True if the session was updated, False otherwise
        """
        if session.id not in self.sessions:
            return False
        
        # Update the timestamp
        session.updated_at = datetime.now()
        
        # Store a deep copy
        self.sessions[session.id] = copy.deepcopy(session)
        return True
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session by ID.
        
        Args:
            session_id: The ID of the session to delete
            
        Returns:
            True if the session was deleted, False otherwise
        """
        if session_id not in self.sessions:
            return False
        
        del self.sessions[session_id]
        return True
    
    async def list_user_sessions(self, user_id: str) -> List[ChatSession]:
        """
        List all sessions for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List of sessions belonging to the user
        """
        user_sessions = [
            session for session in self.sessions.values()
            if session.user_id == user_id
        ]
        
        # Sort by updated_at (most recent first)
        user_sessions.sort(key=lambda s: s.updated_at, reverse=True)
        
        # Return copies to prevent external modifications
        return [copy.deepcopy(session) for session in user_sessions]
    
    async def add_message(self, session_id: str, message: ChatMessage) -> bool:
        """
        Add a message to a session.
        
        Args:
            session_id: The ID of the session
            message: The message to add
            
        Returns:
            True if the message was added, False otherwise
        """
        if session_id not in self.sessions:
            return False
        
        # Get the session
        session = self.sessions[session_id]
        
        # Add the message
        session.messages.append(copy.deepcopy(message))
        
        # Update the timestamp
        session.updated_at = datetime.now()
        
        return True
    
    async def get_messages(self, session_id: str, limit: int = 100) -> List[ChatMessage]:
        """
        Get messages from a session.
        
        Args:
            session_id: The ID of the session
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of messages in the session
        """
        if session_id not in self.sessions:
            return []
        
        # Get the session
        session = self.sessions[session_id]
        
        # Return the most recent messages up to the limit
        messages = session.messages[-limit:] if limit > 0 else session.messages
        
        # Return copies to prevent external modifications
        return [copy.deepcopy(message) for message in messages]
