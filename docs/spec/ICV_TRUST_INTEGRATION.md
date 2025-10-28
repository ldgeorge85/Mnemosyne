# Identity Compression Vectors (ICV) - Trust Primitive Integration
*Specification for Identity Portability in P2P Trust Networks*

## Overview

Identity Compression Vectors (ICVs) are the foundational identity primitive that enables trust establishment between sovereign Mnemosyne instances. This specification defines how ICVs integrate with the trust primitive to enable verifiable, portable identity without central authority.

## Core Concept

An ICV is a compressed mathematical representation of an identity that:
- **Preserves** essential identity characteristics
- **Protects** privacy through selective disclosure
- **Proves** identity without revealing details
- **Persists** across instances and time
- **Progresses** through interactions

## ICV Architecture

### 1. Vector Structure

```python
class IdentityCompressionVector:
    """
    Core identity representation.
    Total: 128 dimensions (reduced from speculative 256)
    """

    def __init__(self):
        # Core Identity (51 dims, 40%)
        self.core_traits = np.zeros(51)        # Stable characteristics
        self.core_metadata = {
            "creation_time": None,
            "last_rotation": None,
            "stability_score": 0.0
        }

        # Adaptive Identity (51 dims, 40%)
        self.adaptive_traits = np.zeros(51)    # Evolving patterns
        self.adaptive_metadata = {
            "last_update": None,
            "volatility_score": 0.0,
            "update_count": 0
        }

        # Private Identity (26 dims, 20%)
        self.private_traits = np.zeros(26)     # Never shared
        self.private_metadata = {
            "encryption_key": None,
            "access_log": []
        }

        # Cryptographic components
        self.public_key = None                  # Ed25519 public key
        self.icv_hash = None                   # SHA-256 of public projection
        self.proof_nonce = None                # For ZK proofs
```

### 2. Scoped Projections

Different trust contexts require different identity revelations:

```python
class ScopedICV:
    """Progressive identity disclosure based on trust relationship."""

    PUBLIC = "public"           # 32 dims - Discovery only
    HANDSHAKE = "handshake"     # 48 dims - Initial contact
    TRANSACTIONAL = "transact"  # 64 dims - Business interaction
    RELATIONAL = "relational"   # 96 dims - Ongoing relationship
    INTIMATE = "intimate"       # 102 dims - Deep trust

    def project(self,
                full_icv: IdentityCompressionVector,
                scope: str,
                trust_level: float) -> np.array:
        """
        Generate scoped projection of ICV.

        Args:
            full_icv: Complete ICV
            scope: Disclosure scope
            trust_level: Current trust score (0.0-1.0)

        Returns:
            Projected vector appropriate for scope
        """
        if scope == self.PUBLIC:
            # Minimal: Just enough for routing
            projection = full_icv.core_traits[:16]  # Most stable traits

        elif scope == self.HANDSHAKE:
            # Basic compatibility check
            projection = np.concatenate([
                full_icv.core_traits[:24],
                full_icv.adaptive_traits[:24]
            ])

        elif scope == self.TRANSACTIONAL:
            # Business-relevant traits
            projection = np.concatenate([
                full_icv.core_traits[:32],
                full_icv.adaptive_traits[:32]
            ])

        elif scope == self.RELATIONAL:
            # Most non-private traits
            projection = np.concatenate([
                full_icv.core_traits[:48],
                full_icv.adaptive_traits[:48]
            ])

        elif scope == self.INTIMATE:
            # Nearly complete (still no private)
            projection = np.concatenate([
                full_icv.core_traits,
                full_icv.adaptive_traits
            ])

        else:
            raise ValueError(f"Unknown scope: {scope}")

        # Apply trust-based noise
        noise_level = max(0, 0.1 * (1 - trust_level))
        noise = np.random.normal(0, noise_level, projection.shape)

        return projection + noise
```

### 3. Zero-Knowledge Identity Proofs

Prove identity properties without revealing the ICV:

```python
class ICVProofSystem:
    """Zero-knowledge proofs for identity verification."""

    def prove_identity(self,
                      icv: IdentityCompressionVector,
                      challenge: str) -> dict:
        """
        Prove ownership of ICV without revealing it.

        Uses Schnorr protocol for proof of knowledge.
        """
        # Generate commitment
        r = generate_random_scalar()
        commitment = group_generator ** r

        # Hash challenge with commitment
        c = hash(challenge + str(commitment))

        # Generate response
        s = r + c * icv.private_key

        return {
            "commitment": commitment,
            "challenge": c,
            "response": s,
            "public_key": icv.public_key
        }

    def prove_trait_threshold(self,
                             icv: IdentityCompressionVector,
                             trait_index: int,
                             threshold: float) -> dict:
        """
        Prove a specific trait exceeds threshold without revealing value.

        Uses range proof (Bulletproofs-style).
        """
        trait_value = icv.core_traits[trait_index]

        # Generate proof that trait_value > threshold
        proof = generate_range_proof(
            value=trait_value,
            min_value=threshold,
            max_value=1.0  # Normalized traits
        )

        return {
            "trait_index": trait_index,
            "threshold": threshold,
            "proof": proof
        }

    def prove_compatibility(self,
                          icv1: IdentityCompressionVector,
                          icv2_hash: str,
                          min_compatibility: float) -> dict:
        """
        Prove compatibility with another ICV without revealing either.

        Uses secure multi-party computation.
        """
        # This would use garbled circuits or homomorphic encryption
        # Simplified version shown
        pass
```

## Trust Integration

### 1. Trust Establishment Protocol

How ICVs enable initial trust between strangers:

```python
class TrustEstablishment:
    """
    ICV-based trust establishment between instances.
    """

    async def initiate_trust_handshake(self,
                                      my_icv: IdentityCompressionVector,
                                      their_instance: str) -> dict:
        """
        Initiate trust establishment with another instance.
        """
        # Step 1: Generate public projection
        public_projection = ScopedICV().project(
            my_icv,
            ScopedICV.PUBLIC,
            trust_level=0.0  # No trust yet
        )

        # Step 2: Create signed introduction
        introduction = {
            "icv_hash": my_icv.icv_hash,
            "public_projection": public_projection.tolist(),
            "instance_id": self.instance_id,
            "timestamp": datetime.utcnow().isoformat(),
            "supported_protocols": ["mnemosyne/trust/1.0"],
            "proof": ICVProofSystem().prove_identity(my_icv, their_instance)
        }

        # Step 3: Sign with private key
        signature = sign_message(introduction, my_icv.private_key)
        introduction["signature"] = signature

        return introduction

    async def verify_trust_handshake(self,
                                    introduction: dict,
                                    minimum_compatibility: float = 0.3) -> bool:
        """
        Verify incoming trust handshake.
        """
        # Step 1: Verify signature
        valid_sig = verify_signature(
            introduction,
            introduction["signature"],
            introduction["proof"]["public_key"]
        )
        if not valid_sig:
            return False

        # Step 2: Verify identity proof
        valid_proof = ICVProofSystem().verify_identity(
            introduction["proof"],
            introduction["instance_id"]
        )
        if not valid_proof:
            return False

        # Step 3: Check compatibility (if we have enough info)
        if "public_projection" in introduction:
            compatibility = self.calculate_compatibility(
                self.my_icv,
                np.array(introduction["public_projection"])
            )
            if compatibility < minimum_compatibility:
                return False

        return True
```

### 2. Progressive Trust Building

How trust deepens through ICV exchanges:

```python
class ProgressiveTrust:
    """
    Trust progression through graduated ICV disclosure.
    """

    def __init__(self):
        self.trust_levels = {
            0.0: ScopedICV.PUBLIC,
            0.1: ScopedICV.HANDSHAKE,
            0.3: ScopedICV.TRANSACTIONAL,
            0.5: ScopedICV.RELATIONAL,
            0.7: ScopedICV.INTIMATE
        }

    def get_disclosure_scope(self, trust_score: float) -> str:
        """Determine appropriate disclosure scope for trust level."""
        for threshold in sorted(self.trust_levels.keys(), reverse=True):
            if trust_score >= threshold:
                return self.trust_levels[threshold]
        return ScopedICV.PUBLIC

    async def exchange_icv_update(self,
                                 my_icv: IdentityCompressionVector,
                                 relationship_id: str,
                                 current_trust: float) -> dict:
        """
        Share updated ICV projection based on current trust.
        """
        # Determine scope based on trust
        scope = self.get_disclosure_scope(current_trust)

        # Generate appropriate projection
        projection = ScopedICV().project(my_icv, scope, current_trust)

        # Create update message
        update = {
            "relationship_id": relationship_id,
            "icv_hash": my_icv.icv_hash,
            "projection_scope": scope,
            "projection": projection.tolist(),
            "trust_level": current_trust,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Sign update
        signature = sign_message(update, my_icv.private_key)
        update["signature"] = signature

        return update
```

### 3. Trust Web Formation

How ICVs create Sybil-resistant trust networks:

```python
class TrustWeb:
    """
    Web of trust using ICV endorsements.
    """

    def __init__(self):
        self.endorsements = {}  # icv_hash -> list of endorsements
        self.trust_paths = {}   # Cached trust paths

    def create_endorsement(self,
                          endorser_icv: IdentityCompressionVector,
                          endorsed_icv_hash: str,
                          trust_level: float,
                          context: str = "") -> dict:
        """
        Create an endorsement for another ICV.
        """
        endorsement = {
            "endorser": endorser_icv.icv_hash,
            "endorsed": endorsed_icv_hash,
            "trust_level": trust_level,
            "context": context,
            "timestamp": datetime.utcnow().isoformat(),
            "expires": (datetime.utcnow() + timedelta(days=90)).isoformat()
        }

        # Sign endorsement
        signature = sign_message(endorsement, endorser_icv.private_key)
        endorsement["signature"] = signature
        endorsement["endorser_public_key"] = endorser_icv.public_key

        return endorsement

    def calculate_trust_distance(self,
                                source_icv_hash: str,
                                target_icv_hash: str,
                                max_hops: int = 6) -> float:
        """
        Calculate trust distance through web of endorsements.

        Returns:
            Trust score (0.0-1.0) based on shortest trust path
        """
        if source_icv_hash == target_icv_hash:
            return 1.0

        # Check direct endorsement
        if target_icv_hash in self.endorsements.get(source_icv_hash, []):
            endorsement = self.get_endorsement(source_icv_hash, target_icv_hash)
            return endorsement["trust_level"]

        # Use Dijkstra's algorithm for trust path
        visited = set()
        queue = [(source_icv_hash, 1.0, 0)]  # (node, trust, hops)

        while queue and queue[0][2] < max_hops:
            current, current_trust, hops = queue.pop(0)

            if current in visited:
                continue
            visited.add(current)

            # Check if we reached target
            if current == target_icv_hash:
                return current_trust

            # Explore endorsements from current
            for endorsed in self.endorsements.get(current, []):
                if endorsed not in visited:
                    endorsement = self.get_endorsement(current, endorsed)
                    # Trust degrades through chain
                    new_trust = current_trust * endorsement["trust_level"] * 0.9
                    queue.append((endorsed, new_trust, hops + 1))
                    queue.sort(key=lambda x: -x[1])  # Sort by trust (descending)

        return 0.0  # No trust path found

    def verify_new_icv(self,
                      new_icv_hash: str,
                      endorsements: List[dict],
                      min_endorsements: int = 3,
                      min_total_trust: float = 1.5) -> bool:
        """
        Verify a new ICV through endorsements (Sybil resistance).
        """
        if len(endorsements) < min_endorsements:
            return False

        total_trust = 0.0
        verified_endorsers = set()

        for endorsement in endorsements:
            # Verify signature
            valid = verify_signature(
                endorsement,
                endorsement["signature"],
                endorsement["endorser_public_key"]
            )
            if not valid:
                continue

            # Check endorser isn't duplicate
            endorser = endorsement["endorser"]
            if endorser in verified_endorsers:
                continue
            verified_endorsers.add(endorser)

            # Add weighted trust
            endorser_reputation = self.get_reputation(endorser)
            total_trust += endorsement["trust_level"] * endorser_reputation

        return total_trust >= min_total_trust
```

## Negotiation Integration

How ICVs enhance multi-party negotiations:

```python
class ICVNegotiationEnhancement:
    """
    ICV integration with negotiation protocol.
    """

    def create_negotiation_with_icv(self,
                                   initiator_icv: IdentityCompressionVector,
                                   participant_icv_hashes: List[str],
                                   terms: dict) -> dict:
        """
        Create negotiation with ICV-based identity.
        """
        negotiation = {
            "id": str(uuid4()),
            "initiator": {
                "icv_hash": initiator_icv.icv_hash,
                "trust_proof": ICVProofSystem().prove_identity(
                    initiator_icv,
                    "negotiation_init"
                )
            },
            "participants": participant_icv_hashes,
            "terms": terms,
            "required_roles": {
                "arbiters": [],  # Can be added
                "escrow_agents": [],  # Can be added
                "witnesses": []  # Can be added
            },
            "icv_disclosures": {
                # Scope of ICV disclosure for this negotiation
                "required_scope": ScopedICV.TRANSACTIONAL,
                "minimum_trust": 0.3
            }
        }

        # Sign negotiation
        signature = sign_message(negotiation, initiator_icv.private_key)
        negotiation["signature"] = signature

        return negotiation

    def select_arbiter(self,
                      dispute: dict,
                      available_arbiters: List[dict]) -> str:
        """
        Select arbiter based on ICV compatibility and reputation.
        """
        best_arbiter = None
        best_score = 0.0

        for arbiter in available_arbiters:
            # Calculate trust distance to all parties
            trust_scores = []
            for party_icv_hash in dispute["parties"]:
                trust = self.trust_web.calculate_trust_distance(
                    party_icv_hash,
                    arbiter["icv_hash"]
                )
                trust_scores.append(trust)

            # Arbiter should be equally trusted by all
            avg_trust = sum(trust_scores) / len(trust_scores)
            trust_variance = sum((t - avg_trust)**2 for t in trust_scores)

            # Score: high average trust, low variance
            score = avg_trust / (1 + trust_variance)

            if score > best_score:
                best_score = score
                best_arbiter = arbiter["icv_hash"]

        return best_arbiter
```

## Privacy & Security

### 1. ICV Protection

```python
class ICVSecurity:
    """Security measures for ICV protection."""

    def encrypt_private_traits(self,
                              private_traits: np.array,
                              password: str) -> bytes:
        """Encrypt private traits with key derivation."""
        salt = os.urandom(16)
        key = derive_key(password, salt)

        # AES-256-GCM encryption
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(os.urandom(12))
        )
        encryptor = cipher.encryptor()

        ciphertext = encryptor.update(private_traits.tobytes())
        encryptor.finalize()

        return salt + encryptor.tag + ciphertext

    def rotate_icv(self,
                  old_icv: IdentityCompressionVector,
                  rotation_reason: str) -> IdentityCompressionVector:
        """
        Rotate ICV while maintaining continuity.
        """
        new_icv = IdentityCompressionVector()

        # Preserve core traits (with slight evolution)
        new_icv.core_traits = old_icv.core_traits * 0.95 + np.random.normal(0, 0.05, 51)

        # Update adaptive traits more significantly
        new_icv.adaptive_traits = old_icv.adaptive_traits * 0.7 + np.random.normal(0, 0.3, 51)

        # Generate new private traits
        new_icv.private_traits = np.random.normal(0, 1, 26)

        # New cryptographic material
        new_icv.public_key, new_icv.private_key = generate_keypair()

        # Link to old ICV
        new_icv.previous_icv_hash = old_icv.icv_hash
        new_icv.rotation_reason = rotation_reason
        new_icv.rotation_timestamp = datetime.utcnow()

        return new_icv
```

### 2. Attack Resistance

```python
class ICVAttackResistance:
    """Defenses against ICV-specific attacks."""

    def detect_icv_collision(self,
                           new_icv_hash: str,
                           similarity_threshold: float = 0.95) -> bool:
        """Detect attempts to create similar ICVs (impersonation)."""
        for existing_hash in self.all_known_icvs:
            similarity = calculate_hash_similarity(new_icv_hash, existing_hash)
            if similarity > similarity_threshold:
                return True  # Likely collision/impersonation
        return False

    def detect_sybil_cluster(self,
                           icv_hashes: List[str],
                           cluster_threshold: float = 0.8) -> bool:
        """Detect clusters of related ICVs (Sybil attack)."""
        # Build similarity matrix
        n = len(icv_hashes)
        similarity_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(i+1, n):
                sim = calculate_icv_similarity(icv_hashes[i], icv_hashes[j])
                similarity_matrix[i, j] = sim
                similarity_matrix[j, i] = sim

        # Check for high similarity clusters
        high_similarity_pairs = np.sum(similarity_matrix > cluster_threshold)
        expected_pairs = n * (n - 1) * 0.05  # 5% expected by chance

        return high_similarity_pairs > expected_pairs * 3  # 3x expected = suspicious
```

## Implementation Roadmap

### Phase 1: Basic ICV (Q1 2025)
- [ ] Implement 128-dimensional vector structure
- [ ] Create scoped projection system
- [ ] Add basic cryptographic signatures
- [ ] Build ICV generation from behavioral data

### Phase 2: Zero-Knowledge Proofs (Q2 2025)
- [ ] Implement Schnorr protocol for identity proofs
- [ ] Add range proofs for trait thresholds
- [ ] Create compatibility proofs
- [ ] Build verification system

### Phase 3: Trust Web (Q2-Q3 2025)
- [ ] Implement endorsement system
- [ ] Build trust path calculation
- [ ] Add Sybil detection
- [ ] Create reputation aggregation

### Phase 4: Full Integration (Q3-Q4 2025)
- [ ] Integrate with negotiation protocol
- [ ] Add arbiter selection
- [ ] Implement ICV rotation
- [ ] Create recovery mechanisms

## Conclusion

ICVs provide the identity foundation for P2P trust networks, enabling:
- **Verifiable identity** without central authority
- **Progressive disclosure** based on trust
- **Sybil resistance** through endorsement webs
- **Privacy preservation** through ZK proofs
- **Negotiation enhancement** through role assignment

Combined with the trust primitive, ICVs enable truly sovereign instances to form binding agreements while maintaining complete independence.

---

*"Identity is not who you are, but how you can be verified to be you."*