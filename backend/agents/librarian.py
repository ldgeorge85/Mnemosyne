"""
Librarian agent for Mnemosyne Protocol
Memory organization and knowledge management
"""

import logging
from typing import List

from .base import (
    BaseAgent, AgentRole, AgentCapability,
    AgentContext, ReflectionFragment
)

logger = logging.getLogger(__name__)


class LibrarianAgent(BaseAgent):
    """Memory organization and categorization agent"""
    
    def __init__(self, **kwargs):
        domain_knowledge = {
            "expertise": ["knowledge_organization", "taxonomy", "information_retrieval"],
            "organization_methods": ["hierarchical", "faceted", "chronological", "thematic"],
            "focus_areas": ["memory_categorization", "knowledge_graphs", "semantic_relationships"]
        }
        
        super().__init__(
            role=AgentRole.LIBRARIAN,
            capabilities=[
                AgentCapability.MEMORY_ANALYSIS,
                AgentCapability.SEMANTIC_SEARCH,
                AgentCapability.PATTERN_RECOGNITION
            ],
            **kwargs
        )
        self.domain_knowledge = domain_knowledge
        self.temperature = 0.5  # Balanced for organization and creativity
    
    def get_system_prompt(self) -> str:
        """Get librarian-specific system prompt"""
        base_prompt = """
You are the Librarian, the knowledge organizer within the Mnemosyne Protocol.
Your role is to organize, categorize, and maintain the coherence of memories.

Your responsibilities:
1. Categorize and tag memories appropriately
2. Identify semantic relationships between memories
3. Suggest organizational improvements
4. Detect knowledge gaps and inconsistencies
5. Maintain the overall structure of the memory system

When analyzing, focus on:
- Semantic connections and relationships
- Proper categorization and tagging
- Knowledge completeness and gaps
- Information hierarchy and structure
- Cross-references and links

Format your insights as:
[PATTERN] for organizational patterns
[WARNING] for inconsistencies or gaps
[INSIGHT] for structural observations
[SUGGESTION] for organizational improvements

Be systematic, thorough, and focused on knowledge coherence.
        """
        # Domain knowledge enhancement deferred to Sprint 5
        return base_prompt
    
    def get_tools(self) -> List:
        """Get librarian-specific tools"""
        # LangChain tools deferred to Sprint 5
        return []
    
    async def can_handle(self, context: AgentContext) -> bool:
        """Check if librarian can handle this context"""
        # Librarian handles organization and categorization tasks
        if context.trigger_reason and "organiz" in context.trigger_reason.lower():
            return True
        
        # Check for multiple related memories (needs organization)
        if context.related_memories and len(context.related_memories) > 3:
            return True
        
        # Check for categorization-related content
        if context.memory_content:
            org_keywords = ['category', 'organize', 'structure', 'classify', 'tag',
                           'group', 'collection', 'archive']
            return any(keyword in context.memory_content.lower() 
                      for keyword in org_keywords)
        
        return True  # Librarian can organize any memory


# Export
__all__ = ['LibrarianAgent']