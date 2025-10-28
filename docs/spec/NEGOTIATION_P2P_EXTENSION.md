# Multi-Party Negotiation: P2P Extension
*Bridging Single-Instance Negotiation to Cross-Instance P2P*

## Overview

This document extends the existing Multi-Party Negotiation Protocol to work across separate Mnemosyne instances, enabling true P2P binding agreements without any central authority.

## Architecture Evolution

### Current State (Single Instance)
```
All parties in same database:
[Alice, Bob, Carol] → Same Negotiation Table → Binding Agreement
```

### Target State (P2P)
```
Parties across instances:
Alice@InstanceA ←→ Negotiation Protocol ←→ Bob@InstanceB
                            ↓
                    Distributed Consensus
                            ↓
                     Binding Agreement
                    (verifiable by anyone)
```

## Key Adaptations Required

### 1. Participant Identification

**Single Instance (Current)**:
```python
participant_ids = [UUID, UUID, UUID]  # Local user IDs
```

**P2P (Extended)**:
```python
participants = [
    {
        "user_id": UUID,
        "instance_id": "alice.mnemosyne.local",
        "icv_hash": "sha256_hash",
        "public_key": "ed25519_public",
        "endpoint": "https://alice.mnemosyne.local/negotiations"
    },
    {
        "user_id": UUID,
        "instance_id": "community.mnemosyne.org",
        "icv_hash": "sha256_hash",
        "public_key": "ed25519_public",
        "endpoint": "https://community.mnemosyne.org/negotiations"
    }
]
```

### 2. Negotiation Storage

**Single Instance**: One negotiation record in one database

**P2P**: Each instance maintains its own copy
```python
class DistributedNegotiation(Negotiation):
    """Extension for P2P negotiations."""

    # Additional fields for P2P
    negotiation_network_id = UUID()  # Global negotiation ID
    local_copy = Boolean(default=True)
    canonical_instance = String()  # Instance that initiated
    sync_status = Enum(["synchronized", "pending", "conflict"])
    remote_participants = JSON()  # Full participant info

    # Message synchronization
    last_sync_timestamp = DateTime()
    message_vector_clock = JSON()  # For ordering
    missing_messages = ARRAY(UUID)
```

### 3. Message Propagation

**Single Instance**: Direct database writes

**P2P**: Message broadcasting protocol
```python
async def broadcast_negotiation_message(
    message: NegotiationMessage,
    participants: List[dict]
) -> dict:
    """Broadcast negotiation message to all participants."""

    # Create P2P message wrapper
    p2p_message = {
        "protocol": "mnemosyne/negotiation/1.0",
        "negotiation_id": message.negotiation_network_id,
        "message": {
            "type": message.message_type,
            "terms": message.terms,
            "terms_version": message.terms_version,
            "sender": {
                "user_id": message.sender_id,
                "instance_id": self.instance_id,
                "icv_hash": self.user_icv_hash
            }
        },
        "vector_clock": increment_vector_clock(self.clock),
        "signature": sign_message(message, self.private_key)
    }

    # Send to each participant's instance
    results = {}
    for participant in participants:
        if participant["instance_id"] != self.instance_id:
            response = await send_to_instance(
                participant["endpoint"],
                p2p_message
            )
            results[participant["instance_id"]] = response

    return results
```

### 4. Consensus Achievement

**Single Instance**: Simple database check

**P2P**: Distributed consensus protocol
```python
class P2PConsensus:
    """Distributed consensus for P2P negotiations."""

    async def achieve_consensus(
        self,
        negotiation_id: UUID,
        local_acceptances: dict,
        remote_instances: List[str]
    ) -> bool:
        """Achieve consensus across instances."""

        # Step 1: Broadcast our acceptances
        await self.broadcast_acceptances(negotiation_id, local_acceptances)

        # Step 2: Collect acceptances from all instances
        all_acceptances = {}
        for instance in remote_instances:
            remote_acceptances = await self.request_acceptances(
                instance,
                negotiation_id
            )
            all_acceptances.update(remote_acceptances)

        # Step 3: Verify all signatures
        for user_id, acceptance in all_acceptances.items():
            if not verify_signature(
                acceptance,
                acceptance["signature"],
                self.get_user_public_key(user_id)
            ):
                return False

        # Step 4: Check if all accept same terms
        versions = [acc["terms_version"] for acc in all_acceptances.values()]
        if len(set(versions)) != 1:
            return False

        # Step 5: Create consensus proof
        consensus_proof = {
            "negotiation_id": negotiation_id,
            "terms_version": versions[0],
            "acceptances": all_acceptances,
            "timestamp": datetime.utcnow().isoformat(),
            "merkle_root": create_merkle_root(all_acceptances)
        }

        # Step 6: Broadcast consensus achievement
        await self.broadcast_consensus(consensus_proof)

        return True
```

### 5. Binding Commitment (P2P)

**Single Instance**: Local binding hash

**P2P**: Distributed binding ceremony
```python
async def create_p2p_binding(
    negotiation_id: UUID,
    consensus_proof: dict,
    participants: List[dict]
) -> dict:
    """Create binding commitment across instances."""

    # Step 1: Each party creates local finalization
    local_finalization = {
        "negotiation_id": negotiation_id,
        "user_id": self.user_id,
        "instance_id": self.instance_id,
        "consensus_proof_hash": hash(consensus_proof),
        "timestamp": datetime.utcnow().isoformat()
    }

    # Sign with user's key
    local_finalization["signature"] = sign_message(
        local_finalization,
        self.user_private_key
    )

    # Step 2: Broadcast finalization
    await self.broadcast_finalization(local_finalization)

    # Step 3: Collect all finalizations
    all_finalizations = await self.collect_finalizations(
        negotiation_id,
        participants,
        timeout=300  # 5 minutes
    )

    # Step 4: Create binding proof
    binding_proof = {
        "negotiation_id": negotiation_id,
        "consensus_proof": consensus_proof,
        "finalizations": all_finalizations,
        "binding_hash": create_binding_hash(
            consensus_proof,
            all_finalizations
        ),
        "binding_timestamp": datetime.utcnow().isoformat(),
        "merkle_tree": create_merkle_tree(all_finalizations)
    }

    # Step 5: Store locally and broadcast
    await self.store_binding(binding_proof)
    await self.broadcast_binding(binding_proof)

    return binding_proof
```

## Cross-Instance Negotiation Flow

### Complete P2P Flow

```
1. INITIATION (Alice@InstanceA)
   ├── Create negotiation locally
   ├── Generate network_negotiation_id
   ├── Invite Bob@InstanceB, Carol@InstanceC
   └── Broadcast invitation

2. JOINING (Bob@InstanceB, Carol@InstanceC)
   ├── Receive invitation
   ├── Verify Alice's identity (ICV proof)
   ├── Create local negotiation copy
   ├── Send join confirmation
   └── Sync initial state

3. NEGOTIATING (All parties)
   ├── Each offer/counter-offer:
   │   ├── Update local copy
   │   ├── Sign with user key
   │   ├── Broadcast to all instances
   │   └── Wait for acknowledgments
   └── Continue until consensus

4. CONSENSUS (Distributed)
   ├── All parties accept same terms_version
   ├── Create consensus proof (Merkle tree)
   ├── Broadcast consensus achievement
   └── Each instance verifies independently

5. BINDING (Ceremony)
   ├── Each party finalizes locally
   ├── Broadcast finalization proof
   ├── Collect all finalizations
   ├── Generate binding hash
   ├── Create Merkle tree of all proofs
   └── Store permanent record

6. VERIFICATION (Any third party)
   ├── Request binding proof from any participant
   ├── Verify all signatures
   ├── Verify Merkle tree
   ├── Verify consensus was achieved
   └── Confirm binding is valid
```

## API Extensions for P2P

### Incoming P2P Negotiation Endpoints

```python
# P2P negotiation endpoints (instance-to-instance)
POST /p2p/negotiations/invite              # Receive invitation
POST /p2p/negotiations/{id}/message        # Receive negotiation message
GET  /p2p/negotiations/{id}/acceptances    # Share acceptances
POST /p2p/negotiations/{id}/consensus      # Receive consensus proof
POST /p2p/negotiations/{id}/finalization   # Receive finalization
GET  /p2p/negotiations/{id}/binding        # Request binding proof

# Verification endpoints
POST /p2p/verify/negotiation               # Verify negotiation state
POST /p2p/verify/binding                   # Verify binding commitment
```

### Outgoing P2P Operations

```python
class P2PNegotiationClient:
    """Client for P2P negotiation operations."""

    async def invite_participant(
        self,
        participant_endpoint: str,
        negotiation: dict
    ) -> bool:
        """Invite participant from another instance."""

        invitation = {
            "negotiation_id": negotiation["network_id"],
            "title": negotiation["title"],
            "initiator": {
                "user_id": self.user_id,
                "instance_id": self.instance_id,
                "icv_hash": self.icv_hash
            },
            "initial_terms": negotiation["terms"],
            "other_participants": negotiation["participants"],
            "deadline": negotiation["deadline"]
        }

        # Sign invitation
        invitation["signature"] = sign_message(invitation, self.private_key)

        # Send to participant's instance
        response = await self.http_client.post(
            f"{participant_endpoint}/p2p/negotiations/invite",
            json=invitation
        )

        return response.status_code == 200
```

## Migration Path

### Phase 1: Parallel Implementation
- Keep single-instance negotiation working
- Add P2P negotiation as separate feature
- Use `negotiation_type` field to distinguish

### Phase 2: Unified Protocol
- Detect if all participants on same instance
- Use optimized local path if true
- Use P2P protocol if distributed

### Phase 3: Full P2P
- All negotiations use P2P protocol
- Local optimizations transparent
- Complete backwards compatibility

## Compatibility Matrix

| Scenario | Alice | Bob | Protocol Used |
|----------|-------|-----|--------------|
| Same Instance | Local User | Local User | Single Instance (optimized) |
| Different Instances | User@A | User@B | P2P Protocol |
| Mixed | User@A | User@A, User@B | P2P Protocol |
| Personal + Community | Alice@Personal | Bob@Community | P2P Protocol |

## Security Enhancements for P2P

### Additional Requirements

1. **Message Authentication**: Every P2P message must be signed
2. **Replay Protection**: Vector clocks + nonces
3. **Instance Verification**: Verify instance identity before accepting messages
4. **Sybil Resistance**: Require ICV endorsements for new participants
5. **Fork Detection**: Detect conflicting negotiation states

### P2P-Specific Attacks

| Attack | Mitigation |
|--------|-----------|
| Instance Impersonation | Verify instance certificates |
| Message Tampering | Cryptographic signatures |
| State Forking | Vector clock ordering |
| Consensus Splitting | Require majority confirmation |
| Finalization Race | Deterministic ordering |

## Implementation Priority

### Immediate (Keep Single-Instance Working)
1. Current MULTI_PARTY_NEGOTIATION.md remains valid for single-instance
2. Add instance_id fields to existing models (nullable)
3. Add signature fields (prepare for P2P)

### Near-term (P2P Foundation)
1. Implement P2P message format
2. Add cross-instance participant support
3. Build message broadcasting
4. Create consensus verification

### Medium-term (Full P2P)
1. Distributed consensus protocol
2. Binding ceremony implementation
3. Third-party verification
4. Fork detection and resolution

## Conclusion

The existing Multi-Party Negotiation Protocol remains valid for single-instance deployments. This P2P extension enables the same protocol to work across instances while maintaining backwards compatibility. The key insight is that the negotiation logic remains the same - only the message transport and consensus mechanism change.

Single-instance deployments get optimized performance, while P2P deployments get true decentralization. Both use the same fundamental trust primitive.

---

*"The same protocol, whether you're negotiating across the table or across the world."*