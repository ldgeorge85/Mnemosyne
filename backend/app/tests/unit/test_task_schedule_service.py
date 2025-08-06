"""
Unit tests for TaskScheduleService.

This module contains unit tests for the TaskScheduleService class.
"""
import uuid
from datetime import datetime, timedelta
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.task.task_schedule_service import TaskScheduleService
from app.db.models.task_schedule import TaskSchedule
from app.db.models.task import Task
from app.schemas.task_schedule import TaskScheduleCreate, TaskScheduleUpdate


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    return AsyncMock()


@pytest.fixture
def mock_task_schedule_repository():
    """Create a mock task schedule repository."""
    with patch("app.services.task.task_schedule_service.TaskScheduleRepository") as mock:
        repository_instance = AsyncMock()
        mock.return_value = repository_instance
        yield repository_instance


@pytest.fixture
def mock_task_repository():
    """Create a mock task repository."""
    with patch("app.services.task.task_schedule_service.TaskRepository") as mock:
        repository_instance = AsyncMock()
        mock.return_value = repository_instance
        yield repository_instance


@pytest.fixture
def task_schedule_service(mock_db_session, mock_task_schedule_repository, mock_task_repository):
    """Create a TaskScheduleService instance with mocked dependencies."""
    return TaskScheduleService(mock_db_session)


@pytest.fixture
def sample_user_id():
    """Create a sample user ID."""
    return uuid.uuid4()


@pytest.fixture
def sample_task_id():
    """Create a sample task ID."""
    return uuid.uuid4()


@pytest.fixture
def sample_schedule_id():
    """Create a sample schedule ID."""
    return uuid.uuid4()


@pytest.fixture
def sample_task(sample_user_id, sample_task_id):
    """Create a sample task."""
    task = MagicMock(spec=Task)
    task.id = sample_task_id
    task.user_id = sample_user_id
    return task


@pytest.fixture
def sample_schedule(sample_task_id, sample_schedule_id):
    """Create a sample task schedule."""
    schedule = MagicMock(spec=TaskSchedule)
    schedule.id = sample_schedule_id
    schedule.task_id = sample_task_id
    schedule.start_time = datetime.utcnow()
    schedule.due_time = datetime.utcnow() + timedelta(hours=2)
    schedule.timezone = "UTC"
    schedule.__dict__ = {
        "id": schedule.id,
        "task_id": schedule.task_id,
        "start_time": schedule.start_time,
        "due_time": schedule.due_time,
        "timezone": schedule.timezone,
        "is_all_day": False,
        "duration_minutes": 120,
        "recurrence_pattern": None,
        "recurrence_count": None,
        "recurrence_end_date": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    return schedule


@pytest.fixture
def sample_schedule_create_data(sample_task_id):
    """Create sample data for creating a task schedule."""
    return TaskScheduleCreate(
        task_id=sample_task_id,
        start_time=datetime.utcnow(),
        due_time=datetime.utcnow() + timedelta(hours=2),
        timezone="UTC",
        is_all_day=False,
        duration_minutes=120
    )


@pytest.fixture
def sample_schedule_update_data():
    """Create sample data for updating a task schedule."""
    return TaskScheduleUpdate(
        start_time=datetime.utcnow() + timedelta(hours=1),
        due_time=datetime.utcnow() + timedelta(hours=3),
        timezone="America/New_York",
        is_all_day=True,
        duration_minutes=180
    )


class TestTaskScheduleService:
    """Test cases for TaskScheduleService."""

    async def test_create_schedule(
        self,
        task_schedule_service,
        mock_task_repository,
        mock_task_schedule_repository,
        sample_user_id,
        sample_task,
        sample_schedule_create_data,
        sample_schedule
    ):
        """Test creating a task schedule."""
        # Setup
        mock_task_repository.get_by_id.return_value = sample_task
        mock_task_schedule_repository.detect_conflicts.return_value = []
        mock_task_schedule_repository.create.return_value = sample_schedule

        # Execute
        schedule, conflicts = await task_schedule_service.create_schedule(
            user_id=sample_user_id,
            schedule_data=sample_schedule_create_data,
            check_conflicts=True
        )

        # Assert
        mock_task_repository.get_by_id.assert_called_once_with(sample_schedule_create_data.task_id)
        mock_task_schedule_repository.detect_conflicts.assert_called_once()
        mock_task_schedule_repository.create.assert_called_once()
        assert schedule == sample_schedule
        assert conflicts == []

    async def test_create_schedule_task_not_found(
        self,
        task_schedule_service,
        mock_task_repository,
        sample_user_id,
        sample_schedule_create_data
    ):
        """Test creating a task schedule when the task does not exist."""
        # Setup
        mock_task_repository.get_by_id.return_value = None

        # Execute & Assert
        with pytest.raises(ValueError, match=f"Task with ID {sample_schedule_create_data.task_id} not found"):
            await task_schedule_service.create_schedule(
                user_id=sample_user_id,
                schedule_data=sample_schedule_create_data
            )

    async def test_create_schedule_unauthorized(
        self,
        task_schedule_service,
        mock_task_repository,
        sample_user_id,
        sample_task,
        sample_schedule_create_data
    ):
        """Test creating a task schedule when the user is not authorized."""
        # Setup
        different_user_id = uuid.uuid4()
        sample_task.user_id = different_user_id
        mock_task_repository.get_by_id.return_value = sample_task

        # Execute & Assert
        with pytest.raises(ValueError, match=f"Task with ID {sample_schedule_create_data.task_id} does not belong to user"):
            await task_schedule_service.create_schedule(
                user_id=sample_user_id,
                schedule_data=sample_schedule_create_data
            )

    async def test_create_schedule_with_conflicts(
        self,
        task_schedule_service,
        mock_task_repository,
        mock_task_schedule_repository,
        sample_user_id,
        sample_task,
        sample_schedule_create_data,
        sample_schedule
    ):
        """Test creating a task schedule with conflicts."""
        # Setup
        conflict_task_id = uuid.uuid4()
        conflict_schedule = MagicMock(spec=TaskSchedule)
        conflict_schedule.task_id = conflict_task_id
        
        mock_task_repository.get_by_id.return_value = sample_task
        mock_task_schedule_repository.detect_conflicts.return_value = [conflict_schedule]
        mock_task_schedule_repository.create.return_value = sample_schedule

        # Execute
        schedule, conflicts = await task_schedule_service.create_schedule(
            user_id=sample_user_id,
            schedule_data=sample_schedule_create_data,
            check_conflicts=True
        )

        # Assert
        mock_task_repository.get_by_id.assert_called_once_with(sample_schedule_create_data.task_id)
        mock_task_schedule_repository.detect_conflicts.assert_called_once()
        mock_task_schedule_repository.create.assert_called_once()
        assert schedule == sample_schedule
        assert conflicts == [conflict_task_id]

    async def test_get_schedule(
        self,
        task_schedule_service,
        mock_task_schedule_repository,
        mock_task_repository,
        sample_user_id,
        sample_task,
        sample_schedule,
        sample_schedule_id
    ):
        """Test getting a task schedule by ID."""
        # Setup
        mock_task_schedule_repository.get_by_id.return_value = sample_schedule
        mock_task_repository.get_by_id.return_value = sample_task

        # Execute
        schedule = await task_schedule_service.get_schedule(
            user_id=sample_user_id,
            schedule_id=sample_schedule_id
        )

        # Assert
        mock_task_schedule_repository.get_by_id.assert_called_once_with(sample_schedule_id)
        mock_task_repository.get_by_id.assert_called_once_with(sample_schedule.task_id)
        assert schedule == sample_schedule

    async def test_get_schedule_not_found(
        self,
        task_schedule_service,
        mock_task_schedule_repository,
        sample_user_id,
        sample_schedule_id
    ):
        """Test getting a task schedule by ID when it does not exist."""
        # Setup
        mock_task_schedule_repository.get_by_id.return_value = None

        # Execute
        schedule = await task_schedule_service.get_schedule(
            user_id=sample_user_id,
            schedule_id=sample_schedule_id
        )

        # Assert
        mock_task_schedule_repository.get_by_id.assert_called_once_with(sample_schedule_id)
        assert schedule is None

    async def test_get_schedule_unauthorized(
        self,
        task_schedule_service,
        mock_task_schedule_repository,
        mock_task_repository,
        sample_user_id,
        sample_task,
        sample_schedule,
        sample_schedule_id
    ):
        """Test getting a task schedule by ID when the user is not authorized."""
        # Setup
        different_user_id = uuid.uuid4()
        sample_task.user_id = different_user_id
        mock_task_schedule_repository.get_by_id.return_value = sample_schedule
        mock_task_repository.get_by_id.return_value = sample_task

        # Execute & Assert
        with pytest.raises(ValueError, match=f"Schedule with ID {sample_schedule_id} does not belong to user"):
            await task_schedule_service.get_schedule(
                user_id=sample_user_id,
                schedule_id=sample_schedule_id
            )

    async def test_update_schedule(
        self,
        task_schedule_service,
        mock_task_schedule_repository,
        mock_task_repository,
        sample_user_id,
        sample_task,
        sample_schedule,
        sample_schedule_id,
        sample_schedule_update_data
    ):
        """Test updating a task schedule."""
        # Setup
        mock_task_schedule_repository.get_by_id.return_value = sample_schedule
        mock_task_repository.get_by_id.return_value = sample_task
        mock_task_schedule_repository.detect_conflicts.return_value = []
        mock_task_schedule_repository.update.return_value = sample_schedule

        # Execute
        schedule, conflicts = await task_schedule_service.update_schedule(
            user_id=sample_user_id,
            schedule_id=sample_schedule_id,
            schedule_data=sample_schedule_update_data,
            check_conflicts=True
        )

        # Assert
        mock_task_schedule_repository.get_by_id.assert_called_once_with(sample_schedule_id)
        mock_task_repository.get_by_id.assert_called_once_with(sample_schedule.task_id)
        mock_task_schedule_repository.detect_conflicts.assert_called_once()
        mock_task_schedule_repository.update.assert_called_once()
        assert schedule == sample_schedule
        assert conflicts == []

    async def test_delete_schedule(
        self,
        task_schedule_service,
        mock_task_schedule_repository,
        mock_task_repository,
        sample_user_id,
        sample_task,
        sample_schedule,
        sample_schedule_id
    ):
        """Test deleting a task schedule."""
        # Setup
        mock_task_schedule_repository.get_by_id.return_value = sample_schedule
        mock_task_repository.get_by_id.return_value = sample_task
        mock_task_schedule_repository.delete.return_value = True

        # Execute
        result = await task_schedule_service.delete_schedule(
            user_id=sample_user_id,
            schedule_id=sample_schedule_id
        )

        # Assert
        mock_task_schedule_repository.get_by_id.assert_called_once_with(sample_schedule_id)
        mock_task_repository.get_by_id.assert_called_once_with(sample_schedule.task_id)
        mock_task_schedule_repository.delete.assert_called_once_with(sample_schedule_id)
        assert result is True
