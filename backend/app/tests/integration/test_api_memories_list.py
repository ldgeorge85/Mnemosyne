"""
Integration tests for /memories/ API endpoint (list memories).
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
def test_list_memories_empty(mock_get_db, mock_get_current_user):
    """Test GET /memories/ endpoint with empty result."""
    # Mock the database session
    mock_db = AsyncMock()
    mock_session_context = AsyncSessionContextMock(mock_db)
    mock_get_db.return_value = mock_session_context
    
    # Mock the repository method to return empty list
    with patch('app.api.v1.endpoints.memories.MemoryRepository') as mock_repo_class:
        mock_repo = mock_repo_class.return_value
        mock_repo.get_memories_by_user_id.return_value = ([], 0)
        
        # Create a test client for FastAPI app
        test_client = TestClient(app)
        
        try:
            # Use the correct endpoint path
            endpoint = "/api/v1/memories/"
            
            # Make the request
            response = test_client.get(endpoint)
            
            # Print response for debugging
            print(f"\nResponse status: {response.status_code}")
            print(f"Response body: {response.json() if response.status_code == 200 else response.text}")
            
            # Assert the response
            assert response.status_code == 200
            assert "items" in response.json()
            assert response.json()["items"] == []
            assert response.json()["total"] == 0
            
            # Verify the mock was called with correct parameters
            mock_repo.get_memories_by_user_id.assert_called_once_with(
                str(get_test_user().id),
                limit=10,
                offset=0,
                include_inactive=False
            )
        except Exception as e:
            print(f"\n\nEXCEPTION DETAILS: {type(e).__name__}: {str(e)}")
            print("\nTRACEBACK:")
            traceback.print_exc()
            raise

@patch('app.api.v1.endpoints.memories.get_current_user', return_value=get_test_user())
@patch('app.api.v1.endpoints.memories.get_async_db')
def test_list_memories_with_data(mock_get_db, mock_get_current_user):
    """Test GET /memories/ endpoint with mock data."""
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
            content=f"Test content {i}",
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
        mock_repo.get_memories_by_user_id.return_value = (mock_memories, len(mock_memories))
        
        # Create a test client for FastAPI app
        test_client = TestClient(app)
        
        try:
            # Use the correct endpoint path
            endpoint = "/api/v1/memories/"
            
            # Make the request
            response = test_client.get(endpoint)
            
            # Print response for debugging
            print(f"\nResponse status: {response.status_code}")
            print(f"Response body: {response.json() if response.status_code == 200 else response.text}")
            
            # Assert the response
            assert response.status_code == 200
            assert "items" in response.json()
            assert len(response.json()["items"]) == 3
            assert response.json()["total"] == 3
            
            # Verify memory data is correctly returned
            for i, memory in enumerate(response.json()["items"]):
                assert memory["title"] == f"Test Memory {i}"
                assert memory["content"] == f"Test content {i}"
                assert "test" in memory["tags"]
                assert f"tag{i}" in memory["tags"]
            
            # Verify the mock was called with correct parameters
            mock_repo.get_memories_by_user_id.assert_called_once_with(
                str(get_test_user().id),
                limit=10,
                offset=0,
                include_inactive=False
            )
        except Exception as e:
            print(f"\n\nEXCEPTION DETAILS: {type(e).__name__}: {str(e)}")
            print("\nTRACEBACK:")
            traceback.print_exc()
            raise

@patch('app.api.v1.endpoints.memories.get_current_user', return_value=get_test_user())
@patch('app.api.v1.endpoints.memories.get_async_db')
def test_list_memories_with_pagination(mock_get_db, mock_get_current_user):
    """Test GET /memories/ endpoint with pagination parameters."""
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
            content=f"Test content {i}",
            tags=["test", f"tag{i}"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True,
            importance_score=0.5,
            source="test"
        )
        for i in range(2)
    ]
    
    # Mock the repository method to return mock memories
    with patch('app.api.v1.endpoints.memories.MemoryRepository') as mock_repo_class:
        mock_repo = mock_repo_class.return_value
        mock_repo.get_memories_by_user_id.return_value = (mock_memories, 20)  # 20 total, 2 returned
        
        # Create a test client for FastAPI app
        test_client = TestClient(app)
        
        try:
            # Use the correct endpoint path with pagination
            endpoint = "/api/v1/memories/?limit=5&offset=10"
            
            # Make the request
            response = test_client.get(endpoint)
            
            # Print response for debugging
            print(f"\nResponse status: {response.status_code}")
            print(f"Response body: {response.json() if response.status_code == 200 else response.text}")
            
            # Assert the response
            assert response.status_code == 200
            assert "items" in response.json()
            assert len(response.json()["items"]) == 2
            assert response.json()["total"] == 20
            
            # Verify the mock was called with correct pagination parameters
            mock_repo.get_memories_by_user_id.assert_called_once_with(
                str(get_test_user().id),
                limit=5,
                offset=10,
                include_inactive=False
            )
        except Exception as e:
            print(f"\n\nEXCEPTION DETAILS: {type(e).__name__}: {str(e)}")
            print("\nTRACEBACK:")
            traceback.print_exc()
            raise
