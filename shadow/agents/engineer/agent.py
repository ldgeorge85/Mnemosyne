"""
Engineer Agent for the Shadow system.

This module implements the specialized Engineer agent responsible for technical
problem-solving, design, and mechanical/electrical/chemical reasoning.
"""

import logging
from typing import Dict, List, Optional, Any
import sys
import os

# Add parent directories to the path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import base agent and utilities
from agents.base_agent import BaseAgent
from utils.llm_connector import create_llm_connector, BaseLLMConnector
from utils.prompt_loader import get_prompt_loader

# Configure logging
logger = logging.getLogger("shadow.agents.engineer")


class EngineerAgent(BaseAgent):
    """
    Engineer agent specialized in technical problem-solving and design.
    
    This agent handles requests related to engineering, design, technical
    problem-solving, and system architecture using LLM-powered responses.
    """
    
    def __init__(self, llm_provider: str = None):
        """
        Initialize the Engineer agent.
        
        Args:
            llm_provider: Optional provider for the LLM (openai, anthropic, local)
        """
        super().__init__("Engineer")
        
        # Set up prompt loader
        self.prompt_loader = get_prompt_loader("engineer")
        
        # Set up LLM connector
        self.use_llm = True
        try:
            self.llm_connector = create_llm_connector(llm_provider)
            logger.info(f"Engineer agent initialized with {type(self.llm_connector).__name__}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM connector: {str(e)}. Using mock responses.")
            self.use_llm = False
    
    def process_request(self, user_input: str, conversation_history: List[Dict] = None, memory_context: Dict[str, Any] = None) -> str:
        """
        Process a user request from an engineering perspective.
        
        Uses an LLM with engineering-focused prompting to generate responses.
        Falls back to mock responses if LLM is not available.
        
        Args:
            user_input: The user's request text
            conversation_history: Optional conversation history for context
            memory_context: Optional memory context from the orchestrator memory
            
        Returns:
            The agent's response string
        """
        # Determine prompt template based on request content
        system_prompt = self._select_prompt_template(user_input)
        
        # Prepare memory context for inclusion in the prompt
        context_str = self._prepare_memory_context(memory_context) if memory_context else ""
        
        if self.use_llm:
            try:
                # Generate response using LLM with memory context
                augmented_user_input = user_input
                if context_str:
                    augmented_user_input = f"Context from memory:\n{context_str}\n\nUser request: {user_input}"
                
                response = self.llm_connector.generate_text(
                    system_prompt=system_prompt,
                    user_input=augmented_user_input,
                    conversation_history=conversation_history
                )
                
                # Extract and return any important technical knowledge
                self.extract_knowledge(response)
                
                return response
            except Exception as e:
                logger.error(f"Error generating LLM response: {str(e)}. Falling back to mock response.")
                self.use_llm = False
        
        # Fall back to mock implementation if LLM fails or is unavailable
        mock_response = (
            f"Engineer Agent Response (Mock):\n\n"
            f"I've analyzed your request: '{user_input}' from an engineering perspective.\n\n"
        )
        
        if context_str:
            mock_response += f"Based on the available context:\n{context_str}\n\n"
        
        mock_response += (
            f"As an Engineer agent, I would provide technical analysis, design considerations, "
            f"system architecture, and implementation approaches. "
            f"This is a mock response as the LLM integration is unavailable."
        )
        
        return mock_response
    
    def _prepare_memory_context(self, memory_context: Dict[str, Any]) -> str:
        """
        Format memory context for inclusion in prompts.
        
        Args:
            memory_context: Memory context from the orchestrator
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Add relevant documents from vector memory if available
        if "relevant_documents" in memory_context and memory_context["relevant_documents"]:
            context_parts.append("Relevant documents from memory:")
            for i, doc in enumerate(memory_context["relevant_documents"][:3]):
                context_parts.append(f"[{i+1}] {doc.get('title', 'Document')}: {doc.get('content', 'No content')}")
        
        # Add relevant entities from relational memory if available
        if "relevant_entities" in memory_context and memory_context["relevant_entities"]:
            context_parts.append("\nRelevant entities from memory:")
            for i, entity in enumerate(memory_context["relevant_entities"][:5]):
                context_parts.append(f"[{i+1}] {entity.get('name', 'Entity')}: {entity.get('description', 'No description')}")
        
        # Add recent conversation summary if available
        if "conversation_summary" in memory_context and memory_context["conversation_summary"]:
            context_parts.append("\nRecent conversation summary:")
            context_parts.append(memory_context["conversation_summary"])
            
        return "\n".join(context_parts)
    
    def extract_knowledge(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Extract technical knowledge from the response for storage in memory.
        
        Args:
            response: The agent's response
            
        Returns:
            Dictionary of extracted knowledge or None
        """
        # In a real implementation, this could use an LLM to extract technical concepts,
        # specifications, and design patterns from the response
        
        # Simple keyword-based extraction for now
        technical_terms = ["algorithm", "architecture", "framework", "pattern", "design", 
                          "system", "database", "infrastructure", "protocol"]
        
        found_knowledge = {}
        
        for term in technical_terms:
            # Very simple detection - in production would use NLP or an LLM
            if term in response.lower():
                found_knowledge[term] = True
        
        if found_knowledge:
            # Return a simplified knowledge extraction result
            return {
                "type": "technical_concepts",
                "content": response[:100] + "...",  # Truncated for simplicity
                "detected_terms": list(found_knowledge.keys())
            }
        
        return None
        
    def _select_prompt_template(self, user_input: str) -> str:
        """
        Select the appropriate prompt template based on the user input.
        
        Analyzes the user input to determine the most suitable engineering
        prompt template (design, problem-solving, optimization, etc.)
        
        Args:
            user_input: The user's request text
            
        Returns:
            The selected prompt template
        """
        # Simple keyword-based template selection
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ["design", "create", "build", "architect"]):
            return self.prompt_loader.get_prompt("design_prompt", self.prompt_loader.get_system_prompt())
        
        elif any(word in input_lower for word in ["problem", "fix", "solve", "troubleshoot"]):
            return self.prompt_loader.get_prompt("problem_solving_prompt", self.prompt_loader.get_system_prompt())
        
        elif any(word in input_lower for word in ["optimize", "improve", "efficiency", "performance"]):
            return self.prompt_loader.get_prompt("optimization_prompt", self.prompt_loader.get_system_prompt())
        
        elif any(word in input_lower for word in ["feasible", "possible", "realistic", "practical"]):
            return self.prompt_loader.get_prompt("feasibility_prompt", self.prompt_loader.get_system_prompt())
        
        # Default to system prompt if no specific template matches
        return self.prompt_loader.get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """
        Get the specialized system prompt for the Engineer agent.
        
        Returns:
            The system prompt string
        """
        return self.prompt_loader.get_system_prompt()


# Create a default instance for easy import
default_engineer = EngineerAgent()
