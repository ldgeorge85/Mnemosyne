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
from app.services.persona.mirror import MirrorPersona, create_mirror_persona, PatternDimension
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
        self.mirror_persona = create_mirror_persona()  # Separate Mirror instance
        self.worldview_adapter = get_worldview_adapter()
        self._mode_history: List[Dict[str, Any]] = []
        self._current_user_id: Optional[str] = None
        self._user_profile: Optional[WorldviewProfile] = None
        self._mirror_mode_active = False
    
    async def initialize_for_user(self, user_id: str) -> None:
        """
        Initialize persona for a specific user.
        
        Args:
            user_id: User ID to initialize for
        """
        self._current_user_id = user_id
        
        # Load user preferences (if available)
        user = await self.db.get(User, user_id)
        if user and hasattr(user, 'preferences') and user.preferences:
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
            "reflection": False,
        }
        
        # Analyze message for mode signals
        message_lower = message.lower()
        
        # Mirror/Reflection signals
        reflection_keywords = ["pattern", "observe", "reflect", "mirror", "notice",
                             "tendency", "behavior", "habit", "recurring", "spectrum"]
        if any(keyword in message_lower for keyword in reflection_keywords):
            context_signals["reflection"] = True
        
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
        elif context_signals["reflection"]:
            return PersonaMode.MIRROR
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
    
    
    async def select_mode_llm(
        self, 
        query: str, 
        context: Dict[str, Any]
    ) -> PersonaMode:
        """
        Select persona mode using LLM reasoning instead of keywords.
        
        Args:
            query: User's query
            context: Current context
            
        Returns:
            Selected PersonaMode
        """
        # Import here to avoid circular dependency
        from app.services.llm.service import LLMService
        from app.core.config import settings
        
        llm_service = LLMService()
        
        # Load persona selection prompt
        import os
        prompt_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "prompts", "agentic_persona_selection.txt"
        )
        
        try:
            with open(prompt_path, "r") as f:
                prompt_template = f.read()
        except FileNotFoundError:
            logger.error(f"CRITICAL: Persona selection prompt not found at {prompt_path}")
            raise FileNotFoundError(f"Required prompt file missing: {prompt_path}")
        
        # Build context for LLM
        mood_indicators = context.get("mood_indicators", {})
        recent_context = {
            "memories_count": len(context.get("memories", [])),
            "recent_modes": [h["to_mode"] for h in self._mode_history[-5:]],
            "trust_level": self.persona.context.trust_level if self.persona.context else 0.5
        }
        
        prompt = prompt_template.format(
            query=query,
            current_mode=self.persona.current_mode.value if self.persona.current_mode else "confidant",
            context=json.dumps(recent_context),
            mood_indicators=json.dumps(mood_indicators)
        )
        
        try:
            # Get LLM response (limited tokens for efficiency)
            response = await llm_service.complete(
                prompt=prompt,
                system="You are a persona mode selector for the Mnemosyne Protocol.",
                max_tokens=settings.OPENAI_MAX_TOKENS_REASONING
            )
            
            # Try to parse JSON response
            content = response.get("content", "{}")
            try:
                result = json.loads(content)
                selected_mode = result.get("selected_mode", "confidant").lower()
                confidence = result.get("confidence", 0.5)
                reasoning = result.get("reasoning", "")
            except json.JSONDecodeError:
                # Fallback: try to extract mode from plain text response
                logger.warning(f"LLM returned non-JSON response, attempting text parsing: {content[:200]}")
                content_lower = content.lower()
                
                # Look for mode keywords in the response
                if "mentor" in content_lower:
                    selected_mode = "mentor"
                elif "guardian" in content_lower:
                    selected_mode = "guardian"
                elif "mediator" in content_lower:
                    selected_mode = "mediator"
                elif "mirror" in content_lower:
                    selected_mode = "mirror"
                else:
                    selected_mode = "confidant"
                    
                confidence = 0.7  # Default confidence for text parsing
                reasoning = content[:200] if content else "Parsed from plain text response"
            
            logger.info(f"LLM selected {selected_mode} mode with {confidence:.2f} confidence: {reasoning}")
            
            # Convert to PersonaMode enum
            mode_map = {
                "confidant": PersonaMode.CONFIDANT,
                "mentor": PersonaMode.MENTOR,
                "mediator": PersonaMode.MEDIATOR,
                "guardian": PersonaMode.GUARDIAN,
                "mirror": PersonaMode.MIRROR
            }
            
            return mode_map.get(selected_mode, PersonaMode.CONFIDANT)
            
        except Exception as e:
            logger.error(f"LLM persona selection failed: {e}")
            raise RuntimeError(f"Failed to select persona mode: {e}")
    
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
            PersonaMode.MIRROR: "I'll observe and reflect your patterns without judgment.",
        }
        
        return transitions.get(new_mode, "I'm here for you.")
    
    def get_llm_config(self, model_profile: Optional[str] = None) -> Dict[str, Any]:
        """
        Get LLM configuration for current persona mode.
        
        Args:
            model_profile: Optional model profile (standard, reasoning_channel, etc.)
            
        Returns:
            Dictionary of LLM parameters
        """
        from app.core.persona_config import get_llm_config_for_persona
        
        if not self.persona.current_mode:
            return {"temperature": 0.7}  # Default
            
        return get_llm_config_for_persona(
            self.persona.current_mode.value,
            model_profile
        )
    
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
        
        # Check if we need reasoning level prefix
        llm_config = self.get_llm_config()
        if llm_config.get("system_prompt_prefix"):
            system_prompt = llm_config["system_prompt_prefix"] + system_prompt
        
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
    
    # Mirror mode specific methods
    async def observe_user_pattern(self, 
                                  user_id: str,
                                  interaction: Dict[str, Any]) -> None:
        """
        Observe user patterns in Mirror mode.
        
        Args:
            user_id: User to observe
            interaction: Interaction data
        """
        if self._mirror_mode_active or self.persona.current_mode == PersonaMode.MIRROR:
            # Observe patterns
            patterns = self.mirror_persona.observe_interaction(interaction)
            
            # Update observed patterns
            for dimension, value in patterns.items():
                self.mirror_persona.update_patterns(dimension, value)
            
            # Log observation for transparency
            receipt = self.mirror_persona.generate_observation_receipt(user_id)
            logger.info(f"Pattern observation receipt: {receipt}")
    
    def get_mirror_reflections(self, user_id: str) -> List[str]:
        """
        Get neutral reflections about observed patterns.
        
        Args:
            user_id: User whose patterns to reflect
            
        Returns:
            List of neutral observations
        """
        if self._mirror_mode_active or self.persona.current_mode == PersonaMode.MIRROR:
            return self.mirror_persona.reflect_patterns(user_id)
        return []
    
    def get_mirror_prompt(self) -> str:
        """
        Get the Mirror mode system prompt.
        
        Returns:
            Mirror mode prompt
        """
        return self.mirror_persona.get_mirror_prompt()
    
    def reset_mirror_observations(self):
        """Reset all Mirror mode observations."""
        self.mirror_persona.reset_observations()
        logger.info("Mirror mode observations reset")