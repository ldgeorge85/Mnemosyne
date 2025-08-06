"""
Authentication Schemas

This module defines Pydantic schemas for authentication-related data validation.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, UUID4, validator
import re


class UserBase(BaseModel):
    """
    Base schema for user data.
    
    Attributes:
        email: User's email address
        username: User's username
        full_name: User's full name (optional)
    """
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """
    Schema for user creation.
    
    Attributes:
        password: User's password (plain text, will be hashed)
    """
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_strength(cls, v):
        """
        Validate password strength.
        
        Args:
            v: Password to validate
            
        Returns:
            The password if valid
            
        Raises:
            ValueError: If the password doesn't meet strength requirements
        """
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[^A-Za-z0-9]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserUpdate(BaseModel):
    """
    Schema for user updates.
    
    Attributes:
        email: User's email address (optional)
        full_name: User's full name (optional)
        password: User's new password (optional)
    """
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength if provided."""
        if v is None:
            return v
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[^A-Za-z0-9]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserInDB(UserBase):
    """
    Schema for user data from the database.
    
    Attributes:
        id: User's unique identifier
        is_active: Whether the user account is active
        is_superuser: Whether the user has superuser privileges
        created_at: When the user was created
        updated_at: When the user was last updated
        last_login: When the user last logged in
    """
    id: UUID4
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class UserResponse(UserBase):
    """
    Schema for user data in API responses.
    
    Attributes:
        id: User's unique identifier
        is_active: Whether the user account is active
        is_superuser: Whether the user has superuser privileges
    """
    id: UUID4
    is_active: bool
    is_superuser: bool
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class Token(BaseModel):
    """
    Schema for authentication tokens.
    
    Attributes:
        access_token: JWT access token
        refresh_token: JWT refresh token for obtaining new access tokens
        token_type: Type of token (always "bearer")
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """
    Schema for JWT token payload.
    
    Attributes:
        sub: Subject of the token (user ID)
        exp: Expiration timestamp
        type: Token type (access or refresh)
    """
    sub: str
    exp: int
    type: Optional[str] = "access"


class LoginRequest(BaseModel):
    """
    Schema for login requests.
    
    Attributes:
        username: Username or email
        password: Password
    """
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    """
    Schema for refresh token requests.
    
    Attributes:
        refresh_token: JWT refresh token
    """
    refresh_token: str


class APIKeyCreate(BaseModel):
    """
    Schema for API key creation.
    
    Attributes:
        name: Descriptive name for the API key
        expires_in_days: Number of days until the API key expires (optional)
    """
    name: str = Field(..., min_length=1, max_length=100)
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)


class APIKeyResponse(BaseModel):
    """
    Schema for API key responses.
    
    Attributes:
        id: API key's unique identifier
        name: Descriptive name for the API key
        prefix: First few characters of the API key
        key: Full API key (only included when first created)
        expires_at: When the API key expires
        created_at: When the API key was created
        last_used_at: When the API key was last used
    """
    id: UUID4
    name: str
    prefix: str
    key: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    last_used_at: Optional[datetime] = None
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
