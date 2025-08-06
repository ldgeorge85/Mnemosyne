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

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_async_db
from app.db.models.task import TaskStatus, TaskPriority
from app.db.models.user import User
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
    TaskSearchParams
)
from app.services.task.task_service import TaskService
from app.services.task.task_intelligence import TaskIntelligenceService
from app.services.task.suggestion_engine import TaskSuggestionEngine


router = APIRouter()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
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
    # Ensure the user can only create tasks for themselves
    if str(task_data.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create tasks for yourself"
        )
    
    task_service = TaskService(db)
    task = await task_service.create_task(
        title=task_data.title,
        user_id=str(current_user.id),
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        due_date=task_data.due_date,
        tags=task_data.tags,
        metadata=task_data.metadata,
        parent_id=task_data.parent_id,
        agent_id=task_data.agent_id
    )
    
    await db.commit()
    
    return {"task": task}


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
    current_user: User = Depends(get_current_user),
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
        user_id=str(current_user.id),
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
    current_user: User = Depends(get_current_user),
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
    if str(task.user_id) != str(current_user.id):
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
    current_user: User = Depends(get_current_user),
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
    if str(task.user_id) != str(current_user.id):
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
    current_user: User = Depends(get_current_user),
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
    if str(parent_task.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own tasks"
        )
    
    # Get the subtasks
    subtasks, total = await task_service.get_tasks_by_user_id(
        user_id=str(current_user.id),
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
    current_user: User = Depends(get_current_user),
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
    if str(task.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own tasks"
        )
    
    # Update the task
    update_data = task_update.dict(exclude_unset=True)
    updated_task = await task_service.update_task(task_id, update_data)
    
    await db.commit()
    
    return {"task": updated_task}


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID = Path(...),
    hard_delete: bool = Query(False),
    current_user: User = Depends(get_current_user),
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
    if str(task.user_id) != str(current_user.id):
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
    current_user: User = Depends(get_current_user),
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
    if str(task.user_id) != str(current_user.id):
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
    current_user: User = Depends(get_current_user),
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
    if str(task.user_id) != str(current_user.id):
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
    current_user: User = Depends(get_current_user),
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
    if str(parent_task.user_id) != str(current_user.id):
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
    current_user: User = Depends(get_current_user),
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
    if str(search_params.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only search your own tasks"
        )
    
    task_service = TaskService(db)
    
    # Search tasks
    tasks = await task_service.search_tasks_by_text(
        user_id=str(current_user.id),
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
    current_user: User = Depends(get_current_user),
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
            user_id=current_user.id,
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
    current_user: User = Depends(get_current_user),
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
        user_id=current_user.id,
        hours_ahead=hours_ahead
    )
    
    return reminders


@router.get("/daily-summary", response_model=Dict[str, Any])
async def get_daily_task_summary(
    include_memories: bool = Query(True, description="Include memory-based insights"),
    current_user: User = Depends(get_current_user),
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
        user_id=current_user.id,
        include_memories=include_memories
    )
    
    return summary


@router.get("/suggestions", response_model=List[Dict[str, Any]])
async def get_task_suggestions(
    include_context: bool = Query(True, description="Include current context in suggestions"),
    current_user: User = Depends(get_current_user),
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
        user_id=current_user.id,
        context=context
    )
    
    return suggestions
