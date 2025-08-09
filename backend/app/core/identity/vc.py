"""
W3C Verifiable Credentials Implementation
Track 1: Production-ready standards-based credentials
"""

import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator
import jwt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ed25519

from .did import DIDManager, DIDKeyPair


class VerifiableCredential(BaseModel):
    """W3C Verifiable Credential Data Model"""
    
    context: List[str] = Field(
        default=[
            "https://www.w3.org/2018/credentials/v1"
        ],
        alias="@context"
    )
    id: str = Field(default_factory=lambda: f"urn:uuid:{uuid.uuid4()}")
    type: List[str] = Field(
        default=["VerifiableCredential"],
        description="Credential types"
    )
    issuer: Union[str, Dict[str, Any]] = Field(
        ...,
        description="DID or object describing the issuer"
    )
    issuance_date: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        alias="issuanceDate"
    )
    expiration_date: Optional[str] = Field(
        None,
        alias="expirationDate"
    )
    credential_subject: Union[Dict[str, Any], List[Dict[str, Any]]] = Field(
        ...,
        alias="credentialSubject"
    )
    credential_status: Optional[Dict[str, Any]] = Field(
        None,
        alias="credentialStatus"
    )
    proof: Optional[Dict[str, Any]] = Field(
        None,
        description="Cryptographic proof"
    )
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @validator('expiration_date')
    def validate_expiration(cls, v, values):
        if v and 'issuance_date' in values:
            issuance = datetime.fromisoformat(values['issuance_date'].replace('Z', '+00:00'))
            expiration = datetime.fromisoformat(v.replace('Z', '+00:00'))
            if expiration <= issuance:
                raise ValueError("Expiration date must be after issuance date")
        return v


class VerifiablePresentation(BaseModel):
    """W3C Verifiable Presentation Data Model"""
    
    context: List[str] = Field(
        default=["https://www.w3.org/2018/credentials/v1"],
        alias="@context"
    )
    id: str = Field(default_factory=lambda: f"urn:uuid:{uuid.uuid4()}")
    type: List[str] = Field(default=["VerifiablePresentation"])
    verifiable_credential: List[VerifiableCredential] = Field(
        ...,
        alias="verifiableCredential"
    )
    holder: str = Field(..., description="DID of the holder")
    proof: Optional[Dict[str, Any]] = Field(None)
    
    class Config:
        populate_by_name = True


class CredentialManager:
    """Manages W3C Verifiable Credentials"""
    
    def __init__(self, did_manager: DIDManager):
        self.did_manager = did_manager
    
    def issue_credential(
        self,
        issuer_key_pair: DIDKeyPair,
        credential_subject: Dict[str, Any],
        credential_type: List[str] = None,
        expiration_days: Optional[int] = None
    ) -> VerifiableCredential:
        """
        Issue a new Verifiable Credential
        """
        # Set credential types
        types = ["VerifiableCredential"]
        if credential_type:
            types.extend(credential_type)
        
        # Calculate expiration
        expiration_date = None
        if expiration_days:
            expiration = datetime.now(timezone.utc) + timedelta(days=expiration_days)
            expiration_date = expiration.isoformat()
        
        # Create credential
        credential = VerifiableCredential(
            type=types,
            issuer=issuer_key_pair.did,
            credential_subject=credential_subject,
            expiration_date=expiration_date
        )
        
        # Add proof
        proof = self._create_proof(issuer_key_pair, credential)
        credential.proof = proof
        
        return credential
    
    def _create_proof(
        self,
        key_pair: DIDKeyPair,
        credential: VerifiableCredential
    ) -> Dict[str, Any]:
        """
        Create a cryptographic proof for the credential
        Using Ed25519Signature2020
        """
        # Remove existing proof for signing
        credential_dict = credential.dict(by_alias=True, exclude={'proof'})
        
        # Canonical JSON for consistent hashing
        canonical_json = json.dumps(credential_dict, sort_keys=True, separators=(',', ':'))
        message = canonical_json.encode('utf-8')
        
        # Sign with DID
        signature = self.did_manager.sign_with_did(key_pair, message)
        
        # Create proof object
        proof = {
            "type": "Ed25519Signature2020",
            "created": datetime.now(timezone.utc).isoformat(),
            "verificationMethod": f"{key_pair.did}#key-1",
            "proofPurpose": "assertionMethod",
            "proofValue": signature.hex()
        }
        
        return proof
    
    def verify_credential(
        self,
        credential: Union[VerifiableCredential, Dict[str, Any]]
    ) -> bool:
        """
        Verify a Verifiable Credential
        """
        # Parse credential if dict
        if isinstance(credential, dict):
            credential = VerifiableCredential(**credential)
        
        # Check expiration
        if credential.expiration_date:
            expiration = datetime.fromisoformat(
                credential.expiration_date.replace('Z', '+00:00')
            )
            if expiration < datetime.now(timezone.utc):
                return False
        
        # Verify proof
        if not credential.proof:
            return False
        
        # Extract proof and remove from credential
        proof = credential.proof
        credential_dict = credential.dict(by_alias=True, exclude={'proof'})
        
        # Recreate canonical JSON
        canonical_json = json.dumps(credential_dict, sort_keys=True, separators=(',', ':'))
        message = canonical_json.encode('utf-8')
        
        # Get issuer DID
        issuer_did = credential.issuer
        if isinstance(issuer_did, dict):
            issuer_did = issuer_did.get('id', '')
        
        # Verify signature
        signature = bytes.fromhex(proof.get('proofValue', ''))
        return self.did_manager.verify_signature(issuer_did, message, signature)
    
    def create_presentation(
        self,
        holder_key_pair: DIDKeyPair,
        credentials: List[VerifiableCredential],
        challenge: Optional[str] = None
    ) -> VerifiablePresentation:
        """
        Create a Verifiable Presentation
        """
        presentation = VerifiablePresentation(
            holder=holder_key_pair.did,
            verifiable_credential=credentials
        )
        
        # Add proof with challenge (for authentication)
        proof = self._create_presentation_proof(
            holder_key_pair,
            presentation,
            challenge
        )
        presentation.proof = proof
        
        return presentation
    
    def _create_presentation_proof(
        self,
        key_pair: DIDKeyPair,
        presentation: VerifiablePresentation,
        challenge: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create proof for presentation
        """
        # Remove existing proof for signing
        presentation_dict = presentation.dict(by_alias=True, exclude={'proof'})
        
        # Add challenge if provided
        if challenge:
            presentation_dict['challenge'] = challenge
        
        # Canonical JSON
        canonical_json = json.dumps(presentation_dict, sort_keys=True, separators=(',', ':'))
        message = canonical_json.encode('utf-8')
        
        # Sign
        signature = self.did_manager.sign_with_did(key_pair, message)
        
        # Create proof
        proof = {
            "type": "Ed25519Signature2020",
            "created": datetime.now(timezone.utc).isoformat(),
            "verificationMethod": f"{key_pair.did}#key-1",
            "proofPurpose": "authentication",
            "proofValue": signature.hex()
        }
        
        if challenge:
            proof["challenge"] = challenge
        
        return proof
    
    def verify_presentation(
        self,
        presentation: Union[VerifiablePresentation, Dict[str, Any]],
        expected_challenge: Optional[str] = None
    ) -> bool:
        """
        Verify a Verifiable Presentation and its credentials
        """
        # Parse presentation if dict
        if isinstance(presentation, dict):
            presentation = VerifiablePresentation(**presentation)
        
        # Verify presentation proof
        if not presentation.proof:
            return False
        
        # Check challenge if expected
        if expected_challenge:
            if presentation.proof.get('challenge') != expected_challenge:
                return False
        
        # Verify each credential
        for credential in presentation.verifiable_credential:
            if not self.verify_credential(credential):
                return False
        
        # Verify presentation signature
        proof = presentation.proof
        presentation_dict = presentation.dict(by_alias=True, exclude={'proof'})
        
        if expected_challenge:
            presentation_dict['challenge'] = expected_challenge
        
        canonical_json = json.dumps(presentation_dict, sort_keys=True, separators=(',', ':'))
        message = canonical_json.encode('utf-8')
        
        signature = bytes.fromhex(proof.get('proofValue', ''))
        return self.did_manager.verify_signature(
            presentation.holder,
            message,
            signature
        )


# Credential templates for Mnemosyne Protocol
class MnemosyneCredentials:
    """Pre-defined credential types for the protocol"""
    
    @staticmethod
    def create_memory_access_credential(
        issuer: DIDKeyPair,
        subject_did: str,
        access_level: str,
        domains: List[str]
    ) -> Dict[str, Any]:
        """
        Create a credential for memory access permissions
        """
        return {
            "id": subject_did,
            "memoryAccess": {
                "level": access_level,  # "read", "write", "admin"
                "domains": domains,
                "grantedAt": datetime.now(timezone.utc).isoformat()
            }
        }
    
    @staticmethod
    def create_trust_credential(
        issuer: DIDKeyPair,
        subject_did: str,
        trust_score: float,
        verification_method: str
    ) -> Dict[str, Any]:
        """
        Create a trust attestation credential
        """
        return {
            "id": subject_did,
            "trustAttestation": {
                "score": trust_score,
                "verificationMethod": verification_method,
                "attestedAt": datetime.now(timezone.utc).isoformat()
            }
        }
    
    @staticmethod
    def create_collective_membership_credential(
        issuer: DIDKeyPair,
        subject_did: str,
        collective_id: str,
        role: str
    ) -> Dict[str, Any]:
        """
        Create a collective membership credential
        """
        return {
            "id": subject_did,
            "collectiveMembership": {
                "collectiveId": collective_id,
                "role": role,  # "member", "moderator", "admin"
                "joinedAt": datetime.now(timezone.utc).isoformat()
            }
        }


# Service layer for dependency injection
class CredentialService:
    """Service layer for Verifiable Credentials"""
    
    def __init__(self, did_manager: DIDManager):
        self.manager = CredentialManager(did_manager)
        self.templates = MnemosyneCredentials()
        # In production, add database storage
        self._credential_store: Dict[str, VerifiableCredential] = {}
    
    async def issue_credential(
        self,
        issuer_did: str,
        subject: Dict[str, Any],
        credential_type: List[str],
        expiration_days: Optional[int] = 365
    ) -> Dict[str, Any]:
        """
        Issue a new credential
        """
        # Get issuer key pair (in production, from secure storage)
        # For now, this is a placeholder
        issuer_key_pair = None  # Would be retrieved from secure storage
        
        if not issuer_key_pair:
            raise ValueError("Issuer key pair not found")
        
        # Issue credential
        credential = self.manager.issue_credential(
            issuer_key_pair,
            subject,
            credential_type,
            expiration_days
        )
        
        # Store credential
        self._credential_store[credential.id] = credential
        
        return credential.dict(by_alias=True)
    
    async def verify_credential(
        self,
        credential: Dict[str, Any]
    ) -> bool:
        """
        Verify a credential
        """
        return self.manager.verify_credential(credential)
    
    async def create_presentation(
        self,
        holder_did: str,
        credential_ids: List[str],
        challenge: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a verifiable presentation
        """
        # Get holder key pair (in production, from secure storage)
        holder_key_pair = None  # Would be retrieved from secure storage
        
        if not holder_key_pair:
            raise ValueError("Holder key pair not found")
        
        # Get credentials
        credentials = []
        for cred_id in credential_ids:
            if cred_id in self._credential_store:
                credentials.append(self._credential_store[cred_id])
        
        # Create presentation
        presentation = self.manager.create_presentation(
            holder_key_pair,
            credentials,
            challenge
        )
        
        return presentation.dict(by_alias=True)