"""
Deep Signal model for Mnemosyne Protocol
Identity compression and symbolic signaling
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum

from sqlalchemy import Column, String, Text, Float, Integer, Boolean, DateTime, JSON, ForeignKey, Index, CheckConstraint, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import JSONB, UUID as SQLAlchemyUUID
from pgvector.sqlalchemy import Vector

from core.database import Base, TimestampMixin, UUIDMixin


class SignalVisibility(str, Enum):
    """Signal visibility levels"""
    PRIVATE = "private"
    TRUSTED = "trusted"
    COLLECTIVE = "collective"
    PUBLIC = "public"


class TrustFragmentType(str, Enum):
    """Types of trust fragments"""
    GLYPHIC = "glyphic"        # Symbol-based trust
    RITUAL = "ritual"           # Through ceremony
    PROOF = "proof"             # Zero-knowledge proof
    RECIPROCAL = "reciprocal"   # Mutual exchange


class DeepSignal(Base, UUIDMixin, TimestampMixin):
    """Deep Signal for identity and meaning compression"""
    
    __tablename__ = "signals"
    
    # User relationship
    user_id: Mapped[SQLAlchemyUUID] = Column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Signal version and identity
    version: Mapped[str] = Column(String(10), default="3.1", nullable=False)
    signal_hash: Mapped[str] = Column(String(64), unique=True, nullable=False, index=True)
    
    # Core symbolic identity
    sigil: Mapped[str] = Column(String(10), nullable=False)  # Core identity symbol
    glyphs: Mapped[List[str]] = Column(JSON, default=list, nullable=False)  # Visual markers
    symbolic_role: Mapped[Optional[str]] = Column(String(50), nullable=True)  # Strategist, Builder, etc
    symbolic_glyph: Mapped[Optional[str]] = Column(String(10), nullable=True)  # Role symbol
    
    # Domains and capabilities
    domains: Mapped[List[str]] = Column(JSON, default=list, nullable=False)
    stack: Mapped[List[str]] = Column(JSON, default=list, nullable=False)
    capabilities: Mapped[List[str]] = Column(JSON, default=list, nullable=False)
    
    # Personality profile
    personality: Mapped[Dict[str, float]] = Column(
        JSONB,
        default={
            "openness": 0.5,
            "chaos_tolerance": 0.5,
            "trust_preference": "progressive"
        },
        nullable=False
    )
    
    # Coherence metrics
    coherence: Mapped[float] = Column(Float, default=1.0, nullable=False, index=True)
    fracture_index: Mapped[float] = Column(Float, default=0.0, nullable=False, index=True)
    integration_level: Mapped[float] = Column(Float, default=0.5, nullable=False)
    recovery_vectors: Mapped[List[str]] = Column(JSON, default=list)
    
    # Status flags
    flags: Mapped[Dict[str, Any]] = Column(
        JSONB,
        default={
            "seeking": [],
            "offering": [],
            "crisis_mode": False,
            "intended_silence": False
        },
        nullable=False
    )
    
    # Visibility and privacy
    visibility: Mapped[float] = Column(Float, default=0.3, nullable=False)  # 0-1 exposure level
    visibility_level: Mapped[SignalVisibility] = Column(
        SQLEnum(SignalVisibility),
        default=SignalVisibility.COLLECTIVE,
        nullable=False,
        index=True
    )
    
    # Trust fragment
    trust_fragment_type: Mapped[Optional[TrustFragmentType]] = Column(
        SQLEnum(TrustFragmentType),
        nullable=True
    )
    trust_fragment_depth: Mapped[Optional[str]] = Column(String(20), nullable=True)  # surface/embedded/esoteric
    trust_fragment_data: Mapped[Dict[str, Any]] = Column(JSONB, default={})
    verified_by: Mapped[List[str]] = Column(JSON, default=list)  # User IDs who verified
    
    # Vector embedding of the signal
    embedding: Mapped[Optional[Vector]] = Column(
        Vector(1536),
        nullable=True
    )
    
    # Lifecycle management
    entropy: Mapped[float] = Column(Float, default=1.0, nullable=False)
    decay_timer_days: Mapped[int] = Column(Integer, default=30, nullable=False)
    last_refreshed_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)
    emission_count: Mapped[int] = Column(Integer, default=0, nullable=False)
    resonance_count: Mapped[int] = Column(Integer, default=0, nullable=False)
    
    # Drift tracking
    local_drift_index: Mapped[float] = Column(Float, default=0.0, nullable=False)
    global_drift_index: Mapped[float] = Column(Float, default=0.0, nullable=False)
    drift_indicators: Mapped[List[str]] = Column(JSON, default=list)
    
    # Kartouche visualization data
    kartouche_svg: Mapped[Optional[str]] = Column(Text, nullable=True)
    kartouche_layers: Mapped[Dict[str, Any]] = Column(JSONB, default={})
    symbolic_trail: Mapped[List[Dict[str, Any]]] = Column(JSON, default=list)
    
    # Performance metrics
    propagation_count: Mapped[int] = Column(Integer, default=0, nullable=False)
    match_count: Mapped[int] = Column(Integer, default=0, nullable=False)
    response_rate: Mapped[float] = Column(Float, default=0.0, nullable=False)
    
    # Cryptographic elements
    signature: Mapped[str] = Column(Text, nullable=False)
    public_key: Mapped[Optional[str]] = Column(Text, nullable=True)
    
    # Metadata
    metadata_json: Mapped[Dict[str, Any]] = Column(JSONB, default={}, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="signals")
    
    # Constraints
    __table_args__ = (
        Index("ix_signals_user_coherence", "user_id", "coherence"),
        Index("ix_signals_visibility_level", "visibility_level"),
        Index("ix_signals_fracture", "fracture_index"),
        Index("ix_signals_entropy", "entropy"),
        Index("ix_signals_embedding", "embedding", postgresql_using="ivfflat"),
        CheckConstraint("coherence >= 0 AND coherence <= 1", name="ck_signals_coherence"),
        CheckConstraint("fracture_index >= 0 AND fracture_index <= 1", name="ck_signals_fracture"),
        CheckConstraint("integration_level >= 0 AND integration_level <= 1", name="ck_signals_integration"),
        CheckConstraint("visibility >= 0 AND visibility <= 1", name="ck_signals_visibility"),
        CheckConstraint("entropy >= 0 AND entropy <= 1", name="ck_signals_entropy"),
        CheckConstraint("local_drift_index >= 0 AND local_drift_index <= 1", name="ck_signals_local_drift"),
        CheckConstraint("global_drift_index >= 0 AND global_drift_index <= 1", name="ck_signals_global_drift"),
    )
    
    def calculate_entropy(self) -> float:
        """Calculate signal entropy (uniqueness/information content)"""
        # Base entropy from domains and capabilities
        domain_entropy = min(1.0, len(self.domains) * 0.1)
        capability_entropy = min(1.0, len(self.capabilities) * 0.05)
        
        # Adjust for coherence (more coherent = less entropy)
        coherence_factor = 1.0 - (self.coherence * 0.3)
        
        # Adjust for fracture (more fractured = more entropy/chaos)
        fracture_factor = 1.0 + (self.fracture_index * 0.2)
        
        # Calculate final entropy
        entropy = (domain_entropy + capability_entropy) / 2
        entropy *= coherence_factor * fracture_factor
        
        return max(0.0, min(1.0, entropy))
    
    def should_decay(self) -> bool:
        """Check if signal should decay"""
        if not self.created_at:
            return False
        
        age_days = (datetime.utcnow() - self.created_at).days
        return age_days > self.decay_timer_days
    
    def should_reevaluate(self) -> bool:
        """Check if signal needs re-evaluation"""
        # High local drift
        if self.local_drift_index > 0.5:
            return True
        
        # Low coherence
        if self.coherence < 0.3:
            return True
        
        # Long time since refresh
        if self.last_refreshed_at:
            days_since_refresh = (datetime.utcnow() - self.last_refreshed_at).days
            if days_since_refresh > 7:
                return True
        
        return False
    
    def apply_decay(self) -> None:
        """Apply decay to signal"""
        # Reduce visibility
        self.visibility *= 0.9
        
        # Increase fracture
        self.fracture_index = min(1.0, self.fracture_index + 0.1)
        
        # Reduce coherence
        self.coherence = max(0.0, self.coherence - 0.1)
        
        # Update decay timer
        self.decay_timer_days = max(7, self.decay_timer_days - 7)
    
    def refresh_from_memories(self, recent_memories: List["Memory"]) -> None:
        """Refresh signal based on recent memories"""
        if not recent_memories:
            return
        
        # Recalculate coherence based on memory patterns
        # This is simplified - real implementation would analyze patterns
        memory_importance = sum(m.importance for m in recent_memories) / len(recent_memories)
        self.coherence = (self.coherence + memory_importance) / 2
        
        # Reset fracture if memories are coherent
        if memory_importance > 0.7:
            self.fracture_index = max(0.0, self.fracture_index - 0.2)
        
        # Update refresh timestamp
        self.last_refreshed_at = datetime.utcnow()
        
        # Reset decay timer
        self.decay_timer_days = 30
    
    def to_protocol_dict(self) -> Dict[str, Any]:
        """Convert to protocol-compliant dictionary"""
        return {
            "version": self.version,
            "sigil": self.sigil,
            "domains": self.domains,
            "stack": self.stack,
            "personality": self.personality,
            "coherence": {
                "fracture_index": self.fracture_index,
                "integration_level": self.integration_level,
                "recovery_vectors": self.recovery_vectors
            },
            "glyphs": self.glyphs,
            "flags": self.flags,
            "visibility": self.visibility,
            "trust_fragment": {
                "type": self.trust_fragment_type.value if self.trust_fragment_type else None,
                "depth": self.trust_fragment_depth,
                "verified_by": self.verified_by
            },
            "symbolic_profile": {
                "role": self.symbolic_role,
                "glyph": self.symbolic_glyph,
                "function": self.metadata.get("function", "Unknown")
            },
            "timestamp": self.created_at.isoformat() if self.created_at else None,
            "signature": self.signature
        }
    
    def to_kartouche_data(self) -> Dict[str, Any]:
        """Prepare data for Kartouche visualization"""
        return {
            "sigil": self.sigil,
            "glyphs": self.glyphs,
            "coherence": self.coherence,
            "fracture_index": self.fracture_index,
            "domains": self.domains[:5],  # Top 5 domains
            "symbolic_trail": self.symbolic_trail[-10:],  # Last 10 events
            "layers": self.kartouche_layers,
            "entropy": self.entropy,
            "visibility": self.visibility
        }
    
    def __repr__(self) -> str:
        return f"<DeepSignal {self.sigil} coherence={self.coherence:.2f} visibility={self.visibility:.2f}>"