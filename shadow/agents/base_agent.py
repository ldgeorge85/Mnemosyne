"""
Base Agent module for the Shadow system.

This module defines the base agent interface that all specialized agents
will implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class BaseAgent(ABC):
    """
    Abstract base class for all specialized agents.
    
    All agents in the Shadow system (Engineer, Librarian, Priest) should
    inherit from this class and implement its abstract methods.
    """
    
    def __init__(self, name: str):
        """
        Initialize the base agent.
        
        Args:
            name: The name of the agent
        """
        self.name = name
    
    @abstractmethod
    def process_request(self, user_input: str, conversation_history: List[Dict] = None, memory_context: Dict[str, Any] = None) -> str:
        """
        Process a user request and generate a response.
        
        Args:
            user_input: The user's request text
            conversation_history: Optional conversation history for context
            memory_context: Optional memory context from the orchestrator memory
            
        Returns:
            The agent's response string
        """
    
    def extract_knowledge(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Extract knowledge entities from a response that should be stored in memory.
        
        Specialized agents can override this to extract key information based on
        their domain expertise.
        
        Args:
            response: The agent's response
            
        Returns:
            Dictionary of extracted knowledge or None
        """
        return None
    
    def enhance_response_with_memory(self, response: str, memory_context: Dict[str, Any]) -> str:
        """
        Enhance an agent response with information from memory.
        
        Specialized agents can override this to improve responses using
        memory context.
        
        Args:
            response: The original agent response
            memory_context: Memory context from the orchestrator
            
        Returns:
            The enhanced response
        """
        return response
        pass
    
    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent type.
        
        Returns:
            The system prompt string
        """
        return f"You are a {self.name} agent."
