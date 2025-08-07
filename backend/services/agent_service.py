"""
Agent service for Mnemosyne Protocol
Manages agent lifecycle and coordination
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.agents.base import AgentRole, AgentFactory, BaseAgent
from backend.agents.orchestrator import orchestrator, resource_manager
from backend.agents.engineer import EngineerAgent
from backend.agents.librarian import LibrarianAgent
from backend.agents.philosopher import PhilosopherAgent
from backend.agents.mystic import MysticAgent
from backend.agents.guardian import GuardianAgent
from backend.agents.collective import CollectiveAgent
from backend.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AgentService:
    """Service for managing cognitive agents"""
    
    def __init__(self):
        self._initialized = False
        self._default_agents: Dict[str, BaseAgent] = {}
    
    async def initialize(self):
        """Initialize agent service and default agents"""
        if self._initialized:
            return
        
        try:
            # Register agent classes with factory
            AgentFactory.register_agent(AgentRole.ENGINEER, EngineerAgent)
            AgentFactory.register_agent(AgentRole.LIBRARIAN, LibrarianAgent)
            AgentFactory.register_agent(AgentRole.PHILOSOPHER, PhilosopherAgent)
            AgentFactory.register_agent(AgentRole.MYSTIC, MysticAgent)
            AgentFactory.register_agent(AgentRole.GUARDIAN, GuardianAgent)
            AgentFactory.register_agent(AgentRole.COLLECTIVE, CollectiveAgent)
            
            # Initialize orchestrator
            await orchestrator.initialize()
            
            # Create and register default agents
            await self._create_default_agents()
            
            logger.info("Agent service initialized")
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize agent service: {e}")
            raise
    
    async def _create_default_agents(self):
        """Create and register default agents"""
        default_roles = [
            AgentRole.ENGINEER,
            AgentRole.LIBRARIAN,
            AgentRole.PHILOSOPHER,
            AgentRole.MYSTIC,
            AgentRole.GUARDIAN,
            AgentRole.COLLECTIVE
        ]
        
        for role in default_roles:
            try:
                agent = await resource_manager.get_or_create_agent(
                    role=role,
                    agent_id=f"default_{role.value}"
                )
                
                self._default_agents[role.value] = agent
                orchestrator.register_agent(agent)
                
                logger.info(f"Created default {role.value} agent")
                
            except Exception as e:
                logger.error(f"Failed to create {role.value} agent: {e}")
    
    async def trigger_reflection(
        self,
        memory_id: str,
        user_id: str,
        agent_roles: Optional[List[str]] = None,
        trigger_reason: str = "manual"
    ) -> Dict[str, Any]:
        """Trigger agent reflection on a memory"""
        try:
            # Select agent IDs based on roles
            agent_ids = None
            if agent_roles:
                agent_ids = [
                    f"default_{role}" for role in agent_roles
                    if role in self._default_agents
                ]
            
            # Trigger orchestrated reflection
            journal = await orchestrator.trigger_reflection(
                memory_id=memory_id,
                user_id=user_id,
                trigger_reason=trigger_reason,
                agent_ids=agent_ids
            )
            
            return {
                "success": True,
                "journal": journal.get_summary(),
                "insights": journal.get_insights()
            }
            
        except Exception as e:
            logger.error(f"Reflection failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def trigger_dialogue(
        self,
        topic: str,
        user_id: str,
        agent_roles: List[str],
        max_rounds: int = 5
    ) -> Dict[str, Any]:
        """Trigger multi-agent dialogue"""
        try:
            # Select agent IDs based on roles
            agent_ids = [
                f"default_{role}" for role in agent_roles
                if role in self._default_agents
            ]
            
            if len(agent_ids) < 2:
                return {
                    "success": False,
                    "error": "At least 2 agents required for dialogue"
                }
            
            # Trigger dialogue
            dialogue = await orchestrator.trigger_dialogue(
                topic=topic,
                user_id=user_id,
                participating_agents=agent_ids,
                max_rounds=max_rounds
            )
            
            return {
                "success": True,
                "dialogue": dialogue,
                "rounds": len(set(r["round"] for r in dialogue))
            }
            
        except Exception as e:
            logger.error(f"Dialogue failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_agent_status(self, agent_role: Optional[str] = None) -> Dict[str, Any]:
        """Get status of agents"""
        try:
            if agent_role:
                agent = self._default_agents.get(agent_role)
                if agent:
                    return await agent.get_status()
                else:
                    return {"error": f"Agent {agent_role} not found"}
            else:
                # Get all agent statuses
                return await orchestrator.get_agent_status()
                
        except Exception as e:
            logger.error(f"Failed to get agent status: {e}")
            return {"error": str(e)}
    
    async def create_custom_agent(
        self,
        role: str,
        agent_id: str,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a custom agent instance"""
        try:
            role_enum = AgentRole(role)
            
            # Create agent
            agent = await resource_manager.get_or_create_agent(
                role=role_enum,
                agent_id=agent_id
            )
            
            # Register with orchestrator
            orchestrator.register_agent(agent)
            
            return {
                "success": True,
                "agent_id": agent_id,
                "role": role,
                "status": await agent.get_status()
            }
            
        except Exception as e:
            logger.error(f"Failed to create custom agent: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_memory_with_agents(
        self,
        memory_id: str,
        user_id: str,
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Perform comprehensive analysis with multiple agents"""
        try:
            results = {}
            
            if analysis_type == "comprehensive":
                # Use all agents
                agent_roles = list(self._default_agents.keys())
            elif analysis_type == "technical":
                agent_roles = ["engineer", "librarian"]
            elif analysis_type == "philosophical":
                agent_roles = ["philosopher", "mystic"]
            elif analysis_type == "privacy":
                agent_roles = ["guardian"]
            else:
                agent_roles = ["engineer", "philosopher"]
            
            # Trigger reflection with selected agents
            reflection_result = await self.trigger_reflection(
                memory_id=memory_id,
                user_id=user_id,
                agent_roles=agent_roles,
                trigger_reason=f"{analysis_type} analysis"
            )
            
            return reflection_result
            
        except Exception as e:
            logger.error(f"Memory analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_collective_wisdom(
        self,
        topic: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get collective wisdom on a topic"""
        try:
            # Use philosopher, mystic, and collective agents
            dialogue_result = await self.trigger_dialogue(
                topic=topic,
                user_id=user_id,
                agent_roles=["philosopher", "mystic", "collective"],
                max_rounds=3
            )
            
            if dialogue_result["success"]:
                # Extract wisdom from dialogue
                wisdom = []
                for response in dialogue_result["dialogue"]:
                    if "wisdom" in response["response"].lower() or \
                       "insight" in response["response"].lower():
                        wisdom.append({
                            "agent": response["agent_role"],
                            "insight": response["response"]
                        })
                
                return {
                    "success": True,
                    "topic": topic,
                    "wisdom": wisdom,
                    "dialogue": dialogue_result["dialogue"]
                }
            else:
                return dialogue_result
                
        except Exception as e:
            logger.error(f"Failed to get collective wisdom: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def shutdown(self):
        """Shutdown agent service"""
        try:
            # Shutdown resource manager
            await resource_manager.shutdown()
            
            logger.info("Agent service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during agent service shutdown: {e}")


# Global agent service instance
agent_service = AgentService()


# Export
__all__ = [
    'AgentService',
    'agent_service',
]