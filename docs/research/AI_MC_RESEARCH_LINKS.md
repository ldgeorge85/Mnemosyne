# AI-MC Research Links to Mnemosyne Documentation

## Mapping AI-MC Standards to Existing Research

### 1. Trust Models → Mnemosyne Trust Research

**AI-MC References:**
- Lee & See (2004): Trust in Automation
- Mayer-Davis-Schoorman (1995): ABI Model

**Mnemosyne Documents:**
- `docs/research/TRUST_MODELS.md` - Discusses EigenTrust and symbolic ceremonies
- `docs/research/trust_establishment_protocols.md` - Progressive trust exchange

**Integration Points:**
- Replace speculative "resonance" metrics with proven ABI dimensions
- Use Lee & See calibration for agent confidence display
- Validate symbolic ceremonies against established trust formation

### 2. Identity Standards → Identity Compression Research

**AI-MC References:**
- W3C Verifiable Credentials (VCs)
- W3C Decentralized Identifiers (DIDs)
- OAuth 2.0 / OpenID Connect

**Mnemosyne Documents:**
- `docs/research/identity_compression_research.md` - 100-128 bit hypothesis
- `docs/research/compression_boundaries.md` - Information theoretic analysis

**Integration Points:**
- Identity compression becomes a VC claim, not core architecture
- DIDs replace custom UUID system
- Compression validation uses VC verification rates

### 3. Privacy Technologies → Privacy Guarantees

**AI-MC References:**
- Differential Privacy (Dwork et al.)
- Private Set Intersection (PSI)
- Bloom Filters
- Fully Homomorphic Encryption

**Mnemosyne Documents:**
- `docs/research/privacy_guarantees_formal.md` - Formal privacy proofs
- `docs/research/nullifier_design.md` - Unlinkability mechanisms

**Integration Points:**
- PSI replaces custom "resonance matching"
- Bloom filters for nullifier registries (already suggested in research)
- Formal DP replaces ad-hoc anonymization

### 4. Provenance → Research Validation

**AI-MC References:**
- W3C PROV Data Model
- C2PA Content Credentials
- Model Cards / Data Sheets

**Mnemosyne Documents:**
- `docs/research/RESEARCH_SPRINT_PLAN.md` - Validation methodology
- `docs/research/INTEGRATION_PLAN.md` - Implementation tracking

**Integration Points:**
- Every research claim gets PROV graph
- Experimental outputs signed with C2PA
- Model Cards for each hypothesis validation

### 5. Secure Messaging → MLS Protocol

**AI-MC References:**
- MLS (RFC 9420)
- Signal Double Ratchet

**Mnemosyne Documents:**
- `docs/research/mls_protocol_analysis.md` - Already analyzed MLS
- `docs/research/protocol_comparison.md` - Compared alternatives

**Status:** ✅ Already aligned - research correctly identified MLS

### 6. Reputation Systems → Collective Intelligence

**AI-MC References:**
- EigenTrust Algorithm
- PageRank
- SybilGuard

**Mnemosyne Documents:**
- `docs/research/quorum_dynamics.md` - Consensus formation
- `docs/research/consensus_coordination_mechanisms.md` - Byzantine consensus

**Integration Points:**
- EigenTrust replaces custom trust scoring
- PageRank for influence propagation
- SybilGuard for open participation

### 7. Regulatory Compliance → Governance

**AI-MC References:**
- EU AI Act (Aug 2024)
- ISO/IEC 42001:2023
- NIST AI RMF

**Mnemosyne Documents:**
- Limited governance discussion in research
- No explicit regulatory compliance analysis

**Critical Gap:** Need immediate EU AI Act compliance assessment

## Research Hypothesis Validation Using AI-MC

### Behavioral Stability (70/30 Rule)

**Current Approach:** Unvalidated hypothesis
**AI-MC Validation:**
- Use Lee & See trust stability metrics
- Apply temporal consistency from trust automation literature
- Validate against Reeves & Nass Media Equation findings

### Identity Compression (100-128 bits)

**Current Approach:** Theoretical speculation
**AI-MC Validation:**
- Test compression as VC attribute set
- Use PSI collision rates as quality metric
- Validate against DID resolution success rates

### Resonance Mechanics

**Current Approach:** Undefined mathematical construct
**AI-MC Validation:**
- Replace with EigenTrust similarity scores
- Use PageRank for propagation dynamics
- Validate against social network trust formation

### Cultural Universality

**Current Approach:** Unsubstantiated claims
**AI-MC Validation:**
- Test against W3C internationalization standards
- Use C2PA multi-cultural content guidelines
- Validate with established cross-cultural HCI research

## Documentation Improvements Needed

### High Priority Updates

1. **Add to TRUST_MODELS.md:**
   - Lee & See trust calibration framework
   - MDS ability/benevolence/integrity model
   - Quantitative trust metrics

2. **Add to privacy_guarantees_formal.md:**
   - Formal differential privacy definitions
   - PSI security proofs
   - Bloom filter false positive analysis

3. **Create new governance.md:**
   - EU AI Act compliance checklist
   - ISO 42001 requirements mapping
   - NIST AI RMF assessment

4. **Update INTEGRATION_PLAN.md:**
   - W3C standards adoption timeline
   - C2PA implementation phases
   - Model Card generation pipeline

### Research Corrections Needed

1. **behavioral_stability_analysis.md:**
   - Add: "Requires validation against Lee & See metrics"
   - Add: "70/30 ratio is hypothesis, not finding"

2. **compression_boundaries.md:**
   - Add: "No empirical validation exists"
   - Add: "W3C VCs provide alternative approach"

3. **resonance_mechanics.md:**
   - Add: "Consider replacing with EigenTrust"
   - Add: "No validated resonance function exists"

## Validation Study Designs Using AI-MC

### Study 1: Trust Calibration Validation
- **Hypothesis:** Behavioral stability enables trust calibration
- **Method:** Apply Lee & See experimental protocol
- **Metrics:** Appropriate reliance, trust-performance correlation
- **Timeline:** 3 months

### Study 2: Identity Compression via VCs
- **Hypothesis:** Identity fits in 100-128 bit VC attribute set
- **Method:** Issue VCs with compressed attributes, measure verification
- **Metrics:** Verification success rate, attribute collision rate
- **Timeline:** 6 months

### Study 3: Privacy-Preserving Resonance
- **Hypothesis:** PSI can replace resonance matching
- **Method:** Implement PSI-based matching, compare to "resonance"
- **Metrics:** Match accuracy, privacy leakage, performance
- **Timeline:** 2 months

## Implementation Checklist

### Immediate (Week 1)
- [ ] Add W3C DID support to core
- [ ] Implement PROV-DM in Research Bus
- [ ] Create Model Card template
- [ ] Document EU AI Act gaps

### Short-term (Month 1)
- [ ] Deploy VC issuance system
- [ ] Implement PSI for matching
- [ ] Add trust calibration UI
- [ ] Set up C2PA signing

### Research Track (Ongoing)
- [ ] Validate behavioral stability with trust metrics
- [ ] Test identity compression as VC claims
- [ ] Replace resonance with EigenTrust
- [ ] Conduct cross-cultural validation

## References to Add to Research Docs

### Core Papers
1. Lee, J. D., & See, K. A. (2004). Trust in automation: Designing for appropriate reliance. Human Factors, 46(1), 50-80.
2. Mayer, R. C., Davis, J. H., & Schoorman, F. D. (1995). An integrative model of organizational trust. Academy of Management Review, 20(3), 709-734.
3. Hancock, J. T., et al. (2020). AI-mediated communication: Definition, research agenda, and ethical considerations. JCMC, 25(1), 89-100.

### Standards Documents
1. W3C Verifiable Credentials Data Model 1.1
2. W3C Decentralized Identifiers (DIDs) v1.0
3. RFC 9420: The Messaging Layer Security (MLS) Protocol
4. C2PA Technical Specification v2.2

### Privacy & Security
1. Dwork, C., & Roth, A. (2014). The Algorithmic Foundations of Differential Privacy
2. Private Set Intersection surveys (2023)
3. NIST AI Risk Management Framework 1.0

---

*This document maps AI-MC standards to existing Mnemosyne research, identifying gaps, corrections, and integration opportunities. Use this as a guide for updating research documentation and validation protocols.*