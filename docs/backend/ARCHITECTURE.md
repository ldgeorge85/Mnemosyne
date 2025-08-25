# Backend Architecture Documentation

## Overview

The Mnemosyne backend is built with FastAPI and SQLAlchemy using modern async/await patterns. It implements a clean architecture with separation of concerns across API, service, repository, and model layers.

## Architecture Patterns

### Core Design Patterns
- **Repository Pattern**: Data access abstracted through repository classes
- **Service Layer Pattern**: Business logic separated from data access
- **Dependency Injection**: FastAPI's DI system for database sessions and auth
- **Async-First**: All I/O operations use async/await
- **Schema Validation**: Pydantic models for request/response validation

## Directory Structure

```
backend/
├── app/
│   ├── api/                 # API Layer
│   │   ├── dependencies/    # Reusable dependencies
│   │   │   ├── auth.py     # Authentication dependency
│   │   │   └── database.py # Database session dependency
│   │   └── v1/
│   │       └── endpoints/   # API endpoints
│   │           ├── auth.py
│   │           ├── chat_llm.py
│   │           ├── memories.py
│   │           └── tasks.py
│   ├── core/               # Core Functionality
│   │   ├── auth/          # Authentication system
│   │   │   ├── manager.py # AuthManager
│   │   │   └── providers.py
│   │   ├── config.py      # Settings management
│   │   ├── exceptions.py  # Custom exceptions
│   │   └── middleware.py  # Request middleware
│   ├── db/                # Database Layer
│   │   ├── models/        # SQLAlchemy models
│   │   ├── repositories/  # Data access layer
│   │   ├── migrations/    # Alembic migrations
│   │   └── session.py     # Session management
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   │   ├── llm/          # LLM integration
│   │   ├── memory/       # Memory services
│   │   ├── persona/      # Persona system
│   │   ├── task/         # Task management
│   │   └── vector_store/ # Vector storage
│   └── main.py           # Application entry
├── agents/               # Agent system (separate)
└── requirements.txt      # Dependencies
```

## Layer Responsibilities

### API Layer (`app/api/`)
**Purpose**: Handle HTTP requests and responses
- Request validation via Pydantic schemas
- Response formatting and status codes
- Authentication/authorization via dependencies
- Route registration and OpenAPI documentation

### Service Layer (`app/services/`)
**Purpose**: Business logic and orchestration
- Complex business rules implementation
- Cross-repository coordination
- External service integration (LLM, vector store)
- Transaction management

### Repository Layer (`app/db/repositories/`)
**Purpose**: Data access abstraction
- CRUD operations
- Complex queries
- Database-specific logic isolation
- No business logic

### Model Layer (`app/db/models/`)
**Purpose**: Database schema definition
- SQLAlchemy ORM models
- Table relationships
- Database constraints
- Model validation

## Database Architecture

### Core Models

```python
User
├── id: UUID (PK)
├── email: String (unique)
├── username: String (unique)
├── hashed_password: String
├── is_active: Boolean
├── is_superuser: Boolean
└── relationships:
    ├── memories (one-to-many)
    ├── tasks (one-to-many)
    └── api_keys (one-to-many)

Memory
├── id: UUID (PK)
├── user_id: UUID (FK → User)
├── title: String
├── content: Text
├── embedding_vector: Vector(1024)
├── source_type: String
├── importance: Float
├── tags: Array[String]
└── relationships:
    ├── user (many-to-one)
    └── chunks (one-to-many)

Task
├── id: UUID (PK)
├── user_id: UUID (FK → User)
├── title: String
├── description: Text
├── status: Enum
├── priority: Enum
├── difficulty: Integer
├── quest_type: Enum
├── experience_points: Integer
└── relationships:
    ├── user (many-to-one)
    └── parent_task (self-referential)
```

### Database Technologies
- **PostgreSQL**: Primary database with pgvector extension
- **Redis**: Caching and session storage
- **Qdrant**: Vector database for similarity search
- **Alembic**: Database migration management

## Authentication Architecture

### Multi-Provider System
The `AuthManager` orchestrates multiple authentication providers:

```python
AuthManager
├── Static Provider (dev/test)
├── OAuth Provider (social login)
├── API Key Provider (service accounts)
└── DID Provider (decentralized identity)
```

### Authentication Flow
1. Request arrives with credentials
2. AuthManager attempts each provider
3. Provider validates credentials
4. JWT token generated with user claims
5. Token verified on subsequent requests

### Security Features
- JWT tokens with expiration
- Refresh token support
- Role-based access control
- Permission-based authorization
- Request ID tracking for audit

## Service Architecture

### Memory Service Stack
```
MemoryService
├── EmbeddingGenerator
│   ├── Remote API (primary)
│   └── Local Model (fallback)
├── VectorStore
│   ├── QdrantStore
│   └── PGVectorStore
└── MemoryRepository
```

### Task Service Stack
```
TaskService
├── TaskRepository
├── TaskIntelligence
│   └── LLM-powered suggestions
├── TaskScheduler
│   └── Recurring task generation
└── GameMechanics
    └── XP calculation
```

### LLM Service Architecture
```
LLMService
├── OpenAI-compatible API
├── Streaming support
├── Context management
└── Error handling/retry
```

## External Integrations

### Vector Storage
- **Qdrant**: Primary vector database
  - Collection management
  - Cosine similarity search
  - Metadata filtering
- **PGVector**: PostgreSQL extension
  - Hybrid queries (SQL + vector)
  - Backup vector storage

### LLM Integration
- **OpenAI-compatible**: Configurable base URL
- **Streaming**: Server-sent events for chat
- **Embeddings**: 1024-dimensional vectors
- **Fallback**: Local models if API fails

## Configuration Management

### Pydantic Settings
```python
class Settings(BaseSettings):
    # Database
    database_url: str
    
    # Redis
    redis_url: str
    
    # Vector Store
    qdrant_host: str
    qdrant_port: int
    
    # LLM
    llm_api_base: str
    llm_api_key: str
    
    # Auth
    jwt_secret_key: str
    jwt_algorithm: str
    
    class Config:
        env_file = ".env"
```

### Environment Variables
- Development: `.env` file
- Production: Environment variables
- Testing: Override in tests

## Error Handling

### Exception Hierarchy
```
AppException (base)
├── AuthException
│   ├── InvalidCredentials
│   └── TokenExpired
├── DatabaseException
│   ├── RecordNotFound
│   └── IntegrityError
└── ServiceException
    ├── LLMException
    └── VectorStoreException
```

### Error Response Format
```json
{
  "error": {
    "code": "AUTH_001",
    "message": "Invalid credentials",
    "detail": "Username or password incorrect",
    "request_id": "uuid-here"
  }
}
```

## Performance Optimizations

### Database
- Connection pooling with asyncpg
- Indexed columns for common queries
- Lazy loading relationships
- Batch operations where possible

### Caching
- Redis for session data
- Embedding cache for repeated content
- Query result caching (planned)

### Async Operations
- Non-blocking I/O throughout
- Concurrent requests handling
- Background task processing

## Deployment Architecture

### Container Structure
```
docker-compose.yml
├── backend (FastAPI app)
├── postgres (with pgvector)
├── redis (caching)
├── qdrant (vector search)
└── nginx (reverse proxy)
```

### Environment Management
- Development: Docker Compose
- Production: Docker Swarm ready
- Testing: Isolated containers

## Security Considerations

### Current Implementation
- JWT authentication
- Password hashing (bcrypt)
- CORS configuration
- SQL injection prevention (ORM)
- Input validation (Pydantic)

### Planned Enhancements
- Rate limiting
- API versioning strategy
- Request signing
- Audit logging
- Encryption at rest

## Testing Strategy

### Current Coverage
- Integration tests for API endpoints
- Repository layer tests
- Service layer tests (partial)

### Testing Approach
- No mocking (real databases in tests)
- Docker containers for test isolation
- Fixtures for test data setup

## Future Considerations

### Scalability
- Horizontal scaling ready (stateless)
- Database read replicas support
- Queue system for async tasks
- Microservices split possible

### Monitoring
- Request ID tracking implemented
- Metrics collection ready
- Log aggregation supported
- Health check endpoints

---

This architecture provides a solid foundation for the Mnemosyne Protocol, balancing clean code organization with practical implementation needs.