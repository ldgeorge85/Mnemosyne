#!/bin/bash

echo "1. Getting token..."
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123", "method": "static"}' | jq -r '.access_token')

echo "Token: ${TOKEN:0:50}..."

echo -e "\n2. Testing auth with /auth/me..."
curl -s "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN" | jq '.username'

echo -e "\n3. Creating task..."
RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "http://localhost:8000/api/v1/tasks/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "description": "Testing"}')

HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | grep -v "HTTP_STATUS")

echo "HTTP Status: $HTTP_STATUS"
echo "Response body:"
echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"