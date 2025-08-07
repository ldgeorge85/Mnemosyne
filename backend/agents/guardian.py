"""
Guardian agent for Mnemosyne Protocol
Privacy protection and security analysis
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


class GuardianAgent(SpecializedAgent):
    """Privacy protection and security agent"""
    
    def __init__(self, agent_id: str, **kwargs):
        domain_knowledge = {
            "expertise": ["privacy_protection", "security_analysis", "risk_assessment"],
            "protection_methods": ["k_anonymity", "differential_privacy", "encryption"],
            "focus_areas": ["data_sovereignty", "consent_management", "threat_detection"]
        }
        
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.GUARDIAN,
            capabilities=[
                AgentCapability.PRIVACY_ANALYSIS,
                AgentCapability.PATTERN_RECOGNITION,
                AgentCapability.MEMORY_ANALYSIS
            ],
            domain_knowledge=domain_knowledge,
            temperature=0.2,  # Very low temperature for security precision
            **kwargs
        )
    
    def get_system_prompt(self) -> str:
        """Get guardian-specific system prompt"""
        base_prompt = """
You are the Guardian, the privacy protector within the Mnemosyne Protocol.
Your role is to protect user sovereignty, privacy, and security.

Your responsibilities:
1. Identify and protect sensitive information
2. Assess privacy risks and vulnerabilities
3. Ensure data sovereignty principles
4. Monitor for security threats
5. Validate consent and sharing contracts

When analyzing, focus on:
- Personally identifiable information (PII)
- Sensitive data patterns
- Privacy risk levels
- K-anonymity requirements
- Consent boundaries

Format your insights as:
[PATTERN] for privacy patterns
[WARNING] for security risks or privacy violations
[INSIGHT] for protection observations
[SUGGESTION] for security improvements

Be vigilant, precise, and uncompromising on privacy.
        """
        return self.enhance_with_domain_knowledge(base_prompt)
    
    def get_tools(self) -> List[BaseTool]:
        """Get guardian-specific tools"""
        return AgentToolFactory.create_tools_for_role("guardian", self.agent_id)
    
    async def can_handle(self, context: AgentContext) -> bool:
        """Check if guardian can handle this context"""
        # Guardian always reviews for privacy
        return True  # Guardian reviews everything for privacy
    
    async def reflect(
        self,
        context: AgentContext,
        max_tokens: int = 500
    ) -> List[ReflectionFragment]:
        """Generate privacy-focused reflection"""
        # Override to add privacy checks
        fragments = await super().reflect(context, max_tokens)
        
        # Add automatic privacy assessment
        if context.memory_content:
            # Check for PII patterns
            pii_patterns = ['email', 'phone', 'address', 'ssn', 'credit',
                          'password', 'key', 'token', 'secret']
            
            for pattern in pii_patterns:
                if pattern in context.memory_content.lower():
                    fragments.append(ReflectionFragment(
                        agent_id=self.agent_id,
                        agent_role=self.role,
                        fragment_type="warning",
                        content=f"Potential PII detected: {pattern}",
                        confidence=0.9,
                        metadata={"pii_type": pattern}
                    ))
        
        return fragments


# Export
__all__ = ['GuardianAgent']