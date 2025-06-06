"""
Authentication Dependencies

This module provides authentication dependencies for API endpoints.
"""

from typing import Dict, Any, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# For development purposes, we'll use a simple mechanism
# In production, this should be replaced with proper JWT validation

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Get the current authenticated user from the provided token.
    For development, this returns a mock user.
    
    Args:
        token: The authentication token (optional)
    
    Returns:
        dict: User information
    
    Raises:
        HTTPException: If authentication fails
    """
    if not token:
        # For development purposes, return a mock user when no token is provided
        return {"id": "dev-user-id", "username": "dev_user", "email": "dev@example.com"}
    
    # In a real implementation, validate the token and return the user
    # For development, we'll just return a mock user
    return {"id": "mock-user-id", "username": "test_user", "email": "test@example.com", "is_admin": True}


async def is_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> bool:
    """
    Check if the current user is an administrator.
    
    Args:
        current_user: The current authenticated user
    
    Returns:
        bool: True if the user is an admin, False otherwise
    
    Raises:
        HTTPException: If the user is not an admin
    """
    # In a real implementation, check user roles
    # For development, we'll assume the user is an admin
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action"
        )
    return True
