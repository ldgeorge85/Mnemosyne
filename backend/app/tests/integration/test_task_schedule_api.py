"""
Integration tests for task schedule API endpoints.

This module contains integration tests for the task schedule API endpoints.
"""
import uuid
from datetime import datetime, timedelta
import pytest
from fastapi import status
from httpx import AsyncClient

from app.db.models.task import Task, TaskStatus, TaskPriority
from app.db.models.task_schedule import TaskSchedule
from app.db.models.user import User


@pytest.fixture
async def test_user(db_session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False,
        first_name="Test",
        last_name="User"
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def test_task(db_session, test_user):
    """Create a test task."""
    task = Task(
        title="Test Task",
        description="Test task description",
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        user_id=test_user.id
    )
    db_session.add(task)
    await db_session.commit()
    return task


@pytest.fixture
async def test_task_schedule(db_session, test_task):
    """Create a test task schedule."""
    task_schedule = TaskSchedule(
        task_id=test_task.id,
        start_time=datetime.utcnow(),
        due_time=datetime.utcnow() + timedelta(hours=2),
        timezone="UTC",
        is_all_day=False,
        duration_minutes=120
    )
    db_session.add(task_schedule)
    await db_session.commit()
    return task_schedule


@pytest.fixture
def auth_headers(test_user):
    """Create authorization headers for the test user."""
    # In a real test, this would use the actual authentication logic
    # For simplicity, we're mocking the JWT token
    return {"Authorization": f"Bearer test_token_for_user_{test_user.id}"}


class TestTaskScheduleAPI:
    """Test cases for task schedule API endpoints."""

    async def test_create_task_schedule(self, client: AsyncClient, test_user, test_task, auth_headers):
        """Test creating a task schedule."""
        # Setup
        start_time = datetime.utcnow()
        due_time = start_time + timedelta(hours=2)
        
        # Execute
        response = await client.post(
            "/api/v1/task-schedules/",
            json={
                "task_id": str(test_task.id),
                "start_time": start_time.isoformat(),
                "due_time": due_time.isoformat(),
                "timezone": "UTC",
                "is_all_day": False,
                "duration_minutes": 120
            },
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["task_id"] == str(test_task.id)
        assert "conflicts" in data
        assert isinstance(data["conflicts"], list)

    async def test_create_task_schedule_unauthorized_task(
        self, client: AsyncClient, test_user, auth_headers, db_session
    ):
        """Test creating a task schedule for a task that doesn't belong to the user."""
        # Setup
        # Create another user
        other_user = User(
            email="other@example.com",
            hashed_password="hashed_password",
            is_active=True,
            is_superuser=False,
            first_name="Other",
            last_name="User"
        )
        db_session.add(other_user)
        await db_session.commit()
        
        # Create a task for the other user
        other_task = Task(
            title="Other Task",
            description="Other task description",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            user_id=other_user.id
        )
        db_session.add(other_task)
        await db_session.commit()
        
        start_time = datetime.utcnow()
        due_time = start_time + timedelta(hours=2)
        
        # Execute
        response = await client.post(
            "/api/v1/task-schedules/",
            json={
                "task_id": str(other_task.id),
                "start_time": start_time.isoformat(),
                "due_time": due_time.isoformat(),
                "timezone": "UTC",
                "is_all_day": False,
                "duration_minutes": 120
            },
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "does not belong to user" in response.json()["detail"]

    async def test_get_task_schedule(
        self, client: AsyncClient, test_user, test_task_schedule, auth_headers
    ):
        """Test getting a task schedule by ID."""
        # Execute
        response = await client.get(
            f"/api/v1/task-schedules/{test_task_schedule.id}",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(test_task_schedule.id)
        assert data["task_id"] == str(test_task_schedule.task_id)

    async def test_get_task_schedule_by_task(
        self, client: AsyncClient, test_user, test_task, test_task_schedule, auth_headers
    ):
        """Test getting a task schedule by task ID."""
        # Execute
        response = await client.get(
            f"/api/v1/task-schedules/task/{test_task.id}",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(test_task_schedule.id)
        assert data["task_id"] == str(test_task.id)

    async def test_update_task_schedule(
        self, client: AsyncClient, test_user, test_task_schedule, auth_headers
    ):
        """Test updating a task schedule."""
        # Setup
        new_due_time = datetime.utcnow() + timedelta(hours=4)
        
        # Execute
        response = await client.put(
            f"/api/v1/task-schedules/{test_task_schedule.id}",
            json={
                "due_time": new_due_time.isoformat(),
                "is_all_day": True,
                "duration_minutes": 240
            },
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(test_task_schedule.id)
        assert data["is_all_day"] is True
        assert data["duration_minutes"] == 240
        assert "conflicts" in data

    async def test_delete_task_schedule(
        self, client: AsyncClient, test_user, test_task_schedule, auth_headers, db_session
    ):
        """Test deleting a task schedule."""
        # Execute
        response = await client.delete(
            f"/api/v1/task-schedules/{test_task_schedule.id}",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        
        # Verify the schedule was deleted from the database
        result = await db_session.get(TaskSchedule, test_task_schedule.id)
        assert result is None

    async def test_get_schedules_in_timerange(
        self, client: AsyncClient, test_user, test_task_schedule, auth_headers
    ):
        """Test getting task schedules within a time range."""
        # Setup
        start_time = datetime.utcnow() - timedelta(hours=1)
        end_time = datetime.utcnow() + timedelta(hours=3)
        
        # Execute
        response = await client.get(
            f"/api/v1/task-schedules/range/{start_time.isoformat()}/{end_time.isoformat()}",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(schedule["id"] == str(test_task_schedule.id) for schedule in data)
