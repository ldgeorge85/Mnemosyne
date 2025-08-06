"""
Task service for the Mnemosyne application.

This module provides business logic for task management, including
creating, retrieving, updating, and deleting tasks, as well as
specialized operations for task management.
"""
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any, Union
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.task import TaskRepository
from app.db.models.task import Task, TaskLog, TaskStatus, TaskPriority


class TaskService:
    """
    Service for task-related business logic.
    
    This class provides methods for managing tasks, including creating,
    retrieving, updating, and deleting tasks, as well as specialized
    operations for task management.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the task service with a database session.
        
        Args:
            db: The SQLAlchemy async database session.
        """
        self.db = db
        self.repository = TaskRepository(db)
    
    async def create_task(
        self,
        title: str,
        user_id: Union[UUID, str],
        description: Optional[str] = None,
        status: TaskStatus = TaskStatus.PENDING,
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        parent_id: Optional[Union[UUID, str]] = None,
        agent_id: Optional[Union[UUID, str]] = None
    ) -> Task:
        """
        Create a new task.
        
        Args:
            title: The title of the task.
            user_id: The ID of the user who owns the task.
            description: The description of the task.
            status: The status of the task.
            priority: The priority of the task.
            due_date: The due date of the task.
            tags: The tags associated with the task.
            metadata: Additional metadata for the task.
            parent_id: The ID of the parent task (for subtasks).
            agent_id: The ID of the agent assigned to the task.
            
        Returns:
            The created task.
        """
        task_data = {
            "title": title,
            "user_id": user_id,
            "description": description,
            "status": status,
            "priority": priority,
            "due_date": due_date,
            "tags": tags or [],
            "metadata": metadata or {},
            "parent_id": parent_id,
            "agent_id": agent_id
        }
        
        task = await self.repository.create_task(task_data)
        
        # Create a log entry for task creation
        await self.create_task_log(
            task_id=task.id,
            message=f"Task '{title}' created",
            log_type="creation"
        )
        
        return task
    
    async def get_task_by_id(
        self, 
        task_id: Union[UUID, str], 
        include_inactive: bool = False
    ) -> Optional[Task]:
        """
        Get a task by its ID.
        
        Args:
            task_id: The ID of the task to retrieve.
            include_inactive: Whether to include inactive tasks.
            
        Returns:
            The task if found, None otherwise.
        """
        return await self.repository.get_task_by_id(task_id, include_inactive)
    
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
        return await self.repository.get_tasks_by_user_id(
            user_id=user_id,
            limit=limit,
            offset=offset,
            include_inactive=include_inactive,
            status=status,
            priority=priority,
            tags=tags,
            due_date_start=due_date_start,
            due_date_end=due_date_end,
            parent_id=parent_id
        )
    
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
        return await self.repository.search_tasks_by_text(
            user_id=user_id,
            search_term=search_term,
            limit=limit,
            include_inactive=include_inactive,
            status=status,
            priority=priority
        )
    
    async def update_task(
        self, 
        task_id: Union[UUID, str], 
        update_data: Dict[str, Any]
    ) -> Optional[Task]:
        """
        Update a task.
        
        Args:
            task_id: The ID of the task to update.
            update_data: Dictionary containing updated task data.
            
        Returns:
            The updated task if found, None otherwise.
        """
        # Get the original task for comparison
        original_task = await self.repository.get_task_by_id(task_id, include_inactive=True)
        if not original_task:
            return None
            
        # Update the task
        updated_task = await self.repository.update_task(task_id, update_data)
        
        # Create a log entry for the update
        log_message = "Task updated"
        log_metadata = {}
        
        # Add specific details to the log message based on what was updated
        if "status" in update_data and update_data["status"] != original_task.status:
            log_message = f"Status changed from {original_task.status} to {update_data['status']}"
            
            # If the task is being completed, set the completed_at timestamp
            if update_data["status"] == TaskStatus.COMPLETED and not original_task.completed_at:
                update_data["completed_at"] = datetime.utcnow()
                
        elif "priority" in update_data and update_data["priority"] != original_task.priority:
            log_message = f"Priority changed from {original_task.priority} to {update_data['priority']}"
            
        elif "title" in update_data and update_data["title"] != original_task.title:
            log_message = f"Title changed from '{original_task.title}' to '{update_data['title']}'"
            
        # Create the log entry
        await self.create_task_log(
            task_id=task_id,
            message=log_message,
            log_type="update",
            metadata=log_metadata
        )
        
        return updated_task
    
    async def delete_task(
        self, 
        task_id: Union[UUID, str], 
        hard_delete: bool = False
    ) -> bool:
        """
        Delete a task.
        
        Args:
            task_id: The ID of the task to delete.
            hard_delete: Whether to perform a hard delete (remove from database).
            
        Returns:
            True if the task was deleted, False otherwise.
        """
        # Get the task first to ensure it exists
        task = await self.repository.get_task_by_id(task_id, include_inactive=True)
        if not task:
            return False
            
        # Delete the task
        result = await self.repository.delete_task(task_id, hard_delete)
        
        if result and not hard_delete:
            # Create a log entry for soft deletion
            await self.create_task_log(
                task_id=task_id,
                message=f"Task '{task.title}' marked as inactive",
                log_type="deletion"
            )
            
        return result
    
    async def create_task_log(
        self,
        task_id: Union[UUID, str],
        message: str,
        log_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TaskLog:
        """
        Create a new task log.
        
        Args:
            task_id: The ID of the task.
            message: The log message.
            log_type: The type of log entry.
            metadata: Additional metadata for the log entry.
            
        Returns:
            The created task log.
        """
        log_data = {
            "task_id": task_id,
            "message": message,
            "log_type": log_type,
            "metadata": metadata or {}
        }
        
        return await self.repository.create_task_log(log_data)
    
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
        return await self.repository.get_task_logs(task_id, limit, offset)
    
    async def assign_task_to_agent(
        self,
        task_id: Union[UUID, str],
        agent_id: Union[UUID, str]
    ) -> Optional[Task]:
        """
        Assign a task to an agent.
        
        Args:
            task_id: The ID of the task to assign.
            agent_id: The ID of the agent to assign the task to.
            
        Returns:
            The updated task if found, None otherwise.
        """
        # Get the task first to ensure it exists
        task = await self.repository.get_task_by_id(task_id, include_inactive=True)
        if not task:
            return None
            
        # Update the task with the agent ID
        update_data = {"agent_id": agent_id}
        updated_task = await self.repository.update_task(task_id, update_data)
        
        # Create a log entry for the assignment
        await self.create_task_log(
            task_id=task_id,
            message=f"Task assigned to agent {agent_id}",
            log_type="assignment"
        )
        
        return updated_task
    
    async def create_subtask(
        self,
        parent_id: Union[UUID, str],
        title: str,
        description: Optional[str] = None,
        status: TaskStatus = TaskStatus.PENDING,
        priority: Optional[TaskPriority] = None,
        due_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        agent_id: Optional[Union[UUID, str]] = None
    ) -> Optional[Task]:
        """
        Create a subtask for an existing task.
        
        Args:
            parent_id: The ID of the parent task.
            title: The title of the subtask.
            description: The description of the subtask.
            status: The status of the subtask.
            priority: The priority of the subtask (defaults to parent's priority).
            due_date: The due date of the subtask.
            tags: The tags associated with the subtask.
            metadata: Additional metadata for the subtask.
            agent_id: The ID of the agent assigned to the subtask.
            
        Returns:
            The created subtask if the parent task exists, None otherwise.
        """
        # Get the parent task first to ensure it exists
        parent_task = await self.repository.get_task_by_id(parent_id, include_inactive=True)
        if not parent_task:
            return None
            
        # If priority is not specified, use the parent's priority
        if priority is None:
            priority = parent_task.priority
            
        # Create the subtask
        subtask = await self.create_task(
            title=title,
            user_id=parent_task.user_id,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
            tags=tags,
            metadata=metadata,
            parent_id=parent_id,
            agent_id=agent_id
        )
        
        # Create a log entry for the parent task
        await self.create_task_log(
            task_id=parent_id,
            message=f"Subtask '{title}' created",
            log_type="subtask_creation"
        )
        
        return subtask
