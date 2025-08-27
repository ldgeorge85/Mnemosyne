#!/bin/bash
# Test Mirror Persona Mode

API_URL="http://localhost:8000/api/v1"
echo "Testing Mirror Persona Mode..."

# First, authenticate
echo -e "\n1. Authenticating..."
AUTH_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpass123")

TOKEN=$(echo $AUTH_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "❌ Authentication failed"
  echo "Response: $AUTH_RESPONSE"
  exit 1
else
  echo "✅ Authentication successful"
fi

# Test getting available modes
echo -e "\n2. Getting available persona modes..."
MODES_RESPONSE=$(curl -s -X GET "$API_URL/persona/modes" \
  -H "Authorization: Bearer $TOKEN")

if echo "$MODES_RESPONSE" | grep -q "mirror"; then
  echo "✅ Mirror mode found in available modes"
else
  echo "❌ Mirror mode not found"
  echo "Response: $MODES_RESPONSE"
fi

# Test switching to Mirror mode
echo -e "\n3. Switching to Mirror mode..."
SWITCH_RESPONSE=$(curl -s -X POST "$API_URL/persona/mode/switch" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "mirror",
    "reason": "Testing pattern reflection"
  }')

if echo "$SWITCH_RESPONSE" | grep -q "mirror"; then
  echo "✅ Successfully switched to Mirror mode"
  echo "Response: $SWITCH_RESPONSE"
else
  echo "❌ Failed to switch to Mirror mode"
  echo "Response: $SWITCH_RESPONSE"
fi

# Test chat with Mirror mode
echo -e "\n4. Testing chat in Mirror mode..."
CHAT_RESPONSE=$(curl -s -X POST "$API_URL/chat_llm/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "I always tend to make decisions quickly without thinking them through. I notice this pattern recurring in my behavior."}
    ],
    "persona_mode": "mirror"
  }')

if [ ! -z "$CHAT_RESPONSE" ]; then
  echo "✅ Chat response received in Mirror mode"
  echo "Response (truncated): $(echo $CHAT_RESPONSE | head -c 200)..."
else
  echo "❌ No chat response received"
fi

# Test getting pattern reflections
echo -e "\n5. Getting pattern reflections..."
REFLECTIONS_RESPONSE=$(curl -s -X GET "$API_URL/persona/mirror/reflections" \
  -H "Authorization: Bearer $TOKEN")

if echo "$REFLECTIONS_RESPONSE" | grep -q "reflections"; then
  echo "✅ Pattern reflections retrieved"
  echo "Response: $REFLECTIONS_RESPONSE"
else
  echo "❌ Failed to get reflections"
  echo "Response: $REFLECTIONS_RESPONSE"
fi

# Test resetting observations
echo -e "\n6. Testing reset of Mirror observations..."
RESET_RESPONSE=$(curl -s -X POST "$API_URL/persona/mirror/reset" \
  -H "Authorization: Bearer $TOKEN")

if echo "$RESET_RESPONSE" | grep -q "success"; then
  echo "✅ Mirror observations reset successfully"
else
  echo "❌ Failed to reset observations"
  echo "Response: $RESET_RESPONSE"
fi

# Test persona state
echo -e "\n7. Getting persona state..."
STATE_RESPONSE=$(curl -s -X GET "$API_URL/persona/state" \
  -H "Authorization: Bearer $TOKEN")

echo "Persona State: $STATE_RESPONSE"

echo -e "\n✨ Mirror Mode Testing Complete!"