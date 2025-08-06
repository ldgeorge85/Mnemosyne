"""
Test data fixtures for backend tests.
"""
from datetime import datetime
from uuid import uuid4

# Memory fixtures
def create_test_memory():
    """
    Create a test memory object with default values.
    
    Returns:
        dict: A dictionary representing a memory object
    """
    return {
        "id": str(uuid4()),
        "title": "Test Memory",
        "content": "This is a test memory content",
        "tags": ["test", "fixture"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "user_id": "test-user-id",
        "importance_score": 0.75,
        "source": "test_fixture"
    }

# Agent fixtures
def create_test_agent():
    """
    Create a test agent object with default values.
    
    Returns:
        dict: A dictionary representing an agent object
    """
    return {
        "id": str(uuid4()),
        "name": "Test Agent",
        "role": "assistant",
        "description": "A test agent for unit tests",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "user_id": "test-user-id",
        "status": "active",
        "capabilities": ["memory_access", "task_execution"]
    }

# Conversation fixtures
def create_test_conversation():
    """
    Create a test conversation object with default values.
    
    Returns:
        dict: A dictionary representing a conversation object
    """
    return {
        "id": str(uuid4()),
        "title": "Test Conversation",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "user_id": "test-user-id",
        "messages": []
    }

# Task fixtures
def create_test_task():
    """
    Create a test task object with default values.
    
    Returns:
        dict: A dictionary representing a task object
    """
    return {
        "id": str(uuid4()),
        "title": "Test Task",
        "description": "A test task for unit tests",
        "status": "pending",
        "priority": "medium",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "due_date": (datetime.now().replace(hour=23, minute=59, second=59)).isoformat(),
        "user_id": "test-user-id",
        "assigned_agent_id": None
    }

# User fixtures
def create_test_user():
    """
    Create a test user object with default values.
    
    Returns:
        dict: A dictionary representing a user object
    """
    return {
        "id": "test-user-id",
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "is_active": True,
        "is_superuser": False
    }
