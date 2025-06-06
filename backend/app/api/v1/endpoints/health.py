"""
Health Check Endpoints

This module provides health check endpoints for the API to verify that various
components of the system are working properly.
"""

from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.db import get_async_db
from app.core.config import settings
from app.core.logging import get_logger
from app.db.connection import connection_health_check
from app.db.vector import ensure_extension

# Define Pydantic models for response validation
class HealthResponse(BaseModel):
    """Basic health check response model."""
    status: str
    service: str
    version: str
    environment: str


class ComponentStatus(BaseModel):
    """Status information for a system component."""
    status: str
    message: str


class DetailedHealthResponse(HealthResponse):
    """Detailed health check response with component statuses."""
    components: Dict[str, ComponentStatus]


router = APIRouter()
logger = get_logger(__name__)


@router.get(
    "/",
    summary="Basic health check",
    description="Returns a simple health status to confirm the API is running",
    status_code=status.HTTP_200_OK,
    response_model=HealthResponse,
)
async def health_check() -> HealthResponse:
    """
    Basic health check endpoint that confirms the API is running.
    
    Returns:
        A dictionary with the service name and status
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
    }


@router.get(
    "/detailed",
    summary="Detailed health check",
    description="Performs checks on all system components and returns detailed status",
    status_code=status.HTTP_200_OK,
    response_model=DetailedHealthResponse,
)
async def detailed_health_check(db: AsyncSession = Depends(get_async_db)) -> DetailedHealthResponse:
    """
    Detailed health check that verifies all system components.
    
    Args:
        db: The database session (injected via dependency)
        
    Returns:
        A dictionary with detailed status information for each component
    """
    # Check database connection
    db_status = "healthy"
    db_message = "Database connection successful"
    
    try:
        # Check if we can connect to the database
        db_health = connection_health_check()
        if not db_health:
            db_status = "degraded"
            db_message = "Database connection check failed"
    except Exception as e:
        db_status = "unhealthy"
        db_message = f"Database error: {str(e)}"
        logger.error(f"Health check database error: {str(e)}")
    
    # Check pgvector extension
    vector_status = "healthy"
    vector_message = "pgvector extension enabled"
    
    try:
        # Check if pgvector extension is installed
        extension_enabled = await ensure_extension(db)
        if not extension_enabled:
            vector_status = "degraded"
            vector_message = "pgvector extension not installed"
    except Exception as e:
        vector_status = "unhealthy"
        vector_message = f"pgvector extension error: {str(e)}"
        logger.error(f"Health check pgvector error: {str(e)}")
    
    # Determine overall system status
    components = {
        "database": {
            "status": db_status,
            "message": db_message,
        },
        "vector": {
            "status": vector_status,
            "message": vector_message,
        },
        "api": {
            "status": "healthy",
            "message": "API is running",
        },
    }
    
    statuses = [component["status"] for component in components.values()]
    overall_status = "healthy"
    
    if "unhealthy" in statuses:
        overall_status = "unhealthy"
    elif "degraded" in statuses:
        overall_status = "degraded"
    
    return {
        "status": overall_status,
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "components": components,
    }


@router.get(
    "/readiness",
    summary="Readiness probe",
    description="Checks if the application is ready to receive traffic",
    status_code=status.HTTP_200_OK,
    response_model=HealthResponse,
)
async def readiness_probe() -> HealthResponse:
    """
    Readiness probe for Kubernetes or other orchestration systems.
    
    Returns:
        A dictionary with the readiness status
    """
    return {
        "status": "ready",
        "service": settings.APP_NAME,
    }


@router.get(
    "/liveness",
    summary="Liveness probe",
    description="Checks if the application is alive and running",
    status_code=status.HTTP_200_OK,
    response_model=HealthResponse,
)
async def liveness_probe() -> HealthResponse:
    """
    Liveness probe for Kubernetes or other orchestration systems.
    
    Returns:
        A dictionary with the liveness status
    """
    return {
        "status": "alive",
        "service": settings.APP_NAME,
    }
