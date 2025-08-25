"""
Task model for the action layer of cognitive sovereignty.
Tasks bridge memories (past) to intentions (future) with time awareness and gamification.
"""
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
import enum

from app.db.base import Base


class TaskStatus(str, enum.Enum):
    """Task lifecycle states"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class TaskPriority(str, enum.Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class QuestType(str, enum.Enum):
    """Gamification quest classifications"""
    TUTORIAL = "tutorial"  # First-time tasks
    DAILY = "daily"        # Recurring habits
    SOLO = "solo"          # Individual challenges
    PARTY = "party"        # Small group (2-5)
    RAID = "raid"          # Large group (6+)
    EPIC = "epic"          # Long-term goals


class Task(Base):
    """
    Core task model with sovereignty, time awareness, and game mechanics built in.
    Every task generates receipts for transparency while maintaining privacy.
    """
    __tablename__ = "tasks"
    
    # Core fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Time awareness
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Duration tracking
    estimated_duration_minutes = Column(Integer, nullable=True)  # Estimated time to complete
    actual_duration_minutes = Column(Integer, nullable=True)     # Actual time taken
    
    # Status and progress
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    progress = Column(Float, default=0.0, nullable=False)  # 0.0 to 1.0
    
    # Privacy and sovereignty
    visibility_mask = Column(String(50), default='private', nullable=False)
    encrypted_content = Column(Boolean, default=False, nullable=False)
    
    # Game mechanics
    difficulty = Column(Integer, default=1, nullable=False)  # 1-5 scale
    quest_type = Column(SQLEnum(QuestType), nullable=True)
    experience_points = Column(Integer, default=0, nullable=False)
    
    # Identity shaping (ICV evolution)
    value_impact = Column(JSON, nullable=True)  # {"craft": 0.2, "care": 0.1, "rigor": 0.3}
    skill_development = Column(JSON, nullable=True)  # Skills this task develops
    
    # Collaboration
    is_shared = Column(Boolean, default=False, nullable=False)
    assignees = Column(JSON, nullable=True)  # List of user IDs for shared tasks
    requires_all_complete = Column(Boolean, default=False)
    
    # Task hierarchy
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    
    # Recurrence
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_rule = Column(String(255), nullable=True)  # RRULE format
    recurring_parent_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Metadata
    tags = Column(JSON, nullable=True)  # List of tags
    context = Column(JSON, nullable=True)  # Additional context data
    
    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    parent_task = relationship("Task", remote_side=[id], backref="subtasks")
    # receipts = relationship("Receipt", back_populates="task")
    # memories = relationship("Memory", secondary="task_memories", back_populates="tasks")
    # achievements = relationship("Achievement", secondary="task_achievements")
    
    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status={self.status.value})>"
    
    def to_dict(self):
        """Convert task to dictionary for API responses"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'title': self.title,
            'description': self.description,
            'status': self.status.value,
            'priority': self.priority.value,
            'progress': self.progress,
            'difficulty': self.difficulty,
            'quest_type': self.quest_type.value if self.quest_type else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'tags': self.tags or [],
            'value_impact': self.value_impact or {},
            'is_shared': self.is_shared,
            'assignees': self.assignees or []
        }
    
    def calculate_experience(self) -> int:
        """Calculate experience points based on task properties"""
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
        """Mark task as completed and calculate rewards"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.progress = 1.0
        self.experience_points = self.calculate_experience()
        
        # Calculate actual duration if we have timestamps
        if hasattr(self, 'started_at') and self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds() / 60
            self.actual_duration_minutes = int(duration)