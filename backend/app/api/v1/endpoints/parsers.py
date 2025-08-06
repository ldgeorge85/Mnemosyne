"""
Response Parser API endpoints.

This module provides API endpoints for parsing structured outputs from LLMs,
demonstrating the response parsing functionality.
"""
from typing import Dict, List, Any, Optional, Type
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, create_model

from app.api.dependencies.db import get_db
from app.api.dependencies.auth import get_current_user
from app.services.llm import (
    ResponseParser, StructuredOutputParser, ResponseParsingResult,
    OpenAIClient, LLMConfig
)


router = APIRouter()


class ParseRequest(BaseModel):
    """Schema for a parsing request."""
    text: str = Field(..., description="Text to parse")
    schema: Dict[str, Any] = Field(..., description="JSON schema to parse into")


class StructuredOutputRequest(BaseModel):
    """Schema for a structured output request."""
    prompt: str = Field(..., description="Prompt to send to the LLM")
    schema: Dict[str, Any] = Field(..., description="Expected output schema")
    model: Optional[str] = Field(None, description="Model to use")
    temperature: Optional[float] = Field(0.7, description="Temperature for sampling")


class ParseResponse(BaseModel):
    """Schema for a parsing response."""
    success: bool = Field(..., description="Whether parsing succeeded")
    data: Optional[Dict[str, Any]] = Field(None, description="Parsed data")
    error_message: Optional[str] = Field(None, description="Error message if parsing failed")
    original_text: str = Field(..., description="Original text that was parsed")


@router.post("/parse", response_model=ParseResponse)
async def parse_structured_output(
    request: ParseRequest,
    db = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ParseResponse:
    """
    Parse structured output from text using a provided schema.
    
    Args:
        request: Parsing request with text and schema
        db: Database session
        current_user_id: ID of the authenticated user
        
    Returns:
        Parsing result
    """
    try:
        # Create a dynamic model from the schema
        model_name = "DynamicModel"
        dynamic_model = create_model(
            model_name,
            **{k: (v.get('type', Any), Field(...)) for k, v in request.schema.items()}
        )
        
        # Parse the text
        result = ResponseParser.parse_json_to_model(request.text, dynamic_model)
        
        return ParseResponse(
            success=result.is_success,
            data=result.parsed_data.dict() if result.parsed_data else None,
            error_message=result.error_message,
            original_text=result.original_response
        )
        
    except Exception as e:
        return ParseResponse(
            success=False,
            error_message=f"Error during parsing: {str(e)}",
            original_text=request.text
        )


@router.post("/generate-structured", response_model=ParseResponse)
async def generate_structured_output(
    request: StructuredOutputRequest,
    db = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ParseResponse:
    """
    Generate structured output from a prompt using an LLM.
    
    Args:
        request: Structured output request
        db: Database session
        current_user_id: ID of the authenticated user
        
    Returns:
        Generated and parsed result
    """
    try:
        # Create a dynamic model from the schema
        model_name = "DynamicModel"
        dynamic_model = create_model(
            model_name,
            **{k: (v.get('type', Any), Field(...)) for k, v in request.schema.items()}
        )
        
        # Create a parser for the model
        parser = StructuredOutputParser(dynamic_model)
        
        # Add format instructions to the prompt
        formatted_prompt = (
            f"{request.prompt}\n\n"
            f"{parser.get_format_instructions()}"
        )
        
        # Create OpenAI client
        client = OpenAIClient()
        
        # Generate response
        response = await client.chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful AI that provides structured outputs in JSON format."},
                {"role": "user", "content": formatted_prompt}
            ],
            model=request.model,
            temperature=request.temperature,
            stream=False
        )
        
        # Parse the response
        result = parser.parse(response)
        
        return ParseResponse(
            success=result.is_success,
            data=result.parsed_data.dict() if result.parsed_data else None,
            error_message=result.error_message,
            original_text=result.original_response
        )
        
    except Exception as e:
        return ParseResponse(
            success=False,
            error_message=f"Error generating or parsing: {str(e)}",
            original_text=""
        )
