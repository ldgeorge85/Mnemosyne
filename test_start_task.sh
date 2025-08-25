#!/bin/bash

# Get token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123", "method": "static"}' | jq -r '.access_token')

echo "Token: ${TOKEN:0:30}..."

# Create a task first
echo "Creating task..."
CREATE_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/tasks/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task for starting"}')

TASK_ID=$(echo $CREATE_RESPONSE | jq -r '.task.id')
echo "Created task: $TASK_ID"

# Start the task
echo -e "\nStarting task..."
START_RESPONSE=$(curl -s -X PATCH "http://localhost:8000/api/v1/tasks/${TASK_ID}/start" \
  -H "Authorization: Bearer $TOKEN")

echo "Start response:"
echo $START_RESPONSE | python3 -m json.tool