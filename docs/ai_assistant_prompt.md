# Mnemosyne Phase 3 Coding Assistant Kickoff Prompt

## Current State
- **Phase 2.5 backend is fully fixed, tested, and documented.**
- All migrations, database schema, and backend tests pass 100% in Docker.
- Documentation and source of truth are up to date and reflect the latest backend architecture and workflow.
- The project is ready to begin **Phase 3: Advanced Agent Orchestration and Memory Reflection**.

## Phase 3 Objective
Integrate CrewAI for sub-agent orchestration, build the AgentManager service for agent lifecycle and orchestration, implement Cognee-inspired memory reflection and importance scoring, and update all APIs, documentation, and test plans accordingly.

## Relevant Context
- **Backend stack:** FastAPI, SQLAlchemy ORM, Alembic, PostgreSQL (with pgvector), Redis (with RQ), LangChain for LLM integration and tool calling.
- **Frontend:** React (TypeScript) with Chakra UI (not the focus for Phase 3).
- **Agent orchestration:** CrewAI for sub-agent/task delegation and recursive agent trees.
- **Memory system:** Cognee-inspired reflection, scoring, and hierarchical memory organization.
- **Architecture:** Modular, layered, containerized; all orchestration/memory state must be DB-persisted for auditability.
- **Security/auth:** Mock OAuth2 for dev, user-level access enforced, API tokens planned.
- **User preferences:**
  - All code and migrations must work in Docker.
  - Documentation (especially `docs/source_of_truth.md`) must be updated with every code or architecture change.
  - Minimal, precise code edits; modular, maintainable, and auditable design.
  - Source of truth (`docs/source_of_truth.md`) is the definitive file/project guide.

## Onboarding and Priorities
1. **Review the following docs:**
   - `docs/source_of_truth.md` (project/file structure, history, and all major changes)
   - `docs/implementation_plan.md` (system architecture, phase roadmap, and technical risks)
   - `docs/task_tracker.md` (detailed tasks and priorities)
   - `docs/api_specifications.md` (API endpoints, including planned CrewAI/AgentManager/memory reflection APIs)
   - `docs/architecture.md` (backend, agent, and memory system design)
2. **Understand the modular backend and DB-persistence requirements.**
3. **Prioritize:**
   - Updating documentation and source of truth for every change
   - Keeping all code container-ready (Docker Compose, .env, etc.)
   - Implementing robust, auditable agent orchestration and memory flows
   - Writing clear, maintainable, and well-commented code
4. **Coordinate all changes with the source of truth doc.**

## Phase 3 Kickoff Checklist
- [ ] Update all documentation to reflect CrewAI/AgentManager/Cognee integration plans
- [ ] Add CrewAI and Cognee to backend dependencies (requirements.txt, Docker, etc.)
- [ ] Scaffold AgentManager service (API, DB models, orchestration logic)
- [ ] Design and document new/updated API endpoints for agent orchestration and memory reflection
- [ ] Plan and document a robust test strategy for all new features
- [ ] Ensure all changes are reflected in `docs/source_of_truth.md`

**Reference `docs/source_of_truth.md` for project structure and file guide. All work must be auditable, documented, and container-ready.**


## Project Overview

You are assisting with the development of Mnemosyne, an AI Executive Assistant project with the following characteristics:
- Web-based UI using React with TypeScript and Chakra UI
- Python backend using FastAPI
- Integration with OpenAI compatible LLM via LangChain
- PostgreSQL + pgvector for database and vector storage
- Redis with RQ for lightweight task queuing
- Key features include: conversation management, memory system, task scheduling, and agentic capabilities

## Current Project Status

The project is currently transitioning from Phase 2 (Core Functionality) to Phase 3 (Advanced Features). We have recently completed:
- Basic UI components including chat interface, message display, typing indicators, navigation sidebar, and settings interface
- Backend development of conversation management, LLM integration, and memory storage system
- Debugging and fixing backend dependency issues and API response validation errors
- Initial frontend-backend connectivity testing

---

## CrewAI & Cognee Integration Phase Kickoff Prompt

**Objective:**
Integrate CrewAI for agent/sub-agent orchestration and Cognee-inspired memory reflection into the Mnemosyne project, updating all relevant documentation, plans, and API/tooling.

**Context Acquisition:**
- Review the following docs: `architecture.md`, `implementation_plan.md`, `task_tracker.md`, `api_specifications.md`, `source_of_truth.md`.
- Understand the current backend stack (FastAPI, LangChain, SQLAlchemy, pgvector, Redis) and planned agent/memory architecture.
- Familiarize yourself with CrewAI and Cognee Python modules (see their official docs for API and usage).

**Next Steps:**
1. Update documentation to reflect CrewAI as the orchestration engine for sub-agents, and Cognee-inspired memory reflection/scoring.
2. Plan and document the AgentManager service for agent lifecycle management, DB integration, and tool/API exposure.
3. Specify changes to API/tooling for agent management and memory reflection.
4. Add/adjust tasks in the tracker for all new integration and refactor work.
5. If any prior plans need to be revised or backtracked, note and document this.

**Implementation Guidelines:**
- Keep the conversational agent on LangChain, but add CrewAI for orchestration.
- Ensure all orchestration and memory state is tracked in the DB.
- Enable recursive agent creation and robust logging/monitoring.
- Use Cognee’s memory reflection/scoring as inspiration for the memory service.
- Document all architectural and API changes clearly.

**Deliverables:**
- Updated documentation and plans.
- Clear, actionable tasks for implementation.
- (Optional) Initial code scaffolding for AgentManager and memory enhancements.

---

## Important Resources

Start by reviewing these key documents to understand the project:

1. **Source of Truth**: `/docs/source_of_truth.md` - The definitive reference for project structure and history
2. **Implementation Plan**: `/docs/implementation_plan.md` - Overview of architecture, components, and implementation approach
3. **Task Tracker**: `/docs/task_tracker.md` - Detailed tasks, priorities, and progress status
4. **API Specifications**: `/docs/api_specifications.md` - Detailed API endpoint documentation
5. **Debugging Guide**: `/docs/debugging_guide.md` - Guide for troubleshooting common issues

## Project Structure

The project follows a structured organization:
- `/backend/` - FastAPI Python backend application
  - `/app/api/` - API routes and dependencies
  - `/app/db/` - Database models and repositories
  - `/app/services/` - Business logic services
  - `/app/core/` - Core application components
- `/frontend/` - React TypeScript frontend application
  - `/src/components/` - UI components
  - `/src/pages/` - Page layouts
  - `/src/stores/` - Zustand state management
- `/docs/` - Project documentation
- `/docker/` - Docker configuration files

## Immediate Next Steps

The project is ready to begin implementation of these next priority tasks:

1. **Task Management System**:
   - Implement the task data model (`TASK-01`)
   - Create database schema for tasks
   - Develop basic scheduling system (`TASK-02`)
   - Implement API endpoints for task CRUD operations

2. **Agent Framework**:
   - Define tool registration system (`AGENT-01`)
   - Implement tool execution framework (`AGENT-02`)
   - Create task queue integration using Redis (`AGENT-03`)

3. **Memory Enhancements**:
   - Develop entity extraction features (`MEM-ENH-01`)
   - Implement relationship tracking (`MEM-ENH-02`)

## Development Guidelines

When working on the project:

1. **Documentation**:
   - Always update documentation including the README
   - Keep the source of truth document current when files are created, renamed, or deleted

2. **Code Structure**:
   - Follow the established patterns for new modules
   - Always comment functions
   - Implement comprehensive error handling

3. **Testing**:
   - Write unit tests for new functionality
   - Test API endpoints with curl or Postman
   - Verify frontend-backend connectivity

4. **Docker**:
   - Use 'docker compose' (not 'docker-compose') for all commands
   - Check container logs for debugging
   - Restart services after making changes

5. **Debugging**:
   - Reference the debugging guide for common issues
   - Check for import errors and dependency issues
   - Verify API response validation

## Authentication and Authorization

For testing admin endpoints, you'll need to:
1. Use the development JWT token: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZXYtdXNlci1pZCIsImV4cCI6MTkyNTAyMjgwMCwiaWF0IjoxNjA5NDQyODAwLCJpc19hZG1pbiI6dHJ1ZX0.example`
2. Include it in API requests: `Authorization: Bearer <token>`

## Getting Started

1. Review the task tracker to identify the next task to implement
2. Examine the relevant existing code and documentation
3. Create a development plan with clear milestones
4. Implement the solution following project patterns
5. Update documentation to reflect changes
6. Test thoroughly before considering the task complete

When developing new features, be sure to align with the existing architectural patterns and ensure compatibility with the current implementation. Leverage the memory system when enhancing agent capabilities and maintain a clean separation of concerns between frontend and backend components.
