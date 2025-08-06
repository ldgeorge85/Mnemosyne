# API Reference

## Base URL
```
http://localhost:8000/api
```

## Authentication

All endpoints except `/auth/register` and `/auth/login` require authentication.

### Headers
```http
Authorization: Bearer <token>
Content-Type: application/json
```

---

## Authentication Endpoints

### Register
```http
POST /auth/register
```

**Request:**
```json
{
  "username": "string",
  "password": "string",
  "email": "string (optional)"
}
```

**Response:**
```json
{
  "user_id": "uuid",
  "username": "string",
  "access_token": "string",
  "refresh_token": "string"
}
```

### Login
```http
POST /auth/login
```

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
  "refresh_token": "string",
  "expires_in": 3600
}
```

### Refresh Token
```http
POST /auth/refresh
```

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
  "expires_in": 3600
}
```

### Logout
```http
POST /auth/logout
```

**Response:**
```json
{
  "message": "Logged out successfully"
}
```

---

## Memory Endpoints

### Create Memory
```http
POST /memories
```

**Request:**
```json
{
  "content": "string",
  "metadata": {
    "domains": ["string"],
    "tags": ["string"],
    "source": "string"
  },
  "importance": 0.5
}
```

**Response:**
```json
{
  "id": "uuid",
  "content": "string",
  "embedding": null,
  "metadata": {},
  "importance": 0.5,
  "created_at": "2024-01-20T10:00:00Z"
}
```

### List Memories
```http
GET /memories?limit=20&offset=0&domain=technical
```

**Query Parameters:**
- `limit` (int): Number of results (default: 20, max: 100)
- `offset` (int): Pagination offset (default: 0)
- `domain` (string): Filter by domain
- `importance_min` (float): Minimum importance (0-1)
- `start_date` (ISO 8601): Filter by date range
- `end_date` (ISO 8601): Filter by date range

**Response:**
```json
{
  "memories": [
    {
      "id": "uuid",
      "content": "string",
      "metadata": {},
      "importance": 0.5,
      "created_at": "2024-01-20T10:00:00Z"
    }
  ],
  "total": 100,
  "limit": 20,
  "offset": 0
}
```

### Get Memory
```http
GET /memories/:id
```

**Response:**
```json
{
  "id": "uuid",
  "content": "string",
  "embedding": [0.1, 0.2, ...],
  "metadata": {},
  "importance": 0.5,
  "consolidation_count": 3,
  "last_accessed": "2024-01-20T10:00:00Z",
  "created_at": "2024-01-20T10:00:00Z"
}
```

### Update Memory
```http
PUT /memories/:id
```

**Request:**
```json
{
  "content": "string (optional)",
  "metadata": {},
  "importance": 0.8
}
```

### Delete Memory
```http
DELETE /memories/:id
```

**Response:**
```json
{
  "message": "Memory deleted successfully"
}
```

### Search Memories
```http
POST /memories/search
```

**Request:**
```json
{
  "query": "string",
  "limit": 10,
  "threshold": 0.7,
  "domains": ["string"]
}
```

**Response:**
```json
{
  "results": [
    {
      "memory": {},
      "similarity": 0.85,
      "relevance": "high"
    }
  ]
}
```

### Consolidate Memories
```http
POST /memories/consolidate
```

**Request:**
```json
{
  "memory_ids": ["uuid"],
  "strategy": "similarity|temporal|importance"
}
```

**Response:**
```json
{
  "consolidated_memory": {},
  "source_memories": ["uuid"],
  "consolidation_type": "synthesis"
}
```

---

## Agent Endpoints

### List Agents
```http
GET /agents
```

**Response:**
```json
{
  "agents": [
    {
      "id": "engineer",
      "name": "Engineer",
      "description": "Technical analysis and system design",
      "status": "available",
      "model": "gpt-4"
    }
  ]
}
```

### Trigger Reflection
```http
POST /agents/:agent_id/reflect
```

**Request:**
```json
{
  "memory_id": "uuid",
  "prompt": "string (optional)",
  "depth": "shallow|deep"
}
```

**Response:**
```json
{
  "reflection": {
    "agent_id": "engineer",
    "memory_id": "uuid",
    "content": "string",
    "insights": ["string"],
    "confidence": 0.8,
    "timestamp": "2024-01-20T10:00:00Z"
  }
}
```

### Orchestrate Agents
```http
POST /agents/orchestrate
```

**Request:**
```json
{
  "memory_ids": ["uuid"],
  "agent_ids": ["engineer", "philosopher"],
  "synthesis": true
}
```

**Response:**
```json
{
  "reflections": [{}],
  "synthesis": "string",
  "coherence": 0.7,
  "fracture_index": 0.3
}
```

### Get Agent Status
```http
GET /agents/:agent_id/status
```

**Response:**
```json
{
  "agent_id": "engineer",
  "status": "available|busy|error",
  "current_task": "string",
  "queue_length": 0,
  "average_response_time": 2.5
}
```

---

## Signal Endpoints

### Generate Signal
```http
POST /signals/generate
```

**Request:**
```json
{
  "regenerate": false,
  "include_domains": ["string"],
  "visibility": 0.3
}
```

**Response:**
```json
{
  "signal": {
    "version": "2.1",
    "sigil": "⊕",
    "domains": ["systems", "philosophy"],
    "personality": {},
    "coherence": {},
    "glyphs": ["∴", "⊙"],
    "flags": {},
    "visibility": 0.3,
    "signature": "string"
  }
}
```

### Get My Signals
```http
GET /signals/mine
```

**Response:**
```json
{
  "signals": [{}],
  "current_signal": {},
  "history_count": 5
}
```

### Verify Signal
```http
POST /signals/verify
```

**Request:**
```json
{
  "signal": {},
  "check_revocation": true
}
```

**Response:**
```json
{
  "valid": true,
  "issuer": "uuid",
  "timestamp": "2024-01-20T10:00:00Z",
  "trust_level": "verified"
}
```

### Discover Signals
```http
GET /signals/discover?domain=philosophy&limit=10
```

**Query Parameters:**
- `domain` (string): Filter by domain
- `seeking` (string): Match seeking flags
- `offering` (string): Match offering flags
- `min_coherence` (float): Minimum coherence level
- `limit` (int): Number of results

**Response:**
```json
{
  "signals": [{}],
  "total": 50,
  "filters_applied": ["domain:philosophy"]
}
```

### Generate Kartouche
```http
POST /signals/kartouche
```

**Request:**
```json
{
  "signal": {},
  "format": "svg|png",
  "size": "small|medium|large"
}
```

**Response:**
```json
{
  "kartouche": "svg-string-or-base64-png",
  "format": "svg"
}
```

---

## Collective Endpoints

### Join Collective
```http
POST /collective/join
```

**Request:**
```json
{
  "collective_id": "string",
  "contract": {
    "domains": ["string"],
    "depth": "summary|detailed|full",
    "duration_days": 30,
    "revocable": true,
    "anonymous": false,
    "k_anonymity": 3
  }
}
```

**Response:**
```json
{
  "contract_id": "uuid",
  "collective_id": "string",
  "expires_at": "2024-02-20T10:00:00Z",
  "status": "active"
}
```

### Share Memory
```http
POST /collective/share
```

**Request:**
```json
{
  "memory_id": "uuid",
  "collective_id": "string",
  "contract_id": "uuid"
}
```

**Response:**
```json
{
  "shared": true,
  "anonymized": false,
  "k_group_size": 5
}
```

### Search Collective
```http
POST /collective/search
```

**Request:**
```json
{
  "collective_id": "string",
  "query": "string",
  "domains": ["string"],
  "limit": 10
}
```

**Response:**
```json
{
  "results": [
    {
      "content": "string",
      "domains": ["string"],
      "source_count": 3,
      "confidence": 0.8
    }
  ]
}
```

### Find Matches
```http
POST /collective/match
```

**Request:**
```json
{
  "collective_id": "string",
  "seeking": ["string"],
  "offering": ["string"]
}
```

**Response:**
```json
{
  "matches": [
    {
      "signal": {},
      "score": 0.85,
      "matched_capabilities": ["string"],
      "introduction_available": true
    }
  ]
}
```

### Find Knowledge Gaps
```http
GET /collective/:collective_id/gaps
```

**Response:**
```json
{
  "gaps": [
    {
      "description": "Bridge needed: systems <-> philosophy",
      "importance": 0.8,
      "suggested_domains": ["systems", "philosophy"]
    }
  ]
}
```

### Revoke Sharing
```http
DELETE /collective/contracts/:contract_id
```

**Response:**
```json
{
  "revoked": true,
  "memories_affected": 42,
  "effective_date": "2024-01-20T10:00:00Z"
}
```

---

## Ritual Endpoints

### List Available Rituals
```http
GET /rituals/available
```

**Response:**
```json
{
  "rituals": [
    {
      "id": "trust_bootstrap",
      "name": "Trust Bootstrap",
      "description": "Establish initial trust with another user",
      "participants_required": 2,
      "estimated_duration": "10 minutes",
      "prerequisites": []
    }
  ]
}
```

### Initiate Ritual
```http
POST /rituals/initiate
```

**Request:**
```json
{
  "ritual_id": "trust_bootstrap",
  "participants": ["user_id"],
  "parameters": {}
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "ritual_id": "trust_bootstrap",
  "status": "waiting_for_participants",
  "expires_at": "2024-01-20T11:00:00Z"
}
```

### Advance Ritual
```http
POST /rituals/:session_id/advance
```

**Request:**
```json
{
  "action": "exchange_glyphs",
  "data": {
    "glyphs": ["∴", "⊙"]
  }
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "current_stage": "mirror_prompt",
  "next_action_required": "submit_reflection",
  "progress": 0.5
}
```

### Get Ritual Status
```http
GET /rituals/:session_id/status
```

**Response:**
```json
{
  "session_id": "uuid",
  "ritual_id": "trust_bootstrap",
  "status": "in_progress",
  "current_stage": "glyph_exchange",
  "participants": [
    {
      "user_id": "uuid",
      "ready": true
    }
  ],
  "progress": 0.25
}
```

---

## Trust Endpoints

### Get Trust Score
```http
GET /trust/:user_id
```

**Response:**
```json
{
  "user_id": "uuid",
  "trust_score": 0.7,
  "verification_level": "signal|ritual|proven",
  "last_interaction": "2024-01-20T10:00:00Z",
  "shared_domains": ["philosophy"]
}
```

### Verify Contribution
```http
POST /trust/verify
```

**Request:**
```json
{
  "user_id": "uuid",
  "contribution_id": "uuid",
  "verification_type": "positive|negative|neutral"
}
```

**Response:**
```json
{
  "verified": true,
  "new_trust_score": 0.75,
  "verification_recorded": "2024-01-20T10:00:00Z"
}
```

---

## Error Responses

All endpoints may return error responses:

### 400 Bad Request
```json
{
  "error": "Invalid request",
  "details": "Specific validation error",
  "field": "field_name"
}
```

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "details": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "error": "Forbidden",
  "details": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "error": "Not found",
  "details": "Resource does not exist"
}
```

### 429 Too Many Requests
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "details": "Something went wrong",
  "request_id": "uuid"
}
```

---

## Rate Limiting

Default rate limits:
- Authentication: 5 requests per minute
- Memory operations: 100 requests per minute
- Agent operations: 20 requests per minute
- Signal generation: 1 request per 15 minutes
- Collective operations: 50 requests per minute

Headers returned:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705741200
```

---

## Webhooks (Future)

Webhook events that will be supported:
- `memory.created`
- `memory.consolidated`
- `signal.generated`
- `ritual.completed`
- `trust.updated`
- `collective.joined`

---

## WebSocket Events (Future)

Real-time events via WebSocket:
- Agent reflection updates
- Ritual progression
- Collective discoveries
- Trust changes

---

*API Version: 1.0.0*