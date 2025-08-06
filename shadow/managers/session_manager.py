"""
Session manager for the Shadow AI system.

This module provides a high-level interface for managing chat sessions,
integrating with the storage backend and memory system.
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from uuid import uuid4

from models.session import ChatSession, ChatMessage
from storage.session_store import SessionStore
from storage.in_memory_session_store import InMemorySessionStore

# Configure logging
logger = logging.getLogger("shadow.session")


class SessionManager:
    """
    Manages chat sessions for the Shadow AI system.
    
    This class provides a high-level interface for creating, retrieving,
    updating, and deleting chat sessions. It integrates with the storage
    backend and memory system to provide a unified interface.
    """
    
    def __init__(self, session_store: Optional[SessionStore] = None, memory_manager = None):
        """
        Initialize the session manager.
        
        Args:
            session_store: Storage backend for sessions
            memory_manager: Memory manager for integration with the memory system
        """
        self.session_store = session_store or InMemorySessionStore()
        self.memory_manager = memory_manager
        logger.info("Initialized Shadow Session Manager")
    
    async def create_session(self, user_id: str, title: Optional[str] = None) -> ChatSession:
        """
        Create a new chat session.
        
        Args:
            user_id: ID of the user creating the session
            title: Optional title for the session
            
        Returns:
            The created session
        """
        session = ChatSession(
            id=str(uuid4()),
            user_id=user_id,
            title=title or "New Chat",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            messages=[],
            metadata={},
            is_active=True
        )
        
        await self.session_store.create_session(session)
        logger.info(f"Created session {session.id} for user {user_id}")
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """
        Retrieve a session by ID.
        
        Args:
            session_id: ID of the session to retrieve
            
        Returns:
            The session if found, None otherwise
        """
        session = await self.session_store.get_session(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found")
        return session
    
    async def update_session(self, session: ChatSession) -> bool:
        """
        Update an existing session.
        
        Args:
            session: The session with updated fields
            
        Returns:
            True if the session was updated, False otherwise
        """
        # Update the timestamp
        session.updated_at = datetime.now()
        
        success = await self.session_store.update_session(session)
        if success:
            logger.info(f"Updated session {session.id}")
        else:
            logger.warning(f"Failed to update session {session.id}")
        
        return success
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session by ID.
        
        Args:
            session_id: ID of the session to delete
            
        Returns:
            True if the session was deleted, False otherwise
        """
        success = await self.session_store.delete_session(session_id)
        if success:
            logger.info(f"Deleted session {session_id}")
        else:
            logger.warning(f"Failed to delete session {session_id}")
        
        return success
    
    async def list_user_sessions(self, user_id: str) -> List[ChatSession]:
        """
        List all sessions for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of sessions belonging to the user
        """
        sessions = await self.session_store.list_user_sessions(user_id)
        logger.info(f"Retrieved {len(sessions)} sessions for user {user_id}")
        return sessions
    
    async def add_message(self, session_id: str, role: str, content: str, 
                         agent: Optional[str] = None, metadata: Optional[Dict] = None) -> bool:
        """
        Add a message to a session.
        
        Args:
            session_id: ID of the session
            role: Role of the message sender ("user" or "assistant")
            content: Content of the message
            agent: Optional name of the agent that generated the message
            metadata: Optional additional data about the message
            
        Returns:
            True if the message was added, False otherwise
        """
        message = ChatMessage(
            role=role,
            content=content,
            agent=agent,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        success = await self.session_store.add_message(session_id, message)
        
        if success:
            logger.info(f"Added {role} message to session {session_id}")
            
            # If memory manager is available, store the message in memory
            if self.memory_manager and role == "assistant":
                try:
                    # Store assistant responses in memory for future context
                    memory_item = {
                        "content": content,
                        "metadata": {
                            "session_id": session_id,
                            "agent": agent,
                            "timestamp": message.timestamp.isoformat()
                        },
                        "type": "conversation"
                    }
                    
                    # This is a placeholder - actual implementation depends on memory_manager interface
                    if hasattr(self.memory_manager, "store_memory"):
                        await self.memory_manager.store_memory(memory_item)
                        
                except Exception as e:
                    logger.error(f"Failed to store message in memory: {str(e)}")
        else:
            logger.warning(f"Failed to add message to session {session_id}")
        
        return success
    
    async def get_messages(self, session_id: str, limit: int = 100) -> List[ChatMessage]:
        """
        Get messages from a session.
        
        Args:
            session_id: ID of the session
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of messages in the session
        """
        messages = await self.session_store.get_messages(session_id, limit)
        logger.info(f"Retrieved {len(messages)} messages from session {session_id}")
        return messages
    
    async def get_conversation_context(self, session_id: str, query: str) -> Dict[str, Any]:
        """
        Get conversation context for a query.
        
        This method retrieves the conversation history and relevant memories
        for a query to provide context for the response.
        
        Args:
            session_id: ID of the session
            query: The user's query
            
        Returns:
            Dictionary with conversation history and relevant memories
        """
        # Get conversation history
        messages = await self.get_messages(session_id)
        
        # Convert to format expected by agents
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        context = {
            "conversation_history": conversation_history,
            "session_id": session_id
        }
        
        # If memory manager is available, get relevant memories
        if self.memory_manager:
            try:
                # This is a placeholder - actual implementation depends on memory_manager interface
                if hasattr(self.memory_manager, "get_relevant_context"):
                    memory_context = await self.memory_manager.get_relevant_context(query)
                    context.update(memory_context)
            except Exception as e:
                logger.error(f"Failed to get relevant memories: {str(e)}")
        
        return context


# Create default session manager for easy import
default_session_manager = SessionManager()
