"""
Custom Exception Classes and Handlers

This module provides custom exception classes and error handlers
for consistent error responses across the application.
"""
from datetime import datetime
from typing import Any, Dict, Optional, Union
from uuid import uuid4

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Error detail model for consistent error responses."""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: str
    timestamp: str


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: ErrorDetail


class BaseAPIException(HTTPException):
    """Base exception class for all API exceptions."""
    
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(status_code=status_code, detail=message, headers=headers)
        self.code = code
        self.message = message
        self.details = details


class ValidationError(BaseAPIException):
    """Raised when request validation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="VALIDATION_ERROR",
            message=message,
            details=details,
        )


class AuthenticationError(BaseAPIException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="AUTHENTICATION_ERROR",
            message=message,
            details=details,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(BaseAPIException):
    """Raised when user lacks permissions."""
    
    def __init__(self, message: str = "Insufficient permissions", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="AUTHORIZATION_ERROR",
            message=message,
            details=details,
        )


class NotFoundError(BaseAPIException):
    """Raised when a resource is not found."""
    
    def __init__(self, resource: str, identifier: Union[str, int], details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            message=f"{resource} with identifier '{identifier}' not found",
            details=details,
        )


class ConflictError(BaseAPIException):
    """Raised when there's a conflict with existing data."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code="CONFLICT",
            message=message,
            details=details,
        )


class RateLimitError(BaseAPIException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code="RATE_LIMIT_EXCEEDED",
            message=message,
            details=details,
        )


class ExternalServiceError(BaseAPIException):
    """Raised when an external service fails."""
    
    def __init__(self, service: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code="EXTERNAL_SERVICE_ERROR",
            message=f"External service '{service}' error: {message}",
            details=details,
        )


class InternalServerError(BaseAPIException):
    """Raised for unexpected server errors."""
    
    def __init__(self, message: str = "An unexpected error occurred", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="INTERNAL_SERVER_ERROR",
            message=message,
            details=details,
        )


async def api_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """
    Handle all BaseAPIException instances.
    
    Args:
        request: The request that caused the exception
        exc: The exception instance
        
    Returns:
        JSONResponse with error details
    """
    request_id = request.state.request_id if hasattr(request.state, "request_id") else str(uuid4())
    
    error_response = ErrorResponse(
        error=ErrorDetail(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=request_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict(),
        headers=exc.headers,
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle standard HTTPException instances.
    
    Args:
        request: The request that caused the exception
        exc: The HTTPException instance
        
    Returns:
        JSONResponse with error details
    """
    request_id = request.state.request_id if hasattr(request.state, "request_id") else str(uuid4())
    
    # Map status codes to error codes
    status_to_code = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_SERVER_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
        504: "GATEWAY_TIMEOUT",
    }
    
    error_code = status_to_code.get(exc.status_code, "UNKNOWN_ERROR")
    
    error_response = ErrorResponse(
        error=ErrorDetail(
            code=error_code,
            message=str(exc.detail),
            details=None,
            request_id=request_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict(),
        headers=getattr(exc, "headers", None),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle all unhandled exceptions.
    
    Args:
        request: The request that caused the exception
        exc: The exception instance
        
    Returns:
        JSONResponse with error details
    """
    request_id = request.state.request_id if hasattr(request.state, "request_id") else str(uuid4())
    
    error_response = ErrorResponse(
        error=ErrorDetail(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            details={"type": type(exc).__name__},
            request_id=request_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.dict(),
    )