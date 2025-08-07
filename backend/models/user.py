"""
User model for Mnemosyne Protocol
Handles authentication, initiation levels, and user profiles
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import bcrypt

from sqlalchemy import Column, String, Boolean, Integer, Float, DateTime, JSON, Index, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import JSONB

from backend.core.database import Base, TimestampMixin, UUIDMixin


class InitiationLevel(str, Enum):
    """Progressive initiation levels in the Mnemonic Order"""
    OBSERVER = "observer"           # Can read and emit basic signals
    FRAGMENTOR = "fragmentor"       # Can create fragments and share with k-anonymity
    AGENT = "agent"                 # Can spawn agents and participate in rituals
    KEEPER = "keeper"               # Full access and governance participation
    
    @property
    def symbol(self) -> str:
        """Get symbolic representation"""
        symbols = {
            "observer": "👁",
            "fragmentor": "◈",
            "agent": "☿",
            "keeper": "🗝"
        }
        return symbols.get(self.value, "?")
    
    @property
    def capabilities(self) -> List[str]:
        """Get capabilities for this level"""
        caps = {
            "observer": ["read", "basic_signal"],
            "fragmentor": ["create_fragments", "share_k3", "memory_consolidation"],
            "agent": ["spawn_agents", "ritual_participation", "collective_access"],
            "keeper": ["all", "governance_vote", "ritual_creation", "trust_ceremonies"]
        }
        return caps.get(self.value, [])


class User(Base, UUIDMixin, TimestampMixin):
    """User model with authentication and initiation tracking"""
    
    __tablename__ = "users"
    
    # Authentication fields
    username: Mapped[str] = Column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = Column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = Column(String(255), nullable=False)
    
    # Profile fields
    display_name: Mapped[Optional[str]] = Column(String(100), nullable=True)
    bio: Mapped[Optional[str]] = Column(String(500), nullable=True)
    sigil: Mapped[Optional[str]] = Column(String(10), nullable=True)  # Personal symbol
    glyphs: Mapped[List[str]] = Column(JSON, default=list)  # Visual identity markers
    
    # Initiation and trust
    initiation_level: Mapped[InitiationLevel] = Column(
        SQLEnum(InitiationLevel),
        default=InitiationLevel.OBSERVER,
        nullable=False
    )
    initiated_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)
    trust_score: Mapped[float] = Column(Float, default=0.0, nullable=False)
    reputation: Mapped[float] = Column(Float, default=1.0, nullable=False)
    
    # Deep Signal fields
    signal_coherence: Mapped[float] = Column(Float, default=1.0, nullable=False)
    fracture_index: Mapped[float] = Column(Float, default=0.0, nullable=False)
    integration_level: Mapped[float] = Column(Float, default=0.5, nullable=False)
    last_signal_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)
    
    # Personality and preferences (for matching)
    personality: Mapped[Dict[str, Any]] = Column(
        JSONB,
        default={
            "openness": 0.5,
            "chaos_tolerance": 0.5,
            "trust_preference": "progressive"
        },
        nullable=False
    )
    domains: Mapped[List[str]] = Column(JSON, default=list)  # Interest areas
    stack: Mapped[List[str]] = Column(JSON, default=list)  # Technical skills
    
    # Activity tracking
    memory_count: Mapped[int] = Column(Integer, default=0, nullable=False)
    reflection_count: Mapped[int] = Column(Integer, default=0, nullable=False)
    ritual_count: Mapped[int] = Column(Integer, default=0, nullable=False)
    consolidation_count: Mapped[int] = Column(Integer, default=0, nullable=False)
    
    # Settings and preferences
    settings: Mapped[Dict[str, Any]] = Column(
        JSONB,
        default={
            "visibility": 0.3,  # 30% public exposure
            "auto_consolidate": True,
            "agent_permissions": {},
            "notification_preferences": {},
            "privacy_level": "standard"
        },
        nullable=False
    )
    
    # Status flags
    is_active: Mapped[bool] = Column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    is_suspended: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    crisis_mode: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    intended_silence: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    
    # Authentication tracking
    last_login_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts: Mapped[int] = Column(Integer, default=0, nullable=False)
    locked_until: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)
    
    # API keys and tokens
    api_key_hash: Mapped[Optional[str]] = Column(String(255), nullable=True)
    refresh_token_hash: Mapped[Optional[str]] = Column(String(255), nullable=True)
    
    # Relationships
    memories = relationship("Memory", back_populates="user", lazy="dynamic")
    reflections = relationship("Reflection", back_populates="user", lazy="dynamic")
    signals = relationship("DeepSignal", back_populates="user", lazy="dynamic")
    trust_relationships = relationship(
        "TrustRelationship",
        foreign_keys="TrustRelationship.user_id",
        back_populates="user",
        lazy="dynamic"
    )
    trusted_by = relationship(
        "TrustRelationship",
        foreign_keys="TrustRelationship.trusted_user_id",
        back_populates="trusted_user",
        lazy="dynamic"
    )
    sharing_contracts = relationship("SharingContract", back_populates="user", lazy="dynamic")
    
    # Indexes for performance
    __table_args__ = (
        Index("ix_users_initiation_level", "initiation_level"),
        Index("ix_users_trust_score", "trust_score"),
        Index("ix_users_last_login", "last_login_at"),
        Index("ix_users_signal_coherence", "signal_coherence"),
    )
    
    def set_password(self, password: str) -> None:
        """Hash and set password"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )
    
    def advance_initiation(self) -> bool:
        """Attempt to advance to next initiation level"""
        current_index = list(InitiationLevel).index(self.initiation_level)
        
        # Check if can advance
        if current_index >= len(InitiationLevel) - 1:
            return False
        
        # Check requirements (simplified for now)
        requirements = {
            InitiationLevel.OBSERVER: {
                "memory_count": 10,
                "consolidation_count": 1
            },
            InitiationLevel.FRAGMENTOR: {
                "memory_count": 50,
                "reflection_count": 20,
                "trust_score": 0.3
            },
            InitiationLevel.AGENT: {
                "memory_count": 200,
                "ritual_count": 5,
                "trust_score": 0.6
            }
        }
        
        next_level = list(InitiationLevel)[current_index + 1]
        reqs = requirements.get(self.initiation_level, {})
        
        # Check all requirements
        for field, required in reqs.items():
            if getattr(self, field) < required:
                return False
        
        # Advance level
        self.initiation_level = next_level
        self.initiated_at = datetime.utcnow()
        return True
    
    def calculate_coherence(self) -> float:
        """Calculate overall coherence from activity patterns"""
        # Simplified coherence calculation
        base_coherence = 1.0 - self.fracture_index
        
        # Adjust based on activity
        if self.memory_count > 0:
            activity_factor = min(1.0, self.consolidation_count / (self.memory_count * 0.1))
            base_coherence = (base_coherence + activity_factor) / 2
        
        return max(0.0, min(1.0, base_coherence))
    
    def can_emit_signal(self) -> bool:
        """Check if user can emit a Deep Signal"""
        if not self.last_signal_at:
            return True
        
        # Check cooldown (15 minutes)
        cooldown_minutes = 15
        time_since_last = (datetime.utcnow() - self.last_signal_at).total_seconds() / 60
        return time_since_last >= cooldown_minutes
    
    def has_capability(self, capability: str) -> bool:
        """Check if user has a specific capability"""
        if capability in self.initiation_level.capabilities:
            return True
        if "all" in self.initiation_level.capabilities:
            return True
        return False
    
    def to_public_dict(self) -> Dict[str, Any]:
        """Get public-safe dictionary representation"""
        return {
            "id": str(self.id),
            "username": self.username,
            "display_name": self.display_name,
            "sigil": self.sigil,
            "glyphs": self.glyphs,
            "initiation_level": self.initiation_level.value,
            "initiation_symbol": self.initiation_level.symbol,
            "domains": self.domains[:3],  # Only show top 3 domains
            "signal_coherence": round(self.signal_coherence, 2),
            "visibility": self.settings.get("visibility", 0.3),
            "crisis_mode": self.crisis_mode,
            "intended_silence": self.intended_silence
        }
    
    def __repr__(self) -> str:
        return f"<User {self.username} ({self.initiation_level.value})>"