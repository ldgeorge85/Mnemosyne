# Multi-Party Negotiation Protocol
*Trust Without Central Authority - Core Primitive*

## Overview

This protocol enables hostile parties to reach binding agreements without central authority, blockchain consensus, or reputation systems. It's the "holy shit" demo of Mnemosyne's Trust Primitive.

## Design Principles

1. **No Central Authority** - All participants have equal power
2. **Cryptographic Proof** - Every action generates tamper-evident receipt
3. **Binding Commitments** - Agreements become irreversible once consensus reached
4. **Appeal Mechanism** - Disputes can be contested through existing appeals system
5. **Timeout Handling** - Abandoned negotiations automatically expire

## Protocol Architecture

### Message Types

```python
class NegotiationMessageType(str, enum.Enum):
    """Types of messages in a negotiation."""
    INITIATE = "initiate"          # Start negotiation with proposal
    OFFER = "offer"                # Make initial offer
    COUNTER_OFFER = "counter_offer" # Respond with modified terms
    ACCEPT = "accept"              # Accept current terms
    REJECT = "reject"              # Reject and optionally continue
    WITHDRAW = "withdraw"          # Leave negotiation entirely
    FINALIZE = "finalize"          # Confirm binding commitment
```

### State Machine

```
INITIATED
    ↓ (parties join)
NEGOTIATING
    ↓ (offers/counter-offers)
NEGOTIATING (continues until...)
    ↓ (all parties accept)
CONSENSUS_REACHED
    ↓ (all parties finalize)
BINDING

Alternative paths:
NEGOTIATING → REJECTED → TERMINATED
NEGOTIATING → WITHDRAWN → TERMINATED
NEGOTIATING → TIMEOUT → EXPIRED
BINDING → DISPUTE → APPEAL (uses existing appeals system)
```

### State Descriptions

1. **INITIATED**: Negotiation created, waiting for all parties to join
2. **NEGOTIATING**: Active offer/counter-offer exchange
3. **CONSENSUS_REACHED**: All parties have accepted same terms (provisional)
4. **BINDING**: All parties have finalized, commitment is irreversible
5. **TERMINATED**: Negotiation ended without agreement
6. **EXPIRED**: Timeout reached without consensus
7. **DISPUTED**: Party contests binding agreement (triggers appeal)

## Data Model

### Negotiation Table

```python
class NegotiationStatus(str, enum.Enum):
    """Status of negotiation."""
    INITIATED = "initiated"
    NEGOTIATING = "negotiating"
    CONSENSUS_REACHED = "consensus_reached"
    BINDING = "binding"
    TERMINATED = "terminated"
    EXPIRED = "expired"
    DISPUTED = "disputed"

class Negotiation(Base):
    """Multi-party negotiation session."""
    __tablename__ = "negotiations"

    # Identity
    id = UUID(primary_key=True, default=uuid4)
    title = String(200)
    description = Text

    # Participants (UUIDs of User IDs)
    initiator_id = UUID(ForeignKey("users.id"), nullable=False)
    participant_ids = ARRAY(UUID)  # All parties including initiator
    required_consensus_count = Integer  # How many must accept (default: all)

    # Status
    status = Enum(NegotiationStatus, default=NegotiationStatus.INITIATED)

    # Terms (evolves through negotiation)
    current_terms = JSON  # Latest proposed terms
    terms_version = Integer(default=1)  # Increments with each counter-offer

    # Consensus tracking
    acceptances = JSON  # {user_id: {terms_version, timestamp, signature}}
    finalizations = JSON  # {user_id: {timestamp, signature}}

    # Timeouts
    negotiation_deadline = DateTime  # Must reach consensus by this time
    finalization_deadline = DateTime  # Must finalize after consensus by this time

    # Binding commitment
    binding_hash = String(64)  # SHA-256 of final agreed terms
    binding_timestamp = DateTime

    # Cryptographic integrity
    content_hash = String(64)  # Hash of negotiation state
    previous_hash = String(64)  # Chain to previous negotiation (optional)

    # Metadata
    negotiation_metadata = JSON
    created_at = DateTime(default=datetime.utcnow)
    updated_at = DateTime(default=datetime.utcnow, onupdate=datetime.utcnow)
```

### NegotiationMessage Table

```python
class NegotiationMessage(Base):
    """Messages in a negotiation (offers, counter-offers, accepts, etc.)."""
    __tablename__ = "negotiation_messages"

    # Identity
    id = UUID(primary_key=True, default=uuid4)
    negotiation_id = UUID(ForeignKey("negotiations.id"), nullable=False)

    # Author
    sender_id = UUID(ForeignKey("users.id"), nullable=False)

    # Message type and content
    message_type = Enum(NegotiationMessageType, nullable=False)
    terms = JSON  # Proposed terms (for OFFER, COUNTER_OFFER)
    terms_version = Integer  # Which version this responds to
    message_text = Text  # Optional explanation

    # Cryptographic proof
    content_hash = String(64)  # Hash of this message
    signature = String(512)  # Digital signature (future: party's key)

    # Timestamps
    created_at = DateTime(default=datetime.utcnow)

    # Receipt tracking
    receipt_id = UUID(ForeignKey("receipts.id"))
```

## Negotiation Flow

### 1. Initiation Phase

```
User A creates negotiation:
  - Sets title, description
  - Specifies participant_ids: [A, B, C, ...]
  - Proposes initial terms (JSON)
  - Sets negotiation_deadline (e.g., 7 days)
  - Status: INITIATED

Receipt generated: "NEGOTIATION_INITIATED"
```

### 2. Joining Phase

```
Each participant must explicitly join:
  - POST /negotiations/{id}/join
  - Status remains INITIATED until all join
  - Once all joined: Status → NEGOTIATING

Receipt generated: "NEGOTIATION_JOINED"
```

### 3. Negotiation Phase

```
Participants exchange offers:

User B sends COUNTER_OFFER:
  - Modifies terms
  - terms_version increments
  - current_terms updated to B's proposal
  - Receipt: "NEGOTIATION_COUNTER_OFFER"

User C sends COUNTER_OFFER:
  - Further modifies terms
  - terms_version increments again
  - current_terms updated to C's proposal
  - Receipt: "NEGOTIATION_COUNTER_OFFER"

User A sends ACCEPT:
  - Accepts current_terms at terms_version=N
  - Stored in acceptances: {A: {version: N, timestamp, signature}}
  - Receipt: "NEGOTIATION_ACCEPT"

User B sends ACCEPT:
  - Accepts same terms_version=N
  - Stored in acceptances: {B: {version: N, timestamp, signature}}
  - Receipt: "NEGOTIATION_ACCEPT"

User C sends ACCEPT:
  - All parties now accept terms_version=N
  - Status: NEGOTIATING → CONSENSUS_REACHED
  - Receipt: "NEGOTIATION_CONSENSUS_REACHED"
```

### 4. Finalization Phase

```
Once consensus reached, parties must finalize:

User A sends FINALIZE:
  - Confirms binding commitment to agreed terms
  - Stored in finalizations: {A: {timestamp, signature}}
  - Receipt: "NEGOTIATION_FINALIZE"

User B sends FINALIZE:
  - Stored in finalizations
  - Receipt: "NEGOTIATION_FINALIZE"

User C sends FINALIZE:
  - All parties finalized
  - binding_hash = SHA-256(final terms + all signatures)
  - binding_timestamp = now
  - Status: CONSENSUS_REACHED → BINDING
  - Receipt: "NEGOTIATION_BINDING"

AT THIS POINT: Agreement is IRREVERSIBLE (except via appeal)
```

### 5. Post-Binding

```
Binding agreement creates:
  - Immutable record in negotiations table
  - Cryptographic proof via binding_hash
  - All receipts chained for audit trail

If party contests:
  - POST /negotiations/{id}/dispute
  - Creates Appeal linked to negotiation
  - Uses existing appeals resolution system
  - Status: BINDING → DISPUTED
```

## Timeout Handling

### Negotiation Deadline

```python
async def check_negotiation_timeouts():
    """Check for expired negotiations."""
    now = datetime.utcnow()

    # Find negotiations past deadline without consensus
    expired = await db.execute(
        select(Negotiation).where(
            and_(
                Negotiation.status.in_([
                    NegotiationStatus.INITIATED,
                    NegotiationStatus.NEGOTIATING
                ]),
                Negotiation.negotiation_deadline < now
            )
        )
    )

    for negotiation in expired.scalars():
        negotiation.status = NegotiationStatus.EXPIRED
        # Generate receipt: "NEGOTIATION_EXPIRED"
```

### Finalization Deadline

```python
async def check_finalization_timeouts():
    """Check for consensus that wasn't finalized in time."""
    now = datetime.utcnow()

    # Find consensus past finalization deadline
    expired = await db.execute(
        select(Negotiation).where(
            and_(
                Negotiation.status == NegotiationStatus.CONSENSUS_REACHED,
                Negotiation.finalization_deadline < now
            )
        )
    )

    for negotiation in expired.scalars():
        negotiation.status = NegotiationStatus.EXPIRED
        # Generate receipt: "NEGOTIATION_FINALIZATION_TIMEOUT"
```

## Consensus Detection

### Simple Consensus (All Must Accept)

```python
def check_consensus(negotiation: Negotiation) -> bool:
    """Check if all parties have accepted same terms version."""
    acceptances = negotiation.acceptances or {}

    # Need acceptance from ALL participants
    if len(acceptances) != len(negotiation.participant_ids):
        return False

    # All must accept same terms_version
    versions = [acc['version'] for acc in acceptances.values()]
    return len(set(versions)) == 1  # All same version
```

### Threshold Consensus (Configurable)

```python
def check_threshold_consensus(negotiation: Negotiation) -> bool:
    """Check if required_consensus_count parties accepted same terms."""
    acceptances = negotiation.acceptances or {}

    if len(acceptances) < negotiation.required_consensus_count:
        return False

    # Count how many accept each version
    version_counts = {}
    for acc in acceptances.values():
        version = acc['version']
        version_counts[version] = version_counts.get(version, 0) + 1

    # Check if any version has enough acceptances
    return any(count >= negotiation.required_consensus_count
               for count in version_counts.values())
```

## Escrow Mechanism (Future Enhancement)

### Concept

For negotiations involving resources (tokens, assets, permissions):

```python
class NegotiationEscrow(Base):
    """Escrow for resources locked during negotiation."""
    __tablename__ = "negotiation_escrows"

    id = UUID(primary_key=True, default=uuid4)
    negotiation_id = UUID(ForeignKey("negotiations.id"))

    # What's locked
    participant_id = UUID(ForeignKey("users.id"))
    resource_type = String(50)  # "token", "permission", "data_access", etc.
    resource_identifier = String(200)
    locked_amount = Float  # For quantifiable resources

    # Status
    locked_at = DateTime
    released_at = DateTime
    release_condition = String(20)  # "on_binding", "on_termination", "on_timeout"

    # Proof
    lock_hash = String(64)
    lock_signature = String(512)
```

## Cryptographic Proofs

### Content Hashing

Every state change generates new content_hash:

```python
def _calculate_negotiation_hash(negotiation: Negotiation) -> str:
    """Generate deterministic hash of negotiation state."""
    hashable = {
        'id': str(negotiation.id),
        'participant_ids': sorted([str(pid) for pid in negotiation.participant_ids]),
        'current_terms': negotiation.current_terms,
        'terms_version': negotiation.terms_version,
        'status': negotiation.status.value,
        'acceptances': negotiation.acceptances,
        'finalizations': negotiation.finalizations,
    }

    json_str = json.dumps(hashable, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
```

### Binding Hash

When agreement becomes binding:

```python
def _calculate_binding_hash(negotiation: Negotiation) -> str:
    """Generate irreversible binding commitment hash."""
    binding_data = {
        'negotiation_id': str(negotiation.id),
        'final_terms': negotiation.current_terms,
        'terms_version': negotiation.terms_version,
        'participant_ids': sorted([str(pid) for pid in negotiation.participant_ids]),
        'acceptances': negotiation.acceptances,
        'finalizations': negotiation.finalizations,
        'timestamp': negotiation.binding_timestamp.isoformat(),
    }

    json_str = json.dumps(binding_data, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
```

## API Endpoints

### Core Endpoints

```
POST   /negotiations                           # Create negotiation
GET    /negotiations/{id}                      # Get negotiation details
GET    /negotiations                           # List user's negotiations

POST   /negotiations/{id}/join                 # Join as participant
POST   /negotiations/{id}/offer                # Send offer/counter-offer
POST   /negotiations/{id}/accept               # Accept current terms
POST   /negotiations/{id}/reject               # Reject current terms
POST   /negotiations/{id}/withdraw             # Leave negotiation
POST   /negotiations/{id}/finalize             # Finalize binding commitment

GET    /negotiations/{id}/messages             # Get negotiation history
POST   /negotiations/{id}/dispute              # Contest binding agreement

GET    /negotiations/pending                   # Negotiations awaiting action
GET    /negotiations/binding                   # User's binding agreements
```

### Verification Endpoints

```
POST   /negotiations/{id}/verify               # Verify negotiation integrity
POST   /negotiations/{id}/verify-binding       # Verify binding commitment
GET    /negotiations/{id}/audit-trail          # Export complete audit trail
```

## Security Properties

### What This Provides

✅ **No Central Authority** - Peers negotiate directly
✅ **Tamper Evidence** - All state changes cryptographically hashed
✅ **Audit Trail** - Complete message history with receipts
✅ **Binding Commitments** - Irreversible once all parties finalize
✅ **Dispute Resolution** - Appeals system for contested agreements
✅ **Timeout Protection** - Abandoned negotiations auto-expire

### What This Does NOT Provide (Yet)

❌ **Sybil Resistance** - No reputation system (by design)
❌ **Resource Escrow** - No on-chain asset locking (future)
❌ **Non-Repudiation** - No digital signatures (coming in Phase 1.3)
❌ **Privacy** - Negotiation terms visible to all parties (by design)

## Attack Resistance

### Considered Attacks

1. **Replay Attack**: Prevented by content_hash chaining and timestamps
2. **Man-in-the-Middle**: Requires digital signatures (Phase 1.3)
3. **Denial of Service**: Mitigated by timeouts and rate limiting
4. **Griefing**: Participant can withdraw; waste of their time too
5. **False Consensus**: All parties must explicitly finalize

### Known Vulnerabilities

1. **Identity Spoofing**: Relies on existing authentication (JWT)
2. **Collusion**: Not preventable in small groups (by design)
3. **Binding Enforcement**: Depends on external enforcement mechanism

## Demo Scenario: "Hostile Parties Reach Agreement"

### Setup

```
Alice and Bob are in conflict.
- Alice claims Bob violated trust boundary
- Bob contests the claim
- Both agree to negotiate resolution
```

### Negotiation

```
1. Alice initiates negotiation:
   - Title: "Resolution of Trust Event #123"
   - Participants: [Alice, Bob]
   - Initial terms: {
       "apology": "Bob must apologize",
       "trust_restoration": "Trust score restored to 0.5",
       "monitoring": "30-day monitoring period"
     }

2. Bob joins and sends counter-offer:
   - Modified terms: {
       "apology": "Bob acknowledges misunderstanding",
       "trust_restoration": "Trust score restored to 0.7",
       "monitoring": "No monitoring"
     }

3. Alice sends counter-offer:
   - Modified terms: {
       "apology": "Bob acknowledges misunderstanding",
       "trust_restoration": "Trust score restored to 0.6",
       "monitoring": "14-day check-in"
     }

4. Bob accepts Alice's terms

5. Alice accepts (her own terms)

6. Consensus reached! Status → CONSENSUS_REACHED

7. Bob finalizes

8. Alice finalizes

9. BINDING AGREEMENT CREATED
   - No central authority involved
   - Cryptographically provable
   - Irreversible commitment
```

### "Holy Shit" Moment

Two hostile parties negotiated and committed to binding terms without:
- Central mediator
- Blockchain consensus
- Reputation system
- Escrow service
- Legal contract

**The primitive works.**

## Implementation Plan

### Phase 1: Basic Protocol (Now)
- [x] Design negotiation protocol
- [ ] Create database models
- [ ] Implement core endpoints
- [ ] Add consensus detection
- [ ] Build binding commitment

### Phase 2: Cryptographic Enhancement
- [ ] Add digital signatures (Phase 1.3)
- [ ] Implement Merkle trees for message history
- [ ] Create audit trail export

### Phase 3: Escrow Mechanism
- [ ] Design resource locking
- [ ] Implement conditional release
- [ ] Add dispute handling for locked resources

### Phase 4: Adversarial Testing
- [ ] Build simulation with hostile agents
- [ ] Test griefing scenarios
- [ ] Measure attack resistance
- [ ] Document failure modes

## References

- Trust Models: `backend/app/db/models/trust.py`
- Appeals System: `backend/app/services/appeals_service.py`
- Receipt System: `backend/app/services/receipt_service.py`
- Task Breakdown: `docs/TASK_BREAKDOWN.md` (Phase 1.4)

---

*"The most radical act is making the impossible routine."*
