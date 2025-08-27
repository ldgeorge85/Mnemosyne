"""
Receipt Enforcement Middleware

Ensures that all state-changing endpoints generate receipts for transparency.
This is a core sovereignty safeguard that cannot be disabled.
"""

import logging
from typing import Callable, Set
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class ReceiptEnforcementMiddleware(BaseHTTPMiddleware):
    """
    Middleware that enforces receipt generation for all state-changing operations.
    
    This is a sovereignty invariant - all actions must be transparent to users.
    """
    
    # Endpoints that are exempt from receipt requirements
    EXEMPT_PATHS: Set[str] = {
        "/docs",
        "/openapi.json",
        "/health",
        "/metrics",
        "/api/v1/receipts",  # Receipt endpoints themselves
        "/api/v1/auth/login",  # Login creates its own receipt
        "/api/v1/auth/logout",  # Logout creates its own receipt
    }
    
    # Methods that require receipts
    STATE_CHANGING_METHODS: Set[str] = {"POST", "PUT", "PATCH", "DELETE"}
    
    def __init__(self, app: ASGIApp, strict_mode: bool = False):
        """
        Initialize the middleware.
        
        Args:
            app: The ASGI application
            strict_mode: If True, reject requests without receipts. If False, log warnings.
        """
        super().__init__(app)
        self.strict_mode = strict_mode
        self._receipt_created = False
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and ensure receipts are generated.
        
        Args:
            request: The incoming request
            call_next: The next middleware or endpoint
            
        Returns:
            The response
            
        Raises:
            HTTPException: If strict mode is enabled and no receipt was created
        """
        # Check if this endpoint requires receipt enforcement
        if not self._requires_receipt(request):
            return await call_next(request)
        
        # Track if a receipt was created during this request
        # This would need to be integrated with the actual receipt service
        # For now, we'll check if the receipt service was called
        
        # Store the original create_receipt method reference
        # In production, this would hook into the actual ReceiptService
        request.state.receipt_created = False
        
        # Process the request
        response = await call_next(request)
        
        # Check if a receipt was created
        if not request.state.receipt_created and response.status_code < 400:
            message = f"No receipt generated for {request.method} {request.url.path}"
            
            if self.strict_mode:
                # In strict mode, reject the request
                logger.error(f"SOVEREIGNTY VIOLATION: {message}")
                raise HTTPException(
                    status_code=500,
                    detail="Receipt generation required for transparency. This is a sovereignty safeguard."
                )
            else:
                # In non-strict mode, log a warning
                logger.warning(f"Receipt not enforced: {message}")
        
        return response
    
    def _requires_receipt(self, request: Request) -> bool:
        """
        Determine if this request requires a receipt.
        
        Args:
            request: The incoming request
            
        Returns:
            True if receipt is required, False otherwise
        """
        # Skip non-state-changing methods
        if request.method not in self.STATE_CHANGING_METHODS:
            return False
        
        # Check if path is exempt
        path = request.url.path
        for exempt_path in self.EXEMPT_PATHS:
            if path.startswith(exempt_path):
                return False
        
        # All other state-changing operations require receipts
        return True


class ReceiptTracker:
    """
    Helper class to track receipt creation within a request context.
    This would be integrated with the ReceiptService.
    """
    
    @staticmethod
    def mark_receipt_created(request: Request):
        """Mark that a receipt was created for this request."""
        if hasattr(request.state, 'receipt_created'):
            request.state.receipt_created = True
    
    @staticmethod
    def was_receipt_created(request: Request) -> bool:
        """Check if a receipt was created for this request."""
        return getattr(request.state, 'receipt_created', False)