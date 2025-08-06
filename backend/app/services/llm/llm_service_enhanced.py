"""
Enhanced LLM Service with Memory Integration

This module provides an enhanced LLM service that integrates memory retrieval
and supports multiple LLM providers including OpenAI-compatible endpoints.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Union, AsyncGenerator
from datetime import datetime
from uuid import UUID
import tiktoken

from langchain.chat_models import ChatOpenAI
from langchain.schema import ChatMessage, HumanMessage, AIMessage, SystemMessage
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.memory.memory_service_enhanced import MemoryService
from app.services.llm.openai_client import OpenAIClient
from app.core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class EnhancedLLMConfig:
    """Configuration for enhanced LLM service."""
    
    def __init__(
        self,
        provider: str = "openai",
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        streaming: bool = True,
        memory_enabled: bool = True,
        memory_search_limit: int = 5,
        memory_threshold: float = 0.7,
        context_window: int = 8192,  # Default for GPT-4
    ):
        self.provider = provider
        self.model_name = model_name or settings.OPENAI_MODEL
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.base_url = base_url or settings.OPENAI_BASE_URL
        self.temperature = temperature
        self.max_tokens = max_tokens or settings.OPENAI_MAX_TOKENS
        self.streaming = streaming
        self.memory_enabled = memory_enabled
        self.memory_search_limit = memory_search_limit
        self.memory_threshold = memory_threshold
        self.context_window = context_window
        
    def get_provider_config(self) -> Dict[str, Any]:
        """Get provider-specific configuration."""
        config = {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "streaming": self.streaming,
        }
        
        if self.provider in ["openai", "vllm", "ollama", "litellm"]:
            # All OpenAI-compatible providers
            config["openai_api_key"] = self.api_key or "dummy-key"
            if self.base_url:
                config["openai_api_base"] = self.base_url
                
        return config


class TokenCounter:
    """Utility for counting tokens in messages."""
    
    def __init__(self, model_name: str = "gpt-4"):
        """Initialize token counter with model-specific encoding."""
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # Fallback to cl100k_base encoding (GPT-4/3.5-turbo)
            self.encoding = tiktoken.get_encoding("cl100k_base")
            
    def count_messages(self, messages: List[Dict[str, str]]) -> int:
        """Count tokens in a list of messages."""
        # Simplified token counting (OpenAI's formula)
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # Every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(self.encoding.encode(str(value)))
                if key == "role":
                    num_tokens -= 1  # Role is always 1 token
        num_tokens += 2  # Every reply is primed with <im_start>assistant
        return num_tokens
    
    def count_text(self, text: str) -> int:
        """Count tokens in a text string."""
        return len(self.encoding.encode(text))


class EnhancedLLMService:
    """
    Enhanced LLM service with memory integration and multi-provider support.
    """
    
    def __init__(
        self,
        config: Optional[EnhancedLLMConfig] = None,
        db: Optional[AsyncSession] = None
    ):
        """
        Initialize the enhanced LLM service.
        
        Args:
            config: LLM configuration
            db: Database session for memory access
        """
        self.config = config or EnhancedLLMConfig()
        self.db = db
        self.memory_service = MemoryService(db) if db and self.config.memory_enabled else None
        self.token_counter = TokenCounter(self.config.model_name)
        
        # Initialize the LLM
        self._setup_llm()
        
    def _setup_llm(self):
        """Set up the LLM based on provider configuration."""
        provider_config = self.config.get_provider_config()
        
        if self.config.provider in ["openai", "vllm", "ollama", "litellm"]:
            # Use ChatOpenAI for all OpenAI-compatible endpoints
            self.llm = ChatOpenAI(**provider_config)
            logger.info(
                f"Initialized {self.config.provider} LLM",
                extra={
                    "model": self.config.model_name,
                    "base_url": self.config.base_url,
                    "streaming": self.config.streaming
                }
            )
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")
    
    async def _retrieve_relevant_memories(
        self,
        user_id: UUID,
        query: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories for the current context.
        
        Args:
            user_id: User ID for memory retrieval
            query: Query text to search memories
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of relevant memories
        """
        if not self.memory_service:
            return []
            
        try:
            memories = await self.memory_service.search_memories(
                user_id=user_id,
                query=query,
                limit=limit or self.config.memory_search_limit,
                threshold=self.config.memory_threshold
            )
            
            logger.info(
                f"Retrieved {len(memories)} relevant memories",
                extra={"user_id": str(user_id), "query": query[:50]}
            )
            
            return memories
            
        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}", exc_info=True)
            return []
    
    def _format_memories_for_context(
        self,
        memories: List[Dict[str, Any]]
    ) -> str:
        """
        Format retrieved memories for inclusion in the prompt.
        
        Args:
            memories: List of memory dictionaries
            
        Returns:
            Formatted memory context string
        """
        if not memories:
            return ""
            
        memory_context = "## Relevant Context from Memory:\n\n"
        
        for idx, memory in enumerate(memories, 1):
            memory_context += f"{idx}. **{memory['title']}**\n"
            memory_context += f"   - {memory['content']}\n"
            memory_context += f"   - Importance: {memory['importance']:.2f}, "
            memory_context += f"Relevance: {memory['similarity']:.2f}\n"
            
            # Include metadata if available
            if memory.get('metadata'):
                for key, value in memory['metadata'].items():
                    if key not in ['confidence']:  # Skip internal metadata
                        memory_context += f"   - {key.replace('_', ' ').title()}: {value}\n"
                        
            memory_context += "\n"
            
        return memory_context
    
    def _build_enhanced_messages(
        self,
        messages: List[Dict[str, str]],
        memory_context: str
    ) -> List[Dict[str, str]]:
        """
        Build enhanced messages with memory context.
        
        Args:
            messages: Original conversation messages
            memory_context: Formatted memory context
            
        Returns:
            Enhanced messages with memory context
        """
        enhanced_messages = []
        
        # Add system message with memory context if available
        if memory_context:
            system_prompt = (
                "You are a helpful AI assistant with access to conversation history "
                "and memories about the user. Use this context to provide more "
                "personalized and relevant responses.\n\n"
                f"{memory_context}"
            )
            enhanced_messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Add original messages
        enhanced_messages.extend(messages)
        
        return enhanced_messages
    
    def _manage_context_window(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int
    ) -> List[Dict[str, str]]:
        """
        Manage messages to fit within context window.
        
        Args:
            messages: List of messages
            max_tokens: Maximum tokens allowed
            
        Returns:
            Trimmed messages that fit within context window
        """
        # Reserve tokens for response
        available_tokens = self.config.context_window - max_tokens
        
        # Always keep system message and last user message
        if not messages:
            return messages
            
        system_messages = [m for m in messages if m["role"] == "system"]
        other_messages = [m for m in messages if m["role"] != "system"]
        
        if not other_messages:
            return messages
            
        # Start with system messages and last user message
        result = system_messages.copy()
        token_count = self.token_counter.count_messages(result)
        
        # Add messages from the end backwards
        for msg in reversed(other_messages):
            msg_tokens = self.token_counter.count_messages([msg])
            if token_count + msg_tokens <= available_tokens:
                result.insert(len(system_messages), msg)
                token_count += msg_tokens
            else:
                # Add truncation notice
                if len(result) > len(system_messages) + 1:
                    result.insert(len(system_messages), {
                        "role": "system",
                        "content": "[Previous messages truncated due to context length]"
                    })
                break
                
        return result
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        user_id: Optional[UUID] = None,
        conversation_id: Optional[UUID] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Generate a chat completion with memory enhancement.
        
        Args:
            messages: Conversation messages
            user_id: User ID for memory retrieval
            conversation_id: Conversation ID for context
            stream: Whether to stream the response
            **kwargs: Additional parameters for the LLM
            
        Returns:
            Generated response or async generator for streaming
        """
        try:
            # Extract query from last user message
            last_user_message = next(
                (m["content"] for m in reversed(messages) if m["role"] == "user"),
                ""
            )
            
            # Retrieve relevant memories if user_id provided
            memory_context = ""
            if user_id and self.config.memory_enabled:
                memories = await self._retrieve_relevant_memories(
                    user_id, last_user_message
                )
                memory_context = self._format_memories_for_context(memories)
            
            # Build enhanced messages
            enhanced_messages = self._build_enhanced_messages(messages, memory_context)
            
            # Manage context window
            max_tokens = kwargs.get("max_tokens", self.config.max_tokens)
            trimmed_messages = self._manage_context_window(enhanced_messages, max_tokens)
            
            # Log token usage
            token_count = self.token_counter.count_messages(trimmed_messages)
            logger.info(
                f"Chat completion request",
                extra={
                    "user_id": str(user_id) if user_id else None,
                    "conversation_id": str(conversation_id) if conversation_id else None,
                    "message_count": len(trimmed_messages),
                    "token_count": token_count,
                    "memory_context_included": bool(memory_context)
                }
            )
            
            # Convert to LangChain messages
            lc_messages = self._convert_to_langchain_messages(trimmed_messages)
            
            # Generate response
            if stream or self.config.streaming:
                return self._stream_chat_completion(lc_messages, **kwargs)
            else:
                response = await self.llm.agenerate([lc_messages])
                return response.generations[0][0].text
                
        except Exception as e:
            logger.error(
                f"Chat completion failed",
                extra={"error": str(e), "user_id": str(user_id) if user_id else None},
                exc_info=True
            )
            raise ExternalServiceError(
                service="LLM",
                message=f"Failed to generate chat completion: {str(e)}"
            )
    
    async def _stream_chat_completion(
        self,
        messages: List[ChatMessage],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream a chat completion response.
        
        Args:
            messages: LangChain formatted messages
            **kwargs: Additional parameters
            
        Yields:
            Chunks of generated text
        """
        # Use streaming callback
        callback = StreamingStdOutCallbackHandler()
        
        # Stream the response
        response = await self.llm.agenerate(
            [messages],
            callbacks=[callback],
            **kwargs
        )
        
        # For now, yield the complete response
        # TODO: Implement proper streaming with callbacks
        yield response.generations[0][0].text
    
    def _convert_to_langchain_messages(
        self,
        messages: List[Dict[str, str]]
    ) -> List[ChatMessage]:
        """Convert messages to LangChain format."""
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
                # Default to human message
                lc_messages.append(HumanMessage(content=content))
                
        return lc_messages
    
    async def extract_and_store_memories(
        self,
        conversation_id: UUID,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Extract and store memories from a conversation.
        
        This creates a feedback loop where conversations generate memories.
        
        Args:
            conversation_id: ID of the conversation
            user_id: User ID
            
        Returns:
            Summary of extracted memories
        """
        if not self.memory_service:
            return {"error": "Memory service not available"}
            
        try:
            result = await self.memory_service.process_conversation(
                conversation_id, user_id
            )
            
            logger.info(
                f"Extracted memories from conversation",
                extra={
                    "conversation_id": str(conversation_id),
                    "user_id": str(user_id),
                    "memories_created": result["memories_created"]
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(
                f"Failed to extract memories",
                extra={
                    "conversation_id": str(conversation_id),
                    "user_id": str(user_id),
                    "error": str(e)
                },
                exc_info=True
            )
            return {"error": str(e)}