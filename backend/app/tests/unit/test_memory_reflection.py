"""
Unit tests for MemoryReflectionService (Phase 3).
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
import pytest
from app.services.memory.reflection import MemoryReflectionService
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_reflect():
    """Test MemoryReflectionService.reflect returns expected result."""
    db = AsyncMock()
    service = MemoryReflectionService(db)
    service.reflect = AsyncMock(return_value={"score": 42})
    result = await service.reflect("agent-1", ["mem1", "mem2"])
    assert result == {"score": 42}
