"""
Modular Authentication API Endpoints
Supports multiple auth methods with easy switching
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from app.core.auth import AuthManager, AuthUser, AuthMethod
from app.core.auth.manager import get_auth_manager, get_current_user, get_optional_user

router = APIRouter(prefix="/auth", tags=["authentication"])


# Request/Response models
class LoginRequest(BaseModel):
    """Static auth login request"""
    username: str
    password: str


class OAuthCodeRequest(BaseModel):
    """OAuth authorization code exchange request"""
    code: str
    state: Optional[str] = None
    code_verifier: Optional[str] = None  # For PKCE


class DIDAuthRequest(BaseModel):
    """DID authentication request"""
    did: str
    challenge: str
    signature: str


class APIKeyRequest(BaseModel):
    """API key authentication request"""
    api_key: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None


class UserResponse(BaseModel):
    """User info response"""
    user_id: str
    username: Optional[str] = None
    email: Optional[str] = None
    display_name: Optional[str] = None
    did: Optional[str] = None
    auth_method: str
    roles: list = Field(default_factory=list)
    permissions: list = Field(default_factory=list)


class AuthMethodsResponse(BaseModel):
    """Available auth methods response"""
    methods: list[str]
    preferred: Optional[str] = None


@router.get("/methods", response_model=AuthMethodsResponse)
async def get_auth_methods():
    """
    Get available authentication methods
    """
    auth_manager = get_auth_manager()
    methods = auth_manager.get_available_methods()
    
    # Determine preferred method based on priority
    preferred = None
    if methods:
        # Get the method with highest priority
        sorted_methods = sorted(
            [(m, auth_manager.providers[m].priority) for m in methods],
            key=lambda x: x[1],
            reverse=True
        )
        preferred = sorted_methods[0][0].value if sorted_methods else None
    
    return AuthMethodsResponse(
        methods=[m.value for m in methods],
        preferred=preferred
    )


@router.post("/login", response_model=TokenResponse)
async def login_static(request: LoginRequest):
    """
    Login with static username/password (for development/testing)
    """
    auth_manager = get_auth_manager()
    
    # Check if static auth is available
    if not auth_manager.is_method_available(AuthMethod.STATIC):
        raise HTTPException(
            status_code=400,
            detail="Static authentication is not enabled"
        )
    
    # Authenticate
    result = await auth_manager.authenticate(
        method=AuthMethod.STATIC,
        username=request.username,
        password=request.password
    )
    
    if not result.success:
        raise HTTPException(
            status_code=401,
            detail=result.error_description or "Authentication failed"
        )
    
    return TokenResponse(
        access_token=result.access_token,
        expires_in=result.expires_in,
        refresh_token=result.refresh_token
    )


@router.post("/oauth/token", response_model=TokenResponse)
async def oauth_token_exchange(request: OAuthCodeRequest):
    """
    Exchange OAuth authorization code for tokens
    Supports both public clients (PKCE) and confidential clients
    """
    auth_manager = get_auth_manager()
    
    # Determine if using public or private OAuth
    method = AuthMethod.OAUTH_PUBLIC if request.code_verifier else AuthMethod.OAUTH_PRIVATE
    
    if not auth_manager.is_method_available(method):
        raise HTTPException(
            status_code=400,
            detail=f"OAuth authentication ({method.value}) is not enabled"
        )
    
    # Exchange code for token
    result = await auth_manager.authenticate(
        method=method,
        code=request.code,
        state=request.state,
        code_verifier=request.code_verifier
    )
    
    if not result.success:
        raise HTTPException(
            status_code=401,
            detail=result.error_description or "Token exchange failed"
        )
    
    return TokenResponse(
        access_token=result.access_token,
        expires_in=result.expires_in,
        refresh_token=result.refresh_token
    )


@router.post("/did/authenticate", response_model=TokenResponse)
async def authenticate_with_did(request: DIDAuthRequest):
    """
    Authenticate using W3C DID
    """
    auth_manager = get_auth_manager()
    
    if not auth_manager.is_method_available(AuthMethod.DID):
        raise HTTPException(
            status_code=400,
            detail="DID authentication is not enabled"
        )
    
    # Authenticate with DID
    result = await auth_manager.authenticate(
        method=AuthMethod.DID,
        did=request.did,
        challenge=request.challenge,
        signature=request.signature
    )
    
    if not result.success:
        raise HTTPException(
            status_code=401,
            detail=result.error_description or "DID authentication failed"
        )
    
    return TokenResponse(
        access_token=result.access_token,
        expires_in=result.expires_in
    )


@router.post("/api-key/authenticate", response_model=TokenResponse)
async def authenticate_with_api_key(request: APIKeyRequest):
    """
    Authenticate using API key
    """
    auth_manager = get_auth_manager()
    
    if not auth_manager.is_method_available(AuthMethod.API_KEY):
        raise HTTPException(
            status_code=400,
            detail="API key authentication is not enabled"
        )
    
    # Authenticate with API key
    result = await auth_manager.authenticate(
        method=AuthMethod.API_KEY,
        api_key=request.api_key
    )
    
    if not result.success:
        raise HTTPException(
            status_code=401,
            detail=result.error_description or "Invalid API key"
        )
    
    return TokenResponse(
        access_token=result.access_token,
        expires_in=result.expires_in
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """
    Refresh access token using refresh token
    """
    auth_manager = get_auth_manager()
    
    result = await auth_manager.refresh_token(refresh_token)
    
    if not result or not result.success:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )
    
    return TokenResponse(
        access_token=result.access_token,
        expires_in=result.expires_in,
        refresh_token=result.refresh_token
    )


@router.post("/logout")
async def logout(
    response: Response,
    user: AuthUser = Depends(get_current_user)
):
    """
    Logout current user
    """
    auth_manager = get_auth_manager()
    
    # Revoke token if possible
    # In production, add token to blacklist
    
    # Clear cookie if used
    response.delete_cookie("access_token")
    
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: AuthUser = Depends(get_current_user)):
    """
    Get current authenticated user information
    """
    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        display_name=user.display_name,
        did=user.did,
        auth_method=user.auth_method.value,
        roles=user.roles,
        permissions=user.permissions
    )


@router.get("/verify")
async def verify_token(user: Optional[AuthUser] = Depends(get_optional_user)):
    """
    Verify if current token is valid
    """
    if user:
        return {
            "valid": True,
            "user_id": user.user_id,
            "auth_method": user.auth_method.value
        }
    else:
        return {"valid": False}


# OAuth 2.0 password flow for compatibility (maps to static auth)
@router.post("/token", response_model=TokenResponse)
async def login_oauth_password_flow(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token endpoint (password flow)
    Maps to static auth for development
    """
    auth_manager = get_auth_manager()
    
    # Use static auth provider
    result = await auth_manager.authenticate(
        method=AuthMethod.STATIC,
        username=form_data.username,
        password=form_data.password
    )
    
    if not result.success:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return TokenResponse(
        access_token=result.access_token,
        expires_in=result.expires_in,
        refresh_token=result.refresh_token
    )


# Health check endpoint (no auth required)
@router.get("/health")
async def auth_health_check():
    """
    Check auth service health
    """
    auth_manager = get_auth_manager()
    methods = auth_manager.get_available_methods()
    
    return {
        "status": "healthy",
        "available_methods": len(methods),
        "methods": [m.value for m in methods]
    }