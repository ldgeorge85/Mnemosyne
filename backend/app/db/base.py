"""
Database Base Import Module

This module imports all models to ensure they're registered with SQLAlchemy's
declarative base. It should be imported by Alembic to ensure all models are
discovered for migrations.
"""

# Import Base and BaseModel
from app.db.session import Base  # noqa
from app.db.base_model import BaseModel  # noqa

# Import all models here
# This ensures all models are registered with the declarative base for migrations

# As new models are created, add imports for them below:
from app.db.models.user import User, APIKey, UserSession  # noqa
from app.db.models.memory import Memory, MemoryChunk  # noqa
from app.db.models.conversation import Conversation, Message  # noqa
from app.db.models.task import Task, TaskLog  # noqa
from app.db.models.task_schedule import TaskSchedule  # noqa
from app.db.models.agent import Agent, AgentLink, AgentLog, MemoryReflection  # noqa
