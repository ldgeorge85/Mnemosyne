"""
API Router Configuration

This module defines the main API router and includes all route handlers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health
from app.core.config import settings

# Create the main API router
api_router = APIRouter(prefix=settings.API_PREFIX)

# Include the health router
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Additional routers will be added as they are implemented
# Examples:
# from app.api.v1.endpoints import items, users
# api_router.include_router(items.router, prefix="/items", tags=["items"])
# api_router.include_router(users.router, prefix="/users", tags=["users"])
