"""
Message Handling API Endpoints

This module defines API endpoints for the message handling system,
including message processing, validation, and formatting operations.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.db import get_db
from app.api.dependencies.auth import get_current_user
from app.services.conversation import (
    MessageHandler,
    MessageFormatter,
    MessageValidationError,
    MessageFormatError
)

# Pydantic models for request and response
from pydantic import BaseModel, Field


class MessageContent(BaseModel):
    """Schema for message content"""
    content: str = Field(..., min_length=1, max_length=10000)
    role: str = Field("user", pattern="^(user|system)$")


class MessageProcessRequest(BaseModel):
    """Schema for message processing request"""
    conversation_id: str
    content: str = Field(..., min_length=1, max_length=10000)
    role: str = Field("user", pattern="^(user|system)$")


class MessageProcessResponse(BaseModel):
    """Schema for message processing response"""
    id: str
    conversation_id: str
    content: str
    role: str
    created_at: str
    metadata: Optional[Dict[str, Any]] = None
    assistant_response: Optional[Dict[str, Any]] = None


class MessageValidationRequest(BaseModel):
    """Schema for message validation request"""
    content: str
    role: str = Field("user", pattern="^(user|system|assistant)$")


class MessageValidationResponse(BaseModel):
    """Schema for message validation response"""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    formatted_content: Optional[str] = None


class MessageFormatRequest(BaseModel):
    """Schema for message format request"""
    content: str
    user_id: Optional[str] = None
    type: str = Field("user", pattern="^(user|system|assistant)$")


class MessageFormatResponse(BaseModel):
    """Schema for message format response"""
    formatted_message: Dict[str, Any]
    metadata: Dict[str, Any] = {}
    extracted_urls: List[str] = []
    extracted_emails: List[str] = []
    is_command: bool = False
    command: Optional[str] = None
    command_args: Optional[str] = None


# Create router
router = APIRouter()


@router.post("/process", response_model=MessageProcessResponse)
async def process_message(
    request: MessageProcessRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Process a message using the message handling system.
    This validates, formats, and creates a new message.
    """
    try:
        # Initialize the message handler
        message_handler = MessageHandler(db)
        
        # Prepare message data
        message_data = {
            "conversation_id": request.conversation_id,
            "content": request.content,
            "role": request.role,
            "user_id": current_user["id"]
        }
        
        # Create the message
        message = await message_handler.create_message(message_data)
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create message"
            )
        
        # Convert to dictionary and return
        result = message.to_dict()
        
        # For now, we don't have assistant responses, so set to None
        result["assistant_response"] = None
        
        return result
    except MessageValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@router.post("/validate", response_model=MessageValidationResponse)
async def validate_message(
    request: MessageValidationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Validate a message without creating it.
    This is useful for client-side validation.
    """
    # Initialize services
    message_formatter = MessageFormatter()
    
    errors = []
    warnings = []
    formatted_content = None
    
    try:
        # Try to format the content
        formatted_content = message_formatter.format_message_content(request.content)
        
        # Check for potential issues
        if len(request.content) > 1000:
            warnings.append("Message is quite long. Consider breaking it into smaller messages.")
        
        # Check URLs
        urls = message_formatter.extract_urls(request.content)
        if urls and request.role == "system":
            warnings.append("System messages with URLs should be reviewed carefully.")
        
        # Check commands
        command = message_formatter.parse_command(request.content)
        if command and request.role != "user":
            errors.append("Commands can only be used in user messages.")
        
        # Success!
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "formatted_content": formatted_content
        }
    except MessageFormatError as e:
        return {
            "is_valid": False,
            "errors": [str(e)],
            "warnings": warnings,
            "formatted_content": None
        }


@router.post("/format", response_model=MessageFormatResponse)
async def format_message(
    request: MessageFormatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Format a message according to its type (user, system, assistant).
    This extracts metadata, formats content, and returns a consistent format.
    """
    try:
        # Initialize services
        message_formatter = MessageFormatter()
        
        # Format based on message type
        if request.type == "user":
            formatted = message_formatter.format_user_message(
                request.content,
                request.user_id or current_user["id"]
            )
        elif request.type == "system":
            formatted = message_formatter.format_system_message(request.content)
        elif request.type == "assistant":
            formatted = message_formatter.format_assistant_message(request.content)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid message type: {request.type}"
            )
        
        # Extract metadata
        urls = message_formatter.extract_urls(request.content)
        emails = message_formatter.extract_emails(request.content)
        command = message_formatter.parse_command(request.content)
        
        # Build response
        return {
            "formatted_message": formatted,
            "metadata": formatted.get("metadata", {}),
            "extracted_urls": urls,
            "extracted_emails": emails,
            "is_command": command is not None,
            "command": command[0] if command else None,
            "command_args": command[1] if command else None
        }
    except MessageFormatError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error formatting message: {str(e)}"
        )
