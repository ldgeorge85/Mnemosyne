"""
Trust System Models

This module defines the trust network models for progressive trust building
and governance with appeals process.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4
from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey, Enum, Float, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from app.db.session import Base
import enum


class TrustLevel(str, enum.Enum):
    """Progressive trust levels between agents."""
    AWARENESS = "awareness"          # Zero-knowledge proof of existence
    RECOGNITION = "recognition"      # Minimal verified disclosure
    FAMILIARITY = "familiarity"      # Shared interaction history
    SHARED_MEMORY = "shared_memory"  # Mutual experiences established
    DEEP_TRUST = "deep_trust"        # Full alignment and revelation


class TrustEventType(str, enum.Enum):
    """Types of trust-affecting events (neutral language)."""
    DISCLOSURE = "disclosure"
    INTERACTION = "interaction"
    CONFLICT = "conflict"
    ALIGNMENT = "alignment"
    DIVERGENCE = "divergence"
    RESONANCE = "resonance"


class AppealStatus(str, enum.Enum):
    """Status of trust event appeals."""
    PENDING = "pending"
    REVIEWING = "reviewing"
    RESOLVED = "resolved"
    WITHDRAWN = "withdrawn"
    ESCALATED = "escalated"


class TrustEvent(Base):
    """
    Trust events with neutral language (not "violations").
    
    Records trust-affecting events between users/agents with
    full governance and appeals process.
    """
    __tablename__ = "trust_events"
    
    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    event_type = Column(Enum(TrustEventType), nullable=False)
    trust_delta = Column(Float)  # Can be positive or negative
    context = Column(JSON)
    
    # Governance fields
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    resolver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # Must be different from reporter
    appeal_id = Column(UUID(as_uuid=True), ForeignKey("appeals.id"))
    policy_version = Column(String(20), default="v1")
    
    # Sovereignty preservation
    visibility_scope = Column(String(20), default="private")  # private/trusted/public
    user_consent = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    # Relationships
    actor = relationship("User", foreign_keys=[actor_id], backref="trust_events_as_actor")
    subject = relationship("User", foreign_keys=[subject_id], backref="trust_events_as_subject")
    reporter = relationship("User", foreign_keys=[reporter_id], backref="trust_events_reported")
    resolver = relationship("User", foreign_keys=[resolver_id], backref="trust_events_resolved")
    appeal = relationship("Appeal", foreign_keys=[appeal_id], backref="trust_event", uselist=False)


class Appeal(Base):
    """
    Appeals process for trust events with due process.
    
    Ensures that trust events can be contested and reviewed
    with proper separation of duties.
    """
    __tablename__ = "appeals"
    
    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    trust_event_id = Column(UUID(as_uuid=True), ForeignKey("trust_events.id"), nullable=False)
    appellant_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(Enum(AppealStatus), nullable=False, default=AppealStatus.PENDING)
    
    # Appeal content
    appeal_reason = Column(Text)
    resolution = Column(Text)
    
    # Due process fields
    evidence = Column(JSON)  # Supporting evidence for appeal
    witness_ids = Column(ARRAY(UUID(as_uuid=True)))  # Array of witness user IDs
    review_board_ids = Column(ARRAY(UUID(as_uuid=True)))  # Multiple reviewers for important cases
    
    # Timestamps
    submitted_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    review_deadline = Column(DateTime)  # SLA for review
    
    # Metadata
    appeal_metadata = Column(JSON)
    
    # Relationships
    appellant = relationship("User", foreign_keys=[appellant_id], backref="appeals_filed")


class TrustRelationship(Base):
    """
    Tracks the current trust level between two users/agents.
    
    This is the aggregate result of all trust events between them.
    """
    __tablename__ = "trust_relationships"
    
    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_a_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user_b_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Trust metrics
    trust_level = Column(Enum(TrustLevel), default=TrustLevel.AWARENESS)
    trust_score = Column(Float, default=0.0)  # Normalized 0-1
    resonance_score = Column(Float, default=0.0)  # Natural affinity 0-1
    
    # Progressive disclosure tracking
    disclosure_level_a = Column(Integer, default=0)  # How much A has revealed to B
    disclosure_level_b = Column(Integer, default=0)  # How much B has revealed to A
    reciprocity_balance = Column(Float, default=0.0)  # Measure of disclosure balance
    
    # Interaction history
    interaction_count = Column(Integer, default=0)
    last_interaction = Column(DateTime)
    first_interaction = Column(DateTime)
    
    # Trust dynamics with bounds
    decay_rate = Column(Float, default=0.95)  # Bounded 0.80-0.95
    recovery_rate = Column(Float, default=1.1)  # Bounded 1.05-1.20
    
    # Additional data
    shared_context = Column(JSON)  # Shared memories, experiences
    relationship_metadata = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_a = relationship("User", foreign_keys=[user_a_id], backref="trust_relationships_as_a")
    user_b = relationship("User", foreign_keys=[user_b_id], backref="trust_relationships_as_b")


class ConsciousnessMap(Base):
    """
    Optional consciousness mapping for pattern observation.
    
    Tracks behavioral patterns on spectrums without judgment.
    Users must explicitly opt-in to this tracking.
    """
    __tablename__ = "consciousness_maps"
    
    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Opt-in tracking
    opted_in = Column(Boolean, default=False, nullable=False)
    opt_in_date = Column(DateTime)
    opt_out_date = Column(DateTime)
    
    # Pattern observations (spectrums, not judgments)
    patterns = Column(JSON)  # {dimension: value} on various spectrums
    """
    Example patterns:
    {
        "transparency": 0.8,  # hidden <---> visible spectrum
        "trust_structure": 0.3,  # hierarchical <---> peer-based
        "language_style": 0.6,  # prescriptive <---> descriptive
        "interaction_style": 0.4,  # passive <---> active
        "disclosure_tendency": 0.7,  # private <---> open
    }
    """
    
    # Temporal tracking
    pattern_history = Column(JSON)  # Historical pattern changes
    observation_count = Column(Integer, default=0)
    
    # User interpretation
    user_values = Column(JSON)  # User's own interpretation of patterns
    user_notes = Column(Text)  # User's reflections on patterns
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_observed = Column(DateTime)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="consciousness_map", uselist=False)