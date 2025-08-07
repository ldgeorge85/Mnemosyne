"""
Sharing and trust models for Mnemosyne Protocol
Handles sharing contracts, trust relationships, and collective participation
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum

from sqlalchemy import Column, String, Text, Float, Integer, Boolean, DateTime, JSON, ForeignKey, Index, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import JSONB, UUID as SQLAlchemyUUID

from backend.core.database import Base, TimestampMixin, UUIDMixin


class SharingDepth(str, Enum):
    """Depth levels for shared content"""
    SUMMARY = "summary"      # Only summaries shared
    DETAILED = "detailed"    # Full content with some redaction
    FULL = "full"           # Complete access


class TrustStage(str, Enum):
    """Progressive trust stages"""
    SIGNAL_EXCHANGE = "signal_exchange"          # Public signals only
    DOMAIN_REVELATION = "domain_revelation"      # Reveal interest areas
    CAPABILITY_SHARING = "capability_sharing"    # Share specific skills
    MEMORY_GLIMPSE = "memory_glimpse"           # Share redacted memories
    FULL_TRUST = "full_trust"                   # Complete access


class RitualType(str, Enum):
    """Types of trust rituals"""
    PROGRESSIVE = "progressive"              # Default progressive path
    MIRRORED_DISSONANCE = "mirrored_dissonance"  # Trust through conflict
    ECHO_DRIFT = "echo_drift"               # Trust through chaos
    SYMBOLIC_PROOF = "symbolic_proof"       # Trust through effort


class SharingContract(Base, UUIDMixin, TimestampMixin):
    """Contracts defining how memories are shared"""
    
    __tablename__ = "sharing_contracts"
    
    # User who owns the contract
    user_id: Mapped[SQLAlchemyUUID] = Column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Collective or group this contract applies to
    collective_id: Mapped[str] = Column(String(100), nullable=False, index=True)
    collective_name: Mapped[Optional[str]] = Column(String(255), nullable=True)
    
    # Sharing parameters
    domains: Mapped[List[str]] = Column(JSON, default=list, nullable=False)
    depth: Mapped[SharingDepth] = Column(
        SQLEnum(SharingDepth),
        default=SharingDepth.SUMMARY,
        nullable=False
    )
    
    # Privacy settings
    k_anonymity: Mapped[int] = Column(Integer, default=3, nullable=False)
    anonymous: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    encrypted: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    
    # Time constraints
    start_date: Mapped[datetime] = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    end_date: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)
    duration_days: Mapped[Optional[int]] = Column(Integer, nullable=True)
    
    # Control flags
    revocable: Mapped[bool] = Column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = Column(Boolean, default=True, nullable=False)
    is_revoked: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    revoked_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)
    
    # Filtering rules
    filters: Mapped[Dict[str, Any]] = Column(
        JSONB,
        default={
            "min_importance": 0.3,
            "memory_types": [],
            "exclude_tags": [],
            "time_range": None
        },
        nullable=False
    )
    
    # Usage tracking
    share_count: Mapped[int] = Column(Integer, default=0, nullable=False)
    access_count: Mapped[int] = Column(Integer, default=0, nullable=False)
    last_accessed_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)
    
    # Reciprocity tracking
    reciprocal_contract_id: Mapped[Optional[SQLAlchemyUUID]] = Column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("sharing_contracts.id", ondelete="SET NULL"),
        nullable=True
    )
    has_reciprocity: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    metadata: Mapped[Dict[str, Any]] = Column(JSONB, default={}, nullable=False)
    notes: Mapped[Optional[str]] = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sharing_contracts")
    reciprocal_contract = relationship("SharingContract", remote_side="SharingContract.id")
    
    # Constraints
    __table_args__ = (
        Index("ix_sharing_contracts_user_collective", "user_id", "collective_id"),
        Index("ix_sharing_contracts_active", "is_active"),
        Index("ix_sharing_contracts_end_date", "end_date"),
        CheckConstraint("k_anonymity >= 1", name="ck_sharing_contracts_k_anonymity"),
        CheckConstraint("duration_days IS NULL OR duration_days > 0", name="ck_sharing_contracts_duration"),
    )
    
    def is_valid(self) -> bool:
        """Check if contract is currently valid"""
        if not self.is_active or self.is_revoked:
            return False
        
        now = datetime.utcnow()
        
        # Check start date
        if self.start_date > now:
            return False
        
        # Check end date
        if self.end_date and self.end_date < now:
            return False
        
        # Check duration
        if self.duration_days:
            expiry = self.start_date + timedelta(days=self.duration_days)
            if expiry < now:
                return False
        
        return True
    
    def validate_memory(self, memory: "Memory") -> bool:
        """Check if a memory matches contract filters"""
        # Check domain match
        if self.domains and not any(d in memory.domains for d in self.domains):
            return False
        
        # Check importance threshold
        min_importance = self.filters.get("min_importance", 0.0)
        if memory.importance < min_importance:
            return False
        
        # Check memory type filter
        allowed_types = self.filters.get("memory_types", [])
        if allowed_types and memory.memory_type.value not in allowed_types:
            return False
        
        # Check excluded tags
        excluded_tags = self.filters.get("exclude_tags", [])
        if any(tag in memory.tags for tag in excluded_tags):
            return False
        
        return True
    
    def revoke(self) -> None:
        """Revoke this sharing contract"""
        if not self.revocable:
            raise ValueError("Contract is not revocable")
        
        self.is_revoked = True
        self.is_active = False
        self.revoked_at = datetime.utcnow()
    
    def __repr__(self) -> str:
        return f"<SharingContract {self.collective_id} depth={self.depth.value} k={self.k_anonymity}>"


class TrustRelationship(Base, UUIDMixin, TimestampMixin):
    """Trust relationships between users"""
    
    __tablename__ = "trust_relationships"
    
    # Users in the relationship
    user_id: Mapped[SQLAlchemyUUID] = Column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    trusted_user_id: Mapped[SQLAlchemyUUID] = Column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Trust parameters
    trust_stage: Mapped[TrustStage] = Column(
        SQLEnum(TrustStage),
        default=TrustStage.SIGNAL_EXCHANGE,
        nullable=False,
        index=True
    )
    trust_score: Mapped[float] = Column(Float, default=0.0, nullable=False)
    trust_tier: Mapped[int] = Column(Integer, default=0, nullable=False)  # 0-3
    
    # Ritual tracking
    ritual_type: Mapped[Optional[RitualType]] = Column(
        SQLEnum(RitualType),
        nullable=True
    )
    ritual_stage: Mapped[int] = Column(Integer, default=0, nullable=False)
    ritual_completed: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    ritual_data: Mapped[Dict[str, Any]] = Column(JSONB, default={})
    
    # Interaction tracking
    positive_interactions: Mapped[int] = Column(Integer, default=0, nullable=False)
    negative_interactions: Mapped[int] = Column(Integer, default=0, nullable=False)
    total_interactions: Mapped[int] = Column(Integer, default=0, nullable=False)
    last_interaction_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)
    
    # Resonance and compatibility
    resonance_score: Mapped[float] = Column(Float, default=0.0, nullable=False)
    domain_overlap: Mapped[float] = Column(Float, default=0.0, nullable=False)
    symbolic_compatibility: Mapped[float] = Column(Float, default=0.0, nullable=False)
    
    # Zero-knowledge proof data
    zk_proof: Mapped[Optional[str]] = Column(Text, nullable=True)
    zk_proof_verified: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    zk_proof_expires_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)
    
    # Shared context
    shared_memories_count: Mapped[int] = Column(Integer, default=0, nullable=False)
    shared_reflections_count: Mapped[int] = Column(Integer, default=0, nullable=False)
    shared_domains: Mapped[List[str]] = Column(JSON, default=list)
    
    # Trust fragments
    trust_fragments: Mapped[List[Dict[str, Any]]] = Column(JSON, default=list)
    fragment_count: Mapped[int] = Column(Integer, default=0, nullable=False)
    
    # Status flags
    is_active: Mapped[bool] = Column(Boolean, default=True, nullable=False)
    is_mutual: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    metadata: Mapped[Dict[str, Any]] = Column(JSONB, default={}, nullable=False)
    notes: Mapped[Optional[str]] = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="trust_relationships")
    trusted_user = relationship("User", foreign_keys=[trusted_user_id], back_populates="trusted_by")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "trusted_user_id", name="uq_trust_relationships_users"),
        Index("ix_trust_relationships_stage", "trust_stage"),
        Index("ix_trust_relationships_score", "trust_score"),
        Index("ix_trust_relationships_mutual", "is_mutual"),
        CheckConstraint("user_id != trusted_user_id", name="ck_trust_relationships_different_users"),
        CheckConstraint("trust_score >= 0 AND trust_score <= 1", name="ck_trust_relationships_score"),
        CheckConstraint("trust_tier >= 0 AND trust_tier <= 3", name="ck_trust_relationships_tier"),
        CheckConstraint("resonance_score >= 0 AND resonance_score <= 1", name="ck_trust_relationships_resonance"),
    )
    
    def can_advance_stage(self) -> bool:
        """Check if trust can advance to next stage"""
        current_index = list(TrustStage).index(self.trust_stage)
        
        # Already at max stage
        if current_index >= len(TrustStage) - 1:
            return False
        
        # Check stage requirements
        requirements = {
            TrustStage.SIGNAL_EXCHANGE: {
                "positive_interactions": 3,
                "total_interactions": 5,
                "days": 1
            },
            TrustStage.DOMAIN_REVELATION: {
                "positive_interactions": 10,
                "total_interactions": 15,
                "days": 7,
                "trust_score": 0.2
            },
            TrustStage.CAPABILITY_SHARING: {
                "positive_interactions": 25,
                "total_interactions": 35,
                "days": 14,
                "trust_score": 0.4
            },
            TrustStage.MEMORY_GLIMPSE: {
                "positive_interactions": 50,
                "total_interactions": 70,
                "days": 30,
                "trust_score": 0.6,
                "shared_memories_count": 5
            }
        }
        
        reqs = requirements.get(self.trust_stage, {})
        
        # Check interaction requirements
        if self.positive_interactions < reqs.get("positive_interactions", 0):
            return False
        if self.total_interactions < reqs.get("total_interactions", 0):
            return False
        
        # Check time requirement
        if self.created_at:
            days_elapsed = (datetime.utcnow() - self.created_at).days
            if days_elapsed < reqs.get("days", 0):
                return False
        
        # Check trust score
        if self.trust_score < reqs.get("trust_score", 0):
            return False
        
        # Check shared content
        if self.shared_memories_count < reqs.get("shared_memories_count", 0):
            return False
        
        return True
    
    def advance_stage(self) -> bool:
        """Attempt to advance to next trust stage"""
        if not self.can_advance_stage():
            return False
        
        current_index = list(TrustStage).index(self.trust_stage)
        self.trust_stage = list(TrustStage)[current_index + 1]
        
        # Update trust tier
        self.trust_tier = min(3, self.trust_tier + 1)
        
        return True
    
    def record_interaction(self, positive: bool = True) -> None:
        """Record an interaction and update scores"""
        self.total_interactions += 1
        
        if positive:
            self.positive_interactions += 1
            self.trust_score = min(1.0, self.trust_score + 0.01)
        else:
            self.negative_interactions += 1
            self.trust_score = max(0.0, self.trust_score - 0.02)
        
        self.last_interaction_at = datetime.utcnow()
    
    def add_trust_fragment(self, fragment: Dict[str, Any]) -> None:
        """Add a trust fragment to the relationship"""
        self.trust_fragments.append({
            **fragment,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.fragment_count += 1
        
        # Boost trust score for fragments
        self.trust_score = min(1.0, self.trust_score + 0.05)
    
    def __repr__(self) -> str:
        return f"<TrustRelationship {self.user_id} -> {self.trusted_user_id} stage={self.trust_stage.value}>"