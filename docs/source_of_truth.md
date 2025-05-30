# Mnemosyne - Source of Truth

This document serves as the definitive reference for the Mnemosyne project structure, tracking all files and directories as they are created, modified, or deleted.

> **Note:** Mnemosyne (named after the ancient Greek Titan goddess of memory and remembrance) is a web-based conversational AI system with advanced memory capabilities, scheduling features, and agentic task execution abilities. The implementation plan (`implementation_plan.md`) includes a detailed phase-based task tracker table, expanded best practices for testing, documentation, CI/CD, security, deployment, and compliance. Refer to both this document and the implementation plan for the most up-to-date project guidance.

## Project Structure

```
/home/lewis/dev/personal/mnemosyne/
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore file with patterns for Python, Node.js, and env files
├── .pre-commit-config.yaml       # Pre-commit hooks configuration
├── .vscode/                      # VSCode editor configuration
│   ├── extensions.json           # Recommended extensions
│   ├── launch.json               # Debug configurations
│   └── settings.json             # Editor settings
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
│   │   └── utils/                # Utility functions
│   └── tests/                    # Test suite
│       ├── unit/                 # Unit tests
│       ├── integration/          # Integration tests
│       └── e2e/                  # End-to-end tests
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

## Documentation Overview

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
