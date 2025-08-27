#!/bin/bash
# Test Trust System Endpoints

API_URL="http://localhost:8000/api/v1"
echo "Testing Trust System Endpoints..."

# First, we need to authenticate (using the test user)
echo -e "\n1. Testing Authentication..."
AUTH_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpass123")

if [ -z "$AUTH_RESPONSE" ]; then
  echo "❌ Authentication failed - no response"
  exit 1
fi

TOKEN=$(echo $AUTH_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "❌ No token received"
  echo "Response: $AUTH_RESPONSE"
else
  echo "✅ Authentication successful"
fi

# Test trust event creation
echo -e "\n2. Testing Trust Event Creation..."
TRUST_EVENT=$(curl -s -X POST "$API_URL/trust/event" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "actor_id": "00000000-0000-0000-0000-000000000001",
    "subject_id": "00000000-0000-0000-0000-000000000002",
    "event_type": "interaction",
    "trust_delta": 0.1,
    "context": {"type": "collaboration"},
    "visibility_scope": "private",
    "user_consent": true
  }')

if echo "$TRUST_EVENT" | grep -q "trust_event_id"; then
  echo "✅ Trust event created successfully"
else
  echo "❌ Trust event creation failed"
  echo "Response: $TRUST_EVENT"
fi

# Test trust relationships
echo -e "\n3. Testing Trust Relationships..."
RELATIONSHIPS=$(curl -s -X GET "$API_URL/trust/relationships" \
  -H "Authorization: Bearer $TOKEN")

if [ ! -z "$RELATIONSHIPS" ]; then
  echo "✅ Trust relationships endpoint working"
  echo "Response: $RELATIONSHIPS"
else
  echo "❌ Trust relationships endpoint failed"
fi

# Test consciousness pattern opt-in
echo -e "\n4. Testing Consciousness Pattern Opt-in..."
OPT_IN=$(curl -s -X POST "$API_URL/trust/patterns/opt-in" \
  -H "Authorization: Bearer $TOKEN")

if echo "$OPT_IN" | grep -q "status"; then
  echo "✅ Consciousness tracking opt-in successful"
  echo "Response: $OPT_IN"
else
  echo "❌ Consciousness tracking opt-in failed"
fi

# Test pattern retrieval
echo -e "\n5. Testing Pattern Retrieval..."
PATTERNS=$(curl -s -X GET "$API_URL/trust/patterns" \
  -H "Authorization: Bearer $TOKEN")

if [ ! -z "$PATTERNS" ]; then
  echo "✅ Pattern retrieval working"
  echo "Response: $PATTERNS"
else
  echo "❌ Pattern retrieval failed"
fi

echo -e "\n✨ Trust System Testing Complete!"