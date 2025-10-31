"""
LangChain Integration Service

This module provides the core LangChain integration service for Mnemosyne,
supporting various LLM providers, models, and operations.
"""
import logging
from enum import Enum
from typing import Dict, Any, List, Optional, Union, Type, Callable, AsyncGenerator

import openai
from langchain_core.messages import ChatMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.callbacks import BaseCallbackHandler
from langchain_community.chat_models import ChatOpenAI, AzureChatOpenAI
from langchain_classic.chains import ConversationChain
from langchain_classic.memory import ConversationBufferMemory

from app.core.config import settings
from app.services.llm.config import LLMConfig, LLMProvider
from app.services.llm.callback_handlers import MnemosyneCallbackHandler


# Set up module logger
logger = logging.getLogger(__name__)


class ModelType(str, Enum):
    """Types of language models."""
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"


class LangChainService:
    """
    Service for interacting with language models via LangChain.
    
    This service provides a unified interface for various LLM operations
    while abstracting away the complexities of specific providers.
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize the LangChain service.
        
        Args:
            config: LLM configuration, if None uses default from settings
        """
        self.config = config or LLMConfig.from_settings()
        self._setup_provider()
        self.chat_model = self._create_chat_model()
        
    def _setup_provider(self) -> None:
        """Configure the LLM provider based on settings."""
        if self.config.provider == LLMProvider.OPENAI:
            # Set OpenAI API key and organization if available
            if settings.OPENAI_API_KEY:
                openai.api_key = settings.OPENAI_API_KEY
            if settings.OPENAI_ORG_ID:
                openai.organization = settings.OPENAI_ORG_ID
                
    def _create_chat_model(self) -> Any:
        """
        Create a ChatModel instance based on the configured provider.
        
        Returns:
            Chat model instance from LangChain
        """
        if self.config.provider == LLMProvider.OPENAI:
            return ChatOpenAI(
                **self.config.get_openai_config()
            )
        elif self.config.provider == LLMProvider.AZURE_OPENAI:
            # Would need additional Azure-specific configuration
            raise NotImplementedError("Azure OpenAI support not yet implemented")
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")
            
    def _convert_to_langchain_messages(
        self, messages: List[Dict[str, str]]
    ) -> List[ChatMessage]:
        """
        Convert application message format to LangChain message format.
        
        Args:
            messages: List of messages in application format
            
        Returns:
            List of LangChain formatted messages
        """
        lc_messages = []
        for msg in messages:
            role = msg.get("role", "").lower()
            content = msg.get("content", "")
            
            if role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
            elif role == "system":
                lc_messages.append(SystemMessage(content=content))
            else:
                # Default to human message for unknown roles
                logger.warning(f"Unknown message role: {role}, treating as user message")
                lc_messages.append(HumanMessage(content=content))
                
        return lc_messages
        
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = True,
        callbacks: Optional[List[BaseCallbackHandler]] = None,
        conversation_id: Optional[str] = None,
        **kwargs: Any
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Generate a completion from a chat model.
        
        Args:
            messages: List of messages in the conversation
            stream: Whether to stream the response
            callbacks: List of callback handlers
            conversation_id: ID of the conversation
            **kwargs: Additional model parameters
            
        Returns:
            Generated text or async generator for streaming responses
            
        Raises:
            ValueError: If messages are invalid
            RuntimeError: If LLM request fails
        """
        if not messages:
            raise ValueError("No messages provided for chat completion")
        
        # Create default callback handler if none provided
        if callbacks is None:
            callbacks = [
                MnemosyneCallbackHandler(
                    verbose=True,
                    conversation_id=conversation_id
                )
            ]
            
        # Convert to LangChain message format
        lc_messages = self._convert_to_langchain_messages(messages)
        
        # Update configuration with any provided kwargs
        config_dict = self.config.dict()
        if kwargs:
            config_dict.update(kwargs)
            
        # Set up runnable configuration
        run_config = RunnableConfig(callbacks=callbacks)
        
        try:
            # Handle streaming vs. non-streaming
            if stream:
                return self._stream_chat_completion(lc_messages, run_config)
            else:
                response = await self.chat_model.apredict_messages(
                    lc_messages,
                    callbacks=callbacks
                )
                return response.content
        except Exception as e:
            logger.error(f"Error in chat completion: {str(e)}")
            raise RuntimeError(f"Failed to generate chat completion: {str(e)}")
            
    async def _stream_chat_completion(
        self,
        messages: List[ChatMessage],
        run_config: RunnableConfig
    ) -> AsyncGenerator[str, None]:
        """
        Stream a chat completion response.
        
        Args:
            messages: LangChain formatted messages
            run_config: Configuration for the runnable
            
        Yields:
            Chunks of generated text
        """
        try:
            async for chunk in self.chat_model.astream_events(
                messages,
                config=run_config,
                version="v1"
            ):
                if chunk.get("event") == "on_chat_model_stream":
                    content = chunk.get("data", {}).get("chunk")
                    if content:
                        yield content
        except Exception as e:
            logger.error(f"Error streaming chat completion: {str(e)}")
            raise RuntimeError(f"Failed to stream chat completion: {str(e)}")
            
    async def create_conversation_chain(
        self,
        system_message: Optional[str] = None,
        memory: Optional[ConversationBufferMemory] = None,
        **kwargs: Any
    ) -> ConversationChain:
        """
        Create a conversation chain with memory.
        
        Args:
            system_message: System message to set context
            memory: Conversation memory component (optional)
            **kwargs: Additional parameters for the conversation chain
            
        Returns:
            Initialized conversation chain
        """
        if memory is None:
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            
        # Create chain with our chat model
        chain = ConversationChain(
            llm=self.chat_model,
            memory=memory,
            verbose=kwargs.get("verbose", False)
        )
        
        # Set system message if provided
        if system_message:
            if not hasattr(chain, "prompt") or not hasattr(chain.prompt, "messages"):
                logger.warning("Cannot set system message: unsupported chain format")
            else:
                # Update the system message in the prompt
                for i, message in enumerate(chain.prompt.messages):
                    if getattr(message, "type", "") == "system":
                        chain.prompt.messages[i].content = system_message
                        break
                else:
                    # No system message found, might need to add one based on the prompt format
                    logger.warning("No system message found in prompt to update")
                
        return chain
