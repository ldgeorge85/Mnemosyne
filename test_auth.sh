#!/bin/bash

echo "Testing authentication flow..."

# 1. Login
echo "1. Testing login..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123", "method": "static"}')

TOKEN=$(echo $RESPONSE | jq -r '.access_token')

if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
    echo "✓ Login successful"
    echo "  Token: ${TOKEN:0:20}..."
else
    echo "✗ Login failed"
    echo "  Response: $RESPONSE"
    exit 1
fi

# 2. Get user info
echo ""
echo "2. Testing /auth/me endpoint..."
USER_RESPONSE=$(curl -s http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN")

USERNAME=$(echo $USER_RESPONSE | jq -r '.username // .data.username // empty')

if [ -n "$USERNAME" ]; then
    echo "✓ User info retrieved"
    echo "  Username: $USERNAME"
    echo $USER_RESPONSE | jq
else
    echo "✗ Failed to get user info"
    echo "  Response: $USER_RESPONSE"
    exit 1
fi

# 3. Test protected endpoint
echo ""
echo "3. Testing protected endpoint (memories)..."
MEMORIES_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" http://localhost:8000/api/v1/memories/ \
  -H "Authorization: Bearer $TOKEN")

HTTP_STATUS=$(echo "$MEMORIES_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
BODY=$(echo "$MEMORIES_RESPONSE" | grep -v "HTTP_STATUS")

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✓ Protected endpoint accessible"
    echo "  Response: $BODY" | head -1
else
    echo "✗ Protected endpoint returned status $HTTP_STATUS"
    echo "  Response: $BODY"
fi

# 4. Test logout
echo ""
echo "4. Testing logout..."
LOGOUT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{}")

echo "✓ Logout request sent"

# 5. Verify token is invalid after logout
echo ""
echo "5. Verifying token is invalid after logout..."
INVALID_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN")

HTTP_STATUS=$(echo "$INVALID_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

if [ "$HTTP_STATUS" = "401" ]; then
    echo "✓ Token correctly invalidated"
else
    echo "⚠ Token may still be valid (status: $HTTP_STATUS)"
fi

echo ""
echo "Authentication flow test complete!"