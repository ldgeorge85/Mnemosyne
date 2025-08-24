#!/bin/bash

echo "Simple Memory CRUD Test"

# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123", "method": "static"}' | jq -r '.access_token')

echo "1. CREATE Memory..."
MEMORY=$(curl -s -X POST http://localhost:8000/api/v1/memories/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Simple Test",
    "content": "Testing CRUD",
    "user_id": "11111111-1111-1111-1111-111111111111",
    "importance": 0.5
  }')

MEMORY_ID=$(echo "$MEMORY" | jq -r '.id // empty')
if [ -n "$MEMORY_ID" ]; then
    echo "✓ Created: $MEMORY_ID"
else
    echo "✗ Create failed"
    echo "$MEMORY" | jq
fi

echo ""
echo "2. LIST Memories..."
LIST=$(curl -s http://localhost:8000/api/v1/memories/ \
  -H "Authorization: Bearer $TOKEN")
COUNT=$(echo "$LIST" | jq 'length // 0')
echo "✓ Found $COUNT memories"

echo ""
echo "3. GET Memory by ID..."
GET=$(curl -s "http://localhost:8000/api/v1/memories/$MEMORY_ID" \
  -H "Authorization: Bearer $TOKEN")
TITLE=$(echo "$GET" | jq -r '.title // empty')
if [ -n "$TITLE" ]; then
    echo "✓ Retrieved: $TITLE"
else
    echo "✗ Get failed"
    echo "$GET" | jq
fi

echo ""
echo "4. UPDATE Memory..."
UPDATE=$(curl -s -X PUT "http://localhost:8000/api/v1/memories/$MEMORY_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title", "importance": 0.9}')
NEW_TITLE=$(echo "$UPDATE" | jq -r '.title // empty')
if [ "$NEW_TITLE" = "Updated Title" ]; then
    echo "✓ Updated successfully"
else
    echo "✗ Update failed"
    echo "$UPDATE" | jq
fi

echo ""
echo "5. DELETE Memory..."
DELETE=$(curl -s -X DELETE "http://localhost:8000/api/v1/memories/$MEMORY_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nSTATUS:%{http_code}")
STATUS=$(echo "$DELETE" | grep "STATUS:" | cut -d: -f2)
if [ "$STATUS" = "204" ]; then
    echo "✓ Deleted successfully"
else
    echo "✗ Delete failed: $STATUS"
fi