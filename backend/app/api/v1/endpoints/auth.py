"""
Authentication Endpoints

This module provides API endpoints for user authentication, registration, and token management.
"""

from datetime import datetime, timedelta
import secrets
import uuid
from typing import Any
import jwt
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.dependencies.auth import (
    authenticate_user,
    get_current_active_user,
    get_current_superuser,
    get_user_by_email,
    get_user_by_username,
)
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.db.models.user import User, APIKey, UserSession
from app.db.session import get_async_db
from app.schemas.auth import (
    UserCreate,
    UserResponse,
    Token,
    RefreshTokenRequest,
    APIKeyCreate,
    APIKeyResponse,
)
from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Register a new user.
    
    Args:
        user_in: User creation data
        db: Database session
        
    Returns:
        Newly created user
        
    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username already exists
    existing_user = await get_user_by_username(db, user_in.username)
    if existing_user:
        raise ConflictError(
            message="Username already registered",
            details={"field": "username", "value": user_in.username}
        )
    
    # Check if email already exists
    existing_user = await get_user_by_email(db, user_in.email)
    if existing_user:
        raise ConflictError(
            message="Email already registered",
            details={"field": "email", "value": user_in.email}
        )
    
    # Create new user
    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_active=True,
        is_superuser=False,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


@router.post("/login", response_model=Token)
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    
    Args:
        response: FastAPI response object for setting cookies
        form_data: OAuth2 password request form
        db: Database session
        
    Returns:
        Access and refresh tokens
        
    Raises:
        HTTPException: If authentication fails
    """
    # Debug logging
    logger.info("Login attempt - Username: %s, Password length: %s", form_data.username, len(form_data.password) if form_data.password else 0)
    
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning("Authentication failed for username: %s", form_data.username)
        raise AuthenticationError(
            message="Incorrect username or password",
            details={"username": form_data.username}
        )
    
    if not user.is_active:
        raise AuthenticationError(
            message="Account has been deactivated",
            details={"username": form_data.username, "active": False}
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=access_token_expires,
    )
    
    # Create refresh token
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        subject=str(user.id),
        expires_delta=refresh_token_expires,
    )
    
    # Store refresh token in database
    refresh_token_hash = get_password_hash(refresh_token)
    session = UserSession(
        user_id=user.id,
        refresh_token_hash=refresh_token_hash,
        expires_at=datetime.utcnow() + refresh_token_expires,
        is_active=True,
    )
    
    db.add(session)
    await db.commit()
    
    # Set cookies
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=settings.APP_ENV == "production",
        samesite="strict",
        max_age=access_token_expires.total_seconds(),
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.APP_ENV == "production",
        samesite="strict",
        max_age=refresh_token_expires.total_seconds(),
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    response: Response,
    refresh_token_req: RefreshTokenRequest,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Refresh access token using refresh token.
    
    Args:
        response: FastAPI response object for setting cookies
        refresh_token_req: Refresh token request
        db: Database session
        
    Returns:
        New access and refresh tokens
        
    Raises:
        HTTPException: If refresh token is invalid or expired
    """
    try:
        # Decode the refresh token
        payload = jwt.decode(
            refresh_token_req.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.TOKEN_ALGORITHM],
        )
        
        # Check if token is a refresh token
        if payload.get("type") != "refresh":
            raise AuthenticationError(
                message="Invalid refresh token",
                details={"reason": "Token type mismatch"}
            )
        
        # Get the user ID from the token
        user_id = payload.get("sub")
        if user_id is None:
            raise AuthenticationError(
                message="Invalid refresh token",
                details={"reason": "Missing user ID"}
            )
        
        # Find the user session with this refresh token
        user_uuid = uuid.UUID(user_id)
        result = await db.execute(
            select(UserSession).where(
                UserSession.user_id == user_uuid,
                UserSession.is_active == True,
            )
        )
        sessions = result.scalars().all()
        
        # Verify the refresh token against stored hashes
        session_found = False
        for session in sessions:
            if verify_password(refresh_token_req.refresh_token, session.refresh_token_hash):
                session_found = True
                
                # Check if session has expired
                if session.expires_at < datetime.utcnow():
                    session.is_active = False
                    await db.commit()
                    raise AuthenticationError(
                        message="Refresh token expired",
                        details={"expired_at": session.expires_at.isoformat()}
                    )
                
                # Invalidate the old refresh token
                session.is_active = False
                await db.commit()
                break
        
        if not session_found:
            raise AuthenticationError(
                message="Invalid refresh token",
                details={"reason": "Token not found in active sessions"}
            )
        
        # Get the user
        result = await db.execute(select(User).where(User.id == user_uuid))
        user = result.scalars().first()
        
        if not user or not user.is_active:
            raise AuthenticationError(
                message="Invalid user or inactive user",
                details={"user_found": user is not None, "active": user.is_active if user else None}
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=str(user.id),
            expires_delta=access_token_expires,
        )
        
        # Create new refresh token
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        new_refresh_token = create_refresh_token(
            subject=str(user.id),
            expires_delta=refresh_token_expires,
        )
        
        # Store new refresh token in database
        new_refresh_token_hash = get_password_hash(new_refresh_token)
        new_session = UserSession(
            user_id=user.id,
            refresh_token_hash=new_refresh_token_hash,
            expires_at=datetime.utcnow() + refresh_token_expires,
            is_active=True,
        )
        
        db.add(new_session)
        await db.commit()
        
        # Set cookies
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=settings.APP_ENV == "production",
            samesite="strict",
            max_age=access_token_expires.total_seconds(),
        )
        
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=settings.APP_ENV == "production",
            samesite="strict",
            max_age=refresh_token_expires.total_seconds(),
        )
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
        
    except jwt.JWTError as e:
        raise AuthenticationError(
            message="Invalid refresh token",
            details={"reason": "JWT decode error", "error": str(e)}
        )


from pydantic import BaseModel
from typing import Optional

class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None

@router.post("/logout")
async def logout(
    response: Response,
    logout_req: Optional[LogoutRequest] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Logout the current user by invalidating their refresh token.
    
    Args:
        response: FastAPI response object for clearing cookies
        refresh_token: Refresh token to invalidate (optional)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    # If refresh token is provided, invalidate only that token
    refresh_token = logout_req.refresh_token if logout_req else None
    
    if refresh_token:
        result = await db.execute(
            select(UserSession).where(
                UserSession.user_id == current_user.id,
                UserSession.is_active == True,
            )
        )
        sessions = result.scalars().all()
        
        for session in sessions:
            if verify_password(refresh_token, session.refresh_token_hash):
                session.is_active = False
                break
    else:
        # Invalidate all active sessions for this user
        result = await db.execute(
            select(UserSession).where(
                UserSession.user_id == current_user.id,
                UserSession.is_active == True,
            )
        )
        sessions = result.scalars().all()
        
        for session in sessions:
            session.is_active = False
    
    await db.commit()
    
    # Clear cookies
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user information
    """
    return current_user


@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    api_key_in: APIKeyCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Create a new API key for the current user.
    
    Args:
        api_key_in: API key creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Newly created API key
    """
    # Generate a random API key
    api_key = f"{secrets.token_urlsafe(8)}.{secrets.token_urlsafe(24)}"
    prefix = api_key[:8]
    
    # Hash the API key
    key_hash = get_password_hash(api_key)
    
    # Set expiration date if requested
    expires_at = None
    if api_key_in.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=api_key_in.expires_in_days)
    
    # Create API key record
    db_api_key = APIKey(
        user_id=current_user.id,
        name=api_key_in.name,
        key_hash=key_hash,
        prefix=prefix,
        expires_at=expires_at,
        is_active=True,
    )
    
    db.add(db_api_key)
    await db.commit()
    await db.refresh(db_api_key)
    
    # Return the API key (only time it will be visible in full)
    response = APIKeyResponse(
        id=db_api_key.id,
        name=db_api_key.name,
        prefix=db_api_key.prefix,
        key=api_key,  # Include the full key only in the creation response
        expires_at=db_api_key.expires_at,
        created_at=db_api_key.created_at,
        last_used_at=None,
    )
    
    return response


@router.get("/api-keys", response_model=list[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    List all API keys for the current user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of API keys
    """
    result = await db.execute(
        select(APIKey).where(
            APIKey.user_id == current_user.id,
            APIKey.is_active == True,
        )
    )
    api_keys = result.scalars().all()
    
    return api_keys


@router.get("/verify")
async def verify_token(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Verify that the current access token is valid.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User info and token validity status
    """
    return {
        "valid": True,
        "user_id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
    }


@router.delete("/api-keys/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    api_key_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
) -> None:
    """
    Delete an API key.
    
    Args:
        api_key_id: ID of the API key to delete
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        No content
        
    Raises:
        HTTPException: If API key not found or not owned by current user
    """
    result = await db.execute(
        select(APIKey).where(
            APIKey.id == api_key_id,
            APIKey.user_id == current_user.id,
        )
    )
    api_key = result.scalars().first()
    
    if not api_key:
        raise NotFoundError(
            resource="API key",
            identifier=str(api_key_id)
        )
    
    # Soft delete by marking as inactive
    api_key.is_active = False
    await db.commit()
    
    # No return value needed for 204 No Content response
    return None


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    List all users (superuser only).
    
    Args:
        skip: Number of users to skip
        limit: Maximum number of users to return
        current_user: Current authenticated superuser
        db: Database session
        
    Returns:
        List of users
    """
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    
    return users
