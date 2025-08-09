"""
Base Authentication Provider Interface
All auth providers must implement this interface
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from enum import Enum


class AuthMethod(str, Enum):
    """Available authentication methods"""
    STATIC = "static"  # Username/password for dev/test
    OAUTH_PUBLIC = "oauth_public"  # OAuth with PKCE (no client secret)
    OAUTH_PRIVATE = "oauth_private"  # OAuth with client secret
    DID = "did"  # W3C DID authentication
    WEBAUTHN = "webauthn"  # WebAuthn/FIDO2
    API_KEY = "api_key"  # Simple API key auth


class AuthUser(BaseModel):
    """Authenticated user information"""
    user_id: str
    username: Optional[str] = None
    email: Optional[str] = None
    display_name: Optional[str] = None
    did: Optional[str] = None  # W3C DID if available
    auth_method: AuthMethod
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    authenticated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuthResult(BaseModel):
    """Authentication result"""
    success: bool
    user: Optional[AuthUser] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None  # seconds
    error: Optional[str] = None
    error_description: Optional[str] = None


class AuthConfig(BaseModel):
    """Configuration for auth provider"""
    enabled: bool = True
    priority: int = 0  # Higher priority providers are tried first
    settings: Dict[str, Any] = Field(default_factory=dict)


class AuthProvider(ABC):
    """
    Abstract base class for authentication providers
    All providers must implement these methods
    """
    
    def __init__(self, config: AuthConfig):
        self.config = config
        self.enabled = config.enabled
        self.priority = config.priority
    
    @property
    @abstractmethod
    def method(self) -> AuthMethod:
        """Return the authentication method this provider handles"""
        pass
    
    @abstractmethod
    async def authenticate(self, **credentials) -> AuthResult:
        """
        Authenticate a user with provided credentials
        
        Args:
            **credentials: Provider-specific credentials
            
        Returns:
            AuthResult with user info if successful
        """
        pass
    
    @abstractmethod
    async def verify_token(self, token: str) -> Optional[AuthUser]:
        """
        Verify an access token and return user info
        
        Args:
            token: Access token to verify
            
        Returns:
            AuthUser if token is valid, None otherwise
        """
        pass
    
    async def refresh_token(self, refresh_token: str) -> Optional[AuthResult]:
        """
        Refresh an access token (optional implementation)
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New AuthResult if successful
        """
        return None
    
    async def revoke_token(self, token: str) -> bool:
        """
        Revoke a token (optional implementation)
        
        Args:
            token: Token to revoke
            
        Returns:
            True if revoked successfully
        """
        return False
    
    def can_handle(self, auth_method: AuthMethod) -> bool:
        """Check if this provider can handle the given auth method"""
        return self.enabled and auth_method == self.method