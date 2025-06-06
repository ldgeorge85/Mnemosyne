# Mnemosyne Project - AI Assistant Prompt

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
