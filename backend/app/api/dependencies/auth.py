"""
Authentication Dependencies

This module provides authentication dependencies for API endpoints.
"""

from datetime import datetime
from typing import Dict, Any, Optional, Union
import uuid

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.security import verify_password
from app.db.models.user import User, APIKey, UserSession
from app.db.session import get_async_db
from app.schemas.auth import TokenPayload

# OAuth2 scheme for token extraction from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login", auto_error=False)

# Credentials exception for authentication failures
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Get a user by email address.
    
    Args:
        db: Database session
        email: Email address to look up
        
    Returns:
        User object if found, None otherwise
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    return user

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """
    Get a user by username.
    
    Args:
        db: Database session
        username: Username to look up
        
    Returns:
        User object if found, None otherwise
    """
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    return user

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """
    Authenticate a user with username/email and password.
    
    Args:
        db: Database session
        username: Username or email
        password: Plain text password
        
    Returns:
        User object if authentication successful, None otherwise
    """
    # Try to find user by username or email
    user = await get_user_by_username(db, username)
    if not user:
        user = await get_user_by_email(db, username)
    
    if not user:
        return None
    
    # Verify password
    if not verify_password(password, user.hashed_password):
        return None
    
    # Update last login time - this will be committed by the endpoint
    user.last_login = datetime.utcnow()
    
    return user

async def get_current_user(
    db: AsyncSession = Depends(get_async_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> User:
    """
    Get the current authenticated user from the provided token.
    
    Args:
        db: Database session
        token: The authentication token (optional)
    
    Returns:
        User object
    
    Raises:
        HTTPException: If authentication fails
    """
    # If authentication is not required, return a development user
    if not settings.AUTH_REQUIRED and not token:
        # For development purposes, return a mock user when no token is provided
        # In production, this should be removed
        mock_user = User(
            id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
            email="dev@example.com",
            username="dev_user",
            hashed_password="",
            is_active=True,
            is_superuser=True
        )
        return mock_user
    
    # Otherwise, validate the token
    if not token:
        raise credentials_exception
    
    try:
        # Decode the token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.TOKEN_ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        # Check if token is expired
        if datetime.fromtimestamp(token_data.exp) < datetime.utcnow():
            raise credentials_exception
        
        # Check if token is a refresh token
        if token_data.type == "refresh":
            raise credentials_exception
        
        # Get the user ID from the token
        user_id = token_data.sub
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get the user from the database
    try:
        user_uuid = uuid.UUID(user_id)
        result = await db.execute(select(User).where(User.id == user_uuid))
        user = result.scalars().first()
    except ValueError:
        raise credentials_exception
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get the current active user.
    
    Args:
        current_user: The current authenticated user
    
    Returns:
        User object
    
    Raises:
        HTTPException: If the user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user

async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get the current superuser.
    
    Args:
        current_user: The current authenticated user
    
    Returns:
        User object
    
    Raises:
        HTTPException: If the user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action"
        )
    return current_user

async def validate_api_key(
    api_key: str,
    db: AsyncSession
) -> Optional[User]:
    """
    Validate an API key and return the associated user.
    
    Args:
        api_key: The API key to validate
        db: Database session
        
    Returns:
        User object if API key is valid, None otherwise
    """
    if not api_key or len(api_key) < 8:
        return None
    
    # Get the prefix (first 8 characters)
    prefix = api_key[:8]
    
    # Find the API key in the database
    result = await db.execute(
        select(APIKey).where(
            APIKey.prefix == prefix,
            APIKey.is_active == True
        )
    )
    db_api_key = result.scalars().first()
    
    if not db_api_key:
        return None
    
    # Verify the API key hash
    if not verify_password(api_key, db_api_key.key_hash):
        return None
    
    # Check if the API key has expired
    if db_api_key.expires_at and db_api_key.expires_at < datetime.utcnow():
        return None
    
    # Update last used timestamp
    db_api_key.last_used_at = datetime.utcnow()
    await db.commit()
    
    # Get the associated user
    result = await db.execute(select(User).where(User.id == db_api_key.user_id))
    user = result.scalars().first()
    
    return user

async def get_api_key_user(
    request: Request,
    db: AsyncSession = Depends(get_async_db)
) -> Optional[User]:
    """
    Get the user associated with an API key from the request.
    
    Args:
        request: The HTTP request
        db: Database session
        
    Returns:
        User object if API key is valid, None otherwise
    """
    # Try to get the API key from the X-API-Key header
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return await validate_api_key(api_key, db)
    
    return None

async def get_current_user_from_token_or_api_key(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> User:
    """
    Get the current user from either a JWT token or an API key.
    
    Args:
        request: The HTTP request
        db: Database session
        token: The JWT token (optional)
        
    Returns:
        User object
        
    Raises:
        HTTPException: If authentication fails
    """
    # If authentication is not required, return a development user
    if not settings.AUTH_REQUIRED and not token:
        # For development purposes, return a mock user when no token is provided
        # In production, this should be removed
        mock_user = User(
            id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
            email="dev@example.com",
            username="dev_user",
            hashed_password="",
            is_active=True,
            is_superuser=True
        )
        return mock_user
    
    # Try to authenticate with API key first
    user = await get_api_key_user(request, db)
    if user:
        return user
    
    # Fall back to JWT token authentication
    if not token:
        raise credentials_exception
    
    try:
        # Decode the token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.TOKEN_ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        # Check if token is expired
        if datetime.fromtimestamp(token_data.exp) < datetime.utcnow():
            raise credentials_exception
        
        # Check if token is a refresh token
        if token_data.type == "refresh":
            raise credentials_exception
        
        # Get the user ID from the token
        user_id = token_data.sub
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get the user from the database
    try:
        user_uuid = uuid.UUID(user_id)
        result = await db.execute(select(User).where(User.id == user_uuid))
        user = result.scalars().first()
    except ValueError:
        raise credentials_exception
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    
    return user

async def is_admin(
    current_user: User = Depends(get_current_user_from_token_or_api_key),
) -> bool:
    """
    Check if the current user is an admin (superuser).
    
    Args:
        current_user: The current authenticated user
    
    Returns:
        True if the user is an admin, False otherwise
    
    Raises:
        HTTPException: If the user is not an admin
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required for this operation"
        )
    return True
