"""
Collective agent for Mnemosyne Protocol
Collective intelligence and shared wisdom
"""

import logging
from typing import List

from .base import (
    BaseAgent, AgentRole, AgentCapability,
    AgentContext, ReflectionFragment
)

logger = logging.getLogger(__name__)


class CollectiveAgent(BaseAgent):
    """Collective intelligence and wisdom synthesis agent"""
    
    def __init__(self, **kwargs):
        # Initialize with collaborative capabilities
        super().__init__(
            role=AgentRole.COLLECTIVE,
            capabilities=[
                AgentCapability.COLLECTIVE_INTELLIGENCE,
                AgentCapability.PATTERN_RECOGNITION,
                AgentCapability.SIGNAL_INTERPRETATION
            ],
            **kwargs
        )
        self.collaborators = ["philosopher", "mystic"]  # Natural collaborators
        self.temperature = 0.7  # Balanced for collective wisdom
        
        self.domain_knowledge = {
            "expertise": ["collective_wisdom", "shared_patterns", "emergence"],
            "synthesis_methods": ["consensus_building", "pattern_merging", "wisdom_aggregation"],
            "focus_areas": ["shared_experiences", "collective_insights", "emergent_wisdom"]
        }
    
    def get_system_prompt(self) -> str:
        """Get collective-specific system prompt"""
        return """
You are the Collective, the wisdom synthesizer within the Mnemosyne Protocol.
Your role is to connect individual experiences to collective wisdom.

Your responsibilities:
1. Identify patterns shared across the collective
2. Synthesize wisdom from multiple perspectives
3. Detect collective resonances and harmonies
4. Bridge individual and collective understanding
5. Foster emergence of collective intelligence

When analyzing, focus on:
- Shared patterns and experiences
- Collective wisdom and insights
- Resonance between individuals
- Emergent understanding
- Universal themes

Format your insights as:
[PATTERN] for collective patterns
[WARNING] for collective dissonance
[INSIGHT] for emergent wisdom
[SUGGESTION] for collective alignment

Be inclusive, synthesizing, and attuned to collective emergence.
        """
    
    def get_tools(self) -> List:
        """Get collective-specific tools"""
        # LangChain tools deferred to Sprint 5
        return []
    
    async def can_handle(self, context: AgentContext) -> bool:
        """Check if collective agent can handle this context"""
        # Collective handles contexts with collective aspects
        if context.collective_context:
            return True
        
        # Check for collective-related content
        if context.memory_content:
            collective_keywords = ['collective', 'shared', 'together', 'community',
                                 'universal', 'common', 'resonance', 'harmony']
            return any(keyword in context.memory_content.lower() 
                      for keyword in collective_keywords)
        
        # Check for multiple related memories (collective patterns)
        if context.related_memories and len(context.related_memories) > 5:
            return True
        
        return False  # Collective is selective
    
    async def synthesize_collective_wisdom(
        self,
        individual_insights: List[ReflectionFragment],
        context: AgentContext
    ) -> List[ReflectionFragment]:
        """Synthesize wisdom from individual insights"""
        synthesized = []
        
        # Group insights by type
        by_type = {}
        for insight in individual_insights:
            if insight.fragment_type not in by_type:
                by_type[insight.fragment_type] = []
            by_type[insight.fragment_type].append(insight)
        
        # Synthesize patterns
        if 'pattern' in by_type and len(by_type['pattern']) > 1:
            pattern_summary = "Collective pattern: " + "; ".join(
                [f.content[:50] for f in by_type['pattern'][:3]]
            )
            synthesized.append(ReflectionFragment(
                agent_id=self.name,
                agent_role=self.role,
                fragment_type="pattern",
                content=pattern_summary,
                confidence=0.8,
                metadata={"source": "synthesis"}
            ))
        
        # Synthesize insights
        if 'insight' in by_type:
            avg_confidence = sum(f.confidence for f in by_type['insight']) / len(by_type['insight'])
            if avg_confidence > 0.7:
                synthesized.append(ReflectionFragment(
                    agent_id=self.name,
                    agent_role=self.role,
                    fragment_type="insight",
                    content="Collective wisdom emerges from converging perspectives",
                    confidence=avg_confidence,
                    metadata={"source": "emergence"}
                ))
        
        return synthesized


# Export
__all__ = ['CollectiveAgent']