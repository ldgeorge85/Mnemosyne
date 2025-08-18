"""
Chat Endpoint with Real LLM Integration
Uses OpenAI-compatible endpoint configured in settings
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import datetime
import uuid
import httpx
from app.core.config import settings
from app.core.auth.manager import get_current_user, get_optional_user
from app.core.auth.base import AuthUser

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False

class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[dict]
    usage: dict

async def call_llm(messages: List[ChatMessage], model: Optional[str] = None, 
                   temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> dict:
    """
    Call the OpenAI-compatible LLM endpoint
    """
    # Use settings or defaults
    base_url = settings.OPENAI_BASE_URL
    api_key = settings.OPENAI_API_KEY
    model_name = model or settings.OPENAI_MODEL
    temp = temperature or settings.OPENAI_TEMPERATURE
    max_tok = max_tokens or settings.OPENAI_MAX_TOKENS
    
    # Prepare the request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Add system prompt for Mnemosyne context
    system_message = {
        "role": "system",
        "content": (
            "You are Mnemosyne, a personal AI assistant focused on cognitive sovereignty and privacy. "
            "You help users manage their memories, thoughts, and knowledge while ensuring complete privacy. "
            "You are thoughtful, helpful, and respect the user's agency and privacy above all else. "
            "Never share user data, always encrypt sensitive information, and empower users to own their cognitive artifacts."
        )
    }
    
    # Prepend system message if not already present
    message_list = [system_message] + [{"role": m.role, "content": m.content} for m in messages]
    
    data = {
        "model": model_name,
        "messages": message_list,
        "temperature": temp,
        "max_tokens": max_tok,
        "stream": False
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="LLM request timed out")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, 
                              detail=f"LLM request failed: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM request error: {str(e)}")

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest, 
    user: AuthUser = Depends(get_current_user if settings.AUTH_REQUIRED else get_optional_user)
) -> ChatResponse:
    """
    Chat endpoint connected to real LLM
    Requires authentication if AUTH_REQUIRED is True
    """
    # Get user context from authenticated user
    user_context = f" (User: {user.username if user else 'anonymous'})"
    
    try:
        # Call the LLM
        llm_response = await call_llm(
            request.messages,
            request.model,
            request.temperature,
            request.max_tokens
        )
        
        # Extract the response
        if not llm_response.get("choices") or not llm_response["choices"]:
            raise HTTPException(status_code=500, detail="No response from LLM")
        
        # Add user context to response if available
        response_content = llm_response["choices"][0]["message"]["content"]
        
        # Return in OpenAI format
        return ChatResponse(
            id=llm_response.get("id", f"chat-{uuid.uuid4()}"),
            object="chat.completion",
            created=llm_response.get("created", int(datetime.datetime.now().timestamp())),
            model=llm_response.get("model", request.model or settings.OPENAI_MODEL),
            choices=llm_response["choices"],
            usage=llm_response.get("usage", {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            })
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Fallback to simple response on error
        print(f"LLM Error: {e}")
        fallback_response = (
            "I apologize, but I'm having trouble connecting to my language processing system. "
            "Please try again in a moment. Your privacy and data remain secure."
        )
        
        return ChatResponse(
            id=f"chat-{uuid.uuid4()}",
            object="chat.completion",
            created=int(datetime.datetime.now().timestamp()),
            model="fallback",
            choices=[{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": fallback_response + user_context
                },
                "finish_reason": "stop"
            }],
            usage={
                "prompt_tokens": sum(len(m.content.split()) for m in request.messages),
                "completion_tokens": len(fallback_response.split()),
                "total_tokens": sum(len(m.content.split()) for m in request.messages) + len(fallback_response.split())
            }
        )

@router.post("/completions", response_model=ChatResponse)
async def chat_completions(
    request: ChatRequest,
    user: AuthUser = Depends(get_current_user if settings.AUTH_REQUIRED else get_optional_user)
) -> ChatResponse:
    """
    Alias for /chat to match OpenAI API
    Requires authentication if AUTH_REQUIRED is True
    """
    return await chat(request, user)