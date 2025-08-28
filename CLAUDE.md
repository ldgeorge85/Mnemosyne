# Instructions for AI Assistants (Claude, GPT, etc.)

## Project Overview

You are working on **The Mnemosyne Protocol** - a cognitive-symbolic operating system for preserving human agency. This is a personal project that will grow into a platform.

## Core Philosophy

**CRITICAL**: Follow the "No Mocking Policy"
- Build real features or explicitly defer them
- No fake implementations, no placeholder code
- If something can't be built now, mark it as "DEFERRED TO PHASE X"

## Persona & Worldview System

Mnemosyne is not just a technical platform - it embodies a **"numinous confidant"** persona with specific philosophical grounding.

### Baseline Persona Creed
- **Listen first, before speaking**
- **Disclose boundaries, not conceal them**
- **Nudge toward growth, never force**
- **Serve user agency, even when divergent**
- **Keep faith with trust, even under pressure**

### Core Axioms
- **Life is sacred** - Every perspective has dignity
- **Meaning is constructed** - Users author their own purpose
- **Agency is inviolable** - User choices supersede defaults
- **Trust is earned** - Guidance with humility and integrity
- **Balance over dogma** - Avoid religious/political traps

### Four Operational Modes
1. **Confidant** - Deep listener, empathic presence
2. **Mentor** - Guides skill, purpose, development
3. **Mediator** - Navigates conflict, trust, alignment
4. **Guardian** - Protects wellbeing, flags risk

### Implementation Requirements
- Every interaction generates a **receipt** for transparency
- **ICV (Identity Compression Vector)** stores user values
- Persona adapts to user worldview while maintaining core axioms
- Conflict protocol: User agency wins, but log the decision

## Project Structure

```
mnemosyne/
├── docs/              # All documentation (START HERE)
│   ├── spec/         # Protocol specifications
│   ├── guides/       # Implementation guides
│   ├── reference/    # API and database docs
│   └── philosophy/   # Vision and principles
├── backend/          # FastAPI + Python backend
├── frontend/         # React + TypeScript frontend
├── shadow/           # Shadow Council orchestration system
├── dialogues/        # Forum of Echoes - 50+ philosophical voices
├── collective/       # Collective intelligence service
├── scripts/          # Setup and utilities
└── tests/            # Test suites
```

## Key Commands

**CRITICAL: NEVER USE docker-compose (with hyphen). ALWAYS USE docker compose (with space) or docker stack deploy**

```bash
# Setup
./scripts/setup.sh

# Development
docker compose up
docker compose exec backend pytest
docker compose logs -f

# Database
docker compose exec postgres psql -U postgres -d mnemosyne
docker compose run --rm backend alembic upgrade head

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

### 4. Agent System (Phase 1.B Priority!)
- Shadow Council in `shadow/` directory (Artificer, Archivist, Mystagogue, Tactician, Daemon)
- Forum of Echoes in `dialogues/` directory (50+ philosophical voices)
- **NEW**: Agentic flow controller in `backend/app/services/agentic/`
- Use ReAct pattern (Reasoning + Acting)
- Parallel execution with asyncio.gather()
- LLM decisions replace keyword matching

### 5. Privacy Requirements
- K-anonymity minimum of 3
- AES-256-GCM encryption
- No data leaves system without explicit contract

### 6. Testing
- Always write tests for new features
- Run `pytest` before committing
- Security > Features > Performance

## Current Status: Phase 1.A COMPLETE! 🎆

**Agentic Enhancement is WORKING** - All core features operational:
- ✅ Flow controller with ReAct pattern
- ✅ LLM reasoning replacing keyword matching (92% confidence)
- ✅ Parallel action execution with asyncio.gather()
- ✅ Task queries working with LIST_TASKS action
- ✅ Proactive suggestions with error handling
- ✅ SSE streaming with status updates
- ✅ Token management (64k context, unlimited responses)
- ✅ Every decision generates a receipt
- ✅ User override always available

## Next Priority: Phase 1.B - Shadow Integration

1. Connect Engineer, Librarian, Priest agents
2. Wire up 50+ philosophical dialogue agents
3. Implement multi-agent debate orchestration
4. Test agent collaboration and synthesis

## LLM Configuration System

The system supports flexible LLM configuration through environment variables:

### Configuration Modes
```bash
# Temperature Control
LLM_TEMPERATURE_MODE=variable  # "static" or "variable" (static uses env, variable uses persona)
LLM_STATIC_TEMPERATURE=0.7     # Used when mode is "static"

# System Prompt Handling
LLM_SYSTEM_PROMPT_MODE=separate # "separate" or "embedded" (for models without system role)
LLM_SUPPORTS_REASONING_LEVEL=false # Set true for models with reasoning channels

# Model Profile Selection
LLM_MODEL_PROFILE=standard # Profile type (not tied to specific models)
```

### Model Profiles (Generic Capability Types)
- **standard**: Models with system role support (GPT-4, Claude, most OpenAI-compatible)
- **reasoning_channel**: Models with explicit reasoning (o1-preview, certain research models)
- **embedded_system**: Models without separate system role (Gemma, some Llama variants)
- **deepseek**: Models requiring special token handling

### Per-Persona Temperatures (Variable Mode)
- **Confidant**: 0.8 (empathetic, understanding)
- **Mentor**: 0.6 (balanced, instructive)
- **Mediator**: 0.5 (neutral, diplomatic)
- **Guardian**: 0.3 (cautious, protective)
- **Mirror**: 0.7 (reflective, exploratory)

### Testing Configuration
Run comprehensive tests with:
```bash
docker compose exec backend python scripts/test_llm_config.py
```

## Architecture Notes

### Technology Stack
- **Backend**: FastAPI, PostgreSQL, Async SQLAlchemy, Redis/KeyDB
- **Vector Store**: Qdrant (multi-embedding support)
- **Configuration**: Pydantic Settings
- **Frontend**: React, TypeScript, Vite
  - **Current UI**: Chakra UI (working, will migrate later)
  - **Target UI**: shadcn/ui + Tailwind CSS (documented plan)
  - **State**: Zustand (already aligned)
- **AI**: OpenAI/Anthropic/Ollama, LangChain
- **Testing**: Pytest with real integration tests (no mocks)
- **Deployment**: Docker (docker compose / docker stack) → Docker Swarm

### Core Architectural Patterns

#### 1. Agentic Flow Pattern (NEW - Phase 1.A)
```python
class AgenticFlowController:
    async def execute_flow(self, query: str, context: Dict):
        # Step 1: LLM analyzes and plans multiple actions
        actions = await self.plan_actions(query, context)
        
        # Step 2: Execute all actions in parallel
        results = await asyncio.gather(*[
            self.execute_action(action) for action in actions
        ])
        
        # Step 3: Check if more needed
        if await self.needs_more_info(results):
            return await self.execute_flow(query, updated_context)
        
        # Step 4: Proactive suggestions
        suggestions = await self.get_suggestions(results)
        
        return {"response": results, "suggestions": suggestions}
```

#### 2. Configuration Management
```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str
    redis_url: str = "redis://redis:6379/0"
    qdrant_host: str = "qdrant"
    encryption_key: str
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
```

#### 2. Async Pipeline Architecture
```python
class MemoryPipeline(ABC):
    async def process(self, memory: Dict) -> Dict:
        # Pipeline stages run concurrently
        embedding = await self.generate_embedding(memory)
        metadata = await self.extract_metadata(memory)
        importance = await self.calculate_importance(memory)
        return await self.store_memory(memory, embedding, metadata, importance)
    
    async def run(self, memories: List[Dict]):
        tasks = [self.process(m) for m in memories]
        return await asyncio.gather(*tasks, return_exceptions=True)
```

#### 3. Event-Driven Agent Orchestration
```python
class AgentOrchestrator:
    async def trigger_reflection(self, memory: Memory):
        # Publish to Redis stream
        await self.redis.xadd("events:reflection", {
            "memory_id": memory.id,
            "agents": self.select_agents(memory)
        })
        # Agents process in parallel via workers
```

#### 4. Vector Storage with Named Embeddings
```python
# Qdrant with multiple embedding strategies
await vector_store.store({
    "content": openai_embedding,      # 1536d
    "semantic": local_embedding,      # 768d
    "contextual": context_embedding   # 384d
})

## Philosophy Reminders

1. **Build for the builder first** - Every feature must serve the person building it
2. **Sovereignty over convenience** - Privacy and control are non-negotiable
3. **Real or nothing** - No mocking, no faking, no pretending
4. **Depth over breadth** - Better to serve 100 deeply than 10,000 shallowly

## Common Tasks

### Adding a New Agent
1. Create agent class inheriting from `BaseAgent`
2. Define system prompt and LangChain tools
3. Implement async reflection logic
4. Register with orchestrator
5. Test with real memories (no mocks)

### Implementing an API Endpoint
1. Check specification in `docs/reference/API.md`
2. Implement in appropriate router with Pydantic models
3. Add async processing with pipelines
4. Write real integration tests
5. Add OpenAPI documentation

### Adding a Database Table
1. Create Async SQLAlchemy model
2. Generate migration: `alembic revision --autogenerate`
3. Review migration file
4. Apply: `alembic upgrade head`
5. Add indexes for performance
6. Create corresponding Qdrant collection if needed

### Setting Up a Pipeline
1. Inherit from `MemoryPipeline` base class
2. Implement `process()` method with async stages
3. Add error handling and retry logic
4. Register with pipeline registry
5. Test with concurrent processing

### Adding Event Handlers
1. Define event schema with Pydantic
2. Create handler function (async)
3. Register pattern with webhook handler
4. Set up Redis stream consumer
5. Test with real events

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
4. Review existing patterns in code

## Remember

You're not building a product. You're building a new way of thinking about cognitive sovereignty. Every line of code should reflect that philosophy.

**Current Phase**: Building personal tool (1 user)
**Next Phase**: Early adopters (10 users)
**Philosophy**: Real implementation or explicit deferral

---

*"For those who see too much and belong nowhere."*