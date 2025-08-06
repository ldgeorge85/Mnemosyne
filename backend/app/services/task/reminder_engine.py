"""
Task Reminder Engine

This module provides task reminder functionality including
scheduled checks, notification preparation, and reminder templates.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from uuid import UUID
import asyncio
import json

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.task import Task
from app.db.models.user import User
from app.services.task.task_intelligence import TaskIntelligenceService
from app.services.llm.llm_service_enhanced import EnhancedLLMService, EnhancedLLMConfig

logger = logging.getLogger(__name__)


class ReminderEngine:
    """
    Engine for managing task reminders and notifications.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the reminder engine.
        
        Args:
            db: Database session
        """
        self.db = db
        self.task_intelligence = TaskIntelligenceService(db)
        self.llm_config = EnhancedLLMConfig(
            temperature=0.7,
            memory_enabled=True
        )
        
    async def check_and_send_reminders(self) -> Dict[str, Any]:
        """
        Check for tasks needing reminders and prepare notifications.
        
        This method should be called periodically (e.g., every hour)
        to check for upcoming tasks and generate reminders.
        
        Returns:
            Summary of reminders processed
        """
        # Get all active users
        result = await self.db.execute(
            select(User).where(User.is_active == True)
        )
        users = result.scalars().all()
        
        reminders_sent = 0
        users_notified = 0
        
        for user in users:
            # Get upcoming reminders for this user
            user_reminders = await self.task_intelligence.get_upcoming_reminders(
                user_id=user.id,
                hours_ahead=24
            )
            
            if user_reminders:
                # Generate personalized reminder message
                reminder_message = await self._generate_reminder_message(
                    user_id=user.id,
                    reminders=user_reminders
                )
                
                # Store reminder for delivery (webhook, email, etc.)
                await self._store_reminder_for_delivery(
                    user_id=user.id,
                    reminder_message=reminder_message,
                    task_reminders=user_reminders
                )
                
                reminders_sent += len(user_reminders)
                users_notified += 1
                
                logger.info(
                    f"Generated reminders for user",
                    extra={
                        "user_id": str(user.id),
                        "reminder_count": len(user_reminders)
                    }
                )
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "users_checked": len(users),
            "users_notified": users_notified,
            "reminders_sent": reminders_sent
        }
    
    async def _generate_reminder_message(
        self,
        user_id: UUID,
        reminders: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a personalized reminder message using LLM.
        
        Args:
            user_id: User ID for context
            reminders: List of task reminders
            
        Returns:
            Formatted reminder message
        """
        # Group reminders by urgency
        urgent = [r for r in reminders if r["reminder_type"] == "urgent"]
        soon = [r for r in reminders if r["reminder_type"] == "soon"]
        today = [r for r in reminders if r["reminder_type"] == "today"]
        upcoming = [r for r in reminders if r["reminder_type"] == "upcoming"]
        
        # Use LLM to generate friendly reminder
        llm_service = EnhancedLLMService(config=self.llm_config, db=self.db)
        
        reminder_data = {
            "urgent": [{"title": r["title"], "hours_until": r["hours_until_due"]} for r in urgent],
            "soon": [{"title": r["title"], "hours_until": r["hours_until_due"]} for r in soon],
            "today": [{"title": r["title"], "hours_until": r["hours_until_due"]} for r in today],
            "upcoming": [{"title": r["title"], "hours_until": r["hours_until_due"]} for r in upcoming]
        }
        
        prompt = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that creates friendly, encouraging task reminders. "
                    "Create a concise reminder message that groups tasks by urgency. "
                    "Be supportive and motivating, not stressful. "
                    "Format the message for easy reading with clear sections."
                )
            },
            {
                "role": "user",
                "content": f"Create a task reminder message for these tasks:\n{json.dumps(reminder_data, indent=2)}"
            }
        ]
        
        message = await llm_service.chat_completion(
            messages=prompt,
            user_id=user_id,
            max_tokens=500
        )
        
        return message
    
    async def _store_reminder_for_delivery(
        self,
        user_id: UUID,
        reminder_message: str,
        task_reminders: List[Dict[str, Any]]
    ) -> None:
        """
        Store reminder for delivery via configured channels.
        
        In a full implementation, this would:
        - Queue email notifications
        - Send webhook events
        - Update user notification preferences
        
        Args:
            user_id: User to notify
            reminder_message: Formatted reminder message
            task_reminders: Raw task reminder data
        """
        # For now, just log the reminder
        logger.info(
            f"Reminder ready for delivery",
            extra={
                "user_id": str(user_id),
                "task_count": len(task_reminders),
                "message_preview": reminder_message[:100] + "..."
            }
        )
        
        # In production, you would:
        # 1. Check user notification preferences
        # 2. Queue appropriate notifications (email, webhook, etc.)
        # 3. Track delivery status
    
    async def get_reminder_preferences(self, user_id: UUID) -> Dict[str, Any]:
        """
        Get user's reminder preferences.
        
        Args:
            user_id: User ID
            
        Returns:
            Reminder preferences
        """
        # Get user
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Extract preferences from user metadata or defaults
        preferences = user.metadata.get("reminder_preferences", {}) if user.metadata else {}
        
        return {
            "enabled": preferences.get("enabled", True),
            "channels": preferences.get("channels", ["in_app"]),
            "advance_notice": {
                "urgent": preferences.get("urgent_hours", 1),
                "high_priority": preferences.get("high_hours", 4),
                "normal": preferences.get("normal_hours", 24)
            },
            "quiet_hours": {
                "enabled": preferences.get("quiet_hours_enabled", False),
                "start": preferences.get("quiet_start", "22:00"),
                "end": preferences.get("quiet_end", "08:00")
            },
            "frequency": preferences.get("frequency", "smart")  # smart, hourly, daily
        }
    
    async def update_reminder_preferences(
        self,
        user_id: UUID,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update user's reminder preferences.
        
        Args:
            user_id: User ID
            preferences: New preferences
            
        Returns:
            Updated preferences
        """
        # Get user
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Update metadata
        if not user.metadata:
            user.metadata = {}
        
        user.metadata["reminder_preferences"] = preferences
        await self.db.commit()
        
        return preferences
    
    async def generate_smart_reminder_schedule(
        self,
        user_id: UUID,
        task_id: UUID
    ) -> List[datetime]:
        """
        Generate an intelligent reminder schedule for a task.
        
        This uses the task priority, deadline, and user patterns
        to create an optimal reminder schedule.
        
        Args:
            user_id: User ID
            task_id: Task ID
            
        Returns:
            List of reminder timestamps
        """
        # Get task
        result = await self.db.execute(
            select(Task)
            .where(Task.id == task_id)
            .where(Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()
        
        if not task or not task.due_date:
            return []
        
        reminders = []
        now = datetime.utcnow()
        
        # Calculate time until due
        time_until_due = task.due_date - now
        hours_until_due = time_until_due.total_seconds() / 3600
        
        # Generate reminders based on priority and time
        if task.priority == "high":
            # High priority: more frequent reminders
            if hours_until_due > 48:
                reminders.append(task.due_date - timedelta(days=2))
            if hours_until_due > 24:
                reminders.append(task.due_date - timedelta(days=1))
            if hours_until_due > 4:
                reminders.append(task.due_date - timedelta(hours=4))
            if hours_until_due > 1:
                reminders.append(task.due_date - timedelta(hours=1))
        elif task.priority == "medium":
            # Medium priority: balanced reminders
            if hours_until_due > 24:
                reminders.append(task.due_date - timedelta(days=1))
            if hours_until_due > 4:
                reminders.append(task.due_date - timedelta(hours=4))
        else:
            # Low priority: minimal reminders
            if hours_until_due > 24:
                reminders.append(task.due_date - timedelta(days=1))
        
        # Filter out past reminders
        reminders = [r for r in reminders if r > now]
        
        return sorted(reminders)