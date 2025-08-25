"""
Task schemas for the Mnemosyne application.

This module defines Pydantic models for task data validation,
serialization, and deserialization.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from uuid import UUID

from pydantic import BaseModel, Field

from app.db.models.task import TaskStatus, TaskPriority, QuestType
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
    """Enhanced base schema for task data with game mechanics."""
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Time awareness
    estimated_duration_minutes: Optional[int] = None
    
    # Game mechanics
    difficulty: int = Field(default=1, ge=1, le=5)
    quest_type: Optional[QuestType] = None
    
    # Identity shaping (ICV evolution)
    value_impact: Dict[str, float] = Field(default_factory=dict)
    skill_development: Dict[str, Any] = Field(default_factory=dict)
    
    # Privacy and sovereignty
    visibility_mask: str = 'private'
    
    # Collaboration
    is_shared: bool = False
    assignees: List[UUID] = Field(default_factory=list)
    
    # Recurrence
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
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
    """Enhanced schema for task data as stored in the database."""
    id: UUID
    user_id: UUID
    parent_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    is_active: bool
    schedule: Optional[TaskSchedule] = None
    
    # Progress and time tracking
    progress: float = 0.0
    actual_duration_minutes: Optional[int] = None
    
    # Game mechanics calculated fields
    experience_points: int = 0
    
    # Collaboration
    requires_all_complete: bool = False
    
    # Recurrence
    recurring_parent_id: Optional[UUID] = None
    
    # Additional context
    context: Dict[str, Any] = Field(default_factory=dict)

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
    # Game mechanics filters
    quest_type: Optional[List[QuestType]] = None
    min_difficulty: Optional[int] = None
    max_difficulty: Optional[int] = None
    is_shared: Optional[bool] = None


class TaskCompleteRequest(BaseModel):
    """Request schema for completing a task."""
    evidence: Optional[str] = None
    actual_duration_minutes: Optional[int] = None
    reflection: Optional[str] = None


class TaskCompleteResponse(BaseModel):
    """Response after completing a task."""
    task: Union[TaskInDB, Dict[str, Any]]
    experience_gained: int
    achievements_unlocked: List[str] = Field(default_factory=list)
    reputation_changes: Dict[str, float] = Field(default_factory=dict)
    memory_created: Optional[UUID] = None


class TaskStats(BaseModel):
    """Statistics about user's tasks."""
    total_tasks: int = 0
    completed_tasks: int = 0
    in_progress_tasks: int = 0
    overdue_tasks: int = 0
    
    # Game stats
    total_experience: int = 0
    current_streak: int = 0
    tasks_by_quest_type: Dict[str, int] = Field(default_factory=dict)
    
    # Time stats
    total_time_estimated: int = 0
    total_time_actual: int = 0
    average_completion_time: Optional[float] = None
    
    # Performance
    on_time_completion_rate: float = 0.0
    average_difficulty: float = 0.0
