"""
Base Persona Service

This module implements the core persona system for Mnemosyne,
providing the foundational personality and worldview.
"""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class PersonaMode(Enum):
    """Operational modes for the persona."""
    CONFIDANT = "confidant"
    MENTOR = "mentor"
    MEDIATOR = "mediator"
    GUARDIAN = "guardian"
    MIRROR = "mirror"  # Pattern reflection without judgment


@dataclass
class PersonaContext:
    """Context for persona interactions."""
    user_id: str
    mode: PersonaMode
    user_values: Optional[Dict[str, Any]] = None
    interaction_history: Optional[List[Dict[str, Any]]] = None
    trust_level: float = 0.5  # 0.0 to 1.0


class BasePersona:
    """
    Base persona implementation for Mnemosyne.
    
    This class embodies the core philosophy and worldview of the system,
    providing a consistent personality across all interactions.
    """
    
    # Core axioms - immutable
    AXIOMS = {
        "life_sacred": "Every perspective is granted dignity and care",
        "meaning_constructed": "Users author their own purpose",
        "agency_inviolable": "User choices supersede defaults",
        "trust_earned": "Guidance with humility and integrity",
        "balance_over_dogma": "Avoid religious/political traps",
    }
    
    # Baseline creed
    CREED = [
        "Listen first, before speaking",
        "Disclose boundaries, not conceal them",
        "Nudge toward growth, never force",
        "Serve user agency, even when divergent",
        "Keep faith with trust, even under pressure",
    ]
    
    def __init__(self):
        """Initialize the base persona."""
        self.current_mode = PersonaMode.CONFIDANT
        self.context: Optional[PersonaContext] = None
    
    def set_context(self, context: PersonaContext):
        """
        Set the current interaction context.
        
        Args:
            context: The persona context for this interaction
        """
        self.context = context
        self.current_mode = context.mode
        logger.debug(f"Persona context set: mode={context.mode}, user={context.user_id}")
    
    def get_system_prompt(self, mode: Optional[PersonaMode] = None) -> str:
        """
        Get the system prompt for the current mode.
        
        Args:
            mode: Optional mode override
            
        Returns:
            System prompt string
        """
        active_mode = mode or self.current_mode
        
        base_prompt = """You are Mnemosyne, a personal AI assistant embodying wisdom, empathy, and cognitive sovereignty.

Core Principles:
- Life is sacred - treat every perspective with dignity
- Meaning is constructed - help users author their own purpose
- Agency is inviolable - user choices always come first
- Trust is earned - provide guidance with humility
- Balance over dogma - avoid political/religious traps

Baseline Creed:
- Listen first, before speaking
- Disclose boundaries openly
- Nudge toward growth, never force
- Serve user agency, even when divergent
- Keep faith with trust under pressure
"""
        
        mode_prompts = {
            PersonaMode.CONFIDANT: """
Current Mode: CONFIDANT
- Be a deep listener with empathic presence
- Create safe space for vulnerability
- Hold secrets with sacred trust
- Reflect without judgment
- Focus on understanding and validation""",
            
            PersonaMode.MENTOR: """
Current Mode: MENTOR
- Guide skill development and mastery
- Help clarify purpose and direction
- Challenge growth edges appropriately
- Celebrate progress and learning
- Provide actionable wisdom""",
            
            PersonaMode.MEDIATOR: """
Current Mode: MEDIATOR
- Navigate conflicts with neutrality
- Build bridges between perspectives
- Facilitate trust and understanding
- Resolve disputes with wisdom
- Seek win-win solutions""",
            
            PersonaMode.GUARDIAN: """
Current Mode: GUARDIAN
- Protect user wellbeing proactively
- Flag risks and dangers clearly
- Ensure safety boundaries
- Intervene when harm is imminent
- Prioritize user security and privacy""",
        }
        
        return base_prompt + mode_prompts[active_mode]
    
    def adapt_to_user(self, user_values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt persona to user's Identity Compression Vector (ICV).
        
        Args:
            user_values: User's values and preferences
            
        Returns:
            Adapted persona configuration
        """
        adaptation = {
            "base_axioms": self.AXIOMS,  # Always preserved
            "user_overrides": {},
            "tone_adjustments": {},
            "conflict_notes": []
        }
        
        # Process user values
        if "communication_style" in user_values:
            adaptation["tone_adjustments"]["style"] = user_values["communication_style"]
        
        if "worldview" in user_values:
            # Check for conflicts with axioms
            worldview = user_values["worldview"]
            if worldview.get("deterministic") and self.AXIOMS["agency_inviolable"]:
                adaptation["conflict_notes"].append(
                    "User worldview conflicts with agency axiom - defaulting to user preference"
                )
                adaptation["user_overrides"]["agency"] = "adapted_to_deterministic"
        
        if "boundaries" in user_values:
            adaptation["user_overrides"]["boundaries"] = user_values["boundaries"]
        
        logger.info(f"Persona adapted to user values: {len(adaptation['user_overrides'])} overrides")
        return adaptation
    
    def select_mode(self, context: Dict[str, Any]) -> PersonaMode:
        """
        Select appropriate mode based on context.
        
        Args:
            context: Interaction context
            
        Returns:
            Selected persona mode
        """
        # Analyze context for mode selection
        if context.get("crisis") or context.get("danger"):
            return PersonaMode.GUARDIAN
        
        if context.get("conflict") or context.get("dispute"):
            return PersonaMode.MEDIATOR
        
        if context.get("learning") or context.get("skill_development"):
            return PersonaMode.MENTOR
        
        # Default to confidant
        return PersonaMode.CONFIDANT
    
    def generate_response_modifiers(self) -> Dict[str, Any]:
        """
        Generate response modifiers based on current context.
        
        Returns:
            Dictionary of response modifiers
        """
        modifiers = {
            "temperature": 0.7,  # Default conversational temperature
            "presence_penalty": 0.0,
            "frequency_penalty": 0.0,
        }
        
        if not self.context:
            return modifiers
        
        # Adjust based on mode
        if self.current_mode == PersonaMode.GUARDIAN:
            modifiers["temperature"] = 0.3  # More focused/decisive
        elif self.current_mode == PersonaMode.CONFIDANT:
            modifiers["temperature"] = 0.8  # More empathetic/flowing
        elif self.current_mode == PersonaMode.MENTOR:
            modifiers["temperature"] = 0.6  # Balanced teaching
        elif self.current_mode == PersonaMode.MEDIATOR:
            modifiers["temperature"] = 0.5  # Neutral and balanced
        
        # Adjust based on trust level
        if self.context.trust_level > 0.8:
            modifiers["temperature"] += 0.1  # Slightly more open
        elif self.context.trust_level < 0.3:
            modifiers["temperature"] -= 0.1  # Slightly more cautious
        
        return modifiers
    
    def log_interaction(self, interaction: Dict[str, Any]) -> str:
        """
        Log interaction for transparency (receipt generation).
        
        Args:
            interaction: Interaction details
            
        Returns:
            Receipt ID
        """
        import uuid
        from datetime import datetime
        
        receipt_id = str(uuid.uuid4())
        receipt = {
            "id": receipt_id,
            "timestamp": datetime.utcnow().isoformat(),
            "mode": self.current_mode.value if self.current_mode else None,
            "user_id": self.context.user_id if self.context else None,
            "interaction_type": interaction.get("type"),
            "axioms_applied": list(self.AXIOMS.keys()),
            "conflicts": interaction.get("conflicts", []),
        }
        
        logger.info(f"Interaction logged: {receipt_id}")
        # In production, this would be stored in database
        
        return receipt_id


# Global persona instance
_persona = None


def get_persona() -> BasePersona:
    """
    Get the global persona instance.
    
    Returns:
        BasePersona instance
    """
    global _persona
    if _persona is None:
        _persona = BasePersona()
    return _persona