# AI Agent Coding Sprint Roadmap - Dual-Track Edition

*This is the sprint-optimized version of the [main roadmap](ROADMAP.md) for AI coding sessions*

## Design Philosophy

This roadmap is optimized for AI agent coding sessions with dual-track separation:
1. **Track 1 Sprints**: Proven, standards-based features only
2. **Track 2 Sprints**: Experimental features with clear hypothesis docs
3. **Maximize uninterrupted coding** - Complete subsystems without stopping
4. **Enable parallel work** - Clear separation allows concurrent development

## Current Status (Updated: August 2025)

### Completed ✅
- Plugin architecture with experimental separation
- Feature flag system with audit logging
- Research Bus with differential privacy
- Basic backend infrastructure
- **Sprint 1A: Standards Foundation** (90% complete)
  - W3C DID implementation (did:mnem method) ✅
  - W3C Verifiable Credentials ✅
  - OAuth 2.0 with PKCE ✅
  - Modular auth system (Static/OAuth/DID/API Key) ✅
- **Sprint 1B: Trust & Transparency** (60% complete)
  - Model Cards (EU AI Act compliant) ✅
  - Trust Calibration (Lee & See framework) ✅

### In Progress 🔄
- Transparency API endpoints
- W3C PROV integration

### Not Started ❌
- WebAuthn/FIDO2
- MLS Protocol (Sprint 2A)
- Frontend UI components
- Track 2 experimental plugins
- Consent management

---

## TRACK 1: PROVEN CORE SPRINTS

## 🚀 Sprint 1A: Standards Foundation
**Goal**: Implement W3C standards and authentication  
**Duration**: Single session (~4 hours)  
**Dependencies**: None

### Implementation Block
```python
# Complete these files in sequence:
1. backend/core/identity/did.py         # W3C DID implementation
2. backend/core/identity/vc.py          # Verifiable Credentials
3. backend/core/auth/oauth.py           # OAuth 2.0 provider
4. backend/core/auth/oidc.py            # OpenID Connect
5. backend/core/auth/webauthn.py        # WebAuthn/FIDO2
6. backend/core/provenance/prov.py      # W3C PROV integration
7. backend/api/v1/identity.py           # Identity endpoints
8. backend/api/v1/credentials.py        # VC issuance endpoints
9. backend/services/did_resolver.py     # DID resolution service
10. backend/migrations/002_did.py       # Migrate to DIDs
```

### Deliverable
- Standards-compliant identity system
- OAuth 2.0/OIDC authentication
- W3C PROV data lineage

---

## 🚀 Sprint 1B: Trust & Transparency
**Goal**: Implement Model Cards and trust calibration  
**Duration**: Single session (~3 hours)  
**Dependencies**: Sprint 1A

### Implementation Block
```python
# Complete these files in sequence:
1. backend/core/transparency/model_card.py  # Model Card generator
2. backend/core/transparency/data_sheet.py  # Data Sheet generator
3. backend/core/trust/calibration.py        # Lee & See framework
4. backend/core/trust/abi_model.py          # Ability/Benevolence/Integrity
5. backend/api/v1/transparency.py           # Transparency endpoints
6. backend/services/trust_service.py        # Trust scoring
7. frontend/src/components/ModelCard.tsx    # Model Card UI
8. frontend/src/components/TrustGauge.tsx   # Trust calibration UI
```

### Deliverable
- Model Cards for all AI components
- Trust calibration in UI
- Transparency artifacts

---

## 🚀 Sprint 1C: Frontend Foundation 🔄 IN PROGRESS
**Goal**: Get basic UI working for local use  
**Duration**: Single session (~4 hours)  
**Progress**: 60% - Frontend running, auth routing issues  
**Dependencies**: Sprint 1A (auth) + existing backend

### Implementation Block
```python
# Core UI Setup:
1. frontend/src/pages/Login.tsx           # Auth with static for dev
2. frontend/src/pages/Dashboard.tsx       # Main memory interface
3. frontend/src/components/MemoryInput.tsx # Capture memories
4. frontend/src/components/MemoryList.tsx  # Display memories
5. frontend/src/api/client.ts             # API client with auth
6. frontend/src/stores/auth.ts            # Auth state management
7. frontend/src/stores/memory.ts          # Memory state
8. Fix CORS and proxy configuration
9. Docker setup for frontend container
```

### Deliverable
- Working login with static auth
- Memory capture and display
- Basic search functionality
- Docker containerized frontend
- **LOCAL MNEMOSYNE IS USABLE!** 🎉

---

## 🚀 Sprint 2A: Secure Communications (MLS)
**Goal**: Implement MLS Protocol for E2E encrypted groups  
**Duration**: Single session (~4 hours)  
**Dependencies**: Sprint 1A

### Implementation Block
```python
# Complete these files in sequence:
1. backend/crypto/mls/wrapper.py        # OpenMLS wrapper
2. backend/crypto/mls/groups.py         # Group management
3. backend/crypto/mls/messages.py       # Message handling
4. backend/crypto/mls/key_packages.py   # Key package store
5. backend/services/mls_service.py      # MLS service layer
6. backend/api/v1/groups.py             # Group endpoints
7. backend/api/v1/messages.py           # Messaging endpoints
8. backend/workers/mls_worker.py        # Async MLS operations
```

### Deliverable
- MLS-based secure group messaging
- Scalable to 50k+ members
- Forward secrecy + PCS

---

## 🚀 Sprint 3A: Privacy Primitives
**Goal**: Implement proven privacy technologies  
**Duration**: Single session (~3 hours)  
**Dependencies**: Sprint 1A

### Implementation Block
```python
# Complete these files in sequence:
1. backend/privacy/psi.py               # Private Set Intersection
2. backend/privacy/bloom_filter.py      # Bloom filter implementation
3. backend/privacy/differential.py      # Formal DP implementation
4. backend/privacy/eigentrust.py        # EigenTrust reputation
5. backend/privacy/pagerank.py          # PageRank trust propagation
6. backend/services/privacy_service.py  # Privacy service layer
7. backend/api/v1/privacy.py           # Privacy endpoints
```

### Deliverable
- PSI for private matching
- Formal differential privacy
- Reputation systems

---

## 🚀 Sprint 4A: Compliance & Governance
**Goal**: EU AI Act and regulatory compliance  
**Duration**: Single session (~3 hours)  
**Dependencies**: Sprint 1B

### Implementation Block
```python
# Complete these files in sequence:
1. backend/compliance/eu_ai_act.py      # EU AI Act checker
2. backend/compliance/iso_42001.py      # ISO 42001 compliance
3. backend/compliance/nist_ai_rmf.py    # NIST AI RMF
4. backend/compliance/c2pa.py           # C2PA content signing
5. backend/compliance/audit.py          # Audit trail generator
6. backend/api/v1/compliance.py         # Compliance endpoints
7. docs/compliance/EU_AI_ACT.md         # Compliance documentation
8. docs/compliance/ISO_42001.md         # ISO documentation
```

### Deliverable
- EU AI Act compliance tools
- C2PA content authenticity
- Audit trail system

---

## TRACK 2: EXPERIMENTAL SPRINTS

## 🔬 Sprint 1E: Identity Compression Plugin
**Goal**: Experimental 100-128 bit compression  
**Duration**: Single session (~3 hours)  
**Dependencies**: Track 1 Sprint 1A
**Status**: HYPOTHESIS - REQUIRES VALIDATION

### Implementation Block
```python
# Complete these files in sequence:
1. backend/plugins/experimental/id_compression/compressor.py
2. backend/plugins/experimental/id_compression/decompressor.py
3. backend/plugins/experimental/id_compression/metrics.py
4. backend/plugins/experimental/id_compression/validation.py
5. docs/hypotheses/id_compression_detailed.md
6. backend/research/studies/compression_study.py
7. backend/api/v1/experimental/compression.py
```

### Validation Requirements
- MI retention > 80%
- F1 score > 0.75
- Human interpretability > 4/5

---

## 🔬 Sprint 2E: Behavioral Stability Tracker
**Goal**: Test 70/30 stability hypothesis  
**Duration**: Single session (~3 hours)  
**Dependencies**: Track 1 Sprint 1A
**Status**: HYPOTHESIS - REQUIRES VALIDATION

### Implementation Block
```python
# Complete these files in sequence:
1. backend/plugins/experimental/behavioral/tracker.py
2. backend/plugins/experimental/behavioral/metrics.py
3. backend/plugins/experimental/behavioral/longitudinal.py
4. backend/plugins/experimental/behavioral/validation.py
5. docs/hypotheses/behavioral_stability_detailed.md
6. backend/research/studies/stability_study.py
7. backend/api/v1/experimental/behavioral.py
```

### Validation Requirements
- ICC > 0.7 over 6 months
- PSI < 0.2
- Predictive accuracy > 70%

---

## 🔬 Sprint 3E: Research Infrastructure
**Goal**: Build validation and consent systems  
**Duration**: Single session (~4 hours)  
**Dependencies**: Track 1 Sprint 1A

### Implementation Block
```python
# Complete these files in sequence:
1. backend/research/consent/manager.py   # Consent management
2. backend/research/consent/irb.py       # IRB compliance
3. backend/research/studies/orchestrator.py  # Study orchestration
4. backend/research/metrics/collector.py # Metrics collection
5. backend/research/metrics/dashboard.py # Dashboard generation
6. backend/research/datasets/export.py   # Dataset export
7. backend/api/v1/research/consent.py   # Consent endpoints
8. backend/api/v1/research/studies.py   # Study endpoints
9. frontend/src/pages/Research.tsx      # Research dashboard
```

### Deliverable
- IRB-compliant consent system
- Longitudinal study support
- Metrics dashboards

---

## Sprint Execution Strategy

### For Track 1 (Core):
1. **Prioritize standards** - W3C DIDs before custom identity
2. **Complete compliance early** - EU AI Act is already in force
3. **Test with real services** - No mocks, actual integration

### For Track 2 (Experimental):
1. **Require consent** - Every experimental feature needs opt-in
2. **Document hypotheses** - Clear success/failure criteria
3. **Collect metrics** - Automated validation tracking
4. **Label clearly** - "EXPERIMENTAL" in all outputs

## Parallel Execution Options

These sprint pairs can run simultaneously:
- Track 1 Sprint 1A + Track 2 Sprint 3E (different layers)
- Track 1 Sprint 2A + Track 1 Sprint 3A (independent services)
- Track 2 Sprint 1E + Track 2 Sprint 2E (separate plugins)

## Status Tracking

### Track 1 (Core) Sprints
| Sprint | Status | Time | Priority |
|--------|--------|------|----------|
| 1A: Standards Foundation | ✅ 90% Complete | 4h | DONE |
| 1B: Trust & Transparency | ✅ Complete | 3h | DONE |
| 1C: Frontend Foundation | 🔄 60% Progress | 4h | URGENT |
| 2A: MLS Communications | 📋 Ready | 4h | HIGH |
| 3A: Privacy Primitives | 📋 Ready | 3h | MEDIUM |
| 4A: Compliance | 📋 Ready | 3h | URGENT |

### Track 2 (Experimental) Sprints
| Sprint | Status | Time | Hypothesis |
|--------|--------|------|------------|
| 1E: ID Compression | ✅ Started | 3h | UNVALIDATED |
| 2E: Behavioral Stability | 📋 Planned | 3h | UNVALIDATED |
| 3E: Research Infrastructure | 📋 Planned | 4h | N/A |

## Migration Path

### From Original Sprints to Dual-Track:
1. **Sprint 1 (Data Layer)** → Keep as-is, add DID migration
2. **Sprint 2 (Memory)** → Keep in Track 1
3. **Sprint 3 (Agents)** → Keep in Track 1, add Model Cards
4. **Sprint 4 (API)** → Refactor to use OAuth/OIDC
5. **Sprint 5 (MLS)** → Move to Track 1 Sprint 2A
6. **Sprint 6 (Signatures)** → Split: proven parts to Track 1, experimental to Track 2

## 🎯 When Will It Be Usable?

### 🚨 After Sprint 1C (NEXT!) - **WORKING LOCAL UI**
- Frontend with login page
- Memory capture interface
- Basic search and display
- **~4 hours work**
- **THIS MAKES MNEMOSYNE USABLE LOCALLY!**

### After Track 1 Sprint 1A+1B - **COMPLIANT CORE**
- Standards-based identity
- Proper authentication
- Trust calibration
- **~7 hours total work**

### After Track 1 Sprint 2A+3A - **SECURE & PRIVATE**
- E2E encrypted messaging
- Privacy-preserving matching
- Reputation systems
- **~14 hours total work**

### After Track 2 Validation - **ENHANCED FEATURES**
- IF hypotheses validated
- Graduated to Track 1
- **3-6 months validation**

## Next Recommended Action

🔴 **URGENT: Complete Track 1 Sprint 1A**
- W3C DID implementation critical
- OAuth/OIDC needed for security
- EU AI Act compliance urgent

Then proceed with:
1. Track 1 Sprint 4A (Compliance) - EU AI Act already in force!
2. Track 1 Sprint 1B (Trust) - Model Cards required
3. Track 2 Sprint 3E (Research) - Enable validation studies

---

*"Build on standards, validate through science."*