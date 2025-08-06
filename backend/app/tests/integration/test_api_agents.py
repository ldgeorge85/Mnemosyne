"""
Integration tests for /agents/* API endpoints.
"""
import sys, os
import traceback
import logging
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

# Disable logging during tests to avoid string formatting issues
logging.disable(logging.CRITICAL)

# Create a context manager mock for async_session_maker
class AsyncSessionContextMock:
    def __init__(self, mock_db):
        self.mock_db = mock_db
    
    async def __aenter__(self):
        return self.mock_db
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

@patch('app.api.v1.endpoints.agents.async_session_maker')
@patch('app.services.agent.agent_manager.AgentManager.create_agent')
def test_create_agent_api(mock_create_agent, mock_session_maker):
    """Test POST /agents/ endpoint with mocked database and service."""
    # Mock the database session
    mock_db = AsyncMock()
    mock_session_context = AsyncSessionContextMock(mock_db)
    mock_session_maker.return_value = mock_session_context
    
    # Mock the create_agent method to return a fake agent_id
    mock_create_agent.return_value = "test-agent-id-123"
    
    # Create a test client for FastAPI app
    test_client = TestClient(app)
    
    try:
        # Use the correct endpoint path as shown in the route listing
        endpoint = "/api/v1/agents/agents/"
        
        # Make the request with the correct path
        response = test_client.post(endpoint, json={"name": "test_agent", "role": "test"})
        
        # Print response for debugging
        print(f"\nResponse status: {response.status_code}")
        print(f"Response body: {response.json() if response.status_code == 200 else response.text}")
        
        # Assert the response
        assert response.status_code == 200
        assert "agent_id" in response.json()
        assert response.json()["agent_id"] == "test-agent-id-123"
        
        # Verify the mock was called
        mock_create_agent.assert_called_once()
    except Exception as e:
        print(f"\n\nEXCEPTION DETAILS: {type(e).__name__}: {str(e)}")
        print("\nTRACEBACK:")
        traceback.print_exc()
        raise
