#!/bin/bash

echo "Testing memory endpoints..."

# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123", "method": "static"}' | jq -r '.access_token')

echo "Token obtained: ${TOKEN:0:20}..."

# 2. Test GET memories
echo "Testing GET /api/v1/memories/..."
curl -s http://localhost:8000/api/v1/memories/ \
  -H "Authorization: Bearer $TOKEN" | jq