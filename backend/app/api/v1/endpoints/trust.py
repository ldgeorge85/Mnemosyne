"""
Trust System API Endpoints

Handles trust events, appeals, and trust relationships with
sovereignty safeguards and neutral language.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
import hashlib
import json
from fastapi import APIRouter, Depends, HTTPException, Query, Body, Request, status
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
from app.services.appeals_service import AppealResolutionService
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


def _calculate_trust_event_hash(event_data: Dict[str, Any]) -> str:
    """Calculate SHA-256 hash of trust event contents."""
    # Exclude hash fields from the hash calculation
    hashable_data = {k: v for k, v in event_data.items()
                    if k not in ['content_hash', 'previous_hash', 'id']}

    # Normalize types for consistent hashing
    normalized_data = {}
    for key, value in hashable_data.items():
        if value is None:
            normalized_data[key] = None
        elif isinstance(value, UUID):
            normalized_data[key] = str(value)
        elif isinstance(value, datetime):
            normalized_data[key] = value.isoformat()
        elif hasattr(value, 'value'):  # Enum
            normalized_data[key] = value.value
        else:
            normalized_data[key] = value

    # Create deterministic JSON string
    json_str = json.dumps(normalized_data, sort_keys=True, separators=(',', ':'), default=str)

    # Calculate SHA-256 hash
    return hashlib.sha256(json_str.encode('utf-8')).hexdigest()


async def _get_last_trust_event_hash(db: AsyncSession, user_id: UUID) -> Optional[str]:
    """Get the content hash of the most recent trust event for a user."""
    result = await db.execute(
        select(TrustEvent).where(
            or_(
                TrustEvent.actor_id == user_id,
                TrustEvent.subject_id == user_id
            )
        ).order_by(TrustEvent.created_at.desc()).limit(1)
    )
    last_event = result.scalar_one_or_none()

    if last_event and last_event.content_hash:
        return last_event.content_hash

    return None


@router.post("/event", response_model=TrustEventResponse, status_code=status.HTTP_201_CREATED)
async def record_trust_event(
    event_data: TrustEventCreate,
    request: Request,
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

    # Get previous trust event hash for chaining
    previous_hash = await _get_last_trust_event_hash(db, current_user.user_id)

    # Prepare event data for hashing
    event_id = uuid4()
    created_at = datetime.utcnow()

    event_hash_data = {
        'id': event_id,
        'actor_id': event_data.actor_id,
        'subject_id': event_data.subject_id,
        'event_type': event_data.event_type,
        'trust_delta': event_data.trust_delta,
        'context': event_data.context,
        'reporter_id': current_user.user_id,
        'visibility_scope': event_data.visibility_scope or "private",
        'user_consent': event_data.user_consent or False,
        'policy_version': "v1",
        'created_at': created_at,
        'previous_hash': previous_hash
    }

    # Calculate content hash
    content_hash = _calculate_trust_event_hash(event_hash_data)

    # Create trust event with cryptographic integrity
    trust_event = TrustEvent(
        id=event_id,
        actor_id=event_data.actor_id,
        subject_id=event_data.subject_id,
        event_type=event_data.event_type,
        trust_delta=event_data.trust_delta,
        context=event_data.context,
        reporter_id=current_user.user_id,
        visibility_scope=event_data.visibility_scope or "private",
        user_consent=event_data.user_consent or False,
        policy_version="v1",
        created_at=created_at,
        content_hash=content_hash,
        previous_hash=previous_hash
    )

    db.add(trust_event)
    await db.commit()
    await db.refresh(trust_event)
    
    # Create receipt for transparency
    receipt_service = ReceiptService(db, request)
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
    request: Request,
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
    receipt_service = ReceiptService(db, request)
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
    request: Request,
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
    receipt_service = ReceiptService(db, request)
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
    request: Request,
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
    receipt_service = ReceiptService(db, request)
    await receipt_service.create_receipt(
        user_id=current_user.user_id,
        action="Opted into consciousness pattern tracking",
        receipt_type=ReceiptType.CONSENT_GIVEN,
        consent_basis="Explicit user opt-in",
        data_categories=["behavioral_patterns"],
        privacy_impact="Low - patterns stored locally"
    )

    return {"status": "Successfully opted into consciousness tracking"}


# Appeals Resolution Endpoints

@router.post("/appeal/{appeal_id}/assign-resolver", response_model=Dict[str, str])
async def assign_resolver(
    appeal_id: UUID,
    request: Request,
    preferred_resolver_id: Optional[UUID] = Body(None),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Dict[str, str]:
    """
    Assign a resolver to an appeal with separation of duties.

    Resolver cannot be:
    - The appellant
    - The reporter of the trust event
    - The actor or subject of the trust event
    """
    appeals_service = AppealResolutionService(db)

    # Verify user has permission (appellant or system admin)
    appeal = await db.get(Appeal, appeal_id)
    if not appeal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appeal not found"
        )

    if str(current_user.user_id) != str(appeal.appellant_id):
        # Future: Add system admin check here
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the appellant can request resolver assignment"
        )

    try:
        resolver_id = await appeals_service.assign_resolver(
            appeal_id=appeal_id,
            preferred_resolver_id=preferred_resolver_id
        )

        # Transition appeal to REVIEWING
        await appeals_service.transition_status(appeal_id, AppealStatus.REVIEWING)

        # Create receipt
        receipt_service = ReceiptService(db, request)
        await receipt_service.create_receipt(
            user_id=current_user.user_id,
            entity_type="appeal",
            entity_id=appeal_id,
            action="Assigned resolver to appeal",
            receipt_type=ReceiptType.TRUST_EVENT,
            response_data={
                "resolver_id": str(resolver_id),
                "appeal_status": "reviewing"
            }
        )

        return {
            "status": "Resolver assigned",
            "resolver_id": str(resolver_id),
            "appeal_status": "reviewing"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/appeal/{appeal_id}/assign-board", response_model=Dict[str, Any])
async def assign_review_board(
    appeal_id: UUID,
    request: Request,
    board_size: int = Body(3, ge=3, le=7),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Dict[str, Any]:
    """
    Assign a review board for complex appeals.

    Review board provides multi-party consensus.
    """
    appeals_service = AppealResolutionService(db)

    # Verify user has permission
    appeal = await db.get(Appeal, appeal_id)
    if not appeal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appeal not found"
        )

    if str(current_user.user_id) != str(appeal.appellant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the appellant can request board assignment"
        )

    try:
        board_member_ids = await appeals_service.assign_review_board(
            appeal_id=appeal_id,
            board_size=board_size
        )

        # Transition to REVIEWING if not already
        if appeal.status == AppealStatus.PENDING:
            await appeals_service.transition_status(appeal_id, AppealStatus.REVIEWING)

        # Create receipt
        receipt_service = ReceiptService(db, request)
        await receipt_service.create_receipt(
            user_id=current_user.user_id,
            entity_type="appeal",
            entity_id=appeal_id,
            action="Assigned review board to appeal",
            receipt_type=ReceiptType.TRUST_EVENT,
            response_data={
                "board_size": len(board_member_ids),
                "appeal_status": "reviewing"
            }
        )

        return {
            "status": "Review board assigned",
            "board_member_ids": [str(id) for id in board_member_ids],
            "board_size": len(board_member_ids),
            "appeal_status": "reviewing"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/appeal/{appeal_id}/vote", response_model=Dict[str, Any])
async def record_board_vote(
    appeal_id: UUID,
    request: Request,
    vote: str = Body(..., pattern="^(uphold|overturn)$"),
    reasoning: Optional[str] = Body(None),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Dict[str, Any]:
    """
    Record a review board member's vote on an appeal.

    Vote must be "uphold" or "overturn".
    """
    appeals_service = AppealResolutionService(db)

    try:
        vote_result = await appeals_service.record_board_vote(
            appeal_id=appeal_id,
            reviewer_id=current_user.user_id,
            vote=vote,
            reasoning=reasoning
        )

        # Check if consensus reached
        consensus = await appeals_service.check_board_consensus(appeal_id)
        if consensus:
            # Auto-resolve if consensus reached
            resolution_text = f"Review board reached consensus: {consensus}"
            await appeals_service.transition_status(
                appeal_id=appeal_id,
                new_status=AppealStatus.RESOLVED,
                resolution=resolution_text
            )
            vote_result['consensus_reached'] = True
            vote_result['resolution'] = consensus

        # Create receipt
        receipt_service = ReceiptService(db, request)
        await receipt_service.create_receipt(
            user_id=current_user.user_id,
            entity_type="appeal",
            entity_id=appeal_id,
            action=f"Voted {vote} on appeal",
            receipt_type=ReceiptType.TRUST_EVENT,
            response_data=vote_result
        )

        return vote_result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/appeal/{appeal_id}/resolve", response_model=AppealResponse)
async def resolve_appeal(
    appeal_id: UUID,
    request: Request,
    resolution: str = Body(...),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> AppealResponse:
    """
    Resolve an appeal with a final decision.

    Only the assigned resolver can resolve an appeal.
    """
    appeals_service = AppealResolutionService(db)

    # Verify resolver
    appeal = await db.get(Appeal, appeal_id)
    if not appeal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appeal not found"
        )

    trust_event = await db.get(TrustEvent, appeal.trust_event_id)
    if str(current_user.user_id) != str(trust_event.resolver_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the assigned resolver can resolve this appeal"
        )

    try:
        appeal = await appeals_service.transition_status(
            appeal_id=appeal_id,
            new_status=AppealStatus.RESOLVED,
            resolution=resolution
        )

        # Create receipt
        receipt_service = ReceiptService(db, request)
        await receipt_service.create_receipt(
            user_id=current_user.user_id,
            entity_type="appeal",
            entity_id=appeal_id,
            action="Resolved appeal",
            receipt_type=ReceiptType.TRUST_EVENT,
            response_data={
                "appeal_id": str(appeal_id),
                "status": "resolved",
                "resolution": resolution[:200]
            }
        )

        return AppealResponse.from_orm(appeal)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/appeal/{appeal_id}/escalate", response_model=AppealResponse)
async def escalate_appeal(
    appeal_id: UUID,
    request: Request,
    reason: str = Body(...),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> AppealResponse:
    """
    Escalate an appeal (e.g., due to complexity or SLA violation).

    Escalation assigns a larger review board.
    """
    appeals_service = AppealResolutionService(db)

    # Verify user is involved
    appeal = await db.get(Appeal, appeal_id)
    if not appeal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appeal not found"
        )

    trust_event = await db.get(TrustEvent, appeal.trust_event_id)

    # Allow appellant or resolver to escalate
    if (str(current_user.user_id) != str(appeal.appellant_id) and
        str(current_user.user_id) != str(trust_event.resolver_id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the appellant or resolver can escalate an appeal"
        )

    try:
        appeal = await appeals_service.escalate_appeal(
            appeal_id=appeal_id,
            reason=reason
        )

        # Create receipt
        receipt_service = ReceiptService(db, request)
        await receipt_service.create_receipt(
            user_id=current_user.user_id,
            entity_type="appeal",
            entity_id=appeal_id,
            action="Escalated appeal",
            receipt_type=ReceiptType.TRUST_EVENT,
            response_data={
                "appeal_id": str(appeal_id),
                "status": "escalated",
                "reason": reason[:200]
            }
        )

        return AppealResponse.from_orm(appeal)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/appeals/sla-violations", response_model=List[AppealResponse])
async def check_sla_violations(
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> List[AppealResponse]:
    """
    Check for appeals with SLA violations (past review deadline).

    Only system admins should have access to this in production.
    """
    appeals_service = AppealResolutionService(db)

    # Future: Add admin check here

    overdue_appeals = await appeals_service.check_sla_violations()

    return [AppealResponse.from_orm(appeal) for appeal in overdue_appeals]