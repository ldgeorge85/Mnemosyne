"""
Mnemosyne FastAPI Application

This module contains the main FastAPI application instance and configuration.
It sets up the API routes, middleware, and other components required for the application.
"""

import time
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.docs import setup_docs
from app.core.logging import configure_logging, get_logger

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
    response = await call_next(request)
    process_time = time.time() - start_time
    
    log_dict = {
        "method": request.method,
        "path": request.url.path,
        "client": request.client.host if request.client else None,
        "processing_time": f"{process_time:.4f}s"
    }
    
    logger.info(f"Request processed", extra=log_dict)
    
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        dict: A simple health status message
    """
    return {"status": "healthy", "service": settings.APP_NAME}

# Version endpoint
@app.get("/version")
async def version():
    """
    Version endpoint to get the current API version.
    
    Returns:
        dict: The current version information
    """
    return {"version": app.version}

# Error handlers
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for all unhandled exceptions.
    
    Args:
        request: The request that caused the exception
        exc: The exception raised
        
    Returns:
        JSONResponse: A JSON response with error details
    """
    logger.exception(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

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
    # Initialize database connections, etc.

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
