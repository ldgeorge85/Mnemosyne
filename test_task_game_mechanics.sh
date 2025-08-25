#!/bin/bash
# Test script for task game mechanics endpoints

# Get auth token
echo "Getting auth token..."
TOKEN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123", "method": "static"}')

TOKEN=$(echo $TOKEN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "Failed to get auth token. Response: $TOKEN_RESPONSE"
  exit 1
fi

echo "✓ Got auth token: ${TOKEN:0:30}..."

# Create a task with game mechanics
echo -e "\n1. Creating task with game mechanics..."
CREATE_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/tasks/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete code review for task system",
    "description": "Review and test the new task endpoints with game mechanics",
    "priority": "high",
    "difficulty": 3,
    "quest_type": "solo",
    "estimated_duration_minutes": 30,
    "value_impact": {"focus": 0.2, "technical_skill": 0.3},
    "skill_development": {"programming": 10, "system_design": 5},
    "tags": ["development", "testing", "code-review"]
  }')

TASK_ID=$(echo $CREATE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['task']['id'])" 2>/dev/null)

if [ -z "$TASK_ID" ]; then
  echo "Failed to create task. Response: $CREATE_RESPONSE"
  exit 1
fi

echo "✓ Created task with ID: $TASK_ID"

# Start the task
echo -e "\n2. Starting task..."
START_RESPONSE=$(curl -s -X PATCH "http://localhost:8000/api/v1/tasks/${TASK_ID}/start" \
  -H "Authorization: Bearer $TOKEN")

echo "Start response: $(echo $START_RESPONSE | python3 -m json.tool 2>/dev/null | head -5)..."

# Get task stats
echo -e "\n3. Getting task stats..."
STATS_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/tasks/stats" \
  -H "Authorization: Bearer $TOKEN")

echo "Stats response: $(echo $STATS_RESPONSE | python3 -m json.tool 2>/dev/null)"

# Complete the task
echo -e "\n4. Completing task with XP calculation..."
COMPLETE_RESPONSE=$(curl -s -X PATCH "http://localhost:8000/api/v1/tasks/${TASK_ID}/complete" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "evidence": "Reviewed all endpoints and tested functionality",
    "actual_duration_minutes": 25,
    "reflection": "The game mechanics integration works well with the task system"
  }')

echo "Complete response:"
echo $COMPLETE_RESPONSE | python3 -m json.tool 2>/dev/null

# Get updated stats
echo -e "\n5. Getting updated task stats..."
UPDATED_STATS=$(curl -s -X GET "http://localhost:8000/api/v1/tasks/stats" \
  -H "Authorization: Bearer $TOKEN")

echo "Updated stats:"
echo $UPDATED_STATS | python3 -m json.tool 2>/dev/null

echo -e "\n✅ Task game mechanics test complete!"