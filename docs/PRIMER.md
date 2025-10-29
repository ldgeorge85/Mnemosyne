# The Mnemosyne Protocol: A Research Project
*Exploring New Primitives for Cognitive Sovereignty*

## What We're Building

Mnemosyne is a **research PROJECT** (not a product) exploring genuinely new mechanisms for preserving human agency in the age of surveillance capitalism. We're attempting to create primitives for digital sovereignty that don't exist elsewhere.

## The Core Problem

**Cognitive Feudalism** - A world where:
- AI systems treat humans as data sources to mine
- Surveillance capitalism controls how we think and interact
- Digital platforms own our memories, relationships, and agency
- Traditional resistance patterns have been compromised

## Our Research Approach

Instead of building another privacy app or AI wrapper, we're exploring **five novel primitives**:

### 1. Trust Without Central Authority [PRIMARY FOCUS]
**Research Question**: Can trust exist without blockchain or central servers?
- **Hypothesis**: Negotiated trust with appeals process
- **Status**: [75% COMPLETE] - Working implementation with cryptographic receipts
- **Goal**: Demo of binding agreement between hostile parties
- **Implementation Docs**:
  - [TRUST_PRIMITIVE_PRIMER.md](TRUST_PRIMITIVE_PRIMER.md) - Complete explanation of how it works
  - [RECEIPT_CRYPTOGRAPHY.md](RECEIPT_CRYPTOGRAPHY.md) - SHA-256 hash chain implementation
  - [spec/MULTI_PARTY_NEGOTIATION.md](spec/MULTI_PARTY_NEGOTIATION.md) - Protocol specification

### 2. Identity Without Surveillance [CONCEPTUAL]
**Research Question**: Can identity persist privately across systems?
- **Hypothesis**: Identity Compression Vectors (ICV)
- **Status**: [UNVERIFIED] - No implementation yet
- **Goal**: Mathematical model and specification
- **Research Docs**:
  - [ICV_IMPLEMENTATION_STRATEGY.md](ICV_IMPLEMENTATION_STRATEGY.md) - Proposed approach
  - [ICV_PROTOCOL_STANDARD.md](ICV_PROTOCOL_STANDARD.md) - Protocol design
  - [MODULAR_IDENTITY_PROTOCOL.md](MODULAR_IDENTITY_PROTOCOL.md) - Architecture

### 3. Collective Intelligence Without Groupthink [PARTIAL]
**Research Question**: Can groups think without collapsing to consensus?
- **Hypothesis**: Tension-preserving synthesis
- **Status**: [PARTIAL] - Agent orchestration works, needs metrics
- **Goal**: Measurable disagreement persistence

### 4. Memory Sovereignty With Portability [PARTIAL]
**Research Question**: Can memory be both owned AND shared?
- **Hypothesis**: Local-first with selective disclosure
- **Status**: [PARTIAL] - Storage works, sharing doesn't
- **Goal**: Cryptographic sharing protocol

### 5. AI Alignment Without Lobotomization [PARTIAL]
**Research Question**: Can AI maintain coherent worldview while respecting agency?
- **Hypothesis**: Philosophical persona system
- **Status**: [PARTIAL] - Personas exist, untested
- **Goal**: Coherence under adversarial stress

## The Four Paradoxes We Accept

1. **Sovereignty Paradox** - We use OpenAI/Anthropic to build sovereignty tools
2. **Network Paradox** - We build network primitives without a network
3. **Abstraction Paradox** - Powerful concepts with unclear utility
4. **Urgency Paradox** - Urgent threat but research takes time

These are inherent to the transition period. We accept them.

## Implementation Documentation

### Key Working Features - With Documentation

For detailed technical implementation, see these documents:

#### Trust & Negotiation System
- **[TRUST_PRIMITIVE_PRIMER.md](TRUST_PRIMITIVE_PRIMER.md)** - Complete guide to the trust primitive (75% working)
- **[RECEIPT_CRYPTOGRAPHY.md](RECEIPT_CRYPTOGRAPHY.md)** - SHA-256 cryptographic receipt implementation
- **[spec/MULTI_PARTY_NEGOTIATION.md](spec/MULTI_PARTY_NEGOTIATION.md)** - Negotiation protocol specification
- **[spec/NEGOTIATION_P2P_EXTENSION.md](spec/NEGOTIATION_P2P_EXTENSION.md)** - P2P extension design

#### Architecture & Deployment
- **[ROADMAP.md](ROADMAP.md)** - Current development priorities and timeline
- **[ROADMAP_P2P_TRUST.md](ROADMAP_P2P_TRUST.md)** - P2P trust network roadmap
- **[P2P_TRUST_ARCHITECTURE_FINAL_SYNTHESIS.md](P2P_TRUST_ARCHITECTURE_FINAL_SYNTHESIS.md)** - Architecture vision
- **[SIMPLE_TRUST_PROTOCOL.md](SIMPLE_TRUST_PROTOCOL.md)** - Simplified protocol overview

#### Conceptual & Future Work
- **[ICV_IMPLEMENTATION_STRATEGY.md](ICV_IMPLEMENTATION_STRATEGY.md)** - Identity compression strategy
- **[IDENTITY_TRUST_COMPARISON.md](IDENTITY_TRUST_COMPARISON.md)** - Comparison of approaches
- **[TASK_BREAKDOWN.md](TASK_BREAKDOWN.md)** - Detailed implementation tasks

## Current Implementation

### What Actually Works
- **Receipt System** [IMPLEMENTED] - Comprehensive transparency primitive
- **Agent Orchestration** [IMPLEMENTED] - ReAct pattern, parallel execution
- **Shadow Council** [IMPLEMENTED] - 5 technical sub-agents
- **Forum of Echoes** [IMPLEMENTED] - 10 philosophical voices
- **Vector Memory** [IMPLEMENTED] - Embeddings with search

### What's Aspirational
- Identity Compression Vectors - No code
- Zero-knowledge proofs - Not implemented
- Progressive disclosure - Owner-only
- Multi-party trust - Conceptual
- Local model support - Future goal

## Technical Foundation

```
Backend:     FastAPI + Python
Frontend:    React + TypeScript
Database:    PostgreSQL
Vector:      Qdrant
Cache:       Redis/KeyDB
Deploy:      Docker Compose
```

Currently dependent on external LLMs (OpenAI/Anthropic). Migration to local models planned but not implemented.

## Development Philosophy

### Research Over Product
- Success = new primitives others can build on
- NOT seeking users or revenue
- Documentation is primary output
- Knowledge preservation paramount

### Honest Implementation
- Build real features or explicitly defer
- No mocking, no faking
- Label everything accurately
- Test adversarially

### Depth Over Breadth
- 80-90% focus on ONE primitive at a time
- Complete demonstration before moving on
- "Holy shit" moments over explanations

## Current Sprint: Trust Primitive

### Immediate Operations
1. Wire receipt enforcement to strict mode
2. Complete appeals resolution workflow
3. Add cryptographic proof-of-process
4. Create multi-party negotiation demo

### Success Target
Demo showing "impossible" trust - two hostile parties reach binding agreement with no central authority, no blockchain, no reputation system.

## For Contributors

This is research, not a startup. We need:
- Deep thinking over fast shipping
- Documentation over features
- Honesty over hype
- Primitives over products

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Why This Matters

The surveillance state is achieving cognitive lock-in. Traditional resistance patterns are compromised. We need fundamentally new mechanisms for preserving human agency.

We're not trying to build a better privacy tool. We're trying to invent the primitives that don't exist yet.

Yes, it's complex - because we're exploring uncharted territory.
Yes, it's incomplete - because research takes time.
Yes, it lacks users - because it's research, not a product.

## The Path Forward

1. Complete ONE primitive fully (Trust)
2. Demonstrate the "impossible"
3. Document everything
4. Enable others to build
5. Move to next primitive OR help others continue

## Research Documentation Paths

The project includes extensive research documentation exploring theoretical foundations and future possibilities:

### 📚 Research Directory Structure

#### For Understanding Core Concepts
- **[/docs/research/GLOSSARY.md](/docs/research/GLOSSARY.md)** - Comprehensive terminology reference
- **[/docs/research/README.md](/docs/research/README.md)** - Research index and navigation guide

#### For Technical Deep Dives
- **Identity & Behavior** - Theoretical models for identity compression and evolution
- **Cryptography & Privacy** - Zero-knowledge proofs, nullifiers, formal privacy models
- **Communication & Coordination** - MLS protocol analysis, consensus mechanisms
- **Collective Intelligence** - Quorum dynamics, resonance mechanics, symbol emergence

#### Important Caveats
- **Much is conceptual**: The research directory contains both working code analysis and pure theory
- **Not all is implemented**: Many documents describe aspirational features
- **Active research**: Some hypotheses have been invalidated, others remain open questions

### 🔬 Review Directory

The `/review/` directory contains critical assessments from October 2024:
- **External validation** of claims vs implementation
- **Honest assessment** of what works vs what doesn't
- **Strategic synthesis** of viable paths forward

## Essential Context

For realistic understanding:
- **[/ALPHA_RELEASE.md](/ALPHA_RELEASE.md)** - Solo developer context and expectations
- **[/docs/PROJECT_STATUS.md](/docs/PROJECT_STATUS.md)** - What's actually built vs conceptual
- `/review/` - October 2024 comprehensive assessment
- `review/synthesis_and_vision.md` - Strategic direction
- `review/PROJECT_STATUS.md` - Implementation reality

---

## The Bottom Line

**We're not building a product. We're discovering new categories of digital resistance.**

If we succeed, we'll have created primitives others can build on.
If we fail, we'll have documented the attempt for the next try.

Either way, the knowledge advances.

---

*"In the age of surveillance capitalism, the most radical act is creating new categories of resistance."*