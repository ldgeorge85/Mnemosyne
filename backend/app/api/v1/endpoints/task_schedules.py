"""
Task schedule endpoints for the Mnemosyne application.

This module provides API endpoints for managing task schedules.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_async_db
from app.db.models.user import User
from app.services.task.task_schedule_service import TaskScheduleService
from app.schemas.task_schedule import (
    TaskScheduleCreate,
    TaskScheduleUpdate,
    TaskSchedule,
    TaskScheduleWithConflicts
)

router = APIRouter()


@router.post("/", response_model=TaskScheduleWithConflicts)
async def create_task_schedule(
    schedule_data: TaskScheduleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
    check_conflicts: bool = Query(True, description="Whether to check for conflicts")
):
    """Create a new task schedule.
    
    Args:
        schedule_data: The schedule data to create.
        current_user: The current authenticated user.
        db: The database session.
        check_conflicts: Whether to check for conflicts.
        
    Returns:
        The created schedule with any conflicts.
        
    Raises:
        HTTPException: If the task does not exist or does not belong to the user.
    """
    task_schedule_service = TaskScheduleService(db)
    
    try:
        schedule, conflicts = await task_schedule_service.create_schedule(
            user_id=current_user.id,
            schedule_data=schedule_data,
            check_conflicts=check_conflicts
        )
        
        # Commit the transaction
        await db.commit()
        
        # Return the schedule with conflicts
        return TaskScheduleWithConflicts(
            **schedule.__dict__,
            conflicts=conflicts
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{schedule_id}", response_model=TaskSchedule)
async def get_task_schedule(
    schedule_id: UUID = Path(..., description="The ID of the schedule to retrieve"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get a task schedule by ID.
    
    Args:
        schedule_id: The ID of the schedule to retrieve.
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        The task schedule.
        
    Raises:
        HTTPException: If the schedule does not exist or does not belong to the user.
    """
    task_schedule_service = TaskScheduleService(db)
    
    try:
        schedule = await task_schedule_service.get_schedule(
            user_id=current_user.id,
            schedule_id=schedule_id
        )
        
        if not schedule:
            raise HTTPException(status_code=404, detail=f"Schedule with ID {schedule_id} not found")
        
        return schedule
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/task/{task_id}", response_model=TaskSchedule)
async def get_task_schedule_by_task(
    task_id: UUID = Path(..., description="The ID of the task to retrieve the schedule for"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get a task schedule by task ID.
    
    Args:
        task_id: The ID of the task to retrieve the schedule for.
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        The task schedule.
        
    Raises:
        HTTPException: If the task does not exist, does not belong to the user, or has no schedule.
    """
    task_schedule_service = TaskScheduleService(db)
    
    try:
        schedule = await task_schedule_service.get_schedule_by_task(
            user_id=current_user.id,
            task_id=task_id
        )
        
        if not schedule:
            raise HTTPException(status_code=404, detail=f"No schedule found for task with ID {task_id}")
        
        return schedule
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.put("/{schedule_id}", response_model=TaskScheduleWithConflicts)
async def update_task_schedule(
    schedule_data: TaskScheduleUpdate,
    schedule_id: UUID = Path(..., description="The ID of the schedule to update"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
    check_conflicts: bool = Query(True, description="Whether to check for conflicts")
):
    """Update a task schedule.
    
    Args:
        schedule_data: The schedule data to update.
        schedule_id: The ID of the schedule to update.
        current_user: The current authenticated user.
        db: The database session.
        check_conflicts: Whether to check for conflicts.
        
    Returns:
        The updated schedule with any conflicts.
        
    Raises:
        HTTPException: If the schedule does not exist or does not belong to the user.
    """
    task_schedule_service = TaskScheduleService(db)
    
    try:
        schedule, conflicts = await task_schedule_service.update_schedule(
            user_id=current_user.id,
            schedule_id=schedule_id,
            schedule_data=schedule_data,
            check_conflicts=check_conflicts
        )
        
        if not schedule:
            raise HTTPException(status_code=404, detail=f"Schedule with ID {schedule_id} not found")
        
        # Commit the transaction
        await db.commit()
        
        # Return the schedule with conflicts
        return TaskScheduleWithConflicts(
            **schedule.__dict__,
            conflicts=conflicts
        )
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{schedule_id}", response_model=Dict[str, bool])
async def delete_task_schedule(
    schedule_id: UUID = Path(..., description="The ID of the schedule to delete"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Delete a task schedule.
    
    Args:
        schedule_id: The ID of the schedule to delete.
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        Dictionary with success status.
        
    Raises:
        HTTPException: If the schedule does not exist or does not belong to the user.
    """
    task_schedule_service = TaskScheduleService(db)
    
    try:
        success = await task_schedule_service.delete_schedule(
            user_id=current_user.id,
            schedule_id=schedule_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Schedule with ID {schedule_id} not found")
        
        # Commit the transaction
        await db.commit()
        
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/range/{start_time}/{end_time}", response_model=List[TaskSchedule])
async def get_schedules_in_timerange(
    start_time: datetime = Path(..., description="The start time of the range (ISO format)"),
    end_time: datetime = Path(..., description="The end time of the range (ISO format)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all task schedules within a time range.
    
    Args:
        start_time: The start time of the range.
        end_time: The end time of the range.
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        List of task schedules within the time range.
    """
    task_schedule_service = TaskScheduleService(db)
    
    schedules = await task_schedule_service.get_schedules_in_timerange(
        user_id=current_user.id,
        start_time=start_time,
        end_time=end_time
    )
    
    return schedules
