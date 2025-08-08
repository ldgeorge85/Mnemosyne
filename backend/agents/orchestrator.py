"""
Agent orchestrator for Mnemosyne Protocol
Coordinates multiple agents for complex reflections
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict
import random

from .base import (
    BaseAgent, AgentRole, AgentCapability, AgentContext,
    ReflectionFragment, AgentFactory
)
from core.redis_client import redis_manager
from core.events import event_bus, EventType, Event
from services.memory_service import MemoryService
from services.search_service import vector_search_service

logger = logging.getLogger(__name__)


class AgentSelectionStrategy:
    """Strategy for selecting agents for a task"""
    
    @staticmethod
    def select_by_capability(
        agents: Dict[str, BaseAgent],
        required_capabilities: List[AgentCapability],
        max_agents: int = 3
    ) -> List[BaseAgent]:
        """Select agents based on required capabilities"""
        selected = []
        capability_coverage = set()
        
        # First pass: agents with multiple required capabilities
        for agent in agents.values():
            agent_caps = set(agent.capabilities)
            matching_caps = agent_caps & set(required_capabilities)
            
            if len(matching_caps) > 1:
                selected.append(agent)
                capability_coverage.update(matching_caps)
                
                if len(selected) >= max_agents:
                    break
        
        # Second pass: fill gaps with specialized agents
        missing_caps = set(required_capabilities) - capability_coverage
        for cap in missing_caps:
            if len(selected) >= max_agents:
                break
            
            for agent in agents.values():
                if cap in agent.capabilities and agent not in selected:
                    selected.append(agent)
                    break
        
        return selected[:max_agents]
    
    @staticmethod
    def select_by_context(
        agents: Dict[str, BaseAgent],
        context: AgentContext,
        max_agents: int = 3
    ) -> List[BaseAgent]:
        """Select agents based on context"""
        selected = []
        
        # Determine required capabilities from context
        required_capabilities = []
        
        if context.memory_content:
            # Analyze memory content
            if any(word in context.memory_content.lower() 
                   for word in ['code', 'bug', 'error', 'function', 'class']):
                required_capabilities.append(AgentCapability.TECHNICAL_ANALYSIS)
            
            if any(word in context.memory_content.lower()
                   for word in ['pattern', 'recurring', 'similar', 'connection']):
                required_capabilities.append(AgentCapability.PATTERN_RECOGNITION)
            
            if any(word in context.memory_content.lower()
                   for word in ['private', 'sensitive', 'personal', 'secret']):
                required_capabilities.append(AgentCapability.PRIVACY_ANALYSIS)
        
        if context.related_memories and len(context.related_memories) > 5:
            required_capabilities.append(AgentCapability.MEMORY_ANALYSIS)
        
        if context.collective_context:
            required_capabilities.append(AgentCapability.COLLECTIVE_INTELLIGENCE)
        
        # Default to philosophical reflection if no specific requirements
        if not required_capabilities:
            required_capabilities.append(AgentCapability.PHILOSOPHICAL_REFLECTION)
        
        return AgentSelectionStrategy.select_by_capability(
            agents, required_capabilities, max_agents
        )


class ReflectionJournal:
    """Journal of agent reflections"""
    
    def __init__(self, memory_id: str, user_id: str):
        self.memory_id = memory_id
        self.user_id = user_id
        self.fragments: List[ReflectionFragment] = []
        self.agent_contributions: Dict[str, List[ReflectionFragment]] = defaultdict(list)
        self.created_at = datetime.utcnow()
        self.metadata: Dict[str, Any] = {}
    
    def add_fragments(self, fragments: List[ReflectionFragment]):
        """Add reflection fragments to journal"""
        for fragment in fragments:
            self.fragments.append(fragment)
            self.agent_contributions[fragment.agent_id].append(fragment)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get journal summary"""
        # Group fragments by type
        by_type = defaultdict(list)
        for fragment in self.fragments:
            by_type[fragment.fragment_type].append(fragment)
        
        # Calculate confidence statistics
        confidences = [f.confidence for f in self.fragments]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            "memory_id": self.memory_id,
            "user_id": self.user_id,
            "total_fragments": len(self.fragments),
            "agent_count": len(self.agent_contributions),
            "fragment_types": {
                ftype: len(frags) for ftype, frags in by_type.items()
            },
            "average_confidence": avg_confidence,
            "created_at": self.created_at.isoformat()
        }
    
    def get_insights(self) -> List[str]:
        """Extract key insights from journal"""
        insights = []
        
        # High confidence insights
        for fragment in self.fragments:
            if fragment.fragment_type == "insight" and fragment.confidence >= 0.8:
                insights.append(fragment.content)
        
        # Important patterns
        for fragment in self.fragments:
            if fragment.fragment_type == "pattern" and fragment.confidence >= 0.7:
                insights.append(f"Pattern detected: {fragment.content}")
        
        # Critical warnings
        for fragment in self.fragments:
            if fragment.fragment_type == "warning":
                insights.append(f"Warning: {fragment.content}")
        
        return insights[:10]  # Top 10 insights


class AgentOrchestrator:
    """Orchestrates multiple agents for complex cognitive tasks"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.memory_service = MemoryService()
        self.active_reflections: Dict[str, ReflectionJournal] = {}
        self.agent_pool_size = 10  # Maximum concurrent agents
        self._initialized = False
    
    async def initialize(self):
        """Initialize orchestrator and agents"""
        if self._initialized:
            return
        
        try:
            # Register event handlers
            event_bus.register_handler(
                EventType.MEMORY_CREATED,
                self
            )
            event_bus.register_handler(
                EventType.REFLECTION_TRIGGERED,
                self
            )
            
            logger.info("Agent orchestrator initialized")
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            raise
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent.agent_id] = agent
        logger.info(f"Registered agent {agent.agent_id} with role {agent.role}")
    
    async def trigger_reflection(
        self,
        memory_id: str,
        user_id: str,
        trigger_reason: str = "manual",
        agent_ids: Optional[List[str]] = None
    ) -> ReflectionJournal:
        """Trigger multi-agent reflection on a memory"""
        try:
            # Get memory
            memory = await self.memory_service.get_memory(memory_id, user_id)
            if not memory:
                raise ValueError(f"Memory {memory_id} not found")
            
            # Get related memories
            related_memories = await vector_search_service.find_related_memories(
                memory_id=memory_id,
                user_id=user_id,
                limit=10
            )
            
            # Build context
            context = AgentContext(
                user_id=user_id,
                memory_id=memory_id,
                memory_content=memory.content,
                related_memories=[
                    {
                        "id": str(m.id),
                        "content": m.content[:200],
                        "summary": m.metadata.get("summary"),
                        "score": m.score
                    }
                    for m in related_memories
                ],
                trigger_reason=trigger_reason,
                metadata={
                    "memory_type": memory.memory_type.value,
                    "importance": memory.importance,
                    "tags": memory.tags,
                    "domains": memory.domains
                }
            )
            
            # Select agents
            if agent_ids:
                selected_agents = [
                    self.agents[aid] for aid in agent_ids
                    if aid in self.agents
                ]
            else:
                selected_agents = AgentSelectionStrategy.select_by_context(
                    self.agents,
                    context,
                    max_agents=3
                )
            
            if not selected_agents:
                logger.warning("No agents selected for reflection")
                return ReflectionJournal(memory_id, user_id)
            
            # Create journal
            journal = ReflectionJournal(memory_id, user_id)
            self.active_reflections[memory_id] = journal
            
            # Trigger reflections concurrently
            tasks = []
            for agent in selected_agents:
                if await agent.can_handle(context):
                    tasks.append(agent.reflect(context))
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, list):
                        journal.add_fragments(result)
                    elif isinstance(result, Exception):
                        logger.error(f"Agent reflection failed: {result}")
            
            # Store journal
            await self._store_journal(journal)
            
            # Emit completion event
            await event_bus.publish(Event(
                event_type=EventType.REFLECTION_COMPLETED,
                user_id=user_id,
                data={
                    "memory_id": memory_id,
                    "journal_summary": journal.get_summary(),
                    "insights": journal.get_insights()
                }
            ))
            
            return journal
            
        except Exception as e:
            logger.error(f"Reflection orchestration failed: {e}")
            
            # Emit failure event
            await event_bus.publish(Event(
                event_type=EventType.REFLECTION_FAILED,
                user_id=user_id,
                data={
                    "memory_id": memory_id,
                    "error": str(e)
                }
            ))
            
            raise
    
    async def trigger_dialogue(
        self,
        topic: str,
        user_id: str,
        participating_agents: List[str],
        max_rounds: int = 5
    ) -> List[Dict[str, Any]]:
        """Trigger multi-agent dialogue on a topic"""
        dialogue = []
        
        try:
            # Initialize dialogue context
            context = AgentContext(
                user_id=user_id,
                trigger_reason=f"Dialogue: {topic}",
                metadata={"topic": topic}
            )
            
            # Get participating agents
            agents = [
                self.agents[aid] for aid in participating_agents
                if aid in self.agents
            ]
            
            if len(agents) < 2:
                raise ValueError("At least 2 agents required for dialogue")
            
            # Conduct dialogue rounds
            for round_num in range(max_rounds):
                round_responses = []
                
                # Each agent responds to the topic and previous responses
                for agent in agents:
                    # Update context with dialogue history
                    context.metadata["dialogue_history"] = dialogue
                    
                    # Get agent response
                    fragments = await agent.reflect(context)
                    
                    if fragments:
                        response = {
                            "round": round_num + 1,
                            "agent_id": agent.agent_id,
                            "agent_role": agent.role.value,
                            "response": " ".join(f.content for f in fragments),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        round_responses.append(response)
                        dialogue.append(response)
                
                # Check for convergence
                if self._check_dialogue_convergence(round_responses):
                    break
            
            return dialogue
            
        except Exception as e:
            logger.error(f"Dialogue orchestration failed: {e}")
            raise
    
    def _check_dialogue_convergence(self, responses: List[Dict[str, Any]]) -> bool:
        """Check if dialogue has converged"""
        if len(responses) < 2:
            return False
        
        # Simple convergence check - can be enhanced
        # Check if responses are becoming similar
        contents = [r["response"] for r in responses]
        
        # If all responses are very short, consider converged
        if all(len(c) < 50 for c in contents):
            return True
        
        return False
    
    async def _store_journal(self, journal: ReflectionJournal):
        """Store reflection journal"""
        try:
            # Store in Redis with TTL
            key = f"reflection_journal:{journal.memory_id}"
            await redis_manager.cache_set(
                key,
                {
                    "summary": journal.get_summary(),
                    "insights": journal.get_insights(),
                    "fragments": [
                        {
                            "agent_id": f.agent_id,
                            "agent_role": f.agent_role.value,
                            "type": f.fragment_type,
                            "content": f.content,
                            "confidence": f.confidence
                        }
                        for f in journal.fragments
                    ]
                },
                ttl=86400  # 24 hours
            )
            
        except Exception as e:
            logger.error(f"Failed to store journal: {e}")
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        status = {
            "orchestrator_initialized": self._initialized,
            "agent_count": len(self.agents),
            "active_reflections": len(self.active_reflections),
            "agents": {}
        }
        
        for agent_id, agent in self.agents.items():
            status["agents"][agent_id] = await agent.get_status()
        
        return status
    
    async def balance_agent_load(self):
        """Balance load across agents"""
        # Track agent usage
        usage_stats = defaultdict(int)
        
        for journal in self.active_reflections.values():
            for agent_id in journal.agent_contributions.keys():
                usage_stats[agent_id] += len(journal.agent_contributions[agent_id])
        
        # Log statistics
        logger.info(f"Agent usage stats: {dict(usage_stats)}")
        
        # Could implement load balancing logic here
        # For now, just log the information
    
    # Event handler methods
    async def can_handle(self, event: Event) -> bool:
        """Check if orchestrator can handle event"""
        return event.event_type in [
            EventType.MEMORY_CREATED,
            EventType.REFLECTION_TRIGGERED
        ]
    
    async def handle(self, event: Event) -> None:
        """Handle events"""
        if event.event_type == EventType.REFLECTION_TRIGGERED:
            memory_id = event.data.get("memory_id")
            user_id = event.user_id
            
            if memory_id and user_id:
                await self.trigger_reflection(
                    memory_id=memory_id,
                    user_id=user_id,
                    trigger_reason=event.data.get("trigger", "event")
                )
    
    async def on_error(self, event: Event, error: Exception) -> None:
        """Handle event processing errors"""
        logger.error(f"Orchestrator error handling event {event.id}: {error}")


class AgentResourceManager:
    """Manages agent resources and lifecycle"""
    
    def __init__(self, max_agents: int = 50):
        self.max_agents = max_agents
        self.agent_pool: Dict[str, BaseAgent] = {}
        self.agent_usage: Dict[str, datetime] = {}
        self.cleanup_interval = 3600  # 1 hour
    
    async def get_or_create_agent(
        self,
        role: AgentRole,
        agent_id: Optional[str] = None
    ) -> BaseAgent:
        """Get existing agent or create new one"""
        if agent_id and agent_id in self.agent_pool:
            self.agent_usage[agent_id] = datetime.utcnow()
            return self.agent_pool[agent_id]
        
        # Check pool size
        if len(self.agent_pool) >= self.max_agents:
            await self._cleanup_inactive_agents()
        
        # Create new agent
        agent = AgentFactory.create_agent(role, agent_id)
        await agent.initialize()
        
        self.agent_pool[agent.agent_id] = agent
        self.agent_usage[agent.agent_id] = datetime.utcnow()
        
        return agent
    
    async def _cleanup_inactive_agents(self):
        """Remove inactive agents from pool"""
        cutoff = datetime.utcnow() - timedelta(seconds=self.cleanup_interval)
        
        to_remove = [
            agent_id
            for agent_id, last_used in self.agent_usage.items()
            if last_used < cutoff
        ]
        
        for agent_id in to_remove:
            del self.agent_pool[agent_id]
            del self.agent_usage[agent_id]
        
        logger.info(f"Cleaned up {len(to_remove)} inactive agents")
    
    async def shutdown(self):
        """Shutdown all agents"""
        self.agent_pool.clear()
        self.agent_usage.clear()


# Global orchestrator instance
orchestrator = AgentOrchestrator()
resource_manager = AgentResourceManager()


# Export classes
__all__ = [
    'AgentSelectionStrategy',
    'ReflectionJournal',
    'AgentOrchestrator',
    'AgentResourceManager',
    'orchestrator',
    'resource_manager',
]