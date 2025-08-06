"""
Tests for Task Intelligence Service

This module tests the task extraction, reminder, and suggestion features.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import Mock, patch, AsyncMock

from app.services.task.task_intelligence import TaskIntelligenceService
from app.services.task.task_extractor import TaskExtractor
from app.services.task.reminder_engine import ReminderEngine
from app.services.task.suggestion_engine import TaskSuggestionEngine
from app.db.models.task import Task, TaskStatus, TaskPriority
from app.db.models.conversation import Conversation, Message


@pytest.mark.asyncio
class TestTaskExtractor:
    """Test task extraction from natural language."""
    
    async def test_extract_simple_reminder(self):
        """Test extracting a simple reminder."""
        extractor = TaskExtractor()
        
        conversation = {
            "id": str(uuid4()),
            "title": "Test conversation",
            "messages": [
                {
                    "role": "user",
                    "content": "Please remind me to call John tomorrow at 3pm",
                    "created_at": datetime.utcnow().isoformat()
                }
            ]
        }
        
        tasks = await extractor.extract_tasks(conversation)
        
        assert len(tasks) == 1
        task = tasks[0]
        assert "call John" in task["description"]
        assert task["type"] == "reminder"
        assert task["deadline"] is not None
        assert task["deadline_text"] == "tomorrow at 3pm"
    
    async def test_extract_multiple_tasks(self):
        """Test extracting multiple tasks from one message."""
        extractor = TaskExtractor()
        
        conversation = {
            "id": str(uuid4()),
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "I need to finish the report by Friday and "
                        "schedule a meeting with the team next week"
                    ),
                    "created_at": datetime.utcnow().isoformat()
                }
            ]
        }
        
        tasks = await extractor.extract_tasks(conversation)
        
        assert len(tasks) == 2
        assert any("report" in t["description"] for t in tasks)
        assert any("meeting" in t["description"] for t in tasks)
    
    async def test_priority_inference(self):
        """Test inferring priority from context."""
        extractor = TaskExtractor()
        
        # High priority
        high_priority_text = "This is urgent! I must submit the proposal by tomorrow"
        tasks = extractor._extract_tasks_from_text(high_priority_text)
        assert tasks[0]["priority"] == "high"
        
        # Low priority
        low_priority_text = "Maybe someday I should organize my bookshelf"
        tasks = extractor._extract_tasks_from_text(low_priority_text)
        assert tasks[0]["priority"] == "low"
    
    async def test_recurring_task_detection(self):
        """Test detecting recurring tasks."""
        extractor = TaskExtractor()
        
        conversation = {
            "id": str(uuid4()),
            "messages": [
                {
                    "role": "user",
                    "content": "Set up a weekly team meeting every Monday at 10am",
                    "created_at": datetime.utcnow().isoformat()
                }
            ]
        }
        
        tasks = await extractor.extract_tasks(conversation)
        
        assert len(tasks) == 1
        task = tasks[0]
        assert task["is_recurring"] is True
        assert "weekly" in task["recurrence_pattern"]


@pytest.mark.asyncio
class TestTaskIntelligence:
    """Test task intelligence service integration."""
    
    async def test_process_conversation_for_tasks(self, mock_db_session):
        """Test processing a conversation to extract tasks."""
        # Mock conversation and messages
        conversation_id = uuid4()
        user_id = uuid4()
        
        mock_conversation = Mock()
        mock_conversation.id = conversation_id
        mock_conversation.user_id = user_id
        mock_conversation.title = "Test conversation"
        
        mock_message = Mock()
        mock_message.role = "user"
        mock_message.content = "Remind me to review the budget tomorrow"
        mock_message.created_at = datetime.utcnow()
        
        # Mock database queries
        mock_db_session.execute = AsyncMock()
        mock_db_session.execute.side_effect = [
            Mock(scalar_one_or_none=Mock(return_value=mock_conversation)),
            Mock(scalars=Mock(return_value=Mock(all=Mock(return_value=[mock_message]))))
        ]
        mock_db_session.add = Mock()
        mock_db_session.commit = AsyncMock()
        
        # Test service
        service = TaskIntelligenceService(mock_db_session)
        service._task_already_exists = AsyncMock(return_value=False)
        service._link_task_to_memories = AsyncMock()
        
        result = await service.process_conversation_for_tasks(
            conversation_id, user_id, auto_create=True
        )
        
        assert result["conversation_id"] == str(conversation_id)
        assert result["extracted_count"] > 0
        assert "review the budget" in str(result["tasks"])
    
    async def test_get_upcoming_reminders(self, mock_db_session):
        """Test getting upcoming task reminders."""
        user_id = uuid4()
        
        # Mock tasks due in different timeframes
        task_urgent = Mock()
        task_urgent.id = uuid4()
        task_urgent.title = "Urgent task"
        task_urgent.priority = "high"
        task_urgent.due_date = datetime.utcnow() + timedelta(minutes=30)
        task_urgent.metadata = {}
        
        task_today = Mock()
        task_today.id = uuid4()
        task_today.title = "Today's task"
        task_today.priority = "medium"
        task_today.due_date = datetime.utcnow() + timedelta(hours=6)
        task_today.metadata = {}
        
        mock_db_session.execute = AsyncMock()
        mock_db_session.execute.return_value = Mock(
            scalars=Mock(return_value=Mock(all=Mock(return_value=[task_urgent, task_today])))
        )
        
        service = TaskIntelligenceService(mock_db_session)
        reminders = await service.get_upcoming_reminders(user_id, hours_ahead=24)
        
        assert len(reminders) == 2
        assert reminders[0]["reminder_type"] == "urgent"
        assert reminders[1]["reminder_type"] == "today"
    
    async def test_daily_summary_generation(self, mock_db_session):
        """Test generating daily task summary."""
        user_id = uuid4()
        
        # Mock today's tasks
        mock_task = Mock()
        mock_task.id = uuid4()
        mock_task.title = "Complete project review"
        mock_task.priority = "high"
        mock_task.status = "pending"
        mock_task.due_date = datetime.utcnow()
        
        # Mock database queries
        mock_db_session.execute = AsyncMock()
        mock_db_session.execute.side_effect = [
            Mock(scalars=Mock(return_value=Mock(all=Mock(return_value=[mock_task])))),  # Today's tasks
            Mock(scalars=Mock(return_value=Mock(all=Mock(return_value=[])))),  # Completed tasks
            Mock(scalars=Mock(return_value=Mock(all=Mock(return_value=[]))))   # Overdue tasks
        ]
        
        service = TaskIntelligenceService(mock_db_session)
        service._generate_insights = AsyncMock(return_value={"patterns": [], "suggestions": []})
        
        summary = await service.generate_daily_summary(user_id)
        
        assert summary["tasks_today"] == 1
        assert summary["today_breakdown"]["high_priority"] == 1
        assert len(summary["tasks"]["today"]) == 1


@pytest.mark.asyncio
class TestReminderEngine:
    """Test reminder engine functionality."""
    
    async def test_check_and_send_reminders(self, mock_db_session):
        """Test checking for and sending reminders."""
        # Mock active users
        mock_user = Mock()
        mock_user.id = uuid4()
        mock_user.is_active = True
        
        mock_db_session.execute = AsyncMock()
        mock_db_session.execute.return_value = Mock(
            scalars=Mock(return_value=Mock(all=Mock(return_value=[mock_user])))
        )
        
        engine = ReminderEngine(mock_db_session)
        engine.task_intelligence = Mock()
        engine.task_intelligence.get_upcoming_reminders = AsyncMock(return_value=[
            {
                "task_id": str(uuid4()),
                "title": "Test task",
                "hours_until_due": 2,
                "reminder_type": "soon"
            }
        ])
        engine._generate_reminder_message = AsyncMock(return_value="You have 1 task due soon")
        engine._store_reminder_for_delivery = AsyncMock()
        
        result = await engine.check_and_send_reminders()
        
        assert result["users_checked"] == 1
        assert result["users_notified"] == 1
        assert result["reminders_sent"] == 1
    
    async def test_smart_reminder_schedule(self, mock_db_session):
        """Test generating smart reminder schedules."""
        user_id = uuid4()
        task_id = uuid4()
        
        # Mock high priority task
        mock_task = Mock()
        mock_task.id = task_id
        mock_task.user_id = user_id
        mock_task.priority = "high"
        mock_task.due_date = datetime.utcnow() + timedelta(days=3)
        
        mock_db_session.execute = AsyncMock()
        mock_db_session.execute.return_value = Mock(
            scalar_one_or_none=Mock(return_value=mock_task)
        )
        
        engine = ReminderEngine(mock_db_session)
        schedule = await engine.generate_smart_reminder_schedule(user_id, task_id)
        
        # High priority tasks should have multiple reminders
        assert len(schedule) >= 2
        assert all(reminder > datetime.utcnow() for reminder in schedule)
        assert all(reminder < mock_task.due_date for reminder in schedule)


@pytest.mark.asyncio
class TestSuggestionEngine:
    """Test task suggestion engine."""
    
    async def test_analyze_user_patterns(self, mock_db_session):
        """Test analyzing user task patterns."""
        user_id = uuid4()
        
        # Mock completed tasks
        tasks = []
        for i in range(5):
            task = Mock()
            task.title = f"Weekly meeting {i}"
            task.status = TaskStatus.COMPLETED
            task.due_date = datetime.utcnow() - timedelta(days=i*7, hours=10)  # Same time each week
            task.description = ""
            tasks.append(task)
        
        mock_db_session.execute = AsyncMock()
        mock_db_session.execute.return_value = Mock(
            scalars=Mock(return_value=Mock(all=Mock(return_value=tasks)))
        )
        
        engine = TaskSuggestionEngine(mock_db_session)
        patterns = await engine._analyze_user_patterns(user_id)
        
        assert 10 in patterns["common_times"]  # 10am is common
        assert "meeting" in patterns["recurring_themes"]
    
    async def test_generate_suggestions(self, mock_db_session):
        """Test generating task suggestions."""
        user_id = uuid4()
        
        # Mock pattern analysis
        mock_db_session.execute = AsyncMock()
        mock_db_session.execute.return_value = Mock(
            scalars=Mock(return_value=Mock(all=Mock(return_value=[])))
        )
        
        engine = TaskSuggestionEngine(mock_db_session)
        engine._analyze_user_patterns = AsyncMock(return_value={
            "common_times": {9: 5, 14: 3},
            "recurring_themes": {"meeting": 10}
        })
        engine._get_contextual_memories = AsyncMock(return_value=[])
        engine._suggest_recurring_tasks = AsyncMock(return_value=[{
            "type": "recurring",
            "title": "Weekly team meeting",
            "confidence": 0.8
        }])
        engine._suggest_follow_up_tasks = AsyncMock(return_value=[])
        engine._suggest_from_memories = AsyncMock(return_value=[])
        engine._suggest_time_based_tasks = AsyncMock(return_value=[])
        engine._refine_suggestions_with_llm = AsyncMock(side_effect=lambda u, s, p, c: s[:5])
        
        suggestions = await engine.generate_suggestions(user_id)
        
        assert len(suggestions) > 0
        assert suggestions[0]["type"] == "recurring"
        assert suggestions[0]["confidence"] >= 0.5


# Fixtures
@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = AsyncMock()
    session.add = Mock()
    session.commit = AsyncMock()
    session.flush = AsyncMock()
    return session