#!/usr/bin/env python3
"""
Test Mirror Persona Mode
"""

import requests
import json
import sys

API_URL = "http://localhost:8000/api/v1"

def test_mirror_mode():
    print("Testing Mirror Persona Mode...")
    
    # 1. Authenticate
    print("\n1. Authenticating...")
    auth_response = requests.post(
        f"{API_URL}/auth/login",
        json={
            "username": "test",
            "password": "test123",
            "method": "static"
        }
    )
    
    if auth_response.status_code != 200:
        print(f"❌ Authentication failed: {auth_response.text}")
        return
    
    token = auth_response.json().get("access_token")
    if not token:
        print("❌ No token received")
        return
    
    print("✅ Authentication successful")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Get available modes
    print("\n2. Getting available persona modes...")
    modes_response = requests.get(f"{API_URL}/persona/modes", headers=headers)
    
    if modes_response.status_code == 200:
        modes = modes_response.json()
        mirror_found = any(m["mode"] == "mirror" for m in modes.get("modes", []))
        if mirror_found:
            print("✅ Mirror mode found in available modes")
        else:
            print("❌ Mirror mode not found")
    else:
        print(f"❌ Failed to get modes: {modes_response.text}")
    
    # 3. Switch to Mirror mode
    print("\n3. Switching to Mirror mode...")
    switch_response = requests.post(
        f"{API_URL}/persona/mode/switch",
        headers=headers,
        json={
            "mode": "mirror",
            "reason": "Testing pattern reflection"
        }
    )
    
    if switch_response.status_code == 200:
        result = switch_response.json()
        if result.get("current_mode") == "mirror":
            print(f"✅ Successfully switched to Mirror mode")
            print(f"   Greeting: {result.get('greeting')}")
        else:
            print(f"❌ Mode is {result.get('current_mode')}, not mirror")
    else:
        print(f"❌ Failed to switch: {switch_response.text}")
    
    # 4. Test chat with Mirror mode
    print("\n4. Testing chat in Mirror mode...")
    chat_response = requests.post(
        f"{API_URL}/chat/chat",
        headers=headers,
        json={
            "messages": [
                {
                    "role": "user",
                    "content": "I always tend to make decisions quickly without thinking them through. I notice this pattern recurring in my behavior."
                }
            ],
            "persona_mode": "mirror"
        }
    )
    
    if chat_response.status_code == 200:
        print("✅ Chat response received in Mirror mode")
        result = chat_response.json()
        if result.get("choices"):
            content = result["choices"][0].get("message", {}).get("content", "")
            print(f"   Response preview: {content[:200]}...")
    else:
        print(f"❌ Chat failed: {chat_response.text}")
    
    # 5. Get pattern reflections
    print("\n5. Getting pattern reflections...")
    reflections_response = requests.get(
        f"{API_URL}/persona/mirror/reflections",
        headers=headers
    )
    
    if reflections_response.status_code == 200:
        reflections = reflections_response.json()
        print(f"✅ Pattern reflections retrieved")
        print(f"   Observation count: {reflections.get('observation_count', 0)}")
        print(f"   Reflections: {reflections.get('reflections', [])}")
        print(f"   Patterns observed: {reflections.get('patterns_observed', [])}")
    else:
        print(f"❌ Failed to get reflections: {reflections_response.text}")
    
    # 6. Reset observations
    print("\n6. Testing reset of Mirror observations...")
    reset_response = requests.post(
        f"{API_URL}/persona/mirror/reset",
        headers=headers
    )
    
    if reset_response.status_code == 200:
        print("✅ Mirror observations reset successfully")
    else:
        print(f"❌ Failed to reset: {reset_response.text}")
    
    # 7. Get persona state
    print("\n7. Getting persona state...")
    state_response = requests.get(f"{API_URL}/persona/state", headers=headers)
    
    if state_response.status_code == 200:
        state = state_response.json()
        print(f"✅ Persona state retrieved")
        print(f"   Current mode: {state.get('current_mode')}")
        print(f"   Trust level: {state.get('trust_level')}")
        print(f"   Mode history count: {state.get('mode_history_count')}")
    else:
        print(f"❌ Failed to get state: {state_response.text}")
    
    print("\n✨ Mirror Mode Testing Complete!")

if __name__ == "__main__":
    test_mirror_mode()