"""
Streaming LLM Connector module for the Shadow system.

This module extends the base LLM connector with streaming capabilities
for real-time response generation.
"""

import os
import logging
import asyncio
from typing import Dict, List, Optional, Union, Any, AsyncGenerator, Callable

from utils.llm_connector import BaseLLMConnector, OpenAIConnector

# Configure logging
logger = logging.getLogger("shadow.llm.streaming")


class StreamingLLMConnector:
    """
    Base class for streaming LLM connectors.
    
    This class adds streaming capabilities to the base LLM connector.
    """
    
    def __init__(self, base_connector: BaseLLMConnector):
        """
        Initialize the streaming connector with a base connector.
        
        Args:
            base_connector: The base LLM connector to use
        """
        self.base_connector = base_connector
    
    async def generate_text_stream(
        self, 
        system_prompt: str, 
        user_input: str,
        conversation_history: Optional[List[Dict]] = None,
        callback: Optional[Callable[[str], None]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate text using the LLM with streaming.
        
        Args:
            system_prompt: System instructions for the LLM
            user_input: User's input/question
            conversation_history: Optional conversation history
            callback: Optional callback function to call with each chunk
            
        Yields:
            Generated text chunks as they become available
        """
        # Default implementation falls back to non-streaming
        # Subclasses should override this method
        response = self.base_connector.generate_text(
            system_prompt, user_input, conversation_history
        )
        
        # Simulate streaming with the full response
        if callback:
            callback(response)
        
        yield response


class StreamingOpenAIConnector(StreamingLLMConnector):
    """
    Streaming connector for OpenAI and OpenAI-compatible models.
    """
    
    def __init__(self, base_connector: Optional[OpenAIConnector] = None, **kwargs):
        """
        Initialize the streaming OpenAI connector.
        
        Args:
            base_connector: Optional base OpenAI connector
            **kwargs: Additional arguments to pass to OpenAIConnector if base_connector is None
        """
        if base_connector is None:
            base_connector = OpenAIConnector(**kwargs)
        
        super().__init__(base_connector)
        
        # Ensure we're working with an OpenAI connector
        if not isinstance(base_connector, OpenAIConnector):
            raise TypeError("base_connector must be an OpenAIConnector")
    
    async def generate_text_stream(
        self, 
        system_prompt: str, 
        user_input: str,
        conversation_history: Optional[List[Dict]] = None,
        callback: Optional[Callable[[str], None]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate text using OpenAI API with streaming.
        
        Args:
            system_prompt: System instructions for the LLM
            user_input: User's input/question
            conversation_history: Optional conversation history
            callback: Optional callback function to call with each chunk
            
        Yields:
            Generated text chunks as they become available
        """
        try:
            import openai
            
            connector = self.base_connector
            
            if not connector.validate_api_key():
                error_msg = "Error: API key not configured or invalid"
                if callback:
                    callback(error_msg)
                yield error_msg
                return
            
            # Configure OpenAI client for custom endpoints
            client = openai.AsyncOpenAI(
                api_key=connector.api_key,
                base_url=connector.base_url
            )
            
            # Prepare messages - same logic as in OpenAIConnector
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history if available
            if conversation_history:
                history = connector.format_history(conversation_history)
                filtered_history = connector._filter_conversation_history(history)
                
                if filtered_history:
                    messages.extend(filtered_history)
                    
                    if filtered_history[-1].get("role") == "user":
                        messages[-1] = {"role": "user", "content": user_input}
                    else:
                        messages.append({"role": "user", "content": user_input})
                else:
                    messages.append({"role": "user", "content": user_input})
            else:
                messages.append({"role": "user", "content": user_input})
            
            # Log the API call
            logger.info(f"Making streaming API call with:")
            logger.info(f"  Model: {connector.model}")
            logger.info(f"  Temperature: {connector.temperature}")
            logger.info(f"  Max tokens: {connector.max_tokens}")
            
            # Create a streaming completion
            stream = await client.chat.completions.create(
                model=connector.model,
                messages=messages,
                temperature=connector.temperature,
                max_tokens=connector.max_tokens,
                stream=True
            )
            
            # Process the streaming response
            full_response = ""
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    
                    # Call the callback if provided
                    if callback:
                        callback(content)
                    
                    yield content
            
            # Return the full response as the last chunk
            if not full_response:
                logger.warning("No content received from streaming API")
                empty_msg = ""
                if callback:
                    callback(empty_msg)
                yield empty_msg
            
        except ImportError:
            error_msg = "Error: OpenAI package not installed. Run 'pip install openai'"
            if callback:
                callback(error_msg)
            yield error_msg
            
        except Exception as e:
            logger.error(f"OpenAI streaming API error: {str(e)}")
            error_msg = f"Error generating streaming response: {str(e)}"
            if callback:
                callback(error_msg)
            yield error_msg


# Factory function to create a streaming connector from a base connector
def create_streaming_connector(base_connector: BaseLLMConnector) -> StreamingLLMConnector:
    """
    Create a streaming connector from a base connector.
    
    Args:
        base_connector: The base connector to wrap
        
    Returns:
        A streaming connector that wraps the base connector
    """
    if isinstance(base_connector, OpenAIConnector):
        return StreamingOpenAIConnector(base_connector)
    else:
        # Default to base streaming connector for other types
        return StreamingLLMConnector(base_connector)
