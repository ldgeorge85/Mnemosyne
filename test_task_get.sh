#!/bin/bash

# Get token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123", "method": "static"}' | jq -r '.access_token')

echo "Testing GET /api/v1/tasks/..."
curl -s -w "\nHTTP_STATUS:%{http_code}" -X GET "http://localhost:8000/api/v1/tasks/" \
  -H "Authorization: Bearer $TOKEN" | tail -1