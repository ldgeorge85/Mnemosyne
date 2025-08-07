"""
API Dependencies for Mnemosyne Protocol
Handles authentication, database sessions, and common dependencies
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from datetime import datetime, timezone

from core.database import get_db
from core.config import get_settings
from models.user import User
from core.redis_client import redis_manager

settings = get_settings()
security = HTTPBearer()


async def get_redis():
    """Get Redis client instance"""
    return redis_manager


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Validate JWT token and return current user
    """
    token = credentials.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        # Check token expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = await db.get(User, user_id)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure user is active"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


class RateLimiter:
    """Simple rate limiter using Redis"""
    
    def __init__(self, times: int = 10, seconds: int = 60):
        self.times = times
        self.seconds = seconds
    
    async def __call__(
        self, 
        user: User = Depends(get_current_user),
        redis: RedisClient = Depends(get_redis)
    ) -> bool:
        """Check if user has exceeded rate limit"""
        key = f"rate_limit:{user.id}"
        
        try:
            current = await redis.client.incr(key)
            if current == 1:
                await redis.client.expire(key, self.seconds)
            
            if current > self.times:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {self.seconds} seconds."
                )
            return True
        except Exception as e:
            # If Redis fails, allow request (fail open)
            print(f"Rate limiter error: {e}")
            return True


# Common dependencies
CommonDeps = [Depends(get_db), Depends(get_current_active_user)]