# Mnemosyne - Architecture Documentation

## Overview

Mnemosyne is an AI Executive Assistant Agent built with modern web technologies. This document provides a comprehensive overview of the system's architecture, including components, data flow, and technical decisions.

## System Architecture

![System Architecture](../assets/diagrams/system_architecture.png)

### Core Components

#### Backend

The backend is built using FastAPI, a modern, high-performance web framework for building APIs with Python. The key components include:

- **Agent Orchestration & Management (Phase 3, as of 2025-06-08T22:42:40-07:00)**
  - CrewAI is fully integrated for sub-agent orchestration, recursive task delegation, and agent team structures
  - AgentManager service (`/backend/app/services/agent/agent_manager.py`) is fully implemented, manages agent lifecycle, orchestration, and DB-backed state, and is wired to all relevant API endpoints
  - All agent/task state, logs, and orchestration events are persisted in Postgres for auditability and monitoring
  - Cognee-inspired memory reflection and importance scoring service (`/backend/app/services/memory/reflection.py`) is fully implemented and integrated with API endpoints and DB
  - All new DB models: Agent, AgentLink, AgentLog, MemoryReflection, etc. are live
  - Alembic migrations for new tables have been applied
  - All new/updated API endpoints for agent orchestration and memory reflection are live (see `api_specifications.md`)
  - LangChain remains the framework for the main conversational agent, including MCP tool calling and LLM integration
  - Robust logging and monitoring are implemented for all agent actions and results
  - All functions are commented as per user rules
  - See `source_of_truth.md` for integration details

1. **API Layer**
   - FastAPI application with versioned endpoints
   - Authentication middleware
   - Input validation via Pydantic models
   - Error handling and logging

2. **Service Layer**
   - Conversation Management Service
   - Memory System Service
   - Task Management Service
   - Agent Framework Service

3. **Data Access Layer**
   - SQLAlchemy ORM for database operations
   - Repository pattern for data access
   - Migrations with Alembic

4. **Integration Layer**
   - LangChain for LLM integrations
   - Vector database operations with pgvector
   - External API clients

#### Frontend

The frontend is a React application using TypeScript and Chakra UI:

1. **Presentation Layer**
   - React components organized by domain
   - Chakra UI for consistent styling and accessibility
   - Responsive layouts for all device sizes

2. **State Management**
   - Zustand stores for global state
   - React hooks for component state
   - Redux-like actions and selectors

3. **API Client**
   - Axios-based API client
   - Request/response interceptors
   - Error handling and retry logic

4. **Routing**
   - React Router for navigation
   - Protected routes for authenticated content
   - Dynamic route parameters

#### Database

PostgreSQL with pgvector extension:

1. **Core Tables**
   - Users
   - Conversations
   - Messages
   - Memories
   - Tasks
   - AgentTools

2. **Vector Database**
   - pgvector extension for embedding storage
   - Similarity search capabilities
   - Indexed vector operations

#### Cache and Task Queue

Redis for caching and lightweight task queuing:

1. **Caching**
   - API response caching
   - Session management
   - Rate limiting

2. **Task Queue**
   - RQ (Redis Queue) for background jobs
   - Scheduled tasks
   - Retry mechanisms

## Data Flow

### Conversation Flow

1. User sends a message via the frontend
2. Message is stored in the PostgreSQL database
3. The conversation service processes the message
4. Relevant memories are retrieved using vector similarity search
5. The message, conversation history, and memories are sent to the LLM
6. The LLM generates a response
7. The response is stored in the database and returned to the user
8. New memories are extracted and stored with vector embeddings

### Task Management Flow

1. Tasks can be created by the user or automatically by the agent
2. Tasks are stored in the PostgreSQL database
3. Scheduled tasks are managed via Redis-based queue
4. Reminders and notifications are delivered via the frontend
5. Task completion updates the task status in the database

## Component Diagrams

### Backend Components

```
                   ┌─────────────────┐
                   │  FastAPI App    │
                   └────────┬────────┘
                            │
                            ▼
        ┌──────────────────────────────────┐
        │           API Routes             │
        └──┬──────────────┬───────────┬────┘
           │              │           │
           ▼              ▼           ▼
┌─────────────────┐ ┌──────────┐ ┌──────────┐
│ Conversation    │ │ Memory   │ │ Task     │
│ Service         │ │ Service  │ │ Service  │
└────────┬────────┘ └────┬─────┘ └────┬─────┘
         │               │            │
         └───────────────┼────────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Database Layer   │
                └──────────────────┘
```

### Frontend Components

```
           ┌─────────────────┐
           │   React App     │
           └────────┬────────┘
                    │
                    ▼
        ┌─────────────────────┐
        │     App Router      │
        └──┬──────────────┬───┘
           │              │
           ▼              ▼
┌─────────────────┐ ┌───────────────┐
│ Public Routes   │ │Protected Routes│
└────────┬────────┘ └───────┬───────┘
         │                  │
         ▼                  ▼
┌─────────────────┐ ┌───────────────┐
│ Home, Login     │ │Dashboard, etc │
└─────────────────┘ └───────────────┘
         │                  │
         └────────┬─────────┘
                  │
                  ▼
         ┌─────────────────┐
         │  Component Lib  │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │   API Client    │
         └─────────────────┘
```

## Technical Decisions

### Choice of FastAPI

FastAPI was chosen for its performance, ease of use, and built-in support for:
- Automatic OpenAPI documentation
- Request validation with Pydantic
- Asynchronous request handling
- Dependency injection

### Choice of React + TypeScript

React with TypeScript was selected for:
- Type safety and improved developer experience
- Component-based architecture
- Large ecosystem of libraries and tools
- Strong community support

### Choice of Zustand over Redux

Zustand was chosen for state management because:
- Simplified API compared to Redux
- Reduced boilerplate code
- Built-in TypeScript support
- Unopinionated middleware system

### Choice of PostgreSQL + pgvector

PostgreSQL with pgvector was selected for:
- ACID compliance for transactional data
- Vector similarity search capabilities
- Mature ecosystem and tooling
- Ability to handle both relational and vector data in one database

### Choice of Redis for Queue

Redis was chosen for task queuing because:
- Low latency for time-sensitive operations
- Simple implementation with RQ
- Built-in support for scheduling
- Can be shared with caching infrastructure

## Deployment Architecture

Mnemosyne is deployed using Docker Compose with the following containers:
- PostgreSQL with pgvector
- Redis
- FastAPI backend
- React frontend with Nginx

For production, the system is designed to scale horizontally with the following considerations:
- Backend API instances behind a load balancer
- Read replicas for PostgreSQL
- Redis cluster for high availability
- Static assets served via CDN

## Future Architecture Considerations

- Migration to Kubernetes for container orchestration
- Implementation of a more robust message queue (RabbitMQ/Kafka)
- Separation of read and write databases for higher scalability
- Integration with cloud-native services for monitoring and logging

#### Memory System
- Automatic information extraction from conversations
- Relevance-based retrieval of past information
- Memory consolidation and priority adjustment
- Cognee-inspired reflection, importance scoring, and hierarchical organization will be implemented to enhance memory robustness.
- Memory state is tightly integrated with agent/task logs and orchestration events for full context and auditability.

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/getting-started.html)
- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [Redis Documentation](https://redis.io/documentation)
