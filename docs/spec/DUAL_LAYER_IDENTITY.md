# Dual-Layer Identity: Instance & User Trust Architecture
*Supporting Single-User, Multi-User, and Identity Migration Scenarios*

## Overview

Mnemosyne supports flexible deployment models where instances can serve single users (personal sovereignty) or multiple users (community/organization). This specification defines the dual-layer identity system that enables trust at both instance and user levels, plus seamless identity migration between instances.

## Architecture Layers

```
┌─────────────────────────────────────┐
│         Instance Identity           │  Layer 1: Instance-to-Instance
│    (Single or Multi-User Host)      │  - Server reputation
│                                     │  - Endpoint discovery
└─────────────────────────────────────┘  - Protocol compatibility
                 ↓ contains
┌─────────────────────────────────────┐
│          User Identities            │  Layer 2: User-to-User
│     (1 to N users per instance)     │  - Personal ICVs
│                                     │  - Individual trust scores
└─────────────────────────────────────┘  - Portable identity

Migration Path: User@InstanceA → User@InstanceB (identity preserved)
```

## Deployment Scenarios

### Scenario 1: Personal Instances (1 user = 1 instance)
```
Alice's Instance          Bob's Instance
├── Alice (user)         ├── Bob (user)
└── Instance ICV ≈       └── Instance ICV ≈
    User ICV                 User ICV
```

### Scenario 2: Community Instance (N users, 1 instance)
```
Community.Mnemosyne.org
├── Alice (user) → Personal ICV
├── Bob (user) → Personal ICV
├── Carol (user) → Personal ICV
└── Instance ICV (aggregate reputation)
```

### Scenario 3: Hybrid Network
```
Personal Instance          Community Instance         Org Instance
├── David (user)          ├── Eve (user)            ├── Frank (user)
└── David's ICV           ├── Grace (user)          ├── Helen (user)
                          ├── Ian (user)             └── Org ICV
                          └── Community ICV
```

## Identity Components

### 1. Instance Identity

```python
class InstanceIdentity:
    """
    Identity of a Mnemosyne instance (server/deployment).
    """

    def __init__(self):
        # Instance-specific
        self.instance_id = uuid4()  # Unique instance identifier
        self.instance_url = ""       # Primary endpoint
        self.deployment_type = ""    # "personal", "community", "organization"

        # Cryptographic
        self.instance_keypair = None  # Ed25519 for instance operations
        self.instance_icv = None      # Optional aggregate ICV

        # Capabilities
        self.supported_protocols = []
        self.user_capacity = 1        # 1 for personal, N for multi-user
        self.federation_policy = {}   # Who can connect

        # Trust metrics
        self.instance_reputation = 0.0
        self.uptime_score = 0.0
        self.response_time_avg = 0.0

    def generate_instance_icv(self, user_icvs: List[np.array]) -> np.array:
        """
        Generate aggregate ICV for multi-user instance.

        For single-user: instance_icv ≈ user_icv
        For multi-user: instance_icv = aggregate(user_icvs)
        """
        if len(user_icvs) == 1:
            # Single user - instance inherits user ICV
            return user_icvs[0] * 0.95  # Slight modification

        else:
            # Multi-user - create aggregate
            # Use privacy-preserving aggregation
            aggregate = np.zeros(128)

            # Average public components
            for icv in user_icvs:
                aggregate[:64] += icv[:64]  # Only public/transactional parts
            aggregate[:64] /= len(user_icvs)

            # Add instance-specific noise for privacy
            aggregate[64:] = np.random.normal(0, 0.1, 64)

            return aggregate
```

### 2. User Identity

```python
class UserIdentity:
    """
    Individual user identity, portable across instances.
    """

    def __init__(self):
        # User-specific (portable)
        self.user_id = uuid4()        # Globally unique user ID
        self.user_icv = None          # Personal ICV (128-dim)
        self.user_keypair = None      # Personal Ed25519

        # Instance binding (current location)
        self.current_instance = None   # Where user currently resides
        self.instance_joined = None    # When joined current instance
        self.instance_role = "user"    # "user", "admin", "moderator"

        # Identity history (for migration)
        self.previous_instances = []   # Migration history
        self.identity_proofs = []      # Cryptographic continuity

        # Trust relationships (portable)
        self.trust_connections = {}     # User-to-user trust
        self.endorsements = []         # Portable endorsements

    def create_migration_proof(self,
                              old_instance: InstanceIdentity,
                              new_instance: InstanceIdentity) -> dict:
        """
        Create cryptographic proof of identity migration.
        """
        migration_proof = {
            "user_id": self.user_id,
            "user_icv_hash": hash(self.user_icv),
            "old_instance": {
                "id": old_instance.instance_id,
                "url": old_instance.instance_url,
                "departure_time": datetime.utcnow().isoformat()
            },
            "new_instance": {
                "id": new_instance.instance_id,
                "url": new_instance.instance_url,
                "arrival_time": datetime.utcnow().isoformat()
            },
            "continuity_proof": self.generate_continuity_proof(),
            "endorsement_transfer": self.package_endorsements()
        }

        # Sign with user's personal key
        user_signature = sign_message(migration_proof, self.user_keypair.private)
        migration_proof["user_signature"] = user_signature

        # Get old instance to co-sign (attestation)
        instance_attestation = old_instance.sign_departure(migration_proof)
        migration_proof["departure_attestation"] = instance_attestation

        return migration_proof
```

## Trust Establishment Protocols

### 1. Instance-to-Instance Trust

```python
class InstanceTrust:
    """
    Trust between Mnemosyne instances.
    """

    async def establish_instance_trust(self,
                                      my_instance: InstanceIdentity,
                                      their_instance_url: str) -> float:
        """
        Establish baseline trust between instances.
        """
        # Exchange instance cards
        their_card = await self.request_instance_card(their_instance_url)

        # Verify instance identity
        if not self.verify_instance_identity(their_card):
            return 0.0

        # Calculate instance trust based on:
        # 1. Deployment type compatibility
        type_compat = self.calculate_type_compatibility(
            my_instance.deployment_type,
            their_card["deployment_type"]
        )

        # 2. Protocol compatibility
        protocol_compat = self.calculate_protocol_compatibility(
            my_instance.supported_protocols,
            their_card["supported_protocols"]
        )

        # 3. Federation policy alignment
        policy_compat = self.check_federation_policy(
            my_instance.federation_policy,
            their_card["federation_policy"]
        )

        # 4. Network reputation (if available)
        network_rep = await self.query_network_reputation(their_card["instance_id"])

        # Weighted combination
        instance_trust = (
            type_compat * 0.2 +
            protocol_compat * 0.3 +
            policy_compat * 0.2 +
            network_rep * 0.3
        )

        return instance_trust
```

### 2. User-to-User Trust (Cross-Instance)

```python
class CrossInstanceUserTrust:
    """
    Trust between users on different instances.
    """

    async def establish_user_trust(self,
                                  alice: UserIdentity,  # on InstanceA
                                  bob_id: str,          # on InstanceB
                                  instance_b_url: str) -> dict:
        """
        Establish trust between users on different instances.
        """
        # Step 1: Verify Bob's instance
        instance_trust = await self.establish_instance_trust(
            alice.current_instance,
            instance_b_url
        )

        if instance_trust < 0.1:  # Minimum instance trust required
            return {"status": "rejected", "reason": "untrusted_instance"}

        # Step 2: Request Bob's scoped ICV through his instance
        bob_request = {
            "type": "user_icv_request",
            "requesting_user": alice.user_id,
            "requesting_instance": alice.current_instance.instance_id,
            "target_user": bob_id,
            "requested_scope": ScopedICV.HANDSHAKE,
            "purpose": "trust_establishment"
        }

        # Sign with both user and instance keys (dual authentication)
        bob_request["user_signature"] = sign_message(bob_request, alice.user_keypair.private)
        bob_request["instance_signature"] = sign_message(
            bob_request,
            alice.current_instance.instance_keypair.private
        )

        # Send request to Bob's instance
        response = await self.send_to_instance(instance_b_url, bob_request)

        # Step 3: Process Bob's response
        if response["status"] == "approved":
            bob_icv_projection = response["icv_projection"]

            # Calculate user-to-user compatibility
            compatibility = self.calculate_icv_compatibility(
                alice.user_icv,
                bob_icv_projection
            )

            # Adjust by instance trust
            effective_trust = compatibility * np.sqrt(instance_trust)

            return {
                "status": "established",
                "user_trust": effective_trust,
                "instance_trust": instance_trust,
                "combined_trust": effective_trust
            }

        return {"status": "rejected", "reason": response.get("reason")}
```

### 3. Mixed-Mode Negotiations

```python
class MixedModeNegotiation:
    """
    Negotiations between different deployment types.
    """

    async def initiate_negotiation(self,
                                  participants: List[dict]) -> dict:
        """
        Create negotiation between mixed instance types.

        Participants can be:
        - Personal instances (1 user each)
        - Community instances (multiple users)
        - Mixed
        """
        negotiation = {
            "id": uuid4(),
            "participants": [],
            "instance_participants": [],
            "trust_requirements": {}
        }

        for participant in participants:
            if participant["type"] == "user":
                # Individual user participating
                negotiation["participants"].append({
                    "user_id": participant["user_id"],
                    "instance_id": participant["instance_id"],
                    "binding_level": "user"  # User personally bound
                })

            elif participant["type"] == "instance_users":
                # Multiple users from same instance
                for user_id in participant["user_ids"]:
                    negotiation["participants"].append({
                        "user_id": user_id,
                        "instance_id": participant["instance_id"],
                        "binding_level": "user"
                    })

            elif participant["type"] == "instance":
                # Entire instance participating (all users bound)
                negotiation["instance_participants"].append({
                    "instance_id": participant["instance_id"],
                    "binding_level": "instance",  # Instance-wide binding
                    "authorized_by": participant["admin_id"]
                })

        # Set trust requirements based on participant types
        if len(negotiation["instance_participants"]) > 0:
            # Higher trust needed for instance-wide bindings
            negotiation["trust_requirements"]["minimum"] = 0.5
        else:
            # User-level only
            negotiation["trust_requirements"]["minimum"] = 0.3

        return negotiation
```

## Identity Migration

### 1. Migration Protocol

```python
class IdentityMigration:
    """
    Protocol for moving user identity between instances.
    """

    async def migrate_identity(self,
                              user: UserIdentity,
                              old_instance: InstanceIdentity,
                              new_instance_url: str) -> bool:
        """
        Migrate user identity to new instance.
        """
        # Step 1: Prepare migration package
        migration_package = {
            "user_identity": {
                "user_id": user.user_id,
                "user_icv": user.user_icv.tolist(),
                "public_key": user.user_keypair.public
            },
            "trust_relationships": user.trust_connections,
            "endorsements": user.endorsements,
            "history": user.previous_instances,
            "migration_proof": user.create_migration_proof(old_instance, None)
        }

        # Step 2: Encrypt sensitive parts
        encrypted_package = self.encrypt_migration_package(
            migration_package,
            new_instance_public_key
        )

        # Step 3: Request admission to new instance
        admission_request = {
            "type": "migration_admission",
            "encrypted_package": encrypted_package,
            "public_metadata": {
                "user_id": user.user_id,
                "coming_from": old_instance.instance_url,
                "endorsement_count": len(user.endorsements)
            }
        }

        # Step 4: Send to new instance
        response = await self.send_to_instance(new_instance_url, admission_request)

        if response["status"] == "accepted":
            # Step 5: Finalize departure from old instance
            await self.finalize_departure(user, old_instance)

            # Step 6: Activate at new instance
            await self.activate_at_new_instance(user, response["activation_token"])

            # Step 7: Notify trust network of migration
            await self.broadcast_migration(user, old_instance, new_instance_url)

            return True

        return False

    async def verify_migrated_identity(self,
                                      migration_package: dict) -> bool:
        """
        Verify a migrating user's identity continuity.
        """
        # Check cryptographic proof chain
        if not self.verify_continuity_proof(migration_package["migration_proof"]):
            return False

        # Verify endorsements are authentic
        valid_endorsements = 0
        for endorsement in migration_package["endorsements"]:
            if self.verify_endorsement(endorsement):
                valid_endorsements += 1

        # Require minimum valid endorsements
        if valid_endorsements < 2:
            return False

        # Check with previous instance (if reachable)
        if previous_instance := migration_package.get("previous_instance"):
            confirmation = await self.confirm_with_instance(
                previous_instance,
                migration_package["user_id"]
            )
            if not confirmation:
                return False

        return True
```

### 2. Identity Continuity

```python
class IdentityContinuity:
    """
    Maintain identity continuity across migrations.
    """

    def generate_continuity_proof(self,
                                 user: UserIdentity,
                                 migration_number: int) -> dict:
        """
        Generate proof of identity continuity.
        """
        # Create chain of proofs
        proof_chain = []

        # Add all previous migration proofs
        for prev_migration in user.previous_instances:
            proof_chain.append({
                "instance_id": prev_migration["instance_id"],
                "joined": prev_migration["joined"],
                "departed": prev_migration["departed"],
                "proof_hash": prev_migration["proof_hash"]
            })

        # Create current proof
        current_proof = {
            "user_id": user.user_id,
            "icv_hash": hash(user.user_icv),
            "migration_number": migration_number,
            "proof_chain": proof_chain,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Sign with user's permanent key
        signature = sign_message(current_proof, user.user_keypair.private)
        current_proof["signature"] = signature

        # Create Merkle tree of proof chain
        merkle_root = self.create_merkle_root(proof_chain + [current_proof])
        current_proof["merkle_root"] = merkle_root

        return current_proof
```

### 3. Trust Preservation

```python
class TrustPreservation:
    """
    Preserve trust relationships during migration.
    """

    async def migrate_trust_relationships(self,
                                         user: UserIdentity,
                                         new_instance: InstanceIdentity) -> dict:
        """
        Migrate user's trust relationships to new instance.
        """
        migrated = {
            "preserved": [],
            "pending": [],
            "lost": []
        }

        for connection_id, trust_data in user.trust_connections.items():
            # Notify connection of migration
            notification = {
                "type": "migration_notification",
                "user_id": user.user_id,
                "old_instance": user.current_instance.instance_id,
                "new_instance": new_instance.instance_id,
                "new_endpoint": new_instance.instance_url,
                "continuity_proof": user.create_continuity_proof()
            }

            try:
                response = await self.notify_connection(connection_id, notification)

                if response["status"] == "acknowledged":
                    # Connection updated their records
                    migrated["preserved"].append(connection_id)

                    # Update local trust record with new instance info
                    trust_data["instance"] = new_instance.instance_id

                elif response["status"] == "pending_verification":
                    # Connection wants to reverify identity
                    migrated["pending"].append(connection_id)

                else:
                    # Connection rejected or unreachable
                    migrated["lost"].append(connection_id)

            except Exception:
                migrated["lost"].append(connection_id)

        return migrated
```

## Instance Types & Trust Policies

### 1. Personal Instance Policy

```python
PERSONAL_INSTANCE_POLICY = {
    "deployment_type": "personal",
    "user_capacity": 1,
    "trust_policy": {
        "default_user_trust": 1.0,  # User fully trusts their own instance
        "instance_endorsement": "automatic",  # Instance endorses user
        "federation": "selective",  # Choose who to connect with
        "migration": "export_allowed"  # User can leave anytime
    }
}
```

### 2. Community Instance Policy

```python
COMMUNITY_INSTANCE_POLICY = {
    "deployment_type": "community",
    "user_capacity": 1000,
    "trust_policy": {
        "default_user_trust": 0.3,  # Moderate initial trust
        "instance_endorsement": "earned",  # Based on behavior
        "federation": "open",  # Connect with most instances
        "migration": "export_allowed",  # Users own their identity
        "admission": "open_registration"  # Anyone can join
    },
    "moderation": {
        "user_reporting": True,
        "trust_adjustment": "community_vote",
        "ban_policy": "3_strikes"
    }
}
```

### 3. Organization Instance Policy

```python
ORGANIZATION_INSTANCE_POLICY = {
    "deployment_type": "organization",
    "user_capacity": 100,
    "trust_policy": {
        "default_user_trust": 0.5,  # Organizational trust
        "instance_endorsement": "role_based",  # Based on org role
        "federation": "allowlist",  # Only approved instances
        "migration": "approval_required",  # Need admin approval
        "admission": "invite_only"  # Closed registration
    },
    "governance": {
        "admin_controls": True,
        "audit_logging": "comprehensive",
        "compliance": ["GDPR", "SOC2"]
    }
}
```

## API Extensions

### Instance-Aware Endpoints

```python
# Instance-level operations
GET  /instance/identity                    # Get instance identity card
POST /instance/federate                    # Request federation
GET  /instance/users                       # List users (if permitted)
POST /instance/endorse                     # Instance endorses something

# User-level operations (instance-aware)
GET  /users/{user_id}/identity            # Get user identity
POST /users/{user_id}/migrate/export      # Export for migration
POST /users/{user_id}/migrate/import      # Import migrating user
GET  /users/{user_id}/instance            # Get user's current instance

# Cross-instance user operations
POST /users/{user_id}@{instance}/trust    # Cross-instance trust
GET  /users/{user_id}@{instance}/verify   # Verify remote user

# Migration operations
POST /migration/initiate                   # Start migration process
POST /migration/accept                     # Accept incoming migration
GET  /migration/status/{migration_id}      # Check migration status
```

## Implementation Priority

### Phase 1: Dual-Layer Foundation (Q1 2025)
- [ ] Implement InstanceIdentity class
- [ ] Implement UserIdentity with instance binding
- [ ] Create instance-to-instance trust protocol
- [ ] Add user@instance notation support

### Phase 2: Migration Protocol (Q2 2025)
- [ ] Build migration package format
- [ ] Implement continuity proofs
- [ ] Create departure/arrival protocol
- [ ] Add trust relationship preservation

### Phase 3: Mixed-Mode Support (Q2 2025)
- [ ] Handle personal ↔ community negotiations
- [ ] Implement instance-wide vs user-specific binding
- [ ] Add role-based permissions
- [ ] Create instance endorsement system

### Phase 4: Advanced Features (Q3 2025)
- [ ] Multi-hop migration (A→B→C with proof chain)
- [ ] Instance reputation aggregation
- [ ] Cross-instance group formation
- [ ] Identity recovery mechanisms

## Conclusion

This dual-layer identity system enables Mnemosyne to support any deployment model while maintaining user sovereignty. Users own their identities and can move between instances freely, while instances can establish their own trust policies and federation rules.

The key innovation is treating user identity as portable and instance identity as infrastructural, allowing both personal sovereignty and community collaboration within the same protocol.

---

*"Your identity is yours, no matter where you choose to host it."*