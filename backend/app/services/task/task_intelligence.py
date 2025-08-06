"""
Task Intelligence Service

This module provides intelligent task management by extracting tasks from
conversations, linking them to memories, and managing reminders.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.task import Task
from app.db.models.conversation import Conversation, Message
from app.db.models.memory import Memory
from app.services.task.task_extractor import TaskExtractor
from app.services.memory.memory_service_enhanced import MemoryService

logger = logging.getLogger(__name__)


class TaskIntelligenceService:
    """
    Intelligent task management service that extracts, creates, and manages tasks.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the task intelligence service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.task_extractor = TaskExtractor()
        self.memory_service = MemoryService(db)
    
    async def process_conversation_for_tasks(
        self,
        conversation_id: UUID,
        user_id: UUID,
        auto_create: bool = True
    ) -> Dict[str, Any]:
        """
        Process a conversation to extract and optionally create tasks.
        
        Args:
            conversation_id: ID of the conversation to process
            user_id: User ID for verification
            auto_create: Whether to automatically create tasks in the database
            
        Returns:
            Summary of extracted and created tasks
        """
        # Get conversation with messages
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .where(Conversation.user_id == user_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Get messages
        messages_result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        messages = messages_result.scalars().all()
        
        # Prepare conversation data
        conversation_data = {
            "id": str(conversation.id),
            "title": conversation.title,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        }
        
        # Extract tasks
        extracted_tasks = await self.task_extractor.extract_tasks(conversation_data)
        
        created_tasks = []
        if auto_create and extracted_tasks:
            # Create tasks in database
            for task_data in extracted_tasks:
                # Check if similar task already exists
                if not await self._task_already_exists(user_id, task_data["description"]):
                    task = await self._create_task_from_extraction(
                        task_data, conversation_id, user_id
                    )
                    created_tasks.append(task)
        
        # Commit all tasks
        if created_tasks:
            await self.db.commit()
        
        return {
            "conversation_id": str(conversation_id),
            "extracted_count": len(extracted_tasks),
            "created_count": len(created_tasks),
            "tasks": [
                {
                    "id": str(task.id) if hasattr(task, 'id') else None,
                    "title": task.title if hasattr(task, 'title') else task_data["description"],
                    "priority": task.priority if hasattr(task, 'priority') else task_data["priority"],
                    "due_date": task.due_date.isoformat() if hasattr(task, 'due_date') and task.due_date else None,
                    "extracted_data": task_data
                }
                for task, task_data in zip(
                    created_tasks + [None] * (len(extracted_tasks) - len(created_tasks)),
                    extracted_tasks
                )
                if task or task_data
            ]
        }
    
    async def _task_already_exists(self, user_id: UUID, description: str) -> bool:
        """Check if a similar task already exists for the user."""
        # Simple check - look for tasks with very similar titles
        result = await self.db.execute(
            select(Task)
            .where(Task.user_id == user_id)
            .where(Task.status.in_(["pending", "in_progress"]))
        )
        
        existing_tasks = result.scalars().all()
        
        # Normalize description
        normalized_new = description.lower().strip()
        
        for task in existing_tasks:
            normalized_existing = task.title.lower().strip()
            
            # Check for high similarity
            if self._calculate_similarity(normalized_new, normalized_existing) > 0.8:
                return True
        
        return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity."""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    async def _create_task_from_extraction(
        self,
        task_data: Dict[str, Any],
        conversation_id: UUID,
        user_id: UUID
    ) -> Task:
        """Create a task from extracted data."""
        # Create task
        task = Task(
            id=uuid4(),
            user_id=user_id,
            title=task_data["description"][:200],  # Limit title length
            description=f"Extracted from conversation: {task_data.get('original_text', task_data['description'])}",
            priority=task_data["priority"],
            status="pending",
            due_date=task_data.get("deadline"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={
                "source": "conversation",
                "conversation_id": str(conversation_id),
                "extraction_confidence": task_data.get("confidence", 0.8),
                "task_type": task_data.get("type", "todo"),
                "is_recurring": task_data.get("is_recurring", False),
                "recurrence_pattern": task_data.get("recurrence_pattern")
            }
        )
        
        self.db.add(task)
        
        # Link to relevant memories
        await self._link_task_to_memories(task, task_data["description"], user_id)
        
        return task
    
    async def _link_task_to_memories(
        self,
        task: Task,
        task_description: str,
        user_id: UUID
    ) -> None:
        """Link a task to relevant memories."""
        # Search for related memories
        related_memories = await self.memory_service.search_memories(
            user_id=user_id,
            query=task_description,
            limit=3,
            threshold=0.7
        )
        
        if related_memories:
            # Store memory links in task metadata
            if not task.metadata:
                task.metadata = {}
            
            task.metadata["linked_memories"] = [
                {
                    "memory_id": mem["id"],
                    "title": mem["title"],
                    "relevance": mem["similarity"]
                }
                for mem in related_memories
            ]
    
    async def get_upcoming_reminders(
        self,
        user_id: UUID,
        hours_ahead: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get tasks that need reminders in the next N hours.
        
        Args:
            user_id: User ID
            hours_ahead: How many hours ahead to look
            
        Returns:
            List of tasks needing reminders
        """
        cutoff_time = datetime.utcnow() + timedelta(hours=hours_ahead)
        
        result = await self.db.execute(
            select(Task)
            .where(
                and_(
                    Task.user_id == user_id,
                    Task.status == "pending",
                    Task.due_date != None,
                    Task.due_date <= cutoff_time,
                    Task.due_date > datetime.utcnow()
                )
            )
            .order_by(Task.due_date)
        )
        
        tasks = result.scalars().all()
        
        reminders = []
        for task in tasks:
            time_until = task.due_date - datetime.utcnow()
            hours_until = time_until.total_seconds() / 3600
            
            reminder = {
                "task_id": str(task.id),
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "due_date": task.due_date.isoformat(),
                "hours_until_due": round(hours_until, 1),
                "reminder_type": self._get_reminder_type(hours_until)
            }
            
            # Add linked memory context if available
            if task.metadata and "linked_memories" in task.metadata:
                reminder["context"] = task.metadata["linked_memories"]
            
            reminders.append(reminder)
        
        return reminders
    
    def _get_reminder_type(self, hours_until: float) -> str:
        """Determine the type of reminder based on time remaining."""
        if hours_until <= 1:
            return "urgent"
        elif hours_until <= 4:
            return "soon"
        elif hours_until <= 24:
            return "today"
        else:
            return "upcoming"
    
    async def generate_daily_summary(
        self,
        user_id: UUID,
        include_memories: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a daily summary of tasks and activities.
        
        Args:
            user_id: User ID
            include_memories: Whether to include relevant memories
            
        Returns:
            Daily summary with tasks, completions, and insights
        """
        today = datetime.utcnow().date()
        tomorrow = today + timedelta(days=1)
        
        # Get today's tasks
        today_tasks_result = await self.db.execute(
            select(Task)
            .where(
                and_(
                    Task.user_id == user_id,
                    Task.due_date >= datetime.combine(today, datetime.min.time()),
                    Task.due_date < datetime.combine(tomorrow, datetime.min.time())
                )
            )
            .order_by(Task.priority.desc(), Task.due_date)
        )
        today_tasks = today_tasks_result.scalars().all()
        
        # Get completed tasks from last 24 hours
        yesterday = today - timedelta(days=1)
        completed_result = await self.db.execute(
            select(Task)
            .where(
                and_(
                    Task.user_id == user_id,
                    Task.status == "completed",
                    Task.updated_at >= datetime.combine(yesterday, datetime.min.time())
                )
            )
        )
        completed_tasks = completed_result.scalars().all()
        
        # Get overdue tasks
        overdue_result = await self.db.execute(
            select(Task)
            .where(
                and_(
                    Task.user_id == user_id,
                    Task.status == "pending",
                    Task.due_date < datetime.utcnow()
                )
            )
        )
        overdue_tasks = overdue_result.scalars().all()
        
        summary = {
            "date": today.isoformat(),
            "tasks_today": len(today_tasks),
            "tasks_completed_24h": len(completed_tasks),
            "tasks_overdue": len(overdue_tasks),
            "today_breakdown": {
                "high_priority": sum(1 for t in today_tasks if t.priority == "high"),
                "medium_priority": sum(1 for t in today_tasks if t.priority == "medium"),
                "low_priority": sum(1 for t in today_tasks if t.priority == "low")
            },
            "tasks": {
                "today": [
                    {
                        "id": str(t.id),
                        "title": t.title,
                        "priority": t.priority,
                        "due_time": t.due_date.strftime("%H:%M") if t.due_date else None,
                        "status": t.status
                    }
                    for t in today_tasks
                ],
                "overdue": [
                    {
                        "id": str(t.id),
                        "title": t.title,
                        "priority": t.priority,
                        "days_overdue": (datetime.utcnow() - t.due_date).days
                    }
                    for t in overdue_tasks[:5]  # Limit to 5 most overdue
                ],
                "completed_recently": [
                    {
                        "id": str(t.id),
                        "title": t.title,
                        "completed_at": t.updated_at.isoformat()
                    }
                    for t in completed_tasks[:5]  # Limit to 5 most recent
                ]
            }
        }
        
        # Add insights
        if include_memories:
            insights = await self._generate_insights(user_id, today_tasks)
            summary["insights"] = insights
        
        return summary
    
    async def _generate_insights(
        self,
        user_id: UUID,
        today_tasks: List[Task]
    ) -> Dict[str, Any]:
        """Generate insights based on tasks and memories."""
        insights = {
            "patterns": [],
            "suggestions": []
        }
        
        # Analyze task patterns
        if today_tasks:
            task_types = {}
            for task in today_tasks:
                if task.metadata and "task_type" in task.metadata:
                    task_type = task.metadata["task_type"]
                    task_types[task_type] = task_types.get(task_type, 0) + 1
            
            if task_types:
                most_common = max(task_types.items(), key=lambda x: x[1])
                insights["patterns"].append(
                    f"Most tasks today are {most_common[0]} tasks ({most_common[1]} tasks)"
                )
        
        # Search for relevant memories
        if today_tasks:
            # Use first high-priority task for memory search
            high_priority = [t for t in today_tasks if t.priority == "high"]
            if high_priority:
                query_task = high_priority[0]
                memories = await self.memory_service.search_memories(
                    user_id=user_id,
                    query=query_task.title,
                    limit=2,
                    threshold=0.7
                )
                
                if memories:
                    insights["suggestions"].append(
                        f"Related to '{query_task.title}': {memories[0]['title']}"
                    )
        
        return insights