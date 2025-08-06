"""
Priest Agent for the Shadow system.

This module implements the specialized Priest agent responsible for 
ethical reasoning and philosophical/religious perspectives.
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
from agents.priest.debate import DebateModule

# Configure logging
logger = logging.getLogger("shadow.agents.priest")


class PriestAgent(BaseAgent):
    """
    Priest agent specialized in ethical reasoning and philosophical perspectives.
    
    This agent handles requests related to ethics, philosophy, religion, and
    provides multi-perspective analysis on complex moral/ethical questions
    using LLM-powered responses.
    """
    
    def __init__(self, llm_provider: str = None):
        """
        Initialize the Priest agent.
        
        Args:
            llm_provider: Optional provider for the LLM (openai, anthropic, local)
        """
        super().__init__("Priest")
        
        # Set up prompt loader
        self.prompt_loader = get_prompt_loader("priest")
        
        # Set up LLM connector
        self.use_llm = True
        try:
            self.llm_connector = create_llm_connector(llm_provider)
            logger.info(f"Priest agent initialized with {type(self.llm_connector).__name__}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM connector: {str(e)}. Using mock responses.")
            self.use_llm = False
            
        # The debate module will be used to simulate multi-perspective debate
        self.debate_module = DebateModule(llm_connector=self.llm_connector if self.use_llm else None)
    
    def process_request(self, user_input: str, conversation_history: List[Dict] = None, memory_context: Dict[str, Any] = None) -> str:
        """
        Process a user request from an ethical/philosophical perspective.
        
        Uses an LLM with ethics-focused prompting to generate responses.
        May use debate architecture for multi-perspective analysis when appropriate.
        Falls back to mock responses if LLM is not available.
        
        Args:
            user_input: The user's request text
            conversation_history: Optional conversation history for context
            memory_context: Optional memory context from the orchestrator memory
            
        Returns:
            The agent's response string
        """
        # Check if the request might benefit from debate structure
        if self._should_use_debate(user_input) and self.use_llm:
            try:
                # For debates, prepare appropriate moral and philosophical context
                debate_context = self._prepare_debate_context(memory_context) if memory_context else None
                return self.debate_module.run_debate(user_input, conversation_history, debate_context)
            except Exception as e:
                logger.error(f"Error running debate module: {str(e)}. Falling back to standard response.")
                # Continue with standard processing if debate fails
        
        # Standard response with appropriate prompt template
        system_prompt = self._select_prompt_template(user_input)
        
        # Format memory context for inclusion in the prompt
        context_str = self._prepare_memory_context(memory_context) if memory_context else ""
        
        if self.use_llm:
            try:
                # Generate response using LLM with memory context
                enhanced_input = user_input
                if context_str:
                    enhanced_input = f"Ethical and philosophical context:\n{context_str}\n\nUser question: {user_input}"
                
                response = self.llm_connector.generate_text(
                    system_prompt=system_prompt,
                    user_input=enhanced_input,
                    conversation_history=conversation_history
                )
                
                # Extract philosophical insights and ethical principles if present
                extracted_knowledge = self.extract_knowledge(response)
                
                return response
            except Exception as e:
                logger.error(f"Error generating LLM response: {str(e)}. Falling back to mock response.")
                self.use_llm = False
        
        # Fall back to mock implementation if LLM fails or is unavailable
        mock_response = (
            f"Priest Agent Response (Mock):\n\n"
            f"I've analyzed your request: '{user_input}' from an ethical/philosophical perspective.\n\n"
        )
        
        if context_str:
            mock_response += f"Based on relevant ethical and philosophical perspectives in memory:\n{context_str}\n\n"
            
        mock_response += (
            f"As a Priest agent, I would provide ethical analysis, philosophical perspectives, "
            f"and multiple worldview considerations. "
            f"This is a mock response as the LLM integration is unavailable."
        )
        
        return mock_response
    
    def _prepare_memory_context(self, memory_context: Dict[str, Any]) -> str:
        """
        Format memory context specifically for ethical and philosophical queries.
        
        Args:
            memory_context: Memory context from the orchestrator
            
        Returns:
            Formatted context string focused on moral and philosophical dimensions
        """
        context_parts = []
        
        # Add relevant ethical principles from entities if available
        if "relevant_entities" in memory_context and memory_context["relevant_entities"]:
            ethics_entities = [e for e in memory_context["relevant_entities"] 
                             if e.get('type', '') in ["ethical_principle", "philosophy", "moral_value", "worldview", "religion"]]
            
            if ethics_entities:
                context_parts.append("Relevant ethical and philosophical principles:")
                for i, entity in enumerate(ethics_entities[:5]):
                    context_parts.append(f"[{i+1}] {entity.get('name', 'Principle')}: {entity.get('description', 'No description')}")
        
        # Add relevant documents that might contain ethical or philosophical content
        if "relevant_documents" in memory_context and memory_context["relevant_documents"]:
            # Filter for philosophical/ethical content using basic keyword detection
            ethics_keywords = ["ethic", "moral", "philosophy", "value", "right", "wrong", 
                             "good", "bad", "virtue", "justice", "fairness", "religion"]
            
            ethics_docs = []
            for doc in memory_context["relevant_documents"]:
                if any(keyword in doc.get('content', '').lower() for keyword in ethics_keywords):
                    ethics_docs.append(doc)
            
            if ethics_docs:
                context_parts.append("\nRelevant ethical/philosophical perspectives from memory:")
                for i, doc in enumerate(ethics_docs[:3]):
                    context_parts.append(f"[{i+1}] {doc.get('title', 'Document')}: {doc.get('content', 'No content')[:150]}...")
        
        # Add past ethical judgments if available in conversation context
        if "past_ethical_judgments" in memory_context:
            context_parts.append("\nPrevious ethical judgments on similar topics:")
            for i, judgment in enumerate(memory_context["past_ethical_judgments"][:3]):
                context_parts.append(f"[{i+1}] {judgment}")
                
        return "\n".join(context_parts)
    
    def _prepare_debate_context(self, memory_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare context specifically for debate-style responses.
        
        Args:
            memory_context: Memory context from the orchestrator
            
        Returns:
            Dictionary with organized philosophical positions from memory
        """
        if not memory_context:
            return {}
            
        debate_context = {}
        
        # Extract perspectives that might be useful in a debate
        perspectives = {}
        if "relevant_entities" in memory_context:
            for entity in memory_context["relevant_entities"]:
                entity_type = entity.get('type', '')
                if entity_type in ["ethical_principle", "philosophy", "religion", "worldview"]:
                    perspective_name = entity.get('name', 'Unknown perspective')
                    perspectives[perspective_name] = entity.get('description', 'No description')
        
        # Find historical arguments on similar topics
        historical_arguments = []
        if "relevant_documents" in memory_context:
            # Simple extraction of arguments from documents (would be more sophisticated in real system)
            for doc in memory_context["relevant_documents"]:
                if "argument" in doc.get('content', '').lower():
                    historical_arguments.append({
                        "source": doc.get('title', 'Unknown source'),
                        "argument": doc.get('content', '')[:200]  # Truncate for simplicity
                    })
                    
        debate_context["perspectives"] = perspectives
        debate_context["historical_arguments"] = historical_arguments
        
        return debate_context
    
    def extract_knowledge(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Extract philosophical and ethical principles from the response.
        
        Args:
            response: The agent's response
            
        Returns:
            Dictionary of extracted ethical/philosophical concepts or None
        """
        # In a real implementation, this could use NLP or an LLM to extract
        # ethical principles, philosophical perspectives, and moral values
        
        # Simple keyword detection to identify ethical/philosophical content
        ethics_terms = ["ethic", "moral", "value", "virtue", "principle",
                       "philosophy", "worldview", "religion", "belief"]
                       
        philosophy_schools = ["utilitarianism", "deontology", "virtue ethics", "existentialism",
                            "pragmatism", "idealism", "materialism", "humanism"]
                            
        religions = ["christianity", "islam", "judaism", "buddhism", "hinduism",
                   "taoism", "secular", "atheism", "agnosticism"]
        
        # Detect principles in the response
        found_principles = {}
        sentences = response.split(". ")
        principles_detected = []
        
        for sentence in sentences:
            lower_sentence = sentence.lower()
            
            # Check for ethical terms
            for term in ethics_terms:
                if term in lower_sentence:
                    principles_detected.append(sentence)
                    break
                    
            # Check for philosophical schools
            for school in philosophy_schools:
                if school in lower_sentence:
                    found_principles[school] = True
                    
            # Check for religious perspectives
            for religion in religions:
                if religion in lower_sentence:
                    found_principles[religion] = True
        
        if found_principles or principles_detected:
            return {
                "type": "ethical_philosophical_content",
                "principles": list(found_principles.keys()),
                "principle_statements": principles_detected[:3],  # Limit to first 3 detected statements
                "response_summary": response[:100] + "..."  # Truncated for simplicity
            }
            
        return None
        
    def _should_use_debate(self, user_input: str) -> bool:
        """
        Determine if the request should use debate architecture.
        
        Args:
            user_input: The user's request text
            
        Returns:
            True if debate should be used, False otherwise
        """
        # Simple keyword detection for topics that benefit from debate
        keywords = [
            "ethics", "moral", "right or wrong", "perspective", "worldview", 
            "religion", "philosophy", "should we", "ethical dilemma", "values",
            "different views", "debate", "controversial", "disagreement"
        ]
        
        return any(keyword in user_input.lower() for keyword in keywords)
    
    def _select_prompt_template(self, user_input: str) -> str:
        """
        Select the appropriate prompt template based on the user input.
        
        Analyzes the user input to determine the most suitable priest
        prompt template (ethical analysis, philosophical inquiry, etc.)
        
        Args:
            user_input: The user's request text
            
        Returns:
            The selected prompt template
        """
        # Simple keyword-based template selection
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ["ethical", "ethics", "moral", "right", "wrong", "should"]):
            return self.prompt_loader.get_prompt("ethical_analysis_prompt", self.prompt_loader.get_system_prompt())
        
        elif any(word in input_lower for word in ["philosophy", "philosophical", "meaning", "existence", "metaphysical"]):
            return self.prompt_loader.get_prompt("philosophical_inquiry_prompt", self.prompt_loader.get_system_prompt())
        
        elif any(word in input_lower for word in ["worldview", "perspective", "debate", "different views", "opinions"]):
            return self.prompt_loader.get_prompt("worldview_debate_prompt", self.prompt_loader.get_system_prompt())
        
        elif any(word in input_lower for word in ["values", "clarify", "priorities", "important", "care about"]):
            return self.prompt_loader.get_prompt("values_clarification_prompt", self.prompt_loader.get_system_prompt())
        
        # Default to system prompt if no specific template matches
        return self.prompt_loader.get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """
        Get the specialized system prompt for the Priest agent.
        
        Returns:
            The system prompt string
        """
        return self.prompt_loader.get_system_prompt()

    def generate_debate(self, issue: str) -> Dict:
        """
        Generate a multi-perspective debate on an ethical issue.
        
        This is a placeholder for a more sophisticated implementation that would
        use an LLM to simulate a debate between different philosophical positions.
        
        Args:
            issue: The ethical/philosophical issue to debate
            
        Returns:
            Dictionary of perspective names to their arguments
        """
        # Mock implementation
        perspectives = {
            "utilitarian": "From a utilitarian perspective, we should consider the greatest good for the greatest number.",
            "deontological": "From a deontological perspective, we must consider our duties and universal principles.",
            "virtue_ethics": "From a virtue ethics perspective, we should consider what actions reflect good character traits."
        }
        
        return perspectives


# Create a default instance for easy import
default_priest = PriestAgent()


# Additional debate architecture module placeholder
class DebateModule:
    """
    Framework for simulating philosophical debates between multiple perspectives.
    
    This is a placeholder for a more sophisticated debate architecture that
    would be implemented in the full system.
    """
    
    def __init__(self, llm_connector=None):
        """Initialize the debate module with optional LLM connector."""
        self.llm_connector = llm_connector
        self.perspectives = [
            "utilitarian", "deontological", "virtue_ethics", 
            "pragmatic", "existentialist", "religious", "secular"
        ]
    
    def run_debate(self, user_input: str, conversation_history: List[Dict] = None, debate_context: Dict[str, Any] = None) -> str:
        """
        Run a multi-perspective debate on the given ethical issue.
        
        Args:
            user_input: The user's ethical/philosophical question
            conversation_history: Optional conversation history for context
            debate_context: Optional context from memory for debate enhancement
            
        Returns:
            A debate-formatted response as a string
        """
        debate_results = self.generate_debate(user_input)
        
        # Enhance debate with memory context if available
        if debate_context and "perspectives" in debate_context and debate_context["perspectives"]:
            # Add perspectives from memory to the debate
            for perspective, description in debate_context["perspectives"].items():
                if perspective not in debate_results and len(debate_results) < 6:
                    debate_results[perspective] = f"From memory: {description[:100]}..."
        
        # Format the debate results into a response
        formatted_debate = []
        formatted_debate.append(f"### Multi-perspective Analysis on: '{user_input}'\n")
        
        for i, (perspective, argument) in enumerate(debate_results.items()):
            formatted_debate.append(f"**{perspective.title()} Perspective ({i+1}/{len(debate_results)}):**")
            formatted_debate.append(f"{argument}\n")
        
        if debate_context and "historical_arguments" in debate_context and debate_context["historical_arguments"]:
            formatted_debate.append("\n### Related Historical Arguments:")
            for i, arg in enumerate(debate_context["historical_arguments"][:2]):
                formatted_debate.append(f"**Source: {arg['source']}**")
                formatted_debate.append(f"{arg['argument']}...\n")
        
        formatted_debate.append("\n### Synthesis and Conclusion:\n")
        formatted_debate.append("The above perspectives represent different ethical frameworks " 
                             "and worldviews on this complex issue. Each has strengths and limitations, " 
                             "and a comprehensive ethical analysis considers multiple viewpoints before " 
                             "reaching a balanced conclusion.")
        
        return "\n".join(formatted_debate)
        
    def generate_debate(self, issue: str) -> Dict[str, Any]:
        """
        Generate a multi-perspective debate on an ethical issue.
        
        Args:
            issue: The ethical/philosophical issue to debate
            
        Returns:
            Dictionary containing the debate structure
        """
        # Simple placeholder implementation - would be much more sophisticated with LLM
        debate = {}
        
        # Generate a simple argument for each perspective
        for perspective in self.perspectives[:4]:  # Limit to 4 for simplicity
            debate[perspective] = f"This is how the issue would be analyzed from a {perspective} viewpoint. "\
                                  f"A more sophisticated implementation would use LLM-generated content "\
                                  f"to simulate different ethical frameworks applied to '{issue}'."
        
        return debate
