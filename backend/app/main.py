"""
Mnemosyne FastAPI Application

This module contains the main FastAPI application instance and configuration.
It sets up the API routes, middleware, and other components required for the application.
"""

import time
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.docs import setup_docs
from app.core.logging import configure_logging, get_logger
from app.core.exceptions import (
    BaseAPIException,
    api_exception_handler,
    http_exception_handler,
    generic_exception_handler,
)
from app.core.middleware import RequestIDMiddleware
from app.core.auth.manager import get_auth_manager
from app.middleware.receipt_enforcement import ReceiptEnforcementMiddleware

# Configure logging
configure_logging()
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="A web-based conversational AI system with advanced memory capabilities",
    version="0.1.0",
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url="/redoc" if settings.APP_ENV != "production" else None,
)

# Add middleware in order (reverse order of execution)
# Request ID middleware (executes first)
app.add_middleware(RequestIDMiddleware)

# Receipt enforcement middleware (sovereignty safeguard)
# Start in non-strict mode, can be made strict once all endpoints have receipts
app.add_middleware(ReceiptEnforcementMiddleware, strict_mode=False)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up custom API documentation
setup_docs(app)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log request information and timing.
    
    Args:
        request: The incoming request
        call_next: The next middleware or route handler
        
    Returns:
        Response: The response from the next middleware or route handler
    """
    start_time = time.time()
    
    # Get request ID from state (set by RequestIDMiddleware)
    request_id = getattr(request.state, "request_id", "unknown")
    
    # Log request start
    logger.info(
        "Request started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else None,
        }
    )
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log request completion
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "processing_time": process_time,
            }
        )
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        
        # Log request failure
        logger.error(
            "Request failed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "error": str(e),
                "processing_time": process_time,
            },
            exc_info=True,
        )
        raise

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        dict: A simple health status message
    """
    return {"status": "healthy", "service": settings.APP_NAME}

# Hot reload test endpoint
@app.get("/hot-reload-test")
async def hot_reload_test():
    """
    Test endpoint to verify hot reload functionality.
    
    Returns:
        dict: A message indicating hot reload is working
    """
    return {"message": "Hot reload is working successfully!", "version": "2"}

# Version endpoint
@app.get("/version")
async def version():
    """
    Version endpoint to get the current API version.
    
    Returns:
        dict: The current version information
    """
    return {"version": app.version}

# Auth endpoints are now handled by the auth router in api/v1/endpoints/auth.py
# Dev-login endpoints have been removed for security

# Exception handlers (order matters - specific to general)
# Handle custom API exceptions
app.add_exception_handler(BaseAPIException, api_exception_handler)

# Handle standard HTTPExceptions
app.add_exception_handler(HTTPException, http_exception_handler)

# Handle all other exceptions
app.add_exception_handler(Exception, generic_exception_handler)

# Include API router
app.include_router(api_router)

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """
    Handler for application startup events.
    Initializes connections and resources needed by the application.
    """
    logger.info(f"Starting {settings.APP_NAME} API")
    
    # Initialize authentication manager
    auth_manager = get_auth_manager()
    available_methods = auth_manager.get_available_methods()
    logger.info(f"Authentication initialized with methods: {available_methods}")
    
    # Database initialization is handled by the session module

@app.on_event("shutdown")
async def shutdown_event():
    """
    Handler for application shutdown events.
    Cleans up resources used by the application.
    """
    logger.info(f"Shutting down {settings.APP_NAME} API")
    # Close database connections, etc.

# Run the application if executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
