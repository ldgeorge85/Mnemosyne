# Phase 2.5 Backend API Fixes Implementation Plan

## Current Issues Analysis

After reviewing the code, I've identified the specific causes of the backend API issues:

### 1. Memory Creation (500 Error)
- **Root Cause**: There's a mismatch in the API endpoint code. The handler function uses `current_user_id` as a variable, but the dependency actually returns a dictionary as `current_user`.
- **Fix Required**: Update the references from `current_user_id` to `current_user["id"]` throughout the memories.py file.

### 2. Memory Search (422 Error)
- **Root Cause**: The test script in `quick_memory_test.py` is sending a search query object that's missing the required `user_id` field.
- **Fix Required**: Update the search query object to include the test user ID.

### 3. Memory Statistics (500 Error)
- **Root Cause**: The error "object CursorResult can't be used in 'await' expression" indicates an issue with async handling in the statistics endpoint.
- **Fix Required**: Modify the query execution and result fetching approach to properly handle the async cursor result.

### 4. Docker Compose Warning
- **Root Cause**: Using the deprecated `version` attribute in docker-compose files.
- **Fix Required**: Remove the version attribute from both docker-compose.yml and docker-compose.override.yml.

## Implementation Steps

### 1. Fix Memory API Authentication References

Update all references in memories.py from `current_user_id` to `current_user["id"]`:
- In the create_memory function
- In the get_memory function
- In the list_memories function 
- In the update_memory function
- In the delete_memory function
- In all memory chunk related functions

### 2. Fix Memory Search Test

Update the search_query in quick_memory_test.py to include the user ID:

```python
search_query = {
    "user_id": TEST_USER_ID,
    "query": "test memory",
    "min_relevance_score": 0.5,
    "limit": 5
}
```

### 3. Fix Memory Statistics Implementation

Locate the memory statistics service implementation and modify it to correctly handle async SQL results:

1. Use `.scalars().all()` instead of direct cursor results
2. Ensure proper awaiting of all database operations
3. Replace any direct cursor usage with proper async fetching patterns

### 4. Remove Docker Compose Version Attribute

Remove the version attribute from:
- docker-compose.yml
- docker-compose.override.yml

## Testing Approach

For each fix:
1. Apply the specific change
2. Run the test script targeting just that endpoint
3. Verify the error is resolved
4. Document the result

Finally, run the complete test script to verify all endpoints work together properly.
