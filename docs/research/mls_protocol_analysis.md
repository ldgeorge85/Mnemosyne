# MLS vs Signal vs Matrix: Deep Protocol Analysis
## Selecting the Optimal Secure Messaging Framework for Mnemosyne

---

## Executive Summary

**MLS (Messaging Layer Security) is the optimal choice for Mnemosyne** due to native group support, efficient scaling, asynchronous operation, and clean integration with zero-knowledge proofs. Signal excels at 1:1 but struggles with groups. Matrix offers federation but adds unnecessary complexity.

---

## Part I: Protocol Architectures

### MLS (RFC 9420) Architecture

```
MLS Structure:
├── TreeKEM (Key Distribution)
│   ├── Binary tree of members
│   ├── Each leaf = member
│   └── Path secrets enable updates
├── Epoch-based progression
│   ├── Commit messages advance epoch
│   └── All members synchronized
└── Application messages
    ├── Encrypted to group
    └── Authenticated sender
```

**Key Innovation**: Tree-based key agreement scales logarithmically.

### Signal Protocol Architecture

```
Signal Structure:
├── X3DH (Initial Key Exchange)
│   ├── Prekeys on server
│   └── Triple DH for forward secrecy
├── Double Ratchet
│   ├── DH ratchet (per message chain)
│   └── Symmetric ratchet (per message)
└── Sessions
    ├── Pairwise only
    └── Group = multiple pairwise
```

**Key Innovation**: Double ratchet provides fine-grained forward secrecy.

### Matrix/Megolm Architecture

```
Matrix Structure:
├── Olm (1:1 encryption)
│   ├── Modified Signal protocol
│   └── Account/session management
├── Megolm (Group encryption)
│   ├── Sender keys approach
│   └── Ratchet per sender
└── Federation layer
    ├── Homeserver routing
    └── Cross-signing trust
```

**Key Innovation**: Federation enables decentralized deployment.

---

## Part II: Detailed Comparison Matrix

### Core Properties

| Property | MLS | Signal | Matrix |
|----------|-----|--------|--------|
| **Group Size** | Scales to large groups** | 2-1,000* | 2-10,000 |
| **PCS** | ✓ Epoch-based | ✓ Per-message | ✓ Per-sender |
| **Async** | ✓ Native | ✓ With server | ✓ With server |
| **Metadata** | Minimal | Phone numbers | Room structure |
| **Setup** | None | Server prekeys | Homeserver |
| **Complexity** | O(log n) | O(n) for groups | O(n) sender keys |

*Signal groups use sender keys (deprecated) or pairwise (expensive)

### Security Properties

| Property | MLS | Signal | Matrix |
|----------|-----|--------|--------|
| **Forward Secrecy** | Per epoch | Per message | Per sender chain |
| **PCS Recovery** | Next epoch | Next ratchet | Next message |
| **Deniability** | ✗ (per-message signatures)*** | ✓ MACs | Partial |
| **Anonymity** | ✓ Possible | ✗ Phone numbers | ✗ User IDs |
| **Quantum** | Upgradeable (not PQ by default)**** | ✗ DH-based | ✗ DH-based |

### Performance Characteristics

| Operation | MLS | Signal | Matrix |
|-----------|-----|--------|--------|
| **Join Group** | O(log n) | O(n) | O(1) |
| **Leave Group** | O(log n) | O(n) | O(1) |
| **Send Message** | O(1) | O(n) or O(1)* | O(1) |
| **Key Update** | O(log n) | O(n) | O(1) |
| **State Size** | O(n) public tree + O(log n) secrets***** | O(n²) | O(n) |

*Depends on sender keys vs pairwise
**RFC 9420 does not specify a hard cap; implementations vary. Benchmarking required for specific group sizes.
***MLS uses per-message signatures by default, which breaks deniability. Application-layer solutions needed.
****MLS supports hybrid KEM for PQ upgrade path but is not post-quantum by default.
*****State size is O(n) for the public tree structure plus O(log n) for path secrets per member.

---

## Part III: MLS Deep Dive

### TreeKEM Mechanics

```python
class TreeKEM:
    """
    MLS's tree-based key agreement
    """
    def __init__(self, members):
        self.tree = self.build_tree(members)
        self.epoch = 0
    
    def build_tree(self, members):
        """
        Binary tree with members at leaves
        """
        leaves = [Leaf(member) for member in members]
        tree = complete_binary_tree(leaves)
        return tree
    
    def path_secrets(self, leaf_index):
        """
        Secrets from leaf to root
        """
        path = []
        node = self.tree.leaves[leaf_index]
        
        while node.parent:
            secret = derive_secret(node.secret, "path")
            path.append(secret)
            node = node.parent
        
        return path
    
    def update_leaf(self, leaf_index, new_secret):
        """
        Update affects log(n) nodes
        """
        affected = []
        node = self.tree.leaves[leaf_index]
        node.secret = new_secret
        
        # Update path to root
        while node.parent:
            node.parent.secret = combine_secrets(
                node.parent.left.secret,
                node.parent.right.secret
            )
            affected.append(node.parent)
            node = node.parent
        
        return affected  # O(log n) nodes
```

### Epoch Progression

```python
class MLSEpoch:
    def __init__(self):
        self.epoch = 0
        self.tree_hash = None
        self.confirmed_transcript = []
    
    def commit(self, proposals):
        """
        Advance to next epoch
        """
        # Validate proposals
        for proposal in proposals:
            if not self.validate_proposal(proposal):
                raise InvalidProposal()
        
        # Apply changes
        new_tree = self.apply_proposals(self.tree, proposals)
        
        # Derive new secrets
        commit_secret = self.derive_commit_secret()
        epoch_secret = KDF(commit_secret, "epoch", self.epoch + 1)
        
        # Update state
        self.epoch += 1
        self.tree = new_tree
        self.tree_hash = hash_tree(new_tree)
        
        # Derive keys
        keys = {
            'encryption': KDF(epoch_secret, "encryption"),
            'authentication': KDF(epoch_secret, "authentication"),
            'confirmation': KDF(epoch_secret, "confirmation")
        }
        
        return keys
```

### Integration with Zero-Knowledge Proofs

**Critical for Mnemosyne**: MLS cleanly integrates with ZK proofs.

```python
class MLSWithProofs:
    def __init__(self):
        self.mls_group = MLSGroup()
        self.proof_system = STARKSystem()
    
    def send_with_proof(self, message, proof_circuit):
        """
        Attach ZK proof to MLS message
        """
        # Generate proof about sender's identity/properties
        proof = self.proof_system.prove(
            circuit=proof_circuit,
            private_inputs=[self.identity_symbol],
            public_inputs=[self.mls_group.epoch]
        )
        
        # Create MLS application message
        mls_msg = self.mls_group.create_message(
            content_type="mnemosyne/proof",
            content={
                'message': message,
                'proof': proof,
                'circuit_id': proof_circuit.id
            }
        )
        
        return mls_msg
    
    def verify_proof_message(self, mls_msg):
        """
        Verify proof attached to message
        """
        # MLS authentication
        sender = self.mls_group.authenticate(mls_msg)
        
        # Extract and verify proof
        proof = mls_msg.content['proof']
        circuit = get_circuit(mls_msg.content['circuit_id'])
        
        valid = self.proof_system.verify(
            proof=proof,
            circuit=circuit,
            public_inputs=[self.mls_group.epoch]
        )
        
        return valid and sender
```

---

## Part IV: Signal Protocol Deep Dive

### Double Ratchet Algorithm

```python
class DoubleRatchet:
    """
    Signal's core ratcheting mechanism
    """
    def __init__(self):
        self.dh_ratchet_key = generate_keypair()
        self.root_chain = None
        self.sending_chain = None
        self.receiving_chains = {}
    
    def ratchet_encrypt(self, plaintext):
        """
        Encrypt with ratchet advancement
        """
        # Symmetric ratchet
        if not self.sending_chain:
            self.sending_chain = self.derive_chain_key()
        
        message_key = KDF(self.sending_chain.key, "message")
        self.sending_chain.key = KDF(self.sending_chain.key, "chain")
        self.sending_chain.index += 1
        
        # Encrypt
        ciphertext = encrypt(message_key, plaintext)
        
        # Include DH public key
        header = {
            'dh_public': self.dh_ratchet_key.public,
            'pn': self.sending_chain.index,
            'n': self.sending_chain.message_number
        }
        
        return header, ciphertext
```

### Signal Groups (Sender Keys)

```python
class SignalGroup:
    """
    Signal's group mechanism (deprecated but instructive)
    """
    def __init__(self, members):
        self.members = members
        self.sender_keys = {}
    
    def distribute_sender_key(self, sender):
        """
        Sender creates key for group
        """
        sender_key = generate_key()
        
        # Distribute to each member via pairwise
        for member in self.members:
            if member != sender:
                pairwise_session = get_session(sender, member)
                encrypted_key = pairwise_session.encrypt(sender_key)
                send_to(member, encrypted_key)
        
        self.sender_keys[sender] = sender_key
    
    def send_group_message(self, sender, message):
        """
        Encrypt once, send to all
        """
        sender_key = self.sender_keys[sender]
        ciphertext = encrypt(sender_key, message)
        
        # Broadcast
        for member in self.members:
            send_to(member, ciphertext)
        
        # Ratchet sender key
        self.sender_keys[sender] = KDF(sender_key, "ratchet")
```

**Problem**: O(n) key distribution, no PCS if sender compromised.

---

## Part V: Matrix/Megolm Deep Dive

### Megolm Ratchet

```python
class Megolm:
    """
    Matrix's group ratchet (per sender)
    """
    def __init__(self):
        self.ratchet = os.urandom(128)  # 4 * 32 bytes
        self.counter = 0
    
    def advance(self):
        """
        Advance ratchet (one-way)
        """
        # Split into 4 parts
        parts = [self.ratchet[i:i+32] for i in range(0, 128, 32)]
        
        # Advance based on counter bits
        if self.counter & 0x00FFFFFF == 0:
            parts[3] = sha256(parts[3])
        if self.counter & 0x0000FFFF == 0:
            parts[2] = sha256(parts[2])
        if self.counter & 0x000000FF == 0:
            parts[1] = sha256(parts[1])
        
        parts[0] = sha256(parts[0])
        
        self.ratchet = b''.join(parts)
        self.counter += 1
    
    def get_message_key(self):
        """
        Derive key for current index
        """
        return HKDF(self.ratchet, info=f"msg{self.counter}")
```

### Federation Complexity

```python
class MatrixFederation:
    """
    Matrix's homeserver federation
    """
    def __init__(self, homeserver):
        self.homeserver = homeserver
        self.rooms = {}
    
    def join_room(self, room_id):
        """
        Complex federation dance
        """
        # Find room's homeserver
        room_server = extract_server(room_id)
        
        # Request join
        join_event = self.create_join_event()
        response = federated_request(room_server, "/join", join_event)
        
        # Verify signatures
        for server in response.servers:
            if not verify_signature(server, response.signature[server]):
                raise InvalidSignature()
        
        # Sync room state
        room_state = federated_request(room_server, "/state")
        self.rooms[room_id] = room_state
        
        # Start syncing events
        self.start_sync(room_id)
```

**Complexity**: Federation adds latency, consistency issues, and attack surface.

---

## Part VI: Mnemosyne's Requirements Analysis

### Why MLS Wins for Mnemosyne

#### 1. Native Group Support
```python
# MLS: Designed for groups
mls_group = MLSGroup(members=identities)  # Efficient

# Signal: Awkward for groups
signal_group = [SignalSession(me, other) for other in members]  # O(n) sessions

# Matrix: Groups work but complex
matrix_room = Room(members)  # Plus federation overhead
```

#### 2. Proof Integration
```python
# MLS: Clean proof attachment
message = MLSMessage(
    content=data,
    extensions=[ProofExtension(proof)]
)

# Signal: Would need custom protocol
# Matrix: Would need room event types
```

#### 3. Epoch Model Aligns with Identity Evolution
```python
# MLS epochs match identity evolution cycles
def advance_epoch(mls_group, identity_evolution):
    # Both advance together
    new_epoch = mls_group.commit()
    new_identity = identity.evolve()
    
    # Natural synchronization points
    return synchronized(new_epoch, new_identity)
```

#### 4. Scalability for Collective Intelligence
```
Groups sizes:
- Small resonance groups: 5-15 members ✓ All handle
- Dunbar communities: 150 members ✓ All handle  
- Large collectives: 1000+ members:
  - MLS: ✓ Efficient O(log n)
  - Signal: ✗ O(n) overhead
  - Matrix: △ Works but complex
```

#### 5. Asynchronous by Design
```python
# MLS: Members can be offline
mls_group.commit(proposals)  # Others update when online

# Signal: Requires server mediation
# Matrix: Requires homeserver availability
```

---

## Part VII: Implementation Considerations

### MLS with Mnemosyne Extensions

```python
class MnemosyneMLS:
    """
    MLS extended for Mnemosyne's needs
    """
    def __init__(self):
        self.base_mls = MLSGroup()
        self.extensions = {
            'identity_proofs': True,
            'resonance_discovery': True,
            'evolution_sync': True,
            'collective_computation': True
        }
    
    def create_resonance_group(self, members, threshold=0.7):
        """
        Form group based on resonance
        """
        # Verify resonance threshold
        for i, m1 in enumerate(members):
            for m2 in members[i+1:]:
                if resonance(m1, m2) < threshold:
                    raise InsufficientResonance(m1, m2)
        
        # Create MLS group
        group = self.base_mls.create_group(members)
        
        # Attach resonance proof
        resonance_proof = prove_collective_resonance(members, threshold)
        group.extensions['resonance_proof'] = resonance_proof
        
        return group
    
    def progressive_trust_ceremony(self, group):
        """
        Gradual identity revelation using MLS epochs
        """
        ceremonies = [
            ('commitment', reveal_nothing),
            ('attributes', reveal_attributes),
            ('archetype', reveal_archetype),
            ('partial_symbol', reveal_partial),
            ('full_symbol', reveal_full)
        ]
        
        for stage, reveal_func in ceremonies:
            # New epoch for each stage
            group.commit(ProposalType.CEREMONY_ADVANCE)
            
            # Members reveal at this level
            for member in group.members:
                proof = reveal_func(member.identity)
                message = group.create_message(
                    content_type=f"ceremony/{stage}",
                    content=proof
                )
                group.send(message)
            
            # Verify all revealed correctly
            if not verify_ceremony_round(group, stage):
                group.remove_violators()
```

### Performance Optimizations

```python
class OptimizedMLS:
    def __init__(self):
        self.tree_cache = {}
        self.batch_size = 10
        self.use_gpu = cuda.is_available()
    
    def batch_commit(self, proposals):
        """
        Batch multiple proposals in one epoch
        """
        batches = [proposals[i:i+self.batch_size] 
                  for i in range(0, len(proposals), self.batch_size)]
        
        for batch in batches:
            if self.use_gpu:
                # Parallel tree operations on GPU
                tree_updates = cuda_tree_update(self.tree, batch)
            else:
                tree_updates = cpu_tree_update(self.tree, batch)
            
            self.commit(tree_updates)
    
    def cached_path_derivation(self, leaf_index):
        """
        Cache frequently used paths
        """
        if leaf_index in self.tree_cache:
            return self.tree_cache[leaf_index]
        
        path = compute_path(self.tree, leaf_index)
        self.tree_cache[leaf_index] = path
        
        return path
```

---

## Part VIII: Security Analysis

### Formal Security Comparison

#### MLS Security Theorem
```
If TreeKEM is secure and signatures are unforgeable, then MLS provides:
- Confidentiality against adaptive adversaries
- Authentication of group members
- Forward secrecy and PCS within one epoch
```

#### Signal Security Theorem
```
If DH is hard and PRFs are secure, Signal provides:
- Confidentiality against adaptive adversaries  
- Authentication via MACs
- Forward secrecy and PCS per message
```

#### Matrix Security Theorem
```
If Megolm ratchet is one-way and federation is honest, Matrix provides:
- Confidentiality per sender chain
- Authentication via signatures
- Forward secrecy per sender
```

### Attack Resistance

| Attack | MLS | Signal | Matrix |
|--------|-----|--------|--------|
| **MITM** | ✓ TreeKEM | ✓ X3DH | △ Trust-on-first-use |
| **Replay** | ✓ Epoch counter | ✓ Ratchet state | ✓ Message indices |
| **Metadata** | ✓ Minimal | ✗ Phone numbers | ✗ Room structure |
| **Sybil** | △ App-level | △ App-level | △ App-level |
| **DOS** | ✓ Efficient | △ O(n) groups | △ Federation |

---

## Part IX: Migration and Compatibility

### Gradual Migration Strategy

```python
class ProtocolBridge:
    """
    Bridge between protocols during migration
    """
    def __init__(self):
        self.mls_groups = {}
        self.signal_sessions = {}
        self.matrix_rooms = {}
    
    def unified_send(self, recipient, message):
        """
        Send via appropriate protocol
        """
        if recipient in self.mls_groups:
            return self.send_mls(recipient, message)
        elif recipient in self.signal_sessions:
            return self.send_signal(recipient, message)
        elif recipient in self.matrix_rooms:
            return self.send_matrix(recipient, message)
        else:
            # Establish MLS by default
            return self.establish_mls(recipient, message)
    
    def protocol_upgrade(self, old_session, new_protocol='mls'):
        """
        Upgrade existing session to MLS
        """
        if new_protocol == 'mls':
            # Extract members
            members = self.get_session_members(old_session)
            
            # Create MLS group
            mls_group = MLSGroup(members)
            
            # Notify members of upgrade
            upgrade_message = create_upgrade_notification(old_session, mls_group)
            self.broadcast(members, upgrade_message)
            
            # Deprecate old session
            self.deprecate_session(old_session)
            
            return mls_group
```

---

## Part X: Recommendations

### Primary Recommendation: MLS

**Use MLS as the primary protocol for Mnemosyne** because:

1. **Designed for groups** - Core Mnemosyne use case
2. **Efficient scaling** - O(log n) operations
3. **Clean abstractions** - Epochs align with identity evolution
4. **Proof integration** - Natural extension point
5. **Future-proof** - IETF standard, quantum-ready

### Implementation Approach

```python
class MnemosyneMessaging:
    def __init__(self):
        # Primary: MLS for groups
        self.mls = MLSImplementation()
        
        # Fallback: Signal for 1:1 when needed
        self.signal = SignalImplementation()
        
        # Never: Matrix adds unnecessary complexity
        
    def create_group(self, members):
        if len(members) == 2:
            # Optional: Use Signal for pure 1:1
            return self.signal.create_session(members)
        else:
            # Use MLS for all groups
            return self.mls.create_group(members)
```

### Specific MLS Configuration

```yaml
mls_config:
  version: "1.0"  # RFC 9420
  ciphersuite: 
    aead: "AES-256-GCM"
    hash: "SHA-384"
    signature: "Ed25519"  # Or SPHINCS+ for PQ
  extensions:
    - identity_proofs
    - resonance_validation
    - evolution_sync
  tree_configuration:
    max_depth: 32  # Support up to 2^32 members
    leaf_lifetime: 30_days
    cache_paths: true
  epoch_configuration:
    max_epoch_size: 1000  # Proposals per epoch
    commit_delay: 100ms  # Batching window
```

---

## Conclusions

### The Clear Winner: MLS

After deep analysis, **MLS is unequivocally the best choice** for Mnemosyne:

| Criterion | MLS | Signal | Matrix |
|-----------|-----|--------|--------|
| **Groups** | ✓✓✓ Native | ✗ Awkward | ✓ Complex |
| **Scale** | ✓✓✓ O(log n) | ✗ O(n) | ✓ O(n) |
| **Proofs** | ✓✓✓ Clean | △ Custom | △ Custom |
| **Complexity** | ✓✓ Moderate | ✓✓✓ Simple | ✗ High |
| **Standards** | ✓✓✓ IETF | ✓✓ De facto | ✓ Matrix.org |

### Key Insights

1. **MLS's epoch model naturally aligns with identity evolution cycles**
2. **TreeKEM efficiency enables large collective intelligence groups**
3. **Extension mechanism allows clean proof integration**
4. **Asynchronous operation supports global, distributed communities**
5. **IETF standardization ensures long-term support**

### Implementation Priority

1. Implement core MLS with basic TreeKEM
2. Add proof extensions for identity validation
3. Integrate with resonance-based group formation
4. Optimize for Mnemosyne's specific patterns
5. Consider Signal fallback for pure 1:1 (optional)

The protocol layer is solved. MLS provides the secure, scalable, proof-friendly foundation Mnemosyne needs.