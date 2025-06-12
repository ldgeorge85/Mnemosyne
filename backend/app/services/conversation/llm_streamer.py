"""
LLM Response Streaming Service

This module provides specialized services for streaming responses from LLMs,
handling token-by-token streaming with support for different LLM providers.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, AsyncGenerator, Callable
from fastapi import Request, WebSocket
from starlette.responses import StreamingResponse

from app.services.conversation.response_streamer import ResponseStreamer, ResponseChunk


class LLMStreamingError(Exception):
    """Exception raised for LLM streaming errors."""
    pass


class LLMResponseStreamer(ResponseStreamer):
    """
    Service for streaming responses from LLMs.
    
    This class extends ResponseStreamer with specialized handling for:
    1. Token-by-token streaming from LLMs
    2. Provider-specific adapters for different LLM APIs
    3. Stateful streaming with support for in-progress state tracking
    """
    
    def __init__(self):
        """Initialize the LLM response streamer."""
        super().__init__()
        
        # Default token generation rate in seconds per token
        self.token_generation_rate = 0.02
        
        # Active streaming sessions
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Register default error handlers
        self.register_error_handler(
            LLMStreamingError,
            self._handle_llm_streaming_error
        )
    
    async def _handle_llm_streaming_error(self, error: LLMStreamingError) -> str:
        """
        Handle LLM streaming errors.
        
        Args:
            error: The error to handle
            
        Returns:
            Error message
        """
        return f"LLM response streaming error: {str(error)}"
    
    async def _simulate_llm_streaming(
        self, 
        response_text: str, 
        session_id: str
    ) -> AsyncGenerator[str, None]:
        """
        Simulate token-by-token streaming from an LLM.
        
        Args:
            response_text: Full response text to stream
            session_id: ID of the streaming session
            
        Yields:
            Tokens from the response
        """
        # Track the session
        self.active_sessions[session_id] = {
            "total_tokens": len(response_text.split()),
            "streamed_tokens": 0,
            "is_complete": False,
            "start_time": asyncio.get_event_loop().time()
        }
        
        try:
            # Simulate token-by-token generation by splitting on spaces
            # In a real implementation, this would use a proper tokenizer
            tokens = response_text.split()
            
            for i, token in enumerate(tokens):
                # Add space except for first token
                prefix = " " if i > 0 else ""
                yield f"{prefix}{token}"
                
                # Update session state
                self.active_sessions[session_id]["streamed_tokens"] = i + 1
                
                # Simulate LLM thinking time
                await asyncio.sleep(self.token_generation_rate)
            
            # Mark session as complete
            self.active_sessions[session_id]["is_complete"] = True
        except Exception as e:
            # Mark session as error
            self.active_sessions[session_id]["error"] = str(e)
            raise
        finally:
            # Calculate statistics
            if session_id in self.active_sessions:
                end_time = asyncio.get_event_loop().time()
                start_time = self.active_sessions[session_id]["start_time"]
                self.active_sessions[session_id]["duration"] = end_time - start_time
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a streaming session.
        
        Args:
            session_id: ID of the streaming session
            
        Returns:
            Session status or None if not found
        """
        return self.active_sessions.get(session_id)
    
    def clean_up_session(self, session_id: str) -> None:
        """
        Clean up a streaming session.
        
        Args:
            session_id: ID of the streaming session
        """
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
    
    async def stream_llm_response(
        self,
        response_text: str,
        session_id: str,
        include_metadata: bool = False
    ) -> AsyncGenerator[ResponseChunk, None]:
        """
        Stream an LLM response token by token.
        
        Args:
            response_text: Full response text to stream
            session_id: ID of the streaming session
            include_metadata: Whether to include metadata in chunks
            
        Yields:
            Response chunks
        """
        buffer = ""
        chunk_index = 0
        
        try:
            # Stream tokens
            async for token in self._simulate_llm_streaming(response_text, session_id):
                buffer += token
                
                # Create a chunk with the current buffer
                metadata = None
                if include_metadata:
                    status = self.get_session_status(session_id)
                    metadata = {
                        "session_id": session_id,
                        "progress": status["streamed_tokens"] / status["total_tokens"] if status else 0,
                        "tokens_streamed": status["streamed_tokens"] if status else 0
                    }
                
                yield ResponseChunk(
                    content=buffer,
                    chunk_index=chunk_index,
                    is_last=False,
                    metadata=metadata
                )
                
                chunk_index += 1
            
            # Final chunk with complete response
            metadata = None
            if include_metadata:
                status = self.get_session_status(session_id)
                metadata = {
                    "session_id": session_id,
                    "progress": 1.0,
                    "tokens_streamed": status["total_tokens"] if status else 0,
                    "duration": status["duration"] if status else 0
                }
            
            yield ResponseChunk(
                content=buffer,
                chunk_index=chunk_index,
                is_last=True,
                metadata=metadata
            )
        except Exception as e:
            # Handle error
            error_chunk = await self._handle_error(e)
            if error_chunk:
                yield error_chunk
        finally:
            # Clean up the session after a delay
            asyncio.create_task(self._delayed_cleanup(session_id, 60))
    
    async def _delayed_cleanup(self, session_id: str, delay_seconds: int) -> None:
        """
        Clean up a session after a delay.
        
        Args:
            session_id: ID of the streaming session
            delay_seconds: Delay before cleanup in seconds
        """
        await asyncio.sleep(delay_seconds)
        self.clean_up_session(session_id)
    
    async def stream_llm_to_websocket(
        self,
        websocket: WebSocket,
        response_text: str,
        session_id: str
    ) -> None:
        """
        Stream an LLM response to a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            response_text: Full response text to stream
            session_id: ID of the streaming session
        """
        try:
            # Stream chunks
            async for chunk in self.stream_llm_response(
                response_text=response_text,
                session_id=session_id,
                include_metadata=True
            ):
                # Send chunk as JSON
                await websocket.send_json(chunk.to_dict())
        except Exception as e:
            # Send error message
            error_chunk = await self._handle_error(e)
            if error_chunk:
                await websocket.send_json(error_chunk.to_dict())
    
    def create_llm_sse_response(
        self,
        response_text: str,
        session_id: str
    ) -> StreamingResponse:
        """
        Create a Server-Sent Events response for an LLM response.
        
        Args:
            response_text: Full response text to stream
            session_id: ID of the streaming session
            
        Returns:
            StreamingResponse configured for SSE
        """
        # Create streaming generator
        generator = self.stream_llm_response(
            response_text=response_text,
            session_id=session_id,
            include_metadata=True
        )
        
        # Create SSE response
        return self.create_sse_response(generator)
