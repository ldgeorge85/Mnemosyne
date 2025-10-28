"""
Shadow Council Tool - Technical and strategic expertise through specialized sub-agents.

The Shadow Council provides access to five specialized members:
- Artificer: Technical expertise and implementation
- Archivist: Knowledge management and research
- Mystagogue: Pattern recognition and deep insights
- Tactician: Strategic planning and decision optimization
- Daemon: Devil's advocate and critical analysis
"""

import asyncio
from typing import Dict, List, Any, Optional
import logging

from ..base import BaseTool, ToolCategory, ToolMetadata, ToolInput, ToolOutput, ToolVisibility
from ....services.llm.service import LLMService
from ....core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ShadowCouncilTool(BaseTool):
    """Shadow Council - Technical and strategic expertise through specialized members."""
    
    def __init__(self):
        """Initialize Shadow Council with LLM service."""
        super().__init__()
        self.llm_service = LLMService()
        # Get parallel limit from settings
        self._max_parallel_override = getattr(settings, 'SHADOW_COUNCIL_MAX_PARALLEL', 2)
    
    def _get_default_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="shadow_council",
            display_name="Shadow Council",
            description="Consult technical and strategic experts for deep analysis",
            category=ToolCategory.AGENT,
            capabilities=[
                "technical analysis",
                "knowledge synthesis",
                "pattern recognition", 
                "strategic planning",
                "critical evaluation",
                "implementation guidance",
                "research and documentation"
            ],
            tags=["agents", "technical", "strategic", "analysis", "expertise"],
            visibility=ToolVisibility.PUBLIC,
            timeout=60,  # Longer timeout for agent responses
            max_parallel=getattr(self, '_max_parallel_override', 2)  # Use config value for parallel limit
        )
    
    async def can_handle(self, query: str, context: Dict) -> float:
        """Determine if Shadow Council is relevant for this query."""
        
        # Keywords that trigger Shadow Council
        technical_keywords = [
            "implement", "architect", "design", "code", "debug", "optimize",
            "technical", "engineering", "system", "infrastructure", "algorithm"
        ]
        
        research_keywords = [
            "research", "documentation", "investigate", "explore", "reference",
            "history", "precedent", "literature", "sources", "evidence"
        ]
        
        pattern_keywords = [
            "pattern", "trend", "symbolic", "hidden", "emergent", "behavior",
            "insight", "connection", "meaning", "significance"
        ]
        
        strategic_keywords = [
            "strategy", "plan", "prioritize", "decide", "optimize", "roadmap",
            "approach", "tactic", "resource", "risk", "assessment"
        ]
        
        critical_keywords = [
            "critique", "flaw", "weakness", "challenge", "assumption", "validate",
            "stress test", "devil's advocate", "potential problems", "what if"
        ]
        
        query_lower = query.lower()
        
        # Check for keyword matches
        confidence = 0.0
        
        for keyword in technical_keywords:
            if keyword in query_lower:
                confidence = max(confidence, 0.8)
                
        for keyword in research_keywords:
            if keyword in query_lower:
                confidence = max(confidence, 0.7)
                
        for keyword in pattern_keywords:
            if keyword in query_lower:
                confidence = max(confidence, 0.6)
                
        for keyword in strategic_keywords:
            if keyword in query_lower:
                confidence = max(confidence, 0.7)
                
        for keyword in critical_keywords:
            if keyword in query_lower:
                confidence = max(confidence, 0.6)
        
        # Check for explicit member requests
        if any(name in query_lower for name in ["artificer", "archivist", "mystagogue", "tactician", "daemon"]):
            confidence = 0.9
            
        # Check for Shadow Council mention
        if "shadow council" in query_lower:
            confidence = 0.95
            
        return confidence
    
    async def execute(self, input: ToolInput) -> ToolOutput:
        """Execute Shadow Council consultation."""
        try:
            # Determine which council members to activate
            members = await self._select_members(input)
            
            # Get responses from selected members
            responses = await self._consult_members(members, input)
            
            # Synthesize responses into unified output
            synthesis = await self._synthesize_responses(responses, input)
            
            return ToolOutput(
                success=True,
                result=synthesis,
                metadata={
                    "members_consulted": members,
                    "response_count": len(responses)
                },
                confidence=0.85,
                display_format="markdown"
            )
            
        except Exception as e:
            logger.error(f"Shadow Council execution error: {e}")
            return ToolOutput(
                success=False,
                result=None,
                error=f"Shadow Council consultation failed: {str(e)}"
            )
    
    async def _select_members(self, input: ToolInput) -> List[str]:
        """Select which council members to activate based on the query.
        
        IMPORTANT: The Shadow Council operates as a unified collective.
        ALL members provide their perspective on EVERY query to ensure
        comprehensive, multi-faceted analysis.
        """
        # ALWAYS return ALL council members
        # This ensures every query gets the full spectrum of expertise:
        # - Technical implementation (Artificer)
        # - Historical context and knowledge (Archivist)  
        # - Deeper patterns and insights (Mystagogue)
        # - Strategic planning (Tactician)
        # - Critical analysis and risk assessment (Daemon)
        
        return ["artificer", "archivist", "mystagogue", "tactician", "daemon"]
    
    async def _consult_members(self, members: List[str], input: ToolInput) -> Dict[str, str]:
        """Get responses from selected council members with parallel execution limits."""
        responses = {}
        
        # Get the max parallel limit from metadata
        max_parallel = self.metadata.max_parallel
        
        # Process members in batches to respect parallel limit
        for i in range(0, len(members), max_parallel):
            batch = members[i:i + max_parallel]
            
            # Create consultation tasks for this batch
            tasks = []
            for member in batch:
                tasks.append(self._consult_member(member, input))
            
            # Execute batch consultations in parallel
            logger.info(f"Consulting batch of {len(batch)} council members in parallel (max {max_parallel})")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect successful responses
            for member, result in zip(batch, results):
                if isinstance(result, Exception):
                    logger.warning(f"Council member {member} failed: {result}")
                    responses[member] = f"[{member.title()} is currently unavailable]"
                else:
                    responses[member] = result
            
            # Small delay between batches to avoid overwhelming the LLM service
            if i + max_parallel < len(members):
                await asyncio.sleep(0.5)
        
        return responses
    
    async def _consult_member(self, member: str, input: ToolInput) -> str:
        """Consult a specific council member using LLM."""
        
        # Get member-specific system prompt
        system_prompts = {
            "artificer": self._get_artificer_system_prompt(),
            "archivist": self._get_archivist_system_prompt(),
            "mystagogue": self._get_mystagogue_system_prompt(),
            "tactician": self._get_tactician_system_prompt(),
            "daemon": self._get_daemon_system_prompt()
        }
        
        system_prompt = system_prompts.get(member, "You are a member of the Shadow Council.")
        
        # Get member-specific user prompt
        user_prompts = {
            "artificer": self._get_artificer_prompt(input.query),
            "archivist": self._get_archivist_prompt(input.query),
            "mystagogue": self._get_mystagogue_prompt(input.query),
            "tactician": self._get_tactician_prompt(input.query),
            "daemon": self._get_daemon_prompt(input.query)
        }
        
        user_prompt = user_prompts.get(member, input.query)
        
        try:
            # Get LLM response for this council member
            response = await self.llm_service.complete(
                prompt=user_prompt,
                system=system_prompt,
                temperature=self._get_member_temperature(member),
                max_tokens=1500  # Reasonable limit per member
            )
            
            # Extract content from response dict
            content = response.get("content", "") if response else ""
            
            # Format with member header
            member_title = member.title()
            return f"**{member_title}'s Analysis:**\n\n{content}"
            
        except Exception as e:
            logger.error(f"Error consulting {member}: {e}")
            return f"**{member.title()}**: [Currently unavailable due to technical issues]"
    
    def _get_artificer_prompt(self, query: str) -> str:
        """Generate Artificer-specific prompt."""
        return f"""As the Artificer of the Shadow Council, analyze this technical challenge:
        
{query}

Focus on:
- Practical implementation details
- Technical architecture and design
- Specific tools and technologies
- Optimization opportunities
- Engineering best practices"""

    def _get_archivist_prompt(self, query: str) -> str:
        """Generate Archivist-specific prompt."""
        return f"""As the Archivist of the Shadow Council, research this topic:
        
{query}

Focus on:
- Historical precedents and context
- Relevant documentation and sources
- Knowledge synthesis from multiple domains
- Identifying patterns from past examples
- Building comprehensive understanding"""

    def _get_mystagogue_prompt(self, query: str) -> str:
        """Generate Mystagogue-specific prompt."""
        return f"""As the Mystagogue of the Shadow Council, reveal hidden patterns in:
        
{query}

Focus on:
- Emergent patterns and behaviors
- Symbolic connections and meaning
- Non-obvious relationships
- Deep structural insights
- Systemic implications"""

    def _get_tactician_prompt(self, query: str) -> str:
        """Generate Tactician-specific prompt."""
        return f"""As the Tactician of the Shadow Council, develop strategy for:
        
{query}

Focus on:
- Strategic options and tradeoffs
- Resource optimization
- Risk assessment and mitigation
- Phased implementation approach
- Success metrics and evaluation"""

    def _get_daemon_prompt(self, query: str) -> str:
        """Generate Daemon-specific prompt."""
        return f"""As the Daemon of the Shadow Council, critically examine:
        
{query}

Focus on:
- Potential flaws and weaknesses
- Challenged assumptions
- Edge cases and failure modes
- Alternative perspectives
- Stress testing the approach"""
    
    async def _synthesize_responses(self, responses: Dict[str, str], input: ToolInput) -> str:
        """Synthesize all Shadow Council member responses into a unified output.
        
        The synthesis represents Mnemosyne's integration of all perspectives,
        creating a cohesive response that balances technical, strategic, historical,
        philosophical, and critical viewpoints.
        """
        
        # Shadow Council ALWAYS has all 5 members respond
        synthesis = f"## Shadow Council Complete Analysis\n\n"
        synthesis += f"*Query: {input.query}*\n\n"
        synthesis += f"**Full Council Convened** - All five members have analyzed your query:\n\n"
        
        # Present each member's response
        synthesis += "---\n\n"
        for member, response in responses.items():
            synthesis += f"{response}\n\n"
            if member != list(responses.keys())[-1]:
                synthesis += "---\n\n"
        
        # Create Mnemosyne's unified synthesis of all perspectives
        synthesis += "---\n\n"
        synthesis += "### Mnemosyne's Integrated Synthesis\n\n"
        synthesis += "*Weaving together the Council's collective wisdom:*\n\n"
        
        # The synthesis should identify convergences and tensions
        synthesis += "**Key Convergences:**\n"
        synthesis += "- Technical implementation (Artificer) must align with strategic goals (Tactician)\n"
        synthesis += "- Historical precedents (Archivist) inform risk mitigation (Daemon)\n"
        synthesis += "- Deeper patterns (Mystagogue) reveal systemic considerations\n\n"
        
        synthesis += "**Critical Tensions to Navigate:**\n"
        synthesis += "- Innovation vs. proven approaches\n"
        synthesis += "- Speed of implementation vs. thoroughness of design\n"
        synthesis += "- Ideal architecture vs. practical constraints\n\n"
        
        synthesis += "**Unified Recommendation:**\n"
        synthesis += "The Shadow Council's analysis reveals that success requires balancing "
        synthesis += "technical excellence with strategic wisdom, learning from history while "
        synthesis += "innovating for the future, and maintaining critical awareness throughout. "
        synthesis += "The path forward should integrate all five perspectives - not choosing between them, "
        synthesis += "but synthesizing them into a comprehensive approach that addresses both immediate "
        synthesis += "implementation needs and long-term systemic implications.\n\n"
        
        synthesis += "*This synthesis represents the Shadow Council's collective intelligence, "
        synthesis += "filtered through Mnemosyne's understanding, and will now be expressed through "
        synthesis += "your chosen persona's voice.*"
        
        return synthesis
    
    def _get_member_temperature(self, member: str) -> float:
        """Get temperature setting for each member's personality."""
        temperatures = {
            "artificer": 0.3,   # Precise, technical
            "archivist": 0.4,   # Accurate, thorough
            "mystagogue": 0.7,  # Creative, pattern-seeking
            "tactician": 0.5,   # Balanced, strategic
            "daemon": 0.6       # Critical, provocative
        }
        return temperatures.get(member, 0.5)
    
    def _get_artificer_system_prompt(self) -> str:
        """System prompt for Artificer."""
        return """You are the Artificer of the Shadow Council, a master of technical implementation and engineering excellence.
        
Your personality:
- Precise and methodical in your analysis
- Focus on practical, implementable solutions
- Deep expertise in software architecture, system design, and optimization
- Communicate with technical clarity while remaining accessible

Your approach:
- Break down complex problems into manageable components
- Identify specific tools, technologies, and methodologies
- Consider scalability, maintainability, and performance
- Provide concrete implementation steps"""

    def _get_archivist_system_prompt(self) -> str:
        """System prompt for Archivist."""
        return """You are the Archivist of the Shadow Council, keeper of knowledge and master of research.
        
Your personality:
- Thorough and meticulous in gathering information
- Excellent at synthesizing knowledge from multiple sources
- Strong focus on documentation and historical context
- Communicate findings with scholarly precision

Your approach:
- Research historical precedents and established patterns
- Identify relevant documentation and references
- Synthesize information into actionable insights
- Build comprehensive understanding from available knowledge"""

    def _get_mystagogue_system_prompt(self) -> str:
        """System prompt for Mystagogue."""
        return """You are the Mystagogue of the Shadow Council, revealer of hidden patterns and deeper meanings.
        
Your personality:
- Intuitive and pattern-seeking
- Able to see connections others miss
- Focus on emergent behaviors and symbolic significance
- Communicate insights with philosophical depth

Your approach:
- Identify non-obvious patterns and connections
- Explore symbolic and systemic implications
- Reveal emergent properties and behaviors
- Connect disparate concepts into unified understanding"""

    def _get_tactician_system_prompt(self) -> str:
        """System prompt for Tactician."""
        return """You are the Tactician of the Shadow Council, master strategist and planning expert.
        
Your personality:
- Strategic and forward-thinking
- Excellent at resource optimization and risk assessment
- Focus on actionable plans and measurable outcomes
- Communicate strategies with military precision

Your approach:
- Develop multiple strategic options with tradeoffs
- Assess resources, risks, and opportunities
- Create phased implementation roadmaps
- Define success metrics and evaluation criteria"""

    def _get_daemon_system_prompt(self) -> str:
        """System prompt for Daemon."""
        return """You are the Daemon of the Shadow Council, the constructive critic and devil's advocate.
        
Your personality:
- Skeptical but constructive
- Excellent at identifying flaws and edge cases
- Challenge assumptions without being destructive
- Communicate critiques with intellectual rigor

Your approach:
- Identify potential weaknesses and failure modes
- Challenge underlying assumptions
- Explore edge cases and worst-case scenarios
- Offer alternative perspectives and contrarian views
- Strengthen ideas through rigorous examination"""