"""
Concrete Authentication Provider Implementations
"""

import secrets
import hashlib
import jwt
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Any, List
from passlib.context import CryptContext

from .base import AuthProvider, AuthResult, AuthUser, AuthMethod, AuthConfig
from ..config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class StaticAuthProvider(AuthProvider):
    """
    Static username/password authentication for development and testing
    Users are defined in configuration or environment variables
    """
    
    def __init__(self, config: AuthConfig):
        super().__init__(config)
        
        # Default test users if none configured (with proper UUIDs)
        self.users = config.settings.get("users", {
            "test": {
                "password": "test123",
                "user_id": "11111111-1111-1111-1111-111111111111",  # Fixed UUID for test user
                "email": "test@mnemosyne.local",
                "display_name": "Test User",
                "roles": ["user"],
                "permissions": ["memory:read", "memory:write"]
            },
            "testuser": {
                "password": "testpass123",
                "user_id": "baf1eeca-1e9f-453c-8e74-31dbbfe26631",  # Match actual DB user
                "email": "testuser@example.com",
                "display_name": "Test User",
                "roles": ["user"],
                "permissions": ["memory:read", "memory:write"]
            },
            "admin": {
                "password": "admin123",
                "user_id": "22222222-2222-2222-2222-222222222222",  # Fixed UUID for admin
                "email": "admin@mnemosyne.local",
                "display_name": "Admin User",
                "roles": ["admin"],
                "permissions": ["*"]
            },
            "demo": {
                "password": "demo123",
                "user_id": "33333333-3333-3333-3333-333333333333",  # Fixed UUID for demo
                "email": "demo@mnemosyne.local",
                "display_name": "Demo User",
                "roles": ["user"],
                "permissions": ["memory:read"]
            }
        })
        
        # Hash passwords if not already hashed
        for username, user_data in self.users.items():
            if "password" in user_data and not user_data["password"].startswith("$2b$"):
                user_data["password_hash"] = pwd_context.hash(user_data["password"])
            elif "password" in user_data:
                user_data["password_hash"] = user_data["password"]
    
    @property
    def method(self) -> AuthMethod:
        return AuthMethod.STATIC
    
    async def authenticate(self, username: str, password: str, **kwargs) -> AuthResult:
        """Authenticate with username and password"""
        
        # Check if user exists
        if username not in self.users:
            return AuthResult(
                success=False,
                error="invalid_credentials",
                error_description="Invalid username or password"
            )
        
        user_data = self.users[username]
        
        # Verify password
        if not pwd_context.verify(password, user_data.get("password_hash", "")):
            return AuthResult(
                success=False,
                error="invalid_credentials",
                error_description="Invalid username or password"
            )
        
        # Create user object
        user = AuthUser(
            user_id=user_data.get("user_id", username),
            username=username,
            email=user_data.get("email"),
            display_name=user_data.get("display_name", username),
            auth_method=self.method,
            roles=user_data.get("roles", ["user"]),
            permissions=user_data.get("permissions", [])
        )
        
        # Generate simple JWT token
        access_token = self._generate_token(user)
        refresh_token = secrets.token_urlsafe(48)
        
        # Store refresh token (in production, use Redis)
        # For now, we'll skip refresh token storage in static auth
        
        return AuthResult(
            success=True,
            user=user,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=3600  # 1 hour
        )
    
    async def verify_token(self, token: str) -> Optional[AuthUser]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=["HS256"]
            )
            
            # Recreate user from token
            return AuthUser(
                user_id=payload["sub"],
                username=payload.get("username"),
                email=payload.get("email"),
                display_name=payload.get("display_name"),
                auth_method=AuthMethod(payload.get("auth_method", "static")),
                roles=payload.get("roles", []),
                permissions=payload.get("permissions", [])
            )
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def _generate_token(self, user: AuthUser) -> str:
        """Generate JWT token for user"""
        payload = {
            "sub": user.user_id,
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "auth_method": user.auth_method.value,
            "roles": user.roles,
            "permissions": user.permissions,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc),
            "iss": "mnemosyne-static"
        }
        
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


class OAuthProvider(AuthProvider):
    """
    OAuth 2.0 authentication provider
    Supports both public clients (PKCE) and confidential clients
    """
    
    def __init__(self, config: AuthConfig):
        super().__init__(config)
        
        # Import the OAuth implementation
        from .oauth import OAuth2Provider
        self.oauth = OAuth2Provider()
        
        # OAuth specific settings
        self.client_id = config.settings.get("client_id")
        self.client_secret = config.settings.get("client_secret")
        self.authorization_url = config.settings.get("authorization_url")
        self.token_url = config.settings.get("token_url")
        self.redirect_uri = config.settings.get("redirect_uri", "http://localhost:3000/callback")
        self.scope = config.settings.get("scope", "openid profile email")
        
        # Determine if public or private client
        self.is_public = config.settings.get("public_client", False)
    
    @property
    def method(self) -> AuthMethod:
        return AuthMethod.OAUTH_PUBLIC if self.is_public else AuthMethod.OAUTH_PRIVATE
    
    async def authenticate(
        self,
        code: Optional[str] = None,
        state: Optional[str] = None,
        code_verifier: Optional[str] = None,
        **kwargs
    ) -> AuthResult:
        """Exchange authorization code for tokens"""
        
        if not code:
            return AuthResult(
                success=False,
                error="missing_code",
                error_description="Authorization code is required"
            )
        
        try:
            # Exchange code for token
            token_response = self.oauth.token(
                grant_type="authorization_code",
                client_id=self.client_id,
                client_secret=self.client_secret if not self.is_public else None,
                code=code,
                redirect_uri=self.redirect_uri,
                code_verifier=code_verifier if self.is_public else None
            )
            
            # Decode the access token to get user info
            payload = jwt.decode(
                token_response.access_token,
                settings.JWT_SECRET_KEY,
                algorithms=["HS256"]
            )
            
            # Create user from token
            user = AuthUser(
                user_id=payload["sub"],
                username=payload.get("preferred_username"),
                email=payload.get("email"),
                display_name=payload.get("name"),
                auth_method=self.method,
                roles=payload.get("roles", ["user"]),
                permissions=payload.get("permissions", [])
            )
            
            return AuthResult(
                success=True,
                user=user,
                access_token=token_response.access_token,
                refresh_token=token_response.refresh_token,
                expires_in=token_response.expires_in
            )
            
        except Exception as e:
            return AuthResult(
                success=False,
                error="oauth_error",
                error_description=str(e)
            )
    
    async def verify_token(self, token: str) -> Optional[AuthUser]:
        """Verify OAuth access token"""
        try:
            payload = self.oauth.verify_access_token(token)
            
            return AuthUser(
                user_id=payload["sub"],
                username=payload.get("preferred_username"),
                email=payload.get("email"),
                display_name=payload.get("name"),
                auth_method=self.method,
                roles=payload.get("roles", ["user"]),
                permissions=payload.get("permissions", [])
            )
        except:
            return None
    
    async def refresh_token(self, refresh_token: str) -> Optional[AuthResult]:
        """Refresh OAuth tokens"""
        try:
            token_response = self.oauth.token(
                grant_type="refresh_token",
                client_id=self.client_id,
                client_secret=self.client_secret if not self.is_public else None,
                refresh_token=refresh_token
            )
            
            # Decode to get user info
            payload = jwt.decode(
                token_response.access_token,
                settings.JWT_SECRET_KEY,
                algorithms=["HS256"]
            )
            
            user = AuthUser(
                user_id=payload["sub"],
                username=payload.get("preferred_username"),
                email=payload.get("email"),
                display_name=payload.get("name"),
                auth_method=self.method,
                roles=payload.get("roles", ["user"]),
                permissions=payload.get("permissions", [])
            )
            
            return AuthResult(
                success=True,
                user=user,
                access_token=token_response.access_token,
                refresh_token=token_response.refresh_token,
                expires_in=token_response.expires_in
            )
        except:
            return None


class DIDAuthProvider(AuthProvider):
    """
    W3C DID authentication provider
    Uses DIDs and Verifiable Credentials for authentication
    """
    
    def __init__(self, config: AuthConfig):
        super().__init__(config)
        
        # Import DID implementation
        from ..identity.did import DIDManager, DIDService
        self.did_manager = DIDManager()
        self.did_service = DIDService()
    
    @property
    def method(self) -> AuthMethod:
        return AuthMethod.DID
    
    async def authenticate(
        self,
        did: str,
        challenge: str,
        signature: str,
        **kwargs
    ) -> AuthResult:
        """Authenticate using DID signature verification"""
        
        try:
            # Verify the signature
            is_valid = self.did_manager.verify_signature(
                did,
                challenge.encode(),
                bytes.fromhex(signature)
            )
            
            if not is_valid:
                return AuthResult(
                    success=False,
                    error="invalid_signature",
                    error_description="DID signature verification failed"
                )
            
            # Resolve DID to get user info
            did_doc = await self.did_service.resolve_did(did)
            
            if not did_doc:
                return AuthResult(
                    success=False,
                    error="did_not_found",
                    error_description="Could not resolve DID"
                )
            
            # Create user from DID
            user = AuthUser(
                user_id=did,
                username=did.split(":")[-1][:8],  # Short form for display
                did=did,
                auth_method=self.method,
                roles=["user"],  # Default role
                permissions=["memory:read", "memory:write"],
                metadata={"did_document": did_doc}
            )
            
            # Generate access token
            access_token = self._generate_token(user)
            
            return AuthResult(
                success=True,
                user=user,
                access_token=access_token,
                expires_in=3600
            )
            
        except Exception as e:
            return AuthResult(
                success=False,
                error="did_auth_error",
                error_description=str(e)
            )
    
    async def verify_token(self, token: str) -> Optional[AuthUser]:
        """Verify DID auth token"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=["HS256"]
            )
            
            return AuthUser(
                user_id=payload["sub"],
                username=payload.get("username"),
                did=payload.get("did"),
                auth_method=AuthMethod.DID,
                roles=payload.get("roles", []),
                permissions=payload.get("permissions", [])
            )
        except:
            return None
    
    def _generate_token(self, user: AuthUser) -> str:
        """Generate JWT token for DID user"""
        payload = {
            "sub": user.user_id,
            "username": user.username,
            "did": user.did,
            "auth_method": user.auth_method.value,
            "roles": user.roles,
            "permissions": user.permissions,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc),
            "iss": "mnemosyne-did"
        }
        
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


class APIKeyProvider(AuthProvider):
    """
    Simple API key authentication for services and bots
    """
    
    def __init__(self, config: AuthConfig):
        super().__init__(config)
        
        # API keys configuration
        self.api_keys = config.settings.get("api_keys", {
            "test-api-key": {
                "user_id": "api-user-001",
                "service_name": "Test Service",
                "roles": ["service"],
                "permissions": ["memory:read", "memory:write"]
            }
        })
    
    @property
    def method(self) -> AuthMethod:
        return AuthMethod.API_KEY
    
    async def authenticate(self, api_key: str, **kwargs) -> AuthResult:
        """Authenticate using API key"""
        
        if api_key not in self.api_keys:
            return AuthResult(
                success=False,
                error="invalid_api_key",
                error_description="Invalid API key"
            )
        
        key_data = self.api_keys[api_key]
        
        # Create user from API key data
        user = AuthUser(
            user_id=key_data["user_id"],
            username=key_data.get("service_name", "API User"),
            auth_method=self.method,
            roles=key_data.get("roles", ["service"]),
            permissions=key_data.get("permissions", []),
            metadata={"api_key": api_key[:8] + "..."}  # Store partial key for logging
        )
        
        # For API keys, the key itself acts as the token
        # We'll generate a JWT for consistency
        access_token = self._generate_token(user)
        
        return AuthResult(
            success=True,
            user=user,
            access_token=access_token,
            expires_in=86400  # 24 hours for API keys
        )
    
    async def verify_token(self, token: str) -> Optional[AuthUser]:
        """Verify API key token"""
        # Check if it's a raw API key
        if token in self.api_keys:
            key_data = self.api_keys[token]
            return AuthUser(
                user_id=key_data["user_id"],
                username=key_data.get("service_name", "API User"),
                auth_method=self.method,
                roles=key_data.get("roles", ["service"]),
                permissions=key_data.get("permissions", [])
            )
        
        # Otherwise try as JWT
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=["HS256"]
            )
            
            if payload.get("auth_method") != AuthMethod.API_KEY.value:
                return None
            
            return AuthUser(
                user_id=payload["sub"],
                username=payload.get("username"),
                auth_method=AuthMethod.API_KEY,
                roles=payload.get("roles", []),
                permissions=payload.get("permissions", [])
            )
        except:
            return None
    
    def _generate_token(self, user: AuthUser) -> str:
        """Generate JWT token for API key user"""
        payload = {
            "sub": user.user_id,
            "username": user.username,
            "auth_method": user.auth_method.value,
            "roles": user.roles,
            "permissions": user.permissions,
            "exp": datetime.now(timezone.utc) + timedelta(days=1),
            "iat": datetime.now(timezone.utc),
            "iss": "mnemosyne-api"
        }
        
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")