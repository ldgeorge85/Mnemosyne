"""
Memory Management API endpoints.

This module provides API endpoints for managing memories, including
maintenance, pruning, and storage optimization.
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from pydantic import BaseModel, Field

from app.db.session import get_async_db
from app.api.dependencies.auth import get_current_user, is_admin
from app.services.memory.management import memory_management_service
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()


class MaintenanceRequest(BaseModel):
    """Schema for a maintenance request."""
    dry_run: bool = Field(True, description="Whether to perform a dry run (no changes)")


class MaintenanceResponse(BaseModel):
    """Schema for a maintenance response."""
    pruned: int = Field(..., description="Number of pruned memories")
    archived: int = Field(..., description="Number of archived memories")
    optimized: int = Field(..., description="Number of optimized storage items")
    pruned_memories: List[Dict[str, Any]] = Field(default_factory=list, description="Details of pruned memories")
    archived_memories: List[Dict[str, Any]] = Field(default_factory=list, description="Details of archived memories")
    stats: Optional[Dict[str, Any]] = Field(None, description="Memory statistics")
    dry_run: bool = Field(..., description="Whether this was a dry run")
    error: Optional[str] = Field(None, description="Error message, if any")


class RetentionPolicyResponse(BaseModel):
    """Schema for a retention policy response."""
    name: str = Field(..., description="Name of the policy")
    max_age_days: Optional[int] = Field(None, description="Maximum age in days")
    max_count: Optional[int] = Field(None, description="Maximum number of memories")
    min_access_count: Optional[int] = Field(None, description="Minimum access count")
    importance_threshold: Optional[float] = Field(None, description="Minimum importance score")
    archive_enabled: bool = Field(..., description="Whether archiving is enabled")


@router.post("/maintenance", response_model=MaintenanceResponse)
async def run_maintenance(
    request: MaintenanceRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    is_admin: bool = Depends(is_admin)
) -> MaintenanceResponse:
    """
    Run memory maintenance tasks.
    
    Args:
        request: Maintenance request parameters
        background_tasks: FastAPI background tasks
        db: Database session
        current_user_id: ID of the authenticated user
        is_admin: Whether the user is an admin
        
    Returns:
        Maintenance results
    """
    # Check admin permissions
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to perform maintenance"
        )
    
    # Run maintenance in background if not dry run
    if not request.dry_run:
        # First, run a dry run to get the preview
        preview_results = await memory_management_service.run_maintenance(
            db=db,
            dry_run=True
        )
        
        # Then, run the actual maintenance in the background
        background_tasks.add_task(
            memory_management_service.run_maintenance,
            db=db,
            dry_run=False
        )
        
        # Return preview results with a note
        preview_results["message"] = "Maintenance is running in the background. This is a preview of the changes."
        return MaintenanceResponse(**preview_results)
    else:
        # Just run a dry run
        results = await memory_management_service.run_maintenance(
            db=db,
            dry_run=True
        )
        
        return MaintenanceResponse(**results)


@router.get("/statistics", response_model=Dict[str, Any])
async def get_memory_statistics(
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    is_admin: bool = Depends(is_admin)
) -> Dict[str, Any]:
    """
    Get memory statistics.
    
    Args:
        db: Database session
        current_user_id: ID of the authenticated user
        is_admin: Whether the user is an admin
        
    Returns:
        Memory statistics
    """
    # Check admin permissions
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to view system-wide statistics"
        )
    
    # Get statistics
    stats = await memory_management_service._get_memory_statistics(db)
    
    return stats


@router.get("/policies", response_model=List[RetentionPolicyResponse])
async def get_retention_policies(
    db: AsyncSession = Depends(get_async_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[RetentionPolicyResponse]:
    """
    Get available retention policies.
    
    Args:
        db: Database session
        current_user_id: ID of the authenticated user
        
    Returns:
        List of retention policies
    """
    # Get policies from the service
    policies = [
        RetentionPolicyResponse(
            name=name,
            max_age_days=policy.max_age_days,
            max_count=policy.max_count,
            min_access_count=policy.min_access_count,
            importance_threshold=policy.importance_threshold,
            archive_enabled=policy.archive_enabled
        )
        for name, policy in memory_management_service.policies.items()
    ]
    
    return policies
