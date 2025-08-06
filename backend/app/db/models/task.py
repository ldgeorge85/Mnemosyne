"""
Task data models for the Mnemosyne application.

This module defines the SQLAlchemy ORM models for storing and 
retrieving task data, including task status, priority, and relationships.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Text,
    Boolean,
    JSON,
    Index,
    Enum
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base_model import BaseModel


class TaskStatus(str, enum.Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    """Task priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(BaseModel):
    """
    Task model for storing user tasks with status, priority, and relationships.
    
    This model represents a task entry in the system, which includes
    title, description, status, priority, and relationships to users and agents.
    """
    __tablename__ = "tasks"
    
    # Core task fields
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Task metadata
    tags = Column(ARRAY(String), default=[], nullable=False)
    task_metadata = Column(JSON, default={}, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    parent_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=True)
    
    # Relationships for ORM
    user = relationship("User", back_populates="tasks")
    agent = relationship("Agent", back_populates="tasks")
    subtasks = relationship("Task", 
                            backref="parent_task",
                            remote_side="Task.id",
                            cascade="all, delete-orphan",
                            single_parent=True)
    task_logs = relationship("TaskLog", back_populates="task", cascade="all, delete-orphan")
    schedule = relationship("TaskSchedule", back_populates="task", uselist=False, cascade="all, delete-orphan")


class TaskLog(BaseModel):
    """
    TaskLog model for storing task activity logs.
    
    This model represents a log entry for a task, recording status changes,
    progress updates, and other important events.
    """
    __tablename__ = "task_logs"
    
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    message = Column(Text, nullable=False)
    log_type = Column(String(50), nullable=False)  # e.g., "status_change", "progress_update", "error"
    task_metadata = Column(JSON, default={}, nullable=False)
    
    # Relationships for ORM
    task = relationship("Task", back_populates="task_logs")
