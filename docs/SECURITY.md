# Security Architecture

## Overview

The Mnemosyne Protocol implements multiple layers of security to ensure data sovereignty, communication privacy, and collective intelligence without surveillance.

## Security Layers

### 1. Local Data Sovereignty
- **All personal data stays local** by default
- User explicitly controls what gets shared
- No automatic cloud backups or syncing
- Full data export capability at any time

### 2. End-to-End Encryption (Signal Protocol)

#### Implementation
We use the Signal Protocol for all peer-to-peer communications:
- **Double Ratchet Algorithm**: Provides forward secrecy and future secrecy
- **X3DH Key Agreement**: Asynchronous key exchange
- **Sender Keys**: Efficient group messaging

#### Message Types
```python
class SecureMessageType(Enum):
    DIRECT = "direct"          # 1-to-1 encrypted
    GROUP = "group"            # Group chat with sender keys
    BROADCAST = "broadcast"    # Public, signed but not encrypted
    MEMORY_SHARE = "memory"    # Encrypted memory fragment with contract
```

#### Security Properties
- **Forward Secrecy**: Compromised keys can't decrypt past messages
- **Future Secrecy**: Compromised keys are automatically replaced
- **Deniability**: Messages are authenticated but repudiable
- **Post-Compromise Security**: Security recovers after key compromise

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
- **Safety Numbers**: Signal Protocol's fingerprint verification
- **Cognitive Signature Matching**: Verify through symbolic patterns
- **QR Codes**: In-person verification
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
- **Signal Protocol**: Core messaging encryption
- **libsodium/NaCl**: General cryptographic operations
- **Ed25519**: Digital signatures
- **X25519**: Key exchange
- **AES-256-GCM**: Symmetric encryption
- **HMAC-SHA256**: Message authentication

#### Key Management
```python
class KeyManager:
    identity_keypair: Ed25519KeyPair      # Long-term identity
    signed_prekey: X25519KeyPair         # Medium-term (rotated)
    one_time_prekeys: List[X25519Key]    # Ephemeral keys
    
    async def rotate_keys(self):
        """Periodic key rotation for forward secrecy"""
        # Rotate signed prekey every 48 hours
        # Generate new one-time prekeys as needed
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

### 7. Agent Security

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
| Signal Protocol | ⏳ Planned | 5 |
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
- Signal Protocol integration
- E2E encrypted messaging
- Group chat encryption

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

- [Signal Protocol Specifications](https://signal.org/docs/)
- [libsodium Documentation](https://doc.libsodium.org/)
- [OWASP Security Guidelines](https://owasp.org/)

---

*Security is not a feature, it's a fundamental requirement for cognitive sovereignty.*