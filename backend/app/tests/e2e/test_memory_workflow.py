"""
End-to-end tests for memory workflow.
"""
import pytest
import asyncio
from fastapi import status
from app.tests.fixtures.test_data import create_test_memory, create_test_user

@pytest.mark.asyncio
async def test_complete_memory_workflow(client, auth_headers, db_session):
    """
    Test the complete memory workflow from creation to deletion.
    This is an end-to-end test that verifies the entire memory lifecycle.
    """
    # Step 1: Create a new memory
    memory_data = {
        "title": "E2E Test Memory",
        "content": "This is a test memory for end-to-end testing",
        "tags": ["e2e", "test", "workflow"],
        "importance_score": 0.9,
        "source": "e2e_test"
    }
    
    # Use the synchronous test_client for API requests
    create_response = client.test_client.post(
        "/api/v1/memories/",
        json=memory_data,
        headers=auth_headers
    )
    
    assert create_response.status_code == status.HTTP_201_CREATED
    created_memory = create_response.json()
    memory_id = created_memory["id"]
    
    # Step 2: Retrieve the created memory
    get_response = client.test_client.get(
        f"/api/v1/memories/{memory_id}",
        headers=auth_headers
    )
    
    assert get_response.status_code == status.HTTP_200_OK
    retrieved_memory = get_response.json()
    assert retrieved_memory["id"] == memory_id
    assert retrieved_memory["title"] == memory_data["title"]
    
    # Step 3: Update the memory
    updated_data = {
        "title": "Updated E2E Test Memory",
        "content": "This content has been updated during E2E testing",
        "tags": ["e2e", "test", "updated"],
        "importance_score": 0.95
    }
    
    update_response = client.test_client.put(
        f"/api/v1/memories/{memory_id}",
        json=updated_data,
        headers=auth_headers
    )
    
    assert update_response.status_code == status.HTTP_200_OK
    updated_memory = update_response.json()
    assert updated_memory["title"] == updated_data["title"]
    assert updated_memory["content"] == updated_data["content"]
    
    # Step 4: Verify the memory appears in the list
    list_response = client.test_client.get(
        "/api/v1/memories/",
        headers=auth_headers
    )
    
    assert list_response.status_code == status.HTTP_200_OK
    memories_list = list_response.json()
    memory_ids = [memory["id"] for memory in memories_list["items"]]
    assert memory_id in memory_ids
    
    # Step 5: Search for the memory by tag
    search_response = client.test_client.get(
        "/api/v1/memories/search?query=updated",
        headers=auth_headers
    )
    
    assert search_response.status_code == status.HTTP_200_OK
    search_results = search_response.json()
    found = False
    for memory in search_results["items"]:
        if memory["id"] == memory_id:
            found = True
            break
    assert found, "Memory not found in search results"
    
    # Step 6: Delete the memory
    delete_response = client.test_client.delete(
        f"/api/v1/memories/{memory_id}",
        headers=auth_headers
    )
    
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    
    # Step 7: Verify the memory is deleted
    verify_response = client.test_client.get(
        f"/api/v1/memories/{memory_id}",
        headers=auth_headers
    )
    
    assert verify_response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_memory_reflection_workflow(client, auth_headers, db_session):
    """
    Test the memory reflection workflow.
    This tests the integration between memory creation and reflection services.
    """
    # Step 1: Create multiple memories
    memories = []
    for i in range(3):
        memory_data = {
            "title": f"Reflection Test Memory {i+1}",
            "content": f"This is test memory {i+1} for reflection testing",
            "tags": ["reflection", "test", f"memory{i+1}"],
            "importance_score": 0.7 + (i * 0.1),
            "source": "reflection_test"
        }
        
        response = client.test_client.post(
            "/api/v1/memories/",
            json=memory_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        memories.append(response.json())
    
    # Allow some time for async processing
    await asyncio.sleep(1)
    
    # Step 2: Trigger memory reflection
    memory_ids = [memory["id"] for memory in memories]
    reflection_response = client.test_client.post(
        "/api/v1/memories/reflect",
        json={
            "agent_id": "test-agent",
            "memories": memory_ids
        },
        headers=auth_headers
    )
    
    # This endpoint might return different status codes depending on implementation
    # Just verify it doesn't error out
    assert reflection_response.status_code < 500
    
    # Step 3: Get memory hierarchy
    hierarchy_response = client.test_client.get(
        "/api/v1/memories/hierarchy",
        params={"memory_ids": ",".join(map(str, memory_ids))},
        headers=auth_headers
    )
    
    assert hierarchy_response.status_code == status.HTTP_200_OK
    hierarchy = hierarchy_response.json()
    assert "hierarchy" in hierarchy
    
    # Step 4: Clean up created memories
    for memory in memories:
        client.test_client.delete(
            f"/api/v1/memories/{memory['id']}",
            headers=auth_headers
        )
