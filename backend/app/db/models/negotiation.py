"""
Negotiation System Models

Multi-party negotiation for reaching binding agreements without central authority.
Core of the "Trust Without Central Authority" primitive demonstration.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import uuid4
from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey, Enum, Integer, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from app.db.session import Base
import enum


class NegotiationStatus(str, enum.Enum):
    """Status of multi-party negotiation."""
    INITIATED = "initiated"              # Created, waiting for all parties to join
    NEGOTIATING = "negotiating"          # Active offer/counter-offer exchange
    CONSENSUS_REACHED = "consensus_reached"  # All parties accepted same terms
    BINDING = "binding"                  # All parties finalized, irreversible
    TERMINATED = "terminated"            # Ended without agreement
    EXPIRED = "expired"                  # Timeout reached without consensus
    DISPUTED = "disputed"                # Party contests binding agreement


class NegotiationMessageType(str, enum.Enum):
    """Types of messages in a negotiation."""
    INITIATE = "initiate"                # Start negotiation with proposal
    JOIN = "join"                        # Join as participant
    OFFER = "offer"                      # Make initial offer
    COUNTER_OFFER = "counter_offer"      # Respond with modified terms
    ACCEPT = "accept"                    # Accept current terms
    REJECT = "reject"                    # Reject and optionally continue
    WITHDRAW = "withdraw"                # Leave negotiation entirely
    FINALIZE = "finalize"                # Confirm binding commitment
    DISPUTE = "dispute"                  # Contest binding agreement


class Negotiation(Base):
    """
    Multi-party negotiation session.

    Enables hostile parties to reach binding agreements without central authority.
    All state changes are cryptographically hashed for tamper evidence.
    """
    __tablename__ = "negotiations"

    # Identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text)

    # Participants
    initiator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    participant_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=False)  # All parties including initiator
    joined_participant_ids = Column(ARRAY(UUID(as_uuid=True)), default=list)  # Who has joined so far
    required_consensus_count = Column(Integer)  # How many must accept (default: all)

    # Status
    status = Column(Enum(NegotiationStatus), nullable=False, default=NegotiationStatus.INITIATED)

    # Terms (evolves through negotiation)
    current_terms = Column(JSON)  # Latest proposed terms
    terms_version = Column(Integer, default=1)  # Increments with each counter-offer
    terms_history = Column(JSON, default=list)  # History of all proposed terms

    # Consensus tracking
    acceptances = Column(JSON, default=dict)  # {user_id: {terms_version, timestamp, signature}}
    finalizations = Column(JSON, default=dict)  # {user_id: {timestamp, signature}}

    # Timeouts
    negotiation_deadline = Column(DateTime)  # Must reach consensus by this time
    finalization_deadline = Column(DateTime)  # Must finalize after consensus by this time

    # Binding commitment
    binding_hash = Column(String(64))  # SHA-256 of final agreed terms
    binding_timestamp = Column(DateTime)
    binding_terms = Column(JSON)  # Final agreed terms (frozen)

    # Cryptographic integrity
    content_hash = Column(String(64))  # Hash of negotiation state
    previous_hash = Column(String(64))  # Chain to previous negotiation (optional)

    # Metadata
    negotiation_metadata = Column(JSON, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    consensus_reached_at = Column(DateTime)

    # Relationships
    initiator = relationship("User", foreign_keys=[initiator_id], backref="negotiations_initiated")
    messages = relationship("NegotiationMessage", back_populates="negotiation", order_by="NegotiationMessage.created_at")


class NegotiationMessage(Base):
    """
    Messages in a negotiation (offers, counter-offers, accepts, etc.).

    Every message generates a cryptographically hashed receipt for audit trail.
    """
    __tablename__ = "negotiation_messages"

    # Identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    negotiation_id = Column(UUID(as_uuid=True), ForeignKey("negotiations.id"), nullable=False)

    # Author
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Message type and content
    message_type = Column(Enum(NegotiationMessageType), nullable=False)
    terms = Column(JSON)  # Proposed terms (for OFFER, COUNTER_OFFER)
    terms_version = Column(Integer)  # Which version this responds to
    message_text = Column(Text)  # Optional explanation

    # Response to
    in_response_to_message_id = Column(UUID(as_uuid=True), ForeignKey("negotiation_messages.id"))

    # Cryptographic proof
    content_hash = Column(String(64))  # Hash of this message
    signature = Column(String(512))  # Digital signature (future: party's key)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Receipt tracking
    receipt_id = Column(UUID(as_uuid=True), ForeignKey("receipts.id"))

    # Relationships
    negotiation = relationship("Negotiation", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id], backref="negotiation_messages_sent")
    receipt = relationship("Receipt", foreign_keys=[receipt_id])

    # Self-referential relationship for threading
    in_response_to = relationship("NegotiationMessage", remote_side=[id], backref="responses")


class NegotiationEscrow(Base):
    """
    Escrow for resources locked during negotiation.

    Future enhancement for negotiations involving assets, tokens, or permissions.
    Resources are locked at start and conditionally released based on outcome.
    """
    __tablename__ = "negotiation_escrows"

    # Identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    negotiation_id = Column(UUID(as_uuid=True), ForeignKey("negotiations.id"), nullable=False)

    # What's locked
    participant_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    resource_type = Column(String(50), nullable=False)  # "token", "permission", "data_access", etc.
    resource_identifier = Column(String(200), nullable=False)
    locked_amount = Column(Float)  # For quantifiable resources

    # Status
    is_locked = Column(String(20), default="locked")  # "locked", "released", "forfeited"
    locked_at = Column(DateTime, default=datetime.utcnow)
    released_at = Column(DateTime)

    # Release conditions
    release_condition = Column(String(20), default="on_binding")  # "on_binding", "on_termination", "on_timeout"

    # Cryptographic proof
    lock_hash = Column(String(64))  # Hash of lock commitment
    lock_signature = Column(String(512))  # Signature proving lock
    release_signature = Column(String(512))  # Signature proving release

    # Metadata
    escrow_metadata = Column(JSON, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    negotiation = relationship("Negotiation", backref="escrows")
    participant = relationship("User", foreign_keys=[participant_id], backref="negotiation_escrows")
