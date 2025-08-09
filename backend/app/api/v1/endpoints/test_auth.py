"""
Test Auth Endpoint - Minimal implementation for debugging
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/test-auth")
async def test_auth():
    """Test endpoint to verify routing works"""
    return {"message": "Test auth endpoint is working!"}