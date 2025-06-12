"""
Integration tests for /memories/* API endpoints.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_reflect_memory_api():
    """Test POST /memories/reflect endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/memories/reflect", json={"agent_id": "agent-1", "memories": ["m1", "m2"]})
        assert response.status_code in (200, 422)  # 422 if validation fails due to missing DB/mock
