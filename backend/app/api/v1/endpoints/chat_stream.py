"""
Chat Streaming Endpoint with SSE Support
Provides real-time streaming responses from LLM
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, AsyncGenerator
import datetime
import uuid
import httpx
import json
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.auth.manager import get_current_user, get_optional_user
from app.core.auth.base import AuthUser
from app.services.persona.base import PersonaMode
from app.services.persona.manager import PersonaManager
from app.db.session import get_async_db
from app.services.memory.context import MemoryContextService
from app.services.receipt_service import ReceiptService
from app.db.models.receipt import ReceiptType
from app.services.agentic import AgenticFlowController, MnemosyneAction
from app.services.llm.service import LLMService

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class StreamChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: Optional[bool] = True
    persona_mode: Optional[str] = None

async def stream_llm_response(
    messages: List[ChatMessage],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    system_prompt: Optional[str] = None
) -> AsyncGenerator[str, None]:
    """
    Stream responses from the OpenAI-compatible LLM endpoint
    """
    # Use settings or defaults
    base_url = settings.OPENAI_BASE_URL
    api_key = settings.OPENAI_API_KEY
    model_name = model or settings.OPENAI_MODEL
    temp = temperature or settings.OPENAI_TEMPERATURE
    # Use provided max_tokens, or settings value, or None for no limit
    max_tok = max_tokens if max_tokens is not None else settings.OPENAI_MAX_TOKENS
    
    # Prepare the request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Use provided system prompt or default
    if not system_prompt:
        system_prompt = (
            "You are Mnemosyne, a personal AI assistant focused on cognitive sovereignty and privacy. "
            "You help users manage their memories, thoughts, and knowledge while ensuring complete privacy. "
            "You are thoughtful, helpful, and respect the user's agency and privacy above all else. "
            "Never share user data, always encrypt sensitive information, and empower users to own their cognitive artifacts."
        )
    
    system_message = {
        "role": "system",
        "content": system_prompt
    }
    
    # Prepend system message if not already present
    message_list = [system_message] + [{"role": m.role, "content": m.content} for m in messages]
    
    data = {
        "model": model_name,
        "messages": message_list,
        "temperature": temp,
        "stream": True  # Enable streaming
    }
    
    # Only add max_tokens if it's not None (let model decide length)
    if max_tok is not None:
        data["max_tokens"] = max_tok
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            async with client.stream(
                "POST",
                f"{base_url}/chat/completions",
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
                                    # Yield SSE formatted data
                                    yield f"data: {json.dumps({'choices': [{'delta': {'content': content}}]})}\n\n"
                        except json.JSONDecodeError:
                            continue
                
                # Send completion signal
                yield "data: [DONE]\n\n"
                
        except httpx.TimeoutException:
            yield f"data: {json.dumps({'error': 'Request timed out'})}\n\n"
        except httpx.HTTPStatusError as e:
            yield f"data: {json.dumps({'error': f'LLM error: {e.response.status_code}'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

@router.post("/chat/stream")
async def stream_chat(
    request: StreamChatRequest,
    user: AuthUser = Depends(get_current_user if settings.AUTH_REQUIRED else get_optional_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Streaming chat endpoint with SSE support
    Returns Server-Sent Events stream for real-time responses
    """
    # Initialize PersonaManager
    persona_manager = PersonaManager(db)
    
    # Initialize for user if authenticated
    if user:
        await persona_manager.initialize_for_user(str(user.user_id))
    
    # Determine persona mode
    if request.persona_mode:
        try:
            mode = PersonaMode(request.persona_mode)
        except ValueError:
            mode = PersonaMode.CONFIDANT
    else:
        # Auto-detect mode from last message
        last_user_msg = ""
        for msg in reversed(request.messages):
            if msg.role == "user":
                last_user_msg = msg.content
                break
        
        mode = await persona_manager.analyze_context_for_mode(
            last_user_msg,
            [{"role": m.role, "content": m.content} for m in request.messages]
        )
    
    # Switch to appropriate mode if needed
    if persona_manager.persona.current_mode != mode:
        await persona_manager.switch_mode(mode, "Context analysis")
    
    # Get appropriate system prompt based on mode
    if mode == PersonaMode.MIRROR:
        system_prompt = persona_manager.get_mirror_prompt()
    else:
        system_prompt = persona_manager.get_enhanced_prompt()
    
    modifiers = persona_manager.get_response_parameters()
    
    # Retrieve relevant memory context if user is authenticated
    memory_context = ""
    if user and request.messages:
        last_user_msg = None
        for msg in reversed(request.messages):
            if msg.role == "user":
                last_user_msg = msg.content
                break
        
        if last_user_msg:
            memory_service = MemoryContextService(db)
            relevant_memories = await memory_service.get_relevant_memories(
                query=last_user_msg,
                user_id=str(user.user_id),
                limit=3,
                score_threshold=0.5
            )
            
            if relevant_memories:
                memory_context = memory_service.format_memory_context(relevant_memories)
                system_prompt = f"{system_prompt}\n\n{memory_context}"
    
    # Use persona temperature if not explicitly set
    if request.temperature is None:
        request.temperature = modifiers.get("temperature", 0.7)
    
    # Create receipt for transparency
    if user:
        receipt_service = ReceiptService(db)
        await receipt_service.create_receipt(
            user_id=user.user_id,
            entity_type="chat",
            entity_id=None,
            action="Streaming chat interaction",
            receipt_type=ReceiptType.CHAT_MESSAGE,
            persona_mode=mode.value,
            request_data={
                "messages": [{"role": m.role, "content": m.content[:200]} for m in request.messages],
                "model": request.model or settings.OPENAI_MODEL,
                "temperature": request.temperature,
                "streaming": True
            }
        )
    
    # Return streaming response
    return StreamingResponse(
        stream_llm_response(
            request.messages,
            request.model,
            request.temperature,
            request.max_tokens,
            system_prompt
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable Nginx buffering
        }
    )

@router.post("/chat/complete")
async def complete_chat(
    request: StreamChatRequest,
    user: AuthUser = Depends(get_current_user if settings.AUTH_REQUIRED else get_optional_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Alternative endpoint that always returns complete responses (no streaming)
    Useful for clients that don't support SSE
    """
    # Collect the full response from the stream
    full_response = ""
    async for chunk in stream_llm_response(
        request.messages,
        request.model,
        request.temperature,
        request.max_tokens
    ):
        if chunk.startswith("data: "):
            data_str = chunk[6:].strip()
            if data_str and data_str != "[DONE]":
                try:
                    chunk_data = json.loads(data_str)
                    if "error" in chunk_data:
                        raise HTTPException(status_code=500, detail=chunk_data["error"])
                    if chunk_data.get("choices"):
                        content = chunk_data["choices"][0].get("delta", {}).get("content", "")
                        full_response += content
                except json.JSONDecodeError:
                    continue
    
    # Return in OpenAI format
    return {
        "id": f"chat-{uuid.uuid4()}",
        "object": "chat.completion",
        "created": int(datetime.datetime.now().timestamp()),
        "model": request.model or settings.OPENAI_MODEL,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": full_response
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": sum(len(m.content.split()) for m in request.messages) * 2,
            "completion_tokens": len(full_response.split()) * 2,
            "total_tokens": (sum(len(m.content.split()) for m in request.messages) + len(full_response.split())) * 2
        }
    }