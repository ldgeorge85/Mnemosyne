"""
Librarian Agent for the Shadow system.

This module implements the specialized Librarian agent responsible for 
information retrieval, semantic search, and structured data management.
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
logger = logging.getLogger("shadow.agents.librarian")


class LibrarianAgent(BaseAgent):
    """
    Librarian agent specialized in information retrieval and knowledge organization.
    
    This agent handles requests related to finding information, semantic search,
    and structured data retrieval using LLM-powered responses.
    """
    
    def __init__(self, llm_provider: str = None):
        """
        Initialize the Librarian agent.
        
        Args:
            llm_provider: Optional provider for the LLM (openai, anthropic, local)
        """
        super().__init__("Librarian")
        
        # Set up prompt loader
        self.prompt_loader = get_prompt_loader("librarian")
        
        # Set up LLM connector
        self.use_llm = True
        try:
            self.llm_connector = create_llm_connector(llm_provider)
            logger.info(f"Librarian agent initialized with {type(self.llm_connector).__name__}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM connector: {str(e)}. Using mock responses.")
            self.use_llm = False
    
    def process_request(self, user_input: str, conversation_history: List[Dict] = None, memory_context: Dict[str, Any] = None) -> str:
        """
        Process a user request from an information retrieval perspective.
        
        Uses an LLM with information-focused prompting to generate responses.
        Falls back to mock responses if LLM is not available.
        
        Args:
            user_input: The user's request text
            conversation_history: Optional conversation history for context
            memory_context: Optional memory context from the orchestrator memory
            
        Returns:
            The agent's response string
        
        Args:
            user_input: The user's request text
            conversation_history: Optional conversation history for context
            
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
                augmented_input = user_input
                if context_str:
                    augmented_input = f"Context from memory:\n{context_str}\n\nUser question: {user_input}"
                
                response = self.llm_connector.generate_text(
                    system_prompt=system_prompt,
                    user_input=augmented_input,
                    conversation_history=conversation_history
                )
                
                # Extract knowledge entities for storage in memory
                knowledge = self.extract_knowledge(response)
                
                return self.enhance_response_with_memory(response, memory_context)
            except Exception as e:
                logger.error(f"Error generating LLM response: {str(e)}. Falling back to mock response.")
                self.use_llm = False
        
        # Fall back to mock implementation if LLM fails or is unavailable
        mock_response = (
            f"Librarian Agent Response (Mock):\n\n"
            f"I've searched for information related to: '{user_input}'\n\n"
        )
        
        if context_str:
            mock_response += f"Based on existing knowledge in memory:\n{context_str}\n\n"
        
        mock_response += (
            f"As a Librarian agent, I would provide relevant facts, research findings, "
            f"and structured knowledge. This is a mock response as the LLM integration "
            f"is unavailable."
        )
        
        return mock_response
    
    def _prepare_memory_context(self, memory_context: Dict[str, Any]) -> str:
        """
        Format memory context for inclusion in prompts, with special emphasis
        on structured knowledge entities relevant to information retrieval.
        
        Args:
            memory_context: Memory context from the orchestrator
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # For Librarian agent, documents are highest priority
        if "relevant_documents" in memory_context and memory_context["relevant_documents"]:
            context_parts.append("Relevant stored information:")
            for i, doc in enumerate(memory_context["relevant_documents"][:5]):
                title = doc.get('title', 'Document')
                content = doc.get('content', 'No content')
                source = doc.get('source', 'Unknown source')
                context_parts.append(f"[{i+1}] {title}\n   Source: {source}\n   Content: {content}")
        
        # Add facts and structured entities
        if "relevant_entities" in memory_context and memory_context["relevant_entities"]:
            context_parts.append("\nRelevant entities and concepts:")
            for i, entity in enumerate(memory_context["relevant_entities"][:5]):
                name = entity.get('name', 'Entity')
                entity_type = entity.get('type', 'Unknown type')
                description = entity.get('description', 'No description')
                context_parts.append(f"[{i+1}] {name} ({entity_type})\n   {description}")
        
        return "\n".join(context_parts)
    
    def extract_knowledge(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Extract knowledge entities and factual information from response.
        
        As the Librarian agent specializes in information, this method identifies
        entities, facts, and concepts for structured storage in memory.
        
        Args:
            response: The agent's response
            
        Returns:
            Dictionary of extracted knowledge or None
        """
        # In a real implementation, this would use NLP or an LLM to extract named entities,
        # facts, and relationships from the response
        
        # Simple extraction based on knowledge indicators
        knowledge_indicators = ["fact", "research", "study", "according to", "data shows", 
                              "evidence suggests", "survey", "analysis", "statistics"]
        entity_indicators = ["person", "organization", "location", "concept", "technology", 
                           "method", "theory", "principle"]
        
        knowledge_facts = []
        entities = []
        
        # Basic fact extraction (simplified)        
        sentences = response.split(". ")
        for sentence in sentences[:5]:  # Limit to first 5 sentences
            for indicator in knowledge_indicators:
                if indicator in sentence.lower():
                    knowledge_facts.append(sentence.strip())
                    break
                    
        # Basic entity extraction (simplified)
        for indicator in entity_indicators:
            if indicator in response.lower():
                entities.append(indicator)
        
        if knowledge_facts or entities:
            return {
                "facts": knowledge_facts,
                "entities": entities,
                "source_response": response[:100] + "..."  # Truncated source
            }
        
        return None
    
    def enhance_response_with_memory(self, response: str, memory_context: Dict[str, Any]) -> str:
        """
        Enhance the Librarian's response with additional information from memory.
        
        Args:
            response: The original response
            memory_context: Memory context from the orchestrator
            
        Returns:
            The enhanced response with additional information from memory
        """
        # If there's limited memory context or the response is already comprehensive, return as is
        if not memory_context or len(response) > 500:
            return response
            
        # Check if there are relevant documents that might add value
        relevant_docs = memory_context.get("relevant_documents", [])
        if not relevant_docs:
            return response
            
        # Add supplementary information section
        supplement = "\n\n**Additional information from memory:**\n"
        for i, doc in enumerate(relevant_docs[:2]):  # Limit to top 2 most relevant
            title = doc.get('title', 'Related information')
            content_snippet = doc.get('content', '')[:100] + "..."
            supplement += f"\n{i+1}. {title}: {content_snippet}"
            
        return response + supplement
    
    def _select_prompt_template(self, user_input: str) -> str:
        """
        Select the appropriate prompt template based on the user input.
        
        Analyzes the user input to determine the most suitable librarian
        prompt template (research, fact checking, synthesis, etc.)
        
        Args:
            user_input: The user's request text
            
        Returns:
            The selected prompt template
        """
        # Simple keyword-based template selection
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ["research", "find", "information", "search"]):
            return self.prompt_loader.get_prompt("research_prompt", self.prompt_loader.get_system_prompt())
        
        elif any(word in input_lower for word in ["fact", "check", "verify", "true", "false"]):
            return self.prompt_loader.get_prompt("fact_checking_prompt", self.prompt_loader.get_system_prompt())
        
        elif any(word in input_lower for word in ["synthesize", "summarize", "combine", "integrate"]):
            return self.prompt_loader.get_prompt("information_synthesis_prompt", self.prompt_loader.get_system_prompt())
        
        elif any(word in input_lower for word in ["organize", "structure", "categorize", "classify"]):
            return self.prompt_loader.get_prompt("knowledge_organization_prompt", self.prompt_loader.get_system_prompt())
        
        # Default to system prompt if no specific template matches
        return self.prompt_loader.get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """
        Get the specialized system prompt for the Librarian agent.
        
        Returns:
            The system prompt string
        """
        return self.prompt_loader.get_system_prompt()


# Create a default instance for easy import
default_librarian = LibrarianAgent()
