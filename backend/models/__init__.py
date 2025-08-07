"""
Database models for Mnemosyne Protocol
Central model registry and base classes
"""

from sqlalchemy import Column, DateTime, String, Float, Integer, Boolean, Text, JSON, ForeignKey, Index, UUID as SQLAlchemyUUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import VECTOR, JSONB
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime

from backend.core.database import Base, TimestampMixin, UUIDMixin, SoftDeleteMixin

# Base model with common functionality
class BaseModel(Base, UUIDMixin, TimestampMixin):
    """Base model with UUID, timestamps, and common methods"""
    __abstract__ = True
    
    def to_dict(self, exclude: Optional[List[str]] = None) -> Dict[str, Any]:
        """Convert model to dictionary"""
        exclude = exclude or []
        data = {}
        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                if isinstance(value, datetime):
                    value = value.isoformat()
                elif isinstance(value, uuid.UUID):
                    value = str(value)
                data[column.name] = value
        return data
    
    def update(self, **kwargs) -> None:
        """Update model attributes"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


# Import all models to ensure they're registered with SQLAlchemy
# These will be created in subsequent steps
from backend.models.user import User
from backend.models.memory import Memory
from backend.models.reflection import Reflection
from backend.models.signal import DeepSignal
from backend.models.sharing import SharingContract, TrustRelationship

# Export all models
__all__ = [
    "BaseModel",
    "User",
    "Memory",
    "Reflection",
    "DeepSignal",
    "SharingContract",
    "TrustRelationship",
]