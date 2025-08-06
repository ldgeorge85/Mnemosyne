"""
Integration tests for /memories/search API endpoint.
"""
import sys, os
import traceback
import logging
import uuid
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.db.models.memory import Memory

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

# Mock for get_current_user dependency
def get_test_user():
    """Return a mock user for testing."""
    user = MagicMock()
    user.id = uuid.UUID("a3bb93e1-0aaa-452f-84af-56aa6a312bf0")
    user.username = "testuser"
    user.email = "test@example.com"
    user.is_active = True
    user.is_superuser = False
    return user

@patch('app.api.v1.endpoints.memories.get_current_user', return_value=get_test_user())
@patch('app.api.v1.endpoints.memories.get_async_db')
def test_search_memories_empty(mock_get_db, mock_get_current_user):
    """Test POST /memories/search endpoint with empty result."""
    # Mock the database session
    mock_db = AsyncMock()
    mock_session_context = AsyncSessionContextMock(mock_db)
    mock_get_db.return_value = mock_session_context
    
    # Mock the repository method to return empty list
    with patch('app.api.v1.endpoints.memories.MemoryRepository') as mock_repo_class:
        mock_repo = mock_repo_class.return_value
        mock_repo.search_memories_by_text.return_value = []
        
        # Create a test client for FastAPI app
        test_client = TestClient(app)
        
        try:
            # Use the correct endpoint path
            endpoint = "/api/v1/memories/search"
            
            # Create search payload
            search_payload = {
                "query": "test query",
                "user_id": str(get_test_user().id),
                "limit": 10,
                "include_inactive": False
            }
            
            # Make the request
            response = test_client.post(endpoint, json=search_payload)
            
            # Print response for debugging
            print(f"\nResponse status: {response.status_code}")
            print(f"Response body: {response.json() if response.status_code == 200 else response.text}")
            
            # Assert the response
            assert response.status_code == 200
            assert "query" in response.json()
            assert response.json()["query"] == "test query"
            assert response.json()["results"] == []
            assert response.json()["total"] == 0
            
            # Verify the mock was called with correct parameters
            mock_repo.search_memories_by_text.assert_called_once_with(
                str(get_test_user().id),
                "test query",
                limit=10,
                include_inactive=False
            )
        except Exception as e:
            print(f"\n\nEXCEPTION DETAILS: {type(e).__name__}: {str(e)}")
            print("\nTRACEBACK:")
            traceback.print_exc()
            raise

@patch('app.api.v1.endpoints.memories.get_current_user', return_value=get_test_user())
@patch('app.api.v1.endpoints.memories.get_async_db')
def test_search_memories_with_results(mock_get_db, mock_get_current_user):
    """Test POST /memories/search endpoint with mock results."""
    # Mock the database session
    mock_db = AsyncMock()
    mock_session_context = AsyncSessionContextMock(mock_db)
    mock_get_db.return_value = mock_session_context
    
    # Create mock memories
    mock_memories = [
        Memory(
            id=uuid.uuid4(),
            user_id=get_test_user().id,
            title=f"Test Memory {i}",
            content=f"Test content with search term {i}",
            tags=["test", f"tag{i}"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True,
            importance_score=0.5,
            source="test"
        )
        for i in range(3)
    ]
    
    # Mock the repository method to return mock memories
    with patch('app.api.v1.endpoints.memories.MemoryRepository') as mock_repo_class:
        mock_repo = mock_repo_class.return_value
        mock_repo.search_memories_by_text.return_value = mock_memories
        
        # Create a test client for FastAPI app
        test_client = TestClient(app)
        
        try:
            # Use the correct endpoint path
            endpoint = "/api/v1/memories/search"
            
            # Create search payload
            search_payload = {
                "query": "search term",
                "user_id": str(get_test_user().id),
                "limit": 10,
                "include_inactive": False
            }
            
            # Make the request
            response = test_client.post(endpoint, json=search_payload)
            
            # Print response for debugging
            print(f"\nResponse status: {response.status_code}")
            print(f"Response body: {response.json() if response.status_code == 200 else response.text}")
            
            # Assert the response
            assert response.status_code == 200
            assert "query" in response.json()
            assert response.json()["query"] == "search term"
            assert len(response.json()["results"]) == 3
            assert response.json()["total"] == 3
            
            # Verify memory data is correctly returned
            for i, memory in enumerate(response.json()["results"]):
                assert memory["title"] == f"Test Memory {i}"
                assert memory["content"] == f"Test content with search term {i}"
                assert "test" in memory["tags"]
                assert f"tag{i}" in memory["tags"]
            
            # Verify the mock was called with correct parameters
            mock_repo.search_memories_by_text.assert_called_once_with(
                str(get_test_user().id),
                "search term",
                limit=10,
                include_inactive=False
            )
        except Exception as e:
            print(f"\n\nEXCEPTION DETAILS: {type(e).__name__}: {str(e)}")
            print("\nTRACEBACK:")
            traceback.print_exc()
            raise

@patch('app.api.v1.endpoints.memories.get_current_user', return_value=get_test_user())
@patch('app.api.v1.endpoints.memories.get_async_db')
def test_search_memories_unauthorized_user(mock_get_db, mock_get_current_user):
    """Test POST /memories/search endpoint with unauthorized user."""
    # Mock the database session
    mock_db = AsyncMock()
    mock_session_context = AsyncSessionContextMock(mock_db)
    mock_get_db.return_value = mock_session_context
    
    # Create a test client for FastAPI app
    test_client = TestClient(app)
    
    try:
        # Use the correct endpoint path
        endpoint = "/api/v1/memories/search"
        
        # Create search payload with different user_id
        different_user_id = str(uuid.uuid4())
        search_payload = {
            "query": "search term",
            "user_id": different_user_id,  # Different from current_user.id
            "limit": 10,
            "include_inactive": False
        }
        
        # Make the request
        response = test_client.post(endpoint, json=search_payload)
        
        # Print response for debugging
        print(f"\nResponse status: {response.status_code}")
        print(f"Response body: {response.json() if response.status_code == 200 else response.text}")
        
        # Assert the response
        assert response.status_code == 403
        assert "detail" in response.json()
        assert "You can only search your own memories" in response.json()["detail"]
        
    except Exception as e:
        print(f"\n\nEXCEPTION DETAILS: {type(e).__name__}: {str(e)}")
        print("\nTRACEBACK:")
        traceback.print_exc()
        raise
