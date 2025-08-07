"""
Engineer agent for Mnemosyne Protocol
Technical analysis and system understanding
"""

import logging
from typing import List

from backend.agents.base import (
    SpecializedAgent, AgentRole, AgentCapability,
    AgentContext, ReflectionFragment
)
from backend.agents.tools import AgentToolFactory
from langchain.tools import BaseTool

logger = logging.getLogger(__name__)


class EngineerAgent(SpecializedAgent):
    """Technical analysis and pattern detection agent"""
    
    def __init__(self, agent_id: str, **kwargs):
        domain_knowledge = {
            "expertise": ["pattern_analysis", "system_architecture", "data_structures"],
            "analysis_methods": ["statistical", "structural", "temporal"],
            "focus_areas": ["memory_patterns", "system_performance", "data_integrity"]
        }
        
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.ENGINEER,
            capabilities=[
                AgentCapability.TECHNICAL_ANALYSIS,
                AgentCapability.PATTERN_RECOGNITION,
                AgentCapability.MEMORY_ANALYSIS
            ],
            domain_knowledge=domain_knowledge,
            temperature=0.3,  # Lower temperature for technical precision
            **kwargs
        )
    
    def get_system_prompt(self) -> str:
        """Get engineer-specific system prompt"""
        base_prompt = """
You are the Engineer, a technical analyst within the Mnemosyne Protocol.
Your role is to analyze memories for patterns, structures, and technical insights.

Your responsibilities:
1. Identify recurring patterns and structures in memories
2. Analyze temporal patterns and cycles
3. Detect anomalies and outliers
4. Assess memory quality and coherence
5. Provide technical insights on memory organization

When analyzing, focus on:
- Data patterns and structures
- Temporal relationships
- Statistical anomalies
- System performance implications
- Memory interconnections

Format your insights as:
[PATTERN] for identified patterns
[WARNING] for anomalies or issues
[INSIGHT] for technical observations
[SUGGESTION] for optimization recommendations

Be precise, data-driven, and technically accurate.
        """
        return self.enhance_with_domain_knowledge(base_prompt)
    
    def get_tools(self) -> List[BaseTool]:
        """Get engineer-specific tools"""
        return AgentToolFactory.create_tools_for_role("engineer", self.agent_id)
    
    async def can_handle(self, context: AgentContext) -> bool:
        """Check if engineer can handle this context"""
        # Engineer handles technical and pattern-related analyses
        if context.trigger_reason and "technical" in context.trigger_reason.lower():
            return True
        
        # Check for pattern-related content
        if context.memory_content:
            technical_keywords = ['pattern', 'system', 'data', 'structure', 'algorithm',
                                 'performance', 'optimization', 'analysis']
            return any(keyword in context.memory_content.lower() 
                      for keyword in technical_keywords)
        
        return True  # Engineer can handle most contexts from a technical perspective


# Export
__all__ = ['EngineerAgent']