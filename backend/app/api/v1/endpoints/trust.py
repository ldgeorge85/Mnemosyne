"""
Trust System API Endpoints

Handles trust events, appeals, and trust relationships with
sovereignty safeguards and neutral language.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.api.dependencies.db import get_async_db
from app.core.auth.manager import get_current_user
from app.core.auth.base import AuthUser
from app.db.models.trust import (
    TrustEvent, 
    Appeal, 
    TrustRelationship,
    ConsciousnessMap,
    TrustLevel,
    TrustEventType,
    AppealStatus
)
from app.db.models.receipt import ReceiptType
from app.services.receipt_service import ReceiptService
from app.schemas.trust import (
    TrustEventCreate,
    TrustEventResponse,
    AppealCreate,
    AppealResponse,
    TrustRelationshipResponse,
    TrustProgressionRequest,
    ConsciousnessPatternResponse
)

router = APIRouter(prefix="/trust", tags=["trust"])


@router.post("/event", response_model=TrustEventResponse, status_code=status.HTTP_201_CREATED)
async def record_trust_event(
    event_data: TrustEventCreate,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> TrustEventResponse:
    """
    Record a trust-affecting event between users.
    
    Uses neutral language (not "violations") and ensures
    sovereignty preservation through consent and visibility controls.
    """
    # Verify user is involved in the event
    if (str(current_user.user_id) != str(event_data.actor_id) and 
        str(current_user.user_id) != str(event_data.subject_id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only record trust events you're involved in"
        )
    
    # Create trust event with neutral language
    trust_event = TrustEvent(
        actor_id=event_data.actor_id,
        subject_id=event_data.subject_id,
        event_type=event_data.event_type,
        trust_delta=event_data.trust_delta,
        context=event_data.context,
        reporter_id=current_user.user_id,
        visibility_scope=event_data.visibility_scope or "private",
        user_consent=event_data.user_consent or False,
        policy_version="v1"
    )
    
    db.add(trust_event)
    await db.commit()
    await db.refresh(trust_event)
    
    # Create receipt for transparency
    receipt_service = ReceiptService(db)
    await receipt_service.create_receipt(
        user_id=current_user.user_id,
        entity_type="trust_event",
        entity_id=trust_event.id,
        action="Recorded trust event",
        receipt_type=ReceiptType.TRUST_EVENT,
        request_data={
            "event_type": event_data.event_type.value,
            "trust_delta": event_data.trust_delta,
            "visibility": event_data.visibility_scope
        },
        response_data={
            "trust_event_id": str(trust_event.id),
            "appeal_deadline": (datetime.utcnow() + timedelta(hours=72)).isoformat()
        }
    )
    
    return TrustEventResponse.from_orm(trust_event)


@router.post("/appeal", response_model=AppealResponse, status_code=status.HTTP_201_CREATED)
async def create_appeal(
    appeal_data: AppealCreate,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> AppealResponse:
    """
    Create an appeal for a trust event with due process.
    
    Ensures separation of duties - reporter cannot be resolver.
    """
    # Verify trust event exists
    trust_event = await db.get(TrustEvent, appeal_data.trust_event_id)
    if not trust_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trust event not found"
        )
    
    # Verify user is involved in the trust event
    if (str(current_user.user_id) != str(trust_event.actor_id) and 
        str(current_user.user_id) != str(trust_event.subject_id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only appeal trust events you're involved in"
        )
    
    # Check if appeal already exists
    existing_appeal = await db.execute(
        select(Appeal).where(
            and_(
                Appeal.trust_event_id == appeal_data.trust_event_id,
                Appeal.appellant_id == current_user.user_id
            )
        )
    )
    if existing_appeal.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appeal already exists for this trust event"
        )
    
    # Create appeal with due process
    appeal = Appeal(
        trust_event_id=appeal_data.trust_event_id,
        appellant_id=current_user.user_id,
        appeal_reason=appeal_data.appeal_reason,
        evidence=appeal_data.evidence,
        witness_ids=appeal_data.witness_ids,
        status=AppealStatus.PENDING,
        review_deadline=datetime.utcnow() + timedelta(days=7)  # 7 day SLA
    )
    
    db.add(appeal)
    
    # Update trust event with appeal reference
    trust_event.appeal_id = appeal.id
    
    await db.commit()
    await db.refresh(appeal)
    
    # Create receipt for transparency
    receipt_service = ReceiptService(db)
    await receipt_service.create_receipt(
        user_id=current_user.user_id,
        entity_type="appeal",
        entity_id=appeal.id,
        action="Filed appeal for trust event",
        receipt_type=ReceiptType.TRUST_EVENT,
        request_data={
            "trust_event_id": str(appeal_data.trust_event_id),
            "reason": appeal_data.appeal_reason[:200]  # Truncate for privacy
        },
        response_data={
            "appeal_id": str(appeal.id),
            "status": appeal.status.value,
            "review_deadline": appeal.review_deadline.isoformat()
        }
    )
    
    return AppealResponse.from_orm(appeal)


@router.get("/appeal/{appeal_id}", response_model=AppealResponse)
async def get_appeal_status(
    appeal_id: UUID,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> AppealResponse:
    """
    Check the status of an appeal.
    
    Only the appellant or involved parties can check status.
    """
    appeal = await db.get(Appeal, appeal_id)
    if not appeal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appeal not found"
        )
    
    # Get trust event to check involvement
    trust_event = await db.get(TrustEvent, appeal.trust_event_id)
    
    # Verify user is involved
    if (str(current_user.user_id) != str(appeal.appellant_id) and
        str(current_user.user_id) != str(trust_event.actor_id) and 
        str(current_user.user_id) != str(trust_event.subject_id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view appeals you're involved in"
        )
    
    return AppealResponse.from_orm(appeal)


@router.get("/relationships", response_model=List[TrustRelationshipResponse])
async def get_trust_relationships(
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> List[TrustRelationshipResponse]:
    """
    Get all trust relationships for the current user.
    
    Shows trust levels and resonance scores with other users.
    """
    relationships = await db.execute(
        select(TrustRelationship).where(
            or_(
                TrustRelationship.user_a_id == current_user.user_id,
                TrustRelationship.user_b_id == current_user.user_id
            )
        )
    )
    
    return [TrustRelationshipResponse.from_orm(r) for r in relationships.scalars()]


@router.post("/progress", response_model=TrustRelationshipResponse)
async def progress_trust_level(
    progression: TrustProgressionRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> TrustRelationshipResponse:
    """
    Progress trust level with another user through mutual disclosure.
    
    Implements the 5-level progression:
    1. Awareness - Zero-knowledge proof
    2. Recognition - Minimal disclosure
    3. Familiarity - Shared history
    4. Shared Memory - Mutual experiences
    5. Deep Trust - Full alignment
    
    Enforces reciprocity - disclosure must be balanced.
    """
    # Find or create trust relationship
    relationship = await db.execute(
        select(TrustRelationship).where(
            or_(
                and_(
                    TrustRelationship.user_a_id == current_user.user_id,
                    TrustRelationship.user_b_id == progression.peer_id
                ),
                and_(
                    TrustRelationship.user_a_id == progression.peer_id,
                    TrustRelationship.user_b_id == current_user.user_id
                )
            )
        )
    )
    relationship = relationship.scalar_one_or_none()
    
    if not relationship:
        # Create new relationship at awareness level
        relationship = TrustRelationship(
            user_a_id=current_user.user_id,
            user_b_id=progression.peer_id,
            trust_level=TrustLevel.AWARENESS,
            trust_score=0.1,
            first_interaction=datetime.utcnow()
        )
        db.add(relationship)
    
    # Check reciprocity - disclosure must be balanced
    is_user_a = str(relationship.user_a_id) == str(current_user.user_id)
    my_disclosure = relationship.disclosure_level_a if is_user_a else relationship.disclosure_level_b
    peer_disclosure = relationship.disclosure_level_b if is_user_a else relationship.disclosure_level_a
    
    if progression.disclosure_level > peer_disclosure + 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Disclosure must be reciprocal - peer needs to match your level"
        )
    
    # Update disclosure levels
    if is_user_a:
        relationship.disclosure_level_a = progression.disclosure_level
    else:
        relationship.disclosure_level_b = progression.disclosure_level
    
    # Calculate reciprocity balance
    relationship.reciprocity_balance = 1 - abs(
        relationship.disclosure_level_a - relationship.disclosure_level_b
    ) / 5.0
    
    # Update trust level based on mutual disclosure
    min_disclosure = min(relationship.disclosure_level_a, relationship.disclosure_level_b)
    trust_levels = list(TrustLevel)
    relationship.trust_level = trust_levels[min(min_disclosure, len(trust_levels) - 1)]
    
    # Update interaction tracking
    relationship.interaction_count += 1
    relationship.last_interaction = datetime.utcnow()
    
    await db.commit()
    await db.refresh(relationship)
    
    # Create receipt for transparency
    receipt_service = ReceiptService(db)
    await receipt_service.create_receipt(
        user_id=current_user.user_id,
        entity_type="trust_relationship",
        entity_id=relationship.id,
        action="Progressed trust level",
        receipt_type=ReceiptType.TRUST_EXCHANGE,
        request_data={
            "peer_id": str(progression.peer_id),
            "disclosure_level": progression.disclosure_level
        },
        response_data={
            "trust_level": relationship.trust_level.value,
            "reciprocity_balance": relationship.reciprocity_balance
        }
    )
    
    return TrustRelationshipResponse.from_orm(relationship)


@router.get("/patterns", response_model=Optional[ConsciousnessPatternResponse])
async def get_consciousness_patterns(
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Optional[ConsciousnessPatternResponse]:
    """
    Get consciousness patterns for the current user (if opted in).
    
    Shows behavioral patterns on spectrums without judgment.
    Users must explicitly opt-in to pattern tracking.
    """
    consciousness_map = await db.execute(
        select(ConsciousnessMap).where(
            and_(
                ConsciousnessMap.user_id == current_user.user_id,
                ConsciousnessMap.opted_in == True
            )
        )
    )
    consciousness_map = consciousness_map.scalar_one_or_none()
    
    if not consciousness_map:
        return None
    
    return ConsciousnessPatternResponse.from_orm(consciousness_map)


@router.post("/patterns/opt-in", response_model=Dict[str, str])
async def opt_in_consciousness_tracking(
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Dict[str, str]:
    """
    Opt into consciousness pattern tracking.
    
    This is completely voluntary and can be revoked at any time.
    Patterns are observed on spectrums, not judged as good/bad.
    """
    # Check if already opted in
    existing = await db.execute(
        select(ConsciousnessMap).where(
            ConsciousnessMap.user_id == current_user.user_id
        )
    )
    consciousness_map = existing.scalar_one_or_none()
    
    if consciousness_map:
        if consciousness_map.opted_in:
            return {"status": "Already opted in to consciousness tracking"}
        else:
            # Re-opt in
            consciousness_map.opted_in = True
            consciousness_map.opt_in_date = datetime.utcnow()
            consciousness_map.opt_out_date = None
    else:
        # Create new consciousness map
        consciousness_map = ConsciousnessMap(
            user_id=current_user.user_id,
            opted_in=True,
            opt_in_date=datetime.utcnow(),
            patterns={
                "transparency": 0.5,
                "trust_structure": 0.5,
                "language_style": 0.5,
                "interaction_style": 0.5,
                "disclosure_tendency": 0.5
            }
        )
        db.add(consciousness_map)
    
    await db.commit()
    
    # Create receipt for transparency
    receipt_service = ReceiptService(db)
    await receipt_service.create_receipt(
        user_id=current_user.user_id,
        action="Opted into consciousness pattern tracking",
        receipt_type=ReceiptType.CONSENT_GIVEN,
        consent_basis="Explicit user opt-in",
        data_categories=["behavioral_patterns"],
        privacy_impact="Low - patterns stored locally"
    )
    
    return {"status": "Successfully opted into consciousness tracking"}