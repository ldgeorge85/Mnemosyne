<div align="center">
<img src="https://github.com/ldgeorge85/Mnemosyne/blob/75c4a7e251995b1f3ffa7d6a848846cabcf5c687/artwork/logo.png"
     alt="Mnemosyne Logo"
     height="420px">

# 🏛️ The Mnemosyne Protocol
*A Cognitive-Symbolic Operating System for Preserving Human Agency*

[![Status](https://img.shields.io/badge/Status-Active%20Development-yellow)]()
[![Security](https://img.shields.io/badge/Security-Activated-green)]()
[![Documentation](https://img.shields.io/badge/Docs-Updated-green)]()
[![Agentic](https://img.shields.io/badge/Agentic%20Flow-Live-blue)]()

</div>

## 📢 Alpha Release - October 2025

**This is an alpha release of a solo research project.** See [ALPHA_RELEASE.md](ALPHA_RELEASE.md) for expectations and context.

## 🎆 Current Status: Research Platform Operational 🎆

**Phase 1.B - Substantially Complete**: Core primitives working, research validation ongoing
- ✅ Trust Primitive (75% complete) - Appeals resolution, multi-party negotiation, cryptographic receipts
- ✅ Agentic orchestration - Shadow Council & Forum of Echoes generating perspectives
- ✅ Tool registry with auto-discovery and parallel execution
- ✅ Memory/Task executors integrated (CREATE_MEMORY, UPDATE_TASK)
- ✅ Receipt system with SHA-256 hashing for transparency
- 🔄 Digital signatures needed for non-repudiation
- 🔄 Identity Compression Vectors (conceptual, no implementation)
- 🔄 Zero-knowledge proofs (research phase)

**What's Next**: Focus on completing Trust Primitive with working demonstrations

## Quick Introduction

**Start here**: [PRIMER.md](docs/PRIMER.md) - Essential concepts and architecture

A world where your AI doesn't just assist you—it truly represents ALL of you, your full spectrum of experience. Where digital interactions preserve human agency by acknowledging human complexity without judgment. Where collective intelligence emerges from individual sovereignty rather than corporate aggregation.

**The Mnemosyne Protocol is building cognitive sovereignty infrastructure** - technology that preserves human agency through full spectrum awareness, not moral imposition.

**Deep dive**: [PROJECT_STATUS.md](docs/PROJECT_STATUS.md) for honest assessment

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

## Getting Started: Choose Your Path

### 🎯 Pick Your Persona
The system adapts to your worldview:
- **Technical** → Full API access, self-hosting, metrics
- **Creative** → Visual tools, pattern art, inspiration tracking
- **Security-Focused** → Maximum privacy, Tor support, audit logs
- **Contemplative** → Minimal tracking, mindfulness, simplicity
- **Vulnerable** → Enhanced safety, support resources, guided experience

### 🛡️ Choose Your Sovereignty Level
- **Protected Mode** - Beginners with safety rails
- **Guided Mode** - Balanced autonomy and support
- **Sovereign Mode** - Full control for advanced users

## What Actually Works Now

Conservative assessment of fully functional features:

### Operational Infrastructure
- ✅ **Authentication** - JWT-based auth with secure token management
- ✅ **PostgreSQL Database** - All migrations working, tables created
- ✅ **Vector Storage** - Qdrant integration for embeddings
- ✅ **Redis Streaming** - Event processing operational
- ✅ **Docker Stack** - Full deployment ready

### Implemented Features
- ✅ **Receipt System** - SHA-256 cryptographic hashing, full transparency logs
- ✅ **Multi-Party Negotiation** - 2046 lines, 3 tables, 10 endpoints (needs user ID fix)
- ✅ **Appeals Resolution** - 422 lines, voting system, SLA tracking
- ✅ **Memory Storage** - CRUD operations, embeddings, vector search, complete UI
- ✅ **Task Management** - Full stack with forms, tracking, and gamification
- ✅ **Chat System** - Conversations with streaming, history, persona integration
- ✅ **Agentic Flow** - ReAct pattern with planning and parallel execution
- ✅ **Agent Tools** - Shadow Council (5 agents) and Forum of Echoes (10 voices) operational

### Research Phase (Not Yet Implemented)
- 🔬 **Identity Compression Vectors (ICV)** - Conceptual only, no code
- 🔬 **Zero-Knowledge Proofs** - Research stage, not implemented
- 🔬 **W3C DID Integration** - Environment variables only, no implementation
- 🔬 **Progressive Disclosure** - Basic owner-only ACL, not relationship-based
- 🔬 **Local Model Support** - Planned, not yet integrated

## Current Status

The project implements **cognitive sovereignty** through proven technologies while researching advanced capabilities.

### Working Features (Detailed)
- ✅ **Authentication System** - Secure, consolidated auth with JWT
- ✅ **Memory System** - FULL STACK: CRUD, embeddings, vector search, complete UI
- ✅ **Vector Storage** - Qdrant integration for semantic search
- ✅ **Chat System** - Conversations with streaming, history, and persona integration
- ✅ **Task System** - FULL STACK: Backend, API, UI with forms, gamification
- ✅ **Receipts System** - FULL STACK: Database, API, UI viewer (ReceiptsSimple.tsx)
- ✅ **Trust System** - Database, migrations, API endpoints all working
- ✅ **Persona System** - 5 modes (Confidant, Mentor, Mediator, Guardian, Mirror) with worldview adaptation
- ✅ **UI Shell** - Persistent navigation with all features integrated
- ✅ **Infrastructure** - Docker, PostgreSQL, Redis, Qdrant all operational
- ✅ **Agentic Flow** - ReAct pattern with reasoning, planning, and parallel action execution
- ✅ **LLM Persona Selection** - Intelligent mode selection based on context (92% confidence achieved)
- ✅ **Shadow Council** - 5 technical sub-agents fully integrated
- ✅ **Forum of Echoes** - 10 philosophical voices for diverse perspectives
- ✅ **Tool System** - Universal tool registry with 7 working tools
- ✅ **Proactive Suggestions** - Context-aware next steps while respecting sovereignty
- ✅ **SSE Streaming** - Real-time status updates during agentic processing
- ✅ **Token Management** - 64k context window with automatic truncation
- ✅ **UI Polish** - Standardized layouts, pagination, consistent search
- ✅ **Per-Message Personas** - Shows which mode was used for each response

### Next Phase: 1.C Protocol Integration (Starting Now)

#### 🚀 External Protocol Support
- 🔄 OpenAPI tool generation from specifications
- 🔄 MCP (Model Context Protocol) client implementation
- 🔄 A2A bidirectional support - consume and provide agents
- 🔄 Privacy guards and exposure controls
- 🔄 Tool permission management per user

#### 🧬 Next-Gen Identity System (PIE + Kartouche)
- 🔬 **Pragmatic Identity Embedding (PIE)** - ML-based identity compression
  - Dynamic data acquisition with LLM-assisted profiling
  - Temporal dynamics (freshness, decay, reinforcement)
  - 128-dimension secure embedding
  - Layered granularity for ZK-proofs
- 🔬 **Identity Kartouche** - Visual identity synthesis
  - Validated symbolic projection (archetypes, tarot, I Ching)
  - Unique visual glyph generation
  - Trust state visualization

#### 🤝 Trust Transaction Framework (TTF)
- 🔬 **Verifiable Claims** - Action-based trust building
  - Platform, history, reputation, and social claims
  - ZK-proof backed verification
  - Privacy-preserving validation
- 🔬 **Trust Ledger** - Local-first trust history
  - Append-only cryptographic log
  - Private, user-sovereign storage
  - Source for ZK-proof generation
- 🔬 **Dynamic Trust Score** - Continuous 0-100 metric
  - Weighted by claims, vouching, history
  - Natural decay requiring maintenance
  - Simple handshake protocol

### Research Track (Parallel)
- 🔬 **PIE Pipeline Validation** - Testing psychographic compression
- 🔬 **Symbolic Classifier Training** - Grounding archetypal mappings
- 🔬 **Trust Dynamics Modeling** - Simulating trust networks
- 🔬 **Kartouche Generation** - Visual identity synthesis algorithms
- 🔬 **ZK-STARK Optimization** - Efficient proof generation

### Next Priorities (Phase 1.B - Tools & Plugin System)
- 🔴 **Onboarding Wizard** - Persona selection for new users
- 🔴 **Sovereignty Levels** - Protected/Guided/Sovereign modes
- 🔴 **Simplified UI** - Non-technical user interfaces
- 🔴 **Values Framework** - Import moral/ethical systems
- 🔴 **Safety Templates** - Optional protection features

### Following Priorities (Phase 1.C - Enhanced Tools)
- 🟡 **Mirror Mode** - Pattern reflection without judgment
- 🟡 **Community Standards** - Optional group rules
- 🟡 **Trust Dynamics** - Appeals and due process
- 🟢 **Specialized Modes** - Operational/Contemplative/Aesthetic
- 🟢 **Integration Tests** - Comprehensive coverage

See [PROJECT_STATUS.md](docs/PROJECT_STATUS.md) for detailed priorities and honest assessment.

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
- **[Project Primer](docs/PRIMER.md)** - Complete vision and philosophy
- **[Roadmap](docs/ROADMAP.md)** - Development plan and priorities
- **[Project Status](docs/PROJECT_STATUS.md)** - Honest assessment of what's built vs. what's research
- **[Trust Primitive Primer](docs/TRUST_PRIMITIVE_PRIMER.md)** - Core innovation explained

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
4. **Progressive Trust** - Trust exists on spectrums, evolves contextually
5. **Full Spectrum Awareness** - Systems that deny any aspect of human experience are already captured
6. **Mirror, Not Judge** - Show patterns for self-awareness, don't impose morality

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

This is a solo research project with limited maintenance capacity. If the ideas resonate with you, please:
- **Fork the repository** and make it your own
- **Open issues** for discussion (checked when possible)
- **Share what you build** with these concepts

See [ALPHA_RELEASE.md](ALPHA_RELEASE.md) for realistic expectations and [Contributing Guide](docs/CONTRIBUTING.md) for technical details.

## Contact

- **GitHub Issues**: Primary communication channel
- **Pull Requests**: Welcome but may not be reviewed quickly
- **Author**: L.D. George (@ldgeorge85)

## Project Structure

```
mnemosyne/
├── backend/               # FastAPI + Python backend
├── frontend/              # React + TypeScript frontend
├── shadow/                # Shadow Council agents (to be ported as unified tool)
├── dialogues/             # Forum of Echoes agents (to be ported as unified tool)
├── tools/                 # Universal tool plugins (coming soon)
├── collective/            # Collective intelligence templates
├── docs/                  # All documentation
│   ├── decisions/         # Architecture decisions
│   ├── research/          # Academic foundations
│   ├── spec/              # Protocol specifications
│   └── PRIMER.md          # Start here
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