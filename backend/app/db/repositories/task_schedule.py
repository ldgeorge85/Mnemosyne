"""
Task schedule repository for the Mnemosyne application.

This module provides database operations for task schedules.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_, or_, between
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.task_schedule import TaskSchedule
from app.db.models.task import Task


class TaskScheduleRepository:
    """Repository for task schedule operations."""

    def __init__(self, db_session: AsyncSession):
        """Initialize the repository with a database session.
        
        Args:
            db_session: The database session to use for operations.
        """
        self.db_session = db_session

    async def create(self, task_schedule_data: Dict[str, Any]) -> TaskSchedule:
        """Create a new task schedule.
        
        Args:
            task_schedule_data: Dictionary containing task schedule data.
            
        Returns:
            The created task schedule.
        """
        task_schedule = TaskSchedule(**task_schedule_data)
        self.db_session.add(task_schedule)
        await self.db_session.flush()
        return task_schedule

    async def get_by_id(self, schedule_id: UUID) -> Optional[TaskSchedule]:
        """Get a task schedule by ID.
        
        Args:
            schedule_id: The ID of the task schedule to retrieve.
            
        Returns:
            The task schedule if found, None otherwise.
        """
        query = select(TaskSchedule).where(TaskSchedule.id == schedule_id)
        result = await self.db_session.execute(query)
        return result.scalars().first()

    async def get_by_task_id(self, task_id: UUID) -> Optional[TaskSchedule]:
        """Get a task schedule by task ID.
        
        Args:
            task_id: The ID of the task to retrieve the schedule for.
            
        Returns:
            The task schedule if found, None otherwise.
        """
        query = select(TaskSchedule).where(TaskSchedule.task_id == task_id)
        result = await self.db_session.execute(query)
        return result.scalars().first()

    async def update(
        self, schedule_id: UUID, task_schedule_data: Dict[str, Any]
    ) -> Optional[TaskSchedule]:
        """Update a task schedule.
        
        Args:
            schedule_id: The ID of the task schedule to update.
            task_schedule_data: Dictionary containing task schedule data to update.
            
        Returns:
            The updated task schedule if found, None otherwise.
        """
        task_schedule = await self.get_by_id(schedule_id)
        if not task_schedule:
            return None

        for key, value in task_schedule_data.items():
            setattr(task_schedule, key, value)

        await self.db_session.flush()
        return task_schedule

    async def delete(self, schedule_id: UUID) -> bool:
        """Delete a task schedule.
        
        Args:
            schedule_id: The ID of the task schedule to delete.
            
        Returns:
            True if the task schedule was deleted, False otherwise.
        """
        task_schedule = await self.get_by_id(schedule_id)
        if not task_schedule:
            return False

        await self.db_session.delete(task_schedule)
        await self.db_session.flush()
        return True

    async def get_schedules_in_timerange(
        self, 
        user_id: UUID, 
        start_time: datetime, 
        end_time: datetime,
        exclude_task_id: Optional[UUID] = None
    ) -> List[TaskSchedule]:
        """Get all task schedules within a time range for a user.
        
        Args:
            user_id: The ID of the user to get schedules for.
            start_time: The start time of the range.
            end_time: The end time of the range.
            exclude_task_id: Optional task ID to exclude from results.
            
        Returns:
            List of task schedules within the time range.
        """
        query = (
            select(TaskSchedule)
            .join(Task, TaskSchedule.task_id == Task.id)
            .where(
                and_(
                    Task.user_id == user_id,
                    or_(
                        # Schedule starts within range
                        and_(
                            TaskSchedule.start_time >= start_time,
                            TaskSchedule.start_time <= end_time
                        ),
                        # Schedule ends within range
                        and_(
                            TaskSchedule.due_time >= start_time,
                            TaskSchedule.due_time <= end_time
                        ),
                        # Schedule spans range
                        and_(
                            TaskSchedule.start_time <= start_time,
                            TaskSchedule.due_time >= end_time
                        )
                    )
                )
            )
        )
        
        if exclude_task_id:
            query = query.where(TaskSchedule.task_id != exclude_task_id)
            
        result = await self.db_session.execute(query)
        return result.scalars().all()

    async def detect_conflicts(
        self, 
        user_id: UUID, 
        start_time: Optional[datetime], 
        due_time: datetime,
        exclude_task_id: Optional[UUID] = None
    ) -> List[TaskSchedule]:
        """Detect conflicts with other task schedules.
        
        Args:
            user_id: The ID of the user to check conflicts for.
            start_time: The start time of the schedule.
            due_time: The due time of the schedule.
            exclude_task_id: Optional task ID to exclude from conflict detection.
            
        Returns:
            List of conflicting task schedules.
        """
        # If no start time is provided, use due time as start time
        effective_start = start_time if start_time else due_time
        
        return await self.get_schedules_in_timerange(
            user_id=user_id,
            start_time=effective_start,
            end_time=due_time,
            exclude_task_id=exclude_task_id
        )
