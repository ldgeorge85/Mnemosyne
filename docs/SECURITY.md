# Security Architecture

## Overview

The Mnemosyne Protocol implements multiple layers of security to ensure data sovereignty, communication privacy, and collective intelligence without surveillance.

## Security Layers

### 1. Local Data Sovereignty
- **All personal data stays local** by default
- User explicitly controls what gets shared
- No automatic cloud backups or syncing
- Full data export capability at any time

### 2. End-to-End Encryption (MLS Protocol - RFC 9420)

#### Implementation
We use the Messaging Layer Security (MLS) Protocol for all secure group communications:
- **Tree-Based Key Agreement**: Logarithmic scaling for groups up to 50,000+
- **Asynchronous Operations**: Add/remove members while they're offline
- **Post-Compromise Security**: Automatic healing after key compromise
- **Forward Secrecy**: Past messages secure even if current keys compromised

#### Message Types
```python
class MLSMessageType(Enum):
    APPLICATION = "application"  # Regular encrypted group message
    PROPOSAL = "proposal"        # Group membership change proposal  
    COMMIT = "commit"           # Finalize group state change
    WELCOME = "welcome"         # Onboard new member with group state
    MEMORY_SHARE = "memory"     # Encrypted memory fragment with contract
```

#### Security Properties (MLS Guarantees)
- **Forward Secrecy**: Compromised keys can't decrypt past messages
- **Post-Compromise Security**: Automatic key rotation heals compromise
- **Asynchronous Operations**: Security maintained during offline operations
- **Scalability**: Efficient operations for groups from 2 to 50,000+ members
- **Membership Authentication**: Cryptographic proof of group membership

### 3. Trust Establishment

#### Progressive Trust Levels
```python
class TrustLevel(Enum):
    NONE = 0        # No trust established
    VERIFIED = 1    # Identity verified (safety numbers)
    TRUSTED = 2     # Ongoing positive interactions
    INNER = 3       # Inner circle, full sharing
```

#### Verification Methods
- **Credential Verification**: MLS credential binding to identity
- **Cognitive Signature Matching**: Verify through symbolic patterns
- **Key Transparency**: Optional integration with key transparency logs
- **Ritual Verification**: Shared symbolic actions

### 4. Privacy Mechanisms

#### K-Anonymity
- Minimum group size of 3 for all shared data
- Automatic aggregation before collective sharing
- No individual attribution without explicit consent

#### Selective Sharing
```python
class SharingContract:
    domains: List[str]      # What topics to share
    depth: str             # "summary" | "detailed" | "full"
    duration: int          # Days until auto-revoke
    k_anonymity: int       # Minimum group size (≥3)
    revocable: bool        # Can user revoke access
```

#### Cognitive Signatures (Not PII)
- Identity compressed to symbolic representation
- No personally identifiable information
- Plausible deniability of signature ownership

### 5. Cryptographic Primitives

#### Libraries Used
- **OpenMLS**: MIT-licensed Rust implementation of MLS (RFC 9420)
- **libsodium/NaCl**: General cryptographic operations
- **Ed25519**: Digital signatures
- **X25519**: Key exchange (used by MLS)
- **AES-256-GCM**: Symmetric encryption
- **HMAC-SHA256**: Message authentication

#### Key Management
```python
class MLSKeyManager:
    credential: MLSCredential              # Long-term identity credential
    signature_keypair: Ed25519KeyPair     # For signing
    init_keys: List[MLSKeyPackage]        # Pre-published for async adds
    
    async def publish_key_packages(self, count: int = 100):
        """Pre-publish key packages for group additions"""
        packages = []
        for _ in range(count):
            package = await self.mls.create_key_package(self.credential)
            packages.append(package)
        await self.server.upload_key_packages(packages)
    
    async def update_leaf(self, group_id: str):
        """Update leaf key for post-compromise security"""
        group = self.get_group(group_id)
        await group.update_leaf_key()
        await group.commit()
```

### 6. Network Security

#### Transport Security
- All network communication uses TLS 1.3+
- Certificate pinning for known peers
- Encrypted at rest and in transit

#### Metadata Protection
- Minimal metadata collection
- No communication pattern analysis
- Peer discovery through DHT (no central directory)

### 7. Group Security (MLS-Specific)

#### Group Management
```python
class MLSGroupSecurity:
    """Security for MLS group operations"""
    
    async def validate_proposal(self, proposal: MLSProposal):
        """Validate group change proposals"""
        # Check proposer has permission
        if not self.has_permission(proposal.sender, proposal.type):
            raise PermissionDenied()
        
        # Validate cryptographic proof
        if not await self.verify_proposal_signature(proposal):
            raise InvalidSignature()
        
        return True
    
    async def enforce_group_policy(self, group_id: str):
        """Enforce group security policies"""
        group = self.get_group(group_id)
        
        # Maximum group size
        if group.member_count > 50000:
            raise GroupTooLarge()
        
        # Require periodic key updates
        if group.last_update > datetime.now() - timedelta(days=7):
            await group.update_epoch()
```

### 8. Agent Security

#### Agent Isolation
- Each agent runs in isolated context
- Limited resource allocation per agent
- No agent can access another's memory
- Audit logging of all agent actions

#### LLM Security
- Local models preferred (Ollama)
- No training on user data
- Prompts sanitized before sending
- Response validation and filtering

## Security Principles

1. **Defense in Depth**: Multiple layers of security
2. **Least Privilege**: Components only get necessary access
3. **Zero Trust**: Verify everything, trust nothing by default
4. **Fail Secure**: System fails to a secure state
5. **Transparency**: Security measures are auditable

## Threat Model

### What We Protect Against
- **Mass Surveillance**: E2E encryption prevents bulk collection
- **Targeted Attacks**: Forward secrecy limits damage
- **Data Breaches**: Local-first means no central honeypot
- **Behavior Manipulation**: User controls their AI, not vice versa
- **Identity Theft**: Cognitive signatures aren't PII

### What We Don't Protect Against
- **Endpoint Compromise**: If device is compromised, data is accessible
- **User Mistakes**: Can't prevent voluntary oversharing
- **Legal Compulsion**: May need to comply with lawful requests
- **Quantum Computing**: Not yet quantum-resistant (planned)

## Implementation Status

| Security Feature | Status | Sprint |
|-----------------|--------|--------|
| Local Data Sovereignty | ✅ Implemented | 1 |
| Basic Encryption (AES) | ✅ Implemented | 1 |
| MLS Protocol (RFC 9420) | ⏳ Planned | 5 |
| Trust Verification | ⏳ Planned | 5 |
| K-Anonymity | ⏳ Planned | 6 |
| Sharing Contracts | ⏳ Planned | 6 |
| Network Security | ⏳ Planned | 7 |

## Security Roadmap

### Phase 1: Foundation (Current)
- Local data storage
- Basic access controls
- Database encryption

### Phase 2: Communication Security (Sprint 5)
- MLS Protocol integration via OpenMLS
- E2E encrypted group messaging
- Asynchronous member management

### Phase 3: Privacy Layer (Sprint 6)
- K-anonymity implementation
- Sharing contracts
- Cognitive signatures

### Phase 4: Advanced Security (Future)
- Zero-knowledge proofs
- Homomorphic encryption
- Quantum resistance

## Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. Email security concerns to [security contact]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work with you to understand and address the issue.

## Security Audits

The protocol will undergo security audits at these milestones:
- Before public beta launch
- After major architecture changes
- Annually thereafter

## Additional Resources

- [MLS Protocol RFC 9420](https://datatracker.ietf.org/doc/rfc9420/)
- [OpenMLS Documentation](https://openmls.tech/)
- [libsodium Documentation](https://doc.libsodium.org/)
- [OWASP Security Guidelines](https://owasp.org/)

---

*Security is not a feature, it's a fundamental requirement for cognitive sovereignty.*