"""
Dead Simple Auth - Just Works
"""

from fastapi import APIRouter, Response, Form, HTTPException
from typing import Optional
import json

router = APIRouter()

# Hardcoded users for development
USERS = {
    "test": {"password": "test", "email": "test@example.com", "id": "1"},
    "admin": {"password": "admin", "email": "admin@example.com", "id": "2"},
    "demo": {"password": "demo", "email": "demo@example.com", "id": "3"}
}

@router.post("/login")
async def login(
    response: Response,
    username: str = Form(...),
    password: str = Form(...)
):
    """Simple login that just works with form data"""
    # Check credentials
    user = USERS.get(username)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Set a simple cookie
    response.set_cookie(
        key="user",
        value=username,
        httponly=False,  # Allow JS access for simplicity
        max_age=86400
    )
    
    return {
        "access_token": f"token-{username}",
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": username,
            "email": user["email"]
        }
    }

@router.get("/me")
async def get_me(user: Optional[str] = None):
    """Get current user - returns test user if not logged in"""
    if user and user in USERS:
        return {
            "id": USERS[user]["id"],
            "username": user,
            "email": USERS[user]["email"]
        }
    
    # Return test user by default
    return {
        "id": "1",
        "username": "test",
        "email": "test@example.com"
    }

@router.post("/logout")
async def logout(response: Response):
    """Simple logout"""
    response.delete_cookie(key="user")
    return {"message": "Logged out"}

@router.post("/register")
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    """Register new user"""
    if username in USERS:
        raise HTTPException(status_code=400, detail="User already exists")
    
    USERS[username] = {
        "password": password,
        "email": email,
        "id": str(len(USERS) + 1)
    }
    
    return {
        "id": USERS[username]["id"],
        "username": username,
        "email": email
    }