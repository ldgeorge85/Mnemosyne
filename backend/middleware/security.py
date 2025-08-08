"""
Security middleware for Mnemosyne Protocol
"""

from typing import Callable
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
import time
import uuid
import logging

from core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # CSP header (adjust based on your needs)
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' wss: https:; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
        
        # Remove server header
        if "server" in response.headers:
            del response.headers["server"]
        
        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Add unique request ID to each request for tracing
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Add to MDC for logging
        logger.info(f"Request {request_id}: {request.method} {request.url.path}")
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting (use Redis in production)
    """
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client identifier
        client_id = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)
        
        now = time.time()
        
        # Clean old entries
        self.clients = {
            k: v for k, v in self.clients.items()
            if now - v["first_request"] < self.period
        }
        
        # Check rate limit
        if client_id in self.clients:
            client_data = self.clients[client_id]
            if now - client_data["first_request"] < self.period:
                if client_data["request_count"] >= self.calls:
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={"detail": "Rate limit exceeded"}
                    )
                client_data["request_count"] += 1
            else:
                # Reset window
                self.clients[client_id] = {
                    "first_request": now,
                    "request_count": 1
                }
        else:
            # New client
            self.clients[client_id] = {
                "first_request": now,
                "request_count": 1
            }
        
        response = await call_next(request)
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Log all requests and responses
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Incoming request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise
        
        # Calculate request duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"Status: {response.status_code} Duration: {duration:.3f}s"
        )
        
        # Add timing header
        response.headers["X-Process-Time"] = str(duration)
        
        return response


def setup_middleware(app):
    """
    Configure all middleware for the application
    """
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted host middleware
    if settings.allowed_hosts:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts
        )
    
    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Request ID for tracing
    app.add_middleware(RequestIDMiddleware)
    
    # Rate limiting
    app.add_middleware(
        RateLimitMiddleware,
        calls=settings.rate_limit_requests_per_minute,
        period=60  # 1 minute
    )
    
    # Logging
    app.add_middleware(LoggingMiddleware)
    
    return app