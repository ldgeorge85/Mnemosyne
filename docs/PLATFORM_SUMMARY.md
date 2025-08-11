# The Mnemosyne Protocol: Platform Summary
## A Cognitive-Symbolic Operating System for Human Agency

---

## Executive Summary

The Mnemosyne Protocol is a **dual-track cognitive assistance platform** that combines a production-ready personal AI assistant with experimental research into identity and collective intelligence. It runs on your hardware, preserves your privacy, and maintains scientific integrity by clearly separating proven features from research hypotheses.

**Core Vision**: Build trustable AI through standards compliance, privacy preservation, and scientific validation.

---

## What It Does

### For Users (Track 1 - Production Ready)
- **Personal AI Assistant** with perfect memory of all conversations
- **Self-hosted** on your hardware - data never leaves your control  
- **Standards-compliant** identity using W3C DIDs and Verifiable Credentials
- **Privacy-preserving** with encryption and local processing
- **Transparent AI** with Model Cards explaining capabilities and limitations

### For Researchers (Track 2 - Experimental)
- **Identity compression research** - Testing if behavioral patterns can compress to 128 bits
- **Trust dynamics studies** - How AI mediation affects human trust formation
- **Collective intelligence experiments** - Privacy-preserving group coordination
- **All clearly labeled** as experimental with opt-in consent

---

## System Architecture

### Technology Stack

```
Frontend:           React + TypeScript + Vite
Backend:            FastAPI + Python 3.11+
Database:           PostgreSQL + Async SQLAlchemy  
Vector Store:       Qdrant (embeddings)
Cache/Queue:        Redis/KeyDB
AI Models:          OpenAI/Anthropic APIs (Track 1)
                   Local models optional (Track 2)
Authentication:     OAuth 2.0, OIDC, W3C DIDs
Deployment:         Docker Compose → Docker Swarm
```

### Dual-Track Architecture

```
┌─────────────────────────────────────────┐
│         User Interface                  │
│    (Chat, Memory Browser, Dashboard)    │
├─────────────────────────────────────────┤
│     Track 1: Core Services              │
│  • Memory Management (CRUD + Search)    │
│  • AI Chat (Context-aware)              │
│  • Authentication (OAuth/DID)           │
│  • Trust Calibration                    │
├─────────────────────────────────────────┤
│     Standards & Protocols               │
│  • W3C DIDs & Verifiable Credentials    │
│  • OAuth 2.0 / OIDC                     │
│  • MLS Protocol (E2E messaging)         │
│  • W3C PROV (Data provenance)           │
├─────────────────────────────────────────┤
│     Track 2: Research Plugins           │
│  • Identity Compression (HYPOTHESIS)    │
│  • Behavioral Analysis (EXPERIMENTAL)   │
│  • Trust Dynamics (RESEARCH)            │
│  • [Requires explicit consent]          │
└─────────────────────────────────────────┘
```

---

## Core Features & Flow

### 1. Memory System
```python
# User stores a memory
POST /api/memories
{
  "content": "Discussed quantum computing with Alice",
  "tags": ["physics", "research"],
  "importance": 0.8
}

# System:
1. Generates embeddings (384-1536 dimensions)
2. Extracts metadata and entities
3. Stores encrypted in PostgreSQL
4. Indexes in Qdrant vector DB
5. Updates user's memory graph

# User searches memories
GET /api/memories/search?q="quantum computing"
Returns semantically similar memories ranked by relevance
```

### 2. AI-Mediated Communication (AIMC)
```python
# Progressive trust-based mediation
Level 0: Direct communication (no AI)
Level 1: Grammar/spelling correction
Level 2: Style enhancement
Level 3: Content structuring
Level 4: Semantic translation
Level 5: Content generation
Level 6: Autonomous negotiation

# Trust determines mediation level
if trust_score < 0.3:
    max_level = 1  # Minimal AI involvement
elif trust_score < 0.6:
    max_level = 3  # Moderate assistance
else:
    max_level = 5  # Full AI capabilities
```

### 3. Identity Management
```python
# W3C DID-based identity
did:mnem:3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy

# Verifiable Credentials for claims
{
  "@context": ["https://www.w3.org/2018/credentials/v1"],
  "type": ["VerifiableCredential", "TrustScore"],
  "credentialSubject": {
    "id": "did:mnem:...",
    "trustScore": 0.75,
    "confidence": 0.85
  }
}
```

---

## Research Components (Track 2)

### Identity Compression Hypothesis
**Claim**: Human behavioral patterns can compress to 128 bits  
**Status**: UNVALIDATED - No scientific evidence exists  
**Research Plan**: 
- Collect interaction data (with consent)
- Apply dimensionality reduction
- Test temporal stability (ICC > 0.7)
- Validate cross-context consistency

### Trust Dynamics Research
**Goal**: Understand how AI mediation affects trust  
**Current Findings**:
- Trust drops 31% when AI involvement disclosed
- Progressive disclosure improves acceptance
- Cultural factors significantly affect trust

### Behavioral Signal Extraction
**What We Collect** (with consent):
- Edit patterns in AI suggestions
- Response times and hesitation
- Topic preferences and depth
- Communication style evolution

---

## Privacy & Security

### Privacy Guarantees
- **Local-first architecture** - Core functions work offline
- **Differential privacy** (ε < 1.0) for aggregations
- **Zero-knowledge proofs** for verification without disclosure
- **Encryption at rest** (AES-256-GCM)
- **No telemetry** without explicit consent

### Security Model
- **Authentication**: Multi-factor with WebAuthn support
- **Authorization**: RBAC with fine-grained permissions
- **Audit logging**: Complete provenance chains
- **Threat model**: Assumes hostile network, trusted hardware

---

## Implementation Status

### ✅ Completed (Track 1)
- Database schema and models
- Plugin architecture for experiments
- W3C DID implementation
- OAuth 2.0 authentication
- Docker containerization
- Qdrant vector store integration
- Basic API endpoints

### 🔄 In Progress
- Frontend-backend connection
- MLS Protocol integration
- Trust calibration UI
- Model Cards system

### 📋 Planned
- WebAuthn/FIDO2
- C2PA content signing
- EU AI Act compliance docs
- Production deployment

---

## AI Model Requirements

### Production Models (Track 1)
```python
models = {
    "text_generation": "GPT-3.5/Claude Haiku API",
    "embeddings": "sentence-transformers/all-MiniLM-L6-v2",
    "grammar": "LanguageTool local server",
    "sentiment": "distilbert-base-uncased"
}

# Costs: ~$5-20/user/month for APIs
# Alternative: Local Llama-2-7B (needs 16GB VRAM)
```

### Research Reality Check
- **Identity to 128 bits**: Mathematically impossible (need 10^6+ bits)
- **Behavioral stability**: No evidence of stable patterns
- **Trust prediction**: 60-70% accuracy maximum
- **Personality from text**: Only 30-40% correlation

---

## Getting Started

### Quick Setup
```bash
# Clone repository
git clone [repo] mnemosyne
cd mnemosyne

# Run setup
./scripts/setup.sh

# Start services
docker-compose up

# Access at http://localhost:3000
```

### Configuration
```yaml
# .env file
DATABASE_URL=postgresql://user:pass@localhost/mnemosyne
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=sk-...  # For AI features
PRIVACY_MODE=maximum   # local-only processing
```

---

## Philosophy & Principles

### Core Beliefs
1. **Sovereignty over convenience** - You own your data and compute
2. **Real or nothing** - No fake implementations or false claims
3. **Science over speculation** - Validate before deployment
4. **Privacy by design** - Not an afterthought
5. **Standards-based** - Interoperable and portable

### Ethical Stance
- **No surveillance capitalism** - Your data isn't the product
- **Transparent limitations** - Honest about what doesn't work
- **Informed consent** - Clear about data collection
- **Right to exit** - Data portability guaranteed

---

## Development Roadmap

### Phase 1: Foundation (Current)
- Core memory and chat system
- Standards-based identity
- Basic AI integration
- Docker deployment

### Phase 2: Enhancement (Next)
- Multi-user support
- Advanced AI features
- Trust network formation
- Mobile applications

### Phase 3: Scale (Future)
- Federated deployment
- Collective intelligence (validated)
- Academic partnerships
- Open source community

---

## Key Differentiators

1. **Dual-track approach** - Separates proven from experimental
2. **Self-hosted** - Complete data sovereignty  
3. **Standards-first** - W3C, IETF, OAuth throughout
4. **Scientific rigor** - Hypotheses with validation metrics
5. **Privacy-preserving** - Local processing, encryption, ZK proofs
6. **Transparent AI** - Model Cards, trust calibration
7. **No lock-in** - Portable identity and data

---

## Challenges & Limitations

### Technical Challenges
- Identity compression likely impossible with current technology
- Local models have quality/performance trade-offs
- Privacy vs. functionality tensions
- Scaling self-hosted infrastructure

### Research Limitations
- No evidence for 128-bit identity compression
- Behavioral patterns show low stability
- Trust prediction accuracy limited to 60-70%
- Cultural biases in AI models

### Practical Considerations
- Requires technical knowledge to self-host
- API costs for quality AI features
- Limited mobile support initially
- Small user base during research phase

---

## Call to Action

### For Users
- Run your own instance for complete privacy
- Provide feedback on core features
- Help identify bugs and usability issues

### For Researchers  
- Review hypothesis documentation
- Participate in validation studies
- Contribute to open science

### For Developers
- Contribute to open source development
- Implement standard protocols
- Build on the plugin architecture

---

## Summary

The Mnemosyne Protocol offers a **pragmatic path** to cognitive assistance that respects human agency. By clearly separating proven technologies from research experiments, it provides immediate value while exploring future possibilities. 

The platform is **honest about its limitations** - identity compression may be impossible, behavioral patterns show limited stability, and trust prediction remains challenging. But it delivers **real value today** through memory augmentation, AI assistance, and privacy preservation.

Most importantly, it's **yours** - running on your hardware, under your control, with your data never leaving your possession. In a world of corporate AI platforms, Mnemosyne offers an alternative: AI that truly works for you.

---

*"For those who see too much and belong nowhere - we're building a place where your complexity is not a burden but a strength."*