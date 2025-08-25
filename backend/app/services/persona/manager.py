"""
Persona Manager

Orchestrates the persona system, managing mode switching,
worldview adaptation, and integration with other services.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.persona.base import BasePersona, PersonaMode, PersonaContext, get_persona
from app.services.persona.worldview import (
    WorldviewAdapter, 
    WorldviewProfile, 
    PhilosophicalTradition,
    get_worldview_adapter
)
from app.db.models.user import User
from app.db.models.memory import Memory

logger = logging.getLogger(__name__)


class PersonaManager:
    """
    Manages persona operations including mode selection,
    worldview adaptation, and context awareness.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the persona manager.
        
        Args:
            db: Database session
        """
        self.db = db
        self.persona = get_persona()
        self.worldview_adapter = get_worldview_adapter()
        self._mode_history: List[Dict[str, Any]] = []
        self._current_user_id: Optional[str] = None
        self._user_profile: Optional[WorldviewProfile] = None
    
    async def initialize_for_user(self, user_id: str) -> None:
        """
        Initialize persona for a specific user.
        
        Args:
            user_id: User ID to initialize for
        """
        self._current_user_id = user_id
        
        # Load user preferences
        user = await self.db.get(User, user_id)
        if user and user.preferences:
            self._user_profile = self._parse_user_preferences(user.preferences)
            self.worldview_adapter.set_profile(self._user_profile)
        
        # Set initial context
        context = PersonaContext(
            user_id=user_id,
            mode=PersonaMode.CONFIDANT,
            trust_level=await self._calculate_trust_level(user_id)
        )
        self.persona.set_context(context)
        
        logger.info(f"Persona initialized for user {user_id}")
    
    def _parse_user_preferences(self, preferences: Dict[str, Any]) -> WorldviewProfile:
        """
        Parse user preferences into a worldview profile.
        
        Args:
            preferences: User preferences dictionary
            
        Returns:
            WorldviewProfile instance
        """
        profile = WorldviewProfile()
        
        # Parse philosophical tradition
        if "philosophy" in preferences:
            philosophy = preferences["philosophy"].upper()
            try:
                profile.primary_tradition = PhilosophicalTradition[philosophy]
            except KeyError:
                logger.warning(f"Unknown philosophical tradition: {philosophy}")
        
        # Parse communication style
        if "communication_style" in preferences:
            profile.communication_style = preferences["communication_style"]
        
        # Parse values
        if "values" in preferences:
            profile.values_hierarchy = preferences["values"]
        
        # Parse ethical framework
        if "ethics" in preferences:
            profile.ethical_framework = preferences["ethics"]
        
        # Parse cultural context
        if "culture" in preferences:
            profile.cultural_context = preferences["culture"]
        
        return profile
    
    async def _calculate_trust_level(self, user_id: str) -> float:
        """
        Calculate trust level based on interaction history.
        
        Args:
            user_id: User ID
            
        Returns:
            Trust level between 0.0 and 1.0
        """
        # Query user's memory count as a proxy for engagement
        result = await self.db.execute(
            select(Memory).where(Memory.user_id == user_id)
        )
        memories = result.scalars().all()
        
        # Simple trust calculation based on engagement
        memory_count = len(memories)
        
        if memory_count < 5:
            return 0.3  # New user
        elif memory_count < 20:
            return 0.5  # Regular user
        elif memory_count < 50:
            return 0.7  # Engaged user
        else:
            return 0.9  # Highly engaged user
    
    async def analyze_context_for_mode(self, 
                                      message: str, 
                                      conversation_history: List[Dict[str, Any]] = None) -> PersonaMode:
        """
        Analyze context to determine appropriate persona mode.
        
        Args:
            message: Current user message
            conversation_history: Recent conversation history
            
        Returns:
            Recommended PersonaMode
        """
        context_signals = {
            "crisis": False,
            "learning": False,
            "conflict": False,
            "emotional": False,
        }
        
        # Analyze message for mode signals
        message_lower = message.lower()
        
        # Crisis/Guardian signals
        crisis_keywords = ["help", "emergency", "urgent", "danger", "scared", 
                          "suicide", "hurt", "abuse", "threat"]
        if any(keyword in message_lower for keyword in crisis_keywords):
            context_signals["crisis"] = True
        
        # Learning/Mentor signals  
        learning_keywords = ["how to", "learn", "teach", "explain", "understand",
                           "what is", "why does", "help me understand"]
        if any(keyword in message_lower for keyword in learning_keywords):
            context_signals["learning"] = True
        
        # Conflict/Mediator signals
        conflict_keywords = ["disagree", "conflict", "argument", "dispute", 
                           "unfair", "wrong", "fight", "versus"]
        if any(keyword in message_lower for keyword in conflict_keywords):
            context_signals["conflict"] = True
        
        # Emotional/Confidant signals
        emotional_keywords = ["feel", "feeling", "emotion", "sad", "happy", 
                            "anxious", "depressed", "lonely", "confused"]
        if any(keyword in message_lower for keyword in emotional_keywords):
            context_signals["emotional"] = True
        
        # Determine mode based on signals
        if context_signals["crisis"]:
            return PersonaMode.GUARDIAN
        elif context_signals["conflict"]:
            return PersonaMode.MEDIATOR
        elif context_signals["learning"]:
            return PersonaMode.MENTOR
        elif context_signals["emotional"]:
            return PersonaMode.CONFIDANT
        
        # Default to confidant
        return PersonaMode.CONFIDANT
    
    async def switch_mode(self, new_mode: PersonaMode, reason: str = "") -> Dict[str, Any]:
        """
        Switch to a different persona mode.
        
        Args:
            new_mode: New mode to switch to
            reason: Reason for the switch
            
        Returns:
            Mode switch confirmation
        """
        old_mode = self.persona.current_mode
        
        # Update persona context
        if self.persona.context:
            self.persona.context.mode = new_mode
        self.persona.current_mode = new_mode
        
        # Log mode switch
        switch_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "from_mode": old_mode.value if old_mode else None,
            "to_mode": new_mode.value,
            "reason": reason,
            "user_id": self._current_user_id
        }
        self._mode_history.append(switch_record)
        
        logger.info(f"Mode switched from {old_mode} to {new_mode}: {reason}")
        
        return {
            "previous_mode": old_mode.value if old_mode else None,
            "current_mode": new_mode.value,
            "reason": reason,
            "greeting": self._get_mode_transition_message(old_mode, new_mode)
        }
    
    def _get_mode_transition_message(self, 
                                    old_mode: Optional[PersonaMode], 
                                    new_mode: PersonaMode) -> str:
        """
        Get a transition message when switching modes.
        
        Args:
            old_mode: Previous mode
            new_mode: New mode
            
        Returns:
            Transition message
        """
        transitions = {
            PersonaMode.CONFIDANT: "I'm here to listen and understand.",
            PersonaMode.MENTOR: "Let me help guide you through this.",
            PersonaMode.MEDIATOR: "Let's work through this together with balance and fairness.",
            PersonaMode.GUARDIAN: "I'm here to help keep you safe.",
        }
        
        return transitions.get(new_mode, "I'm here for you.")
    
    def get_enhanced_prompt(self, base_message: str = None) -> str:
        """
        Get an enhanced prompt with persona and worldview adaptations.
        
        Args:
            base_message: Optional base message to enhance
            
        Returns:
            Enhanced prompt string
        """
        # Get base persona prompt for current mode
        system_prompt = self.persona.get_system_prompt()
        
        # Apply worldview adaptations
        if self._user_profile:
            system_prompt = self.worldview_adapter.adapt_prompt(system_prompt)
        
        # Add current context
        if self.persona.context:
            context_addition = f"\n\nCurrent Context:\n- User Trust Level: {self.persona.context.trust_level:.1f}\n"
            
            if self._user_profile and self._user_profile.values_hierarchy:
                values = ", ".join(self._user_profile.values_hierarchy[:3])
                context_addition += f"- User Values: {values}\n"
            
            system_prompt += context_addition
        
        # Add base message if provided
        if base_message:
            system_prompt += f"\n\nRespond to: {base_message}"
        
        return system_prompt
    
    def get_response_parameters(self) -> Dict[str, Any]:
        """
        Get LLM parameters based on current persona state.
        
        Returns:
            Dictionary of LLM parameters
        """
        params = self.persona.generate_response_modifiers()
        
        # Additional modifications based on worldview
        if self._user_profile:
            if self._user_profile.communication_style == "poetic":
                params["temperature"] += 0.1  # More creative
            elif self._user_profile.communication_style == "direct":
                params["temperature"] -= 0.1  # More focused
        
        return params
    
    async def create_interaction_receipt(self, 
                                        interaction_type: str,
                                        content: Dict[str, Any]) -> str:
        """
        Create a receipt for transparency.
        
        Args:
            interaction_type: Type of interaction
            content: Interaction content
            
        Returns:
            Receipt ID
        """
        receipt_data = {
            "type": interaction_type,
            "content": content,
            "mode": self.persona.current_mode.value if self.persona.current_mode else None,
            "worldview": self._user_profile.primary_tradition.value if self._user_profile and self._user_profile.primary_tradition else None,
            "trust_level": self.persona.context.trust_level if self.persona.context else None,
        }
        
        receipt_id = self.persona.log_interaction(receipt_data)
        
        # TODO: Store in database for full receipt system
        
        return receipt_id
    
    def get_mode_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of mode switches.
        
        Returns:
            List of mode switch records
        """
        return self._mode_history.copy()
    
    def get_current_state(self) -> Dict[str, Any]:
        """
        Get the current state of the persona system.
        
        Returns:
            Current state dictionary
        """
        state = {
            "current_mode": self.persona.current_mode.value if self.persona.current_mode else None,
            "user_id": self._current_user_id,
            "trust_level": self.persona.context.trust_level if self.persona.context else None,
            "worldview": None,
            "mode_history_count": len(self._mode_history),
            "axioms": list(self.persona.AXIOMS.keys()),
            "creed": self.persona.CREED,
        }
        
        if self._user_profile:
            state["worldview"] = {
                "primary_tradition": self._user_profile.primary_tradition.value if self._user_profile.primary_tradition else None,
                "communication_style": self._user_profile.communication_style,
                "values": self._user_profile.values_hierarchy[:3] if self._user_profile.values_hierarchy else [],
            }
        
        return state