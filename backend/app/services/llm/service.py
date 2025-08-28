"""
Simple LLM Service Wrapper

Provides a unified interface for LLM operations used by the agentic system.
"""

import httpx
import json
from typing import Dict, Any, Optional, List, AsyncGenerator
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class LLMService:
    """
    Simple LLM service for agentic operations.
    
    Wraps OpenAI-compatible API calls.
    """
    
    def __init__(self):
        self.base_url = settings.OPENAI_BASE_URL
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.temperature = settings.OPENAI_TEMPERATURE
        self.max_tokens = settings.OPENAI_MAX_TOKENS
    
    async def complete(
        self, 
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs  # Accept additional parameters
    ) -> Dict[str, Any]:
        """
        Get a completion from the LLM.
        
        Args:
            prompt: User prompt
            system: System prompt
            temperature: Temperature override
            max_tokens: Max tokens override
            
        Returns:
            Dict with 'content' key containing the response
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "stream": False,
            **kwargs  # Include any additional parameters
        }
        
        # Only add max_tokens if it's not None
        final_max_tokens = max_tokens if max_tokens is not None else self.max_tokens
        if final_max_tokens is not None:
            data["max_tokens"] = final_max_tokens
        
        logger.info(f"Making LLM request to {self.base_url}/chat/completions")
        logger.debug(f"Request data: {json.dumps(data, indent=2)}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                
                result = response.json()
                logger.debug(f"LLM response: {json.dumps(result, indent=2)[:500]}")
                
                # Handle different response formats
                if "choices" in result and len(result["choices"]) > 0:
                    choice = result["choices"][0]
                    if "message" in choice:
                        # InnoGPT-1 returns content in reasoning_content when content is null
                        content = choice["message"].get("content")
                        if content is None:
                            content = choice["message"].get("reasoning_content", "")
                        if not content:
                            content = ""
                    elif "text" in choice:
                        content = choice["text"]
                    else:
                        content = str(choice)
                else:
                    logger.warning(f"Unexpected LLM response format: {result}")
                    content = ""
                
                return {"content": content}
                
            except httpx.HTTPStatusError as e:
                logger.error(f"LLM HTTP error: {e.response.status_code} - {e.response.text}")
                return {"content": ""}
            except Exception as e:
                logger.error(f"LLM completion error: {e}", exc_info=True)
                return {"content": ""}
    
    async def stream_complete(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs  # Accept additional parameters
    ) -> AsyncGenerator[str, None]:
        """
        Stream a completion from the LLM.
        
        Args:
            messages: Message history
            system: System prompt
            temperature: Temperature override
            max_tokens: Max tokens override
            
        Yields:
            String chunks of the response
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepend system message if provided
        message_list = []
        if system:
            message_list.append({"role": "system", "content": system})
        message_list.extend(messages)
        
        data = {
            "model": self.model,
            "messages": message_list,
            "temperature": temperature or self.temperature,
            "stream": True,
            **kwargs  # Include any additional parameters
        }
        
        # Only add max_tokens if it's not None
        final_max_tokens = max_tokens if max_tokens is not None else self.max_tokens
        if final_max_tokens is not None:
            data["max_tokens"] = final_max_tokens
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str == "[DONE]":
                                break
                            
                            try:
                                chunk = json.loads(data_str)
                                if chunk.get("choices") and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
                                
            except Exception as e:
                logger.error(f"LLM streaming error: {e}")
                yield ""