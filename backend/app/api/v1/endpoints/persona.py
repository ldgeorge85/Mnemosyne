"""
Persona Management Endpoints

This module provides API endpoints for managing persona modes,
worldview preferences, and interaction history.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.auth.manager import get_current_user
from app.core.auth.base import AuthUser
from app.db.session import get_async_db
from app.services.persona.manager import PersonaManager
from app.services.persona.base import PersonaMode
from app.services.persona.worldview import PhilosophicalTradition

router = APIRouter()


class PersonaStateResponse(BaseModel):
    """Current persona state"""
    current_mode: Optional[str]
    trust_level: Optional[float]
    worldview: Optional[Dict[str, Any]]
    mode_history_count: int
    axioms: List[str]
    creed: List[str]


class ModeSwitchRequest(BaseModel):
    """Request to switch persona mode"""
    mode: str  # confidant, mentor, mediator, guardian
    reason: Optional[str] = None


class ModeSwitchResponse(BaseModel):
    """Response after mode switch"""
    previous_mode: Optional[str]
    current_mode: str
    reason: str
    greeting: str


class WorldviewUpdateRequest(BaseModel):
    """Request to update worldview preferences"""
    primary_tradition: Optional[str] = None
    secondary_traditions: Optional[List[str]] = None
    communication_style: Optional[str] = None
    values_hierarchy: Optional[List[str]] = None
    ethical_framework: Optional[str] = None
    cultural_context: Optional[str] = None


class ModeAnalysisRequest(BaseModel):
    """Request to analyze context for appropriate mode"""
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = None


class ModeAnalysisResponse(BaseModel):
    """Recommended mode based on context"""
    recommended_mode: str
    confidence: float
    signals: Dict[str, bool]


@router.get("/state", response_model=PersonaStateResponse)
async def get_persona_state(
    user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> PersonaStateResponse:
    """
    Get the current state of the persona system for the user.
    """
    persona_manager = PersonaManager(db)
    await persona_manager.initialize_for_user(str(user.user_id))
    
    state = persona_manager.get_current_state()
    
    return PersonaStateResponse(
        current_mode=state.get("current_mode"),
        trust_level=state.get("trust_level"),
        worldview=state.get("worldview"),
        mode_history_count=state.get("mode_history_count", 0),
        axioms=state.get("axioms", []),
        creed=state.get("creed", [])
    )


@router.post("/mode/switch", response_model=ModeSwitchResponse)
async def switch_persona_mode(
    request: ModeSwitchRequest,
    user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> ModeSwitchResponse:
    """
    Manually switch the persona to a different mode.
    """
    # Validate mode
    try:
        mode = PersonaMode(request.mode)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode: {request.mode}. Must be one of: confidant, mentor, mediator, guardian"
        )
    
    persona_manager = PersonaManager(db)
    await persona_manager.initialize_for_user(str(user.user_id))
    
    result = await persona_manager.switch_mode(
        mode,
        request.reason or "Manual switch by user"
    )
    
    return ModeSwitchResponse(
        previous_mode=result["previous_mode"],
        current_mode=result["current_mode"],
        reason=result["reason"],
        greeting=result["greeting"]
    )


@router.post("/mode/analyze", response_model=ModeAnalysisResponse)
async def analyze_for_mode(
    request: ModeAnalysisRequest,
    user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> ModeAnalysisResponse:
    """
    Analyze a message and conversation context to recommend appropriate persona mode.
    """
    persona_manager = PersonaManager(db)
    await persona_manager.initialize_for_user(str(user.user_id))
    
    recommended_mode = await persona_manager.analyze_context_for_mode(
        request.message,
        request.conversation_history
    )
    
    # Analyze signals for transparency
    message_lower = request.message.lower()
    signals = {
        "crisis": any(word in message_lower for word in ["help", "emergency", "danger", "scared"]),
        "learning": any(word in message_lower for word in ["how to", "learn", "teach", "explain"]),
        "conflict": any(word in message_lower for word in ["disagree", "conflict", "argument"]),
        "emotional": any(word in message_lower for word in ["feel", "emotion", "sad", "anxious"])
    }
    
    # Calculate confidence based on signal strength
    signal_count = sum(1 for v in signals.values() if v)
    confidence = min(0.9, 0.5 + (signal_count * 0.2))
    
    return ModeAnalysisResponse(
        recommended_mode=recommended_mode.value,
        confidence=confidence,
        signals=signals
    )


@router.get("/mode/history")
async def get_mode_history(
    user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> List[Dict[str, Any]]:
    """
    Get the history of mode switches for the current session.
    """
    persona_manager = PersonaManager(db)
    await persona_manager.initialize_for_user(str(user.user_id))
    
    return persona_manager.get_mode_history()


@router.post("/worldview/update")
async def update_worldview(
    request: WorldviewUpdateRequest,
    user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Dict[str, str]:
    """
    Update user's worldview preferences for persona adaptation.
    """
    # Build preferences dictionary
    preferences = {}
    
    if request.primary_tradition:
        # Validate tradition
        try:
            PhilosophicalTradition[request.primary_tradition.upper()]
            preferences["philosophy"] = request.primary_tradition.upper()
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid philosophical tradition: {request.primary_tradition}"
            )
    
    if request.communication_style:
        preferences["communication_style"] = request.communication_style
    
    if request.values_hierarchy:
        preferences["values"] = request.values_hierarchy
    
    if request.ethical_framework:
        preferences["ethics"] = request.ethical_framework
    
    if request.cultural_context:
        preferences["culture"] = request.cultural_context
    
    # TODO: Save preferences to user profile in database
    # For now, just update the current session
    persona_manager = PersonaManager(db)
    await persona_manager.initialize_for_user(str(user.user_id))
    
    # Update would happen here if we had user preference storage
    
    return {"status": "success", "message": "Worldview preferences updated"}


@router.get("/modes")
async def get_available_modes() -> Dict[str, List[Dict[str, str]]]:
    """
    Get all available persona modes with descriptions.
    """
    modes = [
        {
            "mode": "confidant",
            "name": "Confidant",
            "description": "Deep listener with empathic presence. Creates safe space for vulnerability."
        },
        {
            "mode": "mentor",
            "name": "Mentor",
            "description": "Guides skill development and mastery. Helps clarify purpose and direction."
        },
        {
            "mode": "mediator",
            "name": "Mediator", 
            "description": "Navigates conflicts with neutrality. Builds bridges between perspectives."
        },
        {
            "mode": "guardian",
            "name": "Guardian",
            "description": "Protects wellbeing proactively. Flags risks and ensures safety boundaries."
        }
    ]
    
    return {"modes": modes}


@router.get("/traditions")
async def get_philosophical_traditions() -> Dict[str, List[Dict[str, str]]]:
    """
    Get all available philosophical traditions for worldview configuration.
    """
    traditions = [
        {"key": "stoic", "name": "Stoic", "focus": "Resilience and rational wisdom"},
        {"key": "confucian", "name": "Confucian", "focus": "Harmony and relationships"},
        {"key": "sufi", "name": "Sufi", "focus": "Divine love and mystical unity"},
        {"key": "buddhist", "name": "Buddhist", "focus": "Mindfulness and compassion"},
        {"key": "humanist", "name": "Humanist", "focus": "Human dignity and potential"},
        {"key": "existentialist", "name": "Existentialist", "focus": "Freedom and authentic meaning"},
        {"key": "pragmatist", "name": "Pragmatist", "focus": "Practical solutions and results"},
        {"key": "indigenous", "name": "Indigenous", "focus": "Interconnection and sacred cycles"},
        {"key": "secular", "name": "Secular", "focus": "Reason without religious framework"},
        {"key": "spiritual", "name": "Spiritual", "focus": "Transcendent meaning and connection"}
    ]
    
    return {"traditions": traditions}