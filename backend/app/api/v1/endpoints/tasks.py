"""
Task API endpoints for the Mnemosyne application.

This module provides REST API endpoints for task management,
including creating, retrieving, updating, and deleting tasks.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.db import get_async_db
from app.core.auth.manager import get_current_user
from app.core.auth.base import AuthUser
from app.db.models.task import TaskStatus, TaskPriority, QuestType
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskInDB,
    TaskWithLogs,
    TaskWithSubtasks,
    TaskResponse,
    TaskListResponse,
    TaskLogCreate,
    TaskLogInDB,
    TaskSearchParams,
    TaskCompleteRequest,
    TaskCompleteResponse,
    TaskStats
)
from app.services.task.task_service import TaskService
from app.services.task.task_intelligence import TaskIntelligenceService
from app.services.task.suggestion_engine import TaskSuggestionEngine


router = APIRouter()


def task_to_dict(task) -> dict:
    """Convert task model to dict to avoid lazy loading issues."""
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "user_id": task.user_id,
        "status": task.status,
        "priority": task.priority,
        "due_date": task.due_date,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "completed_at": task.completed_at,
        "started_at": task.started_at,
        "is_active": task.is_active,
        "tags": task.tags,
        "metadata": task.task_metadata,
        "parent_id": task.parent_id,
        "agent_id": task.agent_id,
        # Game mechanics fields
        "estimated_duration_minutes": task.estimated_duration_minutes,
        "actual_duration_minutes": task.actual_duration_minutes,
        "progress": task.progress,
        "difficulty": task.difficulty,
        "quest_type": task.quest_type,
        "experience_points": task.experience_points,
        "value_impact": task.value_impact,
        "skill_development": task.skill_development,
        "visibility_mask": task.visibility_mask,
        "is_shared": task.is_shared,
        "assignees": task.assignees,
        "requires_all_complete": task.requires_all_complete,
        "is_recurring": task.is_recurring,
        "recurrence_rule": task.recurrence_rule,
        "recurring_parent_id": task.recurring_parent_id,
        "context": task.context,
        "schedule": None  # Skip schedule to avoid lazy loading
    }


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Create a new task.
    
    Args:
        task_data: The task data.
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        The created task.
        
    Raises:
        HTTPException: If the user is not authorized to create the task.
    """
    task_service = TaskService(db)
    
    # Create the task with all game mechanics fields
    task = await task_service.create_task(
        title=task_data.title,
        user_id=str(current_user.user_id),
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        due_date=task_data.due_date,
        tags=task_data.tags,
        metadata=task_data.metadata,
        parent_id=task_data.parent_id,
        agent_id=task_data.agent_id,
        # Game mechanics fields
        estimated_duration_minutes=task_data.estimated_duration_minutes,
        difficulty=task_data.difficulty,
        quest_type=task_data.quest_type,
        value_impact=task_data.value_impact,
        skill_development=task_data.skill_development,
        visibility_mask=task_data.visibility_mask,
        is_shared=task_data.is_shared,
        assignees=task_data.assignees,
        is_recurring=task_data.is_recurring,
        recurrence_rule=task_data.recurrence_rule
    )
    
    await db.commit()
    await db.refresh(task)
    
    return {"task": task_to_dict(task)}


@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    include_inactive: bool = Query(False),
    status: Optional[List[TaskStatus]] = Query(None),
    priority: Optional[List[TaskPriority]] = Query(None),
    tags: Optional[List[str]] = Query(None),
    due_date_start: Optional[datetime] = Query(None),
    due_date_end: Optional[datetime] = Query(None),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    List tasks for the current user with optional filtering.
    
    Args:
        limit: Maximum number of tasks to return.
        offset: Number of tasks to skip.
        include_inactive: Whether to include inactive tasks.
        status: Filter by task status.
        priority: Filter by task priority.
        tags: Filter by task tags.
        due_date_start: Filter by due date (start).
        due_date_end: Filter by due date (end).
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        A list of tasks and the total count.
    """
    task_service = TaskService(db)
    tasks, total = await task_service.get_tasks_by_user_id(
        user_id=str(current_user.user_id),
        limit=limit,
        offset=offset,
        include_inactive=include_inactive,
        status=status,
        priority=priority,
        tags=tags,
        due_date_start=due_date_start,
        due_date_end=due_date_end
    )
    
    return {"items": tasks, "total": total}


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID = Path(...),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Get a task by ID.
    
    Args:
        task_id: The ID of the task to retrieve.
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        The task if found.
        
    Raises:
        HTTPException: If the task is not found or the user is not authorized.
    """
    task_service = TaskService(db)
    task = await task_service.get_task_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Ensure the user can only access their own tasks
    if str(task.user_id) != str(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own tasks"
        )
    
    return {"task": task}


@router.get("/{task_id}/with-logs", response_model=TaskWithLogs)
async def get_task_with_logs(
    task_id: UUID = Path(...),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Get a task by ID with its logs.
    
    Args:
        task_id: The ID of the task to retrieve.
        limit: Maximum number of logs to return.
        offset: Number of logs to skip.
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        The task with its logs if found.
        
    Raises:
        HTTPException: If the task is not found or the user is not authorized.
    """
    task_service = TaskService(db)
    task = await task_service.get_task_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Ensure the user can only access their own tasks
    if str(task.user_id) != str(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own tasks"
        )
    
    logs, _ = await task_service.get_task_logs(task_id, limit, offset)
    
    # Create a TaskWithLogs object
    task_with_logs = TaskWithLogs.from_orm(task)
    task_with_logs.logs = logs
    
    return task_with_logs


@router.get("/{task_id}/subtasks", response_model=TaskListResponse)
async def get_subtasks(
    task_id: UUID = Path(...),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    include_inactive: bool = Query(False),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Get subtasks for a task.
    
    Args:
        task_id: The ID of the parent task.
        limit: Maximum number of subtasks to return.
        offset: Number of subtasks to skip.
        include_inactive: Whether to include inactive subtasks.
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        A list of subtasks and the total count.
        
    Raises:
        HTTPException: If the parent task is not found or the user is not authorized.
    """
    task_service = TaskService(db)
    
    # First check if the parent task exists and belongs to the user
    parent_task = await task_service.get_task_by_id(task_id)
    
    if not parent_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent task not found"
        )
    
    # Ensure the user can only access their own tasks
    if str(parent_task.user_id) != str(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own tasks"
        )
    
    # Get the subtasks
    subtasks, total = await task_service.get_tasks_by_user_id(
        user_id=str(current_user.user_id),
        limit=limit,
        offset=offset,
        include_inactive=include_inactive,
        parent_id=task_id
    )
    
    return {"items": subtasks, "total": total}


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID = Path(...),
    task_update: TaskUpdate = Body(...),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Update a task.
    
    Args:
        task_id: The ID of the task to update.
        task_update: The updated task data.
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        The updated task if found.
        
    Raises:
        HTTPException: If the task is not found or the user is not authorized.
    """
    task_service = TaskService(db)
    
    # First check if the task exists and belongs to the user
    task = await task_service.get_task_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Ensure the user can only update their own tasks
    if str(task.user_id) != str(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own tasks"
        )
    
    # Update the task
    update_data = task_update.dict(exclude_unset=True)
    updated_task = await task_service.update_task(task_id, update_data)
    
    await db.commit()
    
    return {"task": updated_task}


@router.patch("/{task_id}/complete", response_model=TaskCompleteResponse)
async def complete_task(
    task_id: UUID = Path(...),
    completion_data: TaskCompleteRequest = Body(TaskCompleteRequest()),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Complete a task and trigger game mechanics.
    
    This endpoint marks a task as complete, calculates experience points,
    checks for achievements, and optionally creates a memory from the task.
    
    Args:
        task_id: The ID of the task to complete.
        completion_data: Optional evidence and reflection.
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        Completed task with XP gained and achievements unlocked.
        
    Raises:
        HTTPException: If the task is not found or user is not authorized.
    """
    task_service = TaskService(db)
    
    # Get the task
    task = await task_service.get_task_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Ensure user owns the task
    if str(task.user_id) != str(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only complete your own tasks"
        )
    
    # Check if already completed
    if task.status == TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is already completed"
        )
    
    # Mark task as complete using the model's helper method
    task.mark_complete()
    
    # Update actual duration if provided
    if completion_data.actual_duration_minutes:
        task.actual_duration_minutes = completion_data.actual_duration_minutes
    
    # Calculate experience points
    experience_gained = task.calculate_experience()
    
    # Auto-classify quest type if not set
    if not task.quest_type:
        task.classify_quest_type()
    
    # Create a task log for completion
    await task_service.create_task_log(
        task_id=task_id,
        message=f"Task completed. Evidence: {completion_data.evidence or 'None'}",
        log_type="completion",
        metadata={
            "experience_gained": experience_gained,
            "reflection": completion_data.reflection
        }
    )
    
    # TODO: Check for achievements (will implement with achievement service)
    achievements_unlocked = []
    
    # TODO: Update reputation (will implement with reputation service)
    reputation_changes = {}
    if task.value_impact:
        reputation_changes = task.value_impact
    
    # TODO: Create memory from completed task if reflection provided
    memory_created = None
    
    await db.commit()
    await db.refresh(task)
    
    return TaskCompleteResponse(
        task=task_to_dict(task),
        experience_gained=experience_gained,
        achievements_unlocked=achievements_unlocked,
        reputation_changes=reputation_changes,
        memory_created=memory_created
    )


@router.patch("/{task_id}/start", response_model=TaskResponse)
async def start_task(
    task_id: UUID = Path(...),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Mark a task as in progress.
    
    Args:
        task_id: The ID of the task to start.
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        The updated task.
        
    Raises:
        HTTPException: If the task is not found or user is not authorized.
    """
    task_service = TaskService(db)
    
    # Get the task
    task = await task_service.get_task_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Ensure user owns the task
    if str(task.user_id) != str(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only start your own tasks"
        )
    
    # Mark as in progress
    task.mark_in_progress()
    
    # Create a task log
    await task_service.create_task_log(
        task_id=task_id,
        message="Task started",
        log_type="status_change",
        metadata={"new_status": TaskStatus.IN_PROGRESS.value}
    )
    
    await db.commit()
    await db.refresh(task)
    
    return {"task": task_to_dict(task)}


@router.get("/stats", response_model=TaskStats)
async def get_task_stats(
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Get statistics about the user's tasks.
    
    Args:
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        Task statistics including XP, streaks, and performance metrics.
    """
    task_service = TaskService(db)
    
    # Get all user's tasks
    tasks, total = await task_service.get_tasks_by_user_id(
        user_id=str(current_user.user_id),
        limit=10000,  # Get all tasks for stats
        include_inactive=True
    )
    
    # Calculate statistics
    stats = TaskStats()
    stats.total_tasks = total
    
    completed_tasks = []
    total_estimated = 0
    total_actual = 0
    on_time_count = 0
    total_difficulty = 0
    
    for task in tasks:
        if task.status == TaskStatus.COMPLETED:
            stats.completed_tasks += 1
            completed_tasks.append(task)
            stats.total_experience += task.experience_points
            
            if task.actual_duration_minutes:
                total_actual += task.actual_duration_minutes
            
            if task.due_date and task.completed_at:
                if task.completed_at <= task.due_date:
                    on_time_count += 1
                    
        elif task.status == TaskStatus.IN_PROGRESS:
            stats.in_progress_tasks += 1
        elif task.status == TaskStatus.PENDING and task.due_date:
            if task.due_date < datetime.now():
                stats.overdue_tasks += 1
        
        if task.estimated_duration_minutes:
            total_estimated += task.estimated_duration_minutes
        
        total_difficulty += task.difficulty
        
        # Count by quest type
        if task.quest_type:
            quest_type_str = task.quest_type.value
            if quest_type_str not in stats.tasks_by_quest_type:
                stats.tasks_by_quest_type[quest_type_str] = 0
            stats.tasks_by_quest_type[quest_type_str] += 1
    
    # Calculate averages
    if stats.completed_tasks > 0:
        stats.on_time_completion_rate = on_time_count / stats.completed_tasks
        if total_actual > 0:
            stats.average_completion_time = total_actual / stats.completed_tasks
    
    if total > 0:
        stats.average_difficulty = total_difficulty / total
    
    stats.total_time_estimated = total_estimated
    stats.total_time_actual = total_actual
    
    # TODO: Calculate current streak (consecutive days with completed tasks)
    stats.current_streak = 0
    
    return stats


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID = Path(...),
    hard_delete: bool = Query(False),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> None:
    """
    Delete a task.
    
    Args:
        task_id: The ID of the task to delete.
        hard_delete: Whether to perform a hard delete (remove from database).
        current_user: The current authenticated user.
        db: The database session.
        
    Raises:
        HTTPException: If the task is not found, the user is not authorized,
            or the deletion fails.
    """
    task_service = TaskService(db)
    
    # First check if the task exists and belongs to the user
    task = await task_service.get_task_by_id(task_id, include_inactive=True)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Ensure the user can only delete their own tasks
    if str(task.user_id) != str(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own tasks"
        )
    
    # Delete the task
    result = await task_service.delete_task(task_id, hard_delete)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task"
        )
    
    await db.commit()


@router.post("/{task_id}/logs", response_model=TaskLogInDB, status_code=status.HTTP_201_CREATED)
async def create_task_log(
    task_id: UUID = Path(...),
    log_data: TaskLogCreate = Body(...),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Create a new log entry for a task.
    
    Args:
        task_id: The ID of the task.
        log_data: The log data.
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        The created log entry.
        
    Raises:
        HTTPException: If the task is not found, the user is not authorized,
            or the task ID in the path doesn't match the task ID in the log data.
    """
    # Ensure the task ID in the path matches the task ID in the log data
    if task_id != log_data.task_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task ID in path must match task ID in log data"
        )
    
    task_service = TaskService(db)
    
    # First check if the task exists and belongs to the user
    task = await task_service.get_task_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Ensure the user can only create logs for their own tasks
    if str(task.user_id) != str(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create logs for your own tasks"
        )
    
    # Create the log entry
    log = await task_service.create_task_log(
        task_id=task_id,
        message=log_data.message,
        log_type=log_data.log_type,
        metadata=log_data.metadata
    )
    
    await db.commit()
    
    return log


@router.get("/{task_id}/logs", response_model=List[TaskLogInDB])
async def get_task_logs(
    task_id: UUID = Path(...),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Get logs for a task.
    
    Args:
        task_id: The ID of the task.
        limit: Maximum number of logs to return.
        offset: Number of logs to skip.
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        A list of log entries.
        
    Raises:
        HTTPException: If the task is not found or the user is not authorized.
    """
    task_service = TaskService(db)
    
    # First check if the task exists and belongs to the user
    task = await task_service.get_task_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Ensure the user can only access logs for their own tasks
    if str(task.user_id) != str(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access logs for your own tasks"
        )
    
    # Get the logs
    logs, _ = await task_service.get_task_logs(task_id, limit, offset)
    
    return logs


@router.post("/{task_id}/subtasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_subtask(
    task_id: UUID = Path(...),
    task_data: TaskCreate = Body(...),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Create a subtask for a task.
    
    Args:
        task_id: The ID of the parent task.
        task_data: The subtask data.
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        The created subtask.
        
    Raises:
        HTTPException: If the parent task is not found or the user is not authorized.
    """
    task_service = TaskService(db)
    
    # First check if the parent task exists and belongs to the user
    parent_task = await task_service.get_task_by_id(task_id)
    
    if not parent_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent task not found"
        )
    
    # Ensure the user can only create subtasks for their own tasks
    if str(parent_task.user_id) != str(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create subtasks for your own tasks"
        )
    
    # Create the subtask
    subtask = await task_service.create_subtask(
        parent_id=task_id,
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        due_date=task_data.due_date,
        tags=task_data.tags,
        metadata=task_data.metadata,
        agent_id=task_data.agent_id
    )
    
    await db.commit()
    
    return {"task": subtask}


@router.post("/search", response_model=TaskListResponse)
async def search_tasks(
    search_params: TaskSearchParams = Body(...),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Search tasks by text content.
    
    Args:
        search_params: The search parameters.
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        A list of matching tasks.
        
    Raises:
        HTTPException: If the user is not authorized to search the specified user's tasks.
    """
    # Ensure the user can only search their own tasks
    if str(search_params.user_id) != str(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only search your own tasks"
        )
    
    task_service = TaskService(db)
    
    # Search tasks
    tasks = await task_service.search_tasks_by_text(
        user_id=str(current_user.user_id),
        search_term=search_params.search_term or "",
        limit=search_params.limit,
        include_inactive=search_params.include_inactive,
        status=search_params.status,
        priority=search_params.priority
    )
    
    return {"items": tasks, "total": len(tasks)}


@router.post("/extract/{conversation_id}", response_model=Dict[str, Any])
async def extract_tasks_from_conversation(
    conversation_id: UUID = Path(...),
    auto_create: bool = Query(True, description="Automatically create extracted tasks"),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Extract tasks from a conversation using AI.
    
    Args:
        conversation_id: The ID of the conversation to analyze.
        auto_create: Whether to automatically create the extracted tasks.
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        Extracted tasks and creation results.
        
    Raises:
        HTTPException: If the conversation is not found or the user is not authorized.
    """
    task_intelligence = TaskIntelligenceService(db)
    
    try:
        result = await task_intelligence.process_conversation_for_tasks(
            conversation_id=conversation_id,
            user_id=current_user.user_id,
            auto_create=auto_create
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract tasks: {str(e)}"
        )


@router.get("/reminders", response_model=List[Dict[str, Any]])
async def get_upcoming_reminders(
    hours_ahead: int = Query(24, ge=1, le=168, description="Hours to look ahead (max 1 week)"),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Get upcoming task reminders for the current user.
    
    Args:
        hours_ahead: Number of hours to look ahead for tasks.
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        List of tasks needing reminders with context.
    """
    task_intelligence = TaskIntelligenceService(db)
    
    reminders = await task_intelligence.get_upcoming_reminders(
        user_id=current_user.user_id,
        hours_ahead=hours_ahead
    )
    
    return reminders


@router.get("/daily-summary", response_model=Dict[str, Any])
async def get_daily_task_summary(
    include_memories: bool = Query(True, description="Include memory-based insights"),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Get a daily summary of tasks and insights.
    
    Args:
        include_memories: Whether to include memory-based insights.
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        Daily summary with tasks, statistics, and insights.
    """
    task_intelligence = TaskIntelligenceService(db)
    
    summary = await task_intelligence.generate_daily_summary(
        user_id=current_user.user_id,
        include_memories=include_memories
    )
    
    return summary


@router.get("/suggestions", response_model=List[Dict[str, Any]])
async def get_task_suggestions(
    include_context: bool = Query(True, description="Include current context in suggestions"),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Get intelligent task suggestions based on patterns and context.
    
    Args:
        include_context: Whether to use current time/date context.
        current_user: The current authenticated user.
        db: The database session.
        
    Returns:
        List of task suggestions with confidence scores.
    """
    suggestion_engine = TaskSuggestionEngine(db)
    
    # Build context if requested
    context = None
    if include_context:
        now = datetime.now()
        context = {
            "time_of_day": "morning" if now.hour < 12 else "afternoon" if now.hour < 18 else "evening",
            "day_of_week": now.strftime("%A"),
            "date": now.date().isoformat()
        }
    
    suggestions = await suggestion_engine.generate_suggestions(
        user_id=current_user.user_id,
        context=context
    )
    
    return suggestions
