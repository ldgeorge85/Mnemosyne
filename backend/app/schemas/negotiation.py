"""
Negotiation Pydantic Schemas

Request and response models for multi-party negotiation API.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

from app.db.models.negotiation import NegotiationStatus, NegotiationMessageType


# Request schemas

class NegotiationCreate(BaseModel):
    """Request to create a new negotiation."""
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    participant_ids: List[UUID] = Field(..., min_items=2)
    initial_terms: Dict[str, Any]
    negotiation_days: int = Field(default=7, ge=1, le=30)
    finalization_days: int = Field(default=3, ge=1, le=14)
    required_consensus_count: Optional[int] = Field(default=None, ge=1)


class OfferCreate(BaseModel):
    """Request to send an offer or counter-offer."""
    terms: Dict[str, Any]
    message_text: Optional[str] = Field(default=None, max_length=1000)


class AcceptTerms(BaseModel):
    """Request to accept current terms."""
    signature: Optional[str] = Field(default=None, max_length=512)
    message_text: Optional[str] = Field(default=None, max_length=1000)


class FinalizeCommitment(BaseModel):
    """Request to finalize binding commitment."""
    signature: Optional[str] = Field(default=None, max_length=512)


class WithdrawRequest(BaseModel):
    """Request to withdraw from negotiation."""
    reason: Optional[str] = Field(default=None, max_length=1000)


class DisputeRequest(BaseModel):
    """Request to dispute binding agreement."""
    dispute_reason: str = Field(..., min_length=1, max_length=1000)


# Response schemas

class NegotiationMessageResponse(BaseModel):
    """Response model for negotiation message."""
    id: UUID
    negotiation_id: UUID
    sender_id: UUID
    message_type: NegotiationMessageType
    terms: Optional[Dict[str, Any]] = None
    terms_version: Optional[int] = None
    message_text: Optional[str] = None
    content_hash: Optional[str] = None
    signature: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NegotiationResponse(BaseModel):
    """Response model for negotiation."""
    id: UUID
    title: str
    description: Optional[str] = None
    initiator_id: UUID
    participant_ids: List[UUID]
    joined_participant_ids: List[UUID]
    required_consensus_count: int
    status: NegotiationStatus
    current_terms: Optional[Dict[str, Any]] = None
    terms_version: int
    acceptances: Dict[str, Any]
    finalizations: Dict[str, Any]
    negotiation_deadline: Optional[datetime] = None
    finalization_deadline: Optional[datetime] = None
    binding_hash: Optional[str] = None
    binding_timestamp: Optional[datetime] = None
    binding_terms: Optional[Dict[str, Any]] = None
    content_hash: Optional[str] = None
    previous_hash: Optional[str] = None
    negotiation_metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    consensus_reached_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NegotiationDetailResponse(NegotiationResponse):
    """Detailed response including messages."""
    messages: List[NegotiationMessageResponse] = []

    class Config:
        from_attributes = True


class NegotiationListResponse(BaseModel):
    """Response for list of negotiations."""
    negotiations: List[NegotiationResponse]
    total: int
    page: int
    page_size: int


class TimeoutCheckResponse(BaseModel):
    """Response for timeout check."""
    negotiation_timeouts: List[NegotiationResponse]
    finalization_timeouts: List[NegotiationResponse]
    total_expired: int
