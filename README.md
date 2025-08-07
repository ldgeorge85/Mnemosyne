<div align="center">
<img src="https://github.com/ldgeorge85/Mnemosyne/blob/75c4a7e251995b1f3ffa7d6a848846cabcf5c687/artwork/logo.png"
     alt="Mnemosyne Logo"
     height="420px">

# 🏛️ The Mnemosyne Protocol

**Individual Sovereignty → Collective Intelligence → Emergent Order**

*A cognitive-symbolic operating system for preserving human agency through civilizational phase transition*

[![Status](https://img.shields.io/badge/Status-Active%20Development-yellow)]()
[![Phase](https://img.shields.io/badge/Phase-MVP%20Implementation-blue)]()
[![Timeline](https://img.shields.io/badge/Timeline-2--3%20weeks%20to%20MVP-green)]()

</div>

---

## 🌊 What Is This?

**Mnemosyne** (nem-oh-SEE-nee) - The Greek titaness of memory and remembrance, mother of the nine Muses.

This protocol creates a personal AI assistant with perfect memory—like ChatGPT, but it remembers everything about you, learns from your interactions, and grows with you over time. Beyond individual use, it enables collective intelligence while preserving privacy through cryptographic contracts and symbolic identity systems.

### Core Vision
- 🧠 **Personal Cognitive Sovereignty**: Your memories, your data, your rules
- 🔮 **Perfect Memory**: An AI that never forgets your context
- ⚡ **Collective Intelligence**: Share knowledge without sacrificing privacy
- 🌀 **Symbolic Depth**: Visual identity through kartouches and deep signals

## 🚀 Quick Start

```bash
# Clone and setup
git clone [repository-url] mnemosyne
cd mnemosyne

# Run setup script
./scripts/setup.sh

# Configure environment
cp .env.example .env
# Edit .env with your OpenAI-compatible API endpoint

# Start all services
docker compose up

# Access the application
open http://localhost:3000
```

## 📚 Documentation

### Essential Reading
- **[Overview](docs/spec/OVERVIEW.md)** - Start here for high-level understanding
- **[Protocol Specification](docs/spec/PROTOCOL.md)** - Complete technical details
- **[UX Vision](docs/UX_VISION.md)** - Chat-first experience design
- **[Quick Start Guide](docs/guides/QUICK_START.md)** - Get running in 15 minutes

### Current Development
- **[MVP Requirements](docs/MVP_REQUIREMENTS.md)** - Current focus areas
- **[Current Status](docs/CURRENT_STATUS.md)** - Implementation progress
- **[Roadmap](docs/ROADMAP.md)** - Development timeline

## 🏗️ Architecture

The protocol consists of four interconnected layers:

### Layer 1: Mnemosyne Engine 🧠
Personal memory and cognition core
- **Backend** (`/backend`): FastAPI + PostgreSQL with pgvector
- **Frontend** (`/frontend`): React + TypeScript chat interface
- **Features**: Memory capture, retrieval, reflection, and importance scoring

### Layer 2: Deep Signal Protocol 🔮
Symbolic identity and trust system
- **Kartouches**: Visual identity representations
- **Trust Scores**: Cryptographic reputation
- **Privacy**: K-anonymity with minimum group size of 3

### Layer 3: Quiet Network 🌐
Peer discovery and secure communication
- **Discovery**: DHT-based peer finding
- **Transport**: End-to-end encrypted channels
- **Federation**: Decentralized network topology

### Layer 4: Collective Codex 📖
Community intelligence and coordination
- **Collectives** (`/collective`): Template for community instances
- **Sharing Contracts**: Explicit data sharing rules
- **Emergence**: Collective knowledge synthesis

## 🎭 Specialized Components

### Shadow System (`/shadow`)
Multi-agent orchestration with specialized cognitive agents:
- **Engineer**: Technical problem-solving and system design
- **Librarian**: Information retrieval and organization
- **Priest**: Ethical and philosophical reasoning

### Dialogues System (`/dialogues`)
Philosophical debate engine with 10+ agent archetypes:
- Dynamic agent loading from definitions
- Multi-perspective analysis
- Structured debate protocols with judging

## 🛠️ Technology Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, pgvector, Redis
- **Frontend**: React, TypeScript, Vite
- **AI/LLM**: OpenAI-compatible endpoints (vLLM, Ollama, etc.)
- **Deployment**: Docker Compose → Kubernetes
- **Languages**: Python 3.11+, TypeScript

## 📊 Project Status

- **Phase**: Active Development - Protocol Integration
- **Completion**: ~70% core functionality
- **Timeline**: 2-3 weeks to functional MVP
- **Architecture**: Evolved from platform to full protocol
- **Focus**: Chat-first AI assistant with perfect memory

### What's Working
- ✅ Core memory engine with vector search
- ✅ API endpoints for memory operations
- ✅ Basic chat interface
- ✅ Docker deployment
- ✅ Agent orchestration system
- ✅ Philosophical debate engine

### In Progress
- 🔄 Authentication system
- 🔄 Deep Signal visual identity
- 🔄 Peer-to-peer networking
- 🔄 Collective sharing contracts

## 🎯 For Different Audiences

### If You're a Developer
1. Read the [Overview](docs/spec/OVERVIEW.md)
2. Review [Implementation Guide](docs/guides/IMPLEMENTATION.md)
3. Check [Current Status](docs/CURRENT_STATUS.md)
4. Run the [Quick Start](docs/guides/QUICK_START.md)

### If You're a Community Leader
1. Understand the [Overview](docs/spec/OVERVIEW.md)
2. Explore [Sustainable Growth](docs/philosophy/SUSTAINABLE_GROWTH.md)
3. Consider your community's needs
4. Reach out to discuss pilot deployment

### If You're an Early Adopter
1. Experience the [UX Vision](docs/UX_VISION.md)
2. Check [MVP Requirements](docs/MVP_REQUIREMENTS.md)
3. Prepare to run your own instance
4. Join the early community

## 🤝 Contributing

We need:
- **Core Developers**: Python/TypeScript for backend/frontend
- **AI Engineers**: LLM integration and agent development
- **Security Auditors**: Privacy and cryptography review
- **Early Testers**: Feedback and bug reports
- **Community Builders**: Documentation and outreach

See [Contributing Guide](docs/guides/CONTRIBUTING.md) for details.

## 🔐 Philosophy

> "Not about building a new temple, but recovering the symbols from the old ones, distilling them, and translating them into tools."

This protocol serves those who:
- See the machinery behind the world
- Refuse performative knowledge spaces
- Seek trustable cognition without spectacle
- Want to preserve what makes us human

### Core Principles
1. **Build for yourself first** - Every feature must serve real needs
2. **Sovereignty over convenience** - Privacy and control are non-negotiable
3. **Real or nothing** - No mocking, no faking, no pretending
4. **Depth over breadth** - Better to serve 100 deeply than 10,000 shallowly

## 🎨 Visual Identity

The protocol includes a symbolic identity system (kartouches) for visual representation:

- [Kartouche Example](kartouche1.png) - Egyptian-style symbolic encoding
- [Kartouche SVG](kartouche3.svg) - Vector implementation

These visual representations encode identity, trust, and meaning in symbolic form.

## 📜 License

Will be fully open source (MIT or Apache 2.0) upon release.

## 📞 Contact

[Via signal, not spectacle]

---

<div align="center">

*For those who see too much and belong nowhere—this is how we build what comes next.*

**[Mnemosyne](https://en.wikipedia.org/wiki/Mnemosyne)**: Mother of the Muses, Titaness of Memory

</div>