"""
Task schedule schemas for the Mnemosyne application.

This module defines the Pydantic models for validating and serializing task schedule data.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class TaskScheduleBase(BaseModel):
    """Base schema for task schedule with common attributes."""
    
    start_time: Optional[datetime] = None
    due_time: datetime
    timezone: str = "UTC"
    is_all_day: bool = False
    duration_minutes: Optional[int] = None
    recurrence_pattern: Optional[str] = None
    recurrence_count: Optional[int] = None
    recurrence_end_date: Optional[datetime] = None


class TaskScheduleCreate(TaskScheduleBase):
    """Schema for creating a new task schedule."""
    
    task_id: UUID


class TaskScheduleUpdate(BaseModel):
    """Schema for updating an existing task schedule."""
    
    start_time: Optional[datetime] = None
    due_time: Optional[datetime] = None
    timezone: Optional[str] = None
    is_all_day: Optional[bool] = None
    duration_minutes: Optional[int] = None
    recurrence_pattern: Optional[str] = None
    recurrence_count: Optional[int] = None
    recurrence_end_date: Optional[datetime] = None


class TaskScheduleInDBBase(TaskScheduleBase):
    """Base schema for task schedule stored in database."""
    
    id: UUID
    task_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic config."""
        
        orm_mode = True


class TaskSchedule(TaskScheduleInDBBase):
    """Schema for task schedule response."""
    
    pass


class TaskScheduleWithConflicts(TaskSchedule):
    """Schema for task schedule with conflict information."""
    
    conflicts: List[UUID] = Field(default_factory=list, description="List of conflicting task IDs")
