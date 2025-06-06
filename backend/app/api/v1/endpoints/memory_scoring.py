"""
Memory Relevance Scoring API endpoints.

This module provides API endpoints for retrieving and updating memory
relevance scores, managing scoring factors, and providing feedback for
the relevance scoring system.
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from pydantic import BaseModel, Field

from app.api.dependencies.db import get_db
from app.api.dependencies.auth import get_current_user, is_admin
from app.services.memory.relevance import memory_relevance_scorer
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()


class MemoryScore(BaseModel):
    """Schema for a memory score."""
    memory_id: str
    overall_score: float
    factor_scores: Dict[str, float]
    calculated_at: Optional[str] = None


class BatchScoreRequest(BaseModel):
    """Schema for a batch scoring request."""
    memory_ids: List[str]
    recalculate: bool = Field(False, description="Whether to recalculate scores")


class ScoringFactorConfig(BaseModel):
    """Schema for a scoring factor configuration."""
    name: str
    weight: float
    enabled: bool = True
    parameters: Optional[Dict[str, Any]] = None


class ScoringFeedback(BaseModel):
    """Schema for user feedback on memory relevance."""
    memory_id: str
    query_context: Optional[str] = None
    user_score: float = Field(..., ge=0.0, le=1.0)
    reason: Optional[str] = None


@router.get("/memories/{memory_id}/score", response_model=MemoryScore)
async def get_memory_score(
    memory_id: str,
    recalculate: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> MemoryScore:
    """
    Get the relevance score for a specific memory.
    
    Args:
        memory_id: ID of the memory
        recalculate: Whether to recalculate the score
        db: Database session
        current_user_id: ID of the authenticated user
        
    Returns:
        Memory score
    """
    # Get and return the memory score
    score = await memory_relevance_scorer.get_memory_score(
        memory_id=memory_id,
        db=db,
        recalculate=recalculate
    )
    
    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory with ID {memory_id} not found"
        )
    
    return MemoryScore(**score)


@router.post("/memories/batch-scores", response_model=List[MemoryScore])
async def get_batch_memory_scores(
    request: BatchScoreRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[MemoryScore]:
    """
    Get relevance scores for multiple memories.
    
    Args:
        request: Batch score request
        db: Database session
        current_user_id: ID of the authenticated user
        
    Returns:
        List of memory scores
    """
    # Get scores for each memory ID
    scores = []
    for memory_id in request.memory_ids:
        score = await memory_relevance_scorer.get_memory_score(
            memory_id=memory_id,
            db=db,
            recalculate=request.recalculate
        )
        
        if score:
            scores.append(MemoryScore(**score))
    
    return scores


@router.post("/update-scores", response_model=Dict[str, Any])
async def update_memory_scores(
    background_tasks: BackgroundTasks,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    is_admin: bool = Depends(is_admin)
) -> Dict[str, Any]:
    """
    Update relevance scores for memories.
    
    Args:
        background_tasks: FastAPI background tasks
        limit: Maximum number of memories to update
        db: Database session
        current_user_id: ID of the authenticated user
        is_admin: Whether the user is an admin
        
    Returns:
        Update results
    """
    # Only admins can update all user scores
    if is_admin:
        # Run in background to avoid timeout
        background_tasks.add_task(
            memory_relevance_scorer.update_memory_scores,
            db=db,
            limit=limit
        )
        
        return {
            "message": f"Updating scores for up to {limit} memories in the background"
        }
    else:
        # Non-admins can only update their own memories
        result = await memory_relevance_scorer.update_memory_scores(
            db=db,
            user_id=current_user_id,
            limit=limit
        )
        
        return result


@router.post("/feedback", response_model=Dict[str, Any])
async def submit_scoring_feedback(
    feedback: ScoringFeedback,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Submit user feedback on memory relevance.
    
    Args:
        feedback: User feedback
        db: Database session
        current_user_id: ID of the authenticated user
        
    Returns:
        Result of feedback submission
    """
    # Insert the feedback
    query = """
        INSERT INTO memory_relevance_feedback (
            memory_id, user_id, user_score, query_context, reason, created_at
        )
        VALUES (
            :memory_id, :user_id, :user_score, :query_context, :reason, NOW()
        )
    """
    
    try:
        await db.execute(
            query,
            {
                "memory_id": feedback.memory_id,
                "user_id": current_user_id,
                "user_score": feedback.user_score,
                "query_context": feedback.query_context,
                "reason": feedback.reason
            }
        )
        
        await db.commit()
        
        # Return success
        return {
            "message": "Feedback submitted successfully",
            "status": "success"
        }
    except Exception as e:
        await db.rollback()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting feedback: {str(e)}"
        )
