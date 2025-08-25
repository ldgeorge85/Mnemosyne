"""
Database Models

This package contains SQLAlchemy models representing database tables and relationships.
"""

# Import the Base from session to ensure all models use the same declarative base
from app.db.session import Base  # noqa

# Import all models here so they can be discovered by SQLAlchemy
from app.db.models.user import User  # noqa
from app.db.models.conversation import Conversation, Message  # noqa
from app.db.models.memory import Memory, MemoryChunk  # noqa
from app.db.models.agent import Agent, AgentLink, AgentLog, MemoryReflection  # noqa
from app.db.models.task import Task, TaskLog, TaskStatus, TaskPriority, QuestType  # noqa
from app.db.models.task_schedule import TaskSchedule  # noqa
from app.db.models.receipt import Receipt, ReceiptType  # noqa
