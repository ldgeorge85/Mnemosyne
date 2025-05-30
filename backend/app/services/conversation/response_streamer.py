"""
Response Streaming Service

This module provides services for streaming responses to clients,
supporting Server-Sent Events (SSE) and handling chunked responses
with proper error recovery.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, AsyncGenerator, Callable, Union
from datetime import datetime
from starlette.responses import StreamingResponse
from fastapi import Request

from app.db.models.conversation import Message


class StreamingError(Exception):
    """Exception raised for streaming errors."""
    pass


class ResponseChunk:
    """Represents a chunk of a streaming response."""
    
    def __init__(
        self, 
        content: str, 
        chunk_id: str = None,
        chunk_index: int = 0,
        is_last: bool = False,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize a response chunk.
        
        Args:
            content: The content of this chunk
            chunk_id: Unique ID for this chunk
            chunk_index: Index of this chunk in the sequence
            is_last: Whether this is the last chunk
            metadata: Additional metadata
        """
        self.content = content
        self.chunk_id = chunk_id or f"chunk-{datetime.utcnow().timestamp()}-{chunk_index}"
        self.chunk_index = chunk_index
        self.is_last = is_last
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the chunk to a dictionary.
        
        Returns:
            Dictionary representation of the chunk
        """
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "index": self.chunk_index,
            "is_last": self.is_last,
            "created_at": self.created_at,
            "metadata": self.metadata
        }
    
    def to_sse_event(self, event: str = "message") -> str:
        """
        Format the chunk as a Server-Sent Event.
        
        Args:
            event: The event name
            
        Returns:
            Formatted SSE event string
        """
        data = json.dumps(self.to_dict())
        return f"event: {event}\ndata: {data}\n\n"
    
    @classmethod
    def create_from_text(cls, text: str, chunk_size: int = 100) -> List["ResponseChunk"]:
        """
        Split a text into multiple chunks.
        
        Args:
            text: The text to split
            chunk_size: Maximum characters per chunk
            
        Returns:
            List of ResponseChunk objects
        """
        chunks = []
        
        # Simple character-based chunking (in production, use token-based chunking)
        for i in range(0, len(text), chunk_size):
            chunk_text = text[i:i+chunk_size]
            chunk_index = i // chunk_size
            is_last = (i + chunk_size) >= len(text)
            
            chunks.append(cls(
                content=chunk_text,
                chunk_index=chunk_index,
                is_last=is_last
            ))
        
        return chunks


class ResponseStreamer:
    """
    Service for streaming responses to clients.
    
    This class handles:
    1. Server-Sent Events (SSE) streaming
    2. Chunked response generation
    3. Error recovery during streaming
    """
    
    def __init__(self):
        """Initialize the response streamer."""
        # Default chunk size in characters
        self.default_chunk_size = 100
        
        # Default delay between chunks in seconds
        self.default_chunk_delay = 0.05
        
        # Default timeout for streaming in seconds
        self.default_timeout = 60
        
        # Error handlers for different error types
        self.error_handlers: Dict[type, Callable] = {}
    
    def register_error_handler(self, error_type: type, handler: Callable) -> None:
        """
        Register an error handler for a specific error type.
        
        Args:
            error_type: The type of error to handle
            handler: The handler function
        """
        self.error_handlers[error_type] = handler
    
    async def _handle_error(self, error: Exception) -> Optional[ResponseChunk]:
        """
        Handle a streaming error using registered error handlers.
        
        Args:
            error: The error to handle
            
        Returns:
            Error chunk if error was handled, None otherwise
        """
        # Find a handler for this error type
        for error_type, handler in self.error_handlers.items():
            if isinstance(error, error_type):
                error_content = await handler(error)
                return ResponseChunk(
                    content=error_content,
                    is_last=True,
                    metadata={"error": str(error), "error_type": error_type.__name__}
                )
        
        # Default error handler
        return ResponseChunk(
            content="An error occurred during streaming. Please try again.",
            is_last=True,
            metadata={"error": str(error), "error_type": type(error).__name__}
        )
    
    async def stream_text(
        self, 
        text: str,
        chunk_size: Optional[int] = None,
        chunk_delay: Optional[float] = None
    ) -> AsyncGenerator[ResponseChunk, None]:
        """
        Stream a text as chunks.
        
        Args:
            text: The text to stream
            chunk_size: Size of each chunk (default: self.default_chunk_size)
            chunk_delay: Delay between chunks (default: self.default_chunk_delay)
            
        Yields:
            Response chunks
        """
        chunk_size = chunk_size or self.default_chunk_size
        chunk_delay = chunk_delay or self.default_chunk_delay
        
        # Create chunks
        chunks = ResponseChunk.create_from_text(text, chunk_size)
        
        try:
            # Stream each chunk
            for chunk in chunks:
                yield chunk
                
                # Simulate processing time
                if not chunk.is_last and chunk_delay > 0:
                    await asyncio.sleep(chunk_delay)
        except Exception as e:
            # Handle error
            error_chunk = await self._handle_error(e)
            if error_chunk:
                yield error_chunk
    
    async def stream_generator(
        self,
        generator: AsyncGenerator[str, None],
        chunk_delay: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> AsyncGenerator[ResponseChunk, None]:
        """
        Stream from an async generator.
        
        Args:
            generator: Async generator producing content
            chunk_delay: Delay between chunks (default: self.default_chunk_delay)
            timeout: Timeout for the entire streaming (default: self.default_timeout)
            
        Yields:
            Response chunks
        """
        chunk_delay = chunk_delay or self.default_chunk_delay
        timeout = timeout or self.default_timeout
        
        chunk_index = 0
        last_chunk = None
        
        try:
            # Start a timeout task
            done = asyncio.Event()
            timeout_task = asyncio.create_task(self._timeout_handler(done, timeout))
            
            # Stream from the generator
            async for content in generator:
                # Cancel timeout if we're still receiving content
                if not done.is_set():
                    done.set()
                
                chunk = ResponseChunk(
                    content=content,
                    chunk_index=chunk_index
                )
                chunk_index += 1
                last_chunk = chunk
                
                yield chunk
                
                # Simulate processing time
                if chunk_delay > 0:
                    await asyncio.sleep(chunk_delay)
            
            # Final chunk if we had content
            if last_chunk:
                # Mark the last chunk as last
                last_chunk.is_last = True
                yield ResponseChunk(
                    content="",
                    chunk_index=chunk_index,
                    is_last=True
                )
        except asyncio.TimeoutError:
            # Handle timeout
            yield ResponseChunk(
                content="Response streaming timed out.",
                chunk_index=chunk_index,
                is_last=True,
                metadata={"error": "timeout", "error_type": "TimeoutError"}
            )
        except Exception as e:
            # Handle other errors
            error_chunk = await self._handle_error(e)
            if error_chunk:
                yield error_chunk
        finally:
            # Clean up timeout task
            if 'timeout_task' in locals() and not timeout_task.done():
                timeout_task.cancel()
    
    async def _timeout_handler(self, done: asyncio.Event, timeout: float) -> None:
        """
        Handle streaming timeout.
        
        Args:
            done: Event to signal completion
            timeout: Timeout in seconds
            
        Raises:
            asyncio.TimeoutError: If timeout occurs
        """
        try:
            await asyncio.wait_for(done.wait(), timeout)
        except asyncio.TimeoutError:
            raise
    
    def create_sse_response(
        self, 
        generator: AsyncGenerator[ResponseChunk, None]
    ) -> StreamingResponse:
        """
        Create a Server-Sent Events streaming response.
        
        Args:
            generator: Async generator producing response chunks
            
        Returns:
            StreamingResponse configured for SSE
        """
        async def sse_generator():
            try:
                async for chunk in generator:
                    yield chunk.to_sse_event()
            except Exception as e:
                # Handle unexpected errors
                error_chunk = await self._handle_error(e)
                if error_chunk:
                    yield error_chunk.to_sse_event("error")
        
        return StreamingResponse(
            sse_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
    
    def create_chunked_response(
        self, 
        generator: AsyncGenerator[ResponseChunk, None]
    ) -> StreamingResponse:
        """
        Create a chunked HTTP response.
        
        Args:
            generator: Async generator producing response chunks
            
        Returns:
            StreamingResponse configured for chunked transfer
        """
        async def json_generator():
            try:
                async for chunk in generator:
                    yield json.dumps(chunk.to_dict()) + "\n"
            except Exception as e:
                # Handle unexpected errors
                error_chunk = await self._handle_error(e)
                if error_chunk:
                    yield json.dumps(error_chunk.to_dict()) + "\n"
        
        return StreamingResponse(
            json_generator(),
            media_type="application/json",
            headers={"Transfer-Encoding": "chunked"}
        )
    
    async def stream_message_creation(
        self,
        message_text: str,
        request: Request,
        use_sse: bool = True,
        chunk_size: Optional[int] = None,
        chunk_delay: Optional[float] = None
    ) -> StreamingResponse:
        """
        Stream the creation of a message to the client.
        
        Args:
            message_text: The message content to stream
            request: FastAPI request object
            use_sse: Whether to use Server-Sent Events (default: True)
            chunk_size: Size of each chunk (default: self.default_chunk_size)
            chunk_delay: Delay between chunks (default: self.default_chunk_delay)
            
        Returns:
            StreamingResponse for the message creation
        """
        # Create text streaming generator
        text_generator = self.stream_text(
            text=message_text,
            chunk_size=chunk_size,
            chunk_delay=chunk_delay
        )
        
        # Create response based on preferred streaming method
        if use_sse:
            return self.create_sse_response(text_generator)
        else:
            return self.create_chunked_response(text_generator)
    
    def recover_from_connection_error(self, message_id: str, chunk_index: int) -> List[ResponseChunk]:
        """
        Recover missing chunks after a connection error.
        
        Args:
            message_id: ID of the message being streamed
            chunk_index: Index of the last received chunk
            
        Returns:
            List of missing chunks
        """
        # This is a placeholder - in a real implementation, this would
        # retrieve the missing chunks from a database or cache
        return [
            ResponseChunk(
                content="[Connection was lost. Resuming streaming...]",
                chunk_index=chunk_index + 1,
                metadata={"recovered": True}
            )
        ]
