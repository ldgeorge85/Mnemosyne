# Mnemosyne - API Specifications

## Overview

This document details the REST API endpoints provided by the Mnemosyne backend service. All API requests and responses are in JSON format unless otherwise specified.

## Base URL

```
/api/v1
```

All endpoints described in this document are relative to this base URL.

## Authentication

Most endpoints require authentication using JSON Web Tokens (JWT).

### Authentication Header

```
Authorization: Bearer {token}
```

### Authentication Endpoints

#### POST /auth/login

Authenticates a user and returns a JWT token.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "string",
    "username": "string",
    "email": "string",
    "firstName": "string",
    "lastName": "string"
  }
}
```

**Status Codes:**
- 200: Success
- 401: Invalid credentials

#### POST /auth/refresh

Refreshes an expired JWT token.

**Request:**
```json
{
  "refresh_token": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Status Codes:**
- 200: Success
- 401: Invalid token

#### POST /auth/register

Registers a new user.

**Request:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "firstName": "string",
  "lastName": "string"
}
```

**Response:**
```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "firstName": "string",
  "lastName": "string",
  "createdAt": "string"
}
```

**Status Codes:**
- 201: Created
- 400: Invalid input
- 409: User already exists

## User Endpoints

#### GET /users/me

Returns the authenticated user's profile.

**Response:**
```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "firstName": "string",
  "lastName": "string",
  "createdAt": "string",
  "updatedAt": "string"
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized

#### PUT /users/me

Updates the authenticated user's profile.

**Request:**
```json
{
  "email": "string",
  "firstName": "string",
  "lastName": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "firstName": "string",
  "lastName": "string",
  "updatedAt": "string"
}
```

**Status Codes:**
- 200: Success
- 400: Invalid input
- 401: Unauthorized

## Conversation Endpoints

#### GET /conversations

Returns a list of the user's conversations.

**Query Parameters:**
- `limit` (integer, default=20): Number of items to return
- `offset` (integer, default=0): Offset for pagination

**Response:**
```json
{
  "total": 0,
  "offset": 0,
  "limit": 20,
  "items": [
    {
      "id": "string",
      "title": "string",
      "createdAt": "string",
      "updatedAt": "string",
      "messageCount": 0,
      "lastMessage": {
        "content": "string",
        "role": "user|assistant|system",
        "createdAt": "string"
      }
    }
  ]
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized

#### POST /conversations

Creates a new conversation.

**Request:**
```json
{
  "title": "string"
}
```

**Response:**
```json
{
  "id": "string",
  "title": "string",
  "createdAt": "string",
  "updatedAt": "string"
}
```

**Status Codes:**
- 201: Created
- 400: Invalid input
- 401: Unauthorized

#### GET /conversations/{id}

Returns a specific conversation with its messages.

**Query Parameters:**
- `limit` (integer, default=50): Number of messages to return
- `offset` (integer, default=0): Offset for pagination

**Response:**
```json
{
  "id": "string",
  "title": "string",
  "createdAt": "string",
  "updatedAt": "string",
  "messages": {
    "total": 0,
    "offset": 0,
    "limit": 50,
    "items": [
      {
        "id": "string",
        "content": "string",
        "role": "user|assistant|system",
        "createdAt": "string"
      }
    ]
  }
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized
- 404: Not found

#### PUT /conversations/{id}

Updates a conversation.

**Request:**
```json
{
  "title": "string"
}
```

**Response:**
```json
{
  "id": "string",
  "title": "string",
  "updatedAt": "string"
}
```

**Status Codes:**
- 200: Success
- 400: Invalid input
- 401: Unauthorized
- 404: Not found

#### DELETE /conversations/{id}

Deletes a conversation.

**Response:**
```json
{
  "success": true
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized
- 404: Not found

#### POST /conversations/{id}/messages

Adds a new message to a conversation.

**Request:**
```json
{
  "content": "string",
  "role": "user|system"
}
```

**Response:**
```json
{
  "id": "string",
  "content": "string",
  "role": "user|system",
  "createdAt": "string",
  "assistant_response": {
    "id": "string",
    "content": "string",
    "role": "assistant",
    "createdAt": "string"
  }
}
```

**Status Codes:**
- 201: Created
- 400: Invalid input
- 401: Unauthorized
- 404: Not found

#### DELETE /conversations/{id}/messages/{messageId}

Deletes a message from a conversation.

**Response:**
```json
{
  "success": true
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized
- 404: Not found

## Memory Endpoints

#### GET /memories

Returns a list of the user's memories.

**Query Parameters:**
- `limit` (integer, default=20): Number of items to return
- `offset` (integer, default=0): Offset for pagination
- `query` (string, optional): Search query
- `importance` (integer, optional): Filter by minimum importance (1-10)

**Response:**
```json
{
  "total": 0,
  "offset": 0,
  "limit": 20,
  "items": [
    {
      "id": "string",
      "content": "string",
      "source": "string",
      "importance": 0,
      "createdAt": "string",
      "updatedAt": "string"
    }
  ]
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized

#### POST /memories

Creates a new memory.

**Request:**
```json
{
  "content": "string",
  "source": "string",
  "importance": 0
}
```

**Response:**
```json
{
  "id": "string",
  "content": "string",
  "source": "string",
  "importance": 0,
  "createdAt": "string",
  "updatedAt": "string"
}
```

**Status Codes:**
- 201: Created
- 400: Invalid input
- 401: Unauthorized

#### GET /memories/{id}

Returns a specific memory.

**Response:**
```json
{
  "id": "string",
  "content": "string",
  "source": "string",
  "importance": 0,
  "createdAt": "string",
  "updatedAt": "string"
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized
- 404: Not found

#### PUT /memories/{id}

Updates a memory.

**Request:**
```json
{
  "content": "string",
  "source": "string",
  "importance": 0
}
```

**Response:**
```json
{
  "id": "string",
  "content": "string",
  "source": "string",
  "importance": 0,
  "updatedAt": "string"
}
```

**Status Codes:**
- 200: Success
- 400: Invalid input
- 401: Unauthorized
- 404: Not found

#### DELETE /memories/{id}

Deletes a memory.

**Response:**
```json
{
  "success": true
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized
- 404: Not found

## Task Endpoints

#### GET /tasks

Returns a list of the user's tasks.

**Query Parameters:**
- `limit` (integer, default=20): Number of items to return
- `offset` (integer, default=0): Offset for pagination
- `status` (string, optional): Filter by status (pending, in_progress, completed, cancelled)
- `priority` (string, optional): Filter by priority (low, medium, high)

**Response:**
```json
{
  "total": 0,
  "offset": 0,
  "limit": 20,
  "items": [
    {
      "id": "string",
      "title": "string",
      "description": "string",
      "status": "pending|in_progress|completed|cancelled",
      "dueDate": "string",
      "priority": "low|medium|high",
      "createdAt": "string",
      "updatedAt": "string"
    }
  ]
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized

#### POST /tasks

Creates a new task.

**Request:**
```json
{
  "title": "string",
  "description": "string",
  "dueDate": "string",
  "priority": "low|medium|high"
}
```

**Response:**
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "status": "pending",
  "dueDate": "string",
  "priority": "low|medium|high",
  "createdAt": "string",
  "updatedAt": "string"
}
```

**Status Codes:**
- 201: Created
- 400: Invalid input
- 401: Unauthorized

#### GET /tasks/{id}

Returns a specific task.

**Response:**
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "status": "pending|in_progress|completed|cancelled",
  "dueDate": "string",
  "priority": "low|medium|high",
  "createdAt": "string",
  "updatedAt": "string"
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized
- 404: Not found

#### PUT /tasks/{id}

Updates a task.

**Request:**
```json
{
  "title": "string",
  "description": "string",
  "status": "pending|in_progress|completed|cancelled",
  "dueDate": "string",
  "priority": "low|medium|high"
}
```

**Response:**
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "status": "pending|in_progress|completed|cancelled",
  "dueDate": "string",
  "priority": "low|medium|high",
  "updatedAt": "string"
}
```

**Status Codes:**
- 200: Success
- 400: Invalid input
- 401: Unauthorized
- 404: Not found

#### DELETE /tasks/{id}

Deletes a task.

**Response:**
```json
{
  "success": true
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized
- 404: Not found

## Health Endpoints

#### GET /health/

Returns basic health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "service": "Mnemosyne",
  "version": "0.1.0",
  "environment": "development"
}
```

**Status Codes:**
- 200: Success
- 500: Internal Server Error

#### GET /health/detailed

Returns detailed health status including component checks.

**Response:**
```json
{
  "status": "healthy",
  "service": "Mnemosyne",
  "version": "0.1.0",
  "environment": "development",
  "components": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful"
    },
    "vector": {
      "status": "healthy",
      "message": "pgvector extension enabled"
    },
    "api": {
      "status": "healthy",
      "message": "API is running"
    }
  }
}
```

**Status Codes:**
- 200: Success
- 500: Internal Server Error

#### GET /health/readiness

Checks if the application is ready to receive traffic. Used for Kubernetes readiness probes.

**Response:**
```json
{
  "status": "ready",
  "service": "Mnemosyne"
}
```

**Status Codes:**
- 200: Success
- 503: Service Not Ready

#### GET /health/liveness

Checks if the application is alive. Used for Kubernetes liveness probes.

**Response:**
```json
{
  "status": "alive",
  "service": "Mnemosyne"
}
```

**Status Codes:**
- 200: Success
- 503: Service Unavailable

## Error Responses

All API endpoints return standardized error responses:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}
```

### Common Error Codes

- `UNAUTHORIZED`: Authentication required
- `FORBIDDEN`: Permission denied
- `NOT_FOUND`: Resource not found
- `BAD_REQUEST`: Invalid request parameters
- `VALIDATION_ERROR`: Request validation failed
- `INTERNAL_ERROR`: Server error

## Rate Limiting

API requests are rate-limited to prevent abuse. Rate limits are applied per IP address and per authenticated user.

**Headers:**
- `X-RateLimit-Limit`: Number of requests allowed in the window
- `X-RateLimit-Remaining`: Number of requests remaining in the window
- `X-RateLimit-Reset`: Time when the rate limit resets (Unix timestamp)

When rate limit is exceeded:

**Status Code:** 429 (Too Many Requests)

**Response:**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in {n} seconds.",
    "details": {
      "resetTime": 1623456789
    }
  }
}
```

## Versioning

API versioning is managed through the URL path. The current version is `v1`.

## Changelog

### v1.0.0 (Initial Release)
- Basic authentication endpoints
- User management endpoints
- Conversation and message endpoints
- Memory management endpoints
- Task management endpoints
- Health check endpoints
