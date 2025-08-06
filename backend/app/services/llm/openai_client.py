"""
OpenAI API Client

This module provides a specialized client for interacting with OpenAI's API,
with additional features like rate limiting, error handling, and retry logic.
"""
import time
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Generator, AsyncGenerator
from functools import wraps
import backoff

from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletion

from app.core.config import settings


# Set up module logger
logger = logging.getLogger(__name__)


class RateLimitManager:
    """
    Manages rate limiting for API requests.
    
    This class implements a token bucket algorithm for rate limiting
    to ensure we don't exceed OpenAI's rate limits.
    """
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        tokens_per_minute: int = 90000,  # GPT-4 token limit per minute
        burst_limit: int = 5
    ):
        """
        Initialize the rate limit manager.
        
        Args:
            requests_per_minute: Maximum requests per minute
            tokens_per_minute: Maximum tokens per minute
            burst_limit: Max concurrent requests allowed in bursts
        """
        self.requests_per_minute = requests_per_minute
        self.tokens_per_minute = tokens_per_minute
        self.burst_limit = burst_limit
        
        # Token buckets
        self.request_tokens = requests_per_minute
        self.content_tokens = tokens_per_minute
        
        # Timestamps for refill
        self.last_request_refill = time.time()
        self.last_token_refill = time.time()
        
        # Semaphore for limiting concurrent requests
        self._semaphore = asyncio.Semaphore(burst_limit)
    
    async def _refill_buckets(self):
        """Refill token buckets based on elapsed time."""
        now = time.time()
        
        # Refill request tokens
        elapsed_minutes = (now - self.last_request_refill) / 60.0
        self.request_tokens = min(
            self.requests_per_minute,
            self.request_tokens + int(elapsed_minutes * self.requests_per_minute)
        )
        self.last_request_refill = now
        
        # Refill content tokens
        elapsed_minutes = (now - self.last_token_refill) / 60.0
        self.content_tokens = min(
            self.tokens_per_minute,
            self.content_tokens + int(elapsed_minutes * self.tokens_per_minute)
        )
        self.last_token_refill = now
    
    async def acquire(self, token_estimate: int = 0) -> None:
        """
        Acquire permission to make an API request.
        
        Args:
            token_estimate: Estimated number of tokens for this request
            
        Raises:
            asyncio.TimeoutError: If rate limit is exceeded and wait time is too long
        """
        async with self._semaphore:
            await self._refill_buckets()
            
            # Check if we have enough tokens
            if self.request_tokens <= 0 or (token_estimate > 0 and self.content_tokens < token_estimate):
                # Calculate wait time
                wait_request = 0
                wait_content = 0
                
                if self.request_tokens <= 0:
                    wait_request = (1 - self.request_tokens / self.requests_per_minute) * 60
                
                if token_estimate > 0 and self.content_tokens < token_estimate:
                    wait_content = ((token_estimate - self.content_tokens) / self.tokens_per_minute) * 60
                
                wait_time = max(wait_request, wait_content)
                
                if wait_time > 10:  # Don't wait longer than 10 seconds
                    raise asyncio.TimeoutError(f"Rate limit exceeded. Would need to wait {wait_time:.1f}s")
                
                logger.warning(f"Rate limit approaching. Waiting {wait_time:.1f}s before request")
                await asyncio.sleep(wait_time)
                await self._refill_buckets()
            
            # Consume tokens
            self.request_tokens -= 1
            if token_estimate > 0:
                self.content_tokens -= token_estimate


class OpenAIClient:
    """
    Client for interacting with OpenAI's API.
    
    This client provides a thin wrapper around OpenAI's API with
    additional features like rate limiting, error handling, and retries.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        organization_id: Optional[str] = None
    ):
        """
        Initialize the OpenAI client.
        
        Args:
            api_key: OpenAI API key (defaults to settings.OPENAI_API_KEY)
            base_url: Base URL for the OpenAI API (defaults to settings.OPENAI_BASE_URL)
            model_name: Default model to use (defaults to settings.OPENAI_MODEL)
            temperature: Default temperature for sampling (0.0-1.0)
            max_tokens: Default maximum tokens to generate (defaults to settings.OPENAI_MAX_TOKENS)
            organization_id: OpenAI organization ID (optional, defaults to settings.OPENAI_ORG_ID)
        """
        # Store the configuration
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.base_url = base_url or settings.OPENAI_BASE_URL
        self.model_name = model_name or settings.OPENAI_MODEL
        self.temperature = temperature or settings.OPENAI_TEMPERATURE
        self.max_tokens = max_tokens or settings.OPENAI_MAX_TOKENS
        self.organization_id = organization_id or settings.OPENAI_ORG_ID
        
        # Initialize OpenAI clients
        self._setup_clients()
        self.rate_limiter = RateLimitManager()
        
        # Global retry configuration using backoff library
        self.max_retries = 5
        self.max_time = 30  # seconds
    
    def _setup_clients(self):
        """Initialize OpenAI clients with proper configuration."""
        # Client configuration
        client_config = {
            "api_key": self.api_key or "dummy-key",  # Provide dummy key if none configured
        }
        
        # Add base URL if provided
        if self.base_url:
            client_config["base_url"] = self.base_url
            logger.info(f"OpenAI base URL configured: {self.base_url}")
        else:
            logger.info("Using default OpenAI API base URL")
            
        # Add organization ID if provided (optional for custom endpoints)
        if self.organization_id:
            client_config["organization"] = self.organization_id
            logger.info("OpenAI organization ID configured")
        else:
            logger.info("OpenAI organization ID not provided (optional for custom endpoints)")
            
        # Initialize both sync and async clients
        try:
            self.client = OpenAI(**client_config)
            self.async_client = AsyncOpenAI(**client_config)
            
            if not self.api_key:
                logger.warning("OpenAI API key is not configured - client initialized with dummy key")
            else:
                logger.info("OpenAI clients initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI clients: {e}")
            # Initialize with minimal config as fallback
            self.client = None
            self.async_client = None
    
    def _estimate_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """
        Estimate token count for a list of messages.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Estimated token count
        """
        # Simplified token estimation (4 chars ~= 1 token)
        total_chars = sum(len(msg.get('content', '')) for msg in messages)
        return total_chars // 4

    def _handle_error(self, e: Exception) -> Exception:
        """
        Process API errors and provide appropriate handling.
        
        Args:
            e: The exception that occurred
            
        Returns:
            Processed exception with additional context
        """
        # Use string-based error detection for compatibility with any OpenAI SDK version
        error_str = str(e).lower()
        error_type = e.__class__.__name__
        
        if "rate limit" in error_str or "ratelimit" in error_type.lower():
            logger.warning(f"Rate limit exceeded: {str(e)}")
            return RuntimeError(f"OpenAI rate limit exceeded. Please try again later.")
        elif "invalid" in error_str:
            logger.error(f"Invalid request: {str(e)}")
            return ValueError(f"Invalid request to OpenAI API: {str(e)}")
        elif "auth" in error_str or "authentication" in error_type.lower():
            logger.critical(f"Authentication error: {str(e)}")
            return RuntimeError("API key error. Please check your OpenAI API key configuration.")
        elif "connection" in error_str or "connection" in error_type.lower():
            logger.error(f"API connection error: {str(e)}")
            return RuntimeError("Could not connect to OpenAI API. Please check your internet connection.")
        elif "unavailable" in error_str or "service" in error_str:
            logger.error(f"Service unavailable: {str(e)}")
            return RuntimeError("OpenAI service is currently unavailable. Please try again later.")
        else:
            logger.error(f"Unexpected error: {str(e)}")
            return e

    # Backoff decorator for retrying on certain errors
    def _backoff_handler(self, e: Exception):
        """
        Determine if an exception should trigger a retry.
        
        Args:
            e: The exception to check
        
        Returns:
            True if the request should be retried, False otherwise
        """
        error_str = str(e).lower()
        error_type = e.__class__.__name__
        
        # Check for connection, service, or timeout issues
        if ("connection" in error_str or 
            "unavailable" in error_str or 
            "timeout" in error_str or 
            "timeout" in error_type.lower() or
            isinstance(e, asyncio.TimeoutError)):
            logger.warning(f"Request failed with {type(e).__name__}. Retrying...")
            return True
        return False

    @backoff.on_exception(
        backoff.expo,
        (Exception),  # Catch all exceptions and filter in the _backoff_handler
        max_tries=5,
        max_time=30,
        giveup=lambda e: "auth" in str(e).lower() or 
                           ("invalid" in str(e).lower() and "request" in str(e).lower())
    )
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs: Any
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Generate a chat completion using OpenAI's API.
        
        Args:
            messages: List of message dictionaries
            model: Model to use for completion
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional parameters for the API
            
        Returns:
            Generated text or async generator for streaming responses
            
        Raises:
            ValueError: If input is invalid
            RuntimeError: If API request fails
        """
        try:
            # Check if client is properly initialized
            if not self.async_client:
                raise RuntimeError("OpenAI client is not properly initialized")
                
            # Validate input
            if not messages:
                raise ValueError("Messages cannot be empty")
                
            # Set up parameters
            params = {
                "model": model or self.model_name,
                "messages": messages,
                "temperature": temperature if temperature is not None else self.temperature,
                "max_tokens": max_tokens or self.max_tokens,
                **kwargs
            }
            
            # Estimate token usage for rate limiting
            token_estimate = self._estimate_tokens(messages)
            await self.rate_limiter.acquire(token_estimate)
            
            # Generate completion
            if stream:
                return self._stream_chat_completion(params)
            else:
                response = await self.async_client.chat.completions.create(**params)
                return response.choices[0].message.content
                
        except Exception as e:
            raise self._handle_error(e)

    async def _stream_chat_completion(
        self, params: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """
        Stream a chat completion from OpenAI's API.
        
        Args:
            params: Parameters for the API request
            
        Yields:
            Chunks of generated text
        """
        try:
            # Enable streaming
            params["stream"] = True
            response = await self.async_client.chat.completions.create(**params)
            
            async for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    choice = chunk.choices[0]
                    if choice.delta and choice.delta.content:
                        yield choice.delta.content
                        
        except Exception as e:
            raise self._handle_error(e)

    async def embeddings(
        self,
        text: Union[str, List[str]],
        model: Optional[str] = None,
        **kwargs: Any
    ) -> List[List[float]]:
        """
        Generate embeddings for text using OpenAI's API.
        
        Args:
            text: Text or list of texts to embed
            model: Model to use for embeddings
            **kwargs: Additional parameters for the API
            
        Returns:
            List of embedding vectors
            
        Raises:
            ValueError: If input is invalid
            RuntimeError: If API request fails
        """
        try:
            # Validate input
            if not text:
                raise ValueError("Text cannot be empty")
                
            # Normalize input to list
            if isinstance(text, str):
                text_list = [text]
            else:
                text_list = text
                
            # Estimate tokens for rate limiting
            token_estimate = sum(len(t) // 4 for t in text_list)  # Rough estimate
            
            # Prepare request parameters
            params = {
                "model": model or "text-embedding-ada-002",
                "input": text_list,
                **kwargs
            }
            
            # Acquire rate limit permission
            await self.rate_limiter.acquire(token_estimate)
            
            # Get embeddings
            response = await self.async_client.embeddings.create(**params)
            
            # Extract embedding vectors
            embeddings = [item.embedding for item in response.data]
            return embeddings
            
        except Exception as e:
            raise self._handle_error(e)

    async def moderation(
        self, 
        text: Union[str, List[str]], 
        model: str = "text-moderation-latest",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Check text against OpenAI's moderation endpoint.
        
        Args:
            text: Text or list of texts to check
            model: Moderation model to use
            **kwargs: Additional parameters for the API
            
        Returns:
            Moderation results
            
        Raises:
            ValueError: If input is invalid
            RuntimeError: If API request fails
        """
        try:
            # Validate input
            if not text:
                raise ValueError("Text cannot be empty")
                
            # Normalize input to list
            if isinstance(text, str):
                text_list = [text]
            else:
                text_list = text
                
            # Prepare request parameters
            params = {
                "model": model,
                "input": text_list,
                **kwargs
            }
            
            # Rate limiting (just count the request, not tokens)
            await self.rate_limiter.acquire(0)
            
            # Get moderation results
            response = await self.async_client.moderations.create(**params)
            return response
            
        except Exception as e:
            raise self._handle_error(e)
