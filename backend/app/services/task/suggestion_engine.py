"""
Task Suggestion Engine

This module provides intelligent task suggestions based on user patterns,
memories, and current context.
"""

import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional
from uuid import UUID
import calendar

from sqlalchemy import select, and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.task import Task, TaskStatus
from app.db.models.memory import Memory
from app.db.models.conversation import Conversation, Message
from app.services.memory.memory_service_enhanced import MemoryService
from app.services.llm.llm_service_enhanced import EnhancedLLMService, EnhancedLLMConfig

logger = logging.getLogger(__name__)


class TaskSuggestionEngine:
    """
    Engine for generating intelligent task suggestions.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the suggestion engine.
        
        Args:
            db: Database session
        """
        self.db = db
        self.memory_service = MemoryService(db)
        self.llm_config = EnhancedLLMConfig(
            temperature=0.8,  # Higher for more creative suggestions
            memory_enabled=True
        )
    
    async def generate_suggestions(
        self,
        user_id: UUID,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate task suggestions for a user.
        
        Args:
            user_id: User ID
            context: Optional context (current time, location, etc.)
            
        Returns:
            List of task suggestions
        """
        suggestions = []
        
        # Analyze patterns
        patterns = await self._analyze_user_patterns(user_id)
        
        # Get relevant memories
        memories = await self._get_contextual_memories(user_id, context)
        
        # Generate different types of suggestions
        suggestions.extend(await self._suggest_recurring_tasks(user_id, patterns))
        suggestions.extend(await self._suggest_follow_up_tasks(user_id))
        suggestions.extend(await self._suggest_from_memories(user_id, memories))
        suggestions.extend(await self._suggest_time_based_tasks(user_id, context))
        
        # Use LLM to refine and rank suggestions
        refined_suggestions = await self._refine_suggestions_with_llm(
            user_id, suggestions, patterns, context
        )
        
        return refined_suggestions
    
    async def _analyze_user_patterns(self, user_id: UUID) -> Dict[str, Any]:
        """
        Analyze user's task patterns.
        
        Args:
            user_id: User ID
            
        Returns:
            Pattern analysis results
        """
        # Get completed tasks from last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        result = await self.db.execute(
            select(Task)
            .where(
                and_(
                    Task.user_id == user_id,
                    Task.status == TaskStatus.COMPLETED,
                    Task.updated_at >= thirty_days_ago
                )
            )
        )
        completed_tasks = result.scalars().all()
        
        # Analyze patterns
        patterns = {
            "common_times": {},
            "common_days": {},
            "recurring_themes": {},
            "average_completion_time": None,
            "preferred_priority": None
        }
        
        if completed_tasks:
            # Time of day analysis
            hour_counts = {}
            for task in completed_tasks:
                if task.due_date:
                    hour = task.due_date.hour
                    hour_counts[hour] = hour_counts.get(hour, 0) + 1
            
            # Day of week analysis
            day_counts = {}
            for task in completed_tasks:
                if task.due_date:
                    day = task.due_date.weekday()
                    day_counts[day] = day_counts.get(day, 0) + 1
            
            # Theme analysis (simplified)
            theme_keywords = {
                "meeting": ["meeting", "call", "conference", "sync"],
                "review": ["review", "check", "analyze", "assess"],
                "planning": ["plan", "schedule", "organize", "prepare"],
                "communication": ["email", "message", "respond", "contact"]
            }
            
            for task in completed_tasks:
                task_text = (task.title + " " + (task.description or "")).lower()
                for theme, keywords in theme_keywords.items():
                    if any(keyword in task_text for keyword in keywords):
                        patterns["recurring_themes"][theme] = patterns["recurring_themes"].get(theme, 0) + 1
            
            patterns["common_times"] = hour_counts
            patterns["common_days"] = day_counts
        
        return patterns
    
    async def _suggest_recurring_tasks(
        self,
        user_id: UUID,
        patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Suggest tasks based on recurring patterns.
        
        Args:
            user_id: User ID
            patterns: User patterns
            
        Returns:
            List of recurring task suggestions
        """
        suggestions = []
        
        # Look for tasks that appear to be recurring
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        result = await self.db.execute(
            select(Task)
            .where(
                and_(
                    Task.user_id == user_id,
                    Task.status == TaskStatus.COMPLETED,
                    Task.updated_at >= seven_days_ago
                )
            )
        )
        recent_completed = result.scalars().all()
        
        # Group by similar titles
        task_groups = {}
        for task in recent_completed:
            # Normalize title for grouping
            normalized = task.title.lower().strip()
            # Remove common date references
            for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                normalized = normalized.replace(day, "")
            normalized = normalized.strip()
            
            if normalized not in task_groups:
                task_groups[normalized] = []
            task_groups[normalized].append(task)
        
        # Suggest recurring tasks
        for normalized_title, tasks in task_groups.items():
            if len(tasks) >= 2:  # Task appeared at least twice
                # Calculate next occurrence
                last_task = max(tasks, key=lambda t: t.due_date or t.created_at)
                
                # Simple heuristic: same time next week
                if last_task.due_date:
                    next_due = last_task.due_date + timedelta(days=7)
                    
                    suggestions.append({
                        "type": "recurring",
                        "title": last_task.title,
                        "description": f"This task appears to be recurring weekly",
                        "suggested_due_date": next_due,
                        "priority": last_task.priority,
                        "confidence": 0.8,
                        "reason": f"You've completed similar tasks {len(tasks)} times recently"
                    })
        
        return suggestions
    
    async def _suggest_follow_up_tasks(self, user_id: UUID) -> List[Dict[str, Any]]:
        """
        Suggest follow-up tasks based on recently completed tasks.
        
        Args:
            user_id: User ID
            
        Returns:
            List of follow-up task suggestions
        """
        suggestions = []
        
        # Get recently completed tasks
        three_days_ago = datetime.utcnow() - timedelta(days=3)
        
        result = await self.db.execute(
            select(Task)
            .where(
                and_(
                    Task.user_id == user_id,
                    Task.status == TaskStatus.COMPLETED,
                    Task.updated_at >= three_days_ago
                )
            )
        )
        recent_completed = result.scalars().all()
        
        # Suggest follow-ups for certain types of tasks
        follow_up_patterns = {
            "meeting": ["Send meeting notes", "Follow up on action items"],
            "proposal": ["Check proposal status", "Follow up with client"],
            "review": ["Implement feedback", "Schedule next review"],
            "plan": ["Execute first step", "Review progress"]
        }
        
        for task in recent_completed:
            task_lower = task.title.lower()
            
            for pattern, follow_ups in follow_up_patterns.items():
                if pattern in task_lower:
                    for follow_up in follow_ups:
                        suggestions.append({
                            "type": "follow_up",
                            "title": f"{follow_up} - {task.title}",
                            "description": f"Follow-up task for: {task.title}",
                            "suggested_due_date": datetime.utcnow() + timedelta(days=2),
                            "priority": "medium",
                            "confidence": 0.6,
                            "reason": f"Common follow-up for {pattern} tasks",
                            "parent_task_id": str(task.id)
                        })
        
        return suggestions
    
    async def _suggest_from_memories(
        self,
        user_id: UUID,
        memories: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Suggest tasks based on user memories.
        
        Args:
            user_id: User ID
            memories: Relevant memories
            
        Returns:
            List of memory-based suggestions
        """
        suggestions = []
        
        # Look for action-oriented memories
        action_keywords = ["plan to", "need to", "want to", "should", "will", "going to"]
        
        for memory in memories[:10]:  # Limit to top 10 memories
            content = memory.get("content", "").lower()
            
            # Check if memory contains action items
            if any(keyword in content for keyword in action_keywords):
                # Extract potential task
                suggestions.append({
                    "type": "memory_based",
                    "title": f"From memory: {memory.get('title', content[:50])}",
                    "description": content,
                    "suggested_due_date": datetime.utcnow() + timedelta(days=7),
                    "priority": "medium",
                    "confidence": 0.5,
                    "reason": "Extracted from your memories",
                    "memory_id": memory.get("id")
                })
        
        return suggestions
    
    async def _suggest_time_based_tasks(
        self,
        user_id: UUID,
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Suggest tasks based on time and context.
        
        Args:
            user_id: User ID
            context: Current context
            
        Returns:
            List of time-based suggestions
        """
        suggestions = []
        now = datetime.utcnow()
        
        # Day-specific suggestions
        if now.weekday() == 0:  # Monday
            suggestions.append({
                "type": "time_based",
                "title": "Weekly planning session",
                "description": "Review last week and plan this week's priorities",
                "suggested_due_date": now.replace(hour=9, minute=0),
                "priority": "high",
                "confidence": 0.7,
                "reason": "Start of the week planning"
            })
        
        # End of month suggestions
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        if now.day >= days_in_month - 3:
            suggestions.append({
                "type": "time_based",
                "title": "Monthly review and planning",
                "description": "Review this month's progress and plan for next month",
                "suggested_due_date": now.replace(day=days_in_month, hour=16, minute=0),
                "priority": "medium",
                "confidence": 0.6,
                "reason": "End of month approaching"
            })
        
        # Time of day suggestions
        if 8 <= now.hour <= 10:
            suggestions.append({
                "type": "time_based",
                "title": "Daily priorities review",
                "description": "Review today's tasks and set priorities",
                "suggested_due_date": now + timedelta(minutes=30),
                "priority": "medium",
                "confidence": 0.5,
                "reason": "Morning planning time"
            })
        
        return suggestions
    
    async def _refine_suggestions_with_llm(
        self,
        user_id: UUID,
        suggestions: List[Dict[str, Any]],
        patterns: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Use LLM to refine and rank suggestions.
        
        Args:
            user_id: User ID
            suggestions: Raw suggestions
            patterns: User patterns
            context: Current context
            
        Returns:
            Refined and ranked suggestions
        """
        if not suggestions:
            return []
        
        llm_service = EnhancedLLMService(config=self.llm_config, db=self.db)
        
        # Prepare context for LLM
        suggestion_summary = [
            {
                "title": s["title"],
                "type": s["type"],
                "reason": s["reason"],
                "confidence": s["confidence"]
            }
            for s in suggestions
        ]
        
        prompt = [
            {
                "role": "system",
                "content": (
                    "You are a helpful task management assistant. Review the suggested tasks "
                    "and rank them by relevance and usefulness. Consider the user's patterns "
                    "and current context. Return the top 5 suggestions with any improvements "
                    "to titles or descriptions. Format as a numbered list."
                )
            },
            {
                "role": "user",
                "content": (
                    f"User patterns: {patterns}\n"
                    f"Current context: {context or 'Normal working day'}\n"
                    f"Suggested tasks:\n{suggestion_summary}\n\n"
                    "Please rank and refine the top 5 most relevant suggestions."
                )
            }
        ]
        
        response = await llm_service.chat_completion(
            messages=prompt,
            user_id=user_id,
            max_tokens=500
        )
        
        # For now, return top 5 suggestions sorted by confidence
        # In production, parse LLM response for refined suggestions
        sorted_suggestions = sorted(
            suggestions,
            key=lambda s: s["confidence"],
            reverse=True
        )[:5]
        
        return sorted_suggestions
    
    async def _get_contextual_memories(
        self,
        user_id: UUID,
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Get memories relevant to current context.
        
        Args:
            user_id: User ID
            context: Current context
            
        Returns:
            List of relevant memories
        """
        # Build search query based on context
        search_query = "tasks goals plans"
        
        if context:
            if "location" in context:
                search_query += f" {context['location']}"
            if "time_of_day" in context:
                search_query += f" {context['time_of_day']}"
        
        # Search memories
        memories = await self.memory_service.search_memories(
            user_id=user_id,
            query=search_query,
            limit=20,
            threshold=0.6
        )
        
        return memories