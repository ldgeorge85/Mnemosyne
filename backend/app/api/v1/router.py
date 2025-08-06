"""
API Router Configuration

This module defines the main API router and includes all route handlers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health, conversations, conversation_context, message_handling, streaming, memories, llm, openai, prompts, parsers, functions, memory_retrieval, memory_management, memory_scoring, memory_extraction, chat_enhanced, agents, auth, tasks, task_schedules, recurring_tasks
from app.core.config import settings

# Create the main API router
api_router = APIRouter(prefix=settings.API_PREFIX)

# Include the health router
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Include the conversations router
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])

# Include the conversation context router
api_router.include_router(conversation_context.router, prefix="/conversations", tags=["conversation-context"])

# Include the message handling router
api_router.include_router(message_handling.router, prefix="/messages", tags=["messages"])

# Include the streaming router
api_router.include_router(streaming.router, prefix="/streaming", tags=["streaming"])

# Include the Enhanced Chat router
api_router.include_router(chat_enhanced.router, prefix="/chat-enhanced", tags=["enhanced-chat"])

# Include the memories router
api_router.include_router(memories.router, prefix="/memories", tags=["memories"])

# Include the agents router
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])

# Include the LLM router
api_router.include_router(llm.router, prefix="/llm", tags=["llm"])

# Include the OpenAI router
api_router.include_router(openai.router, prefix="/openai", tags=["openai"])

# Include the Prompts router
api_router.include_router(prompts.router, prefix="/prompts", tags=["prompts"])

# Include the Parsers router
api_router.include_router(parsers.router, prefix="/parsers", tags=["parsers"])

# Include the Functions router
api_router.include_router(functions.router, prefix="/functions", tags=["functions"])

# Include the Memory Retrieval router
api_router.include_router(memory_retrieval.router, prefix="/memory-retrieval", tags=["memory-retrieval"])

# Include the Memory Management router
api_router.include_router(memory_management.router, prefix="/memory-management", tags=["memory-management"])

# Include the Memory Scoring router
api_router.include_router(memory_scoring.router, prefix="/memory-scoring", tags=["memory-scoring"])

# Include the Memory Extraction router
api_router.include_router(memory_extraction.router, prefix="/memory-extraction", tags=["memory-extraction"])

# Include the Tasks router
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])

# Include the Task Schedules router
api_router.include_router(task_schedules.router, prefix="/task-schedules", tags=["task-schedules"])

# Include the Recurring Tasks router
api_router.include_router(recurring_tasks.router, prefix="/recurring-tasks", tags=["recurring-tasks"])

# Include the Authentication router
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Additional routers will be added as they are implemented
# Examples:
# from app.api.v1.endpoints import items, users
# api_router.include_router(items.router, prefix="/items", tags=["items"])
# api_router.include_router(users.router, prefix="/users", tags=["users"])
