"""
Trust System Schemas

Pydantic models for trust events, appeals, and relationships.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

from app.db.models.trust import TrustLevel, TrustEventType, AppealStatus


# Trust Event Schemas
class TrustEventCreate(BaseModel):
    """Schema for creating a trust event."""
    actor_id: UUID
    subject_id: UUID
    event_type: TrustEventType
    trust_delta: float = Field(ge=-1.0, le=1.0)
    context: Optional[Dict[str, Any]] = None
    visibility_scope: Optional[str] = "private"
    user_consent: Optional[bool] = False


class TrustEventResponse(BaseModel):
    """Schema for trust event responses."""
    id: UUID
    actor_id: UUID
    subject_id: UUID
    event_type: TrustEventType
    trust_delta: float
    context: Optional[Dict[str, Any]]
    reporter_id: Optional[UUID]
    resolver_id: Optional[UUID]
    appeal_id: Optional[UUID]
    policy_version: str
    visibility_scope: str
    user_consent: bool
    created_at: datetime
    resolved_at: Optional[datetime]
    
    class Config:
        from_attributes = True
        orm_mode = True


# Appeal Schemas
class AppealCreate(BaseModel):
    """Schema for creating an appeal."""
    trust_event_id: UUID
    appeal_reason: str
    evidence: Optional[Dict[str, Any]] = None
    witness_ids: Optional[List[UUID]] = None


class AppealResponse(BaseModel):
    """Schema for appeal responses."""
    id: UUID
    trust_event_id: UUID
    appellant_id: UUID
    status: AppealStatus
    appeal_reason: str
    resolution: Optional[str]
    evidence: Optional[Dict[str, Any]]
    witness_ids: Optional[List[UUID]]
    review_board_ids: Optional[List[UUID]]
    submitted_at: datetime
    resolved_at: Optional[datetime]
    review_deadline: Optional[datetime]
    
    class Config:
        from_attributes = True
        orm_mode = True


# Trust Relationship Schemas
class TrustRelationshipResponse(BaseModel):
    """Schema for trust relationship responses."""
    id: UUID
    user_a_id: UUID
    user_b_id: UUID
    trust_level: TrustLevel
    trust_score: float
    resonance_score: float
    disclosure_level_a: int
    disclosure_level_b: int
    reciprocity_balance: float
    interaction_count: int
    last_interaction: Optional[datetime]
    first_interaction: Optional[datetime]
    decay_rate: float
    recovery_rate: float
    shared_context: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        orm_mode = True


class TrustProgressionRequest(BaseModel):
    """Schema for requesting trust level progression."""
    peer_id: UUID
    disclosure_level: int = Field(ge=0, le=5)
    shared_context: Optional[Dict[str, Any]] = None


# Consciousness Pattern Schemas
class ConsciousnessPatternResponse(BaseModel):
    """Schema for consciousness pattern responses."""
    id: UUID
    user_id: UUID
    opted_in: bool
    opt_in_date: Optional[datetime]
    opt_out_date: Optional[datetime]
    patterns: Optional[Dict[str, float]]
    pattern_history: Optional[Dict[str, Any]]
    observation_count: int
    user_values: Optional[Dict[str, Any]]
    user_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_observed: Optional[datetime]
    
    class Config:
        from_attributes = True
        orm_mode = True