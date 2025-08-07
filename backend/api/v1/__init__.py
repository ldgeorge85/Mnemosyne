"""
API v1 router configuration
"""

from fastapi import APIRouter

from .auth import router as auth_router
from .memories import router as memories_router
from .chat import router as chat_router
from .agents import router as agents_router
from .signals import router as signals_router
from .collective import router as collective_router
from .webhooks import router as webhooks_router

api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(memories_router, prefix="/memories", tags=["memories"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_router.include_router(agents_router, prefix="/agents", tags=["agents"])
api_router.include_router(signals_router, prefix="/signals", tags=["signals"])
api_router.include_router(collective_router, prefix="/collective", tags=["collective"])
api_router.include_router(webhooks_router, prefix="/webhooks", tags=["webhooks"])