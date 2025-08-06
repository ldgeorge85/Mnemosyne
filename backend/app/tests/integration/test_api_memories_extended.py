"""
Integration tests for Memory API endpoints.
"""
import pytest
from fastapi import status
from app.tests.fixtures.test_data import create_test_memory, create_test_user

@pytest.mark.asyncio
async def test_create_memory(client, auth_headers):
    """
    Test creating a new memory through the API.
    """
    # Arrange
    memory_data = {
        "title": "Test Memory from API",
        "content": "This is a test memory created through the API",
        "tags": ["test", "api", "integration"],
        "importance_score": 0.85,
        "source": "api_test"
    }
    
    # Act
    response = await client.post(
        "/api/v1/memories/",
        json=memory_data,
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == memory_data["title"]
    assert data["content"] == memory_data["content"]
    assert set(data["tags"]) == set(memory_data["tags"])
    assert data["id"] is not None

@pytest.mark.asyncio
async def test_get_memories(client, auth_headers):
    """
    Test retrieving all memories through the API.
    """
    # Act
    response = await client.get(
        "/api/v1/memories/",
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    assert "total" in data
    assert isinstance(data["total"], int)

@pytest.mark.asyncio
async def test_get_memory_by_id(client, auth_headers, db_session):
    """
    Test retrieving a specific memory by ID through the API.
    """
    # Arrange - Create a test memory in the database
    from app.models.memory import Memory
    from app.models.user import User
    import uuid
    
    # Create test user if not exists
    user_data = create_test_user()
    user = await db_session.query(User).filter(User.id == user_data["id"]).first()
    if not user:
        user = User(
            id=user_data["id"],
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            is_active=user_data["is_active"],
            is_superuser=user_data["is_superuser"]
        )
        db_session.add(user)
        await db_session.commit()
    
    # Create test memory
    memory_data = create_test_memory()
    memory = Memory(
        id=str(uuid.uuid4()),  # Generate a new UUID
        title=memory_data["title"],
        content=memory_data["content"],
        tags=memory_data["tags"],
        user_id=user_data["id"],
        importance_score=memory_data["importance_score"],
        source=memory_data["source"]
    )
    db_session.add(memory)
    await db_session.commit()
    await db_session.refresh(memory)
    
    # Act
    response = await client.get(
        f"/api/v1/memories/{memory.id}",
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == memory.id
    assert data["title"] == memory.title
    assert data["content"] == memory.content
    
    # Cleanup
    await db_session.delete(memory)
    await db_session.commit()

@pytest.mark.asyncio
async def test_update_memory(client, auth_headers, db_session):
    """
    Test updating a memory through the API.
    """
    # Arrange - Create a test memory in the database
    from app.models.memory import Memory
    from app.models.user import User
    import uuid
    
    # Create test user if not exists
    user_data = create_test_user()
    user = await db_session.query(User).filter(User.id == user_data["id"]).first()
    if not user:
        user = User(
            id=user_data["id"],
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            is_active=user_data["is_active"],
            is_superuser=user_data["is_superuser"]
        )
        db_session.add(user)
        await db_session.commit()
    
    # Create test memory
    memory_data = create_test_memory()
    memory = Memory(
        id=str(uuid.uuid4()),  # Generate a new UUID
        title=memory_data["title"],
        content=memory_data["content"],
        tags=memory_data["tags"],
        user_id=user_data["id"],
        importance_score=memory_data["importance_score"],
        source=memory_data["source"]
    )
    db_session.add(memory)
    await db_session.commit()
    await db_session.refresh(memory)
    
    # Updated data
    updated_data = {
        "title": "Updated Memory Title",
        "content": "This is the updated content for the memory",
        "tags": ["updated", "test", "api"],
        "importance_score": 0.95
    }
    
    # Act
    response = await client.put(
        f"/api/v1/memories/{memory.id}",
        json=updated_data,
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == memory.id
    assert data["title"] == updated_data["title"]
    assert data["content"] == updated_data["content"]
    assert set(data["tags"]) == set(updated_data["tags"])
    assert data["importance_score"] == updated_data["importance_score"]
    
    # Cleanup
    await db_session.delete(memory)
    await db_session.commit()

@pytest.mark.asyncio
async def test_delete_memory(client, auth_headers, db_session):
    """
    Test deleting a memory through the API.
    """
    # Arrange - Create a test memory in the database
    from app.models.memory import Memory
    from app.models.user import User
    import uuid
    
    # Create test user if not exists
    user_data = create_test_user()
    user = await db_session.query(User).filter(User.id == user_data["id"]).first()
    if not user:
        user = User(
            id=user_data["id"],
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            is_active=user_data["is_active"],
            is_superuser=user_data["is_superuser"]
        )
        db_session.add(user)
        await db_session.commit()
    
    # Create test memory
    memory_data = create_test_memory()
    memory = Memory(
        id=str(uuid.uuid4()),  # Generate a new UUID
        title=memory_data["title"],
        content=memory_data["content"],
        tags=memory_data["tags"],
        user_id=user_data["id"],
        importance_score=memory_data["importance_score"],
        source=memory_data["source"]
    )
    db_session.add(memory)
    await db_session.commit()
    await db_session.refresh(memory)
    
    # Act
    response = await client.delete(
        f"/api/v1/memories/{memory.id}",
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify memory is deleted
    check_response = await client.get(
        f"/api/v1/memories/{memory.id}",
        headers=auth_headers
    )
    assert check_response.status_code == status.HTTP_404_NOT_FOUND
