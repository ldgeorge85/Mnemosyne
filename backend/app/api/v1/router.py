"""
API Router Configuration

This module defines the main API router and includes all route handlers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health, memories, agents, tasks, task_schedules, recurring_tasks, simple_auth
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
from app.api.v1.endpoints import chat_llm
api_router.include_router(chat_llm.router, prefix="/chat", tags=["chat"])


# Include the Tasks router
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])

# Include the Task Schedules router
api_router.include_router(task_schedules.router, prefix="/task-schedules", tags=["task-schedules"])

# Include the Recurring Tasks router
api_router.include_router(recurring_tasks.router, prefix="/recurring-tasks", tags=["recurring-tasks"])

# Include the Authentication router
api_router.include_router(simple_auth.router, prefix="/auth", tags=["auth"])

# Additional routers will be added as they are implemented
# Examples:
# from app.api.v1.endpoints import items, users
# api_router.include_router(items.router, prefix="/items", tags=["items"])
# api_router.include_router(users.router, prefix="/users", tags=["users"])
