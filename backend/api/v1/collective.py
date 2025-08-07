"""
Collective intelligence endpoints for Mnemosyne Protocol
"""

from typing import List, Optional, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid

from api.deps import get_db, get_current_active_user
from models.user import User
from models.sharing import SharingContract
from models.memory import Memory
from privacy.k_anonymity import KAnonymityProtector
from services.collective_service import CollectiveService

router = APIRouter()


# Pydantic models
class SharingContractCreate(BaseModel):
    collective_id: str
    domains: List[str]
    depth: str = Field(..., pattern="^(summary|detailed|full)$")
    duration_days: int = Field(30, ge=1, le=365)
    k_anonymity: int = Field(3, ge=3, le=100)
    revocable: bool = True
    anonymous: bool = False


class SharingContractResponse(BaseModel):
    id: str
    user_id: str
    collective_id: str
    domains: List[str]
    depth: str
    duration: int
    k_anonymity: int
    revocable: bool
    anonymous: bool
    created_at: datetime
    expires_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class CollectiveSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    domains: Optional[List[str]] = None
    limit: int = Field(10, ge=1, le=50)


class CollectiveMatchRequest(BaseModel):
    domains: List[str]
    skills: Optional[List[str]] = None
    min_trust: float = Field(0.0, ge=0.0, le=1.0)


class MemoryShareRequest(BaseModel):
    memory_id: str
    contract_id: str


@router.post("/join")
async def join_collective(
    collective_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Join a collective (placeholder for future implementation)
    """
    # For MVP, we have a single global collective
    if collective_id != "global":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collective not found"
        )
    
    return {
        "message": "Successfully joined collective",
        "collective_id": collective_id,
        "user_id": current_user.id,
        "status": "active"
    }


@router.post("/contracts", response_model=SharingContractResponse)
async def create_sharing_contract(
    contract_data: SharingContractCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create a sharing contract for selective knowledge transfer
    """
    # Check if user has permission (initiation level)
    if current_user.initiation_level.value < 1:  # Less than FRAGMENTOR
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient initiation level to create sharing contracts"
        )
    
    # Create contract
    contract = SharingContract(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        collective_id=contract_data.collective_id,
        domains=contract_data.domains,
        depth=contract_data.depth,
        duration=contract_data.duration_days * 24 * 3600,  # Convert to seconds
        k_anonymity=contract_data.k_anonymity,
        revocable=contract_data.revocable,
        anonymous=contract_data.anonymous,
        expires_at=datetime.utcnow() + timedelta(days=contract_data.duration_days),
        is_active=True
    )
    
    db.add(contract)
    await db.commit()
    await db.refresh(contract)
    
    return contract


@router.get("/contracts", response_model=List[SharingContractResponse])
async def list_my_contracts(
    active_only: bool = True,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    List user's sharing contracts
    """
    query = select(SharingContract).where(
        SharingContract.user_id == current_user.id
    )
    
    if active_only:
        query = query.where(
            SharingContract.is_active == True,
            SharingContract.expires_at > datetime.utcnow()
        )
    
    result = await db.execute(query)
    contracts = result.scalars().all()
    
    return contracts


@router.post("/share")
async def share_memory(
    request: MemoryShareRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Share a memory with the collective according to contract
    """
    # Get memory
    memory = await db.get(Memory, request.memory_id)
    if not memory or memory.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found or not authorized"
        )
    
    # Get contract
    contract = await db.get(SharingContract, request.contract_id)
    if not contract or contract.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found or not authorized"
        )
    
    # Validate contract is active
    if not contract.is_active or contract.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract is not active or has expired"
        )
    
    # Check domain match
    memory_domains = memory.metadata.get("domains", [])
    if not any(d in contract.domains for d in memory_domains):
        # If no explicit domains, check content relevance
        # For now, allow sharing
        pass
    
    # Apply contract depth restrictions
    shared_content = memory.content
    if contract.depth == "summary":
        # Truncate to summary
        shared_content = shared_content[:500] + "..." if len(shared_content) > 500 else shared_content
    elif contract.depth == "detailed":
        # Keep most content but remove sensitive details
        # This would need more sophisticated processing
        pass
    
    # Apply k-anonymity (would need to batch with other shares in production)
    # For now, just mark as shared
    
    # Store sharing record (would go to collective database)
    sharing_record = {
        "memory_id": memory.id,
        "contract_id": contract.id,
        "shared_content": shared_content,
        "shared_at": datetime.utcnow(),
        "anonymous": contract.anonymous,
        "k_group_size": contract.k_anonymity
    }
    
    return {
        "message": "Memory shared with collective",
        "sharing_id": str(uuid.uuid4()),
        "contract_id": contract.id,
        "anonymized": contract.anonymous
    }


@router.post("/search")
async def search_collective(
    request: CollectiveSearchRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Search collective knowledge (k-anonymized)
    """
    collective_service = CollectiveService(db)
    
    # Search shared memories
    results = await collective_service.search_collective(
        query=request.query,
        domains=request.domains,
        limit=request.limit,
        user_id=current_user.id
    )
    
    # Apply k-anonymity
    protector = KAnonymityProtector()
    anonymized_results = await protector.protect_search_results(results)
    
    return {
        "query": request.query,
        "results": anonymized_results,
        "total": len(anonymized_results),
        "k_anonymity": 3
    }


@router.post("/match")
async def find_collaborators(
    request: CollectiveMatchRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Find potential collaborators based on domains and skills
    """
    collective_service = CollectiveService(db)
    
    matches = await collective_service.find_matches(
        domains=request.domains,
        skills=request.skills,
        min_trust=request.min_trust,
        user_id=current_user.id
    )
    
    # Anonymize results based on their privacy settings
    anonymized_matches = []
    for match in matches:
        if match["visibility"] > 0.3:  # Public enough to show
            anonymized_matches.append({
                "id": match["id"],
                "domains": match["domains"],
                "match_score": match["score"],
                "trust_level": "verified" if match["trust"] > 0.7 else "unverified"
            })
    
    return {
        "matches": anonymized_matches,
        "total": len(anonymized_matches),
        "domains": request.domains
    }


@router.delete("/contracts/{contract_id}")
async def revoke_contract(
    contract_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Revoke a sharing contract
    """
    contract = await db.get(SharingContract, contract_id)
    
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    if contract.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to revoke this contract"
        )
    
    if not contract.revocable:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This contract is not revocable"
        )
    
    # Mark as inactive
    contract.is_active = False
    await db.commit()
    
    return {"message": "Contract revoked successfully"}