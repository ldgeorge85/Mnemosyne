"""
OpenAI-compatible chat endpoint for Mnemosyne Protocol
"""

from typing import List, Optional, Any, AsyncGenerator
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
import json
import uuid
import asyncio

from api.deps import get_db, get_current_active_user
from models.user import User
from models.memory import Memory
from services.memory_service import MemoryService
from services.agent_service import AgentService
# LangChain deferred to Sprint 5
from core.config import get_settings

router = APIRouter()
settings = get_settings()


# OpenAI-compatible models
class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(system|user|assistant)$")
    content: str
    name: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    model: Optional[str] = "gpt-3.5-turbo"
    messages: List[ChatMessage]
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=4000)
    stream: Optional[bool] = False
    # Mnemosyne-specific extensions
    use_memory: Optional[bool] = True
    memory_context_limit: Optional[int] = 5
    create_memory: Optional[bool] = True
    agent_reflection: Optional[bool] = False


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[dict]
    usage: dict


class ChatCompletionStreamResponse(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[dict]


async def generate_chat_response(
    request: ChatCompletionRequest,
    user: User,
    db: AsyncSession
) -> str:
    """
    Generate chat response with memory context
    """
    memory_service = MemoryService(db)
    agent_service = AgentService(db)
    
    # Get relevant memories if requested
    context_messages = []
    if request.use_memory:
        # Extract user's latest message for context search
        user_message = next(
            (msg.content for msg in reversed(request.messages) if msg.role == "user"),
            ""
        )
        
        if user_message:
            memories = await memory_service.search_relevant_memories(
                query=user_message,
                user_id=user.id,
                limit=request.memory_context_limit
            )
            
            if memories:
                memory_context = "\n".join([
                    f"[Memory from {m.created_at.strftime('%Y-%m-%d')}: {m.content[:200]}...]"
                    for m in memories
                ])
                context_messages.append(ChatMessage(
                    role="system",
                    content=f"Relevant memories from our conversations:\n{memory_context}"
                ))
    
    # Build messages for LLM
    llm_messages = context_messages + request.messages
    
    # Simplified response for Sprint 1-4 (LangChain deferred to Sprint 5)
    # For now, return a placeholder response
    user_message = next(
        (msg.content for msg in reversed(request.messages) if msg.role == "user"),
        "Hello"
    )
    assistant_message = f"I received your message: '{user_message[:100]}'. Full LLM integration coming in Sprint 5."
    
    # Create memory from conversation if requested
    if request.create_memory:
        user_message = next(
            (msg.content for msg in reversed(request.messages) if msg.role == "user"),
            ""
        )
        
        if user_message:
            memory_content = f"User: {user_message}\n\nAssistant: {assistant_message}"
            await memory_service.create_memory(
                user_id=user.id,
                content=memory_content,
                metadata={
                    "type": "conversation",
                    "model": request.model,
                    "timestamp": datetime.utcnow().isoformat()
                },
                importance=0.5
            )
    
    # Trigger agent reflection if requested
    if request.agent_reflection and user_message:
        asyncio.create_task(
            agent_service.trigger_reflection(
                user_id=user.id,
                content=user_message,
                response=assistant_message
            )
        )
    
    return assistant_message


async def stream_chat_response(
    request: ChatCompletionRequest,
    user: User,
    db: AsyncSession
) -> AsyncGenerator[str, None]:
    """
    Stream chat response with SSE format
    """
    # Generate unique ID for this completion
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
    created = int(datetime.utcnow().timestamp())
    
    # Get the response (for now, not truly streaming from LLM)
    response_text = await generate_chat_response(request, user, db)
    
    # Stream response in chunks
    chunks = response_text.split(" ")
    for i, chunk in enumerate(chunks):
        # Add space back except for last chunk
        if i < len(chunks) - 1:
            chunk += " "
        
        # Create SSE data
        stream_chunk = ChatCompletionStreamResponse(
            id=completion_id,
            created=created,
            model=request.model,
            choices=[{
                "index": 0,
                "delta": {"content": chunk},
                "finish_reason": None
            }]
        )
        
        yield f"data: {stream_chunk.model_dump_json()}\n\n"
        await asyncio.sleep(0.01)  # Small delay for streaming effect
    
    # Send final chunk
    final_chunk = ChatCompletionStreamResponse(
        id=completion_id,
        created=created,
        model=request.model,
        choices=[{
            "index": 0,
            "delta": {},
            "finish_reason": "stop"
        }]
    )
    yield f"data: {final_chunk.model_dump_json()}\n\n"
    yield "data: [DONE]\n\n"


@router.post("/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    OpenAI-compatible chat completions endpoint
    
    Supports both streaming and non-streaming responses
    """
    if request.stream:
        # Return streaming response
        return StreamingResponse(
            stream_chat_response(request, current_user, db),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    else:
        # Return regular response
        response_text = await generate_chat_response(request, current_user, db)
        
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
        created = int(datetime.utcnow().timestamp())
        
        # Estimate token usage (rough approximation)
        prompt_tokens = sum(len(msg.content.split()) * 1.3 for msg in request.messages)
        completion_tokens = len(response_text.split()) * 1.3
        
        return ChatCompletionResponse(
            id=completion_id,
            created=created,
            model=request.model,
            choices=[{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }],
            usage={
                "prompt_tokens": int(prompt_tokens),
                "completion_tokens": int(completion_tokens),
                "total_tokens": int(prompt_tokens + completion_tokens)
            }
        )


@router.post("/")
async def simple_chat(
    message: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Simple chat endpoint for quick interactions
    """
    request = ChatCompletionRequest(
        messages=[ChatMessage(role="user", content=message)],
        use_memory=True,
        create_memory=True
    )
    
    response = await chat_completions(request, current_user, db)
    
    return {
        "response": response.choices[0]["message"]["content"],
        "memory_created": True
    }