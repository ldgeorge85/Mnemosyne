"""
Integration tests for /agents/* API endpoints.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_agent_api():
    """Test POST /agents/ endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/agents/", json={"role": "test"})
        assert response.status_code == 200
        assert "agent_id" in response.json()
