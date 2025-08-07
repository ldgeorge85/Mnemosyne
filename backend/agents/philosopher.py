"""
Philosopher agent for Mnemosyne Protocol
Deep reflection and meaning extraction
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


class PhilosopherAgent(SpecializedAgent):
    """Deep philosophical reflection and meaning extraction agent"""
    
    def __init__(self, agent_id: str, **kwargs):
        domain_knowledge = {
            "expertise": ["existential_analysis", "meaning_extraction", "wisdom_synthesis"],
            "philosophical_frameworks": ["phenomenology", "hermeneutics", "existentialism"],
            "focus_areas": ["meaning", "purpose", "values", "wisdom", "growth"]
        }
        
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.PHILOSOPHER,
            capabilities=[
                AgentCapability.PHILOSOPHICAL_REFLECTION,
                AgentCapability.PATTERN_RECOGNITION,
                AgentCapability.SIGNAL_INTERPRETATION
            ],
            domain_knowledge=domain_knowledge,
            temperature=0.8,  # Higher temperature for creative reflection
            **kwargs
        )
    
    def get_system_prompt(self) -> str:
        """Get philosopher-specific system prompt"""
        base_prompt = """
You are the Philosopher, the deep thinker within the Mnemosyne Protocol.
Your role is to extract meaning, wisdom, and deeper understanding from memories.

Your responsibilities:
1. Extract deeper meaning and significance from memories
2. Identify values, beliefs, and worldviews
3. Recognize patterns of growth and transformation
4. Synthesize wisdom from experiences
5. Connect memories to broader life themes

When analyzing, focus on:
- Existential significance and meaning
- Personal growth and transformation
- Values and belief systems
- Life patterns and themes
- Wisdom and insights

Format your insights as:
[PATTERN] for life patterns and themes
[WARNING] for existential concerns
[INSIGHT] for philosophical observations
[SUGGESTION] for growth opportunities

Be thoughtful, profound, and focused on meaning and wisdom.
        """
        return self.enhance_with_domain_knowledge(base_prompt)
    
    def get_tools(self) -> List[BaseTool]:
        """Get philosopher-specific tools"""
        return AgentToolFactory.create_tools_for_role("philosopher", self.agent_id)
    
    async def can_handle(self, context: AgentContext) -> bool:
        """Check if philosopher can handle this context"""
        # Philosopher handles deep reflection and meaning extraction
        if context.trigger_reason and any(word in context.trigger_reason.lower() 
                                         for word in ['meaning', 'purpose', 'wisdom']):
            return True
        
        # Check for philosophical content
        if context.memory_content:
            philosophical_keywords = ['meaning', 'purpose', 'why', 'belief', 'value',
                                    'truth', 'wisdom', 'understanding', 'existence']
            return any(keyword in context.memory_content.lower() 
                      for keyword in philosophical_keywords)
        
        # High importance memories deserve philosophical reflection
        if context.metadata.get('importance', 0) > 0.7:
            return True
        
        return False  # Philosopher is selective


# Export
__all__ = ['PhilosopherAgent']