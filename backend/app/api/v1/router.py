"""
API Router Configuration

This module defines the main API router and includes all route handlers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health, memories, agents, tasks, task_schedules, recurring_tasks, auth, persona, receipts, trust, negotiations
from app.core.config import settings

# Create the main API router
api_router = APIRouter(prefix=settings.API_PREFIX)

# Include the health router
api_router.include_router(health.router, prefix="/health", tags=["health"])


# Include the memories router
api_router.include_router(memories.router, prefix="/memories", tags=["memories"])

# Include the agents router
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])

# Include the LLM chat router (connected to OpenAI-compatible endpoint)
from app.api.v1.endpoints import chat_llm, chat_stream, chat_agentic
api_router.include_router(chat_llm.router, prefix="/chat", tags=["chat"])
# Include streaming chat endpoints
api_router.include_router(chat_stream.router, tags=["chat"])
# Include agentic chat endpoints (ReAct pattern with parallel execution)
api_router.include_router(chat_agentic.router, tags=["chat", "agentic"])


# Include the Tasks router
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])

# Include the Task Schedules router
api_router.include_router(task_schedules.router, prefix="/task-schedules", tags=["task-schedules"])

# Include the Recurring Tasks router
api_router.include_router(recurring_tasks.router, prefix="/recurring-tasks", tags=["recurring-tasks"])

# Include the Authentication router (using secure AuthManager)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Include the Persona router
api_router.include_router(persona.router, prefix="/persona", tags=["persona"])

# Include the Receipts router
api_router.include_router(receipts.router, prefix="/receipts", tags=["receipts"])

# Include the Trust router (sovereignty safeguards)
api_router.include_router(trust.router, prefix="/trust", tags=["trust"])

# Include the Negotiations router (multi-party binding agreements)
api_router.include_router(negotiations.router, prefix="/negotiations", tags=["negotiations"])

# Additional routers will be added as they are implemented
# Examples:
# from app.api.v1.endpoints import items, users
# api_router.include_router(items.router, prefix="/items", tags=["items"])
# api_router.include_router(users.router, prefix="/users", tags=["users"])
