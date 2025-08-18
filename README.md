<div align="center">
<img src="https://github.com/ldgeorge85/Mnemosyne/blob/75c4a7e251995b1f3ffa7d6a848846cabcf5c687/artwork/logo.png"
     alt="Mnemosyne Logo"
     height="420px">

# 🏛️ The Mnemosyne Protocol
*A Cognitive-Symbolic Operating System for Preserving Human Agency*

[![Status](https://img.shields.io/badge/Status-Active%20Development-yellow)]()
[![Security](https://img.shields.io/badge/Security-Needs%20Activation-red)]()
[![Documentation](https://img.shields.io/badge/Docs-Updated-green)]()

</div>

## Vision

A world where your AI doesn't just assist you—it truly represents you. Where digital interactions preserve rather than erode human agency. Where collective intelligence emerges from individual sovereignty rather than corporate aggregation.

**Read the full vision**: [MNEMOSYNE_PRIMER.md](docs/MNEMOSYNE_PRIMER.md)

## Quick Start

```bash
# Clone and setup
git clone https://github.com/ldgeorge85/Mnemosyne.git
cd Mnemosyne

# Run setup script
./scripts/setup.sh

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker compose up

# Access the application
open http://localhost:3000
```

## Current Status

⚠️ **CRITICAL**: The project has sophisticated theoretical concepts that are [UNVALIDATED]. Building proceeds on dual tracks.

### Track 1: Proven Technologies (Working)
- ✅ Backend authentication via AuthManager
- ✅ Database services (PostgreSQL, Redis, Qdrant)
- ✅ Docker infrastructure
- ✅ Basic FastAPI structure

### Track 2: Theoretical Concepts (Require Validation)
- ❓ Identity Compression (ICV) - 128-bit identity representation
- ❓ Progressive Trust Exchange - Cryptographic staged disclosure
- ❓ Resonance Algorithms - Mathematical compatibility prediction
- ❓ Collective Intelligence - Emergent meta-minds

### Immediate Priorities
- 🔴 Phase 0.5: Code cleanup - Remove competing auth patterns
- 🔴 Phase 1: Core features - Memory CRUD, chat, basic persona
- 🟡 Phase 1.5: Research validation - ICV empirical testing

See [IMMEDIATE_TASKS.md](docs/IMMEDIATE_TASKS.md) for detailed execution plan.

## Architecture

### Technology Stack
- **Backend**: FastAPI + Python + Async SQLAlchemy
- **Frontend**: React + TypeScript + Tailwind CSS + shadcn/ui
- **Vector Store**: Qdrant (multi-embedding support)
- **Database**: PostgreSQL with pgvector
- **Streaming**: Redis/KeyDB
- **AI/LLM**: OpenAI-compatible endpoints
- **Deployment**: Docker Compose → Kubernetes

### Core Components

#### Implementable Now
1. **Memory Engine** - Personal memory with vector search
2. **Numinous Confidant Persona** - Philosophical AI personality
3. **Basic Agent System** - LLM-powered assistance

#### Requires Validation First
4. **Identity Compression (ICV)** - 128-bit identity representation
5. **Progressive Trust Exchange** - Cryptographic disclosure protocol
6. **Resonance System** - Mathematical compatibility prediction
7. **Collective Intelligence** - Emergent group cognition

## Documentation

### Essential Reading
- **[Project Primer](docs/MNEMOSYNE_PRIMER.md)** - Complete vision with 6 core innovations
- **[Roadmap](docs/ROADMAP_2025.md)** - Dual-track development plan
- **[Integrated Vision](docs/INTEGRATED_VISION_2025.md)** - Strategic analysis
- **[Immediate Tasks](docs/IMMEDIATE_TASKS.md)** - Tactical execution plan

### Technical Deep Dive
- **[Concepts Deep Dive](docs/CONCEPTS_DEEP_DIVE.md)** - Complete theoretical framework
- **[Protocol Spec](docs/spec/PROTOCOL.md)** - Technical specifications
- **[Persona & Worldview](docs/spec/PERSONA_WORLDVIEW.md)** - Agent personality system

### For Developers
- **[CLAUDE.md](CLAUDE.md)** - AI assistant instructions
- **[AI Development Guide](docs/AI_DEVELOPMENT_GUIDE.md)** - How to use AI assistants
- **[Security Log](docs/SECURITY_ACTIVATION_LOG.md)** - Auth activation status

## Philosophy

### Core Principles
1. **Sovereignty First** - Individual control over data, identity, and participation
2. **Real Implementation** - No mocking, no faking—build what works
3. **Privacy by Design** - Cryptographic guarantees, not promises
4. **Progressive Complexity** - Simple core, validated additions
5. **Human Agency First** - Technology serves humanity, not vice versa

### Who This Is For
- Those who see the machinery behind the world
- Those who refuse performative knowledge spaces
- Those who seek trustable cognition without spectacle
- Those who want to preserve what makes us human

## Contributing

We're looking for collaborators who share the vision of digital sovereignty and collective intelligence.

### Immediate Needs
- **Security Activation** - Wire existing auth components
- **Core Features** - Fix chat and memory operations
- **Testing** - Increase coverage and integration tests
- **Documentation** - Keep docs aligned with reality

See [Contributing Guide](docs/CONTRIBUTING.md) for details.

## Project Structure

```
mnemosyne/
├── backend/               # FastAPI + Python backend
├── frontend/              # React + TypeScript frontend
├── shadow/                # Agent orchestration system
├── dialogues/             # Philosophical agents (50+)
├── collective/            # Collective intelligence templates
├── docs/                  # All documentation
│   ├── decisions/         # Architecture decisions
│   ├── research/          # Academic foundations
│   ├── spec/              # Protocol specifications
│   └── MNEMOSYNE_PRIMER.md  # Start here
├── scripts/               # Setup and utilities
└── CLAUDE.md              # AI assistant instructions
```

## License

MIT License (see [LICENSE](LICENSE))

## Acknowledgments

See [ATTRIBUTION.md](ATTRIBUTION.md) for credits and acknowledgments.

---

*"For those who see too much and belong nowhere, building bridges to everywhere."*

**Repository**: [github.com/ldgeorge85/Mnemosyne](https://github.com/ldgeorge85/Mnemosyne)  
**Status**: Active Development - Seeking Collaborators