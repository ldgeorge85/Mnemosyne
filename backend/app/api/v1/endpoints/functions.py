"""
Function Calling API endpoints.

This module provides API endpoints for LLM function calling capabilities,
allowing agents to call functions defined in the system.
"""
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.dependencies.db import get_db
from app.api.dependencies.auth import get_current_user
from app.services.llm import OpenAIClient
from app.services.llm.function_calling import (
    function_registry, ToolExecutor, FunctionCallMode
)


router = APIRouter()


class FunctionListResponse(BaseModel):
    """Schema for listing available functions."""
    functions: List[Dict[str, Any]] = Field(..., description="Available function definitions")


class FunctionCallRequest(BaseModel):
    """Schema for a function call request."""
    messages: List[Dict[str, str]] = Field(..., description="Conversation messages")
    available_functions: Optional[List[str]] = Field(None, description="Names of available functions")
    model: Optional[str] = Field(None, description="Model to use")
    system_prompt: Optional[str] = Field(None, description="System prompt to use")
    mode: str = Field("auto", description="Function calling mode (auto, none, required)")


class FunctionCallResponse(BaseModel):
    """Schema for a function call response."""
    messages: List[Dict[str, Any]] = Field(..., description="Updated conversation messages")
    function_calls: List[Dict[str, Any]] = Field(default_factory=list, description="Function calls that were made")
    truncated: bool = Field(False, description="Whether the conversation was truncated")


@router.get("/", response_model=FunctionListResponse)
async def list_functions(
    db = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> FunctionListResponse:
    """
    List all available functions that can be called by LLMs.
    
    Args:
        db: Database session
        current_user_id: ID of the authenticated user
        
    Returns:
        List of function definitions
    """
    functions = function_registry.get_openai_schema()
    return FunctionListResponse(functions=functions)


@router.post("/call", response_model=FunctionCallResponse)
async def call_functions(
    request: FunctionCallRequest,
    db = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> FunctionCallResponse:
    """
    Call functions using an LLM.
    
    Args:
        request: Function call request
        db: Database session
        current_user_id: ID of the authenticated user
        
    Returns:
        Result of the function calls
    """
    # Create OpenAI client
    client = OpenAIClient()
    
    # Create tool executor
    executor = ToolExecutor(registry=function_registry)
    
    try:
        # Parse mode
        if request.mode == "auto":
            mode = FunctionCallMode.AUTO
        elif request.mode == "none":
            mode = FunctionCallMode.NONE
        elif request.mode == "required":
            mode = FunctionCallMode.REQUIRED
        else:
            mode = FunctionCallMode.AUTO
        
        # Run conversation
        result = await executor.run_conversation(
            openai_client=client,
            messages=request.messages,
            available_functions=request.available_functions,
            system_prompt=request.system_prompt,
            model=request.model,
            max_turns=5
        )
        
        return FunctionCallResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calling functions: {str(e)}"
        )
