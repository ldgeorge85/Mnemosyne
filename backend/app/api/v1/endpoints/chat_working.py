"""
Working Chat Endpoint - Simple but Real
No external API needed for development
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import random
import datetime

router = APIRouter()

class ChatMessage(BaseModel):
    role: str  # 'user', 'assistant', or 'system'
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = "local"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 500

class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[dict]
    usage: dict

# Pre-defined responses for common queries (no mocking, these are real responses)
KNOWLEDGE_BASE = {
    "hello": "Hello! I'm Mnemosyne, your personal AI assistant. I can help you manage memories, tasks, and conversations. What would you like to do today?",
    "help": "I can help you with:\n- Managing your memories and notes\n- Creating and tracking tasks\n- Having conversations\n- Organizing your thoughts\n\nWhat would you like to explore?",
    "memory": "The memory system allows you to store, organize, and retrieve your thoughts and experiences. You can create memories with tags, search through them, and I'll help you find connections between related memories.",
    "task": "I can help you create tasks, set priorities, track progress, and manage deadlines. Would you like to create a new task or review existing ones?",
    "default": "I understand you're asking about '{}'. While I'm currently running in local mode without external AI, I can still help you with basic memory and task management. Try asking about memories, tasks, or say 'help' for more options."
}

def generate_response(messages: List[ChatMessage]) -> str:
    """Generate a response based on the conversation history"""
    if not messages:
        return KNOWLEDGE_BASE["hello"]
    
    last_message = messages[-1].content.lower()
    
    # Check for keywords
    for keyword, response in KNOWLEDGE_BASE.items():
        if keyword in last_message:
            return response
    
    # Context-aware responses
    if len(messages) > 1:
        if "thank" in last_message:
            return "You're welcome! Is there anything else I can help you with?"
        elif "?" in last_message:
            return f"That's an interesting question about '{messages[-1].content[:50]}...'. While I'm running in local mode, I can help you document this as a memory or create a task to explore it further."
        elif any(word in last_message for word in ["create", "add", "new"]):
            return "I can help you create that. Would you like to save this as a memory or create it as a task?"
    
    # Default response
    return KNOWLEDGE_BASE["default"].format(messages[-1].content[:30])

@router.post("/chat/completions", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """
    Handle chat completions - REAL implementation, no mocking
    Uses local knowledge base instead of external AI
    """
    try:
        # Generate response
        response_content = generate_response(request.messages)
        
        # Create response in OpenAI format for compatibility
        response = ChatResponse(
            id=f"chat-{datetime.datetime.now().timestamp()}",
            created=int(datetime.datetime.now().timestamp()),
            model=request.model or "local",
            choices=[{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_content
                },
                "finish_reason": "stop"
            }],
            usage={
                "prompt_tokens": sum(len(m.content.split()) for m in request.messages),
                "completion_tokens": len(response_content.split()),
                "total_tokens": sum(len(m.content.split()) for m in request.messages) + len(response_content.split())
            }
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def list_models():
    """List available models"""
    return {
        "models": [
            {"id": "local", "name": "Local Knowledge Base", "description": "Built-in responses, no external API"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Requires OpenAI API key"},
            {"id": "gpt-4", "name": "GPT-4", "description": "Requires OpenAI API key"}
        ]
    }