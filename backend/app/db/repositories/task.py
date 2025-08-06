"""
Task repository for the Mnemosyne application.

This module provides database operations for tasks, including CRUD operations
and specialized queries for task management.
"""
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any, Union
from uuid import UUID

from sqlalchemy import select, update, delete, func, and_, or_, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import true, false

from app.db.models.task import Task, TaskLog, TaskStatus, TaskPriority


class TaskRepository:
    """
    Repository for task-related database operations.
    
    This class provides methods for creating, retrieving, updating, and deleting
    tasks, as well as specialized queries for task management.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the task repository with a database session.
        
        Args:
            db: The SQLAlchemy async database session.
        """
        self.db = db
    
    async def create_task(self, task_data: Dict[str, Any]) -> Task:
        """
        Create a new task in the database.
        
        Args:
            task_data: Dictionary containing task data.
            
        Returns:
            The created task.
        """
        task = Task(**task_data)
        self.db.add(task)
        await self.db.flush()
        return task
    
    async def get_task_by_id(self, task_id: Union[UUID, str], include_inactive: bool = False) -> Optional[Task]:
        """
        Get a task by its ID.
        
        Args:
            task_id: The ID of the task to retrieve.
            include_inactive: Whether to include inactive tasks.
            
        Returns:
            The task if found, None otherwise.
        """
        query = select(Task).where(Task.id == task_id)
        
        if not include_inactive:
            query = query.where(Task.is_active == true())
            
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_tasks_by_user_id(
        self, 
        user_id: Union[UUID, str], 
        limit: int = 10, 
        offset: int = 0,
        include_inactive: bool = False,
        status: Optional[List[TaskStatus]] = None,
        priority: Optional[List[TaskPriority]] = None,
        tags: Optional[List[str]] = None,
        due_date_start: Optional[datetime] = None,
        due_date_end: Optional[datetime] = None,
        parent_id: Optional[Union[UUID, str]] = None
    ) -> Tuple[List[Task], int]:
        """
        Get tasks for a specific user with optional filtering.
        
        Args:
            user_id: The ID of the user.
            limit: Maximum number of tasks to return.
            offset: Number of tasks to skip.
            include_inactive: Whether to include inactive tasks.
            status: Filter by task status.
            priority: Filter by task priority.
            tags: Filter by task tags.
            due_date_start: Filter by due date (start).
            due_date_end: Filter by due date (end).
            parent_id: Filter by parent task ID (for subtasks).
            
        Returns:
            A tuple containing the list of tasks and the total count.
        """
        # Convert user_id to string for comparison if it's a UUID
        if isinstance(user_id, UUID):
            user_id = str(user_id)
            
        # Build the base query
        query = select(Task).where(cast(Task.user_id, String) == user_id)
        count_query = select(func.count()).select_from(Task).where(cast(Task.user_id, String) == user_id)
        
        # Apply filters
        if not include_inactive:
            query = query.where(Task.is_active == true())
            count_query = count_query.where(Task.is_active == true())
            
        if status:
            query = query.where(Task.status.in_(status))
            count_query = count_query.where(Task.status.in_(status))
            
        if priority:
            query = query.where(Task.priority.in_(priority))
            count_query = count_query.where(Task.priority.in_(priority))
            
        if tags:
            # For each tag in the list, check if it's in the task's tags array
            for tag in tags:
                query = query.where(Task.tags.contains([tag]))
                count_query = count_query.where(Task.tags.contains([tag]))
                
        if due_date_start:
            query = query.where(Task.due_date >= due_date_start)
            count_query = count_query.where(Task.due_date >= due_date_start)
            
        if due_date_end:
            query = query.where(Task.due_date <= due_date_end)
            count_query = count_query.where(Task.due_date <= due_date_end)
            
        if parent_id is not None:
            query = query.where(Task.parent_id == parent_id)
            count_query = count_query.where(Task.parent_id == parent_id)
        else:
            # If parent_id is None, only return top-level tasks
            query = query.where(Task.parent_id == None)
            count_query = count_query.where(Task.parent_id == None)
            
        # Get total count
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination
        query = query.order_by(Task.created_at.desc()).offset(offset).limit(limit)
        
        # Execute query
        result = await self.db.execute(query)
        tasks = result.scalars().all()
        
        return list(tasks), total
    
    async def search_tasks_by_text(
        self, 
        user_id: Union[UUID, str], 
        search_term: str,
        limit: int = 10,
        include_inactive: bool = False,
        status: Optional[List[TaskStatus]] = None,
        priority: Optional[List[TaskPriority]] = None
    ) -> List[Task]:
        """
        Search tasks by text content.
        
        Args:
            user_id: The ID of the user.
            search_term: Text to search for in task title and description.
            limit: Maximum number of tasks to return.
            include_inactive: Whether to include inactive tasks.
            status: Filter by task status.
            priority: Filter by task priority.
            
        Returns:
            A list of matching tasks.
        """
        # Convert user_id to string for comparison if it's a UUID
        if isinstance(user_id, UUID):
            user_id = str(user_id)
            
        # Build the search query
        query = select(Task).where(
            and_(
                cast(Task.user_id, String) == user_id,
                or_(
                    Task.title.ilike(f"%{search_term}%"),
                    Task.description.ilike(f"%{search_term}%")
                )
            )
        )
        
        # Apply filters
        if not include_inactive:
            query = query.where(Task.is_active == true())
            
        if status:
            query = query.where(Task.status.in_(status))
            
        if priority:
            query = query.where(Task.priority.in_(priority))
            
        # Apply limit and order
        query = query.order_by(Task.created_at.desc()).limit(limit)
        
        # Execute query
        result = await self.db.execute(query)
        tasks = result.scalars().all()
        
        return list(tasks)
    
    async def update_task(self, task_id: Union[UUID, str], task_data: Dict[str, Any]) -> Optional[Task]:
        """
        Update a task in the database.
        
        Args:
            task_id: The ID of the task to update.
            task_data: Dictionary containing updated task data.
            
        Returns:
            The updated task if found, None otherwise.
        """
        # Get the task
        task = await self.get_task_by_id(task_id, include_inactive=True)
        if not task:
            return None
            
        # Update the task attributes
        for key, value in task_data.items():
            if hasattr(task, key):
                setattr(task, key, value)
                
        # If status is being set to completed, set completed_at
        if task_data.get("status") == TaskStatus.COMPLETED and not task.completed_at:
            task.completed_at = datetime.utcnow()
                
        await self.db.flush()
        return task
    
    async def delete_task(self, task_id: Union[UUID, str], hard_delete: bool = False) -> bool:
        """
        Delete a task from the database.
        
        Args:
            task_id: The ID of the task to delete.
            hard_delete: Whether to perform a hard delete (remove from database).
            
        Returns:
            True if the task was deleted, False otherwise.
        """
        task = await self.get_task_by_id(task_id, include_inactive=True)
        if not task:
            return False
            
        if hard_delete:
            await self.db.execute(delete(Task).where(Task.id == task_id))
        else:
            task.is_active = False
            await self.db.flush()
            
        return True
    
    async def create_task_log(self, log_data: Dict[str, Any]) -> TaskLog:
        """
        Create a new task log in the database.
        
        Args:
            log_data: Dictionary containing log data.
            
        Returns:
            The created task log.
        """
        log = TaskLog(**log_data)
        self.db.add(log)
        await self.db.flush()
        return log
    
    async def get_task_logs(
        self, 
        task_id: Union[UUID, str], 
        limit: int = 50, 
        offset: int = 0
    ) -> Tuple[List[TaskLog], int]:
        """
        Get logs for a specific task.
        
        Args:
            task_id: The ID of the task.
            limit: Maximum number of logs to return.
            offset: Number of logs to skip.
            
        Returns:
            A tuple containing the list of logs and the total count.
        """
        # Build the query
        query = select(TaskLog).where(TaskLog.task_id == task_id)
        count_query = select(func.count()).select_from(TaskLog).where(TaskLog.task_id == task_id)
        
        # Get total count
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination
        query = query.order_by(TaskLog.created_at.desc()).offset(offset).limit(limit)
        
        # Execute query
        result = await self.db.execute(query)
        logs = result.scalars().all()
        
        return list(logs), total
