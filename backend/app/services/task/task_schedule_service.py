"""
Task schedule service for the Mnemosyne application.

This module provides business logic for managing task schedules.
"""
from datetime import datetime, timedelta
import pytz
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.task_schedule import TaskScheduleRepository
from app.db.repositories.task import TaskRepository
from app.db.models.task_schedule import TaskSchedule
from app.schemas.task_schedule import TaskScheduleCreate, TaskScheduleUpdate, TaskScheduleWithConflicts


class TaskScheduleService:
    """Service for task schedule operations."""

    def __init__(self, db_session: AsyncSession):
        """Initialize the service with a database session.
        
        Args:
            db_session: The database session to use for operations.
        """
        self.db_session = db_session
        self.task_schedule_repository = TaskScheduleRepository(db_session)
        self.task_repository = TaskRepository(db_session)

    async def create_schedule(
        self, 
        user_id: UUID, 
        schedule_data: TaskScheduleCreate,
        check_conflicts: bool = True
    ) -> Tuple[TaskSchedule, List[UUID]]:
        """Create a new task schedule.
        
        Args:
            user_id: The ID of the user creating the schedule.
            schedule_data: The schedule data to create.
            check_conflicts: Whether to check for conflicts.
            
        Returns:
            Tuple of the created schedule and list of conflicting task IDs.
            
        Raises:
            ValueError: If the task does not exist or does not belong to the user.
        """
        # Verify task exists and belongs to the user
        task = await self.task_repository.get_by_id(schedule_data.task_id)
        if not task:
            raise ValueError(f"Task with ID {schedule_data.task_id} not found")
        if task.user_id != user_id:
            raise ValueError(f"Task with ID {schedule_data.task_id} does not belong to user {user_id}")
        
        # Check for conflicts if requested
        conflicts = []
        if check_conflicts:
            conflicting_schedules = await self.task_schedule_repository.detect_conflicts(
                user_id=user_id,
                start_time=schedule_data.start_time,
                due_time=schedule_data.due_time
            )
            conflicts = [schedule.task_id for schedule in conflicting_schedules]
        
        # Create the schedule
        schedule_dict = schedule_data.dict()
        schedule = await self.task_schedule_repository.create(schedule_dict)
        
        return schedule, conflicts

    async def get_schedule(self, user_id: UUID, schedule_id: UUID) -> Optional[TaskSchedule]:
        """Get a task schedule by ID.
        
        Args:
            user_id: The ID of the user requesting the schedule.
            schedule_id: The ID of the schedule to retrieve.
            
        Returns:
            The task schedule if found and belongs to the user, None otherwise.
            
        Raises:
            ValueError: If the schedule does not belong to the user.
        """
        schedule = await self.task_schedule_repository.get_by_id(schedule_id)
        if not schedule:
            return None
        
        # Verify the schedule belongs to the user
        task = await self.task_repository.get_by_id(schedule.task_id)
        if not task or task.user_id != user_id:
            raise ValueError(f"Schedule with ID {schedule_id} does not belong to user {user_id}")
        
        return schedule

    async def get_schedule_by_task(self, user_id: UUID, task_id: UUID) -> Optional[TaskSchedule]:
        """Get a task schedule by task ID.
        
        Args:
            user_id: The ID of the user requesting the schedule.
            task_id: The ID of the task to retrieve the schedule for.
            
        Returns:
            The task schedule if found and belongs to the user, None otherwise.
            
        Raises:
            ValueError: If the task does not belong to the user.
        """
        # Verify task belongs to the user
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            return None
        if task.user_id != user_id:
            raise ValueError(f"Task with ID {task_id} does not belong to user {user_id}")
        
        return await self.task_schedule_repository.get_by_task_id(task_id)

    async def update_schedule(
        self, 
        user_id: UUID, 
        schedule_id: UUID, 
        schedule_data: TaskScheduleUpdate,
        check_conflicts: bool = True
    ) -> Tuple[Optional[TaskSchedule], List[UUID]]:
        """Update a task schedule.
        
        Args:
            user_id: The ID of the user updating the schedule.
            schedule_id: The ID of the schedule to update.
            schedule_data: The schedule data to update.
            check_conflicts: Whether to check for conflicts.
            
        Returns:
            Tuple of the updated schedule and list of conflicting task IDs.
            
        Raises:
            ValueError: If the schedule does not belong to the user.
        """
        # Get the schedule
        schedule = await self.task_schedule_repository.get_by_id(schedule_id)
        if not schedule:
            return None, []
        
        # Verify the schedule belongs to the user
        task = await self.task_repository.get_by_id(schedule.task_id)
        if not task or task.user_id != user_id:
            raise ValueError(f"Schedule with ID {schedule_id} does not belong to user {user_id}")
        
        # Check for conflicts if requested
        conflicts = []
        if check_conflicts:
            # Use updated values or existing values
            start_time = schedule_data.start_time if schedule_data.start_time is not None else schedule.start_time
            due_time = schedule_data.due_time if schedule_data.due_time is not None else schedule.due_time
            
            if start_time or due_time:
                conflicting_schedules = await self.task_schedule_repository.detect_conflicts(
                    user_id=user_id,
                    start_time=start_time,
                    due_time=due_time,
                    exclude_task_id=schedule.task_id
                )
                conflicts = [s.task_id for s in conflicting_schedules]
        
        # Update the schedule
        schedule_dict = schedule_data.dict(exclude_unset=True)
        updated_schedule = await self.task_schedule_repository.update(schedule_id, schedule_dict)
        
        return updated_schedule, conflicts

    async def delete_schedule(self, user_id: UUID, schedule_id: UUID) -> bool:
        """Delete a task schedule.
        
        Args:
            user_id: The ID of the user deleting the schedule.
            schedule_id: The ID of the schedule to delete.
            
        Returns:
            True if the schedule was deleted, False otherwise.
            
        Raises:
            ValueError: If the schedule does not belong to the user.
        """
        # Get the schedule
        schedule = await self.task_schedule_repository.get_by_id(schedule_id)
        if not schedule:
            return False
        
        # Verify the schedule belongs to the user
        task = await self.task_repository.get_by_id(schedule.task_id)
        if not task or task.user_id != user_id:
            raise ValueError(f"Schedule with ID {schedule_id} does not belong to user {user_id}")
        
        return await self.task_schedule_repository.delete(schedule_id)

    async def get_schedules_in_timerange(
        self, 
        user_id: UUID, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[TaskSchedule]:
        """Get all task schedules within a time range for a user.
        
        Args:
            user_id: The ID of the user to get schedules for.
            start_time: The start time of the range.
            end_time: The end time of the range.
            
        Returns:
            List of task schedules within the time range.
        """
        return await self.task_schedule_repository.get_schedules_in_timerange(
            user_id=user_id,
            start_time=start_time,
            end_time=end_time
        )

    def convert_timezone(
        self, 
        dt: datetime, 
        from_tz: str, 
        to_tz: str
    ) -> datetime:
        """Convert a datetime from one timezone to another.
        
        Args:
            dt: The datetime to convert.
            from_tz: The source timezone.
            to_tz: The target timezone.
            
        Returns:
            The converted datetime.
        """
        from_timezone = pytz.timezone(from_tz)
        to_timezone = pytz.timezone(to_tz)
        
        # Localize the datetime to the source timezone
        dt_with_tz = from_timezone.localize(dt)
        
        # Convert to the target timezone
        return dt_with_tz.astimezone(to_timezone)
