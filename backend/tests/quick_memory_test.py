#!/usr/bin/env python
"""
Quick Memory System Test Script

This script performs basic testing of the memory system API endpoints
and documents the results for Phase 2.5 testing requirements.
"""
import sys
import os
import json
import requests
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8000"
API_VERSION = "v1"
# Include Authorization header with a dummy token to trigger the mock auth system
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer dummy-token"  # Any token will work in the dev environment
}
# Use the mock user ID that matches the authentication system
TEST_USER_ID = "mock-user-id"  # This matches the ID returned by get_current_user

# Define test cases
def test_memory_creation():
    """Test creating a new memory."""
    print("\n📝 Testing memory creation...")
    url = f"{API_BASE}/api/{API_VERSION}/memories/"
    
    test_memory = {
        "user_id": TEST_USER_ID,
        "title": f"Test Memory {datetime.now().isoformat()}",
        "content": "This is a test memory created for Phase 2.5 testing.",
        "tags": ["test", "phase2", "memory"],
    }
    
    try:
        response = requests.post(url, json=test_memory, headers=HEADERS)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"Memory created with ID: {result.get('id')}")
            return result.get('id')
        else:
            print(f"Failed to create memory: {response.text}")
            return None
    except Exception as e:
        print(f"Error during memory creation: {str(e)}")
        return None

def test_memory_retrieval():
    """
    Test retrieving a memory by ID.
    This function is self-contained: it creates a new memory, then immediately retrieves it by ID.
    This avoids reliance on external fixtures or test order.
    """
    # Create a new memory to retrieve
    print("\n📝 Creating memory for retrieval test...")
    url_create = f"{API_BASE}/api/{API_VERSION}/memories/"
    test_memory = {
        "user_id": TEST_USER_ID,
        "title": f"Retrieval Test Memory {datetime.now().isoformat()}",
        "content": "This is a retrieval test memory.",
        "tags": ["test", "retrieval"]
    }
    try:
        response = requests.post(url_create, json=test_memory, headers=HEADERS)
        if response.status_code != 201:
            print(f"Failed to create memory for retrieval: {response.text}")
            return False
        memory_id = response.json().get("id")
    except Exception as e:
        print(f"Error during memory creation for retrieval: {str(e)}")
        return False
    
    # Now retrieve the memory by ID
    print(f"\n📚 Testing memory retrieval for ID: {memory_id}")
    url = f"{API_BASE}/api/{API_VERSION}/memories/{memory_id}"
    try:
        response = requests.get(url, headers=HEADERS)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Memory retrieved: {result.get('title')}")
            return True
        else:
            print(f"Failed to retrieve memory: {response.text}")
            return False
    except Exception as e:
        print(f"Error during memory retrieval: {str(e)}")
        return False

def test_memory_search():
    """Test semantic search functionality."""
    print("\n🔍 Testing memory search...")
    url = f"{API_BASE}/api/{API_VERSION}/memories/search"
    
    search_query = {
        "query": "test memory",
        "user_id": TEST_USER_ID,
        "limit": 5,
        "include_chunks": False
    }
    
    try:
        response = requests.post(url, json=search_query, headers=HEADERS)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            memories = result.get("memories", [])
            print(f"Found {len(memories)} memories matching the query")
            
            for idx, memory in enumerate(memories, 1):
                print(f"  {idx}. {memory.get('title')} (score: {memory.get('relevance_score', 'N/A')})")
            
            return True
        else:
            print(f"Failed to search memories: {response.text}")
            return False
    except Exception as e:
        print(f"Error during memory search: {str(e)}")
        return False

def test_memory_statistics():
    """Test memory statistics endpoint."""
    print("\n📊 Testing memory statistics...")
    url = f"{API_BASE}/api/{API_VERSION}/memories/statistics"
    
    try:
        response = requests.get(url, headers=HEADERS)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(json.dumps(result, indent=2))
            return True
        else:
            print(f"Failed to get memory statistics: {response.text}")
            return False
    except Exception as e:
        print(f"Error during memory statistics retrieval: {str(e)}")
        return False

def run_all_tests():
    """Run all memory tests and collate results."""
    print("=" * 50)
    print("MEMORY SYSTEM TEST SUITE")
    print("=" * 50)
    
    results = {
        "creation": False,
        "retrieval": False,
        "search": False,
        "statistics": False,
        "memory_id": None,
        "timestamp": datetime.now().isoformat(),
    }
    
    # Test memory creation
    memory_id = test_memory_creation()
    results["creation"] = bool(memory_id)
    results["memory_id"] = memory_id
    
    # Test memory retrieval if creation succeeded
    if memory_id:
        results["retrieval"] = test_memory_retrieval(memory_id)
    
    # Test memory search
    results["search"] = test_memory_search()
    
    # Test memory statistics
    results["statistics"] = test_memory_statistics()
    
    # Print overall results
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    
    for test_name, passed in results.items():
        if test_name not in ["memory_id", "timestamp"]:
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_name.title()}: {status}")
    
    # Save results to file
    results_file = os.path.join(os.path.dirname(__file__), 
                               "../docs/memory_test_results.json")
    
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    run_all_tests()
