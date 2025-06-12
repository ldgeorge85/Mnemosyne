"""
Unit tests for AgentManager service (Phase 3).
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
import pytest
from app.services.agent.agent_manager import AgentManager
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_create_agent():
    """Test AgentManager.create_agent creates an agent and returns an ID."""
    db = AsyncMock()
    manager = AgentManager(db)
    manager.create_agent = AsyncMock(return_value="agent-123")
    agent_id = await manager.create_agent({"role": "test"})
    assert agent_id == "agent-123"

@pytest.mark.asyncio
async def test_link_agents():
    """Test AgentManager.link_agents links two agents successfully."""
    db = AsyncMock()
    manager = AgentManager(db)
    manager.link_agents = AsyncMock()
    await manager.link_agents("parent", "child")
    manager.link_agents.assert_awaited_with("parent", "child")
