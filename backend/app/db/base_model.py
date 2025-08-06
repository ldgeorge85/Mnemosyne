"""
Base Database Model

This module provides a base model with common fields and functionality
for all database models in the application.
"""

import uuid
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Column, DateTime, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_mixin

from app.utils.common import utc_now
from app.db.session import Base


@declarative_mixin
class TimestampMixin:
    """
    Mixin to add created_at and updated_at timestamp fields to models.
    """
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)


class BaseModel(Base, TimestampMixin):
    """
    Abstract base model class that all models should inherit from.
    Provides common fields and functionality for all models.
    """
    __abstract__ = True
    
    # Use lowercase table names
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    # Use UUID as primary key
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the model instance to a dictionary.
        
        Returns:
            A dictionary representation of the model
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    def __repr__(self) -> str:
        """
        String representation of the model instance.
        
        Returns:
            A string showing class name and ID
        """
        return f"<{self.__class__.__name__} {self.id}>"
