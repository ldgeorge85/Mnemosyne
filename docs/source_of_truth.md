# Mnemosyne - Source of Truth

This document serves as the definitive reference for the Mnemosyne project structure, tracking all files and directories as they are created, modified, or deleted.

> **Note:** Mnemosyne (named after the ancient Greek Titan goddess of memory and remembrance) is a web-based conversational AI system with advanced memory capabilities, scheduling features, and agentic task execution abilities. The implementation plan (`implementation_plan.md`) includes a detailed phase-based task tracker table, expanded best practices for testing, documentation, CI/CD, security, deployment, and compliance. Refer to both this document and the implementation plan for the most up-to-date project guidance.

## Project Structure

> **2025-06-07**: Backend Import Fixes & Docker Rebuild Requirement
> - Fixed all missing imports in `backend/app/api/v1/endpoints/memories.py` (added Path, Query, MemorySearchResponse, MemorySearchQuery, MemoryStatistics, MemoryChunkResponse, MemoryChunkCreate, MemoryChunkUpdate).
> - Backend would not pick up code changes with just `docker compose restart`; a full `docker compose build backend && docker compose up -d backend` is required after backend Python code changes to avoid stale code and import errors.
> - Confirmed backend API now starts and responds to requests after rebuild.
> - Updated workflow documentation and troubleshooting guidance for backend development.

> **2025-06-06**: Phase 3 Kickoff - CrewAI & Cognee Integration
> - Added CrewAI and Cognee to backend dependencies (`requirements.txt`)
> - Created new backend modules (stubs):
>   - `/backend/app/services/agent/agent_manager.py` (AgentManager orchestration)
>   - `/backend/app/db/models/agent.py` (Agent, AgentLink, AgentLog, MemoryReflection models)
>   - `/backend/app/services/memory/reflection.py` (Cognee-inspired memory reflection)
>   - `/backend/app/api/v1/agents.py` (API endpoints for agent orchestration)
>   - `/backend/app/api/v1/memories.py` (API endpoints for memory reflection)
> - Planned Alembic migrations for new agent/memory tables
> - Updated backend Dockerfile to support new dependencies
> - These files are initial stubs for Phase 3 and will be expanded with full logic and tests in subsequent steps.

```
/home/lewis/dev/personal/mnemosyne/
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore file with patterns for Python, Node.js, and env files
├── .pre-commit-config.yaml       # Pre-commit hooks configuration
├── .vscode/                      # VSCode editor configuration
│   ├── extensions.json           # Recommended extensions
│   ├── launch.json               # Debug configurations
│   └── settings.json             # Editor settings
├──<!-- AGENT AND MEMORY SERVICES -->

### backend/app/services/agent/agent_manager.py
- Implements AgentManager class for agent lifecycle, orchestration, sub-agent creation, and logging.
- Integrates with DB models: Agent, AgentLink, AgentLog.
- Async methods: create_agent, link_agents, assign_task, get_status, spawn_subagent, get_logs.
- Fully integrated with CrewAI for agent orchestration.
- All functions are commented as per user rules.
- Fully wired to API endpoints in `/backend/app/api/v1/agents.py`.
- Last updated: 2025-06-08T22:42:40-07:00.

### backend/app/api/v1/agents.py
- Implements all agent orchestration endpoints (create, link, assign_task, get_status, spawn_subagent, get_logs).
- Endpoints are fully wired to AgentManager service (async).
- All endpoints are live and ready for testing.
- Last updated: 2025-06-08T22:42:40-07:00.

### backend/app/services/memory/reflection.py
- Implements MemoryReflectionService for memory reflection, importance scoring, and hierarchy.
- Integrates with DB model: MemoryReflection.
- Async methods: reflect, get_importance_scores, get_hierarchy.
- Fully integrated with API endpoints in `/backend/app/api/v1/memories.py`.
- All functions are commented as per user rules.
- Last updated: 2025-06-08T22:42:40-07:00.

### backend/app/api/v1/memories.py
- Implements all memory reflection endpoints (reflect, get_importance, get_hierarchy).
- Endpoints are fully wired to MemoryReflectionService (async).
- All endpoints are live and ready for testing.
- Last updated: 2025-06-08T22:42:40-07:00.

> Next steps (as of 2025-06-08T22:42:40-07:00):
> - Implement robust tests for all new endpoints/services (AgentManager, MemoryReflectionService)
> - Update implementation_plan.md, architecture.md, and README.md for API usage and integration details
> - Clean up unused code/files and document removals in this file
> - Ensure all documentation is in sync across docs/
> - All functions are commented as per user rules.

├── README.md                     # Project overview and setup instructions
├── backend/                      # FastAPI backend application
│   ├── .env.example              # Example environment variables file
│   ├── Dockerfile                # Multi-stage Docker build for backend
│   ├── requirements-dev.txt      # Python development dependencies
│   ├── requirements.txt          # Python dependencies
│   ├── app/                      # Application code
│   │   ├── api/                  # API routes organized by domain
│   │   │   ├── v1/               # API version 1 endpoints
│   │   │   └── dependencies/     # Endpoint dependencies (auth, permissions)
│   │   ├── core/                 # Core application code
│   │   │   ├── config/           # Configuration management
│   │   │   ├── security/         # Security utilities
│   │   │   └── logging/          # Logging configuration
│   │   ├── db/                   # Database models and operations
│   │   │   ├── migrations/       # Alembic migrations
│   │   │   ├── models/           # SQLAlchemy models
│   │   │   └── repositories/     # Data access layer
│   │   ├── services/             # Business logic services
│   │   │   ├── memory/           # Memory management services
│   │   │   ├── conversation/     # Conversation handling
│   │   │   ├── tasks/            # Task management services
│   │   │   └── agent/            # Agent framework services
│   │   ├── utils/                # Utility functions
│   │   └── tests/                # Test suite
│   │       ├── unit/             # Unit tests
│   │       │   ├── test_agent_manager.py         # Unit tests for AgentManager (added 2025-06-09T08:51:17-07:00)
│   │       │   └── test_memory_reflection.py     # Unit tests for MemoryReflectionService (added 2025-06-09T08:51:17-07:00)
│   │       ├── integration/      # Integration tests
│   │       │   ├── test_api_agents.py            # Integration tests for /agents/* endpoints (added 2025-06-09T08:51:17-07:00)
│   │       │   └── test_api_memories.py          # Integration tests for /memories/* endpoints (added 2025-06-09T08:51:17-07:00)
│   │       └── e2e/              # End-to-end tests
├── docker/                       # Docker configuration files
│   ├── dev/                      # Development tools Docker configuration
│   │   └── Dockerfile.dev-tools  # Development tools image
│   ├── postgres/                 # PostgreSQL Docker configuration
│   │   ├── Dockerfile            # PostgreSQL with pgvector
│   │   └── init-pgvector.sql     # SQL initialization for pgvector
│   └── redis/                    # Redis Docker configuration
├── docker-compose.dev-tools.yml  # Docker Compose for dev tools and testing
├── docker-compose.override.yml   # Development-specific Docker Compose overrides
├── docker-compose.prod.yml       # Production-specific Docker Compose configuration
├── docker-compose.yml            # Base Docker Compose configuration
├── docs/                         # Project documentation
│   ├── implementation_plan.md    # Detailed system architecture and technical implementation details
│   ├── task_tracker.md           # Project phases and specific tasks with checkboxes
│   ├── source_of_truth.md        # This file - tracking all project files and structure
│   ├── architecture.md           # High-level architecture documentation with component diagrams
│   ├── api_specifications.md     # API endpoints documentation with request/response examples
│   ├── development_guidelines.md # Code style guide, Git workflow, and review process
│   ├── phase_2_prompt.md         # Onboarding prompt for Phase 2 with project context and next steps
│   ├── ai_patterns.md            # Implementation patterns for AI assistants
│   ├── progress_template.md      # Template for AI progress reporting
│   ├── feedback_process.md       # Process for AI assistants to request human feedback
│   ├── configuration.md          # Configuration parameter documentation (planned)
│   ├── database/
│   │   └── schema_changes.md     # Documentation of database schema changes (planned)
│   ├── components/               # Documentation for individual system components (planned)
│   └── api/                      # API specifications and examples (planned)
├── frontend/                     # React frontend application
│   ├── Dockerfile                # Multi-stage Docker build for frontend
│   ├── nginx.conf                # Nginx configuration for frontend serving
│   ├── package.json              # Node.js dependencies and scripts
│   ├── public/                   # Static assets
│   └── src/                      # Source code
│       ├── api/                  # API client and service interfaces
│       ├── components/           # Reusable UI components
│       │   ├── common/           # Shared components
│       │   ├── layout/           # Layout components
│       │   └── domain/           # Domain-specific components
│       ├── hooks/                # Custom React hooks
│       ├── pages/                # Page components
│       ├── stores/               # Zustand stores
│       ├── styles/               # Global styles and theming
│       ├── types/                # TypeScript type definitions
│       └── utils/                # Utility functions
└── manage.sh                     # Project management script (executable)
```

## API Endpoints

- **GET /conversations/{id}/messages**: Returns paginated messages for a conversation. Accepts `limit` and `offset` query parameters. Available as of 2025-06-07.

## Documentation Overview

### 2025-06-06: Phase 3 CrewAI & Cognee Integration Plan
- Updated `architecture.md`, `implementation_plan.md`, `task_tracker.md`, `api_specifications.md`, and this file to specify CrewAI for agent orchestration, AgentManager service, and Cognee-inspired memory reflection.
- See those docs for details on DB-backed orchestration, recursive sub-agent support, and memory enhancements.


### implementation_plan.md
Contains the complete system architecture, technical implementation details, and a detailed phase-based task tracker table for Mnemosyne, including:
- Project identity and overview
- Core components (backend and frontend)
- Data architecture
- Core services
- Technical implementation details
- API design
- Deployment architecture
- Best practices for testing, documentation, CI/CD, security, deployment, and compliance
- Task tracker table mapping features to phases, AI assistant roles, human review requirements, dependencies, and status
- Future extension points
- Documentation hierarchy and AI assistant collaboration framework

### task_tracker.md
Outlines all project tasks organized into logical phases and provides detailed, granular checklists for each:
- Phase 1: Project Setup and Foundation (1-2 weeks)
- Phase 2: Core Functionality (2-3 weeks)
- Phase 3: Advanced Features (2-3 weeks)
- Phase 4: Integration and Testing (1-2 weeks)
- Phase 5: Polishing and Deployment (1 week)

Each phase contains detailed tasks with checkboxes for tracking progress, with additional information on:
- AI assistant roles (Primary, Support, Review)
- Human review requirements (Required, Optional, None)
- Implementation guidelines for AI assistants
- Human oversight guidelines

> The task tracker in `implementation_plan.md` provides a high-level, phase-based overview, while `task_tracker.md` contains granular, actionable tasks for day-to-day tracking. Keep both documents in sync as the project evolves.

## Update History

- **2025-06-05**: Permanently Fixed Frontend Console Errors
  - Implemented comprehensive fix for recurring frontend console errors
  - Updated Vite proxy configuration to use Docker service names instead of localhost
  - Added error handling directly in the Vite proxy to intercept and handle connection errors
  - Enhanced Health API client with Docker container networking awareness
  - Added delay mechanism between health check attempts to reduce network congestion
  - Updated documentation with detailed solution in debugging_guide.md
  - Verified browser console is now completely free of errors
  - Updated phase2_testing_guide.md to reflect current error-free status

- **2025-05-29**: Debugging and Stability Improvements
  - Created debugging_status.md tracking document
  - Fixed import errors in multiple backend modules
  - Created missing BaseRepository class for database operations
  - Updated OpenAI client for compatibility with newer SDK versions
  - Fixed dependency injection issues across the codebase
  - Added is_admin dependency function for admin-only endpoints

- **2025-05-29**: Implemented Chat UI Components (UI-01, UI-02, UI-03)
  - Created ChatInput component with multiline support and keyboard shortcuts
  - Built ChatContainer for complete chat experience
  - Implemented TypingIndicator with animated dots
  - Added support for file attachments
  - Created responsive message bubbles with avatar support

  - Established clear testing criteria for all Phase 2 components

- **2025-06-02**: Fixed Backend Conversation Endpoints (CONV-01)
  - Fixed database table creation issues for `conversations` and `messages` tables
  - Created backend `README.md` with documentation for the `create_tables.py` script
  - Fixed async session handling in repository methods to properly commit changes
  - Corrected table name references in SQL queries (plural vs singular form)
  - Updated debugging guide with solutions for common database issues
  - Added test results to `/docs/phase2_testing_guide.md` with API endpoint verification
  - Marked conversation endpoint validation as complete in task tracker
  - Resolved SQLAlchemy asynchronous execution issues in ConversationRepository
  - Fixed raw SQL query execution to properly handle CursorResult objects
  - Documented SQLAlchemy async/sync execution patterns in debugging_guide.md
  - Partially tested: Verified basic conversations endpoint access returns 200 OK
  - Further testing needed for: creating conversations, adding messages, pagination, and UI integration

- **2025-05-30**: Implemented Navigation and Settings UI (UI-04, UI-05)
  - Enhanced Sidebar component with improved responsive behavior
  - Added mobile navigation with bottom bar for small screens
  - Improved active state detection for nested routes
  - Created comprehensive Settings interface with multiple tabs

- **2025-05-30**: Resolved Backend and Frontend Debugging Issues
  - Fixed dependencies on `deps.is_admin` in `memory_management.py` and `memory_scoring.py`
  - Added proper Pydantic response models to health endpoints
  - Fixed response validation errors in the API
  - Installed missing frontend dependencies (uuid, react-markdown, react-syntax-highlighter, remark-gfm)
  - Updated debugging status documentation
  - Verified API endpoint functionality
  - Implemented ThemeSettings component for appearance customization
  - Added AccountSettings component for user profile management
  - Created NotificationSettings for configuring alerts and messages
  - Implemented PrivacySettings for data and security management
  - Integrated all settings components into a cohesive interface

- **2025-05-30**: Implemented Memory Relevance Scoring System (MEM-05)
  - Created multi-factor scoring system with weighted factors
  - Implemented several scoring factors: recency, access frequency, explicit importance, semantic relevance
  - Added feedback collection for relevance improvement
  - Created API endpoints for retrieving and updating memory scores
  - Implemented batch scoring for efficient updates
  - Added score history tracking for performance analysis
  - Added database migration for memory scoring tables

- **2025-05-29**: Implemented Memory Pruning and Management System (MEM-04)
  - Created RetentionPolicy class for configurable memory management
  - Implemented memory maintenance with archiving capabilities
  - Added storage optimization with pgvector index rebuilding
  - Built memory statistics gathering and reporting
  - Created admin API endpoints for maintenance tasks
  - Implemented scheduled maintenance task
  - Added dry-run capability for safe testing

- **2025-05-29**: Implemented Memory Retrieval System (MEM-03)
  - Created MemoryRetrievalService for robust similarity search
  - Implemented hybrid search combining vector similarity and metadata filters
  - Added tag-based memory filtering capabilities
  - Built memory access tracking for usage statistics
  - Created API endpoints for memory retrieval
  - Implemented relevance scoring and result ranking
  - Added support for pagination and result limiting

- **2025-05-29**: Implemented PGVector Storage Interface (MEM-02)
  - Created PGVectorStore class for vector operations
  - Implemented vector similarity search with multiple distance metrics
  - Added index management capabilities
  - Built batch processing for embeddings
  - Created optimized query functions
  - Implemented MemoryVectorStore specialized for memory chunks
  - Added vector index manager for maintenance and optimization

- **2025-05-29**: Implemented Function Calling Framework (LLM-05)
  - Created flexible function registry for tool definitions
  - Implemented function calling with OpenAI's API
  - Added automatic parameter type conversion
  - Built conversation loop for agent function execution
  - Created API endpoints for function discovery and execution
  - Implemented error handling and result processing
  - Added example tool functions for demonstration

- **2025-05-29**: Implemented Response Parsing System (LLM-04)
  - Created robust response parsing utilities for structured outputs
  - Implemented JSON extraction and validation
  - Added support for dynamic schema validation
  - Built structured output generation with schema guidance
  - Created parsers for common output formats
  - Implemented error handling and response validation
  - Added API endpoints for demonstration

- **2025-05-29**: Implemented Prompt Engineering System (LLM-03)
  - Created prompt template management system with versioning
  - Implemented variable interpolation with default values
  - Developed file-based storage for prompt templates
  - Added template tagging and metadata support
  - Built API endpoints for template CRUD operations
  - Created system prompts for common operations
  - Added template filling with validation

- **2025-05-29**: Implemented OpenAI API Client (LLM-02)
  - Created specialized OpenAI client with advanced features
  - Implemented token bucket rate limiting algorithm
  - Added robust error handling with detailed messages
  - Created exponential backoff retry logic
  - Added embeddings generation endpoint
  - Implemented content moderation endpoint
  - Added streaming functionality with proper error recovery

- **2025-05-29**: Implemented LangChain Integration (LLM-01)
  - Set up LangChain service with OpenAI integration
  - Created custom callback handlers for monitoring and logging
  - Implemented streaming and non-streaming chat completions
  - Added conversation chain support with memory
  - Created API endpoints for LLM interactions
  - Added configuration classes for LLM settings
  - Implemented retry logic and error handling

- **2025-05-29**: Implemented Memory Storage System (MEM-01)
  - Created database models for Memory and MemoryChunk
  - Implemented repositories for memory and chunk operations
  - Added API endpoints for memory management
  - Developed memory search and tagging functionality
  - Implemented access tracking for memories
  - Created schemas for memory-related operations
  - Added support for memory chunks with individual embeddings

- **2025-05-29**: Implemented Conversation History UI (CONV-05)
  - Created MessageList component for displaying conversation messages
  - Implemented MessageItem component with role-based styling
  - Added MessageSkeleton component for loading states
  - Implemented timestamp formatting utility for relative time display
  - Added copy and delete functionality for messages
  - Improved auto-scrolling for new messages
  - Updated ConversationDetail page to use the new components

- **2025-05-29**: Implemented Response Streaming (CONV-04)
  - Created ResponseStreamer for Server-Sent Events (SSE) support
  - Implemented LLMResponseStreamer for token-by-token streaming
  - Added streaming endpoints with both REST and WebSocket support
  - Implemented chunked response handling with automatic recovery
  - Created session management for tracking streaming progress
  - Added error handling specific to streaming operations
  - Integrated streaming with the existing conversation system

- **2025-05-29**: Implemented Message Handling System (CONV-03)
  - Created MessageHandler for message processing and validation
  - Implemented MessageFormatter for content standardization
  - Added MessageEventDispatcher for event-driven message handling
  - Created processing pipeline architecture with pluggable processors
  - Implemented content sanitization and role validation
  - Added message format conversions and metadata extraction
  - Created API endpoints for message processing, validation, and formatting

- **2025-05-29**: Implemented Conversation Context Management (CONV-02)
  - Created ConversationContextManager for managing conversation context
  - Implemented ConversationSessionManager for tracking active conversations
  - Added ConversationWindowManager for controlling context window size
  - Created API endpoints for context and session management
  - Implemented context window selection strategies (recent, relevant, hybrid)
  - Added session state tracking for active conversations
  - Added support for conversation context metadata

- **2025-05-29**: Implemented Conversation Data Model (CONV-01)
  - Created conversation and message database models
  - Implemented conversation and message repositories for database operations
  - Added API endpoints for conversation and message management
  - Created database migration for conversation tables
  - Updated frontend API client and store to use real API endpoints
  - Added PaginatedResponse type to the frontend types
  - Integrated conversation endpoints with the frontend conversation store

- **2025-05-29**: Fixed backend and deployment setup
  - Added missing `pydantic-settings` and `asyncpg` dependencies to requirements.txt
  - Fixed vector type definition in the vector.py file
  - Updated API router to use the correct prefix setting
  - Verified the functionality of all services (PostgreSQL, Redis, backend, frontend)
  - Confirmed the correct operation of the pgvector extension
  - Validated API endpoint accessibility and frontend connectivity

- **2025-05-29**: Implemented Frontend Foundation
  - Set up React application with TypeScript
  - Configured Chakra UI theming with customized branding colors
  - Implemented basic page routing with protected routes
  - Created component structure with layouts and pages
  - Set up state management with Zustand stores
  - Implemented API client for backend communication
  - Added ConversationDetail page for viewing and interacting with conversations
  - Ensured accessibility best practices across components

- **2025-05-29**: Completed Documentation for Phase 1
  - Created architecture documentation with component diagrams and data flows
  - Documented API specifications with detailed endpoints and examples
  - Established development guidelines including code style, Git workflow, and PR process
  - Updated the task tracker to mark completion of all Phase 1 tasks
  - Fixed frontend container to include missing react-icons dependency

- **2025-05-28**: Initial project structure and documentation created
  - Created docs directory
  - Added implementation_plan.md
  - Added task_tracker.md
  - Added source_of_truth.md
- **2025-05-28**: Updated documentation with recommendations
  - Updated `implementation_plan.md` with detailed recommendations on task ownership, database migration strategy (Alembic), environment configuration, and testing goals.
  - Updated `task_tracker.md` to include notes on task ownership and refined timelines for better project tracking.
- **2025-05-28**: Updated project branding and AI assistant implementation approach
  - Renamed project to "Mnemosyne" throughout all documentation
  - Updated `implementation_plan.md` to reflect the AI assistant implementation approach, expanded documentation hierarchy, and additional future extension points
  - Updated `task_tracker.md` with AI assistant roles, human review requirements, and implementation guidelines
  - Updated `source_of_truth.md` to reflect new documentation structure and Mnemosyne branding
- **2025-05-28**: Implemented [ENV-01] Set up project repository and structure
  - Created basic project structure following the patterns in `ai_patterns.md`
  - Added `.gitignore` with patterns for Python, Node.js, and environment files
  - Created `README.md` with project overview and setup instructions
  - Added backend structure with FastAPI application skeleton
  - Added frontend structure with React and TypeScript setup
  - Created basic configuration files (`requirements.txt`, `package.json`, `.env.example`)
  - Updated `source_of_truth.md` to reflect the new file structure
- **2025-05-28**: Implemented [ENV-02] Create Docker Compose configuration
  - Created `docker-compose.yml` with services for PostgreSQL, Redis, FastAPI backend, and React frontend
  - Added development-specific configuration in `docker-compose.override.yml`
  - Added production-specific configuration in `docker-compose.prod.yml`
  - Created Dockerfile for PostgreSQL with pgvector extension
  - Created multi-stage Dockerfiles for both backend and frontend services
  - Added nginx configuration for the frontend
  - Created initialization scripts for PostgreSQL
  - Added `.env.example` for environment variables
  - Created `manage.sh` script for convenient container management
  - Updated documentation to reflect Docker configuration
- **2025-05-28**: Implemented [ENV-03] Configure development environment
  - Created Docker-based development environment with consistent tooling
  - Added `docker-compose.dev-tools.yml` for development and testing tools
  - Created development tools Docker image with linting, formatting, and testing capabilities
  - Enhanced `manage.sh` script with comprehensive development commands
  - Added VS Code configuration for Docker-based development
  - Added pre-commit configuration for code quality
  - Set up linting and formatting tools for both backend and frontend
  - Updated `.gitignore` to allow VS Code configuration sharing
- **2025-05-28**: Implemented [BKF-01] Initialize FastAPI application structure
  - Created main FastAPI application file with middleware and error handlers
  - Implemented configuration management with environment variables
  - Set up structured logging system with JSON formatter
  - Added security utilities for authentication
  - Created package structure following the project patterns
  - Added utility functions for common operations
  - Set up health check and version endpoints
- **2025-05-28**: Implemented [BKF-02] Set up database migrations system
  - Configured Alembic for database migrations
  - Created database session management with SQLAlchemy
  - Implemented base model with common fields and functionality
  - Created migration environment and script templates
  - Added migration helper functions for common operations
  - Created a migration management script with CLI interface
  - Set up a base import module to track models for migrations
- **2025-05-28**: Implemented [BKF-03] Configure PostgreSQL with pgvector extension
  - Created vector database integration module for pgvector
  - Implemented VectorMixin for models with embeddings
  - Added utility functions for vector operations and similarity search
  - Created database connection pooling module
  - Implemented database backup and restore utilities
  - Added functions to ensure extension and create vector indexes
- **2025-05-28**: Implemented [BKF-04] Implement basic API endpoints
  - Created API router structure with versioning
  - Implemented health check endpoints with detailed system status
  - Added database dependency injection for API endpoints
  - Set up liveness and readiness probes for Kubernetes compatibility
  - Updated main application to include the API router
- **2025-05-28**: Implemented [BKF-05] Create initial API documentation
  - Created custom OpenAPI schema generator with branding support
  - Implemented customized Swagger UI and ReDoc interfaces
  - Added detailed endpoint descriptions and examples
  - Configured documentation to respect environment settings
  - Set up security schema documentation for future authentication
- **2025-05-28**: Implemented [BKF-06] Define and implement initial/seed data strategy
  - Created seed data management system with environment-specific handlers
  - Implemented development and demo seed handlers with sample data
  - Added CLI interface for seeding and resetting database data
  - Set up priority-based execution order for seed handlers
  - Created pluggable architecture for adding new seed data types

## Specific Files

### Backend

#### Agent Orchestration & Management (Phase 3)
- CrewAI is the orchestration engine for sub-agents, supporting hierarchical agent trees and task delegation.
- AgentManager service manages agent lifecycle, DB-backed orchestration, and exposes APIs/tooling for agent/task management.
- All agent/task state, logs, and orchestration events are persisted in Postgres.
- LangChain remains for the main conversational agent and MCP tool calling.
- Recursive sub-agent creation and robust logging/monitoring are supported.

#### Memory System (Phase 3)
- Cognee-inspired reflection, importance scoring, and hierarchical memory organization are being implemented.
- Memory state is tightly integrated with agent/task logs and orchestration events.

- See updated `architecture.md`, `implementation_plan.md`, and `task_tracker.md` for details.

### Phase 2.5 Backend Status (as of 2025-06-06)
- Backend migration, schema, and test suite are 100% complete and verified in Docker.
- All endpoints and authentication logic are robust and tested.
- Alembic migrations are fully in sync with SQLAlchemy models.
- Container/host mapping issues resolved; workflow is now reliable and repeatable.
- Test suite is self-contained (no reliance on external fixtures).
- Backend is ready for Phase 3 development.
- See `phase2.5_backend_fixes_status.md`, `task_tracker.md`, and README for migration/test workflow and best practices.

- `/backend/app/main.py` - Main FastAPI application with middleware and error handlers
- `/backend/app/core/config.py` - Configuration management with environment variables
- `/backend/app/core/logging.py` - Structured logging system with JSON formatter
- `/backend/app/core/security.py` - Security utilities for authentication
- `/backend/app/core/docs.py` - API documentation customization with branding
- `/backend/app/db/session.py` - Database session management for SQLAlchemy
- `/backend/app/db/base.py` - Base model with common fields and functionality
- `/backend/app/db/vector.py` - Vector database integration with pgvector
- `/backend/app/db/connection.py` - Database connection pooling and health checks
- `/backend/app/db/backup.py` - Database backup and restore utilities
- `/backend/app/db/seed/manager.py` - Seed data management system
- `/backend/app/db/seed/seed_handler.py` - Base class for seed handlers
- `/backend/app/db/seed/development_seed.py` - Development environment seed handler
- `/backend/app/db/seed/demo_seed.py` - Demo environment seed handler
- `/backend/app/db/seed/cli.py` - CLI interface for seed management
- `/backend/app/api/v1/router.py` - API router configuration with versioning
- `/backend/app/api/v1/endpoints/health.py` - Health check endpoints with system status
- `/backend/app/api/dependencies/db.py` - Database dependencies for API endpoints
- `/backend/alembic.ini` - Alembic configuration for database migrations
- `/backend/app/db/migrations/env.py` - Alembic migration environment setup
- `/backend/app/db/migrations/script.py.mako` - Migration script template
- `/backend/app/db/migrations/helpers.py` - Migration helper functions
- `/backend/app/db/manage_migrations.py` - Migration management script with CLI
- `/backend/migrate.py` - CLI entry point for database migrations
- `/backend/seed.py` - CLI entry point for seed data management

### AI Assistant Collaboration Documents (Planned)

#### ai_patterns.md
Standardized implementation patterns for AI assistants working on the Mnemosyne codebase, including:
- Code organization and style guidelines
- Testing patterns and requirements
- Documentation standards
- Error handling approaches
- State management patterns
- Component architecture

#### progress_template.md
Template for AI assistants to report progress on tasks, including:
- Task ID and description
- Current status and completion percentage
- Implementation details and approach
- Challenges encountered and solutions applied
- Next steps and dependencies
- Questions or areas requiring human guidance

#### feedback_process.md
Process for AI assistants to request human feedback during implementation, including:
- When to request feedback (decision points, architecture questions, etc.)
- How to format feedback requests for maximum clarity
- How to respond to and incorporate received feedback
- Escalation paths for critical blockers

#### configuration.md
Comprehensive documentation of all configurable parameters in Mnemosyne, including:
- Environment variables and their purposes
- Configuration file formats and locations
- Default values and valid ranges
- Security considerations for sensitive configuration
- Configuration inheritance and override patterns

### Database Documentation (Planned)

#### schema_changes.md
Documentation of all database schema changes, including:
- Migration version and timestamp
- Description of changes
- Reason for changes
- Backward compatibility considerations
- Rollback procedures

## Changelog

### Recent Changes

- **2025-06-02**: Completed API Testing for Conversation Endpoints (BE-01)
  - Tested and verified key conversation API endpoints functionality
  - Found and documented API behavior differences from original specifications
  - Identified issues with memory endpoints requiring authentication
  - Discovered soft-delete implementation for conversations
  - Updated phase2_testing_guide.md with comprehensive test results
  - Verified that frontend can now safely interact with backend API

- **2025-06-02**: Fixed All Frontend Console Errors (FE-06)
  - Fixed missing exports in client.ts and index.ts modules
  - Fixed syntax error in retryRequest function in client.ts
  - Replaced require() calls with proper ES module imports in index.ts
  - Verified all frontend console errors are resolved
  - Updated phase2_testing_guide.md to reflect completed fixes
  - Application is now stable and error-free for API and UI testing

- **2025-06-03**: Implemented Bulletproof Frontend Fixes (FE-05)
  - Fixed React Router future flags warnings by adding them to index.html head section
  - Resolved custom element registration errors by pre-registering problematic elements
  - Created failsafe health check API implementation with mock responses and background requests
  - Updated debugging guide with comprehensive solutions for all frontend console errors
  - Fixed Docker volume mount caching issues with direct container modifications
