# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Mnemosyne Protocol is a cognitive-symbolic operating system combining personal memory management with collective intelligence. It integrates four existing codebases (Mnemosyne, Shadow, Dialogues, Chatter) into a unified protocol for individual sovereignty and community coordination.

**Core Philosophy**: No mocking or fake implementations. Build real features or defer them.

## Development Commands

### Initial Setup
```bash
# First time setup
./scripts/setup.sh
cp .env.example .env  # Then add API keys

# Start all services
docker-compose up

# Start specific services
docker-compose up backend frontend  # Main app
docker-compose up shadow dialogues  # Agents
docker-compose up collective        # Collective instance
```

### Backend Development (FastAPI + PostgreSQL)
```bash
cd backend

# Virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Database operations
alembic upgrade head              # Apply migrations
alembic revision --autogenerate -m "description"  # New migration
python migrate.py                 # Alternative migration runner

# Run tests
pytest                            # All tests
pytest app/tests/unit/           # Unit tests only
pytest app/tests/integration/    # Integration tests
pytest -k "test_memory"          # Specific test pattern
pytest -v -s                     # Verbose with print statements

# Run backend locally
uvicorn app.main:app --reload --port 8000
```

### Frontend Development (React + TypeScript + Vite)
```bash
cd frontend

# Install and run
npm install
npm run dev              # Development server on :5173
npm run build           # Production build
npm run test            # Run tests
npm run test:watch      # Watch mode
```

### Shadow Orchestration
```bash
cd shadow

# Run Shadow API
python -m uvicorn api.fastapi_server:app --reload --port 8001

# Test collaboration
python test_collaboration.py
python test_memory_integration.py
```

### Dialogues Agents
```bash
cd dialogues

# Run debate system
python src/main.py              # Basic debate
python src/main_dynamic.py      # Dynamic agents
python src/main_with_memory.py  # With memory persistence

# Explore agent memory
./explore_memory.sh
```

## Architecture Overview

### Layer Architecture
```
Layer 4: Collective Codex (Community Intelligence)
    ↓ Selective sharing with contracts
Layer 3: Quiet Network (Discovery & Trust) 
    ↓ Progressive revelation protocol
Layer 2: Deep Signal Protocol (Identity Compression)
    ↓ Symbolic representation as kartouches
Layer 1: Mnemosyne Engine (Personal Memory + Agents)
```

### Service Communication
- **Backend (8000)** ← → **Shadow (8001)**: Agent orchestration via REST
- **Shadow** ← → **Dialogues (8002)**: Philosophical agent loading
- **Backend** ← → **Collective (8003)**: Sharing contracts and collective operations
- **Frontend (3000)** → All services via API calls

### Key Database Models
- `memories`: Personal memory storage with pgvector embeddings
- `sharing_contracts`: Defines what/how users share with collectives
- `collective_knowledge`: Anonymized shared knowledge (k-anonymity enforced)
- `agents`: Agent configurations and orchestration metadata

### Agent System
1. **Shadow Agents** (Python): Engineer, Librarian, Priest - task-specific
2. **Philosophical Agents** (50+ from Dialogues): Deep reflection and debate
3. **Collective Agents**: Matchmaker, Gap Finder, Synthesizer
4. **Mycelium Meta-Agent**: Monitors coherence across all agents

## Critical Implementation Notes

### Privacy Implementation (No Mocking)
- **Week 1**: AES-256-GCM local encryption (real)
- **Week 2**: Selective sharing contracts (real)
- **Week 5**: K-anonymity (k=3 minimum) (real)
- **Deferred to v2**: Zero-knowledge proofs (NOT mocked, build when ready)

### Memory Sharing Flow
1. User creates `SharingContract` specifying domains, depth, duration
2. Memory filtered through contract before export
3. K-anonymity checked before collective storage
4. Revocation tracked via Merkle tree

### A2A Protocol Integration
- Generate Agent Cards for interoperability
- Use existing A2A patterns from industry standard
- Located in: `backend/app/services/agent/`

### Critical Path Dependencies
```
Memory Model → Sharing Contracts → Collective Instance → Synthesis
Shadow Integration → Agent Loading → Mycelium Coherence
```

## Development Workflow

### AI-Assisted Development Model
- AI agents write implementation (2-4 hours per feature)
- Human reviews security and logic
- Target: 5-10 features per day
- Timeline: 2-3 weeks to MVP (not 8-10 weeks)

### Task Tracking
Primary task list: `TASK_TRACKING.md`
- Tasks marked with time estimates in hours (not days)
- Next task: TASK-004 (Memory model extension for sharing)

### Testing Requirements
- Security review mandatory before deployment
- K-anonymity validation on all collective queries
- Integration tests for sharing contracts
- Human verification of privacy guarantees

## Environment Configuration

Required API keys in `.env`:
```
OPENAI_API_KEY=       # For LLM operations
ANTHROPIC_API_KEY=    # Alternative LLM
POSTGRES_PASSWORD=    # Database
SECRET_KEY=          # JWT signing
```

## Key Files for Context

- `MNEMOSYNE_PROTOCOL_SPECIFICATION_v3.md`: Latest clean specification
- `CRITICAL_PATH.md`: Dependencies and blocking chains
- `ROADMAP.md`: Day-by-day implementation plan
- `AI_DEVELOPMENT_STRATEGY.md`: Time compression approach
- `PRIVACY_IMPLEMENTATION.md`: 5-layer privacy architecture

## Important Constraints

1. **No Mocking Policy**: Never create mock implementations. Either build real features or defer to later phases.

2. **Privacy First**: Every collective feature must enforce k-anonymity (k=3 minimum).

3. **Existing Code**: 70% of individual components exist. Focus on integration and collective features.

4. **Naming Convention**: 
   - "The Mnemosyne Protocol" = entire system
   - "Collective Codex" = special Mnemosyne instance for communities
   - "Mnemosyne Engine" = personal memory layer

5. **Testing**: AI writes code, humans validate security and privacy.