"""
API v1 router configuration
"""

from fastapi import APIRouter

from backend.api.v1.auth import router as auth_router
from backend.api.v1.memories import router as memories_router
from backend.api.v1.chat import router as chat_router
from backend.api.v1.agents import router as agents_router
from backend.api.v1.signals import router as signals_router
from backend.api.v1.collective import router as collective_router
from backend.api.v1.webhooks import router as webhooks_router

api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(memories_router, prefix="/memories", tags=["memories"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_router.include_router(agents_router, prefix="/agents", tags=["agents"])
api_router.include_router(signals_router, prefix="/signals", tags=["signals"])
api_router.include_router(collective_router, prefix="/collective", tags=["collective"])
api_router.include_router(webhooks_router, prefix="/webhooks", tags=["webhooks"])