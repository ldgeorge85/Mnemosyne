"""
Task schemas for the Mnemosyne application.

This module defines Pydantic models for task data validation,
serialization, and deserialization.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from uuid import UUID

from pydantic import BaseModel, Field

from app.db.models.task import TaskStatus, TaskPriority
from app.schemas.task_schedule import TaskSchedule


class TaskLogBase(BaseModel):
    """Base schema for task log data."""
    message: str
    log_type: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskLogCreate(TaskLogBase):
    """Schema for creating a new task log."""
    task_id: UUID


class TaskLogUpdate(TaskLogBase):
    """Schema for updating an existing task log."""
    pass


class TaskLogInDB(TaskLogBase):
    """Schema for task log data as stored in the database."""
    id: UUID
    task_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""
        orm_mode = True


class TaskBase(BaseModel):
    """Base schema for task data."""
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    user_id: UUID
    parent_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    agent_id: Optional[UUID] = None


class TaskInDB(TaskBase):
    """Schema for task data as stored in the database."""
    id: UUID
    user_id: UUID
    parent_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    is_active: bool
    schedule: Optional[TaskSchedule] = None

    class Config:
        """Pydantic configuration."""
        orm_mode = True


class TaskWithLogs(TaskInDB):
    """Schema for task data with associated logs."""
    logs: List[TaskLogInDB] = Field(default_factory=list)


class TaskWithSubtasks(TaskInDB):
    """Schema for task data with associated subtasks."""
    subtasks: List["TaskInDB"] = Field(default_factory=list)


# Update forward references for nested models
TaskWithSubtasks.update_forward_refs()


class TaskResponse(BaseModel):
    """Schema for task response data."""
    task: TaskInDB


class TaskListResponse(BaseModel):
    """Schema for task list response data."""
    items: List[TaskInDB]
    total: int


class TaskSearchParams(BaseModel):
    """Schema for task search parameters."""
    user_id: UUID
    status: Optional[List[TaskStatus]] = None
    priority: Optional[List[TaskPriority]] = None
    tags: Optional[List[str]] = None
    due_date_start: Optional[datetime] = None
    due_date_end: Optional[datetime] = None
    search_term: Optional[str] = None
    include_inactive: bool = False
    limit: int = 10
    offset: int = 0
