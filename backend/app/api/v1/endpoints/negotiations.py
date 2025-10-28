"""
Negotiations API Endpoints

Multi-party negotiation for reaching binding agreements without central authority.
"""

import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.api.dependencies.db import get_async_db
from app.core.auth.manager import get_current_user
from app.core.auth.base import AuthUser
from app.db.models.negotiation import Negotiation, NegotiationMessage
from app.db.models.receipt import ReceiptType
from app.services.negotiation_service import NegotiationService
from app.services.receipt_service import ReceiptService
from app.schemas.negotiation import (
    NegotiationCreate,
    NegotiationResponse,
    NegotiationDetailResponse,
    NegotiationListResponse,
    NegotiationMessageResponse,
    OfferCreate,
    AcceptTerms,
    FinalizeCommitment,
    WithdrawRequest,
    DisputeRequest,
    TimeoutCheckResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=NegotiationResponse, status_code=status.HTTP_201_CREATED)
async def create_negotiation(
    request: Request,
    negotiation_data: NegotiationCreate,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> NegotiationResponse:
    """
    Create a new multi-party negotiation.

    Initiator proposes initial terms and invites participants.
    All parties must explicitly join before negotiation begins.
    """
    service = NegotiationService(db)
    receipt_service = ReceiptService(db)

    try:
        negotiation = await service.create_negotiation(
            initiator_id=current_user.user_id,
            title=negotiation_data.title,
            description=negotiation_data.description,
            participant_ids=negotiation_data.participant_ids,
            initial_terms=negotiation_data.initial_terms,
            negotiation_days=negotiation_data.negotiation_days,
            finalization_days=negotiation_data.finalization_days,
            required_consensus_count=negotiation_data.required_consensus_count
        )

        # Create receipt
        await receipt_service.create_receipt(
            user_id=current_user.user_id,
            action=ReceiptType.NEGOTIATION_CREATED,
            resource_type="negotiation",
            resource_id=negotiation.id,
            metadata={
                "negotiation_id": str(negotiation.id),
                "title": negotiation.title,
                "participant_count": len(negotiation.participant_ids),
                "terms_version": 1
            },
            request=request
        )

        return NegotiationResponse.from_orm(negotiation)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating negotiation: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create negotiation")


@router.get("/{negotiation_id}", response_model=NegotiationDetailResponse)
async def get_negotiation(
    negotiation_id: UUID,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> NegotiationDetailResponse:
    """
    Get negotiation details including message history.

    Only participants can view negotiation details.
    """
    negotiation = await db.get(Negotiation, negotiation_id)

    if not negotiation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negotiation not found")

    # Check if user is participant
    if current_user.user_id not in negotiation.participant_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a participant in this negotiation")

    # Load messages
    messages_result = await db.execute(
        select(NegotiationMessage).where(
            NegotiationMessage.negotiation_id == negotiation_id
        ).order_by(NegotiationMessage.created_at)
    )
    messages = messages_result.scalars().all()

    # Create response
    response = NegotiationDetailResponse.from_orm(negotiation)
    response.messages = [NegotiationMessageResponse.from_orm(msg) for msg in messages]

    return response


@router.get("", response_model=NegotiationListResponse)
async def list_negotiations(
    status_filter: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> NegotiationListResponse:
    """
    List negotiations user is participating in.

    Filter by status (initiated, negotiating, consensus_reached, binding, etc.)
    """
    # Build query
    query = select(Negotiation).where(
        Negotiation.participant_ids.contains([current_user.user_id])
    )

    if status_filter:
        from app.db.models.negotiation import NegotiationStatus
        try:
            status_enum = NegotiationStatus(status_filter)
            query = query.where(Negotiation.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status: {status_filter}")

    # Get total count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    # Pagination
    offset = (page - 1) * page_size
    query = query.order_by(Negotiation.created_at.desc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    negotiations = result.scalars().all()

    return NegotiationListResponse(
        negotiations=[NegotiationResponse.from_orm(n) for n in negotiations],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/{negotiation_id}/join", response_model=NegotiationResponse)
async def join_negotiation(
    negotiation_id: UUID,
    request: Request,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> NegotiationResponse:
    """
    Join a negotiation as invited participant.

    Once all participants join, status → NEGOTIATING.
    """
    service = NegotiationService(db)
    receipt_service = ReceiptService(db)

    try:
        negotiation = await service.join_negotiation(
            negotiation_id=negotiation_id,
            participant_id=current_user.user_id
        )

        # Create receipt
        await receipt_service.create_receipt(
            user_id=current_user.user_id,
            action=ReceiptType.NEGOTIATION_JOINED,
            resource_type="negotiation",
            resource_id=negotiation.id,
            metadata={
                "negotiation_id": str(negotiation.id),
                "status": negotiation.status.value,
                "joined_count": len(negotiation.joined_participant_ids),
                "total_participants": len(negotiation.participant_ids)
            },
            request=request
        )

        return NegotiationResponse.from_orm(negotiation)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error joining negotiation: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to join negotiation")


@router.post("/{negotiation_id}/offer", response_model=NegotiationMessageResponse)
async def send_offer(
    negotiation_id: UUID,
    request: Request,
    offer_data: OfferCreate,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> NegotiationMessageResponse:
    """
    Send an offer or counter-offer.

    Updates current terms and increments version.
    Clears previous acceptances (new terms need new consensus).
    """
    service = NegotiationService(db)
    receipt_service = ReceiptService(db)

    try:
        negotiation, message = await service.send_offer(
            negotiation_id=negotiation_id,
            sender_id=current_user.user_id,
            terms=offer_data.terms,
            message_text=offer_data.message_text
        )

        # Create receipt
        await receipt_service.create_receipt(
            user_id=current_user.user_id,
            action=ReceiptType.NEGOTIATION_OFFER,
            resource_type="negotiation_message",
            resource_id=message.id,
            metadata={
                "negotiation_id": str(negotiation.id),
                "message_type": message.message_type.value,
                "terms_version": negotiation.terms_version
            },
            request=request
        )

        return NegotiationMessageResponse.from_orm(message)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error sending offer: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send offer")


@router.post("/{negotiation_id}/accept", response_model=NegotiationResponse)
async def accept_terms(
    negotiation_id: UUID,
    request: Request,
    accept_data: AcceptTerms,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> NegotiationResponse:
    """
    Accept current terms.

    If all required participants accept same version → CONSENSUS_REACHED.
    """
    service = NegotiationService(db)
    receipt_service = ReceiptService(db)

    try:
        negotiation = await service.accept_terms(
            negotiation_id=negotiation_id,
            acceptor_id=current_user.user_id,
            signature=accept_data.signature,
            message_text=accept_data.message_text
        )

        # Create receipt
        receipt_action = (ReceiptType.NEGOTIATION_CONSENSUS if
                         negotiation.status.value == "consensus_reached"
                         else ReceiptType.NEGOTIATION_ACCEPTED)

        await receipt_service.create_receipt(
            user_id=current_user.user_id,
            action=receipt_action,
            resource_type="negotiation",
            resource_id=negotiation.id,
            metadata={
                "negotiation_id": str(negotiation.id),
                "terms_version": negotiation.terms_version,
                "status": negotiation.status.value,
                "acceptance_count": len(negotiation.acceptances)
            },
            request=request
        )

        return NegotiationResponse.from_orm(negotiation)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error accepting terms: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to accept terms")


@router.post("/{negotiation_id}/finalize", response_model=NegotiationResponse)
async def finalize_commitment(
    negotiation_id: UUID,
    request: Request,
    finalize_data: FinalizeCommitment,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> NegotiationResponse:
    """
    Finalize binding commitment.

    If all participants finalize → BINDING (irreversible).
    """
    service = NegotiationService(db)
    receipt_service = ReceiptService(db)

    try:
        negotiation = await service.finalize_commitment(
            negotiation_id=negotiation_id,
            finalizer_id=current_user.user_id,
            signature=finalize_data.signature
        )

        # Create receipt
        receipt_action = (ReceiptType.NEGOTIATION_BINDING if
                         negotiation.status.value == "binding"
                         else ReceiptType.NEGOTIATION_FINALIZED)

        await receipt_service.create_receipt(
            user_id=current_user.user_id,
            action=receipt_action,
            resource_type="negotiation",
            resource_id=negotiation.id,
            metadata={
                "negotiation_id": str(negotiation.id),
                "status": negotiation.status.value,
                "finalization_count": len(negotiation.finalizations),
                "binding_hash": negotiation.binding_hash
            },
            request=request
        )

        return NegotiationResponse.from_orm(negotiation)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error finalizing commitment: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to finalize commitment")


@router.post("/{negotiation_id}/withdraw", response_model=NegotiationResponse)
async def withdraw_from_negotiation(
    negotiation_id: UUID,
    request: Request,
    withdraw_data: WithdrawRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> NegotiationResponse:
    """
    Withdraw from negotiation.

    Terminates negotiation for all parties.
    Cannot withdraw from BINDING agreements (use dispute instead).
    """
    service = NegotiationService(db)
    receipt_service = ReceiptService(db)

    try:
        negotiation = await service.withdraw(
            negotiation_id=negotiation_id,
            withdrawer_id=current_user.user_id,
            reason=withdraw_data.reason
        )

        # Create receipt
        await receipt_service.create_receipt(
            user_id=current_user.user_id,
            action=ReceiptType.NEGOTIATION_WITHDRAWN,
            resource_type="negotiation",
            resource_id=negotiation.id,
            metadata={
                "negotiation_id": str(negotiation.id),
                "reason": withdraw_data.reason,
                "status": negotiation.status.value
            },
            request=request
        )

        return NegotiationResponse.from_orm(negotiation)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error withdrawing from negotiation: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to withdraw")


@router.post("/{negotiation_id}/dispute", response_model=NegotiationResponse)
async def dispute_binding_agreement(
    negotiation_id: UUID,
    request: Request,
    dispute_data: DisputeRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> NegotiationResponse:
    """
    Dispute a binding agreement.

    Creates appeal using existing appeals resolution system.
    Only works for BINDING agreements.
    """
    service = NegotiationService(db)
    receipt_service = ReceiptService(db)

    try:
        negotiation, appeal = await service.dispute_binding(
            negotiation_id=negotiation_id,
            disputer_id=current_user.user_id,
            dispute_reason=dispute_data.dispute_reason
        )

        # Create receipt
        await receipt_service.create_receipt(
            user_id=current_user.user_id,
            action=ReceiptType.NEGOTIATION_DISPUTED,
            resource_type="negotiation",
            resource_id=negotiation.id,
            metadata={
                "negotiation_id": str(negotiation.id),
                "dispute_reason": dispute_data.dispute_reason,
                "status": negotiation.status.value,
                "appeal_id": str(appeal.id) if appeal else None
            },
            request=request
        )

        return NegotiationResponse.from_orm(negotiation)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error disputing agreement: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to dispute agreement")


@router.get("/admin/check-timeouts", response_model=TimeoutCheckResponse)
async def check_negotiation_timeouts(
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> TimeoutCheckResponse:
    """
    Check for negotiations past their deadlines.

    Admin endpoint to find and expire timed-out negotiations.
    """
    service = NegotiationService(db)

    try:
        results = await service.check_timeouts()

        return TimeoutCheckResponse(
            negotiation_timeouts=[NegotiationResponse.from_orm(n) for n in results['negotiation_timeouts']],
            finalization_timeouts=[NegotiationResponse.from_orm(n) for n in results['finalization_timeouts']],
            total_expired=len(results['negotiation_timeouts']) + len(results['finalization_timeouts'])
        )

    except Exception as e:
        logger.error(f"Error checking timeouts: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to check timeouts")


# Add missing import
from sqlalchemy import func
