"""
LLM Connector module for the Shadow system.

This module provides interfaces for connecting to various LLM providers
such as OpenAI, Anthropic Claude, and local models.
"""

import os
import logging
import yaml
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    logging.getLogger("shadow.llm").info("Loaded environment variables from .env file")
except ImportError:
    logging.getLogger("shadow.llm").warning("python-dotenv not installed. Install with: pip install python-dotenv")
except Exception as e:
    logging.getLogger("shadow.llm").warning(f"Could not load .env file: {e}")

# Configure logging
logger = logging.getLogger("shadow.llm")


def load_config():
    """
    Load LLM configuration from config.yaml.
    
    Returns:
        Dictionary containing LLM configuration
    """
    config_path = Path(__file__).parent / "config.yaml"
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            return config.get("llm", {})
    except Exception as e:
        logger.error(f"Error loading LLM config: {e}")
        return {}


class BaseLLMConnector(ABC):
    """
    Abstract base class for LLM connectors.
    
    All LLM connectors (OpenAI, Claude, Local) should inherit from
    this class and implement its abstract methods.
    """
    
    def __init__(self, model: str, temperature: float = 0.7, max_tokens: int = 1024):
        """
        Initialize the LLM connector.
        
        Args:
            model: Name of the model to use
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = None
    
    @abstractmethod
    def generate_text(self, system_prompt: str, user_input: str, 
                    conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Generate text using the LLM.
        
        Args:
            system_prompt: System instructions for the LLM
            user_input: User's input/question
            conversation_history: Optional conversation history
            
        Returns:
            Generated text response
        """
        pass
    
    def validate_api_key(self) -> bool:
        """
        Validate that the API key is available.
        
        Returns:
            True if API key is valid, False otherwise
        """
        return self.api_key is not None and len(self.api_key) > 0
    
    @staticmethod
    def format_history(conversation_history: List[Dict]) -> List[Dict]:
        """
        Format conversation history for LLM consumption.
        
        Args:
            conversation_history: List of conversation entries
            
        Returns:
            Formatted conversation history
        """
        if not conversation_history:
            return []
            
        formatted = []
        for entry in conversation_history:
            if entry.get("role") in ["user", "assistant", "system"]:
                formatted.append({
                    "role": entry["role"],
                    "content": entry["content"]
                })
        
        return formatted
    
    @staticmethod
    def _filter_conversation_history(conversation_history: List[Dict]) -> List[Dict]:
        """
        Filter out test messages and unwanted content from conversation history.
        
        Args:
            conversation_history: List of conversation entries
            
        Returns:
            Filtered conversation history
        """
        # Patterns to filter out (case-insensitive)
        filter_patterns = [
            "test message",
            "verify context inclusion",
            "hello, this is a test",
            "testing",
            "error generating response",
            "test the system",
            "hello world",
            "debug",
            "check if",
            "verify that"
        ]
        
        filtered_history = []
        for entry in conversation_history:
            if entry.get("role") in ["user", "assistant"]:
                content = entry.get("content", "").lower()
                # Skip if content contains any filter patterns
                should_filter = any(pattern in content for pattern in filter_patterns)
                if not should_filter:
                    filtered_history.append(entry)
        
        return filtered_history


class OpenAIConnector(BaseLLMConnector):
    """
    Connector for OpenAI and OpenAI-compatible models.
    Supports configurable base URL, API key, model name, and parameters.
    """
    
    def __init__(self, 
                 model: str = None, 
                 temperature: float = None, 
                 max_tokens: int = None,
                 base_url: str = None,
                 api_key: str = None):
        """
        Initialize the OpenAI connector with configurable parameters.
        
        Args:
            model: Model name (defaults to LLM_MODEL_NAME env var or "gpt-4o")
            temperature: Temperature setting (defaults to LLM_TEMPERATURE env var or 0.7)
            max_tokens: Max tokens (defaults to LLM_MAX_TOKENS env var or 2048)
            base_url: Base URL for API (defaults to LLM_BASE_URL env var or OpenAI default)
            api_key: API key (defaults to LLM_API_KEY env var or OPENAI_API_KEY)
        """
        # Load configuration from environment variables with fallbacks
        self.model = model or os.environ.get("LLM_MODEL_NAME") or os.environ.get("OPENAI_MODEL") or "gpt-4o"
        self.temperature = temperature if temperature is not None else float(os.environ.get("LLM_TEMPERATURE", "0.7"))
        self.max_tokens = max_tokens if max_tokens is not None else int(os.environ.get("LLM_MAX_TOKENS", "2048"))
        self.base_url = base_url or os.environ.get("LLM_BASE_URL") or "https://api.openai.com/v1"
        
        # Initialize parent class first
        super().__init__(self.model, self.temperature, self.max_tokens)
        
        # Set API key after parent class init to prevent it being overwritten
        # API Key priority: parameter > LLM_API_KEY > OPENAI_API_KEY
        self.api_key = api_key or os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
        
        # Log configuration (without exposing API key)
        logger.info(f"OpenAI connector initialized:")
        logger.info(f"  Base URL: {self.base_url}")
        logger.info(f"  Model: {self.model}")
        logger.info(f"  Temperature: {self.temperature}")
        logger.info(f"  Max Tokens: {self.max_tokens}")
        logger.info(f"  API Key: {'*' * 8 + self.api_key[-4:] if self.api_key else 'Not set'}")
        
        if not self.validate_api_key():
            logger.warning("API key not found or invalid")
    
    def validate_api_key(self) -> bool:
        """Validate that the API key is set and not a placeholder."""
        return (self.api_key and 
                self.api_key != "your-openai-api-key-here" and 
                len(self.api_key.strip()) > 10)
    
    def generate_text(self, system_prompt: str, user_input: str, 
                     conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Generate text using OpenAI-compatible API endpoints.
        
        Args:
            system_prompt: System instructions for the LLM
            user_input: User's input/question
            conversation_history: Optional conversation history
            
        Returns:
            Generated text response
        """
        try:
            import openai
            
            if not self.validate_api_key():
                return "Error: API key not configured or invalid"
            
            # Configure OpenAI client for custom endpoints
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            # Prepare messages - InnoScale API requires strict user/assistant alternation
            # Always start with system prompt for agent worldview
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history if available, ensuring proper alternation and filtering
            if conversation_history:
                history = self.format_history(conversation_history)
                
                # Filter out test messages and unwanted content
                filtered_history = self._filter_conversation_history(history)
                
                # Include filtered conversation history
                if filtered_history:
                    messages.extend(filtered_history)
                    
                    # Check if the last message in history is a user message
                    # If so, we need to be careful about adding the current user input
                    if filtered_history[-1].get("role") == "user":
                        # Replace the last user message with the current input to avoid duplication
                        messages[-1] = {"role": "user", "content": user_input}
                    else:
                        # Safe to add current user message since last was assistant
                        messages.append({"role": "user", "content": user_input})
                else:
                    # Empty filtered history, add current user message
                    messages.append({"role": "user", "content": user_input})
            else:
                # For new conversations, add user message
                messages.append({"role": "user", "content": user_input})
            
            # Call the API with configurable parameters
            logger.info(f"Making API call with:")
            logger.info(f"  Model: {self.model}")
            logger.info(f"  Messages: {messages}")
            logger.info(f"  Temperature: {self.temperature}")
            logger.info(f"  Max tokens: {self.max_tokens}")
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract and return the generated text
            return response.choices[0].message.content
            
        except ImportError:
            return "Error: OpenAI package not installed. Run 'pip install openai'"
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return f"Error generating response: {str(e)}"


class AnthropicConnector(BaseLLMConnector):
    """
    Connector for Anthropic Claude models.
    """
    
    def __init__(self, model: str = "claude-3-5-sonnet", temperature: float = 0.7, max_tokens: int = 1024):
        """Initialize the Anthropic connector."""
        super().__init__(model, temperature, max_tokens)
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        
        if not self.validate_api_key():
            logger.warning("Anthropic API key not found in environment variables")
    
    def generate_text(self, system_prompt: str, user_input: str, 
                     conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Generate text using Anthropic Claude models.
        
        Args:
            system_prompt: System instructions for the LLM
            user_input: User's input/question
            conversation_history: Optional conversation history
            
        Returns:
            Generated text response
        """
        try:
            import anthropic
            
            if not self.validate_api_key():
                return "Error: Anthropic API key not configured"
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            # Prepare messages - InnoScale API requires strict user/assistant alternation
            # Always start with system prompt for agent worldview
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history if available, ensuring proper alternation and filtering
            if conversation_history:
                history = self.format_history(conversation_history)
                
                # Filter out test messages and unwanted content
                filtered_history = self._filter_conversation_history(history)
                
                # Include filtered conversation history
                if filtered_history:
                    messages.extend(filtered_history)
                    
                    # Check if the last message in history is a user message
                    # If so, we need to be careful about adding the current user input
                    if filtered_history[-1].get("role") == "user":
                        # Replace the last user message with the current input to avoid duplication
                        messages[-1] = {"role": "user", "content": user_input}
                    else:
                        # Safe to add current user message since last was assistant
                        messages.append({"role": "user", "content": user_input})
                else:
                    # Empty filtered history, add current user message
                    messages.append({"role": "user", "content": user_input})
            else:
                # For new conversations, add user message
                messages.append({"role": "user", "content": user_input})
            
            # Call the API
            response = client.messages.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract and return the generated text
            return response.content[0].text
            
        except ImportError:
            return "Error: Anthropic package not installed. Run 'pip install anthropic'"
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            return f"Error generating response: {str(e)}"


class LocalModelConnector(BaseLLMConnector):
    """
    Connector for local models (via vLLM or similar).
    """
    
    def __init__(self, model: str = "gemma-7b-it", temperature: float = 0.7, max_tokens: int = 768):
        """Initialize the local model connector."""
        super().__init__(model, temperature, max_tokens)
        self.model_path = os.environ.get("LOCAL_MODEL_PATH", "./models")
    
    def generate_text(self, system_prompt: str, user_input: str, 
                     conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Generate text using a local model.
        
        This is a placeholder implementation. In a real deployment, you would
        implement this using vLLM, LlamaCPP, or similar libraries.
        
        Args:
            system_prompt: System instructions for the LLM
            user_input: User's input/question
            conversation_history: Optional conversation history
            
        Returns:
            Generated text response
        """
        try:
            # Placeholder for actual local model implementation
            # In a real system, you would load and run inference with a local model
            
            logger.warning("LocalModelConnector not fully implemented")
            
            # Mock response for development testing
            return (
                "This is a placeholder response from the local model connector. "
                "In a real deployment, this would be generated by a local LLM."
            )
            
        except Exception as e:
            logger.error(f"Local model error: {str(e)}")
            return f"Error generating response: {str(e)}"


class MockLLMConnector(BaseLLMConnector):
    """
    Mock LLM connector for testing purposes.
    
    This connector provides realistic-looking responses without making
    actual API calls, useful for testing and development.
    """
    
    def __init__(self, model: str = "mock-model", temperature: float = 0.7, max_tokens: int = 1024):
        """Initialize the mock connector."""
        super().__init__(model, temperature, max_tokens)
    
    def validate_api_key(self) -> bool:
        """Mock validation always returns True."""
        return True
    
    def generate_text(self, system_prompt: str, user_input: str, 
                     conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Generate mock text responses based on the input and system prompt.
        
        Args:
            system_prompt: System instructions for the LLM
            user_input: User's input/question
            conversation_history: Optional conversation history
            
        Returns:
            Mock generated text response
        """
        # Extract key context from system prompt to determine agent type
        prompt_lower = system_prompt.lower()
        user_lower = user_input.lower()
        
        # Determine response type based on system prompt
        if "engineer" in prompt_lower or "technical" in prompt_lower:
            return self._generate_engineering_response(user_input)
        elif "librarian" in prompt_lower or "research" in prompt_lower:
            return self._generate_research_response(user_input)
        elif "priest" in prompt_lower or "ethical" in prompt_lower:
            return self._generate_ethical_response(user_input)
        else:
            return self._generate_general_response(user_input)
    
    def _generate_engineering_response(self, user_input: str) -> str:
        """Generate a mock engineering response."""
        responses = [
            f"From a technical perspective, '{user_input}' requires careful consideration of system architecture, scalability, and performance optimization. I recommend implementing a modular design with clear separation of concerns, robust error handling, and comprehensive monitoring.",
            f"For the technical implementation of '{user_input}', we should focus on: 1) System design patterns that ensure maintainability, 2) Performance benchmarking and optimization, 3) Security considerations and best practices, 4) Automated testing and continuous integration.",
            f"The engineering approach to '{user_input}' involves analyzing requirements, designing scalable solutions, and implementing with industry best practices. Key considerations include database design, API architecture, and deployment strategies."
        ]
        
        # Simple hash-based selection for consistency
        index = abs(hash(user_input)) % len(responses)
        return responses[index]
    
    def _generate_research_response(self, user_input: str) -> str:
        """Generate a mock research/librarian response."""
        responses = [
            f"Based on my research regarding '{user_input}', I've found several relevant sources and best practices. Current industry trends show increasing adoption of cloud-native technologies, with emphasis on containerization and microservices architectures.",
            f"My investigation into '{user_input}' reveals important research findings: Recent studies indicate the importance of data-driven decision making, with emerging technologies like machine learning and AI playing crucial roles in modern implementations.",
            f"Research on '{user_input}' shows that successful implementations typically follow established patterns: thorough requirements analysis, iterative development approaches, and continuous user feedback integration."
        ]
        
        index = abs(hash(user_input)) % len(responses)
        return responses[index]
    
    def _generate_ethical_response(self, user_input: str) -> str:
        """Generate a mock ethical/philosophical response."""
        responses = [
            f"From an ethical standpoint, '{user_input}' raises important questions about responsibility, fairness, and potential societal impact. We must consider: Who benefits? Who might be harmed? How do we ensure transparency and accountability?",
            f"The philosophical implications of '{user_input}' deserve careful consideration. Key ethical principles to evaluate include autonomy, beneficence, non-maleficence, and justice. We should also consider long-term consequences and unintended effects.",
            f"Examining '{user_input}' through an ethical lens, we must balance innovation with responsibility. Important considerations include privacy rights, equitable access, potential for misuse, and alignment with human values and dignity."
        ]
        
        index = abs(hash(user_input)) % len(responses)
        return responses[index]
    
    def _generate_general_response(self, user_input: str) -> str:
        """Generate a general mock response."""
        return f"This is a mock response to your query: '{user_input}'. In a real implementation, this would be generated by an AI model based on the system prompt and conversation context."


def create_llm_connector(provider: str = None) -> BaseLLMConnector:
    """
    Factory function to create the appropriate LLM connector.
    
    Args:
        provider: The LLM provider to use (openai, anthropic, local)
        
    Returns:
        An instance of the appropriate LLM connector
    """
    # Load config
    config = load_config()
    
    # Use default provider from config if none specified
    if provider is None:
        provider = config.get("default_provider", "openai")
    
    # Get provider-specific config
    providers_config = config.get("providers", {})
    provider_config = providers_config.get(provider, {})
    
    # Create connector based on provider
    if provider == "openai":
        # Prioritize environment variables over config file for Docker compatibility
        model = os.environ.get("LLM_MODEL_NAME") or provider_config.get("model", "gpt-4o")
        temperature = float(os.environ.get("LLM_TEMPERATURE", provider_config.get("temperature", 0.7)))
        max_tokens = int(os.environ.get("LLM_MAX_TOKENS", provider_config.get("max_tokens", 1024)))
        base_url = os.environ.get("LLM_BASE_URL") or provider_config.get("base_url", "https://api.openai.com/v1")
        api_key = os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY") or provider_config.get("api_key")
        return OpenAIConnector(model, temperature, max_tokens, base_url, api_key)
    
    elif provider == "anthropic":
        model = provider_config.get("model", "claude-3-5-sonnet")
        temperature = provider_config.get("temperature", 0.7)
        max_tokens = provider_config.get("max_tokens", 1024)
        return AnthropicConnector(model, temperature, max_tokens)
    
    elif provider == "local":
        model = provider_config.get("model", "gemma-7b-it")
        temperature = provider_config.get("temperature", 0.8)
        max_tokens = provider_config.get("max_tokens", 768)
        return LocalModelConnector(model, temperature, max_tokens)
    
    elif provider == "mock":
        model = provider_config.get("model", "mock-model")
        temperature = provider_config.get("temperature", 0.7)
        max_tokens = provider_config.get("max_tokens", 1024)
        return MockLLMConnector(model, temperature, max_tokens)
    
    else:
        logger.warning(f"Unknown provider '{provider}', falling back to OpenAI")
        return OpenAIConnector()

# Default instances for easy import
default_openai_connector = OpenAIConnector()
default_anthropic_connector = AnthropicConnector()
default_local_connector = LocalModelConnector()
default_mock_connector = MockLLMConnector()
