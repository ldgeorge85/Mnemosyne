"""
Simple Authentication for Development
Provides basic auth endpoints that work without complex dependencies
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import jwt

from app.core.config import settings

router = APIRouter()

# Simple user database for development
USERS_DB = {
    "test": {"password": "test123", "email": "test@example.com", "id": "test-001"},
    "admin": {"password": "admin123", "email": "admin@example.com", "id": "admin-001"},
}

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

@router.post("/auth/simple/login", response_model=TokenResponse)
async def simple_login(request: LoginRequest):
    """
    Simple login endpoint for development
    """
    # Check credentials
    user = USERS_DB.get(request.username)
    if not user or user["password"] != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    
    # Create a simple JWT token
    token_data = {
        "sub": user["id"],
        "username": request.username,
        "email": user["email"],
        "exp": datetime.utcnow() + timedelta(hours=24),
    }
    
    access_token = jwt.encode(token_data, settings.SECRET_KEY, algorithm="HS256")
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": user["id"],
            "username": request.username,
            "email": user["email"],
        }
    )

# Add a dev-login endpoint that's easier to use
@router.post("/auth/dev-login")
async def dev_login(request: LoginRequest):
    """
    Development login - works with username/password
    """
    # Check if it's one of our test users
    if request.username == "test" and request.password == "test123":
        return {
            "access_token": "dev-token-test",
            "refresh_token": "dev-refresh-test", 
            "token_type": "bearer"
        }
    elif request.username == "admin" and request.password == "admin123":
        return {
            "access_token": "dev-token-admin",
            "refresh_token": "dev-refresh-admin",
            "token_type": "bearer"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@router.get("/auth/simple/me")
async def get_current_user_simple():
    """
    Get current user (returns test user for development)
    """
    return {
        "id": "test-001",
        "username": "test",
        "email": "test@example.com",
    }

@router.post("/auth/simple/logout")
async def simple_logout():
    """
    Simple logout (just returns success)
    """
    return {"message": "Logged out successfully"}