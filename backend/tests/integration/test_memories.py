import pytest
from httpx import AsyncClient
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_reflect_memory():
    async with AsyncClient(base_url="http://backend:8000/api/v1") as ac:
        # Create agent first
        resp = await ac.post("/agents/", json={"name": "MemoryAgent", "config": {"role": "reflector"}})
        assert resp.status_code == 200
        agent_id = resp.json()["agent_id"]
        # Reflect some memories
        memories = [{"content": "memory 1"}, {"content": "memory 2"}]
        resp2 = await ac.post("/memories/reflect", json={"agent_id": agent_id, "memories": memories})
        assert resp2.status_code == 200
        assert "reflection" in resp2.json()
        # Importance scores endpoint
        resp3 = await ac.get(f"/memories/importance?agent_id={agent_id}")
        assert resp3.status_code == 200
        assert "scores" in resp3.json()
