"""
Unit tests for the TaskService class.

This module contains tests for the TaskService class, which handles the business logic
for task management operations including creation, retrieval, updating, deletion,
and specialized operations like task assignment and subtask management.
"""

import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from app.db.models.task import Task, TaskLog, TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate, TaskLogCreate
from app.services.task.task_service import TaskService


@pytest.fixture
def mock_task_repository():
    """
    Create a mock TaskRepository with AsyncMock methods.
    """
    repository = AsyncMock()
    return repository


@pytest.fixture
def task_service(mock_task_repository):
    """
    Create a TaskService instance with a mock repository.
    """
    return TaskService(repository=mock_task_repository)


@pytest.fixture
def sample_user_id():
    """
    Return a sample user ID for testing.
    """
    return str(uuid.uuid4())


@pytest.fixture
def sample_task_id():
    """
    Return a sample task ID for testing.
    """
    return str(uuid.uuid4())


@pytest.fixture
def sample_task_create():
    """
    Return a sample TaskCreate object for testing.
    """
    return TaskCreate(
        title="Test Task",
        description="This is a test task",
        status=TaskStatus.pending,
        priority=TaskPriority.medium,
        due_date=datetime.utcnow() + timedelta(days=1),
        tags=["test", "unit-test"],
        metadata={"source": "test"}
    )


@pytest.fixture
def sample_task_update():
    """
    Return a sample TaskUpdate object for testing.
    """
    return TaskUpdate(
        title="Updated Task",
        description="This is an updated test task",
        status=TaskStatus.in_progress,
        priority=TaskPriority.high
    )


@pytest.fixture
def sample_task_log_create():
    """
    Return a sample TaskLogCreate object for testing.
    """
    return TaskLogCreate(
        message="Test log message",
        log_type="info",
        metadata={"source": "test"}
    )


@pytest.mark.asyncio
async def test_create_task(task_service, mock_task_repository, sample_user_id, sample_task_create):
    """
    Test creating a task with the TaskService.
    """
    # Setup
    mock_task = MagicMock()
    mock_task.id = str(uuid.uuid4())
    mock_task_repository.create_task.return_value = mock_task
    
    # Execute
    result = await task_service.create_task(
        db=AsyncMock(),
        user_id=sample_user_id,
        task_create=sample_task_create
    )
    
    # Assert
    assert result == mock_task
    mock_task_repository.create_task.assert_called_once_with(
        db=mock_task_repository.create_task.call_args[0][0],
        user_id=sample_user_id,
        task_create=sample_task_create
    )


@pytest.mark.asyncio
async def test_get_task_by_id(task_service, mock_task_repository, sample_user_id, sample_task_id):
    """
    Test retrieving a task by ID with the TaskService.
    """
    # Setup
    mock_task = MagicMock()
    mock_task.id = sample_task_id
    mock_task.user_id = sample_user_id
    mock_task_repository.get_task_by_id.return_value = mock_task
    
    # Execute
    result = await task_service.get_task_by_id(
        db=AsyncMock(),
        task_id=sample_task_id,
        user_id=sample_user_id
    )
    
    # Assert
    assert result == mock_task
    mock_task_repository.get_task_by_id.assert_called_once_with(
        db=mock_task_repository.get_task_by_id.call_args[0][0],
        task_id=sample_task_id
    )


@pytest.mark.asyncio
async def test_get_task_by_id_not_found(task_service, mock_task_repository, sample_user_id, sample_task_id):
    """
    Test retrieving a non-existent task by ID with the TaskService.
    """
    # Setup
    mock_task_repository.get_task_by_id.return_value = None
    
    # Execute & Assert
    with pytest.raises(ValueError, match="Task not found"):
        await task_service.get_task_by_id(
            db=AsyncMock(),
            task_id=sample_task_id,
            user_id=sample_user_id
        )


@pytest.mark.asyncio
async def test_get_task_by_id_unauthorized(task_service, mock_task_repository, sample_task_id):
    """
    Test retrieving a task by ID with an unauthorized user.
    """
    # Setup
    mock_task = MagicMock()
    mock_task.id = sample_task_id
    mock_task.user_id = str(uuid.uuid4())  # Different user ID
    mock_task_repository.get_task_by_id.return_value = mock_task
    
    # Execute & Assert
    with pytest.raises(ValueError, match="Unauthorized access to task"):
        await task_service.get_task_by_id(
            db=AsyncMock(),
            task_id=sample_task_id,
            user_id=str(uuid.uuid4())  # Different user ID
        )


@pytest.mark.asyncio
async def test_update_task(task_service, mock_task_repository, sample_user_id, sample_task_id, sample_task_update):
    """
    Test updating a task with the TaskService.
    """
    # Setup
    mock_task = MagicMock()
    mock_task.id = sample_task_id
    mock_task.user_id = sample_user_id
    mock_task_repository.get_task_by_id.return_value = mock_task
    mock_task_repository.update_task.return_value = mock_task
    
    # Execute
    result = await task_service.update_task(
        db=AsyncMock(),
        task_id=sample_task_id,
        task_update=sample_task_update,
        user_id=sample_user_id
    )
    
    # Assert
    assert result == mock_task
    mock_task_repository.update_task.assert_called_once_with(
        db=mock_task_repository.update_task.call_args[0][0],
        task_id=sample_task_id,
        task_update=sample_task_update
    )


@pytest.mark.asyncio
async def test_delete_task(task_service, mock_task_repository, sample_user_id, sample_task_id):
    """
    Test deleting a task with the TaskService.
    """
    # Setup
    mock_task = MagicMock()
    mock_task.id = sample_task_id
    mock_task.user_id = sample_user_id
    mock_task_repository.get_task_by_id.return_value = mock_task
    
    # Execute
    await task_service.delete_task(
        db=AsyncMock(),
        task_id=sample_task_id,
        user_id=sample_user_id
    )
    
    # Assert
    mock_task_repository.delete_task.assert_called_once_with(
        db=mock_task_repository.delete_task.call_args[0][0],
        task_id=sample_task_id
    )


@pytest.mark.asyncio
async def test_create_task_log(task_service, mock_task_repository, sample_user_id, sample_task_id, sample_task_log_create):
    """
    Test creating a task log with the TaskService.
    """
    # Setup
    mock_task = MagicMock()
    mock_task.id = sample_task_id
    mock_task.user_id = sample_user_id
    mock_task_repository.get_task_by_id.return_value = mock_task
    
    mock_task_log = MagicMock()
    mock_task_log.id = str(uuid.uuid4())
    mock_task_repository.create_task_log.return_value = mock_task_log
    
    # Execute
    result = await task_service.create_task_log(
        db=AsyncMock(),
        task_id=sample_task_id,
        task_log_create=sample_task_log_create,
        user_id=sample_user_id
    )
    
    # Assert
    assert result == mock_task_log
    mock_task_repository.create_task_log.assert_called_once_with(
        db=mock_task_repository.create_task_log.call_args[0][0],
        task_id=sample_task_id,
        task_log_create=sample_task_log_create
    )


@pytest.mark.asyncio
async def test_get_task_logs(task_service, mock_task_repository, sample_user_id, sample_task_id):
    """
    Test retrieving task logs with the TaskService.
    """
    # Setup
    mock_task = MagicMock()
    mock_task.id = sample_task_id
    mock_task.user_id = sample_user_id
    mock_task_repository.get_task_by_id.return_value = mock_task
    
    mock_logs = [MagicMock(), MagicMock()]
    mock_task_repository.get_task_logs.return_value = mock_logs
    
    # Execute
    result = await task_service.get_task_logs(
        db=AsyncMock(),
        task_id=sample_task_id,
        user_id=sample_user_id
    )
    
    # Assert
    assert result == mock_logs
    mock_task_repository.get_task_logs.assert_called_once_with(
        db=mock_task_repository.get_task_logs.call_args[0][0],
        task_id=sample_task_id
    )


@pytest.mark.asyncio
async def test_create_subtask(task_service, mock_task_repository, sample_user_id, sample_task_id, sample_task_create):
    """
    Test creating a subtask with the TaskService.
    """
    # Setup
    mock_parent_task = MagicMock()
    mock_parent_task.id = sample_task_id
    mock_parent_task.user_id = sample_user_id
    mock_task_repository.get_task_by_id.return_value = mock_parent_task
    
    mock_subtask = MagicMock()
    mock_subtask.id = str(uuid.uuid4())
    mock_task_repository.create_task.return_value = mock_subtask
    
    # Execute
    result = await task_service.create_subtask(
        db=AsyncMock(),
        parent_id=sample_task_id,
        task_create=sample_task_create,
        user_id=sample_user_id
    )
    
    # Assert
    assert result == mock_subtask
    # Check that create_task was called with parent_id
    call_kwargs = mock_task_repository.create_task.call_args[1]
    assert call_kwargs.get('parent_id') == sample_task_id
