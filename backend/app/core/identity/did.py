"""
W3C Decentralized Identifier (DID) Implementation
Track 1: Production-ready standards-based identity
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import base58
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from pydantic import BaseModel, Field

# DID Method: did:mnem (Mnemosyne)
DID_METHOD = "mnem"
DID_PREFIX = f"did:{DID_METHOD}"


class DIDDocument(BaseModel):
    """W3C DID Document Structure"""
    
    context: List[str] = Field(
        default=["https://www.w3.org/ns/did/v1"],
        alias="@context"
    )
    id: str = Field(..., description="The DID")
    controller: Optional[str] = Field(None, description="Controller DID")
    verification_method: List[Dict[str, Any]] = Field(
        default_factory=list,
        alias="verificationMethod"
    )
    authentication: List[str] = Field(
        default_factory=list,
        description="Authentication verification methods"
    )
    assertion_method: List[str] = Field(
        default_factory=list,
        alias="assertionMethod"
    )
    key_agreement: List[str] = Field(
        default_factory=list,
        alias="keyAgreement"
    )
    capability_invocation: List[str] = Field(
        default_factory=list,
        alias="capabilityInvocation"
    )
    capability_delegation: List[str] = Field(
        default_factory=list,
        alias="capabilityDelegation"
    )
    service: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Service endpoints"
    )
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


@dataclass
class DIDKeyPair:
    """Ed25519 key pair for DID"""
    private_key: ed25519.Ed25519PrivateKey
    public_key: ed25519.Ed25519PublicKey
    public_key_multibase: str  # Base58 encoded public key
    did: str  # Full DID identifier


class DIDManager:
    """Manages W3C DIDs for the Mnemosyne Protocol"""
    
    def __init__(self):
        self.method = DID_METHOD
        
    def generate_did(self) -> DIDKeyPair:
        """
        Generate a new DID with Ed25519 key pair
        Following W3C DID Core specification
        """
        # Generate Ed25519 key pair
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        # Get public key bytes
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        # Create multibase encoding (base58btc with 'z' prefix)
        # Add the multicodec prefix for Ed25519 public key (0xed01)
        multicodec_prefix = bytes.fromhex('ed01')
        public_key_multibase = 'z' + base58.b58encode(
            multicodec_prefix + public_key_bytes
        ).decode('ascii')
        
        # Generate DID using the public key
        did = f"{DID_PREFIX}:{public_key_multibase}"
        
        return DIDKeyPair(
            private_key=private_key,
            public_key=public_key,
            public_key_multibase=public_key_multibase,
            did=did
        )
    
    def create_did_document(
        self,
        key_pair: DIDKeyPair,
        service_endpoints: Optional[List[Dict]] = None
    ) -> DIDDocument:
        """
        Create a W3C-compliant DID Document
        """
        did = key_pair.did
        key_id = f"{did}#key-1"
        
        # Create verification method
        verification_method = {
            "id": key_id,
            "type": "Ed25519VerificationKey2020",
            "controller": did,
            "publicKeyMultibase": key_pair.public_key_multibase
        }
        
        # Create service endpoints
        services = []
        if service_endpoints:
            for idx, endpoint in enumerate(service_endpoints):
                services.append({
                    "id": f"{did}#service-{idx}",
                    "type": endpoint.get("type", "MnemosyneService"),
                    "serviceEndpoint": endpoint.get("endpoint", "")
                })
        
        # Create DID Document
        return DIDDocument(
            id=did,
            controller=did,  # Self-sovereign by default
            verification_method=[verification_method],
            authentication=[key_id],
            assertion_method=[key_id],
            key_agreement=[key_id],
            capability_invocation=[key_id],
            capability_delegation=[key_id],
            service=services
        )
    
    def resolve_did(self, did: str) -> Optional[DIDDocument]:
        """
        Resolve a DID to its DID Document
        For now, this is a local resolver - can be extended to universal resolver
        """
        # Validate DID format
        if not did.startswith(DID_PREFIX):
            raise ValueError(f"Invalid DID method. Expected {DID_PREFIX}")
        
        # Extract public key from DID
        parts = did.split(":")
        if len(parts) != 3:
            raise ValueError("Invalid DID format")
        
        public_key_multibase = parts[2]
        
        # Recreate DID Document from public key
        # In production, this would query a DID registry
        key_id = f"{did}#key-1"
        
        verification_method = {
            "id": key_id,
            "type": "Ed25519VerificationKey2020",
            "controller": did,
            "publicKeyMultibase": public_key_multibase
        }
        
        return DIDDocument(
            id=did,
            controller=did,
            verification_method=[verification_method],
            authentication=[key_id],
            assertion_method=[key_id]
        )
    
    def sign_with_did(
        self,
        key_pair: DIDKeyPair,
        message: bytes
    ) -> bytes:
        """
        Sign a message with DID's private key
        """
        return key_pair.private_key.sign(message)
    
    def verify_signature(
        self,
        did: str,
        message: bytes,
        signature: bytes
    ) -> bool:
        """
        Verify a signature using the DID's public key
        """
        # Resolve DID to get public key
        did_doc = self.resolve_did(did)
        if not did_doc or not did_doc.verification_method:
            return False
        
        # Extract public key from verification method
        vm = did_doc.verification_method[0]
        public_key_multibase = vm.get("publicKeyMultibase", "")
        
        if not public_key_multibase or not public_key_multibase.startswith('z'):
            return False
        
        # Decode the public key
        try:
            # Remove 'z' prefix and base58 decode
            key_bytes = base58.b58decode(public_key_multibase[1:])
            # Remove multicodec prefix (0xed01)
            if key_bytes[:2] != bytes.fromhex('ed01'):
                return False
            public_key_bytes = key_bytes[2:]
            
            # Create public key object
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            
            # Verify signature
            public_key.verify(signature, message)
            return True
        except Exception:
            return False
    
    def rotate_keys(
        self,
        old_did: str,
        new_key_pair: DIDKeyPair
    ) -> DIDDocument:
        """
        Rotate keys for a DID (key rotation for security)
        """
        # In production, this would update the DID registry
        # For now, create a new document with rotated keys
        old_doc = self.resolve_did(old_did)
        if not old_doc:
            raise ValueError("Cannot resolve old DID")
        
        # Create new document with same DID but new keys
        new_key_id = f"{old_did}#key-2"
        
        new_verification_method = {
            "id": new_key_id,
            "type": "Ed25519VerificationKey2020",
            "controller": old_did,
            "publicKeyMultibase": new_key_pair.public_key_multibase
        }
        
        # Keep old key in verification methods but update authentication
        old_doc.verification_method.append(new_verification_method)
        old_doc.authentication = [new_key_id]
        old_doc.assertion_method = [new_key_id]
        
        return old_doc
    
    def export_did_document(self, did_doc: DIDDocument) -> str:
        """
        Export DID Document as JSON-LD
        """
        return did_doc.json(by_alias=True, indent=2)
    
    def import_did_document(self, json_ld: str) -> DIDDocument:
        """
        Import DID Document from JSON-LD
        """
        return DIDDocument.parse_raw(json_ld)


# Service interface for dependency injection
class DIDService:
    """Service layer for DID operations"""
    
    def __init__(self):
        self.manager = DIDManager()
        # In production, add database storage for DID documents
        self._did_registry: Dict[str, DIDDocument] = {}
        self._key_pairs: Dict[str, DIDKeyPair] = {}
    
    async def create_did_for_user(
        self,
        user_id: str,
        service_endpoints: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Create a new DID for a user
        """
        # Generate key pair and DID
        key_pair = self.manager.generate_did()
        
        # Create DID Document
        did_doc = self.manager.create_did_document(key_pair, service_endpoints)
        
        # Store in registry (in production, use database)
        self._did_registry[key_pair.did] = did_doc
        self._key_pairs[key_pair.did] = key_pair
        
        # Return DID info (never expose private key directly)
        return {
            "did": key_pair.did,
            "did_document": did_doc.dict(by_alias=True),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def resolve_did(self, did: str) -> Optional[Dict[str, Any]]:
        """
        Resolve a DID to its document
        """
        # Check local registry first
        if did in self._did_registry:
            return self._did_registry[did].dict(by_alias=True)
        
        # Try to resolve using manager
        did_doc = self.manager.resolve_did(did)
        if did_doc:
            return did_doc.dict(by_alias=True)
        
        return None
    
    async def authenticate_with_did(
        self,
        did: str,
        challenge: bytes,
        signature: bytes
    ) -> bool:
        """
        Authenticate a user using DID
        """
        return self.manager.verify_signature(did, challenge, signature)