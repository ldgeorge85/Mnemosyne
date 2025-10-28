"""
Authentication Manager
Orchestrates multiple auth providers based on configuration
"""

from typing import Dict, List, Optional, Any
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param

from .base import AuthProvider, AuthResult, AuthUser, AuthMethod, AuthConfig
from .providers import (
    StaticAuthProvider,
    OAuthProvider, 
    DIDAuthProvider,
    APIKeyProvider
)
from ..config import get_settings

settings = get_settings()


class AuthManager:
    """
    Central authentication manager that coordinates multiple providers
    """
    
    def __init__(self):
        self.providers: Dict[AuthMethod, AuthProvider] = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize auth providers based on configuration"""
        
        # Get auth configuration from settings
        auth_config = getattr(settings, 'AUTH_CONFIG', {})
        
        # Default configuration if none provided
        if not auth_config:
            # Development mode: Enable static auth by default
            if settings.ENVIRONMENT in ['development', 'testing']:
                auth_config = {
                    'static': {
                        'enabled': True,
                        'priority': 100,  # Highest priority for dev
                        'settings': {}
                    },
                    'api_key': {
                        'enabled': True,
                        'priority': 90,
                        'settings': {}
                    }
                }
            else:
                # Production mode: OAuth and DID
                auth_config = {
                    'oauth_public': {
                        'enabled': True,
                        'priority': 100,
                        'settings': {
                            'public_client': True,
                            'client_id': settings.OAUTH_CLIENT_ID,
                            'authorization_url': settings.OAUTH_AUTH_URL,
                            'token_url': settings.OAUTH_TOKEN_URL,
                            'redirect_uri': settings.OAUTH_REDIRECT_URI,
                            'scope': 'openid profile email'
                        }
                    },
                    'did': {
                        'enabled': settings.W3C_DID_ENABLED,
                        'priority': 90,
                        'settings': {}
                    }
                }
        
        # Initialize configured providers
        provider_classes = {
            'static': StaticAuthProvider,
            'oauth_public': lambda cfg: OAuthProvider({**cfg, 'settings': {**cfg['settings'], 'public_client': True}}),
            'oauth_private': lambda cfg: OAuthProvider({**cfg, 'settings': {**cfg['settings'], 'public_client': False}}),
            'did': DIDAuthProvider,
            'api_key': APIKeyProvider
        }
        
        for provider_name, config_dict in auth_config.items():
            if provider_name in provider_classes:
                config = AuthConfig(**config_dict)
                if config.enabled:
                    provider_class = provider_classes[provider_name]
                    if callable(provider_class) and not isinstance(provider_class, type):
                        # It's a lambda function
                        provider = provider_class(config)
                    else:
                        # It's a class
                        provider = provider_class(config)
                    
                    self.providers[provider.method] = provider
    
    async def authenticate(
        self,
        method: AuthMethod,
        **credentials
    ) -> AuthResult:
        """
        Authenticate using specified method
        
        Args:
            method: Authentication method to use
            **credentials: Method-specific credentials
            
        Returns:
            AuthResult with user info if successful
        """
        
        # Check if provider exists and is enabled
        if method not in self.providers:
            return AuthResult(
                success=False,
                error="unsupported_method",
                error_description=f"Authentication method {method} is not available"
            )
        
        provider = self.providers[method]
        
        # Delegate to provider
        return await provider.authenticate(**credentials)
    
    async def verify_token(self, token: str) -> Optional[AuthUser]:
        """
        Verify a token with any available provider
        Tries providers in priority order
        
        Args:
            token: Access token to verify
            
        Returns:
            AuthUser if token is valid, None otherwise
        """
        
        # Sort providers by priority
        sorted_providers = sorted(
            self.providers.values(),
            key=lambda p: p.priority,
            reverse=True
        )
        
        # Try each provider
        for provider in sorted_providers:
            user = await provider.verify_token(token)
            if user:
                return user
        
        return None
    
    async def refresh_token(
        self,
        refresh_token: str,
        method: Optional[AuthMethod] = None
    ) -> Optional[AuthResult]:
        """
        Refresh an access token
        
        Args:
            refresh_token: Refresh token
            method: Optional auth method hint
            
        Returns:
            New AuthResult if successful
        """
        
        if method and method in self.providers:
            # Try specific provider
            return await self.providers[method].refresh_token(refresh_token)
        
        # Try all providers
        for provider in self.providers.values():
            result = await provider.refresh_token(refresh_token)
            if result:
                return result
        
        return None
    
    async def revoke_token(
        self,
        token: str,
        method: Optional[AuthMethod] = None
    ) -> bool:
        """
        Revoke a token
        
        Args:
            token: Token to revoke
            method: Optional auth method hint
            
        Returns:
            True if revoked successfully
        """
        
        if method and method in self.providers:
            # Try specific provider
            return await self.providers[method].revoke_token(token)
        
        # Try all providers
        for provider in self.providers.values():
            if await provider.revoke_token(token):
                return True
        
        return False
    
    def get_available_methods(self) -> List[AuthMethod]:
        """Get list of available authentication methods"""
        return list(self.providers.keys())
    
    def is_method_available(self, method: AuthMethod) -> bool:
        """Check if a specific auth method is available"""
        return method in self.providers


# Singleton instance
_auth_manager: Optional[AuthManager] = None


def get_auth_manager() -> AuthManager:
    """Get or create auth manager singleton"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager


# FastAPI dependencies
security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> AuthUser:
    """
    FastAPI dependency to get current authenticated user

    Supports multiple token sources:
    1. Authorization header (Bearer token)
    2. API-Key header
    3. Cookie (for web apps)
    """

    # Check if authentication is disabled (test mode)
    if not settings.AUTH_REQUIRED:
        # Return a test user
        return AuthUser(
            user_id="00000000-0000-0000-0000-000000000001",
            auth_method=AuthMethod.STATIC,
            username="test_user",
            email="test@example.com",
            roles=["user", "admin"],
            permissions=["*"],
            metadata={}
        )

    auth_manager = get_auth_manager()
    token = None

    # Try Authorization header
    if credentials and credentials.scheme.lower() == "bearer":
        token = credentials.credentials

    # Try API-Key header
    if not token:
        api_key = request.headers.get("X-API-Key") or request.headers.get("API-Key")
        if api_key:
            # Try API key authentication
            result = await auth_manager.authenticate(
                method=AuthMethod.API_KEY,
                api_key=api_key
            )
            if result.success and result.user:
                return result.user

    # Try cookie (for web apps)
    if not token:
        token = request.cookies.get("access_token")

    # Verify token
    if token:
        user = await auth_manager.verify_token(token)
        if user:
            return user

    # No valid authentication found
    raise HTTPException(
        status_code=401,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"}
    )


async def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[AuthUser]:
    """
    FastAPI dependency to get optional authenticated user
    Returns None if not authenticated instead of raising exception
    """
    
    try:
        return await get_current_user(request, credentials)
    except HTTPException:
        return None


def require_roles(*roles: str):
    """
    FastAPI dependency factory to require specific roles
    
    Usage:
        @router.get("/admin")
        async def admin_endpoint(user: AuthUser = Depends(require_roles("admin"))):
            ...
    """
    
    async def role_checker(user: AuthUser = Depends(get_current_user)) -> AuthUser:
        if not any(role in user.roles for role in roles):
            raise HTTPException(
                status_code=403,
                detail=f"Requires one of roles: {', '.join(roles)}"
            )
        return user
    
    return role_checker


def require_permissions(*permissions: str):
    """
    FastAPI dependency factory to require specific permissions
    
    Usage:
        @router.post("/memories")
        async def create_memory(
            user: AuthUser = Depends(require_permissions("memory:write"))
        ):
            ...
    """
    
    async def permission_checker(user: AuthUser = Depends(get_current_user)) -> AuthUser:
        # Check for wildcard permission
        if "*" in user.permissions:
            return user
        
        # Check specific permissions
        if not any(perm in user.permissions for perm in permissions):
            raise HTTPException(
                status_code=403,
                detail=f"Requires permissions: {', '.join(permissions)}"
            )
        return user
    
    return permission_checker