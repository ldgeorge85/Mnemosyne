"""
Base agent classes for Mnemosyne Protocol
LangChain-integrated cognitive agents
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Type, Callable
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
import json

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from pydantic import BaseModel, Field

from ..core.config import get_settings
from ..core.redis_client import redis_manager
from ..models.memory import Memory

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
    ORCHESTRATOR = "orchestrator"


class AgentCapability(str, Enum):
    """Agent capabilities"""
    MEMORY_ANALYSIS = "memory_analysis"
    PATTERN_RECOGNITION = "pattern_recognition"
    TECHNICAL_ANALYSIS = "technical_analysis"
    SEMANTIC_SEARCH = "semantic_search"
    PRIVACY_ANALYSIS = "privacy_analysis"
    COLLECTIVE_INTELLIGENCE = "collective_intelligence"
    PHILOSOPHICAL_REFLECTION = "philosophical_reflection"
    SIGNAL_INTERPRETATION = "signal_interpretation"


class ReflectionFragment(BaseModel):
    """A fragment of agent reflection"""
    agent_id: str
    agent_role: AgentRole
    fragment_type: str  # insight, pattern, warning, suggestion
    content: str
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentContext(BaseModel):
    """Context passed to agents"""
    user_id: str
    memory_id: Optional[str] = None
    memory_content: Optional[str] = None
    related_memories: List[Dict[str, Any]] = Field(default_factory=list)
    user_signal: Optional[Dict[str, Any]] = None
    collective_context: Optional[Dict[str, Any]] = None
    trigger_reason: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseAgent(ABC):
    """Base class for all cognitive agents"""
    
    def __init__(
        self,
        agent_id: str,
        role: AgentRole,
        capabilities: List[AgentCapability],
        temperature: float = 0.7,
        model_name: Optional[str] = None
    ):
        self.agent_id = agent_id
        self.role = role
        self.capabilities = capabilities
        self.temperature = temperature
        self.model_name = model_name or settings.default_llm_model
        
        self._llm = None
        self._tools: List[BaseTool] = []
        self._agent_executor = None
        self._memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        self._logger = logging.getLogger(f"{__name__}.{agent_id}")
    
    @property
    def llm(self):
        """Get LLM instance"""
        if self._llm is None:
            if settings.use_local_models:
                self._llm = ChatOllama(
                    model=self.model_name,
                    temperature=self.temperature,
                    base_url=settings.ollama_base_url
                )
            else:
                self._llm = ChatOpenAI(
                    model=self.model_name,
                    temperature=self.temperature,
                    api_key=settings.openai_api_key.get_secret_value() if settings.openai_api_key else None
                )
        return self._llm
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        pass
    
    @abstractmethod
    def get_tools(self) -> List[BaseTool]:
        """Get tools available to this agent"""
        pass
    
    async def initialize(self):
        """Initialize the agent"""
        try:
            # Get tools
            self._tools = self.get_tools()
            
            # Create prompt
            system_prompt = self.get_system_prompt()
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            
            # Create agent
            agent = create_openai_tools_agent(
                llm=self.llm,
                tools=self._tools,
                prompt=prompt
            )
            
            # Create executor
            self._agent_executor = AgentExecutor(
                agent=agent,
                tools=self._tools,
                memory=self._memory,
                verbose=settings.debug_mode,
                handle_parsing_errors=True,
                max_iterations=5
            )
            
            self._logger.info(f"Agent {self.agent_id} initialized")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize agent: {e}")
            raise
    
    async def reflect(
        self,
        context: AgentContext,
        max_tokens: int = 500
    ) -> List[ReflectionFragment]:
        """Generate reflection on the given context"""
        try:
            # Build input for the agent
            input_data = self._build_input(context)
            
            # Run agent
            response = await self._agent_executor.ainvoke({
                "input": input_data
            })
            
            # Parse response into fragments
            fragments = self._parse_response(response['output'], context)
            
            return fragments
            
        except Exception as e:
            self._logger.error(f"Reflection failed: {e}")
            return []
    
    def _build_input(self, context: AgentContext) -> str:
        """Build input string from context"""
        parts = []
        
        if context.memory_content:
            parts.append(f"Memory: {context.memory_content}")
        
        if context.related_memories:
            parts.append(f"Related memories: {len(context.related_memories)} found")
            for i, mem in enumerate(context.related_memories[:3]):
                parts.append(f"  {i+1}. {mem.get('summary', mem.get('content', ''))[:100]}...")
        
        if context.user_signal:
            parts.append(f"User signal: Coherence={context.user_signal.get('coherence', 0):.2f}")
        
        if context.trigger_reason:
            parts.append(f"Trigger: {context.trigger_reason}")
        
        return "\n".join(parts)
    
    def _parse_response(
        self,
        response: str,
        context: AgentContext
    ) -> List[ReflectionFragment]:
        """Parse agent response into reflection fragments"""
        fragments = []
        
        # Simple parsing - can be enhanced with structured output
        lines = response.strip().split('\n')
        current_type = "insight"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect fragment type markers
            if line.startswith('[PATTERN]'):
                current_type = "pattern"
                line = line[9:].strip()
            elif line.startswith('[WARNING]'):
                current_type = "warning"
                line = line[9:].strip()
            elif line.startswith('[SUGGESTION]'):
                current_type = "suggestion"
                line = line[12:].strip()
            elif line.startswith('[INSIGHT]'):
                current_type = "insight"
                line = line[9:].strip()
            
            if line:
                fragment = ReflectionFragment(
                    agent_id=self.agent_id,
                    agent_role=self.role,
                    fragment_type=current_type,
                    content=line,
                    confidence=0.8,  # Default confidence
                    metadata={
                        "memory_id": context.memory_id,
                        "user_id": context.user_id
                    }
                )
                fragments.append(fragment)
        
        return fragments
    
    async def can_handle(self, context: AgentContext) -> bool:
        """Check if this agent can handle the given context"""
        # Override in subclasses for specific logic
        return True
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "capabilities": [c.value for c in self.capabilities],
            "initialized": self._agent_executor is not None,
            "temperature": self.temperature,
            "model": self.model_name
        }


class SpecializedAgent(BaseAgent):
    """Base class for specialized agents with domain knowledge"""
    
    def __init__(
        self,
        agent_id: str,
        role: AgentRole,
        capabilities: List[AgentCapability],
        domain_knowledge: Dict[str, Any],
        **kwargs
    ):
        super().__init__(agent_id, role, capabilities, **kwargs)
        self.domain_knowledge = domain_knowledge
    
    def enhance_with_domain_knowledge(self, base_prompt: str) -> str:
        """Enhance prompt with domain-specific knowledge"""
        knowledge_str = json.dumps(self.domain_knowledge, indent=2)
        return f"{base_prompt}\n\nDomain Knowledge:\n{knowledge_str}"


class ReactiveAgent(BaseAgent):
    """Agent that reacts to events"""
    
    def __init__(
        self,
        agent_id: str,
        role: AgentRole,
        capabilities: List[AgentCapability],
        event_triggers: List[str],
        **kwargs
    ):
        super().__init__(agent_id, role, capabilities, **kwargs)
        self.event_triggers = event_triggers
    
    async def should_trigger(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Check if agent should trigger on this event"""
        return event_type in self.event_triggers
    
    async def handle_event(
        self,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> List[ReflectionFragment]:
        """Handle an event"""
        context = AgentContext(
            user_id=event_data.get('user_id', 'system'),
            memory_id=event_data.get('memory_id'),
            trigger_reason=f"Event: {event_type}",
            metadata=event_data
        )
        
        return await self.reflect(context)


class CollaborativeAgent(BaseAgent):
    """Agent that can collaborate with other agents"""
    
    def __init__(
        self,
        agent_id: str,
        role: AgentRole,
        capabilities: List[AgentCapability],
        collaborators: List[str] = None,
        **kwargs
    ):
        super().__init__(agent_id, role, capabilities, **kwargs)
        self.collaborators = collaborators or []
    
    async def request_collaboration(
        self,
        target_agent_id: str,
        context: AgentContext,
        request: str
    ) -> Optional[List[ReflectionFragment]]:
        """Request collaboration from another agent"""
        # This would be implemented through the orchestrator
        # For now, return None
        return None
    
    async def respond_to_collaboration(
        self,
        requesting_agent_id: str,
        context: AgentContext,
        request: str
    ) -> List[ReflectionFragment]:
        """Respond to a collaboration request"""
        enhanced_context = AgentContext(
            **context.dict(),
            metadata={
                **context.metadata,
                "collaboration_request": request,
                "requesting_agent": requesting_agent_id
            }
        )
        
        return await self.reflect(enhanced_context)


# Agent factory
class AgentFactory:
    """Factory for creating agents"""
    
    _agent_classes: Dict[AgentRole, Type[BaseAgent]] = {}
    
    @classmethod
    def register_agent(cls, role: AgentRole, agent_class: Type[BaseAgent]):
        """Register an agent class"""
        cls._agent_classes[role] = agent_class
    
    @classmethod
    def create_agent(
        cls,
        role: AgentRole,
        agent_id: Optional[str] = None,
        **kwargs
    ) -> BaseAgent:
        """Create an agent instance"""
        if role not in cls._agent_classes:
            raise ValueError(f"No agent class registered for role {role}")
        
        agent_class = cls._agent_classes[role]
        
        if agent_id is None:
            agent_id = f"{role.value}_{datetime.utcnow().timestamp()}"
        
        return agent_class(agent_id=agent_id, role=role, **kwargs)


# Export classes
__all__ = [
    'AgentRole',
    'AgentCapability',
    'ReflectionFragment',
    'AgentContext',
    'BaseAgent',
    'SpecializedAgent',
    'ReactiveAgent',
    'CollaborativeAgent',
    'AgentFactory',
]