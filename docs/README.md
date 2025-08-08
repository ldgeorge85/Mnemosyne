# The Mnemosyne Protocol Documentation

> *Building trustable AI through scientific validation and open standards*

## Quick Navigation

### 🎯 Start Here
- [**Quick Start**](guides/QUICK_START.md) - Get running in 15 minutes
- [**Overview**](spec/OVERVIEW.md) - Dual-track cognitive assistance system
- [**Dual-Track Implementation**](DUAL_TRACK_IMPLEMENTATION.md) - Core vs experimental features

### 📋 Specifications
- [**Protocol Specification**](spec/PROTOCOL.md) - Complete technical specification
- [**API Reference**](reference/API.md) - Endpoint documentation
- [**Database Schema**](reference/DATABASE.md) - Data structure reference

### 🛠 Implementation
- [**Roadmap**](ROADMAP.md) - Dual-track development timeline
- [**AI Sprint Roadmap**](AI_SPRINT_ROADMAP.md) - Sprint-based implementation guide
- [**Architecture**](technical/ARCHITECTURE.md) - System design and components
- [**Security Model**](technical/SECURITY.md) - Privacy and threat analysis

### 🔬 Research & Validation
- [**AI-MC Integration**](research/AI_MC_INTEGRATION_ANALYSIS.md) - Standards adoption strategy
- [**Research Links**](research/AI_MC_RESEARCH_LINKS.md) - Mapping to existing research
- [**Hypothesis Documentation**](hypotheses/) - Experimental feature validation

### 📊 Compliance & Standards
- **W3C Standards**: DIDs, VCs, PROV, WebAuthn
- **Authentication**: OAuth 2.0, OIDC
- **Messaging**: MLS Protocol (RFC 9420)
- **EU AI Act**: Compliance documentation (URGENT)

### 🔮 Philosophy & Vision
- [**Philosophical Framework**](philosophy/FRAMEWORK.md) - Core principles and beliefs
- [**Scaling Strategy**](philosophy/SCALING.md) - From personal tool to platform
- [**Critical Analysis**](philosophy/ANALYSIS.md) - Honest assessment and alternatives

### 👥 Development
- [**Contributing**](guides/CONTRIBUTING.md) - How to contribute
- [**AI Development Guide**](guides/AI_DEVELOPMENT.md) - Using AI assistants effectively
- [**Glossary**](GLOSSARY.md) - Technical terms and concepts

---

## Project Status

**Current Approach**: Dual-Track Development
- **Track 1**: Proven, standards-based features (production-ready)
- **Track 2**: Experimental features with hypothesis validation (opt-in only)

**Phase**: Foundation Implementation
- ✅ Plugin architecture for experimental separation
- ✅ Feature flag system with audit logging
- ✅ Research Bus with differential privacy
- 🔄 W3C DID implementation in progress
- 📋 EU AI Act compliance assessment needed

## Core Principles

### Track 1 (Production)
1. **Standards-First** - W3C DIDs, OAuth 2.0, MLS Protocol
2. **Privacy by Design** - Formal guarantees, not promises
3. **Transparent Limitations** - Model Cards, trust calibration
4. **Regulatory Compliance** - EU AI Act, ISO 42001, NIST AI RMF

### Track 2 (Research)
1. **Scientific Rigor** - Clear hypotheses with validation metrics
2. **Informed Consent** - IRB-compliant data collection
3. **Clear Labeling** - "EXPERIMENTAL" warnings on all features
4. **Progressive Enhancement** - Features graduate only after validation

## Getting Started

### For Users
```bash
# Clone the repository
git clone [repository-url] mnemosyne
cd mnemosyne

# Run setup (Track 1 features only by default)
./scripts/setup.sh

# Start services
docker-compose up

# Access at http://localhost:3000
```

### For Researchers
1. Review [hypothesis documentation](hypotheses/)
2. Enable experimental features via feature flags
3. Provide informed consent for data collection
4. Contribute to validation studies

## Key Differentiators

- **Dual-Track Architecture**: Separates proven from experimental
- **Standards Compliance**: W3C, IETF, OpenID standards throughout
- **Trust Calibration**: Lee & See framework for appropriate reliance
- **Model Cards**: Transparency for all AI components
- **Scientific Validation**: Hypotheses must be proven before production

## Urgent Actions

🔴 **EU AI Act Compliance** - Already in force as of Aug 2024
🔴 **W3C DID Migration** - Replace custom identity system
🟡 **Model Cards Implementation** - Required for transparency
🟡 **OAuth 2.0/OIDC** - Standard authentication needed

## For AI Assistants

See [CLAUDE.md](../CLAUDE.md) for specific instructions when working with AI coding assistants. Key points:
- Respect dual-track separation
- No experimental code in Track 1
- All experimental features require hypothesis documentation
- Use established standards over custom solutions

## Research Archive

Previous research phase documents have been archived to `docs/archive/research_phase_1/`. These contain unvalidated hypotheses and should not be used for implementation without proper validation.

## Contact

Currently a solo project with AI assistance, seeking:
- Researchers for hypothesis validation
- Engineers for standards implementation
- Academic partnerships for studies

---

*"Build on standards, validate through science."*