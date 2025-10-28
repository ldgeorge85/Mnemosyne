# Mnemosyne P2P Trust Protocol Roadmap
*From Single Instance to True Peer-to-Peer Trust Without Central Authority*

## Executive Summary

This roadmap outlines the evolution from our current single-instance trust primitive to a fully decentralized P2P protocol where separate Mnemosyne instances can negotiate binding agreements without any central authority. This is not about users sharing one platform - it's about independent sovereign instances forming a trust network.

## Current State: Single-Instance Trust (75% Complete)

### What We Have
- **Multi-party negotiation** within single database (2,046 lines)
- **Cryptographic receipts** with SHA-256 hashing
- **Binding commitments** once consensus reached
- **Appeals resolution** with voting system
- **Trust relationships** with graduated scoring

### What's Missing
- Instance-to-instance communication
- Identity portability across instances
- Distributed consensus mechanism
- Network discovery protocol
- Sybil resistance through trust web

## Target Architecture: True P2P Trust

### Vision
```
Alice's Mnemosyne ←→ Bob's Mnemosyne
     ↓                    ↓
Alice's Data         Bob's Data
     ↓                    ↓
Alice's ICV          Bob's ICV
```

Each party:
- Runs their own instance (sovereignty)
- Maintains their own data (privacy)
- Negotiates via protocol (interoperability)
- Forms trust network (Sybil resistance)

## Phase 1: Protocol Foundation (Q1 2025)

### 1.1 Message Protocol Specification
**Goal**: Define standard for instance-to-instance communication

#### Message Format
```json
{
  "protocol": "mnemosyne/trust/1.0",
  "message": {
    "id": "uuid",
    "type": "negotiation.offer|negotiation.accept|trust.exchange",
    "from": {
      "instance_id": "alice.mnemosyne.local",
      "user_icv_hash": "sha256_of_public_icv"
    },
    "to": {
      "instance_id": "bob.mnemosyne.net",
      "user_icv_hash": "sha256_of_public_icv"
    },
    "payload": {},
    "timestamp": "ISO-8601",
    "signature": "base64_encoded"
  },
  "proof": {
    "previous_hash": "sha256",
    "nonce": 12345,
    "merkle_root": "optional"
  }
}
```

#### Transport Options
1. **Direct HTTP/HTTPS** (simple, immediate)
2. **WebSocket** (real-time, bidirectional)
3. **Email-like** (async, resilient)
4. **IPFS** (distributed, permanent)

### 1.2 Digital Signatures Implementation
**Goal**: Non-repudiation and message integrity

```python
class MessageSigner:
    def sign(self, message: dict, private_key: str) -> str:
        """Sign message with Ed25519."""
        pass

    def verify(self, message: dict, signature: str, public_key: str) -> bool:
        """Verify signature."""
        pass
```

### 1.3 Instance Registry Protocol
**Goal**: Discovery without central directory

#### Hybrid Approach (User's Preference)
```
Instance Discovery Methods:
1. Direct URL exchange (manual bootstrap)
2. DHT-based discovery (Kademlia-like)
3. Friend-of-friend introduction
4. QR code exchange (in-person)
5. DNS TXT records (optional)
```

## Phase 2: Identity Compression Vectors (Q2 2025)

### 2.1 ICV Implementation (Based on Research)
**Goal**: Portable, verifiable identity across instances

#### ICV Structure
```python
class IdentityCompressionVector:
    # Core Components (from CONCEPTS_DEEP_DIVE.md)
    core_traits: np.array      # 40% - Stable characteristics
    adaptive_traits: np.array  # 40% - Evolving patterns
    private_traits: np.array   # 20% - Never shared

    # Public Projection
    public_icv: np.array       # For discovery/routing

    # Verification
    def generate_proof(self, challenge: str) -> ZKProof:
        """Prove identity without revealing ICV."""
        pass
```

### 2.2 Scoped ICV Disclosure
**Goal**: Progressive trust through selective revelation

```python
class ScopedICV:
    PUBLIC = "public"           # Minimal for routing
    TRANSACTIONAL = "transact"  # For specific interactions
    CONTRACTUAL = "contract"    # For trust relationships
    PRIVATE = "private"         # Never shared

    def get_scoped_icv(self, scope: str, relationship_depth: float) -> np.array:
        """Return ICV appropriate for scope and trust level."""
        pass
```

### 2.3 Trust Web Integration
**Goal**: Web of trust for Sybil resistance

```python
class TrustWeb:
    def __init__(self):
        self.endorsements = {}  # Who vouches for whom
        self.trust_paths = {}   # Paths between instances

    def calculate_trust_distance(self, from_icv: str, to_icv: str) -> float:
        """Calculate trust distance through web."""
        # Dijkstra's algorithm on trust graph
        pass

    def verify_newcomer(self, new_icv: str, vouchers: List[str]) -> bool:
        """Verify new instance through existing trust."""
        # Require minimum vouchers with sufficient trust
        pass
```

## Phase 3: P2P Negotiation Protocol (Q3 2025)

### 3.1 Cross-Instance Negotiation
**Goal**: Negotiate between separate instances

#### Protocol Flow
```
Alice's Instance                    Bob's Instance
       |                                  |
       |------ NEGOTIATION_INVITE ------->|
       |<----- NEGOTIATION_JOIN ----------|
       |                                  |
       |------ OFFER (signed) ----------->|
       |<----- COUNTER_OFFER (signed) ----|
       |                                  |
       |------ ACCEPT (signed) ---------->|
       |<----- ACCEPT (signed) -----------|
       |                                  |
       |------ FINALIZE (signed) -------->|
       |<----- FINALIZE (signed) ---------|
       |                                  |
    [BINDING]                         [BINDING]
```

### 3.2 Distributed Consensus
**Goal**: Agreement without shared state

```python
class DistributedConsensus:
    def __init__(self):
        self.pending_agreements = {}
        self.finalized_agreements = {}

    async def achieve_consensus(self, negotiation_id: str) -> bool:
        """Achieve consensus across instances."""
        # 1. Collect signed accepts from all parties
        # 2. Verify all signatures
        # 3. Ensure all accept same terms
        # 4. Generate binding proof
        pass

    def generate_binding_proof(self, terms: dict, signatures: List[str]) -> str:
        """Create cryptographic proof of agreement."""
        # Merkle tree of all components
        pass
```

### 3.3 Third-Party Verification
**Goal**: Provable agreements to non-participants

```python
class AgreementVerifier:
    def verify_agreement(self,
                        agreement_hash: str,
                        proofs: List[dict],
                        public_keys: List[str]) -> bool:
        """Verify agreement without access to instances."""
        # 1. Verify Merkle proofs
        # 2. Verify all signatures
        # 3. Verify consensus was achieved
        # 4. Verify no tampering
        pass
```

## Phase 4: Advanced Trust Mechanics (Q4 2025)

### 4.1 Arbiter & Escrow Roles
**Goal**: Specialized negotiation participants

```python
class NegotiationRole(Enum):
    PARTICIPANT = "participant"  # Direct party
    ARBITER = "arbiter"         # Neutral resolver
    ESCROW = "escrow"           # Resource holder
    WITNESS = "witness"         # Observer only

class Arbiter:
    def __init__(self, icv: str, reputation: float):
        self.icv = icv
        self.reputation = reputation

    async def mediate(self, dispute: dict) -> dict:
        """Provide neutral mediation."""
        pass

class EscrowAgent:
    def hold_resources(self, resources: dict, conditions: dict):
        """Hold resources until conditions met."""
        pass
```

### 4.2 Graduated Trust Exchange
**Goal**: Progressive trust building

```python
class GraduatedTrust:
    # Trust levels (from zero trust)
    STRANGER = 0.0      # No trust
    ENCOUNTERED = 0.1   # Have interacted
    TRANSACTED = 0.3    # Successful transaction
    RELIABLE = 0.5      # Multiple successes
    TRUSTED = 0.7       # Deep trust
    BONDED = 0.9        # Fully integrated

    def calculate_next_level(self,
                            current: float,
                            interaction_type: str,
                            outcome: str) -> float:
        """Calculate trust progression."""
        pass
```

### 4.3 Routing Protocol
**Goal**: Find paths through trust network

```python
class TrustRouter:
    def find_trust_path(self,
                       source: str,
                       destination: str,
                       max_hops: int = 6) -> List[str]:
        """Find path through trust network."""
        # Modified Dijkstra's with trust weights
        pass

    def advertise_instance(self, instance_id: str, neighbors: List[str]):
        """Advertise instance to trusted neighbors."""
        # Selective flooding with TTL
        pass
```

## Phase 5: Network Effects (2026)

### 5.1 Trust Network Formation
**Goal**: Organic network growth

```
Initial State (Q1 2025):
A --- B  (Direct connection)

Growth (Q2 2025):
A --- B --- C
 \         /
  D ----- E

Mature Network (2026):
    A---B---C
   /|\  |  /|\
  D-+-E-F-G-+-H
   \|/  |  \|/
    I---J---K
```

### 5.2 Network Services
- **Trust routing** between distant parties
- **Reputation aggregation** (optional)
- **Dispute resolution pools**
- **Escrow agent marketplace**
- **Identity verification ceremonies**

### 5.3 Ecosystem Development
- **Client libraries** (Python, JS, Rust)
- **Mobile apps** for identity management
- **Browser extensions** for web integration
- **Hardware wallets** for key storage
- **Institutional bridges** for legacy systems

## Implementation Priorities

### Immediate (This Month)
1. Fix current negotiation user ID handling
2. Add digital signatures to binding commits
3. Create hostile party demo (single instance)
4. Document message protocol spec

### Near-term (Q1 2025)
1. Implement HTTP-based message passing
2. Add Ed25519 signatures
3. Create instance discovery mechanism
4. Build cross-instance negotiation demo

### Medium-term (Q2-Q3 2025)
1. Implement ICV system
2. Build trust web
3. Add arbiter/escrow roles
4. Create routing protocol

### Long-term (Q4 2025+)
1. Scale testing with 100+ instances
2. Security audits
3. Reference implementations
4. Community building

## Success Metrics

### Technical Metrics
- **Consensus time** < 10 seconds for 10 parties
- **Verification time** < 100ms for third parties
- **Network discovery** < 5 hops average
- **Sybil resistance** > 90% detection rate

### Adoption Metrics
- **Phase 1**: 10 instances interconnected
- **Phase 2**: 100 instances, 1000 negotiations
- **Phase 3**: 1000 instances, 10K negotiations
- **Phase 4**: Self-sustaining network growth

## Risk Mitigation

### Technical Risks
| Risk | Impact | Mitigation |
|------|---------|------------|
| Protocol incompatibility | High | Versioning from day 1 |
| Sybil attacks | High | Graduated trust + vouching |
| Network partitions | Medium | Async reconciliation |
| Key compromise | High | Key rotation protocol |

### Social Risks
| Risk | Impact | Mitigation |
|------|---------|------------|
| Bad actor infiltration | High | Trust web defense |
| Dispute flooding | Medium | Rate limiting + stakes |
| Ghost town effect | High | Focus on quality over quantity |
| Centralization pressure | High | Maintain sovereignty invariants |

## Development Philosophy

### Core Principles
1. **Sovereignty First** - Every instance is independent
2. **No Central Authority** - Not even us
3. **Progressive Decentralization** - Start simple, evolve
4. **Adversarial Mindset** - Assume hostile environment
5. **Gradual Trust** - Zero trust default, earn everything

### What We're NOT Building
- Not a blockchain (no global consensus needed)
- Not a reputation system (no scores follow you)
- Not a social network (no public profiles)
- Not a marketplace (no transaction fees)
- Not a company (no business model)

### What We ARE Building
- A protocol for sovereign instances to interact
- A primitive others can build upon
- A new category of human coordination
- A demonstration of the impossible
- A gift to those who need it

## Next Steps

### This Week
1. Review and refine this roadmap
2. Fix negotiation POST endpoint
3. Start message protocol specification
4. Begin signature implementation

### This Month
1. Complete Phase 1.1 specification
2. Implement basic message signing
3. Create cross-instance demo setup
4. Document protocol for others

### This Quarter
1. Launch testnet with 10 instances
2. Implement basic ICV
3. Test hostile party scenarios
4. Publish first paper

## Conclusion

This roadmap charts a path from our current single-instance implementation to a true P2P trust network. Each phase builds on the previous, maintaining backwards compatibility while adding new capabilities. The goal isn't to create a product but to prove that trust without central authority is possible at network scale.

The current 75% complete trust primitive is the seed. The P2P protocol is the garden. The trust network is the ecosystem that emerges.

---

## Addendum: Technical Dependencies

### Required Infrastructure
- PostgreSQL with UUID support
- Redis for message queuing
- Qdrant for vector operations
- Docker for instance isolation

### External Libraries
- `cryptography` for Ed25519
- `asyncio` for concurrent operations
- `httpx` for async HTTP
- `websockets` for real-time

### Protocol Standards
- JSON-LD for semantic messages
- W3C DIDs for identity (compatible)
- OpenAPI for API documentation
- JWT for session management (internal)

---

*"Trust is not given, it is constructed - one cryptographic proof at a time."*