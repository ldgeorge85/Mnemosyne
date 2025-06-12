import pytest
from httpx import AsyncClient
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_agent():
    async with AsyncClient(base_url="http://backend:8000/api/v1") as ac:
        resp = await ac.post("/agents/", json={"name": "TestAgent", "config": {"role": "test"}})
        assert resp.status_code == 200
        data = resp.json()
        assert "agent_id" in data
        agent_id = data["agent_id"]
        # Test status endpoint
        resp2 = await ac.get(f"/agents/{agent_id}/status")
        assert resp2.status_code == 200
        assert resp2.json()["id"] == agent_id
