"""
Integration tests for the task API endpoints.

This module contains tests for the task API endpoints, focusing on CRUD operations
and ensuring proper authentication and authorization.
"""

import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_async_db
from app.db.models.task import TaskStatus, TaskPriority
from app.db.models.user import User
from app.main import app


# Mock user for authentication
@pytest.fixture
def mock_user():
    """Create a mock user for authentication."""
    user = User(
        id=uuid.uuid4(),
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False
    )
    return user


# Mock async DB session
@pytest.fixture
def mock_db():
    """Create a mock async database session."""
    async_session = AsyncMock(spec=AsyncSession)
    async_session.__aenter__.return_value = async_session
    return async_session


# Override dependencies
@pytest.fixture
def client(mock_user, mock_db):
    """Create a test client with overridden dependencies."""
    
    async def override_get_current_user():
        return mock_user
    
    async def override_get_async_db():
        yield mock_db
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_async_db] = override_get_async_db
    
    with TestClient(app) as client:
        yield client
    
    # Clean up
    app.dependency_overrides = {}


# Test creating a task
def test_create_task(client, mock_db, mock_user):
    """Test creating a task via the API endpoint."""
    # Setup
    task_id = str(uuid.uuid4())
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    
    # Mock the task creation in repository
    mock_task = MagicMock()
    mock_task.id = task_id
    mock_task.user_id = str(mock_user.id)
    mock_task.title = "Test Task"
    mock_task.description = "This is a test task"
    mock_task.status = TaskStatus.pending
    mock_task.priority = TaskPriority.medium
    mock_task.due_date = datetime.utcnow() + timedelta(days=1)
    mock_task.tags = ["test", "api"]
    mock_task.metadata = {"source": "api_test"}
    mock_task.created_at = datetime.utcnow()
    mock_task.updated_at = datetime.utcnow()
    
    # Configure the mock to return our task
    with patch("app.db.repositories.task.TaskRepository.create_task", return_value=mock_task):
        # Execute
        response = client.post(
            "/api/v1/tasks/",
            json={
                "title": "Test Task",
                "description": "This is a test task",
                "status": "pending",
                "priority": "medium",
                "tags": ["test", "api"],
                "metadata": {"source": "api_test"}
            }
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Test Task"
        assert data["status"] == "pending"
        assert data["priority"] == "medium"
        assert "test" in data["tags"]
        assert "api" in data["tags"]
        assert data["metadata"]["source"] == "api_test"


# Test getting a task by ID
def test_get_task_by_id(client, mock_db, mock_user):
    """Test retrieving a task by ID via the API endpoint."""
    # Setup
    task_id = str(uuid.uuid4())
    
    # Mock the task retrieval in repository
    mock_task = MagicMock()
    mock_task.id = task_id
    mock_task.user_id = str(mock_user.id)
    mock_task.title = "Test Task"
    mock_task.description = "This is a test task"
    mock_task.status = TaskStatus.pending
    mock_task.priority = TaskPriority.medium
    mock_task.due_date = datetime.utcnow() + timedelta(days=1)
    mock_task.tags = ["test", "api"]
    mock_task.metadata = {"source": "api_test"}
    mock_task.created_at = datetime.utcnow()
    mock_task.updated_at = datetime.utcnow()
    
    # Configure the mock to return our task
    with patch("app.db.repositories.task.TaskRepository.get_task_by_id", return_value=mock_task):
        # Execute
        response = client.get(f"/api/v1/tasks/{task_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Test Task"
        assert data["status"] == "pending"
        assert data["priority"] == "medium"


# Test getting a task that doesn't exist
def test_get_task_not_found(client, mock_db, mock_user):
    """Test retrieving a non-existent task via the API endpoint."""
    # Setup
    task_id = str(uuid.uuid4())
    
    # Configure the mock to return None (task not found)
    with patch("app.db.repositories.task.TaskRepository.get_task_by_id", return_value=None):
        # Execute
        response = client.get(f"/api/v1/tasks/{task_id}")
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


# Test updating a task
def test_update_task(client, mock_db, mock_user):
    """Test updating a task via the API endpoint."""
    # Setup
    task_id = str(uuid.uuid4())
    
    # Mock the task retrieval and update in repository
    mock_task = MagicMock()
    mock_task.id = task_id
    mock_task.user_id = str(mock_user.id)
    mock_task.title = "Updated Task"
    mock_task.description = "This is an updated test task"
    mock_task.status = TaskStatus.in_progress
    mock_task.priority = TaskPriority.high
    mock_task.due_date = datetime.utcnow() + timedelta(days=1)
    mock_task.tags = ["test", "api", "updated"]
    mock_task.metadata = {"source": "api_test", "updated": True}
    mock_task.created_at = datetime.utcnow()
    mock_task.updated_at = datetime.utcnow()
    
    # Configure the mocks
    with patch("app.db.repositories.task.TaskRepository.get_task_by_id", return_value=mock_task), \
         patch("app.db.repositories.task.TaskRepository.update_task", return_value=mock_task):
        # Execute
        response = client.put(
            f"/api/v1/tasks/{task_id}",
            json={
                "title": "Updated Task",
                "description": "This is an updated test task",
                "status": "in_progress",
                "priority": "high",
                "tags": ["test", "api", "updated"],
                "metadata": {"source": "api_test", "updated": True}
            }
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Updated Task"
        assert data["status"] == "in_progress"
        assert data["priority"] == "high"
        assert "updated" in data["tags"]
        assert data["metadata"]["updated"] is True


# Test deleting a task
def test_delete_task(client, mock_db, mock_user):
    """Test deleting a task via the API endpoint."""
    # Setup
    task_id = str(uuid.uuid4())
    
    # Mock the task retrieval in repository
    mock_task = MagicMock()
    mock_task.id = task_id
    mock_task.user_id = str(mock_user.id)
    
    # Configure the mocks
    with patch("app.db.repositories.task.TaskRepository.get_task_by_id", return_value=mock_task), \
         patch("app.db.repositories.task.TaskRepository.delete_task", return_value=None):
        # Execute
        response = client.delete(f"/api/v1/tasks/{task_id}")
        
        # Assert
        assert response.status_code == 204


# Test listing tasks
def test_list_tasks(client, mock_db, mock_user):
    """Test listing tasks via the API endpoint."""
    # Setup
    # Mock the task listing in repository
    mock_tasks = [MagicMock(), MagicMock()]
    mock_tasks[0].id = str(uuid.uuid4())
    mock_tasks[0].user_id = str(mock_user.id)
    mock_tasks[0].title = "Task 1"
    mock_tasks[0].status = TaskStatus.pending
    
    mock_tasks[1].id = str(uuid.uuid4())
    mock_tasks[1].user_id = str(mock_user.id)
    mock_tasks[1].title = "Task 2"
    mock_tasks[1].status = TaskStatus.in_progress
    
    # Configure the mock to return our tasks
    with patch("app.db.repositories.task.TaskRepository.get_tasks_by_user", return_value=(mock_tasks, 2)):
        # Execute
        response = client.get("/api/v1/tasks/")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 2
        assert data["total"] == 2
        assert data["items"][0]["title"] == "Task 1"
        assert data["items"][1]["title"] == "Task 2"


# Test unauthorized access
def test_unauthorized_access(client, mock_db, mock_user):
    """Test unauthorized access to another user's task."""
    # Setup
    task_id = str(uuid.uuid4())
    
    # Mock the task retrieval in repository - task belongs to another user
    mock_task = MagicMock()
    mock_task.id = task_id
    mock_task.user_id = str(uuid.uuid4())  # Different user ID
    
    # Configure the mock to return the task
    with patch("app.db.repositories.task.TaskRepository.get_task_by_id", return_value=mock_task):
        # Execute
        response = client.get(f"/api/v1/tasks/{task_id}")
        
        # Assert
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
        assert "unauthorized" in data["detail"].lower()
