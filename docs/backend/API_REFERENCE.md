# Backend API Reference

## Base URL
- Development: `http://localhost:8000/api/v1`
- Production: `https://your-domain.com/api/v1`

## Authentication

All endpoints require authentication unless specified. Include the JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## API Endpoints

### Authentication (`/auth`)

#### POST `/auth/login`
**Public endpoint**

Login with email/username and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "access_token": "jwt-token",
  "refresh_token": "refresh-token",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username"
  }
}
```

#### POST `/auth/register`
**Public endpoint**

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "securepassword"
}
```

#### POST `/auth/refresh`
Refresh access token using refresh token.

#### GET `/auth/me`
Get current authenticated user information.

---

### Memories (`/memories`)

#### POST `/memories`
Create a new memory with automatic embedding generation.

**Request Body:**
```json
{
  "title": "Memory Title",
  "content": "Memory content text",
  "tags": ["tag1", "tag2"],
  "source_type": "manual",
  "importance": 0.8,
  "memory_metadata": {
    "custom": "data"
  }
}
```

**Response:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "Memory Title",
  "content": "Memory content text",
  "embedding_model": "BAAI/bge-m3",
  "embedding_dimension": 1024,
  "tags": ["tag1", "tag2"],
  "importance": 0.8,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

#### GET `/memories`
List user's memories with pagination.

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 20, max: 100)
- `source_type`: Filter by source type
- `tags`: Filter by tags (comma-separated)
- `search`: Text search in title and content

**Response:**
```json
{
  "items": [...],
  "total": 50,
  "skip": 0,
  "limit": 20
}
```

#### GET `/memories/{memory_id}`
Get a specific memory by ID.

#### PUT `/memories/{memory_id}`
Update an existing memory.

**Request Body:**
```json
{
  "title": "Updated Title",
  "content": "Updated content",
  "tags": ["new-tag"],
  "importance": 0.9
}
```

#### DELETE `/memories/{memory_id}`
Delete a memory (soft delete by default).

**Query Parameters:**
- `hard_delete`: Boolean, permanently delete if true

#### POST `/memories/search`
Search memories by text.

**Request Body:**
```json
{
  "query": "search text",
  "limit": 10,
  "source_types": ["manual", "conversation"]
}
```

#### POST `/memories/search/similar`
Find similar memories using vector similarity.

**Request Body:**
```json
{
  "query": "text to find similar memories",
  "limit": 10,
  "threshold": 0.7
}
```

#### GET `/memories/statistics`
Get memory system statistics for the user.

**Response:**
```json
{
  "total_memories": 150,
  "by_source_type": {
    "manual": 50,
    "conversation": 80,
    "task": 20
  },
  "total_chunks": 450,
  "average_importance": 0.65,
  "most_used_tags": ["work", "personal", "ideas"]
}
```

---

### Tasks (`/tasks`)

#### POST `/tasks`
Create a new task.

**Request Body:**
```json
{
  "title": "Task Title",
  "description": "Task description",
  "priority": "medium",
  "status": "pending",
  "due_date": "2025-02-01T00:00:00Z",
  "tags": ["work", "urgent"],
  "difficulty": 3,
  "quest_type": "solo",
  "estimated_duration_minutes": 60,
  "parent_id": null
}
```

**Response:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "Task Title",
  "status": "pending",
  "priority": "medium",
  "difficulty": 3,
  "quest_type": "solo",
  "experience_points": 30,
  "created_at": "2025-01-01T00:00:00Z"
}
```

#### GET `/tasks`
List user's tasks with filtering.

**Query Parameters:**
- `skip`: Number of records to skip
- `limit`: Maximum records to return
- `status`: Filter by status (pending, in_progress, completed)
- `priority`: Filter by priority (low, medium, high, urgent)
- `quest_type`: Filter by quest type
- `tags`: Filter by tags (comma-separated)

#### GET `/tasks/{task_id}`
Get a specific task by ID.

#### PUT `/tasks/{task_id}`
Update a task.

#### DELETE `/tasks/{task_id}`
Delete a task (soft delete).

#### PATCH `/tasks/{task_id}/start`
Mark a task as in progress.

**Response:**
```json
{
  "id": "uuid",
  "status": "in_progress",
  "started_at": "2025-01-01T10:00:00Z"
}
```

#### PATCH `/tasks/{task_id}/complete`
Complete a task and calculate experience points.

**Response:**
```json
{
  "task": {
    "id": "uuid",
    "status": "completed",
    "completed_at": "2025-01-01T11:00:00Z",
    "actual_duration_minutes": 45,
    "experience_points": 35
  },
  "experience_gained": 35,
  "achievements_unlocked": [],
  "level_progress": {
    "current_level": 5,
    "current_xp": 235,
    "next_level_xp": 500
  }
}
```

#### GET `/tasks/stats`
Get task statistics for the user.

**Response:**
```json
{
  "total_tasks": 150,
  "completed_tasks": 100,
  "in_progress_tasks": 10,
  "pending_tasks": 40,
  "total_experience": 3500,
  "average_difficulty": 3.2,
  "completion_rate": 0.67
}
```

#### POST `/tasks/search`
Search tasks by text.

#### GET `/tasks/reminders`
Get upcoming task reminders.

#### GET `/tasks/suggestions`
Get AI-powered task suggestions based on patterns.

---

### Chat (`/chat`)

#### POST `/chat/stream`
Stream chat response from LLM.

**Request Body:**
```json
{
  "message": "User message",
  "conversation_id": "uuid",
  "include_memories": true,
  "temperature": 0.7
}
```

**Response:** Server-sent events stream
```
data: {"token": "Hello", "type": "content"}
data: {"token": " there", "type": "content"}
data: {"type": "done"}
```

#### POST `/chat/message`
Send a chat message (non-streaming).

**Request Body:**
```json
{
  "message": "User message",
  "conversation_id": "uuid",
  "include_memories": true
}
```

**Response:**
```json
{
  "response": "AI response",
  "conversation_id": "uuid",
  "message_id": "uuid",
  "memories_used": ["memory-id-1", "memory-id-2"]
}
```

---

### Agents (`/agents`)

#### GET `/agents`
List available agents.

**Response:**
```json
{
  "agents": [
    {
      "id": "reflection-agent",
      "name": "Reflection Agent",
      "description": "Provides deep insights on memories",
      "capabilities": ["reflection", "analysis"]
    }
  ]
}
```

#### POST `/agents/{agent_id}/invoke`
Invoke an agent for processing.

**Request Body:**
```json
{
  "input": {
    "memory_id": "uuid",
    "prompt": "Analyze this memory"
  }
}
```

---

## Common Response Formats

### Success Response
```json
{
  "data": {...},
  "message": "Operation successful"
}
```

### Error Response
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "detail": "Additional error details",
    "request_id": "uuid"
  }
}
```

### Pagination Response
```json
{
  "items": [...],
  "total": 100,
  "skip": 0,
  "limit": 20,
  "has_more": true
}
```

## Status Codes

- `200 OK`: Successful GET, PUT
- `201 Created`: Successful POST creating resource
- `204 No Content`: Successful DELETE
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Authenticated but not authorized
- `404 Not Found`: Resource doesn't exist
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

## Rate Limiting

Currently not implemented, planned for future releases.

## API Versioning

The API uses URL versioning: `/api/v1/...`

Future versions will maintain backward compatibility where possible.

## WebSocket Endpoints

### `/ws/chat`
Real-time chat connection (planned).

### `/ws/notifications`
Real-time notifications (planned).

---

## OpenAPI Documentation

Interactive API documentation is available at:
- Development: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

*For implementation details, see [ARCHITECTURE.md](ARCHITECTURE.md)*