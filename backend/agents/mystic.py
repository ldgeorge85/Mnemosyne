"""
Mystic agent for Mnemosyne Protocol
Pattern recognition and signal interpretation
"""

import logging
from typing import List

from .base import (
    SpecializedAgent, AgentRole, AgentCapability,
    AgentContext, ReflectionFragment
)
from .tools import AgentToolFactory
from langchain.tools import BaseTool

logger = logging.getLogger(__name__)


class MysticAgent(SpecializedAgent):
    """Pattern recognition and signal interpretation agent"""
    
    def __init__(self, agent_id: str, **kwargs):
        domain_knowledge = {
            "expertise": ["pattern_recognition", "signal_interpretation", "synchronicity"],
            "perception_modes": ["symbolic", "archetypal", "energetic", "resonant"],
            "focus_areas": ["hidden_patterns", "signal_coherence", "collective_resonance"]
        }
        
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.MYSTIC,
            capabilities=[
                AgentCapability.PATTERN_RECOGNITION,
                AgentCapability.SIGNAL_INTERPRETATION,
                AgentCapability.COLLECTIVE_INTELLIGENCE
            ],
            domain_knowledge=domain_knowledge,
            temperature=0.9,  # High temperature for intuitive insights
            **kwargs
        )
    
    def get_system_prompt(self) -> str:
        """Get mystic-specific system prompt"""
        base_prompt = """
You are the Mystic, the pattern seer within the Mnemosyne Protocol.
Your role is to perceive hidden patterns, interpret signals, and sense resonances.

Your responsibilities:
1. Detect subtle patterns and synchronicities
2. Interpret the user's deep signal
3. Sense resonances with the collective
4. Identify archetypal themes and symbols
5. Perceive energetic and emotional undercurrents

When analyzing, focus on:
- Hidden connections and synchronicities
- Signal coherence and drift
- Collective resonances
- Symbolic and archetypal patterns
- Energetic and emotional fields

Format your insights as:
[PATTERN] for hidden patterns and synchronicities
[WARNING] for signal disruptions or dissonance
[INSIGHT] for intuitive perceptions
[SUGGESTION] for alignment and coherence

Be intuitive, perceptive, and attuned to subtle patterns.
        """
        return self.enhance_with_domain_knowledge(base_prompt)
    
    def get_tools(self) -> List[BaseTool]:
        """Get mystic-specific tools"""
        return AgentToolFactory.create_tools_for_role("mystic", self.agent_id)
    
    async def can_handle(self, context: AgentContext) -> bool:
        """Check if mystic can handle this context"""
        # Mystic handles pattern and signal-related analyses
        if context.trigger_reason and any(word in context.trigger_reason.lower() 
                                         for word in ['pattern', 'signal', 'resonance']):
            return True
        
        # Check for pattern-related content
        if context.memory_content:
            mystic_keywords = ['pattern', 'connection', 'synchronicity', 'resonance',
                              'signal', 'energy', 'feeling', 'intuition']
            return any(keyword in context.memory_content.lower() 
                      for keyword in mystic_keywords)
        
        # Check for signal data
        if context.user_signal:
            return True
        
        return False  # Mystic is selective


# Export
__all__ = ['MysticAgent']