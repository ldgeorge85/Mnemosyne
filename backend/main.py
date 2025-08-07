"""
Main FastAPI application for Mnemosyne Protocol
"""

from contextlib import asynccontextmanager
from typing import Any
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
import logging

from backend.api.v1 import api_router
from backend.core.config import get_settings
from backend.core.database import init_db
from backend.middleware.security import setup_middleware
from backend.core.redis_client import RedisClient
from backend.core.vectors import VectorStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle
    """
    # Startup
    logger.info("Starting Mnemosyne Protocol API...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize Redis
    redis = await RedisClient.get_instance()
    logger.info("Redis connected")
    
    # Initialize vector store
    vector_store = await VectorStore.get_instance()
    logger.info("Vector store initialized")
    
    # Yield control to the application
    yield
    
    # Shutdown
    logger.info("Shutting down Mnemosyne Protocol API...")
    
    # Close Redis connection
    await redis.close()
    
    # Close vector store
    await vector_store.close()
    
    logger.info("Cleanup complete")


# Create FastAPI application
app = FastAPI(
    title="Mnemosyne Protocol API",
    description="Cognitive-symbolic operating system for preserving human agency",
    version="1.0.0",
    docs_url="/docs" if settings.DOCS_ENABLED else None,
    redoc_url="/redoc" if settings.DOCS_ENABLED else None,
    openapi_url="/openapi.json" if settings.DOCS_ENABLED else None,
    lifespan=lifespan
)

# Setup middleware
app = setup_middleware(app)

# Include API router
app.include_router(api_router, prefix="/api/v1")


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check() -> Any:
    """
    Health check endpoint
    """
    try:
        # Check Redis
        redis = await RedisClient.get_instance()
        await redis.client.ping()
        redis_status = "healthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        redis_status = "unhealthy"
    
    try:
        # Check vector store
        vector_store = await VectorStore.get_instance()
        # Assume vector store has a health check method
        vector_status = "healthy"
    except Exception as e:
        logger.error(f"Vector store health check failed: {e}")
        vector_status = "unhealthy"
    
    # Overall health
    overall_status = "healthy" if redis_status == "healthy" and vector_status == "healthy" else "degraded"
    
    return {
        "status": overall_status,
        "version": "1.0.0",
        "services": {
            "redis": redis_status,
            "vector_store": vector_status
        }
    }


# Metrics endpoint (basic)
@app.get("/metrics", tags=["monitoring"])
async def metrics() -> Any:
    """
    Basic metrics endpoint (extend with Prometheus in production)
    """
    return {
        "app": "mnemosyne-protocol",
        "version": "1.0.0",
        "status": "running"
    }


# Root endpoint
@app.get("/")
async def root() -> Any:
    """
    Root endpoint
    """
    return {
        "name": "Mnemosyne Protocol",
        "tagline": "For those who see too much and belong nowhere",
        "version": "1.0.0",
        "status": "active",
        "documentation": "/docs" if settings.DOCS_ENABLED else None
    }


# Custom exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )