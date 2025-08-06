"""
Integration tests for /memories/* API endpoints.
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

@patch('app.api.v1.endpoints.memories.async_session_maker')
@patch('app.services.memory.reflection.MemoryReflectionService.reflect')
def test_reflect_memory_api(mock_reflect, mock_session_maker):
    """Test POST /memories/reflect endpoint with mocked database and service."""
    # Mock the database session
    mock_db = AsyncMock()
    mock_session_context = AsyncSessionContextMock(mock_db)
    mock_session_maker.return_value = mock_session_context
    
    # Mock the reflection service to return a fake response
    mock_reflection_result = "This is a test reflection"
    mock_reflect.return_value = mock_reflection_result
    
    # Create a test client for FastAPI app
    test_client = TestClient(app)
    
    try:
        # Use the correct endpoint path as shown in the route listing
        endpoint = "/api/v1/memories/memories/reflect"
        
        # Make the request with the correct path
        response = test_client.post(endpoint, json={"agent_id": "agent-1", "memories": ["m1", "m2"]})
        
        # Print response for debugging
        print(f"\nResponse status: {response.status_code}")
        print(f"Response body: {response.json() if response.status_code == 200 else response.text}")
        
        # Assert the response
        assert response.status_code == 200
        assert "reflection" in response.json()
        assert response.json()["reflection"] == "This is a test reflection"
        
        # Verify the mock was called
        mock_reflect.assert_called_once()
    except Exception as e:
        print(f"\n\nEXCEPTION DETAILS: {type(e).__name__}: {str(e)}")
        print("\nTRACEBACK:")
        traceback.print_exc()
        raise
