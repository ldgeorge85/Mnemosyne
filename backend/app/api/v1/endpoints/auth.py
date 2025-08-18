"""
Authentication Endpoints

Provides authentication endpoints using the AuthManager system.
Supports multiple auth methods including OAuth, API Keys, and DIDs.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Response, Request
from pydantic import BaseModel

from app.core.auth.manager import get_auth_manager, get_current_user, get_optional_user
from app.core.auth.base import AuthMethod, AuthUser, AuthResult
from app.core.config import settings

router = APIRouter()


class LoginRequest(BaseModel):
    """Login request model"""
    username: Optional[str] = None
    email: Optional[str] = None
    password: str
    method: AuthMethod = AuthMethod.STATIC  # Default to static for dev


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None


class RefreshRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str
    method: Optional[AuthMethod] = None


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    response: Response
) -> TokenResponse:
    """
    Authenticate user and return tokens
    
    Supports multiple authentication methods based on configuration.
    """
    auth_manager = get_auth_manager()
    
    # Prepare credentials based on method
    credentials = {}
    if request.method == AuthMethod.STATIC:
        credentials = {
            "username": request.username or request.email,
            "password": request.password
        }
    elif request.method == AuthMethod.API_KEY:
        credentials = {
            "api_key": request.password  # Password field used for API key
        }
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Authentication method {request.method} not supported via login endpoint"
        )
    
    # Authenticate
    result = await auth_manager.authenticate(
        method=request.method,
        **credentials
    )
    
    if not result.success:
        raise HTTPException(
            status_code=401,
            detail=result.error_description or "Authentication failed"
        )
    
    # Set cookie for web clients
    if result.access_token:
        response.set_cookie(
            key="access_token",
            value=result.access_token,
            httponly=True,
            secure=settings.APP_ENV == "production",
            samesite="lax",
            max_age=result.expires_in or 3600
        )
    
    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        token_type="bearer",
        expires_in=result.expires_in
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshRequest
) -> TokenResponse:
    """
    Refresh access token using refresh token
    """
    auth_manager = get_auth_manager()
    
    result = await auth_manager.refresh_token(
        refresh_token=request.refresh_token,
        method=request.method
    )
    
    if not result or not result.success:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )
    
    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        token_type="bearer",
        expires_in=result.expires_in
    )


@router.post("/logout")
async def logout(
    response: Response,
    user: AuthUser = Depends(get_current_user)
) -> dict:
    """
    Logout current user
    
    Clears authentication cookies and optionally revokes tokens.
    """
    # Clear cookie
    response.delete_cookie(
        key="access_token",
        secure=settings.APP_ENV == "production",
        samesite="lax"
    )
    
    return {"message": "Successfully logged out"}


@router.get("/me")
async def get_me(
    user: AuthUser = Depends(get_current_user)
) -> dict:
    """
    Get current authenticated user information
    """
    return {
        "id": user.user_id,
        "username": user.username,
        "email": user.email,
        "roles": user.roles,
        "permissions": user.permissions,
        "metadata": user.metadata
    }


@router.get("/methods")
async def get_auth_methods() -> dict:
    """
    Get available authentication methods
    
    Returns list of configured authentication methods that clients can use.
    """
    auth_manager = get_auth_manager()
    methods = auth_manager.get_available_methods()
    
    return {
        "methods": [method.value for method in methods],
        "oauth_enabled": AuthMethod.OAUTH_PUBLIC in methods or AuthMethod.OAUTH_PRIVATE in methods,
        "did_enabled": AuthMethod.DID in methods,
        "api_key_enabled": AuthMethod.API_KEY in methods
    }


@router.get("/verify")
async def verify_auth(
    user: Optional[AuthUser] = Depends(get_optional_user)
) -> dict:
    """
    Verify if current request is authenticated
    
    Returns authentication status without requiring auth.
    Useful for checking auth state from frontend.
    """
    return {
        "authenticated": user is not None,
        "user": {
            "id": user.user_id,
            "username": user.username,
            "email": user.email
        } if user else None
    }