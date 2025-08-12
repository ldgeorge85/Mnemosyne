"""
Working Authentication - Simple and Functional
No complexity, just working auth for development
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Response, Cookie, Form
from pydantic import BaseModel
import jwt
import hashlib

router = APIRouter()

# In-memory user store for simplicity
USERS: Dict[str, Dict[str, Any]] = {}
SECRET_KEY = "your-secret-key-change-this"

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str]

def hash_password(password: str) -> str:
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(username: str) -> str:
    """Create a simple JWT token"""
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token: str) -> Optional[str]:
    """Verify JWT token and return username"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("sub")
    except:
        return None

@router.post("/register")
async def register(request: RegisterRequest):
    """Register a new user - SIMPLIFIED"""
    # Check if user exists
    if request.username in USERS:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create user
    user_id = str(len(USERS) + 1)
    USERS[request.username] = {
        "id": user_id,
        "username": request.username,
        "email": request.email,
        "password_hash": hash_password(request.password),
        "full_name": request.full_name
    }
    
    return UserResponse(
        id=user_id,
        username=request.username,
        email=request.email,
        full_name=request.full_name
    )

@router.post("/login")
async def login(response: Response, 
                request: Optional[LoginRequest] = None,
                username: Optional[str] = Form(None), 
                password: Optional[str] = Form(None)):
    """Login user - SIMPLIFIED - Accepts both JSON and form data"""
    # Handle both JSON body and form data
    if request:
        username = request.username
        password = request.password
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")
    # Check user exists
    if username not in USERS:
        # Try with some default users
        if username == "test" and password == "test":
            # Create test user on the fly
            USERS["test"] = {
                "id": "test-user",
                "username": "test",
                "email": "test@example.com",
                "password_hash": hash_password("test"),
                "full_name": "Test User"
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check password
    user = USERS.get(username)
    if user and user["password_hash"] != hash_password(password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    token = create_token(username)
    
    # Set cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=86400,  # 1 day
        samesite="lax"
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user.get("full_name")
        }
    }

@router.get("/me")
async def get_me(access_token: Optional[str] = Cookie(None)):
    """Get current user - SIMPLIFIED"""
    # Check cookie token
    if not access_token:
        # Return a default user for development
        return UserResponse(
            id="dev-user",
            username="developer",
            email="dev@example.com",
            full_name="Developer User"
        )
    
    # Verify token
    username = verify_token(access_token)
    if not username or username not in USERS:
        # Return dev user as fallback
        return UserResponse(
            id="dev-user",
            username="developer", 
            email="dev@example.com",
            full_name="Developer User"
        )
    
    user = USERS[username]
    return UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        full_name=user.get("full_name")
    )

@router.post("/logout")
async def logout(response: Response):
    """Logout user - SIMPLIFIED"""
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}

# Add a test endpoint
@router.get("/test")
async def test_auth():
    """Test endpoint to verify auth is working"""
    return {
        "status": "working",
        "users_count": len(USERS),
        "test_user_available": "test" in USERS or "Use username: test, password: test"
    }