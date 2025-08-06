"""
Comprehensive unit tests for AgentManager service.
Tests all methods, error handling, and edge cases for agent orchestration.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

import pytest
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.agent.agent_manager import AgentManager
from app.db.models.agent import Agent, AgentLink, AgentLog


@pytest.fixture
def mock_db_session():
    """Create a mock database session for testing."""
    session = AsyncMock(spec=AsyncSession)
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.get = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def agent_manager(mock_db_session):
    """Create an AgentManager instance with mocked database session."""
    return AgentManager(db_session=mock_db_session)


@pytest.mark.asyncio
class TestAgentManager:
    """Test suite for AgentManager service."""

    async def test_create_agent_success(self, agent_manager, mock_db_session):
        """Test successful agent creation with valid configuration."""
        config = {
            'name': 'TestAgent',
            'role': 'assistant',
            'capabilities': ['task_execution', 'memory_management']
        }
        
        agent_id = await agent_manager.create_agent(config)
        
        # Verify agent ID is a valid UUID
        assert uuid.UUID(agent_id)
        
        # Verify database operations
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_awaited_once()
        
        # Verify agent object creation
        added_agent = mock_db_session.add.call_args[0][0]
        assert isinstance(added_agent, Agent)
        assert added_agent.name == 'TestAgent'
        assert added_agent.config == config

    async def test_create_agent_minimal_config(self, agent_manager, mock_db_session):
        """Test agent creation with minimal configuration."""
        config = {}
        
        agent_id = await agent_manager.create_agent(config)
        
        # Verify default name is used
        added_agent = mock_db_session.add.call_args[0][0]
        assert added_agent.name == 'Agent'
        assert added_agent.config == config

    async def test_create_agent_database_error(self, agent_manager, mock_db_session):
        """Test agent creation when database commit fails."""
        mock_db_session.commit.side_effect = Exception("Database error")
        
        with pytest.raises(Exception, match="Database error"):
            await agent_manager.create_agent({'name': 'TestAgent'})

    async def test_link_agents_success(self, agent_manager, mock_db_session):
        """Test successful agent linking."""
        parent_id = str(uuid.uuid4())
        child_id = str(uuid.uuid4())
        
        await agent_manager.link_agents(parent_id, child_id)
        
        # Verify database operations
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_awaited_once()
        
        # Verify link object creation
        added_link = mock_db_session.add.call_args[0][0]
        assert isinstance(added_link, AgentLink)
        assert added_link.parent_id == parent_id
        assert added_link.child_id == child_id

    async def test_link_agents_database_error(self, agent_manager, mock_db_session):
        """Test agent linking when database commit fails."""
        mock_db_session.commit.side_effect = Exception("Link creation failed")
        
        with pytest.raises(Exception, match="Link creation failed"):
            await agent_manager.link_agents("parent-id", "child-id")

    async def test_assign_task_success(self, agent_manager, mock_db_session):
        """Test successful task assignment to agent."""
        agent_id = str(uuid.uuid4())
        task = {
            'type': 'data_analysis',
            'description': 'Analyze user behavior patterns',
            'priority': 'high'
        }
        
        # Mock the log ID return
        mock_log = MagicMock()
        mock_log.id = uuid.uuid4()
        mock_db_session.add.side_effect = lambda obj: setattr(obj, 'id', mock_log.id)
        
        log_id = await agent_manager.assign_task(agent_id, task)
        
        # Verify log ID is returned as string
        assert log_id == str(mock_log.id)
        
        # Verify database operations
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_awaited_once()
        
        # Verify log object creation
        added_log = mock_db_session.add.call_args[0][0]
        assert isinstance(added_log, AgentLog)
        assert added_log.agent_id == agent_id
        assert added_log.log == task

    async def test_assign_task_empty_task(self, agent_manager, mock_db_session):
        """Test task assignment with empty task dictionary."""
        agent_id = str(uuid.uuid4())
        task = {}
        
        mock_log = MagicMock()
        mock_log.id = uuid.uuid4()
        mock_db_session.add.side_effect = lambda obj: setattr(obj, 'id', mock_log.id)
        
        log_id = await agent_manager.assign_task(agent_id, task)
        
        assert log_id == str(mock_log.id)
        added_log = mock_db_session.add.call_args[0][0]
        assert added_log.log == {}

    async def test_get_status_agent_found(self, agent_manager, mock_db_session):
        """Test getting agent status when agent exists."""
        agent_id = str(uuid.uuid4())
        
        # Mock agent retrieval
        mock_agent = MagicMock()
        mock_agent.id = agent_id
        mock_agent.name = "TestAgent"
        mock_agent.status = "active"
        mock_db_session.get.return_value = mock_agent
        
        # Mock logs retrieval
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            {'id': str(uuid.uuid4()), 'log': {'task': 'test'}, 'timestamp': datetime.now()},
            {'id': str(uuid.uuid4()), 'log': {'task': 'test2'}, 'timestamp': datetime.now()}
        ]
        mock_db_session.execute.return_value = mock_result
        
        status = await agent_manager.get_status(agent_id)
        
        # Verify status structure
        assert status['id'] == agent_id
        assert status['name'] == "TestAgent"
        assert status['status'] == "active"
        assert len(status['logs']) == 2
        
        # Verify database calls
        mock_db_session.get.assert_called_once_with(Agent, agent_id)
        mock_db_session.execute.assert_called_once()

    async def test_get_status_agent_not_found(self, agent_manager, mock_db_session):
        """Test getting agent status when agent doesn't exist."""
        agent_id = str(uuid.uuid4())
        mock_db_session.get.return_value = None
        
        status = await agent_manager.get_status(agent_id)
        
        assert status == {"error": "Agent not found"}

    async def test_spawn_subagent_success(self, agent_manager, mock_db_session):
        """Test successful subagent spawning."""
        parent_id = str(uuid.uuid4())
        config = {'name': 'SubAgent', 'role': 'worker'}
        
        # Mock create_agent and link_agents methods
        with patch.object(agent_manager, 'create_agent') as mock_create, \
             patch.object(agent_manager, 'link_agents') as mock_link:
            
            subagent_id = str(uuid.uuid4())
            mock_create.return_value = subagent_id
            mock_link.return_value = None
            
            result = await agent_manager.spawn_subagent(parent_id, config)
            
            assert result == subagent_id
            mock_create.assert_called_once_with(config)
            mock_link.assert_called_once_with(parent_id, subagent_id)

    async def test_spawn_subagent_creation_fails(self, agent_manager, mock_db_session):
        """Test subagent spawning when agent creation fails."""
        parent_id = str(uuid.uuid4())
        config = {'name': 'SubAgent'}
        
        with patch.object(agent_manager, 'create_agent') as mock_create:
            mock_create.side_effect = Exception("Agent creation failed")
            
            with pytest.raises(Exception, match="Agent creation failed"):
                await agent_manager.spawn_subagent(parent_id, config)

    async def test_get_logs_success(self, agent_manager, mock_db_session):
        """Test successful log retrieval for an agent."""
        agent_id = str(uuid.uuid4())
        
        # Mock logs retrieval
        mock_result = MagicMock()
        mock_logs = [
            {'id': str(uuid.uuid4()), 'log': {'task': 'analysis'}, 'timestamp': datetime.now()},
            {'id': str(uuid.uuid4()), 'log': {'task': 'reporting'}, 'timestamp': datetime.now()}
        ]
        mock_result.fetchall.return_value = mock_logs
        mock_db_session.execute.return_value = mock_result
        
        logs = await agent_manager.get_logs(agent_id)
        
        assert len(logs) == 2
        assert logs == mock_logs
        mock_db_session.execute.assert_called_once()

    async def test_get_logs_no_logs(self, agent_manager, mock_db_session):
        """Test log retrieval when agent has no logs."""
        agent_id = str(uuid.uuid4())
        
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db_session.execute.return_value = mock_result
        
        logs = await agent_manager.get_logs(agent_id)
        
        assert logs == []

    async def test_get_logs_database_error(self, agent_manager, mock_db_session):
        """Test log retrieval when database query fails."""
        agent_id = str(uuid.uuid4())
        mock_db_session.execute.side_effect = Exception("Database query failed")
        
        with pytest.raises(Exception, match="Database query failed"):
            await agent_manager.get_logs(agent_id)

    async def test_agent_manager_initialization_default_session(self):
        """Test AgentManager initialization with default session."""
        with patch('app.services.agent.agent_manager.async_session_maker') as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value = mock_session
            
            manager = AgentManager()
            
            assert manager.db_session == mock_session
            mock_session_maker.assert_called_once()

    async def test_agent_manager_initialization_custom_session(self, mock_db_session):
        """Test AgentManager initialization with custom session."""
        manager = AgentManager(db_session=mock_db_session)
        
        assert manager.db_session == mock_db_session


@pytest.mark.asyncio
class TestAgentManagerIntegration:
    """Integration tests for AgentManager with multiple operations."""

    async def test_create_and_link_workflow(self, agent_manager, mock_db_session):
        """Test complete workflow of creating agents and linking them."""
        # Mock successful operations
        with patch.object(agent_manager, 'create_agent') as mock_create, \
             patch.object(agent_manager, 'link_agents') as mock_link:
            
            parent_id = str(uuid.uuid4())
            child_id = str(uuid.uuid4())
            
            mock_create.side_effect = [parent_id, child_id]
            mock_link.return_value = None
            
            # Create parent agent
            created_parent = await agent_manager.create_agent({'name': 'Parent'})
            assert created_parent == parent_id
            
            # Create child agent
            created_child = await agent_manager.create_agent({'name': 'Child'})
            assert created_child == child_id
            
            # Link agents
            await agent_manager.link_agents(parent_id, child_id)
            
            # Verify all operations were called
            assert mock_create.call_count == 2
            mock_link.assert_called_once_with(parent_id, child_id)

    async def test_agent_task_assignment_workflow(self, agent_manager, mock_db_session):
        """Test workflow of creating agent and assigning multiple tasks."""
        agent_id = str(uuid.uuid4())
        
        with patch.object(agent_manager, 'create_agent') as mock_create, \
             patch.object(agent_manager, 'assign_task') as mock_assign:
            
            mock_create.return_value = agent_id
            mock_assign.side_effect = [str(uuid.uuid4()), str(uuid.uuid4())]
            
            # Create agent
            created_id = await agent_manager.create_agent({'name': 'Worker'})
            assert created_id == agent_id
            
            # Assign multiple tasks
            task1 = {'type': 'analysis', 'priority': 'high'}
            task2 = {'type': 'reporting', 'priority': 'medium'}
            
            log1_id = await agent_manager.assign_task(agent_id, task1)
            log2_id = await agent_manager.assign_task(agent_id, task2)
            
            assert log1_id != log2_id
            assert mock_assign.call_count == 2
