# Instructions for AI Assistants (Claude, GPT, etc.)

## Project Overview

You are working on **The Mnemosyne Protocol** - a cognitive-symbolic operating system for preserving human agency. This is a personal project that will grow into a platform.

## Core Philosophy

**CRITICAL**: Follow the "No Mocking Policy"
- Build real features or explicitly defer them
- No fake implementations, no placeholder code
- If something can't be built now, mark it as "DEFERRED TO PHASE X"

## Project Structure

```
protocol/
├── docs/              # All documentation (START HERE)
│   ├── spec/         # Protocol specifications
│   ├── guides/       # Implementation guides
│   ├── reference/    # API and database docs
│   └── philosophy/   # Vision and principles
├── backend/          # FastAPI + Python backend
├── frontend/         # React + TypeScript frontend
├── shadow/           # Agent orchestration system
├── dialogues/        # 50+ philosophical agents
├── collective/       # Collective intelligence service
├── scripts/          # Setup and utilities
└── archive/          # Old documentation (for reference)
```

## Key Commands

```bash
# Setup
./scripts/setup.sh

# Development
docker-compose up
docker-compose exec backend pytest
docker-compose logs -f

# Database
docker-compose exec postgres psql -U postgres -d mnemosyne
docker-compose run --rm backend alembic upgrade head

# Git
git add -A && git commit -m "message"
```

## Working Guidelines

### 1. Always Read First
- Read relevant files before editing
- Check `docs/` for specifications
- Review existing code patterns

### 2. Database Schema
The schema needs completion. Key tables:
- `memories` - Personal memory storage with vector embeddings
- `users` - Authentication (NEEDS IMPLEMENTATION)
- `signals` - Deep Signal storage (NEEDS IMPLEMENTATION)
- `sharing_contracts` - Collective sharing rules
- `trust_relationships` - Trust scores (NEEDS IMPLEMENTATION)

### 3. API Endpoints
See `docs/reference/API.md` for complete specification. Many endpoints need implementation.

### 4. Agent System
- Base agents in `shadow/` directory
- Philosophical agents in `dialogues/` directory
- Resource management needed for 50+ agents

### 5. Privacy Requirements
- K-anonymity minimum of 3
- AES-256-GCM encryption
- No data leaves system without explicit contract

### 6. Testing
- Always write tests for new features
- Run `pytest` before committing
- Security > Features > Performance

## Current Priorities (Week 1)

1. Complete database schema with auth tables
2. Implement core memory operations
3. Basic agent orchestration
4. Authentication system
5. Docker deployment

## Architecture Notes

### Technology Stack
- **Backend**: FastAPI, PostgreSQL, pgvector, Redis
- **Frontend**: React, TypeScript, Vite
- **AI**: OpenAI/Anthropic/Ollama
- **Deployment**: Docker Compose → Kubernetes

### Key Patterns
```python
# Memory capture pattern
async def capture_memory(content: str) -> Memory:
    embedding = generate_embedding(content)
    metadata = extract_metadata(content)
    importance = calculate_importance(content)
    return store_memory(content, embedding, metadata, importance)

# Agent reflection pattern
async def reflect(memory: Memory) -> Reflection:
    prompt = build_prompt(memory)
    response = await llm_call(prompt)
    return process_reflection(response)
```

## Philosophy Reminders

1. **Build for the builder first** - Every feature must serve the person building it
2. **Sovereignty over convenience** - Privacy and control are non-negotiable
3. **Real or nothing** - No mocking, no faking, no pretending
4. **Depth over breadth** - Better to serve 100 deeply than 10,000 shallowly

## Common Tasks

### Adding a New Agent
1. Create agent class inheriting from `BaseAgent`
2. Define system prompt
3. Implement reflection logic
4. Add to agent registry
5. Test with real memories

### Implementing an API Endpoint
1. Check specification in `docs/reference/API.md`
2. Implement in appropriate router
3. Add input validation
4. Write tests
5. Update documentation if needed

### Adding a Database Table
1. Create SQLAlchemy model
2. Generate migration: `alembic revision --autogenerate`
3. Review migration file
4. Apply: `alembic upgrade head`
5. Add indexes for performance

## Warnings

⚠️ **DO NOT**:
- Add features for hypothetical users
- Implement fake/mock functionality
- Compromise on privacy
- Add unnecessary dependencies
- Over-engineer before need

✅ **DO**:
- Build what you need today
- Test with real data
- Maintain security first
- Keep it simple
- Document decisions

## Getting Help

1. Check `docs/` directory first
2. Review similar code in codebase
3. Look at test files for examples
4. Check archive/ for historical context

## Remember

You're not building a product. You're building a new way of thinking about cognitive sovereignty. Every line of code should reflect that philosophy.

**Current Phase**: Building personal tool (1 user)
**Next Phase**: Early adopters (10 users)
**Philosophy**: Real implementation or explicit deferral

---

*"For those who see too much and belong nowhere."*