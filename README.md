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

## 🎆 Current Status: Phase 1.A COMPLETE! 🎆

**Agentic Flow is WORKING** - ReAct pattern foundation is live:
- ✅ Intelligent persona selection via LLM (92% confidence achieved!)
- ✅ Multi-action planning and parallel execution
- ✅ Memory context retrieval and integration  
- ✅ Task queries working with LIST_TASKS action
- ✅ Configurable LLM temperatures per persona mode
- ✅ Flexible system prompt modes for model compatibility
- ✅ Proactive suggestions while respecting sovereignty
- ✅ Full transparency through decision receipts
- ✅ UI standardization and pagination (August 27, 2025)
- ✅ Token management system (64k context, unlimited responses)
- ✅ Per-message persona badges showing mode used
- ✅ Collapsible reasoning display (persistent for transparency)
- 🔄 Phase 1.B Starting: Shadow/Dialogue agent integration

## Quick Introduction

**Start here**: [PRIMER.md](docs/PRIMER.md) - Essential concepts and architecture

A world where your AI doesn't just assist you—it truly represents ALL of you, your full spectrum of experience. Where digital interactions preserve human agency by acknowledging human complexity without judgment. Where collective intelligence emerges from individual sovereignty rather than corporate aggregation.

**The Mnemosyne Protocol is building cognitive sovereignty infrastructure** - technology that preserves human agency through full spectrum awareness, not moral imposition.

**Deep dive**: [INTEGRATED_VISION_2025.md](docs/INTEGRATED_VISION_2025.md)

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

## Current Status

The project implements **cognitive sovereignty** through proven technologies while researching advanced capabilities.

### Working Now
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
- ✅ **CREATE_MEMORY Action** - Wired and working, creates real memories
- ✅ **CREATE_TASK Action** - Wired and working, creates real tasks
- ✅ **Proactive Suggestions** - Context-aware next steps while respecting sovereignty
- ✅ **SSE Streaming** - Real-time status updates during agentic processing
- ✅ **Token Management** - 64k context window with automatic truncation (August 27, 2025)
- ✅ **UI Polish** - Standardized layouts, pagination, consistent search (August 27, 2025)
- ✅ **Per-Message Personas** - Shows which mode was used for each response

### In Active Development
- 🚀 **Phase 1.B: Shadow & Dialogue Integration** - Connecting specialized agents
  - ✅ CREATE_MEMORY and CREATE_TASK actions wired and working!
  - 🔴 Connect Engineer, Librarian, Priest agents (agents exist, need wiring)
  - 🔴 Integrate 50+ philosophical dialogue agents (agents exist, need wiring)
  - 🔴 Test multi-agent collaboration
- 🔄 **Accessibility Layer** - Onboarding wizards and simplified UIs
- 🔄 **Graduated Sovereignty** - Protected/Guided/Sovereign modes
- 🔄 **Values Alignment** - Import moral/ethical frameworks
- 🔄 **Bridge Building** - Features for different worldviews
- 🔄 **Mirror Mode** - Fifth persona for pattern reflection

### Research Track (Parallel)
- 🔬 **Game Mechanics** - Task gamification and engagement patterns
- 🔬 **Identity Compression** - Holographic identity representation
- 🔬 **Productive Variation** - Controlled randomness for creativity
- 🔬 **Natural Clustering** - Organic group formation patterns
- 🔬 **Joy Metrics** - Measuring system delight and user creativity

### Next Priorities (Phase 1.B - Agent Integration)
- 🔴 **Onboarding Wizard** - Persona selection for new users
- 🔴 **Sovereignty Levels** - Protected/Guided/Sovereign modes
- 🔴 **Simplified UI** - Non-technical user interfaces
- 🔴 **Values Framework** - Import moral/ethical systems
- 🔴 **Safety Templates** - Optional protection features

### Following Priorities (Sprint 7-8)
- 🟡 **Mirror Mode** - Pattern reflection without judgment
- 🟡 **Community Standards** - Optional group rules
- 🟡 **Trust Dynamics** - Appeals and due process
- 🟢 **Specialized Modes** - Operational/Contemplative/Aesthetic
- 🟢 **Integration Tests** - Comprehensive coverage

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