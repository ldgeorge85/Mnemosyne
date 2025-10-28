#!/usr/bin/env python3
"""
Simple test of negotiation endpoints without authentication
"""

import requests
import json
from datetime import datetime, timedelta
from uuid import uuid4

BASE_URL = "http://localhost:8000/api/v1"

print("=" * 60)
print("TESTING MULTI-PARTY NEGOTIATION ENDPOINTS")
print("=" * 60)

# Test data
alice_id = str(uuid4())
bob_id = str(uuid4())

print(f"\nTest participants:")
print(f"  Alice ID: {alice_id}")
print(f"  Bob ID: {bob_id}")

# Step 1: Create a negotiation
print("\n1. Creating negotiation...")

negotiation_data = {
    "title": "Test Trust Resolution",
    "description": "Testing multi-party negotiation system",
    "initiator_id": alice_id,
    "participant_ids": [alice_id, bob_id],
    "initial_terms": {
        "issue": "Trust violation",
        "resolution": "Needs agreement"
    },
    "negotiation_deadline": (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z",
    "required_consensus_count": 2
}

try:
    response = requests.post(f"{BASE_URL}/negotiations", json=negotiation_data)
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        negotiation_id = result.get("id")
        print(f"   ✓ Negotiation created: {negotiation_id}")
        print(f"   Current status: {result.get('status')}")
    else:
        print(f"   ✗ Error: {response.text[:200]}")
        negotiation_id = None

except Exception as e:
    print(f"   ✗ Failed: {e}")
    negotiation_id = None

# Step 2: Get negotiation details
if negotiation_id:
    print("\n2. Getting negotiation details...")

    try:
        response = requests.get(f"{BASE_URL}/negotiations/{negotiation_id}")
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"   ✓ Status: {result.get('status')}")
            print(f"   ✓ Participants: {len(result.get('participant_ids', []))}")
            print(f"   ✓ Current terms version: {result.get('terms_version')}")
        else:
            print(f"   ✗ Error: {response.text[:200]}")

    except Exception as e:
        print(f"   ✗ Failed: {e}")

# Step 3: Test join endpoint
if negotiation_id:
    print("\n3. Testing join endpoint (Bob joins)...")

    try:
        response = requests.post(
            f"{BASE_URL}/negotiations/{negotiation_id}/join",
            json={"participant_id": bob_id}
        )
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            print(f"   ✓ Bob joined negotiation")
        else:
            print(f"   ✗ Error: {response.text[:200]}")

    except Exception as e:
        print(f"   ✗ Failed: {e}")

# Step 4: List all negotiations
print("\n4. Listing negotiations...")

try:
    response = requests.get(f"{BASE_URL}/negotiations")
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        results = response.json()
        if isinstance(results, list):
            print(f"   ✓ Found {len(results)} negotiation(s)")
        else:
            print(f"   ✓ Response received")
    else:
        print(f"   ✗ Error: {response.text[:200]}")

except Exception as e:
    print(f"   ✗ Failed: {e}")

print("\n" + "=" * 60)
print("ENDPOINT TEST COMPLETE")
print("=" * 60)

if negotiation_id:
    print(f"\n📝 Created negotiation ID: {negotiation_id}")
    print("   You can use this ID to test other endpoints manually")