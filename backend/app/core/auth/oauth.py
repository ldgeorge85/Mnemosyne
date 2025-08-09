"""
OAuth 2.0 Implementation
Track 1: Production-ready OAuth 2.0 provider
"""

import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, List, Any
from pydantic import BaseModel, Field, validator
from enum import Enum
import jwt
from urllib.parse import urlparse, parse_qs

from ..config import get_settings

settings = get_settings()


class GrantType(str, Enum):
    """OAuth 2.0 Grant Types"""
    AUTHORIZATION_CODE = "authorization_code"
    REFRESH_TOKEN = "refresh_token"
    CLIENT_CREDENTIALS = "client_credentials"
    IMPLICIT = "implicit"  # Deprecated but included for completeness


class ResponseType(str, Enum):
    """OAuth 2.0 Response Types"""
    CODE = "code"
    TOKEN = "token"  # For implicit flow (deprecated)


class TokenType(str, Enum):
    """OAuth 2.0 Token Types"""
    BEARER = "Bearer"


class OAuthClient(BaseModel):
    """OAuth 2.0 Client Registration"""
    
    client_id: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    client_secret: str = Field(default_factory=lambda: secrets.token_urlsafe(48))
    client_name: str
    redirect_uris: List[str]
    grant_types: List[GrantType] = Field(
        default=[GrantType.AUTHORIZATION_CODE, GrantType.REFRESH_TOKEN]
    )
    response_types: List[ResponseType] = Field(default=[ResponseType.CODE])
    scope: str = Field(default="openid profile email")
    contacts: List[str] = Field(default_factory=list)
    logo_uri: Optional[str] = None
    client_uri: Optional[str] = None
    policy_uri: Optional[str] = None
    tos_uri: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @validator('redirect_uris')
    def validate_redirect_uris(cls, v):
        for uri in v:
            parsed = urlparse(uri)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"Invalid redirect URI: {uri}")
            # Prevent open redirects
            if parsed.scheme not in ['http', 'https']:
                raise ValueError(f"Invalid URI scheme: {parsed.scheme}")
        return v


class AuthorizationCode(BaseModel):
    """OAuth 2.0 Authorization Code"""
    
    code: str = Field(default_factory=lambda: secrets.token_urlsafe(48))
    client_id: str
    user_id: str
    redirect_uri: str
    scope: str
    code_challenge: Optional[str] = None  # For PKCE
    code_challenge_method: Optional[str] = None  # For PKCE
    expires_at: datetime
    used: bool = Field(default=False)
    
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at
    
    def verify_pkce(self, code_verifier: str) -> bool:
        """Verify PKCE code challenge"""
        if not self.code_challenge:
            return True  # PKCE not required
        
        if self.code_challenge_method == "S256":
            # SHA256 hash of verifier
            challenge = hashlib.sha256(code_verifier.encode()).digest()
            # Base64url encode without padding
            import base64
            computed = base64.urlsafe_b64encode(challenge).decode().rstrip('=')
            return computed == self.code_challenge
        elif self.code_challenge_method == "plain":
            return code_verifier == self.code_challenge
        
        return False


class OAuthToken(BaseModel):
    """OAuth 2.0 Token Response"""
    
    access_token: str
    token_type: TokenType = TokenType.BEARER
    expires_in: int = Field(default=3600)  # 1 hour
    refresh_token: Optional[str] = None
    scope: str
    id_token: Optional[str] = None  # For OpenID Connect


class OAuth2Provider:
    """OAuth 2.0 Authorization Server"""
    
    def __init__(self):
        self.clients: Dict[str, OAuthClient] = {}
        self.authorization_codes: Dict[str, AuthorizationCode] = {}
        self.refresh_tokens: Dict[str, Dict[str, Any]] = {}
        
    def register_client(
        self,
        client_name: str,
        redirect_uris: List[str],
        **kwargs
    ) -> OAuthClient:
        """
        Register a new OAuth client
        Dynamic Client Registration (RFC 7591)
        """
        client = OAuthClient(
            client_name=client_name,
            redirect_uris=redirect_uris,
            **kwargs
        )
        
        self.clients[client.client_id] = client
        return client
    
    def authorize(
        self,
        client_id: str,
        user_id: str,
        redirect_uri: str,
        scope: str,
        response_type: ResponseType = ResponseType.CODE,
        state: Optional[str] = None,
        code_challenge: Optional[str] = None,
        code_challenge_method: Optional[str] = "S256"
    ) -> Dict[str, Any]:
        """
        Handle authorization request
        Returns authorization code or token
        """
        # Validate client
        if client_id not in self.clients:
            raise ValueError("Invalid client_id")
        
        client = self.clients[client_id]
        
        # Validate redirect URI
        if redirect_uri not in client.redirect_uris:
            raise ValueError("Invalid redirect_uri")
        
        # Validate response type
        if response_type not in client.response_types:
            raise ValueError("Unsupported response_type")
        
        # Validate scope
        requested_scopes = set(scope.split())
        allowed_scopes = set(client.scope.split())
        if not requested_scopes.issubset(allowed_scopes):
            raise ValueError("Invalid scope")
        
        if response_type == ResponseType.CODE:
            # Generate authorization code
            auth_code = AuthorizationCode(
                client_id=client_id,
                user_id=user_id,
                redirect_uri=redirect_uri,
                scope=scope,
                code_challenge=code_challenge,
                code_challenge_method=code_challenge_method,
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=10)
            )
            
            self.authorization_codes[auth_code.code] = auth_code
            
            response = {
                "code": auth_code.code,
                "state": state
            }
        else:
            # Implicit flow (deprecated)
            raise NotImplementedError("Implicit flow is deprecated")
        
        return response
    
    def token(
        self,
        grant_type: GrantType,
        client_id: str,
        client_secret: Optional[str] = None,
        code: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        refresh_token: Optional[str] = None,
        code_verifier: Optional[str] = None  # For PKCE
    ) -> OAuthToken:
        """
        Handle token request
        Returns access token and optionally refresh token
        """
        # Validate client
        if client_id not in self.clients:
            raise ValueError("Invalid client_id")
        
        client = self.clients[client_id]
        
        # Validate client secret (not required for public clients with PKCE)
        if client_secret and client.client_secret != client_secret:
            raise ValueError("Invalid client_secret")
        
        # Validate grant type
        if grant_type not in client.grant_types:
            raise ValueError("Unsupported grant_type")
        
        if grant_type == GrantType.AUTHORIZATION_CODE:
            # Exchange authorization code for token
            if not code:
                raise ValueError("Missing authorization code")
            
            if code not in self.authorization_codes:
                raise ValueError("Invalid authorization code")
            
            auth_code = self.authorization_codes[code]
            
            # Validate code
            if auth_code.client_id != client_id:
                raise ValueError("Code not issued to this client")
            
            if auth_code.is_expired():
                raise ValueError("Authorization code expired")
            
            if auth_code.used:
                raise ValueError("Authorization code already used")
            
            if redirect_uri != auth_code.redirect_uri:
                raise ValueError("Redirect URI mismatch")
            
            # Verify PKCE if present
            if auth_code.code_challenge:
                if not code_verifier:
                    raise ValueError("Missing PKCE code_verifier")
                if not auth_code.verify_pkce(code_verifier):
                    raise ValueError("Invalid PKCE code_verifier")
            
            # Mark code as used
            auth_code.used = True
            
            # Generate tokens
            access_token = self._generate_access_token(
                client_id=client_id,
                user_id=auth_code.user_id,
                scope=auth_code.scope
            )
            
            refresh_token_str = None
            if GrantType.REFRESH_TOKEN in client.grant_types:
                refresh_token_str = self._generate_refresh_token(
                    client_id=client_id,
                    user_id=auth_code.user_id,
                    scope=auth_code.scope
                )
            
            return OAuthToken(
                access_token=access_token,
                refresh_token=refresh_token_str,
                scope=auth_code.scope,
                expires_in=3600
            )
        
        elif grant_type == GrantType.REFRESH_TOKEN:
            # Refresh access token
            if not refresh_token:
                raise ValueError("Missing refresh token")
            
            if refresh_token not in self.refresh_tokens:
                raise ValueError("Invalid refresh token")
            
            token_data = self.refresh_tokens[refresh_token]
            
            if token_data["client_id"] != client_id:
                raise ValueError("Refresh token not issued to this client")
            
            # Generate new access token
            access_token = self._generate_access_token(
                client_id=client_id,
                user_id=token_data["user_id"],
                scope=token_data["scope"]
            )
            
            # Optionally rotate refresh token
            new_refresh_token = self._generate_refresh_token(
                client_id=client_id,
                user_id=token_data["user_id"],
                scope=token_data["scope"]
            )
            
            # Revoke old refresh token
            del self.refresh_tokens[refresh_token]
            
            return OAuthToken(
                access_token=access_token,
                refresh_token=new_refresh_token,
                scope=token_data["scope"],
                expires_in=3600
            )
        
        elif grant_type == GrantType.CLIENT_CREDENTIALS:
            # Client credentials flow
            if not client_secret:
                raise ValueError("Client secret required for client credentials flow")
            
            # Generate access token for client (no user)
            access_token = self._generate_access_token(
                client_id=client_id,
                user_id=None,
                scope=client.scope
            )
            
            return OAuthToken(
                access_token=access_token,
                scope=client.scope,
                expires_in=3600
            )
        
        else:
            raise ValueError(f"Unsupported grant type: {grant_type}")
    
    def _generate_access_token(
        self,
        client_id: str,
        user_id: Optional[str],
        scope: str
    ) -> str:
        """Generate JWT access token"""
        payload = {
            "iss": settings.JWT_ISSUER if hasattr(settings, 'JWT_ISSUER') else "mnemosyne",
            "sub": user_id or client_id,
            "aud": client_id,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc),
            "scope": scope,
            "token_type": "access"
        }
        
        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm="HS256"
        )
    
    def _generate_refresh_token(
        self,
        client_id: str,
        user_id: str,
        scope: str
    ) -> str:
        """Generate refresh token"""
        token = secrets.token_urlsafe(48)
        
        self.refresh_tokens[token] = {
            "client_id": client_id,
            "user_id": user_id,
            "scope": scope,
            "created_at": datetime.now(timezone.utc)
        }
        
        return token
    
    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode access token"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=["HS256"]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {e}")
    
    def revoke_token(self, token: str, token_type: str = "refresh"):
        """Revoke a token"""
        if token_type == "refresh" and token in self.refresh_tokens:
            del self.refresh_tokens[token]
        # For access tokens, add to revocation list (in production, use Redis)
    
    def introspect(self, token: str) -> Dict[str, Any]:
        """
        Token introspection (RFC 7662)
        Check if token is active and return metadata
        """
        try:
            # Try as access token
            payload = self.verify_access_token(token)
            return {
                "active": True,
                "scope": payload.get("scope"),
                "client_id": payload.get("aud"),
                "username": payload.get("sub"),
                "exp": payload.get("exp")
            }
        except:
            # Try as refresh token
            if token in self.refresh_tokens:
                token_data = self.refresh_tokens[token]
                return {
                    "active": True,
                    "scope": token_data["scope"],
                    "client_id": token_data["client_id"],
                    "username": token_data["user_id"]
                }
        
        return {"active": False}


# Service layer for dependency injection
class OAuthService:
    """Service layer for OAuth operations"""
    
    def __init__(self):
        self.provider = OAuth2Provider()
        
    async def register_client(
        self,
        client_name: str,
        redirect_uris: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """Register a new OAuth client"""
        client = self.provider.register_client(
            client_name,
            redirect_uris,
            **kwargs
        )
        return client.dict()
    
    async def authorize(
        self,
        client_id: str,
        user_id: str,
        redirect_uri: str,
        scope: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Process authorization request"""
        return self.provider.authorize(
            client_id,
            user_id,
            redirect_uri,
            scope,
            **kwargs
        )
    
    async def exchange_code_for_token(
        self,
        client_id: str,
        code: str,
        redirect_uri: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Exchange authorization code for token"""
        token = self.provider.token(
            GrantType.AUTHORIZATION_CODE,
            client_id,
            code=code,
            redirect_uri=redirect_uri,
            **kwargs
        )
        return token.dict()