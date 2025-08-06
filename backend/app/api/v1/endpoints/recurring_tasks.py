"""
Recurring task endpoints for the Mnemosyne application.

This module provides API endpoints for managing recurring tasks.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_async_db
from app.db.models.user import User
from app.services.task.recurring_task_service import RecurringTaskService
from app.schemas.task import TaskInDB, TaskUpdate

router = APIRouter()


@router.post("/{task_id}/instances", response_model=List[TaskInDB])
async def create_recurring_task_instances(
    task_id: UUID = Path(..., description="The ID of the master task"),
    recurrence_pattern: str = Body(..., description="The recurrence pattern (e.g., 'daily', 'weekly', 'every 2 weeks')"),
    count: Optional[int] = Body(None, description="Maximum number of instances to create"),
    end_date: Optional[datetime] = Body(None, description="End date for recurrence"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Create recurring task instances based on a master task.
    
    Args:
        task_id: The ID of the master task.
        recurrence_pattern: The recurrence pattern string.
        count: Maximum number of instances to create.
        end_date: End date for recurrence.
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        List of created task instances.
        
    Raises:
        HTTPException: If the task doesn't exist, pattern is invalid, or access is denied.
    """
    recurring_service = RecurringTaskService(db)
    
    try:
        created_tasks = await recurring_service.create_recurring_task_instances(
            task_id=task_id,
            user_id=current_user.id,
            recurrence_pattern=recurrence_pattern,
            count=count,
            end_date=end_date
        )
        return created_tasks
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create recurring tasks: {str(e)}")


@router.put("/{master_task_id}/series", response_model=List[TaskInDB])
async def update_recurring_task_series(
    master_task_id: UUID = Path(..., description="The ID of the master task"),
    update_data: TaskUpdate = Body(..., description="Data to update in the task series"),
    update_future_only: bool = Query(False, description="Whether to update only future instances"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Update a series of recurring tasks.
    
    Args:
        master_task_id: The ID of the master task.
        update_data: Data to update in the tasks.
        update_future_only: Whether to update only future instances.
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        List of updated tasks.
        
    Raises:
        HTTPException: If the task doesn't exist or access is denied.
    """
    recurring_service = RecurringTaskService(db)
    
    try:
        # Convert Pydantic model to dict, excluding None values
        update_dict = update_data.model_dump(exclude_unset=True, exclude_none=True)
        
        updated_tasks = await recurring_service.update_recurring_task_series(
            master_task_id=master_task_id,
            user_id=current_user.id,
            update_data=update_dict,
            update_future_only=update_future_only
        )
        return updated_tasks
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update recurring tasks: {str(e)}")


@router.delete("/{master_task_id}/series")
async def delete_recurring_task_series(
    master_task_id: UUID = Path(..., description="The ID of the master task"),
    delete_future_only: bool = Query(False, description="Whether to delete only future instances"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Delete a series of recurring tasks.
    
    Args:
        master_task_id: The ID of the master task.
        delete_future_only: Whether to delete only future instances.
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        Dictionary with the number of tasks deleted.
        
    Raises:
        HTTPException: If the task doesn't exist or access is denied.
    """
    recurring_service = RecurringTaskService(db)
    
    try:
        deleted_count = await recurring_service.delete_recurring_task_series(
            master_task_id=master_task_id,
            user_id=current_user.id,
            delete_future_only=delete_future_only
        )
        return {"deleted_count": deleted_count, "message": f"Successfully deleted {deleted_count} recurring tasks"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete recurring tasks: {str(e)}")


@router.post("/validate-pattern")
async def validate_recurrence_pattern(
    pattern: str = Body(..., description="The recurrence pattern to validate"),
    start_date: datetime = Body(..., description="Start date for pattern validation"),
    preview_count: int = Body(5, description="Number of dates to preview"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Validate a recurrence pattern and preview generated dates.
    
    Args:
        pattern: The recurrence pattern to validate.
        start_date: Start date for pattern validation.
        preview_count: Number of dates to preview.
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        Dictionary with validation result and preview dates.
        
    Raises:
        HTTPException: If the pattern is invalid.
    """
    recurring_service = RecurringTaskService(db)
    
    try:
        # Parse the pattern
        recurrence_data = recurring_service.parse_recurrence_pattern(pattern)
        
        # Generate preview dates
        preview_dates = recurring_service.generate_recurring_dates(
            start_date=start_date,
            recurrence_data=recurrence_data,
            count=preview_count
        )
        
        return {
            "valid": True,
            "pattern": pattern,
            "parsed_data": recurrence_data,
            "preview_dates": preview_dates,
            "message": f"Pattern is valid. Generated {len(preview_dates)} preview dates."
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid recurrence pattern: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate pattern: {str(e)}")


@router.get("/{master_task_id}/instances", response_model=List[TaskInDB])
async def get_recurring_task_instances(
    master_task_id: UUID = Path(..., description="The ID of the master task"),
    include_completed: bool = Query(True, description="Whether to include completed tasks"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get all instances of a recurring task series.
    
    Args:
        master_task_id: The ID of the master task.
        include_completed: Whether to include completed tasks.
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        List of recurring task instances.
        
    Raises:
        HTTPException: If the task doesn't exist or access is denied.
    """
    recurring_service = RecurringTaskService(db)
    
    try:
        # Get all recurring instances
        recurring_tasks = await recurring_service.task_repository.get_by_parent_id(master_task_id)
        
        # Filter by user and completion status
        filtered_tasks = []
        for task in recurring_tasks:
            if task.user_id != current_user.id:
                continue
            
            if not include_completed and task.status.value in ['completed', 'cancelled']:
                continue
            
            filtered_tasks.append(task)
        
        return filtered_tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recurring task instances: {str(e)}")
