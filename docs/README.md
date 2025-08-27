# Mnemosyne Protocol Documentation

## Core Documentation

### 📍 Start Here
1. **[MNEMOSYNE_PRIMER.md](MNEMOSYNE_PRIMER.md)** - Vision, philosophy, and what we're building
2. **[ROADMAP_2025.md](ROADMAP_2025.md)** - Development roadmap and phases  
3. **[IMMEDIATE_TASKS.md](IMMEDIATE_TASKS.md)** - Current sprint tasks (Phase 1.A: 100% COMPLETE)

### 🛠 Development
- **[AI_DEVELOPMENT_GUIDE.md](AI_DEVELOPMENT_GUIDE.md)** - Instructions for AI assistants
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Deployment and infrastructure
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines

## Project Structure

### Technical Documentation
- **[backend/](backend/)** - Backend architecture and API reference
  - `ARCHITECTURE.md` - Backend design and patterns
  - `API_REFERENCE.md` - Complete API documentation
- **[frontend/](frontend/)** - Frontend architecture and components
  - `ARCHITECTURE.md` - Frontend design and patterns
  - `COMPONENT_GUIDE.md` - Component documentation

### Specifications
- **[spec/](spec/)** - Technical specifications
  - `OVERVIEW.md` - System overview
  - `PROTOCOL.md` - Protocol details
  - `PERSONA_WORLDVIEW.md` - Persona system

### Philosophy
- **[philosophy/](philosophy/)** - Core principles
  - `SCIENTIFIC_INTEGRITY.md` - Research approach
  - `SUSTAINABLE_GROWTH.md` - Growth philosophy

### Architecture
- **[decisions/](decisions/)** - Architecture decision records
  - `001-production-architecture.md` - Production setup
  - `002-dual-track-architecture.md` - Dual-track approach
  - `003-strategic-reset.md` - Strategic realignment

### Research
- **[research/](research/)** - Research papers and findings
- **[aimc/](aimc/)** - AI-mediated communication research

## Current Status (2025-08-27)

### ✅ Complete
- **Security**: Auth activated, vulnerabilities patched, user data protected
- **Agentic Flow**: ReAct pattern with 92% confidence in persona selection (PHASE 1.A COMPLETE)
- **Task Queries**: LIST_TASKS action working, displays user's tasks correctly
- **Backend**: Memory CRUD, Chat SSE, Tasks, 5 Personas, Trust system
- **Frontend**: Chat default page, conversation history, memory UI, auto-focus
- **UI**: Standardized across all pages, pagination, persona badges per message
- **Token Management**: 64k context window, unlimited responses
- **Infrastructure**: Docker, PostgreSQL, Redis, Qdrant all operational

### 🔄 Next Priority (Phase 1.B)
- Shadow agent integration (Engineer, Librarian, Priest)
- Dialogue agent connection (50+ philosophical agents)
- Wire CREATE_MEMORY action to executor
- Wire UPDATE_TASK action to executor
- Test multi-agent collaboration

### 🔴 Next Priority (Phase 1.C-D)
- Graduated sovereignty (Protected/Guided/Sovereign modes)
- Onboarding personas for different worldviews
- OAuth providers
- CI/CD pipeline

## Quick Start

```bash
# Setup
./scripts/setup.sh

# Development
docker compose up

# Access
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
```

## Key Concepts

**Mnemosyne Protocol** is a cognitive-symbolic operating system for preserving human agency through:

1. **Identity Compression (ICV)** - Holographic representation of worldview
2. **Progressive Trust Exchange** - Gradual relationship building
3. **Collective Intelligence** - Emergent group cognition
4. **Contextual Presentation** - Adaptive information masking
5. **Numinous Confidant** - Persona system with five modes (including Mirror)
6. **Joy Metrics** - System health through delight measurement

## Development Philosophy

- **Build for the builder first** - Personal tool before platform
- **Sovereignty over convenience** - Privacy is non-negotiable
- **Real or nothing** - No mocking, no faking
- **Depth over breadth** - Serve 100 deeply vs 10,000 shallowly

---

*"For those who see too much and belong nowhere."*