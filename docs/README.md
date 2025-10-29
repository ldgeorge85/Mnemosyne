# Mnemosyne Protocol Documentation

## What This Is

**Mnemosyne is a research PROJECT exploring genuinely new primitives for cognitive sovereignty.** We're creating mechanisms for preserving human agency that don't exist anywhere else - not another privacy tool or AI wrapper, but fundamental new patterns of digital resistance.

## Current Focus

**Primary Primitive**: Trust Without Central Authority [80-90% effort]
**Implementation Status**: Mixed - see [PROJECT_STATUS.md](PROJECT_STATUS.md) for reality check
**Success Target**: Demo of "impossible" trust between hostile parties

## Core Documentation

### 📍 Essential Reading - Start Here
1. **[PRIMER.md](PRIMER.md)** - Project overview with all implementation references
2. **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - Honest assessment of what's built vs. claimed
3. **[TRUST_PRIMITIVE_PRIMER.md](TRUST_PRIMITIVE_PRIMER.md)** - Our main working innovation (75% complete)

### 🚀 Key Implementation Documents
- **[RECEIPT_CRYPTOGRAPHY.md](RECEIPT_CRYPTOGRAPHY.md)** - SHA-256 cryptographic receipts (WORKING)
- **[TASK_BREAKDOWN.md](TASK_BREAKDOWN.md)** - Detailed implementation phases
- **[spec/MULTI_PARTY_NEGOTIATION.md](spec/MULTI_PARTY_NEGOTIATION.md)** - Negotiation protocol spec
- **[spec/NEGOTIATION_P2P_EXTENSION.md](spec/NEGOTIATION_P2P_EXTENSION.md)** - P2P extension design

### 🗺️ Roadmaps & Architecture
- **[ROADMAP.md](ROADMAP.md)** - Order of operations for primitive development
- **[ROADMAP_P2P_TRUST.md](ROADMAP_P2P_TRUST.md)** - P2P trust network roadmap
- **[P2P_TRUST_ARCHITECTURE_FINAL_SYNTHESIS.md](P2P_TRUST_ARCHITECTURE_FINAL_SYNTHESIS.md)** - Architecture vision
- **[SIMPLE_TRUST_PROTOCOL.md](SIMPLE_TRUST_PROTOCOL.md)** - Simplified protocol explanation

### 🔬 Research Context
- **[/review/](../review/)** - October 2024 comprehensive assessment
  - `synthesis_and_vision.md` - Strategic direction
  - `review_external.md` - External validation summary
- **[philosophy/](philosophy/)** - Core principles
- **[research/](research/)** - Papers and theoretical work

### 🛠 Development
- **[TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md)** - System design
- **[AI_DEVELOPMENT_GUIDE.md](AI_DEVELOPMENT_GUIDE.md)** - Instructions for AI assistants
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Running the system
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines

### 📁 Component Documentation
- **[backend/](backend/)** - Backend architecture and API reference
- **[frontend/](frontend/)** - Frontend components and patterns
- **[spec/](spec/)** - Technical specifications
- **[decisions/](decisions/)** - Architecture decision records

## Implementation Reality

| Primitive | Status | Evidence | Next Step |
|-----------|--------|----------|-----------|
| **Trust Without Authority** | [PARTIAL] | Models & CRUD only | Complete resolution workflow |
| **Receipt System** | [IMPLEMENTED] | Full transparency primitive | Add cryptographic integrity |
| **Agent Orchestration** | [IMPLEMENTED] | ReAct pattern working | Add evaluation metrics |
| **Shadow Council/Forum** | [IMPLEMENTED] | Multi-voice orchestration | Tension preservation metrics |
| **Identity (ICV)** | [UNVERIFIED] | No code found | Create specification |
| **Memory Sovereignty** | [PARTIAL] | Vector storage only | Selective disclosure |

**Critical**: All features labeled [IMPLEMENTED], [PARTIAL], or [UNVERIFIED] based on code review.

## The Five Novel Primitives

1. **Trust Without Central Authority** - Negotiated trust with appeals (PRIMARY FOCUS)
2. **Identity Without Surveillance** - Identity Compression Vectors (CONCEPTUAL)
3. **Collective Intelligence Without Groupthink** - Tension-preserving synthesis
4. **Memory Sovereignty With Portability** - Local-first with selective sharing
5. **AI Alignment Without Lobotomization** - Philosophical coherence with agency

## The Four Central Paradoxes

1. **Sovereignty Paradox** - Using OpenAI/Anthropic while claiming sovereignty
2. **Network Paradox** - Network primitives without network to test
3. **Abstraction Paradox** - Powerful concepts, unclear utility
4. **Urgency Paradox** - Urgent threat, research timeline

We accept these paradoxes as inherent to the transition period.

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

# Database
docker compose exec postgres psql -U postgres -d mnemosyne
```

## Development Philosophy

### What Guides Decisions
- **Sovereignty over convenience** - Never compromise agency
- **Depth over breadth** - Complete one primitive fully
- **Honesty over hype** - Label reality accurately
- **Knowledge over product** - Research output primary
- **Real or nothing** - No mocking, no faking

### Success Metrics (Research, Not Product)
- ✅ ONE primitive others can implement
- ✅ ONE pattern that changes thinking
- ✅ ONE demonstration of impossible
- ❌ NOT user count or revenue

## Current Sprint

### Immediate Operations
1. Wire receipt enforcement to strict mode
2. Complete appeals resolution workflow
3. Add cryptographic proof-of-process
4. Create multi-party negotiation demo

### This Week
- Label ALL documentation accurately
- Focus 80-90% on Trust primitive
- Abstract LLM calls for future sovereignty
- Start "holy shit" demo outline

## Project Structure

```
mnemosyne/
├── backend/          # FastAPI + Python implementation
├── frontend/         # React + TypeScript interface
├── docs/             # Documentation (you are here)
├── review/           # October 2024 comprehensive assessment
├── scripts/          # Setup and utilities
├── .archive/         # Outdated documentation
└── docker-compose.yml
```

## For AI Assistants

See [AI_DEVELOPMENT_GUIDE.md](AI_DEVELOPMENT_GUIDE.md) and [../CLAUDE.md](../CLAUDE.md) for detailed instructions. Key points:
- Build real features or explicitly defer
- No mocking, no placeholder code
- Mark unimplemented features clearly
- Focus on Trust primitive completion

## Contact & Resources

- Comprehensive review: `/review/` directory
- Project status: `review/PROJECT_STATUS.md`
- External validation: `review/review_external.md`
- Historical docs: `.archive/` directory

---

## Essential Insight

**We're not building a product. We're discovering new categories of digital resistance.**

The complexity isn't failure - it's innovation. The lack of users isn't a problem - it's appropriate for research. The path forward is deepening primitives, not simplifying to conventional solutions.

---

*"In the age of surveillance capitalism, the most radical act is creating new categories of resistance."*