"""
Memory Integration for Shadow Orchestrator.

This module provides integration between the Shadow orchestrator and 
the memory system, enabling context-aware responses.
"""

import logging
import json
from typing import Dict, List, Any, Optional

from memory.memory_manager import MemoryManager, default_memory_manager
from memory.memory_base import MemoryItem
from memory.document_store import DocumentItem

# Configure logging
logger = logging.getLogger("shadow.orchestrator.memory")


class OrchestratorMemory:
    """
    Memory integration for the Shadow orchestrator.
    
    Manages conversation history, context retrieval, and persistent storage
    of important information for the Shadow system.
    """
    
    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        """
        Initialize the orchestrator memory.
        
        Args:
            memory_manager: Optional memory manager instance
        """
        self.memory_manager = memory_manager or default_memory_manager
        self.current_conversation_id = None
        self.current_conversation = []
        logger.info("Initialized orchestrator memory integration")
    
    def start_conversation(self, conversation_id: Optional[str] = None) -> str:
        """
        Start a new conversation.
        
        Args:
            conversation_id: Optional ID for the conversation
            
        Returns:
            The conversation ID
        """
        self.current_conversation_id = conversation_id or f"conv_{len(self.current_conversation)}"
        self.current_conversation = []
        logger.info(f"Started new conversation with ID {self.current_conversation_id}")
        return self.current_conversation_id
    
    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the current conversation.
        
        Args:
            role: Role of the message sender (user, system, agent)
            content: Message content
        """
        self.current_conversation.append({
            "role": role,
            "content": content,
            "timestamp": str(self.memory_manager.embedding_service.get_embedding(content)[:5]),  # Mock timestamp
        })
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get the current conversation history.
        
        Returns:
            List of message dictionaries
        """
        return self.current_conversation
    
    def save_conversation(self) -> str:
        """
        Save the current conversation to memory.
        
        Returns:
            ID of the saved conversation
        """
        if not self.current_conversation:
            logger.warning("Attempted to save empty conversation")
            return None
        
        conversation_data = {
            "id": self.current_conversation_id,
            "title": f"Conversation {self.current_conversation_id}",
            "messages": self.current_conversation,
            "timestamp": str(self.memory_manager.embedding_service.get_embedding("timestamp")[:5]),  # Mock timestamp
        }
        
        conversation_id = self.memory_manager.store_conversation_memory(conversation_data)
        logger.info(f"Saved conversation with ID {conversation_id}")
        return conversation_id
    
    def get_relevant_context(self, user_input: str) -> Dict[str, Any]:
        """
        Get relevant context for a user input from memory.
        
        Args:
            user_input: The user's input text
            
        Returns:
            Dictionary of relevant context from memory
        """
        return self.memory_manager.get_agent_context(user_input)
    
    def store_important_information(self, title: str, content: str, source: str = None) -> Dict[str, str]:
        """
        Store important information in memory.
        
        Args:
            title: Title of the information
            content: Content of the information
            source: Optional source of the information
            
        Returns:
            Dictionary of storage type to ID of stored item
        """
        return self.memory_manager.store_knowledge(title, content, source)
    
    def add_entity(
        self, 
        name: str, 
        entity_type: str,
        description: str, 
        properties: Dict[str, Any] = None
    ) -> str:
        """
        Add an entity to the relational memory store.
        
        Args:
            name: Name of the entity
            entity_type: Type of the entity
            description: Description of the entity
            properties: Entity properties
            
        Returns:
            ID of the stored entity
        """
        return self.memory_manager.store_entity(
            name, entity_type, description, properties
        )

    def store_entity(
        self, 
        name: str, 
        entity_type: str,
        description: str, 
        properties: Dict[str, Any] = None
    ) -> str:
        """
        Store an entity to the relational memory store (alias for add_entity).
        
        Args:
            name: Name of the entity
            entity_type: Type of the entity
            description: Description of the entity
            properties: Entity properties
            
        Returns:
            ID of the stored entity
        """
        return self.add_entity(name, entity_type, description, properties)


# Create default orchestrator memory for easy import
default_orchestrator_memory = OrchestratorMemory()
