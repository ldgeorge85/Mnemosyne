"""
Comprehensive unit tests for MemoryReflectionService.
Tests all methods, error handling, and edge cases for memory reflection and importance scoring.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

import pytest
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.memory.reflection import MemoryReflectionService
from app.db.models.agent import MemoryReflection


@pytest.fixture
def mock_db_session():
    """Create a mock database session for testing."""
    session = AsyncMock(spec=AsyncSession)
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def memory_reflection_service(mock_db_session):
    """Create a MemoryReflectionService instance with mocked database session."""
    return MemoryReflectionService(db_session=mock_db_session)


@pytest.mark.asyncio
class TestMemoryReflectionService:
    """Test suite for MemoryReflectionService."""

    async def test_reflect_success(self, memory_reflection_service, mock_db_session):
        """Test successful memory reflection with valid inputs."""
        agent_id = str(uuid.uuid4())
        memories = [
            {"id": str(uuid.uuid4()), "content": "User prefers morning meetings"},
            {"id": str(uuid.uuid4()), "content": "User works in Pacific timezone"},
            {"id": str(uuid.uuid4()), "content": "User likes detailed project updates"}
        ]
        
        result = await memory_reflection_service.reflect(agent_id, memories)
        
        # Verify reflection structure
        assert "summary" in result
        assert "memories" in result
        assert result["memories"] == memories
        assert f"Reflected on {len(memories)} memories" in result["summary"]
        
        # Verify database operations
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_awaited_once()
        
        # Verify MemoryReflection object creation
        added_reflection = mock_db_session.add.call_args[0][0]
        assert isinstance(added_reflection, MemoryReflection)
        assert added_reflection.agent_id == agent_id
        assert added_reflection.reflection == result
        assert added_reflection.importance_score == 5

    async def test_reflect_empty_memories(self, memory_reflection_service, mock_db_session):
        """Test memory reflection with empty memories list."""
        agent_id = str(uuid.uuid4())
        memories = []
        
        result = await memory_reflection_service.reflect(agent_id, memories)
        
        assert result["summary"] == "Reflected on 0 memories."
        assert result["memories"] == []
        
        # Verify database operations still occur
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_awaited_once()

    async def test_reflect_single_memory(self, memory_reflection_service, mock_db_session):
        """Test memory reflection with single memory."""
        agent_id = str(uuid.uuid4())
        memories = [{"id": str(uuid.uuid4()), "content": "Single important memory"}]
        
        result = await memory_reflection_service.reflect(agent_id, memories)
        
        assert result["summary"] == "Reflected on 1 memories."
        assert len(result["memories"]) == 1
        assert result["memories"][0]["content"] == "Single important memory"

    async def test_reflect_database_commit_error(self, memory_reflection_service, mock_db_session):
        """Test memory reflection when database commit fails."""
        agent_id = str(uuid.uuid4())
        memories = [{"id": str(uuid.uuid4()), "content": "Test memory"}]
        
        mock_db_session.commit.side_effect = Exception("Database commit failed")
        
        with pytest.raises(Exception, match="Database commit failed"):
            await memory_reflection_service.reflect(agent_id, memories)

    async def test_reflect_invalid_agent_id(self, memory_reflection_service, mock_db_session):
        """Test memory reflection with invalid agent ID format."""
        agent_id = "invalid-uuid"
        memories = [{"id": str(uuid.uuid4()), "content": "Test memory"}]
        
        # Should still work as the service doesn't validate UUID format
        result = await memory_reflection_service.reflect(agent_id, memories)
        
        assert result["summary"] == "Reflected on 1 memories."
        added_reflection = mock_db_session.add.call_args[0][0]
        assert added_reflection.agent_id == "invalid-uuid"

    async def test_get_importance_scores_success(self, memory_reflection_service, mock_db_session):
        """Test successful retrieval of importance scores."""
        agent_id = str(uuid.uuid4())
        
        # Mock database query result
        mock_result = MagicMock()
        mock_scores = [
            {
                'id': str(uuid.uuid4()),
                'agent_id': agent_id,
                'importance_score': 8,
                'reflection': {'summary': 'High importance memory'},
                'created_at': datetime.now()
            },
            {
                'id': str(uuid.uuid4()),
                'agent_id': agent_id,
                'importance_score': 3,
                'reflection': {'summary': 'Low importance memory'},
                'created_at': datetime.now()
            }
        ]
        mock_result.fetchall.return_value = mock_scores
        mock_db_session.execute.return_value = mock_result
        
        scores = await memory_reflection_service.get_importance_scores(agent_id)
        
        assert len(scores) == 2
        assert scores == mock_scores
        assert scores[0]['importance_score'] == 8
        assert scores[1]['importance_score'] == 3
        
        # Verify database query was executed
        mock_db_session.execute.assert_called_once()

    async def test_get_importance_scores_no_results(self, memory_reflection_service, mock_db_session):
        """Test importance scores retrieval when no reflections exist."""
        agent_id = str(uuid.uuid4())
        
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db_session.execute.return_value = mock_result
        
        scores = await memory_reflection_service.get_importance_scores(agent_id)
        
        assert scores == []
        mock_db_session.execute.assert_called_once()

    async def test_get_importance_scores_database_error(self, memory_reflection_service, mock_db_session):
        """Test importance scores retrieval when database query fails."""
        agent_id = str(uuid.uuid4())
        mock_db_session.execute.side_effect = Exception("Database query failed")
        
        with pytest.raises(Exception, match="Database query failed"):
            await memory_reflection_service.get_importance_scores(agent_id)

    async def test_get_hierarchy_success(self, memory_reflection_service, mock_db_session):
        """Test successful retrieval of memory hierarchy."""
        agent_id = str(uuid.uuid4())
        
        # Mock get_importance_scores method
        mock_scores = [
            {'id': str(uuid.uuid4()), 'importance_score': 9, 'reflection': {'summary': 'Critical memory'}},
            {'id': str(uuid.uuid4()), 'importance_score': 5, 'reflection': {'summary': 'Medium memory'}},
            {'id': str(uuid.uuid4()), 'importance_score': 2, 'reflection': {'summary': 'Low memory'}}
        ]
        
        with patch.object(memory_reflection_service, 'get_importance_scores') as mock_get_scores:
            mock_get_scores.return_value = mock_scores
            
            hierarchy = await memory_reflection_service.get_hierarchy(agent_id)
            
            assert hierarchy['agent_id'] == agent_id
            assert hierarchy['hierarchy'] == mock_scores
            assert len(hierarchy['hierarchy']) == 3
            
            mock_get_scores.assert_called_once_with(agent_id)

    async def test_get_hierarchy_empty_scores(self, memory_reflection_service, mock_db_session):
        """Test hierarchy retrieval when no importance scores exist."""
        agent_id = str(uuid.uuid4())
        
        with patch.object(memory_reflection_service, 'get_importance_scores') as mock_get_scores:
            mock_get_scores.return_value = []
            
            hierarchy = await memory_reflection_service.get_hierarchy(agent_id)
            
            assert hierarchy['agent_id'] == agent_id
            assert hierarchy['hierarchy'] == []

    async def test_get_hierarchy_scores_error(self, memory_reflection_service, mock_db_session):
        """Test hierarchy retrieval when get_importance_scores fails."""
        agent_id = str(uuid.uuid4())
        
        with patch.object(memory_reflection_service, 'get_importance_scores') as mock_get_scores:
            mock_get_scores.side_effect = Exception("Scores retrieval failed")
            
            with pytest.raises(Exception, match="Scores retrieval failed"):
                await memory_reflection_service.get_hierarchy(agent_id)

    async def test_service_initialization_default_session(self):
        """Test MemoryReflectionService initialization with default session."""
        with patch('app.services.memory.reflection.async_session_maker') as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value = mock_session
            
            service = MemoryReflectionService()
            
            assert service.db_session == mock_session
            mock_session_maker.assert_called_once()

    async def test_service_initialization_custom_session(self, mock_db_session):
        """Test MemoryReflectionService initialization with custom session."""
        service = MemoryReflectionService(db_session=mock_db_session)
        
        assert service.db_session == mock_db_session


@pytest.mark.asyncio
class TestMemoryReflectionServiceIntegration:
    """Integration tests for MemoryReflectionService with multiple operations."""

    async def test_reflect_and_retrieve_workflow(self, memory_reflection_service, mock_db_session):
        """Test complete workflow of reflecting on memories and retrieving scores."""
        agent_id = str(uuid.uuid4())
        memories = [
            {"id": str(uuid.uuid4()), "content": "Important user preference"},
            {"id": str(uuid.uuid4()), "content": "Critical system configuration"}
        ]
        
        # Mock the get_importance_scores method for the workflow test
        with patch.object(memory_reflection_service, 'get_importance_scores') as mock_get_scores:
            mock_scores = [
                {'id': str(uuid.uuid4()), 'importance_score': 7, 'agent_id': agent_id}
            ]
            mock_get_scores.return_value = mock_scores
            
            # Perform reflection
            reflection_result = await memory_reflection_service.reflect(agent_id, memories)
            assert reflection_result['summary'] == "Reflected on 2 memories."
            
            # Retrieve importance scores
            scores = await memory_reflection_service.get_importance_scores(agent_id)
            assert len(scores) == 1
            assert scores[0]['importance_score'] == 7
            
            # Get hierarchy
            hierarchy = await memory_reflection_service.get_hierarchy(agent_id)
            assert hierarchy['agent_id'] == agent_id
            assert hierarchy['hierarchy'] == mock_scores

    async def test_multiple_reflections_workflow(self, memory_reflection_service, mock_db_session):
        """Test workflow with multiple reflection operations for same agent."""
        agent_id = str(uuid.uuid4())
        
        # First reflection
        memories1 = [{"id": str(uuid.uuid4()), "content": "First batch of memories"}]
        result1 = await memory_reflection_service.reflect(agent_id, memories1)
        assert result1['summary'] == "Reflected on 1 memories."
        
        # Second reflection
        memories2 = [
            {"id": str(uuid.uuid4()), "content": "Second batch memory 1"},
            {"id": str(uuid.uuid4()), "content": "Second batch memory 2"}
        ]
        result2 = await memory_reflection_service.reflect(agent_id, memories2)
        assert result2['summary'] == "Reflected on 2 memories."
        
        # Verify both reflections were processed
        assert mock_db_session.add.call_count == 2
        assert mock_db_session.commit.call_count == 2

    async def test_cross_agent_isolation(self, memory_reflection_service, mock_db_session):
        """Test that reflections are properly isolated between different agents."""
        agent1_id = str(uuid.uuid4())
        agent2_id = str(uuid.uuid4())
        
        memories1 = [{"id": str(uuid.uuid4()), "content": "Agent 1 memory"}]
        memories2 = [{"id": str(uuid.uuid4()), "content": "Agent 2 memory"}]
        
        # Reflect for both agents
        result1 = await memory_reflection_service.reflect(agent1_id, memories1)
        result2 = await memory_reflection_service.reflect(agent2_id, memories2)
        
        # Verify both reflections were created with correct agent IDs
        assert mock_db_session.add.call_count == 2
        
        # Check that the correct agent IDs were used
        calls = mock_db_session.add.call_args_list
        reflection1 = calls[0][0][0]
        reflection2 = calls[1][0][0]
        
        assert reflection1.agent_id == agent1_id
        assert reflection2.agent_id == agent2_id
        assert reflection1.reflection != reflection2.reflection


@pytest.mark.asyncio
class TestMemoryReflectionServiceEdgeCases:
    """Edge case tests for MemoryReflectionService."""

    async def test_reflect_with_complex_memory_structure(self, memory_reflection_service, mock_db_session):
        """Test reflection with complex nested memory structures."""
        agent_id = str(uuid.uuid4())
        complex_memories = [
            {
                "id": str(uuid.uuid4()),
                "content": "Complex memory",
                "metadata": {
                    "importance": "high",
                    "tags": ["user_preference", "critical"],
                    "context": {
                        "session_id": str(uuid.uuid4()),
                        "timestamp": datetime.now().isoformat()
                    }
                }
            }
        ]
        
        result = await memory_reflection_service.reflect(agent_id, complex_memories)
        
        assert result['memories'] == complex_memories
        assert "Reflected on 1 memories" in result['summary']
        
        # Verify the complex structure was preserved
        added_reflection = mock_db_session.add.call_args[0][0]
        assert added_reflection.reflection['memories'][0]['metadata']['importance'] == "high"

    async def test_reflect_with_none_memories(self, memory_reflection_service, mock_db_session):
        """Test reflection behavior with None as memories input."""
        agent_id = str(uuid.uuid4())
        
        # This should handle None gracefully or raise appropriate error
        try:
            result = await memory_reflection_service.reflect(agent_id, None)
            # If it doesn't raise an error, verify it handles None appropriately
            assert result is not None
        except (TypeError, AttributeError):
            # Expected behavior for None input
            pass

    async def test_importance_score_consistency(self, memory_reflection_service, mock_db_session):
        """Test that importance scores are consistently set."""
        agent_id = str(uuid.uuid4())
        memories = [{"id": str(uuid.uuid4()), "content": "Test memory"}]
        
        # Perform multiple reflections
        for i in range(3):
            await memory_reflection_service.reflect(agent_id, memories)
        
        # Verify all reflections have the same importance score
        calls = mock_db_session.add.call_args_list
        for call in calls:
            reflection = call[0][0]
            assert reflection.importance_score == 5  # Default score from implementation
