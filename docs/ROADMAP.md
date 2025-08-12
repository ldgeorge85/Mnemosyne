# Development Roadmap - Dual-Track Approach

*For AI-optimized sprint planning, see [AI Sprint Roadmap](AI_SPRINT_ROADMAP.md)*

## Current Status: Foundation Phase
**Updated**: August 11, 2025  
**Approach**: Dual-Track Development (Proven Core + Research Experiments)  
**Target**: Production-ready core in 4 weeks, validated research in 3-6 months
**Sprint Status**: Completed Sprint 1-4 (Backend MVP)

---

## Track 1: Proven Core Development

### Phase 1: Standards Foundation (Weeks 1-2) ✅ COMPLETE
- [x] Repository structure and setup ✅
- [x] Documentation framework ✅
- [x] Pydantic Settings configuration system ✅
- [x] Database schema with async SQLAlchemy ✅
- [x] Plugin architecture for experimental separation ✅
- [x] Feature flag system with audit logging ✅
- [x] Research Bus with differential privacy ✅
- [x] **W3C DID implementation** ✅ (did:mnem method)
- [x] **W3C Verifiable Credentials** ✅
- [x] **OAuth 2.0 with PKCE** ✅
- [x] **Modular auth system** ✅ (Static/OAuth/DID/API Key)
- [x] **Qdrant vector database added** ✅
- [ ] **W3C PROV data model integration** (Sprint 1A remaining)
- [ ] **Model Cards template system** (Sprint 1B)

### Phase 2: Core Services (Weeks 2-3) 🔄 IN PROGRESS
- [x] Qdrant vector database integration ✅
- [x] Async pipeline architecture ✅
- [x] Core API endpoints ✅
- [x] Redis/KeyDB for streaming ✅
- [x] **Trust calibration backend** ✅ (Lee & See framework)
- [x] **Model Cards system** ✅ (EU AI Act compliance)
- [x] **Docker containerization** ✅ (All services running)
- [x] **Frontend container setup** ✅ (React + Vite running)
- [x] **LLM Integration** ✅ (OpenAI-compatible endpoint working)
- [x] **Simple Auth System** ✅ (Dev auth operational)
- [ ] **Frontend UI connection** 🔄 IN PROGRESS - Need to fix chat endpoint
- [ ] **MLS Protocol integration** (RFC 9420)
- [ ] **WebAuthn/FIDO2 authentication** (optional)
- [ ] **C2PA content signing**

### Phase 3: Production Deployment (Weeks 3-4) 📋 PLANNED
- [ ] Docker Swarm orchestration
- [ ] Service mesh with health checks
- [ ] Prometheus metrics and logging
- [ ] Production secrets management
- [ ] CI/CD with experimental code checks
- [ ] EU AI Act compliance documentation
- [ ] ISO 42001 preparation

**Track 1 Deliverable**: Standards-compliant, privacy-preserving AI assistant

---

## Track 2: Research Experiments (Opt-in Only)

### Phase 1: Infrastructure (Weeks 1-4) 🔄 IN PROGRESS
- [x] Experimental plugin system ✅
- [x] ID Compression plugin (example) ✅
- [x] Hypothesis documentation template ✅
- [ ] **Consent management system** (IRB-compliant)
- [ ] **Longitudinal study orchestration**
- [ ] **Metrics collection dashboards**
- [ ] **Validation study protocols**

### Phase 2: Hypothesis Testing (Months 2-3) 📋 PLANNED
- [ ] **Behavioral Stability Plugin**
  - Hypothesis: 70/30 stability ratio
  - Metrics: ICC > 0.7, PSI < 0.2
  - Timeline: 6-month longitudinal study
- [ ] **Identity Compression Validation**
  - Hypothesis: 100-128 bit representation
  - Metrics: MI > 80%, F1 > 0.75
  - Method: Use W3C VCs for claims
- [ ] **Resonance Mechanics Testing**
  - Replace with EigenTrust/PageRank
  - Validate against trust formation
  - Use PSI for privacy

### Phase 3: Cross-validation (Months 4-6) 📋 PLANNED
- [ ] Cross-cultural validation studies
- [ ] Academic partnerships
- [ ] Peer review process
- [ ] Publication of results
- [ ] Feature graduation to Track 1

**Track 2 Deliverable**: Validated or rejected hypotheses with published results

---

## Integration Points (AI-MC Standards)

### Immediate Adoptions (Track 1)
- **W3C Standards**: DIDs, VCs, PROV, WebAuthn
- **Authentication**: OAuth 2.0, OIDC
- **Messaging**: MLS Protocol (RFC 9420)
- **Trust**: Lee & See calibration framework
- **Transparency**: Model Cards, Data Sheets

### Research Validation (Track 2)
- **Privacy**: PSI, Bloom filters, formal DP
- **Reputation**: EigenTrust, PageRank
- **Trust**: MDS ability/benevolence/integrity
- **Anthropomorphism**: Reeves & Nass validation

---

## Compliance & Governance

### Regulatory Requirements
- [ ] **EU AI Act Compliance** (URGENT - already in force)
  - Transparency obligations
  - Risk assessment
  - Provenance requirements
- [ ] **ISO/IEC 42001:2023** preparation
- [ ] **NIST AI RMF** implementation
- [ ] **GDPR** compliance verification

### Documentation Requirements
- [ ] Model Cards for all AI components
- [ ] Data Sheets for datasets
- [ ] Hypothesis documentation for experiments
- [ ] Validation reports
- [ ] Audit trails with W3C PROV

---

## Key Milestones

| Date | Milestone | Success Criteria | Track |
|------|-----------|-----------------|-------|
| Week 2 | Standards Integration | W3C DIDs, OAuth working | Track 1 |
| Week 4 | Core MVP Complete | Production-ready, compliant | Track 1 |
| Month 2 | Research Infrastructure | Studies running, metrics flowing | Track 2 |
| Month 3 | First Validation Results | Hypotheses tested | Track 2 |
| Month 4 | Feature Graduation | Validated features to Track 1 | Both |
| Month 6 | Full Validation | All hypotheses resolved | Track 2 |

---

## Resource Requirements

### Human Resources
- **Now**: Solo founder + AI assistance
- **Week 4**: + Research collaborator
- **Month 2**: + Academic partnership
- **Month 4**: + 1-2 engineers
- **Month 6**: Team of 3-5

### Validation Resources
- **Participants**: 1000+ for behavioral studies
- **Compute**: GPU cluster for compression tests
- **Storage**: Time-series DB for metrics
- **Analysis**: Statistical expertise

### Infrastructure (Monthly)
- **Track 1 Core**: $50-200 (standard deployment)
- **Track 2 Research**: $500-1000 (metrics, storage)
- **Validation Studies**: $2000-5000 (compute, storage)

---

## Risk Management

### Technical Risks
| Risk | Mitigation | Status |
|------|------------|--------|
| Experimental code in production | Plugin architecture, CI checks | ✅ Mitigated |
| Hypothesis validation failure | Dual-track allows core progress | ✅ Mitigated |
| Standards complexity | Phased adoption, proven libraries | 🔄 In Progress |
| Regulatory non-compliance | EU AI Act assessment urgent | 🔴 High Priority |

### Research Risks
| Risk | Mitigation | Status |
|------|------------|--------|
| Insufficient participants | Academic partnerships | 📋 Planned |
| Invalid hypotheses | Clear failure criteria | ✅ Defined |
| Publication rejection | Multiple venues planned | 📋 Planned |

---

## Success Metrics

### Track 1 (Production Core)
- Response time < 100ms
- 99.9% uptime
- Zero security breaches
- Standards compliance verified
- EU AI Act compliant

### Track 2 (Research)
- Hypothesis validation rate
- Publication acceptance
- Participant satisfaction
- Metrics quality (ICC, PSI, MI)
- Feature graduation rate

---

## Development Principles

1. **Scientific Rigor**: No unvalidated claims in production
2. **Standards-First**: Proven standards over custom solutions
3. **Privacy by Design**: Formal guarantees, not promises
4. **Transparent Limitations**: Clear about what works
5. **Progressive Enhancement**: Simple core, validated additions

---

## Next Actions

### This Week (Sprint 5 - Week 2)
1. Fix chat endpoint user object issue
2. Implement memory CRUD operations with embeddings
3. Connect frontend authentication flow
4. Configure alternative embedding model
5. Deploy first philosophical agent demo

### Next Sprints (6-8)
1. Complete user authentication with real users table
2. Full memory system with vector embeddings
3. Agent orchestration system
4. Deep Signal detection implementation
5. Begin collective intelligence features
6. Deploy consent management
7. Launch validation studies

---

*Building trustable AI through scientific validation and open standards.*

**Next Action**: Complete W3C DID migration