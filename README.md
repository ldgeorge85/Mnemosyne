
<img align="center"
     src="https://github.com/ldgeorge85/Mnemosyne/blob/75c4a7e251995b1f3ffa7d6a848846cabcf5c687/artwork/logo.png"
     height="420px"
     style="padding-right: 20px">

# Mnemosyne

A web-based conversational AI system with advanced memory capabilities, scheduling features, and agentic task execution abilities.

## Project Overview

### Phase 3: CrewAI & Cognee Integration
- CrewAI will be used for agent/sub-agent orchestration, task delegation, and hierarchical agent trees.
- AgentManager and MemoryReflectionService are now fully implemented and integrated (as of 2025-06-08T22:42:40-07:00), with all endpoints and DB models live.
- LangChain remains for the main conversational agent and MCP tool calling.
- Cognee-inspired memory reflection, importance scoring, and hierarchical organization are now fully implemented.
- See `architecture.md`, `implementation_plan.md`, and `task_tracker.md` for details.

Named after the ancient Greek Titan goddess of memory and remembrance, Mnemosyne embodies the preservation and utilization of knowledge to enhance personal productivity. This AI Executive Assistant provides a comprehensive system for managing conversations, storing memories, scheduling tasks, and executing actions through an agentic framework.

## Key Features

- **Conversation Management**: Natural language interface with context tracking and history
- **Advanced Memory System**: Automatic information extraction and relevance-based retrieval
- **Task Scheduling**: Calendar integration and reminder generation
- **Agentic Capabilities**: Extensible tool framework for autonomous task execution

## Technology Stack

### Backend
- **FastAPI**: High-performance API framework for Python
- **PostgreSQL + pgvector**: Database with vector storage capabilities
- **Redis + RQ**: Task queue and caching system
- **LangChain**: LLM integration framework

### Frontend
- **React**: UI framework with TypeScript
- **Chakra UI**: Component library for accessible, customizable UI
- **Zustand**: State management

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.9+
- Node.js 16+

### Development Setup

### Backend Development

**Important:** After making changes to backend Python code, you must run:

```bash
docker compose build backend && docker compose up -d backend
```

This ensures your changes are picked up by the running container. A simple `docker compose restart backend` is not sufficient for code changes (only for environment/config changes).

### Recent Fixes
- 2025-06-07: Fixed missing imports in `backend/app/api/v1/endpoints/memories.py` (Path, Query, MemorySearchResponse, MemorySearchQuery, MemoryStatistics, MemoryChunkResponse, MemoryChunkCreate, MemoryChunkUpdate).
- Backend API will fail to start or respond if container is not rebuilt after such changes.

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/mnemosyne.git
   cd mnemosyne
   ```

2. Start the development environment:
   ```bash
   docker compose up -d
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

## Project Structure

```
/
├── backend/               # Python/FastAPI backend
│   ├── app/               # Application code
│   │   ├── api/           # API routes
│   │   ├── core/          # Core functionality
│   │   ├── db/            # Database models and migrations
│   │   ├── services/      # Business logic services
│   │   └── utils/         # Utility functions
│   └── tests/             # Test suite
├── frontend/              # React/TypeScript frontend
│   ├── public/            # Static assets
│   ├── src/               # Source code
│   │   ├── api/           # API client
│   │   ├── components/    # UI components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── pages/         # Page components
│   │   ├── stores/        # Zustand stores
│   │   └── utils/         # Utility functions
│   └── tests/             # Test suite
├── docs/                  # Documentation
└── docker/                # Docker configuration
```

## Documentation

Comprehensive documentation is available in the `/docs` directory:

- **Implementation Plan**: `/docs/implementation_plan.md`
- **Task Tracker**: `/docs/task_tracker.md`
- **Source of Truth**: `/docs/source_of_truth.md`
- **AI Patterns**: `/docs/ai_patterns.md`

## License

[MIT License](LICENSE)
