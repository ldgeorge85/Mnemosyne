"""
Chat Endpoint with Real LLM Integration and Persona Support
Uses OpenAI-compatible endpoint configured in settings
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import datetime
import uuid
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.auth.manager import get_current_user, get_optional_user
from app.core.auth.base import AuthUser
from app.services.persona.base import get_persona, PersonaMode, PersonaContext
from app.services.persona.manager import PersonaManager
from app.db.session import get_async_db
from app.db.repositories.conversation import ConversationRepository, MessageRepository
from app.services.memory.context import MemoryContextService

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
    persona_mode: Optional[str] = None  # confidant, mentor, mediator, guardian

class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[dict]
    usage: dict

async def call_llm(messages: List[ChatMessage], model: Optional[str] = None, 
                   temperature: Optional[float] = None, max_tokens: Optional[int] = None,
                   system_prompt: Optional[str] = None) -> dict:
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
    
    # Use provided system prompt or default
    if system_prompt:
        system_content = system_prompt
    else:
        system_content = (
            "You are Mnemosyne, a personal AI assistant focused on cognitive sovereignty and privacy. "
            "You help users manage their memories, thoughts, and knowledge while ensuring complete privacy. "
            "You are thoughtful, helpful, and respect the user's agency and privacy above all else. "
            "Never share user data, always encrypt sensitive information, and empower users to own their cognitive artifacts."
        )
    
    system_message = {
        "role": "system",
        "content": system_content
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
    user: AuthUser = Depends(get_current_user if settings.AUTH_REQUIRED else get_optional_user),
    db: AsyncSession = Depends(get_async_db)
) -> ChatResponse:
    """
    Chat endpoint connected to real LLM with persona support
    Requires authentication if AUTH_REQUIRED is True
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
    
    # Get enhanced system prompt with worldview adaptations
    system_prompt = persona_manager.get_enhanced_prompt()
    modifiers = persona_manager.get_response_parameters()
    
    # Retrieve relevant memory context if user is authenticated
    memory_context = ""
    if user and request.messages:
        # Get the last user message as the query
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
                limit=3,  # Top 3 most relevant memories
                score_threshold=0.5  # Lower threshold for broader context
            )
            
            if relevant_memories:
                memory_context = memory_service.format_memory_context(relevant_memories)
                # Add memory context to system prompt
                system_prompt = f"{system_prompt}\n\n{memory_context}"
    
    # Use persona temperature if not explicitly set
    if request.temperature is None:
        request.temperature = modifiers.get("temperature", 0.7)
    
    try:
        # Call the LLM with persona system prompt and memory context
        llm_response = await call_llm(
            request.messages,
            request.model,
            request.temperature,
            request.max_tokens,
            system_prompt
        )
        
        # Extract the response
        if not llm_response.get("choices") or not llm_response["choices"]:
            raise HTTPException(status_code=500, detail="No response from LLM")
        
        # Persist conversation if user is authenticated
        if user:
            conv_repo = ConversationRepository(db)
            msg_repo = MessageRepository(db)
            
            # Create or get conversation (simplified - could track conversation_id in session)
            conversation_data = {
                "user_id": str(user.user_id),
                "title": request.messages[0].content[:100] if request.messages else "Chat",
                "metadata": {"persona_mode": mode.value}
            }
            conversation = await conv_repo.create_conversation(conversation_data)
            
            # Save user messages
            for msg in request.messages:
                if msg.role == "user":
                    await msg_repo.create_message({
                        "conversation_id": str(conversation.id),
                        "role": msg.role,
                        "content": msg.content,
                        "metadata": {}
                    })
            
            # Save assistant response
            if llm_response["choices"]:
                assistant_msg = llm_response["choices"][0].get("message", {})
                if assistant_msg:
                    await msg_repo.create_message({
                        "conversation_id": str(conversation.id),
                        "role": "assistant",
                        "content": assistant_msg.get("content", ""),
                        "metadata": {"model": request.model or settings.OPENAI_MODEL}
                    })
        
        # Create interaction receipt for transparency
        receipt_id = await persona_manager.create_interaction_receipt(
            "chat",
            {
                "mode": mode.value,
                "user": user.username if user else "anonymous",
                "message_count": len(request.messages),
                "model": request.model or settings.OPENAI_MODEL
            }
        )
        
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
                    "content": fallback_response
                },
                "finish_reason": "stop"
            }],
            usage={
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        )

@router.get("/models")
async def list_models(
    user: AuthUser = Depends(get_current_user if settings.AUTH_REQUIRED else get_optional_user)
):
    """
    List available models
    Endpoint for compatibility with OpenAI clients
    """
    return {
        "object": "list",
        "data": [
            {
                "id": settings.OPENAI_MODEL,
                "object": "model",
                "created": 1677649963,
                "owned_by": "mnemosyne",
                "permission": [],
                "root": settings.OPENAI_MODEL,
                "parent": None
            }
        ]
    }

@router.get("/persona/modes")
async def get_persona_modes():
    """
    Get available persona modes
    """
    return {
        "modes": [
            {
                "name": "confidant",
                "description": "Deep listener with empathic presence",
                "focus": "Understanding and validation"
            },
            {
                "name": "mentor",
                "description": "Guide for skill development and mastery",
                "focus": "Learning and growth"
            },
            {
                "name": "mediator",
                "description": "Navigator of conflicts with neutrality",
                "focus": "Resolution and understanding"
            },
            {
                "name": "guardian",
                "description": "Protector of wellbeing and safety",
                "focus": "Security and protection"
            }
        ]
    }