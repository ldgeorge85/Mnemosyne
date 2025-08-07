"""
Reflection model for Mnemosyne Protocol
Agent reflections and insights on memories
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, String, Text, Float, Integer, Boolean, DateTime, JSON, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import JSONB, UUID as SQLAlchemyUUID
from pgvector.sqlalchemy import Vector

from backend.core.database import Base, TimestampMixin, UUIDMixin


class AgentType(str, Enum):
    """Types of agents that can create reflections"""
    # Core agents
    ENGINEER = "engineer"
    LIBRARIAN = "librarian"
    PRIEST = "priest"
    MYCELIUM = "mycelium"
    
    # Philosophical agents
    STOIC = "stoic"
    SAGE = "sage"
    CRITIC = "critic"
    TRICKSTER = "trickster"
    BUILDER = "builder"
    MYSTIC = "mystic"
    GUARDIAN = "guardian"
    HEALER = "healer"
    SCHOLAR = "scholar"
    PROPHET = "prophet"
    
    # Collective agents
    MATCHMAKER = "matchmaker"
    GAP_FINDER = "gap_finder"
    SYNTHESIZER = "synthesizer"
    ARBITRATOR = "arbitrator"
    CURATOR = "curator"
    RITUAL_MASTER = "ritual_master"
    
    @property
    def symbol(self) -> str:
        """Get symbolic representation"""
        symbols = {
            "engineer": "⚒",
            "librarian": "📚",
            "priest": "☩",
            "mycelium": "🍄",
            "stoic": "Σ",
            "sage": "♾",
            "critic": "‡",
            "trickster": "☿",
            "builder": "⚒",
            "mystic": "✧",
            "guardian": "⚔",
            "healer": "⚕",
            "scholar": "📚",
            "prophet": "☄",
            "matchmaker": "♡",
            "gap_finder": "◯",
            "synthesizer": "⊕",
            "arbitrator": "⚖",
            "curator": "◈",
            "ritual_master": "☆"
        }
        return symbols.get(self.value, "?")


class ReflectionType(str, Enum):
    """Types of reflections"""
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    PATTERN = "pattern"
    INSIGHT = "insight"
    WARNING = "warning"
    QUESTION = "question"
    CONNECTION = "connection"
    RITUAL = "ritual"


class Reflection(Base, UUIDMixin, TimestampMixin):
    """Agent reflections on memories"""
    
    __tablename__ = "reflections"
    
    # Relationships
    user_id: Mapped[SQLAlchemyUUID] = Column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    memory_id: Mapped[SQLAlchemyUUID] = Column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("memories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Agent information
    agent_type: Mapped[AgentType] = Column(
        SQLEnum(AgentType),
        nullable=False,
        index=True
    )
    agent_id: Mapped[str] = Column(String(100), nullable=False)
    agent_symbol: Mapped[str] = Column(String(10), nullable=False)
    
    # Reflection content
    content: Mapped[str] = Column(Text, nullable=False)
    summary: Mapped[Optional[str]] = Column(Text, nullable=True)
    reflection_type: Mapped[ReflectionType] = Column(
        SQLEnum(ReflectionType),
        default=ReflectionType.ANALYSIS,
        nullable=False
    )
    
    # Vector embedding for the reflection
    embedding: Mapped[Optional[Vector]] = Column(
        Vector(1536),
        nullable=True
    )
    
    # Scores and metrics
    confidence: Mapped[float] = Column(
        Float,
        default=0.7,
        nullable=False
    )
    relevance: Mapped[float] = Column(Float, default=0.5, nullable=False)
    coherence: Mapped[float] = Column(Float, default=0.8, nullable=False)
    drift_from_memory: Mapped[float] = Column(Float, default=0.0, nullable=False)
    
    # Sub-signal modulation (affects user's Deep Signal)
    sub_signal: Mapped[Dict[str, Any]] = Column(
        JSONB,
        default={},
        nullable=False
    )
    signal_modulation: Mapped[float] = Column(
        Float,
        default=0.0,
        nullable=False
    )  # -1 to 1, how much this affects user signal
    
    # Extracted insights
    patterns: Mapped[List[str]] = Column(JSON, default=list)
    connections: Mapped[List[str]] = Column(JSON, default=list)  # IDs of connected memories
    questions: Mapped[List[str]] = Column(JSON, default=list)
    recommendations: Mapped[List[str]] = Column(JSON, default=list)
    
    # Metadata
    metadata: Mapped[Dict[str, Any]] = Column(
        JSONB,
        default={},
        nullable=False
    )
    tags: Mapped[List[str]] = Column(JSON, default=list)
    domains: Mapped[List[str]] = Column(JSON, default=list)
    
    # Processing information
    processing_time_ms: Mapped[Optional[int]] = Column(Integer, nullable=True)
    model_used: Mapped[Optional[str]] = Column(String(100), nullable=True)
    prompt_tokens: Mapped[Optional[int]] = Column(Integer, nullable=True)
    completion_tokens: Mapped[Optional[int]] = Column(Integer, nullable=True)
    
    # Consolidation and lifecycle
    is_consolidated: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    consolidation_group_id: Mapped[Optional[SQLAlchemyUUID]] = Column(
        SQLAlchemyUUID(as_uuid=True),
        nullable=True,
        index=True
    )
    decay_rate: Mapped[float] = Column(Float, default=1.0, nullable=False)
    last_evaluated_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)
    
    # User feedback
    user_rating: Mapped[Optional[float]] = Column(Float, nullable=True)
    user_feedback: Mapped[Optional[str]] = Column(Text, nullable=True)
    was_helpful: Mapped[Optional[bool]] = Column(Boolean, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="reflections")
    memory = relationship("Memory", back_populates="reflections")
    
    # Constraints
    __table_args__ = (
        Index("ix_reflections_user_agent", "user_id", "agent_type"),
        Index("ix_reflections_memory_agent", "memory_id", "agent_type"),
        Index("ix_reflections_confidence", "confidence"),
        Index("ix_reflections_drift", "drift_from_memory"),
        Index("ix_reflections_consolidation", "consolidation_group_id"),
        Index("ix_reflections_embedding", "embedding", postgresql_using="ivfflat"),
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="ck_reflections_confidence"),
        CheckConstraint("relevance >= 0 AND relevance <= 1", name="ck_reflections_relevance"),
        CheckConstraint("coherence >= 0 AND coherence <= 1", name="ck_reflections_coherence"),
        CheckConstraint("drift_from_memory >= 0 AND drift_from_memory <= 1", name="ck_reflections_drift"),
        CheckConstraint("signal_modulation >= -1 AND signal_modulation <= 1", name="ck_reflections_modulation"),
    )
    
    def calculate_impact(self) -> float:
        """Calculate the impact score of this reflection"""
        # Base impact from confidence and relevance
        base_impact = (self.confidence + self.relevance) / 2
        
        # Adjust for coherence
        base_impact *= self.coherence
        
        # Boost for certain reflection types
        type_boost = {
            ReflectionType.INSIGHT: 1.2,
            ReflectionType.WARNING: 1.3,
            ReflectionType.PATTERN: 1.1,
            ReflectionType.CONNECTION: 1.1,
        }
        base_impact *= type_boost.get(self.reflection_type, 1.0)
        
        # Consider user feedback if available
        if self.user_rating:
            base_impact = (base_impact + self.user_rating) / 2
        
        return max(0.0, min(1.0, base_impact))
    
    def generate_sub_signal(self) -> Dict[str, Any]:
        """Generate sub-signal that modulates user's Deep Signal"""
        return {
            "agent": self.agent_type.value,
            "symbol": self.agent_symbol,
            "type": self.reflection_type.value,
            "confidence": self.confidence,
            "drift": self.drift_from_memory,
            "modulation": self.signal_modulation,
            "patterns": self.patterns[:3],  # Top 3 patterns
            "timestamp": self.created_at.isoformat()
        }
    
    def should_trigger_ritual(self) -> bool:
        """Check if this reflection should trigger a ritual"""
        # High-impact insights might trigger rituals
        if self.calculate_impact() > 0.8:
            return True
        
        # Warnings always trigger evaluation
        if self.reflection_type == ReflectionType.WARNING:
            return True
        
        # High drift indicates need for re-evaluation
        if self.drift_from_memory > 0.7:
            return True
        
        # Ritual type reflections obviously trigger rituals
        if self.reflection_type == ReflectionType.RITUAL:
            return True
        
        return False
    
    def to_fragment(self) -> Dict[str, Any]:
        """Convert to shareable fragment format"""
        return {
            "id": str(self.id),
            "agent": {
                "type": self.agent_type.value,
                "symbol": self.agent_symbol
            },
            "type": self.reflection_type.value,
            "summary": self.summary or self.content[:200],
            "confidence": round(self.confidence, 2),
            "coherence": round(self.coherence, 2),
            "patterns": self.patterns,
            "domains": self.domains,
            "impact": round(self.calculate_impact(), 2)
        }
    
    def __repr__(self) -> str:
        return f"<Reflection {self.id} by {self.agent_type.value} ({self.reflection_type.value})>"