"""
Task Extraction Service

This module provides intelligent task extraction from conversations,
including natural language date parsing and priority inference.
"""

import re
import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional, Tuple
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta
import spacy

logger = logging.getLogger(__name__)


class TaskExtractor:
    """
    Extracts tasks, deadlines, and priorities from natural language conversations.
    """
    
    def __init__(self):
        """Initialize the task extractor with NLP models."""
        self.spacy_model = None
        self._load_models()
        
        # Priority keywords
        self.high_priority_indicators = [
            "urgent", "asap", "immediately", "critical", "important",
            "must", "need to", "have to", "deadline", "by tomorrow",
            "by today", "by end of day", "eod", "cob", "emergency"
        ]
        
        self.medium_priority_indicators = [
            "should", "would like", "please", "when you can",
            "next week", "soon", "coming up"
        ]
        
        self.low_priority_indicators = [
            "might", "maybe", "eventually", "someday", "could",
            "when possible", "no rush", "whenever"
        ]
    
    def _load_models(self):
        """Load NLP models for entity extraction."""
        try:
            import spacy
            try:
                self.spacy_model = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found, using regex extraction only")
        except ImportError:
            logger.warning("spaCy not available, using regex extraction only")
    
    async def extract_tasks(self, conversation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract tasks from a conversation.
        
        Args:
            conversation_data: Conversation data with messages
            
        Returns:
            List of extracted tasks with metadata
        """
        messages = conversation_data.get("messages", [])
        tasks = []
        
        for idx, message in enumerate(messages):
            if message.get("role") == "user":
                content = message.get("content", "")
                
                # Extract tasks from this message
                message_tasks = self._extract_tasks_from_text(content)
                
                # Add context from surrounding messages
                for task in message_tasks:
                    task["message_index"] = idx
                    task["conversation_id"] = conversation_data.get("id")
                    
                    # Check if assistant confirmed the task
                    if idx + 1 < len(messages) and messages[idx + 1].get("role") == "assistant":
                        assistant_response = messages[idx + 1].get("content", "").lower()
                        if any(word in assistant_response for word in ["i'll remind", "noted", "scheduled", "will do"]):
                            task["confirmed"] = True
                    
                    tasks.append(task)
        
        return tasks
    
    def _extract_tasks_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract individual tasks from a text message."""
        tasks = []
        
        # Task patterns
        task_patterns = [
            # Direct commands
            (r"(?:please\s+)?(?:remind me to|remember to|don't forget to)\s+([^.!?]+)", "reminder"),
            (r"(?:i need to|i have to|i must|i should)\s+([^.!?]+)", "todo"),
            (r"(?:can you|could you|would you)\s+(?:please\s+)?(?:remind me to|help me)\s+([^.!?]+)", "reminder"),
            
            # Scheduled items
            (r"(?:i have|there's|there is)\s+(?:a|an)\s+([^.!?]+)\s+(?:at|on|tomorrow|today|next)", "scheduled"),
            (r"(?:meeting|appointment|call|interview)\s+(?:with|at)\s+([^.!?]+)", "meeting"),
            
            # Future intentions
            (r"(?:i will|i'll|i am going to|i'm going to|planning to|plan to)\s+([^.!?]+)", "planned"),
            (r"(?:need to|have to|must|should)\s+([^.!?]+)\s+(?:by|before|until)", "deadline"),
            
            # Task lists
            (r"(?:todo|to-do|task):\s*([^.!?]+)", "todo"),
            (r"[-•]\s+([^.!?\n]+)", "list_item"),  # Bullet points
        ]
        
        for pattern, task_type in task_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                task_text = match.group(1).strip()
                
                # Skip very short or invalid tasks
                if len(task_text) < 3 or task_text.lower() in ["it", "that", "this"]:
                    continue
                
                # Extract deadline from task text
                deadline_info = self._extract_deadline(task_text)
                
                # Infer priority
                priority = self._infer_priority(text, task_text, deadline_info["deadline"])
                
                task = {
                    "description": task_text,
                    "type": task_type,
                    "original_text": match.group(0),
                    "priority": priority,
                    "confidence": 0.8,
                    **deadline_info
                }
                
                tasks.append(task)
        
        # Deduplicate similar tasks
        return self._deduplicate_tasks(tasks)
    
    def _extract_deadline(self, text: str) -> Dict[str, Any]:
        """
        Extract deadline information from task text.
        
        Args:
            text: Task description text
            
        Returns:
            Dictionary with deadline and related metadata
        """
        deadline_info = {
            "deadline": None,
            "deadline_text": None,
            "is_recurring": False,
            "recurrence_pattern": None
        }
        
        # Time-based patterns
        time_patterns = [
            # Relative dates
            (r"(?:by|before|until)\s+(tomorrow|today|tonight)", "relative_day"),
            (r"(?:by|before|until)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)", "weekday"),
            (r"(?:by|before|until)\s+(next\s+\w+)", "next_period"),
            (r"(?:by|before|until)\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)", "time"),
            (r"(?:by|before|until)\s+(end of (?:day|week|month))", "period_end"),
            
            # Specific dates
            (r"(?:by|before|until|on)\s+(\d{1,2}/\d{1,2}(?:/\d{2,4})?)", "date"),
            (r"(?:by|before|until|on)\s+((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{1,2})", "month_day"),
            
            # Recurring patterns
            (r"(?:every|each)\s+(day|morning|evening|night|week|month)", "recurring"),
            (r"(?:daily|weekly|monthly|yearly)", "recurring_adverb"),
        ]
        
        for pattern, pattern_type in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                deadline_text = match.group(1)
                deadline_info["deadline_text"] = deadline_text
                
                # Parse the deadline
                if pattern_type == "relative_day":
                    deadline_info["deadline"] = self._parse_relative_day(deadline_text)
                elif pattern_type == "weekday":
                    deadline_info["deadline"] = self._parse_weekday(deadline_text)
                elif pattern_type in ["recurring", "recurring_adverb"]:
                    deadline_info["is_recurring"] = True
                    deadline_info["recurrence_pattern"] = deadline_text.lower()
                else:
                    # Try dateutil parser
                    try:
                        parsed_date = date_parser.parse(deadline_text, fuzzy=True)
                        deadline_info["deadline"] = parsed_date
                    except:
                        pass
                
                break
        
        return deadline_info
    
    def _parse_relative_day(self, day_text: str) -> Optional[datetime]:
        """Parse relative day references."""
        day_lower = day_text.lower()
        now = datetime.now()
        
        if day_lower == "today" or day_lower == "tonight":
            return now.replace(hour=23, minute=59, second=59)
        elif day_lower == "tomorrow":
            return (now + timedelta(days=1)).replace(hour=23, minute=59, second=59)
        
        return None
    
    def _parse_weekday(self, weekday_text: str) -> Optional[datetime]:
        """Parse weekday references."""
        weekdays = {
            "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6
        }
        
        target_weekday = weekdays.get(weekday_text.lower())
        if target_weekday is None:
            return None
        
        today = datetime.now()
        days_ahead = target_weekday - today.weekday()
        
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        
        return (today + timedelta(days=days_ahead)).replace(hour=23, minute=59, second=59)
    
    def _infer_priority(
        self,
        full_text: str,
        task_text: str,
        deadline: Optional[datetime]
    ) -> str:
        """
        Infer task priority from context and deadline.
        
        Args:
            full_text: Full message text
            task_text: Extracted task description
            deadline: Task deadline if any
            
        Returns:
            Priority level: "high", "medium", or "low"
        """
        combined_text = (full_text + " " + task_text).lower()
        
        # Check for explicit priority indicators
        high_score = sum(1 for indicator in self.high_priority_indicators if indicator in combined_text)
        medium_score = sum(1 for indicator in self.medium_priority_indicators if indicator in combined_text)
        low_score = sum(1 for indicator in self.low_priority_indicators if indicator in combined_text)
        
        # Deadline-based priority
        if deadline:
            days_until = (deadline - datetime.now()).days
            if days_until <= 1:
                high_score += 2
            elif days_until <= 3:
                medium_score += 1
        
        # Determine priority based on scores
        if high_score > medium_score and high_score > low_score:
            return "high"
        elif medium_score > low_score:
            return "medium"
        else:
            return "low"
    
    def _deduplicate_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate or very similar tasks."""
        if not tasks:
            return tasks
        
        unique_tasks = []
        seen_descriptions = set()
        
        for task in tasks:
            # Normalize description for comparison
            normalized = re.sub(r'\W+', ' ', task["description"].lower()).strip()
            
            # Check if we've seen a very similar task
            is_duplicate = False
            for seen in seen_descriptions:
                if self._are_similar_tasks(normalized, seen):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_tasks.append(task)
                seen_descriptions.add(normalized)
        
        return unique_tasks
    
    def _are_similar_tasks(self, task1: str, task2: str) -> bool:
        """Check if two tasks are similar enough to be considered duplicates."""
        # Simple word overlap check
        words1 = set(task1.split())
        words2 = set(task2.split())
        
        if not words1 or not words2:
            return False
        
        overlap = len(words1.intersection(words2))
        similarity = overlap / min(len(words1), len(words2))
        
        return similarity > 0.8