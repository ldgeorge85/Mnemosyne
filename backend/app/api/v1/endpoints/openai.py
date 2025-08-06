"""
OpenAI API endpoints.

This module provides API endpoints for direct interactions with OpenAI's services,
including embeddings generation, moderation, and additional OpenAI-specific features.
"""
from typing import List, Dict, Any, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, validator

from app.core.config import settings
from app.api.dependencies.db import get_db
from app.api.dependencies.auth import get_current_user
from app.services.llm import OpenAIClient


router = APIRouter()


class EmbeddingRequest(BaseModel):
    """Schema for an embedding request."""
    text: Union[str, List[str]] = Field(..., description="Text(s) to embed")
    model: str = Field("text-embedding-ada-002", description="Model to use for embeddings")


class EmbeddingResponse(BaseModel):
    """Schema for an embedding response."""
    embeddings: List[List[float]] = Field(..., description="Generated embedding vectors")
    model: str = Field(..., description="Model used for generation")
    token_count_estimate: int = Field(..., description="Estimated token count")
    
    @validator("token_count_estimate", pre=True)
    def estimate_tokens(cls, v, values):
        """Estimate token count if not provided."""
        if v is not None:
            return v
        
        # If token count not provided, estimate it from the embeddings
        text = values.get("text", "")
        if isinstance(text, str):
            return len(text) // 4  # Rough estimate: 4 chars ~= 1 token
        elif isinstance(text, list):
            return sum(len(t) // 4 for t in text)
        return 0


class ModerationRequest(BaseModel):
    """Schema for a moderation request."""
    text: Union[str, List[str]] = Field(..., description="Text(s) to check")
    model: str = Field("text-moderation-latest", description="Moderation model to use")


class ModerationResponse(BaseModel):
    """Schema for a moderation response."""
    results: List[Dict[str, Any]] = Field(..., description="Moderation results")
    flagged: bool = Field(..., description="Whether any content was flagged")


class TestConnectionRequest(BaseModel):
    """Schema for testing OpenAI connection."""
    message: str = Field("Hello, this is a test message", description="Test message to send")


class TestConnectionResponse(BaseModel):
    """Schema for test connection response."""
    success: bool = Field(..., description="Whether the connection test was successful")
    response: Optional[str] = Field(None, description="Response from OpenAI")
    model_used: str = Field(..., description="Model used for the test")
    error: Optional[str] = Field(None, description="Error message if any")


@router.post("/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(
    request: EmbeddingRequest,
    db = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> EmbeddingResponse:
    """
    Generate embeddings for text using OpenAI's API.
    
    Args:
        request: Embedding request
        db: Database session
        current_user_id: ID of the authenticated user
        
    Returns:
        Generated embedding vectors
    """
    # Validate OpenAI API key
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API is not properly configured"
        )
    
    # Create OpenAI client
    client = OpenAIClient()
    
    try:
        # Generate embeddings
        embeddings = await client.embeddings(
            text=request.text,
            model=request.model
        )
        
        # Estimate token count
        if isinstance(request.text, str):
            token_count_estimate = len(request.text) // 4
        else:
            token_count_estimate = sum(len(t) // 4 for t in request.text)
        
        return EmbeddingResponse(
            embeddings=embeddings,
            model=request.model,
            token_count_estimate=token_count_estimate
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating embeddings: {str(e)}"
        )


@router.post("/moderation", response_model=ModerationResponse)
async def check_moderation(
    request: ModerationRequest,
    db = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ModerationResponse:
    """
    Check content against OpenAI's moderation endpoint.
    
    Args:
        request: Moderation request
        db: Database session
        current_user_id: ID of the authenticated user
        
    Returns:
        Moderation results
    """
    # Validate OpenAI API key
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API is not properly configured"
        )
    
    # Create OpenAI client
    client = OpenAIClient()
    
    try:
        # Check moderation
        response = await client.moderation(
            text=request.text,
            model=request.model
        )
        
        # Extract results
        results = response.get('results', [])
        flagged = any(result.get('flagged', False) for result in results)
        
        return ModerationResponse(
            results=results,
            flagged=flagged
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking moderation: {str(e)}"
        )


@router.post("/test-connection", response_model=TestConnectionResponse)
async def test_openai_connection(
    request: TestConnectionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> TestConnectionResponse:
    """
    Test the OpenAI API connection.
    
    Args:
        request: Test connection request
        current_user: Authenticated user
        
    Returns:
        Test connection results
    """
    try:
        client = OpenAIClient()
        
        # Simple test message
        messages = [
            {"role": "user", "content": request.message}
        ]
        
        response = await client.chat_completion(
            messages=messages,
            max_tokens=50
        )
        
        return TestConnectionResponse(
            success=True,
            response=response,
            model_used=client.model_name,
            error=None
        )
        
    except Exception as e:
        return TestConnectionResponse(
            success=False,
            response=None,
            model_used=settings.OPENAI_MODEL,
            error=str(e)
        )
