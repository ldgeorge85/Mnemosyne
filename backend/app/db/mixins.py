"""
Database Mixins

This module provides reusable SQLAlchemy mixins for common database model patterns.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String, func


class TimestampMixin:
    """
    Adds created_at and updated_at fields to a model.
    """
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


class UUIDMixin:
    """
    Adds a UUID primary key field to a model.
    """
    id = Column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4()),
        index=True
    )
