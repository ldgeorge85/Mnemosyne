# The Mnemosyne Protocol
*A Cognitive-Symbolic Operating System for Preserving Human Agency*

[![Status](https://img.shields.io/badge/Status-Active%20Development-yellow)]()
[![Security](https://img.shields.io/badge/Security-Needs%20Activation-red)]()
[![Documentation](https://img.shields.io/badge/Docs-Updated-green)]()

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

⚠️ **CRITICAL**: Security architecture exists but needs activation. See [Strategic Reset](docs/decisions/003-strategic-reset.md).

### What Works
- ✅ Core memory engine with vector search
- ✅ Basic chat interface
- ✅ Docker containerization
- ✅ Agent orchestration system
- ✅ Philosophical debate engine

### Needs Immediate Fix
- 🔴 Authentication disabled (components exist, need wiring)
- 🔴 Chat endpoint user object error
- 🔴 Memory CRUD incomplete
- 🔴 Frontend auth flow not connected

### Next Actions
1. **Activation Sprint** - Enable existing security components
2. **Core Features** - Fix chat and memory operations
3. **Documentation** - Align docs with reality

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
1. **Memory Engine** - Personal memory augmentation
2. **Agent System** - AI-mediated interactions
3. **Identity Layer** - W3C DIDs and Verifiable Credentials
4. **Trust Network** - Progressive trust building
5. **Collective Engine** - Group intelligence emergence

## Documentation

### Essential Reading
- **[Project Primer](docs/MNEMOSYNE_PRIMER.md)** - High-level introduction
- **[Integrated Vision](docs/INTEGRATED_VISION_2025.md)** - Strategic roadmap
- **[Protocol Spec](docs/spec/PROTOCOL.md)** - Technical details
- **[Philosophy](docs/philosophy/)** - Core principles

### For Developers
- **[CLAUDE.md](CLAUDE.md)** - AI assistant instructions
- **[Architecture Decisions](docs/decisions/)** - Key technical choices
- **[Implementation Guides](docs/guides/)** - How-to documentation

### Research & Innovation
- **[Research Documentation](docs/research/)** - Academic foundations
- **[AI-MC Integration](docs/aimc/)** - AI-mediated communication
- **[Hypotheses](docs/hypotheses/)** - Experimental features

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