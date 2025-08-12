"""
Memory model for Mnemosyne Protocol
Core memory storage with vector embeddings and metadata
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, String, Text, Float, Integer, Boolean, DateTime, JSON, ForeignKey, Index, CheckConstraint, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import JSONB, UUID as SQLAlchemyUUID
from pgvector.sqlalchemy import Vector

from core.database import Base, TimestampMixin, UUIDMixin, SoftDeleteMixin


class MemoryType(str, Enum):
    """Types of memories in the system"""
    CONVERSATION = "conversation"
    REFLECTION = "reflection"
    CONSOLIDATION = "consolidation"
    EXTERNAL = "external"
    SYSTEM = "system"
    RITUAL = "ritual"
    SIGNAL = "signal"


class MemoryStatus(str, Enum):
    """Memory processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    CONSOLIDATED = "consolidated"
    ARCHIVED = "archived"
    FAILED = "failed"


class Memory(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """Core memory model with vector embeddings"""
    
    __tablename__ = "memories"
    
    # User relationship
    user_id: Mapped[SQLAlchemyUUID] = Column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Content fields
    content: Mapped[str] = Column(Text, nullable=False)
    summary: Mapped[Optional[str]] = Column(Text, nullable=True)
    title: Mapped[Optional[str]] = Column(String(255), nullable=True)
    
    # Memory type and status
    memory_type: Mapped[MemoryType] = Column(
        SQLEnum(MemoryType),
        default=MemoryType.CONVERSATION,
        nullable=False,
        index=True
    )
    status: Mapped[MemoryStatus] = Column(
        SQLEnum(MemoryStatus),
        default=MemoryStatus.PENDING,
        nullable=False,
        index=True
    )
    
    # Vector embeddings (multi-embedding support)
    embedding_content: Mapped[Optional[Vector]] = Column(
        Vector(1536),  # OpenAI ada-002 dimensions
        nullable=True
    )
    embedding_semantic: Mapped[Optional[Vector]] = Column(
        Vector(768),   # Local model dimensions
        nullable=True
    )
    embedding_contextual: Mapped[Optional[Vector]] = Column(
        Vector(384),   # Smaller contextual embedding
        nullable=True
    )
    
    # Importance and relevance scores
    importance: Mapped[float] = Column(
        Float,
        default=0.5,
        nullable=False,
        index=True
    )
    relevance: Mapped[float] = Column(Float, default=0.5, nullable=False)
    emotional_valence: Mapped[float] = Column(Float, default=0.0, nullable=False)  # -1 to 1
    confidence: Mapped[float] = Column(Float, default=0.8, nullable=False)
    
    # Consolidation tracking
    consolidation_count: Mapped[int] = Column(Integer, default=0, nullable=False)
    consolidation_group_id: Mapped[Optional[SQLAlchemyUUID]] = Column(
        SQLAlchemyUUID(as_uuid=True),
        nullable=True,
        index=True
    )
    parent_memory_id: Mapped[Optional[SQLAlchemyUUID]] = Column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("memories.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Metadata and tags
    metadata_json: Mapped[Dict[str, Any]] = Column(
        JSONB,
        default={},
        nullable=False
    )
    tags: Mapped[List[str]] = Column(JSON, default=list, nullable=False)
    domains: Mapped[List[str]] = Column(JSON, default=list, nullable=False)
    entities: Mapped[List[Dict[str, Any]]] = Column(JSON, default=list)  # Extracted entities
    
    # Source tracking
    source: Mapped[Optional[str]] = Column(String(50), nullable=True)  # web, chat, api, etc
    source_url: Mapped[Optional[str]] = Column(Text, nullable=True)
    source_metadata_json: Mapped[Dict[str, Any]] = Column(JSONB, default={})
    
    # Temporal information
    occurred_at: Mapped[Optional[datetime]] = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    last_accessed_at: Mapped[Optional[datetime]] = Column(
        DateTime(timezone=True),
        nullable=True
    )
    access_count: Mapped[int] = Column(Integer, default=0, nullable=False)
    
    # Drift and decay tracking
    drift_index: Mapped[float] = Column(Float, default=0.0, nullable=False)
    decay_rate: Mapped[float] = Column(Float, default=1.0, nullable=False)
    last_refreshed_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)
    
    # Privacy and sharing
    is_private: Mapped[bool] = Column(Boolean, default=True, nullable=False)
    sharing_level: Mapped[int] = Column(Integer, default=0, nullable=False)  # 0=private, 1-5 progressive
    encrypted: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    encryption_key_id: Mapped[Optional[str]] = Column(String(100), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="memories")
    reflections = relationship("Reflection", back_populates="memory", lazy="dynamic")
    child_memories = relationship(
        "Memory",
        backref="parent_memory",
        remote_side="Memory.id",
        lazy="select"
    )
    
    # Constraints
    __table_args__ = (
        Index("ix_memories_user_importance", "user_id", "importance"),
        Index("ix_memories_user_type", "user_id", "memory_type"),
        Index("ix_memories_user_occurred", "user_id", "occurred_at"),
        Index("ix_memories_consolidation_group", "consolidation_group_id"),
        Index("ix_memories_drift", "drift_index"),
        Index("ix_memories_embedding_content", "embedding_content", postgresql_using="ivfflat"),
        Index("ix_memories_embedding_semantic", "embedding_semantic", postgresql_using="ivfflat"),
        CheckConstraint("importance >= 0 AND importance <= 1", name="ck_memories_importance"),
        CheckConstraint("relevance >= 0 AND relevance <= 1", name="ck_memories_relevance"),
        CheckConstraint("emotional_valence >= -1 AND emotional_valence <= 1", name="ck_memories_valence"),
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="ck_memories_confidence"),
        CheckConstraint("drift_index >= 0 AND drift_index <= 1", name="ck_memories_drift"),
        CheckConstraint("sharing_level >= 0 AND sharing_level <= 5", name="ck_memories_sharing"),
    )
    
    def calculate_importance(self) -> float:
        """Calculate dynamic importance score"""
        base_importance = self.importance
        
        # Boost for frequently accessed
        if self.access_count > 10:
            base_importance += 0.1
        
        # Boost for consolidated memories
        if self.consolidation_count > 0:
            base_importance += 0.1 * min(self.consolidation_count, 3)
        
        # Decay over time
        if self.last_accessed_at:
            days_since_access = (datetime.utcnow() - self.last_accessed_at).days
            decay_factor = max(0.5, 1.0 - (days_since_access * 0.01))
            base_importance *= decay_factor
        
        return max(0.0, min(1.0, base_importance))
    
    def calculate_drift(self, reflections: List["Reflection"]) -> float:
        """Calculate semantic drift from reflections"""
        if not reflections:
            return 0.0
        
        # This would normally calculate vector distances
        # Simplified for now
        drift_scores = [r.confidence for r in reflections]
        avg_confidence = sum(drift_scores) / len(drift_scores) if drift_scores else 1.0
        
        return 1.0 - avg_confidence
    
    def should_consolidate(self) -> bool:
        """Check if memory should be consolidated"""
        # High importance memories
        if self.importance > 0.8:
            return True
        
        # Frequently accessed memories
        if self.access_count > 20:
            return True
        
        # Old unaccessed memories (candidates for consolidation)
        if self.last_accessed_at:
            days_since_access = (datetime.utcnow() - self.last_accessed_at).days
            if days_since_access > 30 and self.consolidation_count == 0:
                return True
        
        # High drift memories need re-evaluation
        if self.drift_index > 0.7:
            return True
        
        return False
    
    def mark_accessed(self) -> None:
        """Update access tracking"""
        self.last_accessed_at = datetime.utcnow()
        self.access_count += 1
        
        # Slight importance boost for access
        self.importance = min(1.0, self.importance + 0.01)
    
    def to_vector_dict(self) -> Dict[str, Any]:
        """Prepare memory for vector storage"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "content": self.content,
            "summary": self.summary or self.content[:200],
            "memory_type": self.memory_type.value,
            "importance": self.importance,
            "domains": self.domains,
            "tags": self.tags,
            "occurred_at": self.occurred_at.isoformat() if self.occurred_at else None,
            "metadata": self.metadata
        }
    
    def to_public_dict(self) -> Dict[str, Any]:
        """Get privacy-safe dictionary representation"""
        return {
            "id": str(self.id),
            "summary": self.summary or "Private memory",
            "memory_type": self.memory_type.value,
            "domains": self.domains[:2],  # Limited domains
            "importance": round(self.importance, 1),
            "occurred_at": self.occurred_at.isoformat() if self.occurred_at else None,
            "emotional_valence": round(self.emotional_valence, 1)
        }
    
    def __repr__(self) -> str:
        return f"<Memory {self.id} ({self.memory_type.value}) importance={self.importance:.2f}>"