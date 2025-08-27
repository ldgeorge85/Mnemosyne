# The Mnemosyne Protocol: Overview

## What Is This?

**The Mnemosyne Protocol is a dual-track cognitive assistance system.**

At its surface, it's your personal AI assistant that actually belongs to you:
- **Natural chat interface** like ChatGPT but with perfect memory of all your conversations
- **Self-hosted** on your hardware with your data never leaving your control
- **Standards-compliant** using W3C DIDs, VCs, and proven cryptographic protocols
- **Privacy-preserving** with formal differential privacy and zero-knowledge proofs
- **Transparent** with Model Cards and trust calibration based on established research

Think of it as: *ChatGPT + Perfect Memory + Your Hardware + Zero Surveillance + Scientific Rigor*

## The Dual-Track Approach

### Track 1: Proven Core (Production-Ready)
- Chat and memory system with standard authentication (OAuth 2.0/OIDC)
- W3C Decentralized Identifiers (DIDs) for portable identity
- MLS Protocol (RFC 9420) for secure group messaging
- W3C PROV for complete data provenance
- Model Cards for AI transparency
- EU AI Act compliant architecture

### Track 2: Research Experiments (Opt-in Only)
- Identity compression hypothesis (100-128 bits) - UNVALIDATED
- Behavioral stability patterns (70/30 rule) - REQUIRES VALIDATION
- Resonance mechanics for compatibility - EXPERIMENTAL
- Symbolic identity mapping - RESEARCH PHASE
- All clearly labeled as experimental with hypothesis documentation

## Why Build This?

### The Problem
- Information overload is destroying our ability to think clearly
- Current tools optimize for engagement, not understanding
- Privacy and collective intelligence are treated as mutually exclusive
- Unvalidated AI claims are deployed without scientific rigor

### The Solution
Your own AI assistant that:
- **Remembers everything** - Every conversation, forever searchable
- **Works for you** - Running on your hardware, serving your interests
- **Respects science** - Only proven features in production
- **Enables research** - Opt-in experimental features with clear validation metrics
- **Maintains trust** - Transparent about capabilities and limitations

## Who Is This For?

### Primary Users

**Researchers and Early Adopters** who:
- Want control over their AI interactions
- Value privacy and data sovereignty
- Understand the difference between proven and experimental features
- Are willing to participate in validation studies
- Need trustable tools for clear thinking

### You Know You Need This If:
- You're tired of ChatGPT forgetting your context
- You want AI assistance without corporate surveillance
- You care about scientific validation of AI claims
- You believe in standards-based interoperability
- You want transparency about AI capabilities

## Core Innovation

### What Makes This Different

1. **Agentic Intelligence (Phase 1.A - COMPLETE)**
   - ✅ LLM-driven reasoning replaces keyword matching
   - ✅ Parallel action execution using ReAct patterns
   - ✅ Proactive suggestions that respect user sovereignty
   - ✅ Task queries working with LIST_TASKS action
   - ✅ Every decision transparent and overridable
   - ✅ Reasoning recorded in receipts for trust
   - 🔴 Multi-agent orchestration (Phase 1.B - Next)

2. **Dual-Track Architecture**
   - Production features use only proven technology
   - Experimental features clearly labeled and sandboxed
   - Scientific validation before production deployment

3. **Standards-First Design**
   - W3C DIDs for decentralized identity
   - OAuth 2.0/OIDC for authentication
   - MLS for secure messaging
   - PROV for data provenance

4. **Privacy by Design**
   - Formal differential privacy (Dwork et al.)
   - Private Set Intersection for matching
   - Zero-knowledge proofs for verification
   - Local-first architecture

5. **Trust Calibration**
   - Lee & See framework for appropriate reliance
   - Model Cards for transparency
   - Provenance chains for all data
   - Clear capability boundaries

## High-Level Architecture

The Mnemosyne Protocol uses a dual-track architecture to separate proven technologies from experimental research:

- **Track 1 (Core)**: Standards-based, production-ready features
- **Track 2 (Research)**: Experimental features requiring validation

For detailed technical specifications, see:
- [Protocol Specification](PROTOCOL.md) - Complete technical details
- [Kartouche Specification](KARTOUCHE.md) - Visual representation system

## Key Features

### Available Now (Track 1 - Proven)
- Personal memory with vector search
- Basic AI chat with context retention
- Task management and scheduling
- W3C DID-based identity (did:mnem method)
- Modular authentication (Static/OAuth/DID/API Key)
- Model Cards for all AI components
- Trust calibration system
- Docker containerization
- Qdrant vector database integration

### Experimental (Track 2 - Research)
Each requires explicit opt-in and consent:
- Identity compression to 100-128 bits (HYPOTHESIS)
- Behavioral stability tracking (UNVALIDATED)
- Resonance-based matching (EXPERIMENTAL)
- Symbolic identity mapping (RESEARCH)

### Coming Soon (Based on Validation)
Features move from Track 2 to Track 1 only after validation:
- Validated compression methods
- Proven behavioral patterns
- Trust network formation
- Collective intelligence (if privacy preserved)

## Standards & Compliance Summary

The protocol prioritizes established standards and regulatory compliance:

- **Identity**: W3C DIDs and Verifiable Credentials
- **Authentication**: OAuth 2.0, OIDC, WebAuthn
- **Messaging**: MLS Protocol (RFC 9420)
- **Compliance**: EU AI Act, ISO 42001, NIST AI RMF

For complete technical specifications, see [Protocol Specification](PROTOCOL.md).

## Trust & Transparency

Every component includes:
- **Model Cards**: Describing capabilities and limitations
- **Hypothesis Documentation**: For experimental features
- **Validation Metrics**: Clear success criteria
- **Provenance Chains**: Complete audit trails
- **Trust Calibration**: Based on Lee & See (2004) framework

## Getting Started

### For Users
1. Install the core system (Track 1 only)
2. Set up your W3C DID identity
3. Configure OAuth authentication
4. Start using chat and memory features

### For Researchers
1. Review hypothesis documentation
2. Opt into specific experiments
3. Provide informed consent
4. Contribute validation data
5. Help prove or disprove hypotheses

## Development Philosophy

1. **Scientific Rigor**: Hypotheses must be validated before production
2. **Standards-First**: Use proven standards over custom solutions
3. **Privacy by Design**: Data protection is architectural
4. **Transparent Limitations**: Clear about what works and what doesn't
5. **Progressive Enhancement**: Start simple, add complexity only when validated

## Current Status

### Track 1 (Production)
- ✅ Plugin architecture complete
- ✅ Feature flag system implemented
- ✅ Research bus with differential privacy
- ✅ W3C DID implementation (did:mnem method)
- ✅ OAuth 2.0 with modular auth system
- ✅ Model Cards implementation (EU AI Act compliant)
- ✅ Trust Calibration (Lee & See framework)
- 🔄 W3C PROV integration in progress
- 📋 Frontend UI connection needed (Sprint 1C)

### Track 2 (Research)
- ✅ ID compression plugin created
- ✅ Hypothesis documentation template
- ✅ Experimental plugin base class
- 📋 Behavioral stability plugin planned
- 📋 Consent management system needed
- 📋 Validation studies planned
- 📋 Research partnerships needed

## Contributing

We need:
- **Researchers**: To validate hypotheses
- **Engineers**: To implement standards
- **Users**: To test and provide feedback
- **Reviewers**: To ensure scientific rigor

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

---

*Building trustable AI through scientific validation and open standards.*