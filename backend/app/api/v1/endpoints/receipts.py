"""
Receipts API Endpoints

Provides endpoints for viewing and managing transparency receipts.
"""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.auth.manager import get_current_user
from app.core.auth.base import AuthUser
from app.db.session import get_async_db
from app.db.models.receipt import Receipt, ReceiptType
from app.services.receipt_service import ReceiptService

logger = logging.getLogger(__name__)

router = APIRouter()


class ReceiptResponse(BaseModel):
    """Receipt response model."""
    id: str
    user_id: str
    receipt_type: str
    timestamp: datetime
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    context: Optional[dict] = None
    persona_mode: Optional[str] = None
    worldview_profile: Optional[dict] = None
    decisions_made: Optional[list] = None
    confidence_score: Optional[float] = None
    explanation: Optional[str] = None
    privacy_impact: Optional[str] = None
    user_visible: bool = True
    
    class Config:
        from_attributes = True


class ReceiptStatsResponse(BaseModel):
    """Receipt statistics response."""
    total_receipts: int
    by_type: dict = Field(default_factory=dict)
    by_entity: dict = Field(default_factory=dict)
    by_privacy_impact: dict = Field(default_factory=dict)
    by_persona_mode: dict = Field(default_factory=dict)


@router.get("/", response_model=List[ReceiptResponse])
async def get_user_receipts(
    receipt_type: Optional[str] = Query(None, description="Filter by receipt type"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[str] = Query(None, description="Filter by entity ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of receipts"),
    offset: int = Query(0, ge=0, description="Number of receipts to skip"),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get receipts for the current user.
    
    Returns a list of receipts with optional filtering.
    """
    try:
        service = ReceiptService(db)
        
        # Convert receipt type string to enum if provided
        receipt_type_enum = None
        if receipt_type:
            try:
                receipt_type_enum = ReceiptType(receipt_type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid receipt type: {receipt_type}"
                )
        
        # Convert entity_id string to UUID if provided
        entity_uuid = None
        if entity_id:
            try:
                entity_uuid = UUID(entity_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid entity ID format: {entity_id}"
                )
        
        receipts = await service.get_user_receipts(
            user_id=UUID(current_user.user_id),
            receipt_type=receipt_type_enum,
            entity_type=entity_type,
            entity_id=entity_uuid,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
            only_visible=True
        )
        
        return [
            ReceiptResponse(
                id=str(r.id),
                user_id=str(r.user_id),
                receipt_type=r.receipt_type.value if r.receipt_type else "unknown",
                timestamp=r.timestamp,
                action=r.action,
                entity_type=r.entity_type,
                entity_id=str(r.entity_id) if r.entity_id else None,
                context=r.context,
                persona_mode=r.persona_mode,
                worldview_profile=r.worldview_profile,
                decisions_made=r.decisions_made,
                confidence_score=r.confidence_score,
                explanation=r.explanation,
                privacy_impact=r.privacy_impact,
                user_visible=r.user_visible
            )
            for r in receipts
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user receipts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve receipts"
        )


@router.get("/stats", response_model=ReceiptStatsResponse)
async def get_receipt_stats(
    start_date: Optional[datetime] = Query(None, description="Start date for statistics"),
    end_date: Optional[datetime] = Query(None, description="End date for statistics"),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get receipt statistics for the current user.
    
    Returns aggregated statistics about the user's receipts.
    """
    try:
        service = ReceiptService(db)
        
        stats = await service.get_receipt_stats(
            user_id=UUID(current_user.user_id),
            start_date=start_date,
            end_date=end_date
        )
        
        return ReceiptStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Error getting receipt stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve receipt statistics"
        )


@router.get("/{receipt_id}", response_model=ReceiptResponse)
async def get_receipt(
    receipt_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get a specific receipt by ID.
    
    Returns the receipt if found and the user has access to it.
    """
    try:
        # Convert receipt_id to UUID
        try:
            receipt_uuid = UUID(receipt_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid receipt ID format: {receipt_id}"
            )
        
        service = ReceiptService(db)
        
        receipt = await service.get_receipt_by_id(
            receipt_id=receipt_uuid,
            user_id=UUID(current_user.user_id)
        )
        
        if not receipt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receipt not found"
            )
        
        return ReceiptResponse(
            id=str(receipt.id),
            user_id=str(receipt.user_id),
            receipt_type=receipt.receipt_type.value if receipt.receipt_type else "unknown",
            timestamp=receipt.timestamp,
            action=receipt.action,
            entity_type=receipt.entity_type,
            entity_id=str(receipt.entity_id) if receipt.entity_id else None,
            context=receipt.context,
            persona_mode=receipt.persona_mode,
            worldview_profile=receipt.worldview_profile,
            decisions_made=receipt.decisions_made,
            confidence_score=receipt.confidence_score,
            explanation=receipt.explanation,
            privacy_impact=receipt.privacy_impact,
            user_visible=receipt.user_visible
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting receipt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve receipt"
        )


@router.get("/entity/{entity_type}/{entity_id}", response_model=List[ReceiptResponse])
async def get_entity_receipts(
    entity_type: str,
    entity_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all receipts for a specific entity.
    
    Returns all receipts related to a specific entity (e.g., a memory or task).
    """
    try:
        # Convert entity_id to UUID
        try:
            entity_uuid = UUID(entity_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid entity ID format: {entity_id}"
            )
        
        service = ReceiptService(db)
        
        receipts = await service.get_entity_receipts(
            entity_type=entity_type,
            entity_id=entity_uuid,
            user_id=UUID(current_user.user_id)
        )
        
        return [
            ReceiptResponse(
                id=str(r.id),
                user_id=str(r.user_id),
                receipt_type=r.receipt_type.value if r.receipt_type else "unknown",
                timestamp=r.timestamp,
                action=r.action,
                entity_type=r.entity_type,
                entity_id=str(r.entity_id) if r.entity_id else None,
                context=r.context,
                persona_mode=r.persona_mode,
                worldview_profile=r.worldview_profile,
                decisions_made=r.decisions_made,
                confidence_score=r.confidence_score,
                explanation=r.explanation,
                privacy_impact=r.privacy_impact,
                user_visible=r.user_visible
            )
            for r in receipts
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting entity receipts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve entity receipts"
        )