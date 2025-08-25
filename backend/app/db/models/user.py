"""
User Database Models

This module defines the database models for user authentication and management.
"""

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_model import BaseModel


class User(BaseModel):
    """
    User model for authentication and authorization.
    
    Attributes:
        id: Unique identifier for the user
        email: User's email address (unique)
        username: User's username (unique)
        hashed_password: Securely hashed password
        full_name: User's full name (optional)
        is_active: Whether the user account is active
        is_superuser: Whether the user has superuser privileges
        last_login: Timestamp of the user's last login
        api_keys: List of API keys associated with the user
    """
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    receipts = relationship("Receipt", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        """String representation of the user."""
        return f"<User {self.username}>"


class APIKey(BaseModel):
    """
    API Key model for service account authentication.
    
    Attributes:
        id: Unique identifier for the API key
        user_id: ID of the user who owns this API key
        name: Descriptive name for the API key
        key_hash: Securely hashed API key
        prefix: First few characters of the API key (for display)
        expires_at: Expiration timestamp for the API key
        is_active: Whether the API key is active
        last_used_at: Timestamp of the API key's last use
        user: Relationship to the user who owns this API key
    """
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    key_hash = Column(String, nullable=False)
    prefix = Column(String(8), nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    def __repr__(self):
        """String representation of the API key."""
        return f"<APIKey {self.name} ({self.prefix}...)>"


class UserSession(BaseModel):
    """
    User session model for tracking active sessions.
    
    Attributes:
        id: Unique identifier for the session
        user_id: ID of the user who owns this session
        refresh_token_hash: Securely hashed refresh token
        user_agent: User agent string from the client
        ip_address: IP address of the client
        expires_at: Expiration timestamp for the session
        is_active: Whether the session is active
        last_activity: Timestamp of the session's last activity
    """
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    refresh_token_hash = Column(String, nullable=False)
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    last_activity = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        """String representation of the user session."""
        return f"<UserSession {self.id}>"
