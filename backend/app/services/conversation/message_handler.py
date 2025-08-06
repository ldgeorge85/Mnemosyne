"""
Message Handling System

This module provides services for processing, validating,
and managing conversation messages, including content sanitization,
error handling, and processing pipeline management.
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.conversation import ConversationRepository, MessageRepository
from app.db.models.conversation import Message

logger = logging.getLogger(__name__)


class MessageValidationError(Exception):
    """Exception raised for message validation errors."""
    pass


class MessageProcessor:
    """
    Base class for message processors in the pipeline.
    Each processor handles a specific aspect of message processing.
    """
    
    async def process(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message and return the modified message data.
        
        Args:
            message_data: The message data to process
            
        Returns:
            The processed message data
        """
        # Base implementation does nothing
        return message_data


class ContentSanitizer(MessageProcessor):
    """Message processor that sanitizes message content."""
    
    def __init__(self, max_length: int = 10000):
        """
        Initialize the sanitizer.
        
        Args:
            max_length: Maximum allowed content length
        """
        self.max_length = max_length
    
    async def process(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize message content.
        
        Args:
            message_data: The message data to process
            
        Returns:
            The processed message data with sanitized content
            
        Raises:
            MessageValidationError: If content is invalid
        """
        content = message_data.get("content", "")
        
        # Check content length
        if not content:
            raise MessageValidationError("Message content cannot be empty")
        
        if len(content) > self.max_length:
            raise MessageValidationError(f"Message content exceeds maximum length of {self.max_length} characters")
        
        # Sanitize content: remove null bytes, control characters, etc.
        # This is a simple example - in production, use a proper HTML sanitizer
        sanitized_content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)
        
        # Replace the content with sanitized version
        message_data["content"] = sanitized_content
        
        return message_data


class RoleValidator(MessageProcessor):
    """Message processor that validates message roles."""
    
    def __init__(self, allowed_roles: List[str] = None):
        """
        Initialize the validator.
        
        Args:
            allowed_roles: List of allowed roles
        """
        self.allowed_roles = allowed_roles or ["user", "assistant", "system"]
    
    async def process(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate message role.
        
        Args:
            message_data: The message data to process
            
        Returns:
            The processed message data
            
        Raises:
            MessageValidationError: If role is invalid
        """
        role = message_data.get("role")
        
        if not role:
            raise MessageValidationError("Message role is required")
        
        if role not in self.allowed_roles:
            raise MessageValidationError(f"Invalid message role: {role}. Allowed roles: {', '.join(self.allowed_roles)}")
        
        return message_data


class MessageLogger(MessageProcessor):
    """Message processor that logs message data."""
    
    async def process(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log message data.
        
        Args:
            message_data: The message data to process
            
        Returns:
            The processed message data
        """
        # In a real implementation, this would log to a logging system
        # For now, we'll just print to the console
        logger.info(f"Processing message: {message_data.get('role')} message for conversation {message_data.get('conversation_id')}")
        
        return message_data


class MessageHandler:
    """
    Service for handling message processing, validation,
    and error handling throughout the message lifecycle.
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize the message handler with a database session.
        
        Args:
            db_session: SQLAlchemy async session for database operations
        """
        self.db_session = db_session
        self.conversation_repo = ConversationRepository(db_session)
        self.message_repo = MessageRepository(db_session)
        
        # Set up the processing pipeline
        self.processors: List[MessageProcessor] = [
            ContentSanitizer(),
            RoleValidator(),
            MessageLogger()
        ]
        
        # Error handlers mapped by error type
        self.error_handlers: Dict[type, Callable] = {}
    
    def register_processor(self, processor: MessageProcessor) -> None:
        """
        Register a message processor in the pipeline.
        
        Args:
            processor: The processor to register
        """
        self.processors.append(processor)
    
    def register_error_handler(self, error_type: type, handler: Callable) -> None:
        """
        Register an error handler for a specific error type.
        
        Args:
            error_type: The type of error to handle
            handler: The handler function
        """
        self.error_handlers[error_type] = handler
    
    async def process_message(self, message_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], Optional[Exception]]:
        """
        Process a message through the pipeline.
        
        Args:
            message_data: The message data to process
            
        Returns:
            Tuple of (success, processed_data, error)
        """
        try:
            processed_data = message_data.copy()
            
            # Run through all processors in the pipeline
            for processor in self.processors:
                processed_data = await processor.process(processed_data)
            
            return True, processed_data, None
        except Exception as e:
            # Handle the error
            handled = await self._handle_error(e, message_data)
            
            if handled:
                # If the error was handled, return partial success
                return False, message_data, e
            else:
                # If the error wasn't handled, re-raise it
                raise
    
    async def _handle_error(self, error: Exception, message_data: Dict[str, Any]) -> bool:
        """
        Handle an error using registered error handlers.
        
        Args:
            error: The error to handle
            message_data: The message data that caused the error
            
        Returns:
            True if the error was handled, False otherwise
        """
        # Find a handler for this error type
        for error_type, handler in self.error_handlers.items():
            if isinstance(error, error_type):
                await handler(error, message_data)
                return True
        
        # No handler found
        return False
    
    async def create_message(self, message_data: Dict[str, Any]) -> Optional[Message]:
        """
        Create a new message after processing.
        
        Args:
            message_data: The message data to process and create
            
        Returns:
            The created message or None if processing failed
            
        Raises:
            MessageValidationError: If validation fails
            ValueError: If the conversation doesn't exist
        """
        # Verify the conversation exists
        conversation = await self.conversation_repo.get_conversation(
            message_data["conversation_id"],
            message_data.get("user_id")  # This might be None for system messages
        )
        
        if not conversation:
            raise ValueError(f"Conversation {message_data['conversation_id']} not found")
        
        # Process the message
        success, processed_data, error = await self.process_message(message_data)
        
        if not success:
            # Log the error
            logger.error(f"Error processing message: {error}")
            
            # Re-raise validation errors
            if isinstance(error, MessageValidationError):
                raise error
            
            # For other errors, return None
            return None
        
        # Create the message
        message = await self.message_repo.create_message(processed_data)
        
        return message
    
    async def get_message_history(
        self, 
        conversation_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> Tuple[List[Message], int]:
        """
        Get the message history for a conversation.
        
        Args:
            conversation_id: ID of the conversation
            limit: Maximum number of messages to return
            offset: Pagination offset
            
        Returns:
            Tuple of (messages, total_count)
        """
        return await self.message_repo.get_messages(conversation_id, limit, offset)
    
    async def delete_message(self, message_id: str, conversation_id: str) -> bool:
        """
        Delete a message.
        
        Args:
            message_id: ID of the message to delete
            conversation_id: ID of the conversation
            
        Returns:
            True if deleted, False if not found
        """
        return await self.message_repo.delete_message(message_id, conversation_id)


class MessageEventDispatcher:
    """
    Service for dispatching message events to subscribers.
    This allows for decoupled handling of message-related events.
    """
    
    def __init__(self):
        """Initialize the event dispatcher."""
        # Event subscribers mapped by event type
        self.subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """
        Subscribe to an event type.
        
        Args:
            event_type: The type of event to subscribe to
            callback: The callback function to call when the event occurs
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(callback)
    
    async def dispatch(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Dispatch an event to all subscribers.
        
        Args:
            event_type: The type of event to dispatch
            data: The event data
        """
        if event_type not in self.subscribers:
            return
        
        # Call all subscribers for this event type
        for callback in self.subscribers[event_type]:
            try:
                await callback(data)
            except Exception as e:
                # Log errors but don't stop dispatching
                logger.error(f"Error in event subscriber: {e}", exc_info=True)


# Predefined event types
class MessageEventTypes:
    """Enum-like class defining message event types."""
    CREATED = "message.created"
    UPDATED = "message.updated"
    DELETED = "message.deleted"
    ERROR = "message.error"
