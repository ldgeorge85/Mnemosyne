<div align="center">
<img src="https://github.com/ldgeorge85/Mnemosyne/blob/75c4a7e251995b1f3ffa7d6a848846cabcf5c687/artwork/logo.png"
     alt="Mnemosyne Logo"
     height="420px">

# 🏛️ The Mnemosyne Protocol
*A Cognitive-Symbolic Operating System for Preserving Human Agency*

[![Status](https://img.shields.io/badge/Status-Active%20Development-yellow)]()
[![Security](https://img.shields.io/badge/Security-Activated-green)]()
[![Documentation](https://img.shields.io/badge/Docs-Updated-green)]()

</div>

## Vision

A world where your AI doesn't just assist you—it truly represents you. Where digital interactions preserve rather than erode human agency. Where collective intelligence emerges from individual sovereignty rather than corporate aggregation.

**The Mnemosyne Protocol is building cognitive sovereignty infrastructure** - technology that preserves human agency in an age of AI-mediated reality.

**Read the full vision**: [INTEGRATED_VISION_2025.md](docs/INTEGRATED_VISION_2025.md)

## Quick Start

### Development Setup

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

### Production Deployment

```bash
# Configure production environment
cp .env.prod .env.prod
nano .env.prod  # Add your domain and API keys

# Test configuration
./test_production_config.sh

# Deploy with SSL
./deploy.sh deploy
./deploy.sh ssl

# Your app is now live at https://your-domain.com
```

See [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for complete production setup.

## Current Status

The project implements **cognitive sovereignty** through proven technologies while researching advanced capabilities.

### Working Now
- ✅ **Authentication System** - Secure, consolidated auth with JWT
- ✅ **Memory System** - Full CRUD with embeddings, search, and UI
- ✅ **Vector Storage** - Qdrant integration for semantic search
- ✅ **Chat System** - Conversations with streaming, history, and persona
- ✅ **Task System** - Complete with toned-down gamification
- ✅ **Persona System** - 4 modes with worldview adaptation
- ✅ **UI Shell** - Persistent navigation with all features integrated
- ✅ **Infrastructure** - Docker, PostgreSQL, Redis, Qdrant all operational

### In Active Development
- 🔄 **Receipts System** - Database storage for transparency audit trail
- 🔄 **Auth Providers** - OAuth and API key authentication
- 🔄 **Testing & Quality** - Integration tests and CI/CD pipeline
- 🔄 **Trust Networks** - Progressive relationship building

### Research Track (Parallel)
- 🔬 **Game Mechanics** - Task gamification and engagement patterns
- 🔬 **Identity Compression** - Holographic identity representation
- 🔬 **Productive Variation** - Controlled randomness for creativity
- 🔬 **Natural Clustering** - Organic group formation patterns
- 🔬 **Joy Metrics** - Measuring system delight and user creativity

### Next Priorities
- 🔴 **Receipts Database** - Store interaction receipts for audit trail
- 🔴 **Receipt UI** - View transparency logs and interactions
- 🟡 **OAuth Provider** - Implement social login authentication
- 🟡 **API Key Auth** - Service account authentication
- 🟢 **Integration Tests** - Comprehensive test coverage

See [IMMEDIATE_TASKS.md](docs/IMMEDIATE_TASKS.md) for detailed execution plan.

## Architecture

### Technology Stack
- **Backend**: FastAPI + Python + Async SQLAlchemy
- **Frontend**: React + TypeScript + Tailwind CSS + shadcn/ui
- **Vector Store**: Qdrant (multi-embedding support)
- **Database**: PostgreSQL with pgvector
- **Streaming**: Redis/KeyDB
- **AI/LLM**: Model-agnostic (user-configured endpoints)
- **Deployment**: Docker Compose → Kubernetes

### Core Components

#### Production Ready
1. **Memory Engine** - Personal memory with vector search and embeddings
2. **Sovereign Identity System** - User-owned data, user-chosen AI
3. **Adaptive Personas** - Context-aware AI personalities
4. **Trust Networks** - Progressive relationship building
5. **Task System** - Time-aware action layer with natural gamification

#### Advanced Capabilities (Research)
6. **Identity Compression** - Holographic identity representation
7. **Productive Variation** - Creative randomness injection
8. **Natural Clustering** - Organic group formation
9. **Joy Engineering** - System delight optimization
10. **Game Mechanics** - Ethical gamification patterns

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
1. **Cognitive Sovereignty** - Users own their data and control their AI choices
2. **Resistance to Feudalism** - Prevent centralized control of cognition
3. **Privacy Through Architecture** - Sovereignty embedded, not added
4. **Progressive Trust** - Relationships build naturally over time
5. **Joy as Metric** - Systems without delight are already captured

### Design Philosophy
- **Contextual Presentation** - Adaptive masking based on context
- **Useful Infrastructure** - Value first, sovereignty inherent
- **Natural Emergence** - Let advanced features grow organically
- **Model Agnostic** - Interface with any AI endpoint you choose

### Who This Is For
- Those resisting cognitive feudalism
- Those building alternatives to centralized AI
- Those preserving human agency
- Those who value both utility and sovereignty

## Contributing

We're looking for collaborators who share the vision of digital sovereignty and collective intelligence.

### Immediate Needs
- **Persona System** - Complete 4-mode adaptive personality
- **ICV Research** - Validate identity compression hypothesis
- **Trust Networks** - Design progressive disclosure protocols
- **Testing** - Increase coverage and integration tests

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