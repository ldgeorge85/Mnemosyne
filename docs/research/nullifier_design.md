# Nullifier Design: Preventing Correlation Across Contexts
## Privacy Through Unlinkable One-Time Tokens

---

## Executive Summary

**Nullifiers enable privacy-preserving, one-time actions without revealing identity or enabling correlation across contexts.** We design a hierarchical nullifier system with deterministic derivation, context separation, and epoch-based rotation.

---

## Part I: The Correlation Problem

### Attack Scenarios

Without proper nullifiers, adversaries can:

```python
class CorrelationAttacks:
    def timing_correlation(self, actions):
        """
        Link actions by temporal patterns
        """
        # Alice always acts at 9am, 2pm, 7pm
        temporal_signature = extract_timing_pattern(actions)
        return find_matching_patterns(temporal_signature)
    
    def behavioral_correlation(self, proofs):
        """
        Link by consistent behavior
        """
        # Same proof patterns across contexts
        proof_signature = extract_proof_style(proofs)
        return cluster_by_signature(proof_signature)
    
    def network_correlation(self, connections):
        """
        Link by social graph
        """
        # Same set of connections in different contexts
        connection_fingerprint = extract_graph_signature(connections)
        return match_fingerprints(connection_fingerprint)
```

### Requirements for Unlinkability

1. **Context Separation**: Actions in different contexts unlinkable
2. **Temporal Unlinkability**: Actions at different times unlinkable
3. **One-Time Use**: Prevent double-spending/voting
4. **Deterministic**: Same input always produces same nullifier
5. **Unpredictable**: Cannot compute others' nullifiers

---

## Part II: Nullifier Theory

### Mathematical Foundation

A nullifier is a commitment that:
- Uniquely identifies an action
- Reveals nothing about the actor
- Cannot be linked to other nullifiers

Formally:
```
Nullifier: (Identity, Context, Action) → {0,1}^256

Properties:
1. Deterministic: N(I,C,A) always produces same output
2. Collision-resistant: N(I₁,C₁,A₁) ≠ N(I₂,C₂,A₂) for different inputs
3. Unlinkable: Given N₁,N₂ cannot determine if same I
4. Unpredictable: Cannot compute N without knowing I
```

### Basic Construction

```python
class BasicNullifier:
    def __init__(self, hash_function=SHA3_256):
        # Using SHA3-256 for post-quantum resistance
        # Poseidon is STARK-friendly but not necessarily PQ-safe
        self.hash = hash_function
        
    def generate(self, identity, context, nonce):
        """
        Basic nullifier generation
        """
        nullifier = self.hash(identity || context || nonce)
        return nullifier
    
    def verify_uniqueness(self, nullifier, used_set):
        """
        Check if nullifier already used
        """
        if nullifier in used_set:
            return False
        used_set.add(nullifier)
        return True
```

**Problem**: Too simple, doesn't handle complex requirements.

---

## Part III: Hierarchical Nullifier System

### Design Architecture

```
Nullifier Hierarchy:
├── Master Secret (never revealed)
├── Context Keys (derived per context)
├── Epoch Keys (rotated periodically)
└── Action Nullifiers (one per action)
```

### Implementation

```python
class HierarchicalNullifierSystem:
    def __init__(self, master_secret):
        self.master = master_secret
        self.context_keys = {}
        self.epoch_keys = {}
        
    def derive_context_key(self, context):
        """
        Derive context-specific key using keyed PRF (HKDF)
        """
        if context not in self.context_keys:
            # Use HKDF-SHA256 with proper domain separation
            # This provides computational security, not information-theoretic
            self.context_keys[context] = HKDF(
                self.master,
                salt=b"mnemosyne_context_v1",
                info=f"context:{context}".encode(),
                length=32  # 256 bits output
            )
        return self.context_keys[context]
    
    def derive_epoch_key(self, context, epoch):
        """
        Derive epoch-specific key
        """
        context_key = self.derive_context_key(context)
        
        key = (context, epoch)
        if key not in self.epoch_keys:
            self.epoch_keys[key] = KDF(
                context_key,
                salt=f"epoch:{epoch}",
                info="epoch_rotation"
            )
        return self.epoch_keys[key]
    
    def generate_nullifier(self, context, epoch, action, nonce=None):
        """
        Generate action-specific nullifier with optional blinding
        """
        epoch_key = self.derive_epoch_key(context, epoch)
        
        # Add per-action nonce to prevent guessing attacks
        if nonce is None:
            nonce = os.urandom(16)  # 128-bit nonce
        
        # Nullifier = PRF(epoch_key, action || nonce)
        # Using SHA3-256 for post-quantum resistance
        nullifier = SHA3_256(epoch_key + action.encode() + nonce)
        
        return nullifier, nonce
    
    def generate_with_proof(self, context, epoch, action):
        """
        Generate nullifier with ZK proof of correctness
        """
        nullifier = self.generate_nullifier(context, epoch, action)
        
        # Prove nullifier correctly derived without revealing keys
        proof = ZKProof.prove(
            statement="correct_nullifier_derivation",
            public=[nullifier, context, epoch, action],
            private=[self.master, self.context_keys[context]]
        )
        
        return nullifier, proof
```

---

## Part IV: Context Separation Mechanisms

### Domain-Specific Nullifiers

```python
class ContextSeparation:
    def __init__(self):
        self.domains = {
            'voting': VotingNullifier(),
            'messaging': MessagingNullifier(),
            'transactions': TransactionNullifier(),
            'authentication': AuthNullifier()
        }
    
    def get_nullifier_scheme(self, context_type):
        """
        Different schemes for different contexts
        """
        return self.domains.get(context_type, DefaultNullifier())

class VotingNullifier:
    """
    Nullifiers for voting (one per election)
    """
    def generate(self, identity, election_id):
        # Deterministic: same person always gets same nullifier for election
        return hash(identity.voting_key, election_id)
    
    def verify(self, nullifier, election):
        # Check not already voted
        if nullifier in election.used_nullifiers:
            raise DoubleVotingAttempt()
        
        election.used_nullifiers.add(nullifier)
        return True

class MessagingNullifier:
    """
    Nullifiers for messages (new each message)
    """
    def generate(self, identity, conversation_id, message_index):
        # Include message index for uniqueness
        return hash(identity.messaging_key, conversation_id, message_index)

class TransactionNullifier:
    """
    Nullifiers for transactions (prevent double-spend)
    """
    def generate(self, identity, utxo):
        # Tied to specific unspent output
        return hash(identity.transaction_key, utxo.id)
```

### Cross-Context Unlinkability

```python
class UnlinkabilityGuarantee:
    def __init__(self):
        self.context_transforms = {}
    
    def ensure_unlinkability(self, identity, contexts):
        """
        Ensure nullifiers across contexts are unlinkable
        """
        nullifiers = []
        
        for context in contexts:
            # Different derivation path per context
            context_identity = self.transform_identity(identity, context)
            nullifier = self.generate_nullifier(context_identity, context)
            nullifiers.append(nullifier)
        
        # Verify statistical independence
        correlation = self.compute_correlation(nullifiers)
        assert correlation < 0.01, "Nullifiers are correlated!"
        
        return nullifiers
    
    def transform_identity(self, identity, context):
        """
        Context-specific identity transformation
        """
        # Use different projection for each context
        if context not in self.context_transforms:
            self.context_transforms[context] = random_orthogonal_matrix()
        
        transformed = self.context_transforms[context] @ identity.vector
        return Identity(transformed)
    
    def compute_correlation(self, nullifiers):
        """
        Measure statistical correlation between nullifiers
        """
        # Convert to bit vectors
        bit_vectors = [to_bits(n) for n in nullifiers]
        
        # Compute pairwise correlations
        correlations = []
        for i in range(len(bit_vectors)):
            for j in range(i+1, len(bit_vectors)):
                corr = pearson_correlation(bit_vectors[i], bit_vectors[j])
                correlations.append(abs(corr))
        
        return max(correlations) if correlations else 0
```

---

## Part V: Epoch-Based Rotation

### Temporal Unlinkability

```python
class EpochRotation:
    def __init__(self, epoch_duration=86400):  # 1 day
        self.epoch_duration = epoch_duration
        self.current_epoch = self.get_current_epoch()
        self.epoch_nullifiers = defaultdict(set)
    
    def get_current_epoch(self):
        """
        Calculate current epoch number
        """
        return int(time.time() // self.epoch_duration)
    
    def rotate_if_needed(self):
        """
        Check and perform epoch rotation
        """
        new_epoch = self.get_current_epoch()
        
        if new_epoch > self.current_epoch:
            self.perform_rotation(new_epoch)
            self.current_epoch = new_epoch
    
    def perform_rotation(self, new_epoch):
        """
        Rotate to new epoch
        """
        # Archive old nullifiers
        old_epoch = new_epoch - 1
        if old_epoch in self.epoch_nullifiers:
            self.archive_nullifiers(old_epoch, self.epoch_nullifiers[old_epoch])
            del self.epoch_nullifiers[old_epoch]
        
        # Generate new epoch parameters
        self.initialize_epoch(new_epoch)
    
    def generate_epoch_nullifier(self, identity, action):
        """
        Generate nullifier for current epoch
        """
        self.rotate_if_needed()
        
        # Include epoch in derivation
        nullifier = hash(
            identity.epoch_key(self.current_epoch),
            action,
            self.current_epoch
        )
        
        # Track for uniqueness within epoch
        if nullifier in self.epoch_nullifiers[self.current_epoch]:
            raise NullifierAlreadyUsed()
        
        self.epoch_nullifiers[self.current_epoch].add(nullifier)
        
        return nullifier, self.current_epoch
```

### Forward Security

```python
class ForwardSecureNullifiers:
    """
    Past nullifiers remain valid even if current key compromised
    """
    def __init__(self):
        self.key_chain = self.initialize_chain()
        self.current_index = 0
    
    def initialize_chain(self, length=365):
        """
        Generate hash chain for forward security
        """
        # Start with random seed
        chain = [random_bytes(32)]
        
        # Build chain backwards
        for i in range(length - 1):
            chain.append(hash(chain[-1]))
        
        # Reverse so we can reveal forward
        return chain[::-1]
    
    def get_current_key(self):
        """
        Get current key and advance
        """
        if self.current_index >= len(self.key_chain):
            # Regenerate chain
            self.key_chain = self.initialize_chain()
            self.current_index = 0
        
        key = self.key_chain[self.current_index]
        self.current_index += 1
        
        # Delete old keys for forward security
        if self.current_index > 1:
            self.key_chain[self.current_index - 2] = None
        
        return key
    
    def generate_forward_secure_nullifier(self, action):
        """
        Generate nullifier with forward security
        """
        current_key = self.get_current_key()
        nullifier = hash(current_key, action)
        
        # Cannot generate past nullifiers even if current key leaked
        return nullifier
```

---

## Part VI: Zero-Knowledge Nullifier Proofs

### Proving Nullifier Correctness

```python
class ZKNullifierProof:
    def __init__(self):
        self.circuit = self.build_circuit()
    
    def build_circuit(self):
        """
        STARK circuit for nullifier proof
        """
        circuit = STARKCircuit()
        
        # Public inputs
        circuit.add_public('nullifier')
        circuit.add_public('context')
        circuit.add_public('epoch')
        circuit.add_public('merkle_root')  # Identity set
        
        # Private inputs
        circuit.add_private('identity')
        circuit.add_private('master_secret')
        circuit.add_private('merkle_path')
        circuit.add_private('derivation_path')
        
        # Constraints
        
        # 1. Identity is in authorized set
        circuit.add_constraint(
            'membership',
            lambda identity, path, root:
                verify_merkle_path(identity, path, root)
        )
        
        # 2. Nullifier correctly derived
        circuit.add_constraint(
            'derivation',
            lambda master, context, epoch, nullifier:
                derive_nullifier(master, context, epoch) == nullifier
        )
        
        # 3. Identity owns master secret
        circuit.add_constraint(
            'ownership',
            lambda identity, master:
                hash(master) == identity.commitment
        )
        
        return circuit
    
    def prove_nullifier(self, identity, nullifier, context, epoch):
        """
        Generate ZK proof for nullifier
        """
        proof = STARK.prove(
            circuit=self.circuit,
            public_inputs={
                'nullifier': nullifier,
                'context': context,
                'epoch': epoch,
                'merkle_root': get_identity_root()
            },
            private_inputs={
                'identity': identity.symbol,
                'master_secret': identity.master,
                'merkle_path': get_merkle_path(identity),
                'derivation_path': get_derivation_path(identity, context, epoch)
            }
        )
        
        return proof
    
    def verify_nullifier(self, nullifier, proof, context, epoch):
        """
        Verify nullifier proof
        """
        # Check nullifier not used
        if is_nullifier_used(nullifier, context, epoch):
            return False
        
        # Verify ZK proof
        valid = STARK.verify(
            proof=proof,
            circuit=self.circuit,
            public_inputs={
                'nullifier': nullifier,
                'context': context,
                'epoch': epoch,
                'merkle_root': get_identity_root()
            }
        )
        
        if valid:
            mark_nullifier_used(nullifier, context, epoch)
        
        return valid
```

---

## Part VII: Nullifier Storage and Management

### Efficient Storage

```python
class NullifierStorage:
    def __init__(self):
        self.bloom_filter = BloomFilter(
            capacity=10_000_000,
            error_rate=0.001
        )
        self.recent_nullifiers = deque(maxlen=100_000)
        self.persistent_storage = NullifierDB()
    
    def add_nullifier(self, nullifier, context, epoch):
        """
        Store nullifier efficiently
        """
        # Quick check in Bloom filter
        if nullifier in self.bloom_filter:
            # Might be duplicate, check thoroughly
            if self.check_duplicate(nullifier, context, epoch):
                raise DuplicateNullifier()
        
        # Add to all storage layers
        self.bloom_filter.add(nullifier)
        self.recent_nullifiers.append({
            'nullifier': nullifier,
            'context': context,
            'epoch': epoch,
            'timestamp': time.time()
        })
        
        # Persist for long-term storage
        self.persistent_storage.insert(nullifier, context, epoch)
    
    def check_duplicate(self, nullifier, context, epoch):
        """
        Thorough duplicate check
        """
        # Check recent cache
        for entry in self.recent_nullifiers:
            if entry['nullifier'] == nullifier and \
               entry['context'] == context and \
               entry['epoch'] == epoch:
                return True
        
        # Check persistent storage
        return self.persistent_storage.exists(nullifier, context, epoch)
    
    def cleanup_old_epochs(self, current_epoch, retention_epochs=7):
        """
        Remove old nullifiers outside retention window
        """
        cutoff_epoch = current_epoch - retention_epochs
        
        # Remove from recent cache
        self.recent_nullifiers = deque(
            (n for n in self.recent_nullifiers if n['epoch'] >= cutoff_epoch),
            maxlen=100_000
        )
        
        # Archive in persistent storage
        self.persistent_storage.archive_before_epoch(cutoff_epoch)
        
        # Rebuild Bloom filter periodically
        if current_epoch % 30 == 0:  # Monthly
            self.rebuild_bloom_filter()
```

### Nullifier Aggregation

```python
class NullifierAggregation:
    """
    Aggregate multiple nullifiers for batch verification
    """
    def __init__(self):
        self.accumulator = 1  # Multiplicative accumulator
        self.modulus = generate_safe_prime(2048)
    
    def aggregate_nullifiers(self, nullifiers):
        """
        Create single proof for multiple nullifiers
        """
        # Hash nullifiers to primes
        primes = [hash_to_prime(n) for n in nullifiers]
        
        # Accumulate
        for prime in primes:
            self.accumulator = (self.accumulator * prime) % self.modulus
        
        # Generate batch proof
        batch_proof = self.generate_batch_proof(nullifiers, primes)
        
        return self.accumulator, batch_proof
    
    def verify_batch(self, nullifiers, accumulator, proof):
        """
        Verify all nullifiers in batch
        """
        # Verify accumulator correctness
        expected = 1
        for n in nullifiers:
            prime = hash_to_prime(n)
            expected = (expected * prime) % self.modulus
        
        if expected != accumulator:
            return False
        
        # Verify batch proof
        return self.verify_batch_proof(proof, accumulator, nullifiers)
```

---

## Part VIII: Application-Specific Nullifiers

### Voting System

```python
class VotingNullifiers:
    def __init__(self, election_id):
        self.election_id = election_id
        self.used_nullifiers = set()
        
    def generate_ballot_nullifier(self, voter_identity):
        """
        One nullifier per voter per election
        """
        # Deterministic for same voter
        nullifier = hash(
            voter_identity.voting_credential,
            self.election_id,
            "ballot_cast"
        )
        
        return nullifier
    
    def cast_vote(self, nullifier, encrypted_vote, proof):
        """
        Accept vote with nullifier
        """
        # Verify hasn't voted
        if nullifier in self.used_nullifiers:
            raise DoubleVotingAttempt()
        
        # Verify proof of eligibility
        if not self.verify_eligibility_proof(nullifier, proof):
            raise IneligibleVoter()
        
        # Record vote
        self.used_nullifiers.add(nullifier)
        self.record_encrypted_vote(encrypted_vote)
        
        return "Vote recorded"
```

### Anonymous Credentials

```python
class CredentialNullifiers:
    def __init__(self):
        self.credential_nullifiers = defaultdict(set)
    
    def generate_show_nullifier(self, credential, context, nonce):
        """
        Nullifier for showing credential
        """
        # Different nullifier each time shown
        nullifier = hash(
            credential.secret,
            context,
            nonce,
            time.time() // 3600  # Hourly rotation
        )
        
        return nullifier
    
    def generate_revocation_nullifier(self, credential):
        """
        Permanent nullifier for revocation
        """
        # Same nullifier always - enables revocation
        return hash(credential.secret, "REVOKED")
    
    def show_credential(self, credential, context):
        """
        Show credential with fresh nullifier
        """
        nonce = random_bytes(32)
        nullifier = self.generate_show_nullifier(credential, context, nonce)
        
        # Check not revoked
        revocation_nullifier = self.generate_revocation_nullifier(credential)
        if revocation_nullifier in self.revoked_credentials:
            raise CredentialRevoked()
        
        # Generate proof
        proof = self.prove_credential_ownership(credential, nullifier)
        
        return nullifier, proof
```

---

## Part IX: Privacy Analysis

### Unlinkability Guarantees

```python
class UnlinkabilityAnalysis:
    def measure_unlinkability(self, nullifiers_set_1, nullifiers_set_2):
        """
        Measure unlinkability between two sets of nullifiers
        """
        # Statistical tests
        tests = {
            'chi_squared': chi2_test(nullifiers_set_1, nullifiers_set_2),
            'kolmogorov_smirnov': ks_test(nullifiers_set_1, nullifiers_set_2),
            'mutual_information': mutual_information(nullifiers_set_1, nullifiers_set_2),
            'hamming_distance': average_hamming(nullifiers_set_1, nullifiers_set_2)
        }
        
        # All tests should show independence
        unlinkable = all(
            test_result.pvalue > 0.05 
            for test_result in tests.values()
        )
        
        return unlinkable, tests
    
    def differential_privacy_analysis(self, nullifier_system):
        """
        Analyze differential privacy guarantees
        """
        # Generate nullifiers for neighboring datasets
        dataset_1 = generate_identities(1000)
        dataset_2 = dataset_1.copy()
        dataset_2[0] = generate_random_identity()  # Change one
        
        nullifiers_1 = [nullifier_system.generate(id) for id in dataset_1]
        nullifiers_2 = [nullifier_system.generate(id) for id in dataset_2]
        
        # Measure privacy loss
        epsilon = self.compute_privacy_loss(nullifiers_1, nullifiers_2)
        
        return epsilon < 1.0  # ε-differential privacy
```

### Information Leakage

```python
class LeakageAnalysis:
    def analyze_timing_leakage(self, nullifier_generation_function):
        """
        Check if timing reveals information
        """
        identities = generate_diverse_identities(100)
        timings = []
        
        for identity in identities:
            start = time.perf_counter()
            nullifier = nullifier_generation_function(identity)
            end = time.perf_counter()
            timings.append(end - start)
        
        # Check if timing correlates with identity properties
        correlation = pearson_correlation(
            [id.complexity for id in identities],
            timings
        )
        
        return abs(correlation) < 0.1  # Low correlation = good
    
    def analyze_pattern_leakage(self, nullifiers_by_user):
        """
        Check if nullifier patterns reveal identity
        """
        # Extract features from nullifier sequences
        features = []
        for user_nullifiers in nullifiers_by_user.values():
            feature = {
                'entropy': calculate_entropy(user_nullifiers),
                'periodicity': detect_periodicity(user_nullifiers),
                'clustering': measure_clustering(user_nullifiers)
            }
            features.append(feature)
        
        # Try to cluster users by features
        clusters = kmeans(features, n_clusters=len(nullifiers_by_user)//10)
        
        # Measure clustering quality (should be poor)
        silhouette = silhouette_score(features, clusters)
        
        return silhouette < 0.2  # Poor clustering = good privacy
```

---

## Part X: Implementation Recommendations

### Mnemosyne Nullifier System

```python
class MnemosyneNullifierSystem:
    def __init__(self, identity):
        self.identity = identity
        self.master_secret = identity.nullifier_master
        
        # Hierarchical derivation
        self.hierarchy = HierarchicalNullifierSystem(self.master_secret)
        
        # Context handlers
        self.contexts = {
            'voting': VotingNullifiers(),
            'messaging': MessagingNullifiers(),
            'credentials': CredentialNullifiers(),
            'transactions': TransactionNullifiers()
        }
        
        # Epoch management
        self.epoch_manager = EpochRotation()
        
        # Storage
        self.storage = NullifierStorage()
    
    def generate(self, context, action):
        """
        Generate nullifier for action in context
        """
        # Get current epoch
        epoch = self.epoch_manager.get_current_epoch()
        
        # Derive nullifier
        nullifier = self.hierarchy.generate_nullifier(context, epoch, action)
        
        # Generate proof
        proof = self.generate_proof(nullifier, context, epoch, action)
        
        return {
            'nullifier': nullifier,
            'context': context,
            'epoch': epoch,
            'proof': proof,
            'timestamp': time.time()
        }
    
    def verify(self, nullifier_data):
        """
        Verify nullifier and proof
        """
        # Check not already used
        if self.storage.check_duplicate(
            nullifier_data['nullifier'],
            nullifier_data['context'],
            nullifier_data['epoch']
        ):
            return False, "Nullifier already used"
        
        # Verify proof
        if not self.verify_proof(nullifier_data['proof']):
            return False, "Invalid proof"
        
        # Check epoch validity
        current_epoch = self.epoch_manager.get_current_epoch()
        if abs(nullifier_data['epoch'] - current_epoch) > 1:
            return False, "Invalid epoch"
        
        # Store nullifier
        self.storage.add_nullifier(
            nullifier_data['nullifier'],
            nullifier_data['context'],
            nullifier_data['epoch']
        )
        
        return True, "Valid nullifier"
```

### Configuration

```yaml
nullifier_config:
  hierarchy:
    master_derivation: "HKDF-SHA256"
    context_separation: true
    epoch_rotation: "daily"
    
  storage:
    bloom_filter_size: 10_000_000
    bloom_error_rate: 0.001
    cache_size: 100_000
    archive_after_days: 30
    
  contexts:
    voting:
      type: "deterministic"
      one_per_election: true
    messaging:
      type: "sequential"
      rotation: "per_message"
    credentials:
      type: "random"
      rotation: "hourly"
      
  privacy:
    differential_privacy_epsilon: 1.0
    unlinkability_threshold: 0.01
    
  proofs:
    system: "STARK"
    circuit: "nullifier_v1"
    recursion: false
```

---

## Security Posture and Assumptions

### Cryptographic Foundations
- **PRF-based derivation**: Using HKDF-SHA256 for key derivation
- **Post-quantum considerations**: SHA3-256 for nullifier generation (quantum-resistant hash)
- **Formal security**: Computational unlinkability under PRF indistinguishability assumption
- **NOT information-theoretic security**: Relies on computational hardness

### Failure Modes to Document
- **Clock drift**: Epoch synchronization issues
- **Retry handling**: What happens if nullifier submission fails
- **Offline issuance**: Pre-generating nullifiers for offline use
- **Registry false positives**: Bloom filter collisions causing DoS

---

## Conclusions

### Key Design Decisions

1. **Hierarchical derivation** prevents cross-context correlation
2. **Epoch rotation** provides temporal unlinkability
3. **Deterministic generation** ensures consistency
4. **Zero-knowledge proofs** validate without revealing identity
5. **Bloom filters** enable efficient duplicate detection

### Security Properties Achieved

| Property | Method | Guarantee |
|----------|--------|-----------|
| **Unlinkability** | Context separation | Statistical independence |
| **One-time use** | Duplicate detection | No double-spending |
| **Forward security** | Epoch rotation | Past nullifiers safe |
| **Privacy** | ZK proofs | Identity hidden |
| **Efficiency** | Bloom filters | O(1) checking |

### Implementation Priority

1. Basic nullifier generation with context separation
2. Epoch-based rotation system
3. Efficient storage with Bloom filters
4. ZK proof integration
5. Application-specific optimizations

The nullifier system provides the crucial privacy layer that prevents correlation while enabling one-time actions. This completes the privacy infrastructure needed for Mnemosyne's identity system.