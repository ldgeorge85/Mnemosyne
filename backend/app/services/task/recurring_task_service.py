"""
Recurring task service for the Mnemosyne application.

This module provides business logic for managing recurring tasks,
including parsing recurrence patterns and generating task instances.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Generator
from uuid import UUID
import re
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.task import TaskRepository
from app.db.repositories.task_schedule import TaskScheduleRepository
from app.db.models.task import Task, TaskStatus, TaskPriority
from app.db.models.task_schedule import TaskSchedule
from app.services.task.task_service import TaskService


class RecurrenceType(str, Enum):
    """Enumeration of supported recurrence types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class RecurringTaskService:
    """
    Service for recurring task management.
    
    This class provides methods for parsing recurrence patterns,
    generating recurring task instances, and managing recurring task schedules.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the recurring task service with a database session.
        
        Args:
            db: The SQLAlchemy async database session.
        """
        self.db = db
        self.task_repository = TaskRepository(db)
        self.schedule_repository = TaskScheduleRepository(db)
        self.task_service = TaskService(db)
    
    def parse_recurrence_pattern(self, pattern: str) -> Dict[str, Any]:
        """
        Parse a recurrence pattern string into structured data.
        
        Supported patterns:
        - "daily" or "every day"
        - "weekly" or "every week"
        - "monthly" or "every month"
        - "yearly" or "every year"
        - "every N days/weeks/months/years"
        - "weekdays" (Monday-Friday)
        - "weekends" (Saturday-Sunday)
        - "every monday,wednesday,friday"
        
        Args:
            pattern: The recurrence pattern string.
            
        Returns:
            Dictionary containing parsed recurrence data.
            
        Raises:
            ValueError: If the pattern is invalid or unsupported.
        """
        if not pattern:
            raise ValueError("Recurrence pattern cannot be empty")
        
        pattern = pattern.lower().strip()
        
        # Simple patterns
        simple_patterns = {
            "daily": {"type": RecurrenceType.DAILY, "interval": 1},
            "every day": {"type": RecurrenceType.DAILY, "interval": 1},
            "weekly": {"type": RecurrenceType.WEEKLY, "interval": 1},
            "every week": {"type": RecurrenceType.WEEKLY, "interval": 1},
            "monthly": {"type": RecurrenceType.MONTHLY, "interval": 1},
            "every month": {"type": RecurrenceType.MONTHLY, "interval": 1},
            "yearly": {"type": RecurrenceType.YEARLY, "interval": 1},
            "every year": {"type": RecurrenceType.YEARLY, "interval": 1},
            "weekdays": {"type": RecurrenceType.CUSTOM, "weekdays": [0, 1, 2, 3, 4]},  # Mon-Fri
            "weekends": {"type": RecurrenceType.CUSTOM, "weekdays": [5, 6]},  # Sat-Sun
        }
        
        if pattern in simple_patterns:
            return simple_patterns[pattern]
        
        # Pattern: "every N days/weeks/months/years"
        interval_match = re.match(r"every (\d+) (day|week|month|year)s?", pattern)
        if interval_match:
            interval = int(interval_match.group(1))
            unit = interval_match.group(2)
            
            type_mapping = {
                "day": RecurrenceType.DAILY,
                "week": RecurrenceType.WEEKLY,
                "month": RecurrenceType.MONTHLY,
                "year": RecurrenceType.YEARLY,
            }
            
            return {"type": type_mapping[unit], "interval": interval}
        
        # Pattern: "every monday,wednesday,friday"
        weekday_match = re.match(r"every ((?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)(?:,(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday))*)", pattern)
        if weekday_match:
            weekday_names = weekday_match.group(1).split(",")
            weekday_mapping = {
                "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                "friday": 4, "saturday": 5, "sunday": 6
            }
            
            weekdays = [weekday_mapping[day.strip()] for day in weekday_names]
            return {"type": RecurrenceType.CUSTOM, "weekdays": weekdays}
        
        raise ValueError(f"Unsupported recurrence pattern: {pattern}")
    
    def generate_recurring_dates(
        self,
        start_date: datetime,
        recurrence_data: Dict[str, Any],
        count: Optional[int] = None,
        end_date: Optional[datetime] = None,
        max_instances: int = 100
    ) -> List[datetime]:
        """
        Generate a list of dates based on recurrence pattern.
        
        Args:
            start_date: The starting date for recurrence.
            recurrence_data: Parsed recurrence data from parse_recurrence_pattern.
            count: Maximum number of instances to generate.
            end_date: End date for recurrence (exclusive).
            max_instances: Safety limit for maximum instances.
            
        Returns:
            List of datetime objects representing recurring dates.
        """
        dates = []
        current_date = start_date
        generated_count = 0
        
        # Safety limit
        if count and count > max_instances:
            count = max_instances
        
        recurrence_type = recurrence_data["type"]
        
        while generated_count < (count or max_instances):
            # Check end date condition
            if end_date and current_date >= end_date:
                break
            
            # Add current date if it matches the pattern
            if self._date_matches_pattern(current_date, recurrence_data):
                dates.append(current_date)
                generated_count += 1
            
            # Move to next potential date
            current_date = self._get_next_date(current_date, recurrence_type, recurrence_data)
            
            # Safety check to prevent infinite loops
            if current_date > start_date + timedelta(days=365 * 10):  # 10 years max
                break
        
        return dates
    
    def _date_matches_pattern(self, date: datetime, recurrence_data: Dict[str, Any]) -> bool:
        """
        Check if a date matches the recurrence pattern.
        
        Args:
            date: The date to check.
            recurrence_data: Parsed recurrence data.
            
        Returns:
            True if the date matches the pattern, False otherwise.
        """
        recurrence_type = recurrence_data["type"]
        
        if recurrence_type == RecurrenceType.CUSTOM:
            if "weekdays" in recurrence_data:
                return date.weekday() in recurrence_data["weekdays"]
        
        return True  # For interval-based patterns, all dates in sequence match
    
    def _get_next_date(self, current_date: datetime, recurrence_type: RecurrenceType, recurrence_data: Dict[str, Any]) -> datetime:
        """
        Get the next date in the recurrence sequence.
        
        Args:
            current_date: The current date.
            recurrence_type: The type of recurrence.
            recurrence_data: Parsed recurrence data.
            
        Returns:
            The next date in the sequence.
        """
        interval = recurrence_data.get("interval", 1)
        
        if recurrence_type == RecurrenceType.DAILY:
            return current_date + timedelta(days=interval)
        elif recurrence_type == RecurrenceType.WEEKLY:
            return current_date + timedelta(weeks=interval)
        elif recurrence_type == RecurrenceType.MONTHLY:
            # Handle month boundaries properly
            next_month = current_date.month + interval
            next_year = current_date.year + (next_month - 1) // 12
            next_month = ((next_month - 1) % 12) + 1
            
            try:
                return current_date.replace(year=next_year, month=next_month)
            except ValueError:
                # Handle cases like Feb 31 -> Feb 28/29
                import calendar
                last_day = calendar.monthrange(next_year, next_month)[1]
                day = min(current_date.day, last_day)
                return current_date.replace(year=next_year, month=next_month, day=day)
        elif recurrence_type == RecurrenceType.YEARLY:
            try:
                return current_date.replace(year=current_date.year + interval)
            except ValueError:
                # Handle leap year edge case (Feb 29)
                return current_date.replace(year=current_date.year + interval, day=28)
        elif recurrence_type == RecurrenceType.CUSTOM:
            # For custom patterns, move to next day and let matching logic handle it
            return current_date + timedelta(days=1)
        
        return current_date + timedelta(days=1)
    
    async def create_recurring_task_instances(
        self,
        task_id: UUID,
        user_id: UUID,
        recurrence_pattern: str,
        count: Optional[int] = None,
        end_date: Optional[datetime] = None
    ) -> List[Task]:
        """
        Create recurring task instances based on a master task.
        
        Args:
            task_id: The ID of the master task.
            user_id: The ID of the user.
            recurrence_pattern: The recurrence pattern string.
            count: Maximum number of instances to create.
            end_date: End date for recurrence.
            
        Returns:
            List of created task instances.
            
        Raises:
            ValueError: If the task doesn't exist or pattern is invalid.
        """
        # Get the master task
        master_task = await self.task_repository.get_by_id(task_id)
        if not master_task or master_task.user_id != user_id:
            raise ValueError("Task not found or access denied")
        
        # Get the task schedule
        schedule = await self.schedule_repository.get_by_task_id(task_id)
        if not schedule:
            raise ValueError("Task must have a schedule to create recurring instances")
        
        # Parse recurrence pattern
        recurrence_data = self.parse_recurrence_pattern(recurrence_pattern)
        
        # Generate recurring dates
        start_date = schedule.due_time
        recurring_dates = self.generate_recurring_dates(
            start_date,
            recurrence_data,
            count,
            end_date
        )
        
        # Create task instances
        created_tasks = []
        for i, due_date in enumerate(recurring_dates[1:], 1):  # Skip first date (original task)
            # Create new task instance
            new_task = await self.task_service.create_task(
                title=f"{master_task.title} (#{i})",
                user_id=user_id,
                description=master_task.description,
                status=TaskStatus.PENDING,
                priority=master_task.priority,
                due_date=due_date,
                tags=master_task.tags,
                metadata={
                    **master_task.metadata,
                    "recurring_master_id": str(task_id),
                    "recurring_instance": i,
                    "recurring_pattern": recurrence_pattern
                },
                parent_id=task_id,
                agent_id=master_task.agent_id
            )
            
            created_tasks.append(new_task)
        
        return created_tasks
    
    async def update_recurring_task_series(
        self,
        master_task_id: UUID,
        user_id: UUID,
        update_data: Dict[str, Any],
        update_future_only: bool = False
    ) -> List[Task]:
        """
        Update a series of recurring tasks.
        
        Args:
            master_task_id: The ID of the master task.
            user_id: The ID of the user.
            update_data: Data to update in the tasks.
            update_future_only: Whether to update only future instances.
            
        Returns:
            List of updated tasks.
        """
        # Get all recurring instances
        recurring_tasks = await self.task_repository.get_by_parent_id(master_task_id)
        
        updated_tasks = []
        current_time = datetime.utcnow()
        
        for task in recurring_tasks:
            if task.user_id != user_id:
                continue
            
            # Skip past tasks if update_future_only is True
            if update_future_only and task.due_date and task.due_date < current_time:
                continue
            
            # Update the task
            updated_task = await self.task_service.update_task(
                task.id,
                user_id,
                **update_data
            )
            updated_tasks.append(updated_task)
        
        return updated_tasks
    
    async def delete_recurring_task_series(
        self,
        master_task_id: UUID,
        user_id: UUID,
        delete_future_only: bool = False
    ) -> int:
        """
        Delete a series of recurring tasks.
        
        Args:
            master_task_id: The ID of the master task.
            user_id: The ID of the user.
            delete_future_only: Whether to delete only future instances.
            
        Returns:
            Number of tasks deleted.
        """
        # Get all recurring instances
        recurring_tasks = await self.task_repository.get_by_parent_id(master_task_id)
        
        deleted_count = 0
        current_time = datetime.utcnow()
        
        for task in recurring_tasks:
            if task.user_id != user_id:
                continue
            
            # Skip past tasks if delete_future_only is True
            if delete_future_only and task.due_date and task.due_date < current_time:
                continue
            
            # Delete the task
            await self.task_service.delete_task(task.id, user_id)
            deleted_count += 1
        
        return deleted_count
