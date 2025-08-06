"""Task schedule models for the Mnemosyne application."""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, ForeignKey, String, DateTime, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_model import BaseModel


class TaskSchedule(BaseModel):
    """Task schedule model for storing scheduling information for tasks."""
    
    __tablename__ = "task_schedules"
    
    # id is inherited from BaseModel
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime, nullable=True)
    due_time = Column(DateTime, nullable=False)
    timezone = Column(String, nullable=False, default="UTC")
    is_all_day = Column(Boolean, default=False)
    duration_minutes = Column(Integer, nullable=True)
    recurrence_pattern = Column(String, nullable=True)  # For future recurring tasks
    recurrence_count = Column(Integer, nullable=True)  # Number of recurrences
    recurrence_end_date = Column(DateTime, nullable=True)  # End date for recurrences
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    task = relationship("Task", back_populates="schedule")
    
    def __repr__(self) -> str:
        """Return string representation of the task schedule."""
        return f"<TaskSchedule(id={self.id}, task_id={self.task_id}, due_time={self.due_time})>"
