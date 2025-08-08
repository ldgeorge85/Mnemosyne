# Mnemosyne Dual-Track Implementation Plan

## Executive Summary

Following critical review findings that core scientific claims remain unvalidated, we are implementing a dual-track development approach:

1. **Track 1: Implementation (Core)** - Stable, proven features with standard cryptography
2. **Track 2: Research (Experimental)** - Sandboxed modules for hypothesis validation

This separation ensures we can deliver value while conducting necessary empirical validation.

## Current State Assessment

### Existing Issues Identified
- Identity compression code (`backend/models/signal.py`) assumes unproven 100-128 bit representation
- No clear separation between proven and experimental features
- Missing infrastructure for longitudinal studies and validation metrics
- No consent workflows for research data collection
- Lacking modular plugin system for experimental features

### Existing Strengths
- User system already uses standard UUIDs (no compression)
- Basic memory/chat infrastructure in place
- Docker deployment ready
- Database migrations established

## Implementation Strategy

### Phase 1: Core Refactoring (Week 1-2)

#### 1.1 Plugin Architecture
```python
# backend/app/core/plugins/__init__.py
class PluginInterface:
    """Base interface for all plugins"""
    def __init__(self, config: dict):
        self.enabled = config.get('enabled', False)
        self.experimental = config.get('experimental', True)
        self.hypothesis_doc = config.get('hypothesis_doc', '')
    
    async def initialize(self): pass
    async def shutdown(self): pass
    def get_status(self) -> dict: pass
```

#### 1.2 Feature Flag System
```python
# backend/app/core/features.py
class FeatureFlags:
    """Centralized feature flag management"""
    EXPERIMENTAL_ID_COMPRESSION = "experimental.id_compression"
    EXPERIMENTAL_BEHAVIORAL_TRACKING = "experimental.behavioral_tracking"
    EXPERIMENTAL_RESONANCE = "experimental.resonance"
    
    @classmethod
    def is_enabled(cls, flag: str, user_id: str = None) -> bool:
        # Check global, per-instance, and per-user flags
        pass
```

#### 1.3 Research Bus
```python
# backend/app/core/research_bus.py
class ResearchBus:
    """Event bus for publishing anonymized data to research track"""
    async def publish(self, event_type: str, data: dict, consent_id: str):
        # Anonymize and validate consent before publishing
        pass
```

### Phase 2: Research Infrastructure (Week 2-3)

#### 2.1 Longitudinal Study Support
```yaml
# backend/app/research/studies/behavioral_stability.yaml
study:
  name: "Behavioral Stability Validation"
  hypothesis: "Human behavior exhibits 70% stability over 6 months"
  metrics:
    - ICC (test-retest correlation)
    - PSI (population stability index)
    - KL divergence
  schedule:
    - baseline: 0d
    - followup_1: 30d
    - followup_2: 90d
    - followup_3: 180d
  required_n: 1000
  consent_version: "v1.2"
```

#### 2.2 Metrics Collection
```python
# backend/app/research/metrics/__init__.py
class MetricsCollector:
    """Centralized metrics collection for research"""
    
    async def record_icc(self, user_id: str, value: float, context: dict):
        """Record Intraclass Correlation Coefficient"""
        pass
    
    async def record_mi_retention(self, bits: int, mi_score: float):
        """Record mutual information retention by bit budget"""
        pass
```

#### 2.3 Consent Management
```python
# backend/app/research/consent.py
class ConsentManager:
    """IRB-compliant consent workflows"""
    
    async def request_consent(self, user_id: str, study_id: str) -> ConsentRequest:
        pass
    
    async def verify_consent(self, user_id: str, data_type: str) -> bool:
        pass
```

### Phase 3: Experimental Modules (Week 3-4)

#### 3.1 ID Compression Module (EXPERIMENTAL)
```python
# backend/app/plugins/experimental/id_compression/__init__.py
"""
EXPERIMENTAL: Identity Compression to 100-128 bits
Status: UNVALIDATED HYPOTHESIS
Hypothesis: Human identity can be compressed to 100-128 bits while preserving distinctiveness
Success Metrics: 
  - MI retention > 80%
  - Downstream task F1 > 0.75
  - Human interpretability rating > 4/5
"""

class IDCompressionPlugin(PluginInterface):
    experimental = True
    hypothesis_doc = "docs/research/hypotheses/id_compression.md"
    
    async def compress(self, behavioral_data: dict) -> bytes:
        if not FeatureFlags.is_enabled(FeatureFlags.EXPERIMENTAL_ID_COMPRESSION):
            raise ExperimentalFeatureDisabled()
        # Implementation here
```

#### 3.2 Behavioral Stability Tracker (EXPERIMENTAL)
```python
# backend/app/plugins/experimental/behavioral_stability/__init__.py
"""
EXPERIMENTAL: 70/30 Behavioral Stability Rule
Status: UNVALIDATED HYPOTHESIS
Hypothesis: Identity is 70% stable, 30% evolving over time
Success Metrics:
  - ICC > 0.7 over 6 months
  - PSI < 0.2 
  - Predictive accuracy > 70%
"""
```

### Phase 4: Benchmarking & CI Integration (Week 4)

#### 4.1 Benchmark Harness
```python
# benchmarks/run_benchmarks.py
class BenchmarkSuite:
    """Automated benchmark runner"""
    
    async def run_mls_scalability(self):
        """Test MLS with n ∈ {100, 1k, 5k, 10k} members"""
        pass
    
    async def run_proof_performance(self):
        """Measure STARK/Merkle proof generation/verification"""
        pass
```

#### 4.2 CI Integration
```yaml
# .github/workflows/dual-track-ci.yml
name: Dual Track CI
on: [push, pull_request]

jobs:
  core-tests:
    name: Core Track Tests
    runs-on: ubuntu-latest
    steps:
      - name: Run core unit tests
      - name: Verify no experimental deps in core
      
  experimental-tests:
    name: Experimental Track Tests
    runs-on: ubuntu-latest
    steps:
      - name: Run experimental tests (sandboxed)
      - name: Generate hypothesis status report
      
  benchmarks:
    name: Performance Benchmarks
    runs-on: ubuntu-latest
    steps:
      - name: Run benchmark suite
      - name: Upload results to metrics DB
```

## Directory Structure

```
mnemosyne/
├── backend/
│   ├── app/
│   │   ├── core/               # Track 1: Proven features only
│   │   │   ├── auth/          # Standard UUID-based auth
│   │   │   ├── memory/        # Basic memory/chat
│   │   │   ├── crypto/        # MLS, Sparse Merkle
│   │   │   ├── plugins/       # Plugin interface
│   │   │   ├── features.py    # Feature flags
│   │   │   └── research_bus.py
│   │   ├── plugins/
│   │   │   └── experimental/   # Track 2: Sandboxed experiments
│   │   │       ├── id_compression/
│   │   │       ├── behavioral_stability/
│   │   │       └── resonance/
│   │   └── research/           # Research infrastructure
│   │       ├── studies/       # Study definitions
│   │       ├── metrics/       # Metrics collection
│   │       ├── consent/       # Consent management
│   │       └── datasets/      # Dataset schemas
├── benchmarks/                 # Performance benchmarks
├── docs/
│   ├── hypotheses/            # Hypothesis documentation
│   │   ├── id_compression.md
│   │   ├── behavioral_stability.md
│   │   └── resonance.md
│   └── validation/            # Validation results
└── research_dashboards/       # Metrics visualization

```

## Deliverable Schedule (Updated)

### Phase 1: Foundation (Weeks 1-2) ✅ PARTIALLY COMPLETE
- [x] Plugin architecture with experimental/core separation
- [x] Feature flag system with audit logging
- [x] Research Bus with differential privacy
- [x] Example experimental module (ID Compression)
- [ ] W3C DID implementation
- [ ] W3C PROV integration
- [ ] Model Cards template
- [ ] EU AI Act compliance assessment

### Phase 2: Standards Integration (Weeks 3-4) 🔄 IN PROGRESS
- [ ] Migrate identity system to W3C DIDs/VCs
- [ ] Add OAuth 2.0/OIDC authentication
- [ ] Implement WebAuthn for secure login
- [ ] Deploy Model Cards for all plugins
- [ ] Add C2PA content signing
- [ ] Trust calibration UI (Lee & See framework)

### Phase 3: Research Validation (Weeks 5-8) 📋 PLANNED
- [ ] PSI for privacy-preserving matching
- [ ] Formal DP bounds on metrics
- [ ] EigenTrust reputation system
- [ ] Longitudinal study infrastructure
- [ ] Consent management with IRB compliance
- [ ] Benchmark harness for MLS/proofs

### Phase 4: Compliance & Governance (Weeks 9-12) 📋 PLANNED
- [ ] Complete EU AI Act compliance
- [ ] ISO 42001 implementation
- [ ] NIST AI RMF assessment
- [ ] Full documentation update
- [ ] Research partnerships established

## Success Criteria

### Track 1 (Core)
- Zero dependencies on unvalidated hypotheses
- All features work with standard UUIDs
- No experimental code in production path
- 100% test coverage for core features

### Track 2 (Research)
- Every experimental module has linked hypothesis doc
- All modules clearly labeled "EXPERIMENTAL"
- Metrics collection automated
- Benchmarks reproducible from scripts

## Risk Mitigation (Updated)

| Risk | Mitigation | Status |
|------|------------|--------|
| Experimental code leaking to core | Plugin architecture, feature flags, CI checks | ✅ Implemented |
| Users confused by experimental features | Clear "EXPERIMENTAL" labeling, Model Cards, opt-in only | 🔄 In Progress |
| Research data privacy | Differential privacy, W3C PROV, consent management | 🔄 In Progress |
| Validation takes too long | Parallel tracks, proven standards in Track 1 | ✅ Architected |
| Regulatory non-compliance | EU AI Act assessment, ISO 42001 planning | 🔴 Urgent |
| Unvalidated hypotheses in production | Mandatory hypothesis docs, validation metrics | ✅ Implemented |
| Identity system incompatibility | W3C DID migration path defined | 📋 Planned |
| Trust miscalibration | Lee & See framework adoption | 📋 Planned |
| Sybil attacks | EigenTrust/SybilGuard patterns | 📋 Planned |
| Content authenticity | C2PA signing implementation | 📋 Planned |

## Current Status (2025-08-08)

### Completed Infrastructure
- ✅ Plugin architecture with clear experimental/core separation
- ✅ Feature flag system with audit logging
- ✅ Research Bus for anonymized event publishing  
- ✅ Example experimental module (ID Compression) with hypothesis doc
- ✅ Base documentation and templates

### In Progress
- 🔄 Refactoring core to remove identity compression assumptions
- 🔄 Consent management workflows
- 🔄 Longitudinal study infrastructure

### Implementation Notes

#### Key Design Decisions Made
1. **Experimental features disabled by default** - Require explicit opt-in via feature flags
2. **Mandatory hypothesis documentation** - Every experimental module must link to validation criteria
3. **Multi-level anonymization** - Basic, differential privacy, and full anonymization options
4. **Plugin status tracking** - Real-time validation metrics and status reporting
5. **Research event prioritization** - Critical, high, normal, low priority levels for event processing

#### Technical Highlights
- Research Bus implements differential privacy with Laplacian noise generation
- Plugin registry enforces separation at registration time
- Feature flags support per-user and per-instance overrides
- Consent verification integrated into event publishing pipeline

## Next Steps

### Immediate Priority (This Week)
1. **W3C DID Migration**: Replace custom UUIDs with decentralized identifiers
2. **PROV Integration**: Add W3C PROV to Research Bus (partially complete)
3. **Model Cards**: Create templates and generate for existing plugins
4. **EU AI Act**: Document compliance gaps and create action plan
5. **Refactor Signal Model**: Remove identity compression from core

### Short-term (Next 2 Weeks)
1. **Authentication Standards**: Implement OAuth 2.0/OIDC + WebAuthn
2. **Trust Calibration**: Add Lee & See metrics to UI
3. **PSI Implementation**: Privacy-preserving set intersection for matching
4. **C2PA Pipeline**: Content authenticity signing
5. **Consent Management**: IRB-compliant workflows

### Medium-term (Month 2)
1. **EigenTrust Integration**: Replace resonance with proven reputation
2. **Longitudinal Studies**: Orchestration and scheduling system
3. **Benchmark Suite**: Automated performance testing
4. **Research Partnerships**: Academic collaboration for validation
5. **ISO 42001 Prep**: Begin management system implementation

### Long-term (Months 3-6)
1. **Validation Studies**: Execute hypothesis testing protocols
2. **Cross-cultural Testing**: Validate against diverse populations
3. **FHE Exploration**: Investigate homomorphic encryption
4. **Full Compliance**: Complete EU AI Act, ISO 42001, NIST AI RMF
5. **Production Readiness**: Move validated features to Track 1

### Research Integration Opportunities (AI-MC Framework)

#### Standards Adoption (Track 1 - Proven)
- **W3C DIDs/VCs**: Replace custom identity with decentralized standards
- **W3C PROV**: Complete provenance graphs for all research data
- **OAuth 2.0/OIDC**: Standard authentication replacing custom auth
- **WebAuthn/FIDO2**: Phishing-resistant authentication
- **Model Cards**: Transparency artifacts for all modules
- **C2PA**: Content authenticity for generated outputs

#### Validation Frameworks (Track 2 - Research)
- **Lee & See Trust Metrics**: Validate behavioral stability hypothesis
- **MDS ABI Model**: Measure ability/benevolence/integrity dimensions
- **PSI (Private Set Intersection)**: Privacy-preserving resonance testing
- **Formal Differential Privacy**: Replace ad-hoc anonymization
- **EigenTrust/PageRank**: Replace speculative resonance mechanics
- **Bloom Filters**: Efficient nullifier registries

#### Regulatory Compliance (Critical)
- **EU AI Act**: Already in force (Aug 2024) - immediate compliance needed
- **ISO/IEC 42001:2023**: AI management system standard
- **NIST AI RMF**: Risk management framework

---

*This dual-track approach ensures we deliver value through proven features while conducting the empirical validation necessary to substantiate our research hypotheses. Infrastructure is now in place to begin parallel development.*