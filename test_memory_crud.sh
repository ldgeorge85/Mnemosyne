#!/bin/bash

echo "Testing Memory CRUD operations..."

# 1. Login
echo "1. Getting auth token..."
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123", "method": "static"}' | jq -r '.access_token')

echo "Token: ${TOKEN:0:20}..."

# 2. Create a memory
echo -e "\n2. Creating a memory..."
MEMORY_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/memories/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Memory",
    "content": "This is a test memory created via the API. It contains important information about testing the memory system.",
    "user_id": "11111111-1111-1111-1111-111111111111",
    "source": "api_test",
    "source_type": "test",
    "tags": ["test", "api", "memory"],
    "metadata": {"test": true, "timestamp": "2025-08-22"},
    "importance": 0.7
  }')

echo "Response:"
echo "$MEMORY_RESPONSE" | jq

# Extract memory ID if created successfully
MEMORY_ID=$(echo "$MEMORY_RESPONSE" | jq -r '.id // empty')

if [ -n "$MEMORY_ID" ]; then
    echo "✓ Memory created with ID: $MEMORY_ID"
    
    # 3. Get the memory by ID
    echo -e "\n3. Getting memory by ID..."
    curl -s "http://localhost:8000/api/v1/memories/$MEMORY_ID" \
      -H "Authorization: Bearer $TOKEN" | jq
    
    # 4. List all memories
    echo -e "\n4. Listing all memories..."
    curl -s http://localhost:8000/api/v1/memories/ \
      -H "Authorization: Bearer $TOKEN" | jq
    
    # 5. Update the memory
    echo -e "\n5. Updating the memory..."
    UPDATE_RESPONSE=$(curl -s -X PUT "http://localhost:8000/api/v1/memories/$MEMORY_ID" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "title": "Updated Test Memory",
        "importance": 0.9,
        "tags": ["test", "api", "memory", "updated"]
      }')
    
    echo "Update response:"
    echo "$UPDATE_RESPONSE" | jq
    
    # 6. Soft delete the memory
    echo -e "\n6. Soft deleting the memory..."
    curl -s -X DELETE "http://localhost:8000/api/v1/memories/$MEMORY_ID" \
      -H "Authorization: Bearer $TOKEN" \
      -w "\nHTTP Status: %{http_code}\n"
    
    # 7. Try to get deleted memory (should fail or show inactive)
    echo -e "\n7. Trying to get deleted memory..."
    curl -s "http://localhost:8000/api/v1/memories/$MEMORY_ID" \
      -H "Authorization: Bearer $TOKEN" | jq
else
    echo "✗ Failed to create memory"
fi

echo -e "\nMemory CRUD test complete!"