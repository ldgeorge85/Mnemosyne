"""
Cognitive Signature (Deep Signal) endpoints for Mnemosyne Protocol
"""

from typing import List, Optional, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from backend.api.deps import get_db, get_current_active_user
from backend.models.user import User
from backend.models.signal import CognitiveSignature
from backend.services.signature_service import SignatureService
from backend.signatures.generator import SignatureGenerator
from backend.core.redis_client import RedisClient

router = APIRouter()


# Pydantic models
class SignalGenerateRequest(BaseModel):
    force_regenerate: bool = False
    visibility: float = Field(0.3, ge=0.0, le=1.0)


class SignalResponse(BaseModel):
    id: str
    user_id: str
    sigil: str
    domains: List[str]
    glyphs: List[str]
    coherence: dict
    flags: dict
    visibility: float
    kartouche_svg: Optional[str]
    created_at: datetime
    decay_timer: int
    
    class Config:
        from_attributes = True


class SignalVerifyRequest(BaseModel):
    signal_id: str
    verification_type: str = "cognitive"  # cognitive, cryptographic, ritual


class SignalDiscoveryRequest(BaseModel):
    domains: Optional[List[str]] = None
    min_coherence: float = Field(0.5, ge=0.0, le=1.0)
    limit: int = Field(10, ge=1, le=50)


@router.post("/generate", response_model=SignalResponse)
async def generate_signal(
    request: SignalGenerateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    redis: RedisClient = Depends(get_redis)
) -> Any:
    """
    Generate or retrieve user's Cognitive Signature
    """
    # Check cooldown
    cooldown_key = f"signal_cooldown:{current_user.id}"
    if not request.force_regenerate:
        cooldown = await redis.client.get(cooldown_key)
        if cooldown:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Signal generation on cooldown. Wait {cooldown} seconds."
            )
    
    signature_service = SignatureService(db)
    
    # Check for existing signal
    existing = await signature_service.get_user_signature(current_user.id)
    
    if existing and not request.force_regenerate:
        # Check if signal needs re-evaluation
        age_days = (datetime.utcnow() - existing.created_at).days
        if age_days < 7:  # Signal still fresh
            return existing
    
    # Generate new signal
    generator = SignatureGenerator(db)
    signature = await generator.generate_signature(
        user_id=current_user.id,
        visibility=request.visibility
    )
    
    # Set cooldown (15 minutes)
    await redis.client.setex(cooldown_key, 900, "900")
    
    return signature


@router.get("/mine", response_model=SignalResponse)
async def get_my_signal(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get current user's Cognitive Signature
    """
    signature_service = SignatureService(db)
    signature = await signature_service.get_user_signature(current_user.id)
    
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No signal generated yet. Use /generate endpoint first."
        )
    
    return signature


@router.post("/verify")
async def verify_signal(
    request: SignalVerifyRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Verify another user's Cognitive Signature
    """
    signature_service = SignatureService(db)
    
    # Get the signal to verify
    signal = await db.get(CognitiveSignature, request.signal_id)
    if not signal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signal not found"
        )
    
    # Check visibility
    if signal.visibility < 0.1:  # Too private to verify
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Signal is too private to verify"
        )
    
    # Perform verification
    if request.verification_type == "cognitive":
        # Compare cognitive patterns
        my_signal = await signature_service.get_user_signature(current_user.id)
        if not my_signal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Generate your own signal first"
            )
        
        # Calculate resonance
        resonance = await signature_service.calculate_resonance(my_signal, signal)
        
        return {
            "verified": resonance > 0.5,
            "resonance": resonance,
            "shared_domains": list(set(my_signal.domains) & set(signal.domains)),
            "compatibility": "high" if resonance > 0.7 else "medium" if resonance > 0.4 else "low"
        }
    
    elif request.verification_type == "cryptographic":
        # Verify cryptographic signature
        is_valid = await signature_service.verify_cryptographic_signature(signal)
        
        return {
            "verified": is_valid,
            "method": "ed25519",
            "timestamp": signal.created_at
        }
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification type"
        )


@router.post("/discover", response_model=List[SignalResponse])
async def discover_signals(
    request: SignalDiscoveryRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Discover other users' Cognitive Signatures based on criteria
    """
    query = select(CognitiveSignature).where(
        CognitiveSignature.user_id != current_user.id,
        CognitiveSignature.visibility >= 0.2  # Minimum visibility for discovery
    )
    
    # Filter by domains if specified
    if request.domains:
        # This would need a more complex query with JSONB operations
        # For now, fetch all and filter in Python
        pass
    
    # Filter by coherence
    # Note: This assumes coherence is stored as JSONB with a 'strength' field
    # Would need proper JSONB query in production
    
    query = query.limit(request.limit)
    
    result = await db.execute(query)
    signals = result.scalars().all()
    
    # Filter by coherence in Python (should be done in SQL for production)
    filtered_signals = []
    for signal in signals:
        coherence_strength = signal.coherence.get("strength", 0)
        if coherence_strength >= request.min_coherence:
            filtered_signals.append(signal)
    
    return filtered_signals


@router.put("/{signal_id}/decay")
async def update_signal_decay(
    signal_id: str,
    decay_days: int = Field(..., ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Update the decay timer for a signal
    """
    signal = await db.get(CognitiveSignature, signal_id)
    
    if not signal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signal not found"
        )
    
    if signal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this signal"
        )
    
    # Update decay timer
    signal.decay_timer = decay_days * 24 * 3600  # Convert to seconds
    await db.commit()
    
    return {"message": f"Decay timer updated to {decay_days} days"}


@router.get("/kartouche/{signal_id}")
async def get_kartouche(
    signal_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get the Kartouche (visual representation) for a signal
    """
    signal = await db.get(CognitiveSignature, signal_id)
    
    if not signal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signal not found"
        )
    
    # Check visibility
    if signal.user_id != current_user.id and signal.visibility < 0.1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Signal is too private to view"
        )
    
    # Generate or retrieve Kartouche SVG
    if not signal.kartouche_svg:
        from backend.signatures.kartouche import KartoucheRenderer
        renderer = KartoucheRenderer()
        signal.kartouche_svg = await renderer.render_svg(signal)
        await db.commit()
    
    return {
        "signal_id": signal_id,
        "kartouche_svg": signal.kartouche_svg,
        "sigil": signal.sigil,
        "glyphs": signal.glyphs
    }