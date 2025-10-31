"""
Rate Limiting Middleware

Redis-based sliding window rate limiting to prevent abuse of the Trust Primitive.
"""

import logging
import time
from typing import Optional, Dict, Tuple
from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from redis import asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Redis-based rate limiter with sliding window."""

    def __init__(self, redis_url: str):
        """Initialize rate limiter with Redis connection."""
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self):
        """Connect to Redis."""
        if not self.redis:
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Rate limiter connected to Redis")

    async def close(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            logger.info("Rate limiter Redis connection closed")

    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window: int = 3600
    ) -> Tuple[bool, int, int]:
        """
        Check if request exceeds rate limit using sliding window.

        Args:
            key: Redis key for this limit (e.g., "rate_limit:user_123:/api/negotiations")
            limit: Maximum number of requests allowed
            window: Time window in seconds (default: 3600 = 1 hour)

        Returns:
            Tuple of (allowed, remaining, reset_time)
            - allowed: True if request is within limit
            - remaining: Number of requests remaining
            - reset_time: Unix timestamp when limit resets
        """
        if not self.redis:
            # If Redis not available, allow request (fail open for availability)
            logger.warning("Redis not connected, allowing request")
            return True, limit, int(time.time() + window)

        try:
            current_time = int(time.time())
            window_start = current_time - window

            # Use Redis pipeline for atomic operations
            pipe = self.redis.pipeline()

            # Remove old entries outside the window
            pipe.zremrangebyscore(key, 0, window_start)

            # Add current request with score = timestamp
            pipe.zadd(key, {str(current_time): current_time})

            # Count requests in current window
            pipe.zcard(key)

            # Set expiry on key (cleanup)
            pipe.expire(key, window + 60)  # Extra 60s buffer

            # Execute pipeline
            results = await pipe.execute()
            request_count = results[2]  # Result of zcard

            # Calculate remaining and reset time
            remaining = max(0, limit - request_count)
            reset_time = current_time + window

            allowed = request_count <= limit

            if not allowed:
                logger.warning(
                    f"Rate limit exceeded for {key}: {request_count}/{limit}"
                )

            return allowed, remaining, reset_time

        except Exception as e:
            logger.error(f"Rate limit check error: {e}", exc_info=True)
            # Fail open - allow request if Redis error
            return True, limit, int(time.time() + window)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware to enforce rate limits."""

    # Rate limit configuration: {pattern: (limit, window_seconds)}
    RATE_LIMITS: Dict[str, Tuple[int, int]] = {
        "/api/v1/negotiations": (10, 3600),  # 10 negotiations per hour
        "/api/v1/negotiations/*/offer": (100, 3600),  # 100 offers per hour
        "/api/v1/negotiations/*/accept": (20, 3600),  # 20 accepts per hour
        "/api/v1/negotiations/*/finalize": (20, 3600),  # 20 finalizations per hour
        "/api/v1/negotiations/*/dispute": (5, 3600),  # 5 disputes per hour
        "/api/v1/memories": (100, 3600),  # 100 memory operations per hour
        "/api/v1/tasks": (200, 3600),  # 200 task operations per hour
    }

    def __init__(self, app, rate_limiter: RateLimiter):
        super().__init__(app)
        self.rate_limiter = rate_limiter

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""

        # Skip rate limiting for health checks and static assets
        if request.url.path in ["/health", "/metrics", "/docs", "/openapi.json"]:
            return await call_next(request)

        # Get user ID from request (from JWT or session)
        user_id = self.get_user_id(request)

        if not user_id:
            # No auth = no rate limiting (let auth middleware handle it)
            return await call_next(request)

        # Check if path matches any rate limit patterns
        path = request.url.path
        method = request.method

        # Only rate limit write operations
        if method not in ["POST", "PUT", "PATCH", "DELETE"]:
            return await call_next(request)

        for pattern, (limit, window) in self.RATE_LIMITS.items():
            if self.path_matches(path, pattern):
                # Construct Redis key
                key = f"rate_limit:{user_id}:{pattern}"

                # Check rate limit
                allowed, remaining, reset_time = await self.rate_limiter.check_rate_limit(
                    key, limit, window
                )

                if not allowed:
                    # Return 429 Too Many Requests
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": "Rate limit exceeded",
                            "message": f"You have exceeded the rate limit for this endpoint. Please try again later.",
                            "limit": limit,
                            "window": window,
                            "retry_after": reset_time - int(time.time())
                        },
                        headers={
                            "X-RateLimit-Limit": str(limit),
                            "X-RateLimit-Remaining": str(remaining),
                            "X-RateLimit-Reset": str(reset_time),
                            "Retry-After": str(reset_time - int(time.time()))
                        }
                    )

                # Add rate limit headers to response
                response = await call_next(request)

                # Add rate limit info headers
                response.headers["X-RateLimit-Limit"] = str(limit)
                response.headers["X-RateLimit-Remaining"] = str(remaining)
                response.headers["X-RateLimit-Reset"] = str(reset_time)

                return response

        # No rate limit matched, proceed
        return await call_next(request)

    def get_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request (JWT token or session)."""
        try:
            # Try to get from JWT token in Authorization header
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                # In production, decode JWT and extract user_id
                # For now, placeholder
                # token = auth_header.split(" ")[1]
                # payload = jwt.decode(token, settings.JWT_SECRET_KEY)
                # return payload.get("sub")
                pass

            # Try to get from request state (set by auth middleware)
            if hasattr(request.state, "user_id"):
                return str(request.state.user_id)

            # Try to get from session
            if hasattr(request.state, "user"):
                return str(request.state.user.id)

            return None

        except Exception as e:
            logger.error(f"Error extracting user ID: {e}")
            return None

    def path_matches(self, path: str, pattern: str) -> bool:
        """
        Check if path matches pattern (with * wildcard support).

        Examples:
            path_matches("/api/v1/negotiations/123/offer", "/api/v1/negotiations/*/offer") -> True
            path_matches("/api/v1/negotiations", "/api/v1/negotiations") -> True
        """
        path_parts = path.rstrip('/').split('/')
        pattern_parts = pattern.rstrip('/').split('/')

        if len(path_parts) != len(pattern_parts):
            return False

        for path_part, pattern_part in zip(path_parts, pattern_parts):
            if pattern_part == '*':
                continue  # Wildcard matches anything
            if path_part != pattern_part:
                return False

        return True


# Global rate limiter instance
rate_limiter = RateLimiter(settings.REDIS_URI)
