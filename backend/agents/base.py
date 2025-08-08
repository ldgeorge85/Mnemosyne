"""
Base agent framework for Mnemosyne Protocol
Cognitive agents with specialized roles and capabilities
LangChain integration deferred to Sprint 5
"""

import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
from datetime import datetime
from enum import Enum
import uuid
import json

from pydantic import BaseModel, Field

from core.config import get_settings
from core.redis_client import redis_manager
from models.memory import Memory

logger = logging.getLogger(__name__)
settings = get_settings()


class AgentRole(str, Enum):
    """Agent roles in the system"""
    ENGINEER = "engineer"
    LIBRARIAN = "librarian"
    PHILOSOPHER = "philosopher"
    MYSTIC = "mystic"
    GUARDIAN = "guardian"
    COLLECTIVE = "collective"
    PRIEST = "priest"
    PROPHET = "prophet"
    ARCHITECT = "architect"
    ALCHEMIST = "alchemist"


class AgentCapability(str, Enum):
    """Agent capabilities"""
    PATTERN_RECOGNITION = "pattern_recognition"
    CAUSAL_ANALYSIS = "causal_analysis"
    SEMANTIC_EXTRACTION = "semantic_extraction"
    EMOTIONAL_MAPPING = "emotional_mapping"
    PRIVACY_PROTECTION = "privacy_protection"
    KNOWLEDGE_SYNTHESIS = "knowledge_synthesis"
    RITUAL_DESIGN = "ritual_design"
    SIGNAL_GENERATION = "signal_generation"
    COLLECTIVE_WISDOM = "collective_wisdom"


class AgentContext(BaseModel):
    """Context for agent execution"""
    user_id: str
    memory_id: Optional[str] = None
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ReflectionFragment(BaseModel):
    """A fragment of reflection from an agent"""
    agent_role: AgentRole
    memory_id: str
    content: str
    insights: List[str] = Field(default_factory=list)
    patterns: List[str] = Field(default_factory=list)
    connections: List[str] = Field(default_factory=list)
    questions: List[str] = Field(default_factory=list)
    confidence: float = 0.8
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseAgent(ABC):
    """Base class for all cognitive agents"""
    
    def __init__(
        self,
        role: AgentRole,
        capabilities: List[AgentCapability],
        name: Optional[str] = None
    ):
        self.role = role
        self.capabilities = capabilities
        self.name = name or f"{role.value}_agent"
        self.initialized = False
        logger.info(f"Initialized {self.name} with capabilities: {capabilities}")
    
    async def initialize(self) -> None:
        """Initialize agent resources"""
        if not self.initialized:
            # LangChain initialization deferred to Sprint 5
            self.initialized = True
            logger.info(f"{self.name} initialized (simplified mode)")
    
    async def reflect(
        self,
        memory: Memory,
        context: AgentContext
    ) -> ReflectionFragment:
        """Generate reflection on a memory"""
        # Simplified implementation for Sprint 1-4
        return ReflectionFragment(
            agent_role=self.role,
            memory_id=str(memory.id),
            content=f"Reflection from {self.role.value}: {memory.content[:100]}",
            insights=["Simplified insight"],
            patterns=[],
            connections=[],
            questions=[],
            confidence=0.7,
            metadata={"simplified": True}
        )
    
    async def dialogue(
        self,
        message: str,
        context: AgentContext
    ) -> str:
        """Engage in dialogue"""
        # Simplified implementation for Sprint 1-4
        return f"{self.name}: Processing message about {message[:50]}..."
    
    async def process_memory(
        self,
        memory: Memory,
        context: AgentContext
    ) -> Dict[str, Any]:
        """Process a memory and generate insights"""
        try:
            reflection = await self.reflect(memory, context)
            
            # Store reflection in Redis for aggregation
            await self._store_reflection(reflection, context)
            
            return {
                "agent": self.name,
                "role": self.role.value,
                "reflection": reflection.dict(),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"{self.name} failed to process memory: {e}")
            return {
                "agent": self.name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _store_reflection(
        self,
        reflection: ReflectionFragment,
        context: AgentContext
    ) -> None:
        """Store reflection in Redis for aggregation"""
        key = f"reflection:{context.session_id}:{self.role.value}"
        value = json.dumps(reflection.dict())
        
        await redis_manager.set_with_expiry(
            key,
            value,
            expiry=3600  # 1 hour TTL
        )
    
    def get_system_prompt(self) -> str:
        """Get agent's system prompt"""
        # Override in subclasses for specialized prompts
        return f"""You are a {self.role.value} agent in the Mnemosyne Protocol.
Your capabilities include: {', '.join([c.value for c in self.capabilities])}.
Analyze memories deeply and generate meaningful insights."""
    
    async def shutdown(self) -> None:
        """Cleanup agent resources"""
        logger.info(f"{self.name} shutting down")


class AgentFactory:
    """Factory for creating agents"""
    
    _agents: Dict[AgentRole, Type[BaseAgent]] = {}
    
    @classmethod
    def register(cls, role: AgentRole, agent_class: Type[BaseAgent]) -> None:
        """Register an agent class"""
        cls._agents[role] = agent_class
        logger.info(f"Registered {agent_class.__name__} for role {role.value}")
    
    @classmethod
    async def create(
        cls,
        role: AgentRole,
        **kwargs
    ) -> BaseAgent:
        """Create an agent instance"""
        if role not in cls._agents:
            raise ValueError(f"No agent registered for role {role.value}")
        
        agent_class = cls._agents[role]
        agent = agent_class(**kwargs)
        await agent.initialize()
        
        return agent
    
    @classmethod
    def get_available_roles(cls) -> List[AgentRole]:
        """Get list of available agent roles"""
        return list(cls._agents.keys())


# Export key items
__all__ = [
    "AgentRole",
    "AgentCapability",
    "AgentContext",
    "ReflectionFragment",
    "BaseAgent",
    "AgentFactory"
]