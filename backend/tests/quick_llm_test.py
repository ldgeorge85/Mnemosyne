#!/usr/bin/env python
"""
Quick LLM Integration Test Script

This script performs basic testing of the LLM integration API endpoints
and documents the results for Phase 2.5 testing requirements.
"""
import sys
import os
import json
import requests
from datetime import datetime
import uuid

# Configuration
API_BASE = "http://localhost:8000"
API_VERSION = "v1"
HEADERS = {"Content-Type": "application/json", "Authorization": "Bearer test-token"}
TEST_USER_ID = "test-user-1"  # Replace with a valid user ID if needed
TEST_CONVERSATION_ID = str(uuid.uuid4())  # Generate a random conversation ID for tests

# Define test cases
def test_chat_completion():
    """Test the chat completion API."""
    print("\n💬 Testing chat completion API...")
    url = f"{API_BASE}/api/{API_VERSION}/llm/chat/completions"
    
    test_request = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, who are you?"}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    try:
        response = requests.post(url, json=test_request, headers=HEADERS)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Chat completion response: {result.get('content', 'No content')[:100]}...")
            return True
        else:
            print(f"Failed to get chat completion: {response.text}")
            return False
    except Exception as e:
        print(f"Error during chat completion: {str(e)}")
        return False

def test_structured_output():
    """Test the structured output API."""
    print("\n🔄 Testing structured output generation...")
    url = f"{API_BASE}/api/{API_VERSION}/parsers/generate-structured"
    
    test_request = {
        "prompt": "List three popular programming languages with their use cases",
        "schema": {
            "languages": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "language": {"type": "string"},
                        "use_case": {"type": "string"}
                    }
                }
            }
        },
        "model": "gpt-3.5-turbo",
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, json=test_request, headers=HEADERS)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Structured output: {json.dumps(result, indent=2)[:100]}...")
            return True
        else:
            print(f"Failed to get structured output: {response.text}")
            return False
    except Exception as e:
        print(f"Error during structured output generation: {str(e)}")
        return False

def test_function_calling():
    """Test the function calling API."""
    print("\n🔧 Testing function calling...")
    url = f"{API_BASE}/api/{API_VERSION}/functions/call"
    
    # New OpenAI format for function calling (v1.0+)
    test_request = {
        "messages": [
            {"role": "user", "content": "What's the weather like in San Francisco?"}
        ],
        "tools": [{
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "The city and state, e.g. San Francisco, CA"}
                    },
                    "required": ["location"]
                }
            }
        }],
        "tool_choice": "auto"
    }
    
    try:
        response = requests.post(url, json=test_request, headers=HEADERS)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Function calling response: {json.dumps(result, indent=2)[:100]}...")
            return True
        else:
            print(f"Failed to call function: {response.text}")
            return False
    except Exception as e:
        print(f"Error during function calling: {str(e)}")
        return False

def test_streaming():
    """Test the streaming API."""
    print("\n🔄 Testing streaming API...")
    url = f"{API_BASE}/api/{API_VERSION}/streaming/llm"
    
    test_request = {
        "conversation_id": TEST_CONVERSATION_ID,  # Required parameter
        "message_content": "Tell me about artificial intelligence",  # Required parameter
        "user_id": TEST_USER_ID,  # Required parameter
        "max_tokens": 100,
        "temperature": 0.7,
        "stream": True
    }
    
    try:
        print("Note: Stream response cannot be fully displayed here")
        print("Sending request to streaming endpoint...")
        # We don't actually process the streaming response here as it requires SSE handling
        response = requests.post(url, json=test_request, headers=HEADERS, stream=True)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("Streaming endpoint responded successfully")
            response.close()  # Close the connection without reading all data
            return True
        else:
            print(f"Failed to access streaming endpoint: {response.text}")
            return False
    except Exception as e:
        print(f"Error during streaming test: {str(e)}")
        return False

def run_all_tests():
    """Run all LLM integration tests and collate results."""
    print("=" * 50)
    print("LLM INTEGRATION TEST SUITE")
    print("=" * 50)
    
    results = {
        "chat_completion": False,
        "structured_output": False,
        "function_calling": False,
        "streaming": False,
        "timestamp": datetime.now().isoformat(),
    }
    
    # Run all tests
    results["chat_completion"] = test_chat_completion()
    results["structured_output"] = test_structured_output()
    results["function_calling"] = test_function_calling()
    results["streaming"] = test_streaming()
    
    # Print overall results
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    
    for test_name, passed in results.items():
        if test_name != "timestamp":
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    # Save results to local file (not in container)
    try:
        results_file = "llm_test_results.json"
        
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to: {results_file}")
    except Exception as e:
        print(f"Could not save results file: {str(e)}")
    
    return results

if __name__ == "__main__":
    run_all_tests()
