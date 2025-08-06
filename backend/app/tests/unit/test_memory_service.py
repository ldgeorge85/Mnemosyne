"""
Unit tests for MemoryService.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.memory.memory_service import MemoryService
from app.models.memory import Memory
from app.tests.fixtures.test_data import create_test_memory

@pytest.mark.asyncio
async def test_create_memory():
    """
    Test that MemoryService.create_memory creates a memory and returns it.
    """
    # Arrange
    db_session = AsyncMock()
    memory_data = create_test_memory()
    memory_service = MemoryService(db_session)
    
    # Mock the add and commit methods
    db_session.add = AsyncMock()
    db_session.commit = AsyncMock()
    db_session.refresh = AsyncMock()
    
    # Act
    result = await memory_service.create_memory(
        title=memory_data["title"],
        content=memory_data["content"],
        tags=memory_data["tags"],
        user_id=memory_data["user_id"],
        importance_score=memory_data["importance_score"],
        source=memory_data["source"]
    )
    
    # Assert
    assert db_session.add.called
    assert db_session.commit.called
    assert db_session.refresh.called
    assert result is not None
    assert result.title == memory_data["title"]
    assert result.content == memory_data["content"]

@pytest.mark.asyncio
async def test_get_memory_by_id():
    """
    Test that MemoryService.get_memory_by_id returns the correct memory.
    """
    # Arrange
    db_session = AsyncMock()
    memory_data = create_test_memory()
    memory_id = memory_data["id"]
    
    # Create a mock memory object
    mock_memory = MagicMock(spec=Memory)
    mock_memory.id = memory_id
    mock_memory.title = memory_data["title"]
    mock_memory.content = memory_data["content"]
    
    # Mock the query method to return our mock memory
    db_session.query = MagicMock()
    db_session.query.return_value.filter.return_value.first.return_value = mock_memory
    
    memory_service = MemoryService(db_session)
    
    # Act
    result = await memory_service.get_memory_by_id(memory_id)
    
    # Assert
    assert result is not None
    assert result.id == memory_id
    assert result.title == memory_data["title"]
    assert result.content == memory_data["content"]

@pytest.mark.asyncio
async def test_get_memory_by_id_not_found():
    """
    Test that MemoryService.get_memory_by_id returns None when memory not found.
    """
    # Arrange
    db_session = AsyncMock()
    memory_id = "non-existent-id"
    
    # Mock the query method to return None
    db_session.query = MagicMock()
    db_session.query.return_value.filter.return_value.first.return_value = None
    
    memory_service = MemoryService(db_session)
    
    # Act
    result = await memory_service.get_memory_by_id(memory_id)
    
    # Assert
    assert result is None

@pytest.mark.asyncio
async def test_update_memory():
    """
    Test that MemoryService.update_memory updates a memory correctly.
    """
    # Arrange
    db_session = AsyncMock()
    memory_data = create_test_memory()
    memory_id = memory_data["id"]
    
    # Create a mock memory object
    mock_memory = MagicMock(spec=Memory)
    mock_memory.id = memory_id
    mock_memory.title = memory_data["title"]
    mock_memory.content = memory_data["content"]
    
    # Mock the query method to return our mock memory
    db_session.query = MagicMock()
    db_session.query.return_value.filter.return_value.first.return_value = mock_memory
    
    # Mock commit
    db_session.commit = AsyncMock()
    db_session.refresh = AsyncMock()
    
    memory_service = MemoryService(db_session)
    
    # New data for update
    new_title = "Updated Test Memory"
    new_content = "Updated test memory content"
    
    # Act
    result = await memory_service.update_memory(
        memory_id=memory_id,
        title=new_title,
        content=new_content
    )
    
    # Assert
    assert result is not None
    assert result.title == new_title
    assert result.content == new_content
    assert db_session.commit.called
    assert db_session.refresh.called

@pytest.mark.asyncio
async def test_delete_memory():
    """
    Test that MemoryService.delete_memory deletes a memory correctly.
    """
    # Arrange
    db_session = AsyncMock()
    memory_data = create_test_memory()
    memory_id = memory_data["id"]
    
    # Create a mock memory object
    mock_memory = MagicMock(spec=Memory)
    mock_memory.id = memory_id
    
    # Mock the query method to return our mock memory
    db_session.query = MagicMock()
    db_session.query.return_value.filter.return_value.first.return_value = mock_memory
    
    # Mock delete and commit
    db_session.delete = AsyncMock()
    db_session.commit = AsyncMock()
    
    memory_service = MemoryService(db_session)
    
    # Act
    result = await memory_service.delete_memory(memory_id)
    
    # Assert
    assert result is True
    assert db_session.delete.called
    assert db_session.commit.called

@pytest.mark.asyncio
async def test_delete_memory_not_found():
    """
    Test that MemoryService.delete_memory returns False when memory not found.
    """
    # Arrange
    db_session = AsyncMock()
    memory_id = "non-existent-id"
    
    # Mock the query method to return None
    db_session.query = MagicMock()
    db_session.query.return_value.filter.return_value.first.return_value = None
    
    memory_service = MemoryService(db_session)
    
    # Act
    result = await memory_service.delete_memory(memory_id)
    
    # Assert
    assert result is False
    assert not db_session.delete.called
    assert not db_session.commit.called
