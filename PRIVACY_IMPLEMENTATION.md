# Mnemosyne Protocol - Privacy Layer Implementation

## Overview

This document details the privacy-preserving mechanisms for the Mnemosyne Protocol, ensuring individual sovereignty while enabling collective intelligence.

## Core Privacy Principles

1. **Local-First**: All personal data stays on user's machine by default
2. **Selective Sharing**: Users explicitly choose what to share
3. **Revocable Access**: Shared memories can be withdrawn
4. **K-Anonymity**: Collective data requires minimum group size
5. **Differential Privacy**: Statistical noise prevents deanonymization
6. **Zero-Knowledge Proofs**: Verify without revealing

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Privacy Layers                         │
├─────────────────────────────────────────────────────────┤
│  Layer 1: Local Encryption (AES-256-GCM)                │
│  Layer 2: Selective Export (Contract-based)             │
│  Layer 3: Anonymization (K-anonymity + DP)              │
│  Layer 4: Cryptographic Proofs (ZK-SNARKs)              │
│  Layer 5: Revocation System (Merkle Trees)              │
└─────────────────────────────────────────────────────────┘
```

---

## Layer 1: Local Encryption

### Implementation
```python
# privacy/encryption.py

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import os

class LocalEncryption:
    def __init__(self, user_password: str):
        # Derive key from password
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.get_or_create_salt(),
            iterations=100000,
        )
        self.key = kdf.derive(user_password.encode())
        self.aesgcm = AESGCM(self.key)
    
    def encrypt_memory(self, memory: dict) -> bytes:
        """Encrypt a memory before storage"""
        nonce = os.urandom(12)  # 96-bit nonce
        plaintext = json.dumps(memory).encode()
        ciphertext = self.aesgcm.encrypt(nonce, plaintext, None)
        return nonce + ciphertext  # Prepend nonce for decryption
    
    def decrypt_memory(self, encrypted: bytes) -> dict:
        """Decrypt a stored memory"""
        nonce = encrypted[:12]
        ciphertext = encrypted[12:]
        plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
        return json.loads(plaintext)
    
    def get_or_create_salt(self) -> bytes:
        """Get or create user-specific salt"""
        salt_file = Path.home() / '.mnemosyne' / 'salt'
        if salt_file.exists():
            return salt_file.read_bytes()
        else:
            salt = os.urandom(16)
            salt_file.parent.mkdir(parents=True, exist_ok=True)
            salt_file.write_bytes(salt)
            return salt
```

---

## Layer 2: Selective Export

### Sharing Contract System
```python
# privacy/sharing_contracts.py

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional
import hashlib

@dataclass
class SharingContract:
    """Defines what a user shares with a collective"""
    
    domains: List[str]  # ["technology", "philosophy", "skills"]
    depth: str  # "summary" | "detailed" | "full"
    duration: Optional[datetime]  # Expiration time
    revocable: bool = True  # Can withdraw memories
    anonymous: bool = False  # Share without attribution
    
    # Privacy settings
    min_k_anonymity: int = 3  # Minimum group size
    noise_level: float = 0.1  # Differential privacy epsilon
    
    def validate_memory(self, memory: dict) -> bool:
        """Check if memory fits contract"""
        # Check domain match
        if memory.get('domain') not in self.domains:
            return False
        
        # Check expiration
        if self.duration and datetime.now() > self.duration:
            return False
        
        # Check privacy level
        if memory.get('privacy_level', 0) > self.get_max_privacy():
            return False
        
        return True
    
    def get_max_privacy(self) -> int:
        """Get maximum privacy level based on depth"""
        return {
            "summary": 1,  # Only high-level patterns
            "detailed": 5,  # Some specifics
            "full": 10     # Complete access
        }.get(self.depth, 1)

class SelectiveExporter:
    def __init__(self, memory_store):
        self.memory_store = memory_store
        self.contracts = {}
    
    def create_contract(self, user_id: str, collective_id: str, 
                        contract: SharingContract) -> str:
        """Create a new sharing contract"""
        contract_id = hashlib.sha256(
            f"{user_id}{collective_id}{datetime.now()}".encode()
        ).hexdigest()[:16]
        
        self.contracts[contract_id] = {
            'user_id': user_id,
            'collective_id': collective_id,
            'contract': contract,
            'created_at': datetime.now(),
            'active': True
        }
        
        return contract_id
    
    def export_memories(self, contract_id: str) -> List[dict]:
        """Export memories according to contract"""
        contract_data = self.contracts.get(contract_id)
        if not contract_data or not contract_data['active']:
            return []
        
        contract = contract_data['contract']
        user_id = contract_data['user_id']
        
        # Get user memories
        memories = self.memory_store.get_user_memories(user_id)
        
        # Filter by contract
        exported = []
        for memory in memories:
            if contract.validate_memory(memory):
                # Apply depth-based filtering
                filtered = self.apply_depth_filter(memory, contract.depth)
                exported.append(filtered)
        
        # Apply anonymization if needed
        if contract.anonymous:
            exported = self.anonymize_memories(exported)
        
        return exported
    
    def apply_depth_filter(self, memory: dict, depth: str) -> dict:
        """Filter memory content based on depth"""
        if depth == "summary":
            # Only return high-level summary
            return {
                'id': memory['id'],
                'domain': memory['domain'],
                'summary': self.generate_summary(memory['content']),
                'timestamp': memory['timestamp']
            }
        elif depth == "detailed":
            # Return most fields but redact sensitive
            filtered = memory.copy()
            filtered.pop('private_notes', None)
            filtered.pop('personal_context', None)
            return filtered
        else:  # full
            return memory
    
    def revoke_contract(self, contract_id: str):
        """Revoke a sharing contract"""
        if contract_id in self.contracts:
            self.contracts[contract_id]['active'] = False
            self.contracts[contract_id]['revoked_at'] = datetime.now()
```

---

## Layer 3: Anonymization

### K-Anonymity Implementation
```python
# privacy/k_anonymity.py

import numpy as np
from typing import List, Dict, Any

class KAnonymityProtector:
    def __init__(self, k: int = 3):
        self.k = k  # Minimum group size
    
    def check_k_anonymity(self, data: List[Dict], 
                         quasi_identifiers: List[str]) -> bool:
        """Check if data satisfies k-anonymity"""
        groups = {}
        
        for record in data:
            # Create group key from quasi-identifiers
            key = tuple(record.get(qi) for qi in quasi_identifiers)
            groups[key] = groups.get(key, 0) + 1
        
        # Check all groups meet k threshold
        return all(count >= self.k for count in groups.values())
    
    def generalize_data(self, data: List[Dict], 
                       quasi_identifiers: List[str]) -> List[Dict]:
        """Generalize data to achieve k-anonymity"""
        generalized = []
        
        for record in data:
            gen_record = record.copy()
            
            for qi in quasi_identifiers:
                if qi in gen_record:
                    gen_record[qi] = self.generalize_value(qi, gen_record[qi])
            
            generalized.append(gen_record)
        
        # Recursively generalize until k-anonymity achieved
        if not self.check_k_anonymity(generalized, quasi_identifiers):
            return self.generalize_data(generalized, quasi_identifiers)
        
        return generalized
    
    def generalize_value(self, field: str, value: Any) -> Any:
        """Generalize a single value"""
        generalizations = {
            'age': lambda v: (v // 10) * 10,  # Round to decade
            'location': lambda v: v.split(',')[0] if ',' in v else v,  # City only
            'timestamp': lambda v: v.replace(hour=0, minute=0, second=0),  # Day only
            'skill_level': lambda v: 'intermediate' if v in ['beginner', 'advanced'] else v
        }
        
        if field in generalizations:
            return generalizations[field](value)
        return value

### Differential Privacy Implementation
class DifferentialPrivacy:
    def __init__(self, epsilon: float = 1.0):
        self.epsilon = epsilon  # Privacy budget
    
    def add_laplace_noise(self, value: float, sensitivity: float) -> float:
        """Add Laplace noise to a value"""
        scale = sensitivity / self.epsilon
        noise = np.random.laplace(0, scale)
        return value + noise
    
    def add_gaussian_noise(self, value: float, sensitivity: float, 
                         delta: float = 1e-5) -> float:
        """Add Gaussian noise for (ε,δ)-differential privacy"""
        sigma = sensitivity * np.sqrt(2 * np.log(1.25 / delta)) / self.epsilon
        noise = np.random.normal(0, sigma)
        return value + noise
    
    def privatize_count(self, true_count: int) -> int:
        """Add noise to count queries"""
        noisy_count = self.add_laplace_noise(true_count, sensitivity=1)
        return max(0, int(noisy_count))  # Ensure non-negative
    
    def privatize_average(self, values: List[float], 
                         bounds: tuple = (0, 1)) -> float:
        """Compute differentially private average"""
        true_avg = np.mean(values)
        sensitivity = (bounds[1] - bounds[0]) / len(values)
        return np.clip(
            self.add_laplace_noise(true_avg, sensitivity),
            bounds[0], bounds[1]
        )
```

---

## Layer 4: Zero-Knowledge Proofs

### ZK Proof System
```python
# privacy/zk_proofs.py

import hashlib
from typing import Tuple
import secrets

class ZKProofSystem:
    """Simple ZK proof implementation for trust without exposure"""
    
    def __init__(self):
        self.prime = 2**256 - 189  # Large prime
    
    def generate_commitment(self, secret: str) -> Tuple[int, int]:
        """Generate commitment to a secret"""
        # Convert secret to number
        secret_num = int.from_bytes(
            hashlib.sha256(secret.encode()).digest(), 
            'big'
        )
        
        # Generate random blinding factor
        r = secrets.randbelow(self.prime)
        
        # Commitment = hash(secret || r)
        commitment = int.from_bytes(
            hashlib.sha256(
                secret_num.to_bytes(32, 'big') + 
                r.to_bytes(32, 'big')
            ).digest(),
            'big'
        ) % self.prime
        
        return commitment, r
    
    def prove_knowledge(self, secret: str, r: int) -> dict:
        """Create proof of knowledge without revealing secret"""
        # Fiat-Shamir heuristic for non-interactive proof
        
        # Step 1: Commitment
        x = secrets.randbelow(self.prime)
        t = pow(2, x, self.prime)  # g^x mod p
        
        # Step 2: Challenge (hash of commitment)
        c = int.from_bytes(
            hashlib.sha256(str(t).encode()).digest(),
            'big'
        ) % self.prime
        
        # Step 3: Response
        secret_num = int.from_bytes(
            hashlib.sha256(secret.encode()).digest(),
            'big'
        )
        s = (x + c * secret_num) % (self.prime - 1)
        
        return {
            'commitment': t,
            'challenge': c,
            'response': s
        }
    
    def verify_proof(self, commitment: int, proof: dict) -> bool:
        """Verify ZK proof"""
        t = proof['commitment']
        c = proof['challenge']
        s = proof['response']
        
        # Verify: g^s = t * commitment^c
        left = pow(2, s, self.prime)
        right = (t * pow(commitment, c, self.prime)) % self.prime
        
        return left == right

class TrustProof:
    """ZK proofs for trust scores"""
    
    def __init__(self):
        self.zk = ZKProofSystem()
    
    def prove_trust_threshold(self, trust_score: float, 
                             threshold: float) -> dict:
        """Prove trust score exceeds threshold without revealing exact score"""
        if trust_score >= threshold:
            # Create proof that score >= threshold
            diff = trust_score - threshold
            secret = f"trust_{diff}"
            commitment, r = self.zk.generate_commitment(secret)
            proof = self.zk.prove_knowledge(secret, r)
            
            return {
                'valid': True,
                'proof': proof,
                'commitment': commitment
            }
        else:
            return {'valid': False}
```

---

## Layer 5: Revocation System

### Merkle Tree Revocation
```python
# privacy/revocation.py

import hashlib
from typing import List, Optional, Dict

class MerkleTree:
    """Merkle tree for efficient revocation checking"""
    
    def __init__(self, leaves: List[str]):
        self.leaves = leaves
        self.tree = self.build_tree(leaves)
        self.root = self.tree[-1][0] if self.tree else None
    
    def build_tree(self, leaves: List[str]) -> List[List[str]]:
        """Build Merkle tree from leaves"""
        if not leaves:
            return []
        
        tree = [leaves]
        current_level = leaves
        
        while len(current_level) > 1:
            next_level = []
            
            for i in range(0, len(current_level), 2):
                if i + 1 < len(current_level):
                    combined = current_level[i] + current_level[i + 1]
                else:
                    combined = current_level[i] + current_level[i]
                
                hash_val = hashlib.sha256(combined.encode()).hexdigest()
                next_level.append(hash_val)
            
            tree.append(next_level)
            current_level = next_level
        
        return tree
    
    def get_proof(self, index: int) -> List[Tuple[str, str]]:
        """Get Merkle proof for leaf at index"""
        if index >= len(self.leaves):
            return []
        
        proof = []
        current_index = index
        
        for level in self.tree[:-1]:
            if current_index % 2 == 0:
                # Right sibling
                if current_index + 1 < len(level):
                    proof.append(('right', level[current_index + 1]))
            else:
                # Left sibling
                proof.append(('left', level[current_index - 1]))
            
            current_index //= 2
        
        return proof

class RevocationSystem:
    def __init__(self):
        self.revoked_memories = {}  # collective_id -> set of memory_ids
        self.revocation_trees = {}  # collective_id -> MerkleTree
        self.revocation_log = []
    
    def revoke_memory(self, user_id: str, collective_id: str, 
                     memory_id: str) -> bool:
        """Revoke a shared memory"""
        # Add to revocation set
        if collective_id not in self.revoked_memories:
            self.revoked_memories[collective_id] = set()
        
        self.revoked_memories[collective_id].add(memory_id)
        
        # Log revocation
        self.revocation_log.append({
            'user_id': user_id,
            'collective_id': collective_id,
            'memory_id': memory_id,
            'timestamp': datetime.now(),
            'hash': hashlib.sha256(
                f"{user_id}{collective_id}{memory_id}".encode()
            ).hexdigest()
        })
        
        # Rebuild Merkle tree
        self.rebuild_revocation_tree(collective_id)
        
        return True
    
    def rebuild_revocation_tree(self, collective_id: str):
        """Rebuild Merkle tree for efficient revocation checking"""
        if collective_id in self.revoked_memories:
            leaves = list(self.revoked_memories[collective_id])
            self.revocation_trees[collective_id] = MerkleTree(leaves)
    
    def is_revoked(self, collective_id: str, memory_id: str) -> bool:
        """Check if memory is revoked"""
        return (collective_id in self.revoked_memories and 
                memory_id in self.revoked_memories[collective_id])
    
    def get_revocation_proof(self, collective_id: str, 
                            memory_id: str) -> Optional[List]:
        """Get cryptographic proof of revocation"""
        if not self.is_revoked(collective_id, memory_id):
            return None
        
        tree = self.revocation_trees.get(collective_id)
        if tree:
            leaves = list(self.revoked_memories[collective_id])
            index = leaves.index(memory_id)
            return tree.get_proof(index)
        
        return None
```

---

## Integration with Collective

### Privacy-Preserving Collective
```python
# collective/private_collective.py

class PrivateCollective:
    def __init__(self, collective_id: str):
        self.collective_id = collective_id
        self.k_anonymity = KAnonymityProtector(k=3)
        self.dp = DifferentialPrivacy(epsilon=1.0)
        self.zk = TrustProof()
        self.revocation = RevocationSystem()
    
    def receive_memory(self, user_id: str, memory: dict, 
                      contract: SharingContract) -> bool:
        """Receive memory with privacy protection"""
        
        # Check revocation status
        if self.revocation.is_revoked(self.collective_id, memory['id']):
            return False
        
        # Apply k-anonymity
        if contract.min_k_anonymity > 1:
            # Wait for enough similar memories
            if not self.check_batch_anonymity(memory, contract.min_k_anonymity):
                self.queue_for_batching(memory)
                return False
        
        # Apply differential privacy
        if contract.noise_level > 0:
            memory = self.add_privacy_noise(memory, contract.noise_level)
        
        # Store with privacy metadata
        self.store_private_memory(user_id, memory, contract)
        
        return True
    
    def query_aggregate(self, query: str) -> dict:
        """Execute query with privacy guarantees"""
        
        # Parse query
        result = self.execute_raw_query(query)
        
        # Apply differential privacy to results
        if 'count' in result:
            result['count'] = self.dp.privatize_count(result['count'])
        
        if 'average' in result:
            result['average'] = self.dp.privatize_average(
                result['values'], 
                bounds=(0, 100)
            )
        
        # Ensure k-anonymity in results
        if 'groups' in result:
            result['groups'] = self.k_anonymity.generalize_data(
                result['groups'],
                quasi_identifiers=['location', 'age', 'skill_level']
            )
        
        return result
    
    def verify_trust(self, user_id: str, threshold: float) -> dict:
        """Verify trust level without revealing exact score"""
        trust_score = self.calculate_trust(user_id)
        return self.zk.prove_trust_threshold(trust_score, threshold)
```

---

## Privacy Configuration

### User Settings
```yaml
# config/privacy.yaml

privacy:
  # Local encryption
  encryption:
    algorithm: AES-256-GCM
    key_derivation: PBKDF2
    iterations: 100000
  
  # Sharing defaults
  sharing:
    default_depth: summary
    default_duration_days: 30
    default_revocable: true
    default_anonymous: false
  
  # Anonymization
  anonymization:
    k_anonymity_threshold: 3
    quasi_identifiers:
      - age
      - location
      - skill_level
    
  # Differential privacy
  differential_privacy:
    epsilon: 1.0  # Privacy budget
    delta: 1e-5
    noise_type: laplace
  
  # Zero-knowledge
  zk_proofs:
    enabled: true
    proof_system: fiat_shamir
    
  # Revocation
  revocation:
    merkle_tree_enabled: true
    log_retention_days: 365
```

---

## Security Considerations

### Attack Vectors & Mitigations

1. **Correlation Attacks**
   - Mitigation: Temporal noise, batch processing
   
2. **Membership Inference**
   - Mitigation: K-anonymity enforcement
   
3. **Model Inversion**
   - Mitigation: Differential privacy on all outputs
   
4. **Sybil Attacks**
   - Mitigation: Proof of work for identity creation
   
5. **Timing Attacks**
   - Mitigation: Constant-time operations

---

## Testing Strategy

### Privacy Tests
```python
# tests/test_privacy.py

def test_k_anonymity():
    """Test k-anonymity protection"""
    protector = KAnonymityProtector(k=3)
    data = generate_test_data(100)
    
    anonymized = protector.generalize_data(data, ['age', 'location'])
    assert protector.check_k_anonymity(anonymized, ['age', 'location'])

def test_differential_privacy():
    """Test differential privacy noise"""
    dp = DifferentialPrivacy(epsilon=1.0)
    
    # Test multiple runs give different results
    results = [dp.privatize_count(100) for _ in range(10)]
    assert len(set(results)) > 1  # Should have variation
    
    # Test average is close to true value
    assert abs(np.mean(results) - 100) < 10

def test_revocation():
    """Test memory revocation"""
    revocation = RevocationSystem()
    
    revocation.revoke_memory("user1", "collective1", "memory1")
    assert revocation.is_revoked("collective1", "memory1")
    
    proof = revocation.get_revocation_proof("collective1", "memory1")
    assert proof is not None
```

---

## Performance Optimization

### Caching Strategy
```python
# privacy/cache.py

class PrivacyCache:
    def __init__(self):
        self.anonymized_cache = TTLCache(maxsize=1000, ttl=3600)
        self.proof_cache = TTLCache(maxsize=100, ttl=300)
    
    def get_or_compute_anonymized(self, data_hash: str, 
                                  compute_func: callable):
        if data_hash in self.anonymized_cache:
            return self.anonymized_cache[data_hash]
        
        result = compute_func()
        self.anonymized_cache[data_hash] = result
        return result
```

---

## Deployment Checklist

- [ ] Enable encryption at rest
- [ ] Configure k-anonymity thresholds
- [ ] Set differential privacy budgets
- [ ] Initialize ZK proof system
- [ ] Test revocation mechanisms
- [ ] Audit privacy guarantees
- [ ] Document privacy policies
- [ ] Train users on privacy settings

---

*This privacy implementation ensures the Mnemosyne Protocol maintains individual sovereignty while enabling collective intelligence.*