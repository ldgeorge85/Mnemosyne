# Mnemosyne Project - Phase 2 Onboarding Prompt

## Project Context

I'm working on Mnemosyne, an AI Executive Assistant Agent project with the following architecture:

- **Frontend**: React with TypeScript and Chakra UI
- **Backend**: Python-based FastAPI
- **Database**: PostgreSQL with pgvector for vector embeddings
- **Integration**: LangChain for LLM capabilities
- **Task Queue**: Redis with RQ for background jobs

We've just completed Phase 1 (Setup and Foundation) and are now beginning Phase 2 (Core Functionality). All essential documentation is in the `/docs` directory, with containerized development using Docker Compose.

## Current Project Status

### Phase 1 Completion
We have successfully completed all Phase 1 tasks:
- Environment setup with Docker Compose
- Backend foundation with FastAPI
- PostgreSQL configured with pgvector extension
- Frontend foundation with React, TypeScript, and Chakra UI
- Comprehensive documentation

### Frontend Components
Key frontend components developed so far:
- Main application layout with header, sidebar, and footer
- Basic page components (Home, Dashboard, Login, Settings, etc.)
- Conversation components including a ConversationDetail view
- State management with Zustand stores
- API client for backend communication

### Backend Services
The backend currently includes:
- API router structure with versioned endpoints
- Database connection with PostgreSQL and pgvector
- Health check endpoints
- Database models and migrations system

## Key Documentation to Review

To get fully onboarded, please review:

1. `/docs/architecture.md` - System architecture overview
2. `/docs/api_specifications.md` - API endpoints documentation
3. `/docs/development_guidelines.md` - Code style and process guidelines
4. `/docs/source_of_truth.md` - Project structure and file tracking
5. `/docs/task_tracker.md` - Project phases and specific tasks

## Next Steps for Phase 2

### How to Check What's Next
1. Review `/docs/task_tracker.md` under the "Phase 2" section
2. Check which tasks are marked with highest priority (H)
3. Verify dependencies are completed (all Phase 1 tasks are done)
4. Look at the detailed implementation guidance in `/docs/implementation_plan.md`

### Initial Phase 2 Tasks

We should begin with the following key tasks from Phase 2:

1. **Conversation System**:
   - [CONV-01] Implement conversation data model
   - [CONV-02] Create conversation context management
   - [CONV-03] Develop message history handling

2. **Memory System**:
   - [MEM-01] Implement memory storage system
   - [MEM-02] Create memory retrieval mechanism
   - [MEM-03] Implement embedding generation

3. **Basic UI**:
   - [UI-01] Develop chat interface components
   - [UI-02] Create message display system
   - [UI-04] Design and implement sidebar/navigation

## Development Requirements

### Docker-Based Development
- Always use Docker containers for development
- Run services with `docker compose up -d`
- Use `docker compose logs [service]` to check service logs
- Make sure container dependencies are listed in Dockerfile

### Documentation Updates
- Keep `source_of_truth.md` updated when creating/modifying files
- Document all API endpoints in `api_specifications.md`
- Follow code style from `development_guidelines.md`
- Update `task_tracker.md` when tasks are completed

### Development Process
1. Select a task from Phase 2
2. Verify its dependencies are completed
3. Implement the required functionality
4. Update documentation
5. Mark task as completed in the task tracker

## Getting Started on Phase 2

Let's start with implementing the conversation data model [CONV-01]:

1. First, examine the current database models in `/backend/app/db/models/`
2. Review the types defined in `/frontend/src/types/index.ts`
3. Create the conversation and message models for the database
4. Implement the necessary API endpoints according to `/docs/api_specifications.md`
5. Update the frontend conversation store to connect with the backend
6. Test the conversation creation and retrieval flow

## Working With This Project

### Common Commands
- Start containers: `docker compose up -d`
- View logs: `docker compose logs -f [service]`
- Run backend tests: `docker compose exec backend pytest`
- Access frontend: http://localhost:3000
- Access API documentation: http://localhost:8000/docs

### Best Practices
- Keep commits focused on specific tasks
- Update documentation as you implement features
- Follow the development guidelines for code style
- Clean up unused code and files
- Ensure proper error handling in both frontend and backend
- Use TypeScript types consistently

Please review the project structure and documentation before proceeding with Phase 2 implementation.
