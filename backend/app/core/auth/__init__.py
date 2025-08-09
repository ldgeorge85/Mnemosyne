"""
Modular Authentication System
Supports multiple auth providers with easy switching
"""

from .base import AuthProvider, AuthResult, AuthUser, AuthMethod
from .providers import StaticAuthProvider, OAuthProvider, DIDAuthProvider
from .manager import AuthManager

__all__ = [
    "AuthProvider",
    "AuthResult", 
    "AuthUser",
    "AuthMethod",
    "StaticAuthProvider",
    "OAuthProvider",
    "DIDAuthProvider",
    "AuthManager"
]