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
    BLOCKED = "blocked"  # Added for dependency tracking


class TaskPriority(str, enum.Enum):
    """Task priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class QuestType(str, enum.Enum):
    """Gamification quest classifications for tasks."""
    TUTORIAL = "tutorial"  # First-time tasks
    DAILY = "daily"        # Recurring habits
    SOLO = "solo"          # Individual challenges
    PARTY = "party"        # Small group (2-5)
    RAID = "raid"          # Large group (6+)
    EPIC = "epic"          # Long-term goals
    CHALLENGE = "challenge"  # Special difficulty tasks


class Task(BaseModel):
    """
    Enhanced task model with time awareness, game mechanics, and sovereignty.
    
    This model represents a task as the action layer of cognitive sovereignty,
    bridging memories (past) to intentions (future) with gamification.
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
    
    # Time awareness (new fields)
    estimated_duration_minutes = Column(Integer, nullable=True)
    actual_duration_minutes = Column(Integer, nullable=True)
    started_at = Column(DateTime, nullable=True)  # When work actually began
    
    # Progress tracking
    progress = Column(Float, default=0.0, nullable=False)  # 0.0 to 1.0
    
    # Game mechanics (new fields)
    difficulty = Column(Integer, default=1, nullable=False)  # 1-5 scale
    quest_type = Column(Enum(QuestType), nullable=True)
    experience_points = Column(Integer, default=0, nullable=False)
    
    # Identity shaping - ICV evolution (new fields)
    value_impact = Column(JSON, default={}, nullable=True)  # {"craft": 0.2, "care": 0.1}
    skill_development = Column(JSON, default={}, nullable=True)  # Skills developed
    
    # Privacy and sovereignty (new fields)
    visibility_mask = Column(String(50), default='private', nullable=False)
    encrypted_content = Column(Boolean, default=False, nullable=False)
    
    # Collaboration (new fields)
    is_shared = Column(Boolean, default=False, nullable=False)
    assignees = Column(JSON, default=[], nullable=True)  # List of user IDs
    requires_all_complete = Column(Boolean, default=False, nullable=False)
    
    # Recurrence (new fields)
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_rule = Column(String(255), nullable=True)  # RRULE format
    recurring_parent_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Task metadata
    tags = Column(ARRAY(String), default=[], nullable=False)
    task_metadata = Column(JSON, default={}, nullable=False)
    context = Column(JSON, default={}, nullable=True)  # Additional context
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
    
    def calculate_experience(self) -> int:
        """Calculate experience points based on task properties."""
        base_xp = self.difficulty * 10
        
        # Bonus for on-time completion
        if self.completed_at and self.due_date:
            if self.completed_at <= self.due_date:
                base_xp += 5
        
        # Bonus for collaboration
        if self.is_shared and self.assignees:
            base_xp += len(self.assignees) * 2
        
        # Apply value impact multipliers
        if self.value_impact:
            for value, impact in self.value_impact.items():
                base_xp += int(impact * 10)
        
        return base_xp
    
    def mark_complete(self):
        """Mark task as completed and calculate rewards."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.progress = 1.0
        self.experience_points = self.calculate_experience()
        
        # Calculate actual duration if we have timestamps
        if self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds() / 60
            self.actual_duration_minutes = int(duration)
    
    def mark_in_progress(self):
        """Mark task as in progress."""
        self.status = TaskStatus.IN_PROGRESS
        if not self.started_at:
            self.started_at = datetime.utcnow()
    
    def classify_quest_type(self):
        """Auto-classify quest type based on task properties."""
        if not self.quest_type:
            if self.is_recurring:
                self.quest_type = QuestType.DAILY
            elif self.difficulty >= 4:
                self.quest_type = QuestType.CHALLENGE
            elif self.is_shared and len(self.assignees or []) > 5:
                self.quest_type = QuestType.RAID
            elif self.is_shared and len(self.assignees or []) > 1:
                self.quest_type = QuestType.PARTY
            elif self.parent_id and self.difficulty >= 3:
                self.quest_type = QuestType.EPIC
            else:
                self.quest_type = QuestType.SOLO


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
