# The Mnemosyne Protocol Specification
## Version 4.0 - Dual-Track Edition

---

## 1. Core Architecture

### 1.1 Dual-Track System Design

The protocol implements strict separation between proven and experimental features:

```
┌─────────────────────────────────────────┐
│         Application Layer               │
│    (Chat UI, Memory Browser, Tasks)     │
├─────────────────────────────────────────┤
│     Track 1: Proven Core Services      │
│  (Standards-based, Production-ready)    │
├─────────────────────────────────────────┤
│      Standards & Protocols Layer        │
│  (W3C DIDs/VCs, OAuth, MLS, PROV)      │
├─────────────────────────────────────────┤
│    Track 2: Experimental Plugins       │
│    (Sandboxed, Opt-in, Validated)      │
│         [REQUIRES CONSENT]             │
├─────────────────────────────────────────┤
│      Research Infrastructure            │
│  (Metrics, Validation, Consent Mgmt)    │
└─────────────────────────────────────────┘
```

### 1.2 Design Principles

#### Track 1 Principles (Production)
1. **Standards-First** - W3C, IETF, OpenID standards throughout
2. **Privacy by Design** - Formal guarantees via differential privacy
3. **Security First** - End-to-end encryption, zero-knowledge proofs
4. **Transparent Limitations** - Model Cards, trust calibration
5. **Regulatory Compliance** - EU AI Act, ISO 42001, NIST AI RMF

#### Track 2 Principles (Research)
1. **Scientific Rigor** - Hypotheses with clear validation metrics
2. **Informed Consent** - IRB-compliant data collection
3. **Clear Labeling** - "EXPERIMENTAL" warnings mandatory
4. **Progressive Enhancement** - Graduation only after validation
5. **Sandboxed Execution** - Cannot affect core stability

### 1.3 Technology Stack

#### Core Services (Track 1)
- **Identity**: W3C DIDs with resolver infrastructure ✅
- **Credentials**: W3C Verifiable Credentials ✅
- **Authentication**: Modular auth (Static/OAuth/DID/API Key) ✅
- **API Framework**: FastAPI with async/await ✅
- **Database**: PostgreSQL with Async SQLAlchemy ✅
- **Vector Store**: Qdrant (multi-embedding support) ✅
- **Queue/Events**: Redis/KeyDB streams ✅
- **Configuration**: Pydantic Settings ✅
- **Frontend**: React + TypeScript + ChakraUI ⚠️ NOT CONNECTED

#### Standards Integration
- **Provenance**: W3C PROV-DM for data lineage
- **Trust**: Lee & See framework, MDS ABI model
- **Transparency**: Model Cards (Mitchell et al. 2019)
- **Content**: C2PA for authenticity signatures

#### Security & Cryptography
- **Messaging Protocol**: MLS (RFC 9420) for E2E groups
- **Privacy**: PSI, Bloom filters, formal DP
- **Reputation**: EigenTrust, PageRank algorithms
- **General Crypto**: libsodium/NaCl primitives

#### Experimental Components (Track 2)
- **Identity Compression**: 100-128 bit hypothesis (UNVALIDATED)
- **Behavioral Stability**: 70/30 rule (REQUIRES VALIDATION)
- **Resonance Mechanics**: Compatibility metrics (EXPERIMENTAL)
- **Symbolic Systems**: Archetype mapping (RESEARCH PHASE)

---

## 2. Track 1: Core Protocol Layers

### 2.1 Identity Layer (W3C DIDs)

#### DID Method Specification
```
did:mnem:Base58(Hash(PublicKey))

Example: did:mnem:3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy
```

#### DID Document Structure
```json
{
  "@context": [
    "https://www.w3.org/ns/did/v1",
    "https://w3id.org/security/suites/jws-2020/v1"
  ],
  "id": "did:mnem:3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy",
  "verificationMethod": [{
    "id": "#key-1",
    "type": "JsonWebKey2020",
    "controller": "did:mnem:3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy",
    "publicKeyJwk": {...}
  }],
  "authentication": ["#key-1"],
  "assertionMethod": ["#key-1"]
}
```

### 2.2 Authentication Layer (OAuth 2.0 + OIDC)

#### Token Flow
```python
class AuthenticationFlow:
    async def authenticate(self, credentials: OAuth2PasswordBearer):
        # OAuth 2.0 password flow
        token = await self.oauth_provider.get_token(credentials)
        
        # OIDC ID token validation
        id_token = await self.oidc_provider.validate(token)
        
        # WebAuthn for second factor
        if self.requires_2fa(id_token.sub):
            await self.webauthn.verify(credentials)
        
        return AuthToken(
            access_token=token.access_token,
            id_token=id_token,
            did=self.resolve_did(id_token.sub)
        )
```

### 2.3 Messaging Layer (MLS Protocol)

#### Group Operations
```python
class MLSGroupManager:
    async def create_group(self, creator_did: str) -> MLSGroup:
        # Initialize group with creator
        group = await self.mls.create_group(creator_did)
        
        # TreeKEM for key agreement
        group.key_tree = TreeKEM()
        
        # Enable post-compromise security
        group.enable_pcs()
        
        return group
    
    async def add_member(self, group: MLSGroup, member_did: str):
        # Fetch member's key package
        key_package = await self.fetch_key_package(member_did)
        
        # Update group state
        commit = await group.add(key_package)
        
        # Distribute to all members
        await self.distribute_commit(group, commit)
```

### 2.4 Privacy Layer

#### Differential Privacy Implementation
```python
class DifferentialPrivacy:
    def __init__(self, epsilon: float = 1.0):
        self.epsilon = epsilon  # Privacy budget
    
    def add_laplace_noise(self, value: float, sensitivity: float) -> float:
        """Add calibrated noise for ε-differential privacy"""
        scale = sensitivity / self.epsilon
        noise = np.random.laplace(0, scale)
        return value + noise
    
    def private_aggregate(self, data: List[float]) -> float:
        """Compute differentially private sum"""
        true_sum = sum(data)
        sensitivity = max(abs(d) for d in data)
        return self.add_laplace_noise(true_sum, sensitivity)
```

#### Private Set Intersection
```python
class PSI:
    async def intersect(self, 
                       local_set: Set[bytes],
                       remote_party: Party) -> Set[bytes]:
        # Diffie-Hellman PSI protocol
        # Hash elements with shared secret
        hashed_local = {self.hash_element(e) for e in local_set}
        hashed_remote = await remote_party.get_hashed_set()
        
        # Find intersection without revealing non-matches
        intersection_hashes = hashed_local & hashed_remote
        
        # Recover original elements
        return self.recover_elements(intersection_hashes)
```

### 2.5 Trust & Transparency Layer

#### Model Cards Generation
```python
class ModelCard:
    def generate(self, model: AIModel) -> Dict:
        return {
            "model_details": {
                "name": model.name,
                "version": model.version,
                "type": model.type,
                "training_date": model.training_date
            },
            "intended_use": {
                "primary_uses": model.primary_uses,
                "out_of_scope": model.out_of_scope_uses
            },
            "performance": {
                "metrics": model.evaluation_metrics,
                "test_data": model.test_dataset_info,
                "limitations": model.known_limitations
            },
            "ethical_considerations": {
                "bias_assessment": model.bias_assessment,
                "fairness_metrics": model.fairness_metrics
            },
            "transparency": {
                "is_experimental": model.is_experimental,
                "validation_status": model.validation_status,
                "hypothesis_doc": model.hypothesis_doc if model.is_experimental else None
            }
        }
```

#### Trust Calibration (Lee & See Framework)
```python
class TrustCalibration:
    def calculate_trust_score(self, 
                             ability: float,
                             benevolence: float, 
                             integrity: float) -> TrustScore:
        """MDS ABI model for trust measurement"""
        # Weighted combination
        trust = (0.5 * ability + 0.3 * benevolence + 0.2 * integrity)
        
        # Calibrate to user's risk tolerance
        calibrated = self.calibrate_to_user(trust)
        
        return TrustScore(
            raw_score=trust,
            calibrated_score=calibrated,
            components={
                "ability": ability,
                "benevolence": benevolence,
                "integrity": integrity
            },
            recommendation=self.get_reliance_recommendation(calibrated)
        )
```

---

## 3. Track 2: Experimental Protocols

### 3.1 Plugin Interface

```python
class ExperimentalPlugin(PluginInterface):
    """Base class for all experimental features"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.require_hypothesis_doc()
        self.require_consent()
        self.enable_metrics_collection()
    
    @property
    def warning_label(self) -> str:
        return """
        ⚠️ EXPERIMENTAL FEATURE
        This feature is based on unvalidated hypotheses.
        See: {self.hypothesis_doc}
        Status: {self.validation_status}
        Consent Required: Yes
        """
    
    async def validate_hypothesis(self) -> ValidationResult:
        """Run validation tests against success criteria"""
        pass
```

### 3.2 Identity Compression (HYPOTHESIS)

**Status**: UNVALIDATED  
**Hypothesis**: Human identity can be compressed to 100-128 bits  
**Success Criteria**: MI > 80%, F1 > 0.75, Human interpretability > 4/5

```python
class IdentityCompressionPlugin(ExperimentalPlugin):
    hypothesis_doc = "docs/hypotheses/id_compression.md"
    
    async def compress(self, behavioral_data: Dict) -> Optional[bytes]:
        # Require feature flag and consent
        self.require_experimental_flag("experimental.id_compression")
        if not self.has_consent():
            return None
        
        # Theoretical compression (UNVALIDATED)
        features = await self.extract_features(behavioral_data)
        compressed = await self.reduce_dimensions(features, target_bits=128)
        
        # Emit research metrics
        await self.emit_metric("compression_ratio", len(features) / 128)
        
        return compressed
```

### 3.3 Behavioral Stability (HYPOTHESIS)

**Status**: UNVALIDATED  
**Hypothesis**: Human behavior is 70% stable, 30% dynamic  
**Success Criteria**: ICC > 0.7, PSI < 0.2, Predictive accuracy > 70%

```python
class BehavioralStabilityPlugin(ExperimentalPlugin):
    hypothesis_doc = "docs/hypotheses/behavioral_stability.md"
    
    async def track_stability(self, user_id: str, timepoint: int):
        # Longitudinal tracking (REQUIRES VALIDATION)
        current = await self.capture_behavioral_snapshot(user_id)
        baseline = await self.get_baseline(user_id)
        
        # Calculate stability metrics
        icc = self.calculate_icc(baseline, current)
        psi = self.calculate_psi(baseline, current)
        
        # Emit for validation study
        await self.emit_metric("stability.icc", icc)
        await self.emit_metric("stability.psi", psi)
        
        return StabilityMeasure(
            icc=icc,
            psi=psi,
            warning="UNVALIDATED HYPOTHESIS"
        )
```

---

## 4. Compliance & Governance

### 4.1 EU AI Act Requirements

```python
class EUAIActCompliance:
    def assess_system(self) -> ComplianceReport:
        return {
            "risk_category": "high_risk",  # Human-centric AI system
            "transparency_obligations": {
                "model_cards": "IMPLEMENTED",
                "user_notification": "IMPLEMENTED",
                "human_oversight": "IMPLEMENTED"
            },
            "data_governance": {
                "data_quality": "W3C PROV lineage",
                "bias_monitoring": "Ongoing metrics",
                "privacy": "GDPR + Differential Privacy"
            },
            "technical_documentation": {
                "architecture": "docs/spec/PROTOCOL.md",
                "risk_assessment": "docs/compliance/RISK_ASSESSMENT.md",
                "validation": "docs/research/validation/"
            },
            "conformity_assessment": "REQUIRED_BEFORE_DEPLOYMENT"
        }
```

### 4.2 Content Authenticity (C2PA)

```python
class C2PAContentSigner:
    async def sign_generated_content(self, content: bytes, metadata: Dict) -> SignedContent:
        manifest = {
            "claim_generator": "Mnemosyne Protocol v4.0",
            "claim_generator_info": {
                "name": "Mnemosyne",
                "version": "4.0",
                "model_card": self.get_model_card_url()
            },
            "assertions": [
                {
                    "label": "c2pa.ai_generated",
                    "data": {
                        "generated": True,
                        "model": metadata.get("model"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
            ]
        }
        
        signature = await self.create_signature(content, manifest)
        return SignedContent(content, manifest, signature)
```

---

## 5. Implementation Priorities

### 🚨 URGENT: Frontend UI Connection (Sprint 1C - 4 hours)
The system has a working backend but NO USABLE UI. This must be completed next:
1. Connect frontend to backend with CORS/proxy
2. Wire up static auth for development
3. Create login page and dashboard
4. Implement memory capture and display
5. Enable basic search functionality

**This makes Mnemosyne locally usable!**

### Phase 1: Standards Foundation (90% COMPLETE)
1. ✅ W3C DID implementation (did:mnem method)
2. ✅ OAuth 2.0 authentication with modular system
3. ✅ Model Cards system (EU AI Act compliant)
4. ✅ Trust calibration (Lee & See framework)
5. 🔄 W3C PROV integration
6. 📋 WebAuthn/FIDO2 authentication
7. 📋 EU AI Act compliance assessment

### Phase 2: Privacy & Security (NEXT PRIORITY)
1. MLS Protocol integration (Sprint 2A)
2. PSI implementation
3. Formal differential privacy
4. C2PA content authenticity
5. E2E encryption for groups

### Phase 3: Research Infrastructure (PLANNED)
1. IRB-compliant consent management
2. Longitudinal study orchestration
3. Metrics collection dashboards
4. Validation study protocols
5. Research Bus enhancements

### Phase 4: Experimental Validation (3-6 MONTHS)
1. Identity compression validation (MI > 80%, F1 > 0.75)
2. Behavioral stability studies (ICC > 0.7, PSI < 0.2)
3. Cross-cultural symbol recognition
4. Academic partnerships
5. Peer-reviewed publication

---

## 6. Protocol Versioning

- **v4.0**: Current - Dual-track architecture with standards focus
- **v3.1**: Deprecated - Unified experimental approach
- **v2.x**: Archived - Initial research phase
- **v1.x**: Historical - Proof of concept

---

*"Build on standards, validate through science."*