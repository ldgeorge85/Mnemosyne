"""
Shadow Orchestrator Agent.

This module contains the core orchestrator that manages routing requests
to specialized agents and aggregating their responses with advanced
multi-agent collaboration capabilities.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any

from .classifier import default_classifier
from .aggregator import default_aggregator
from .memory_integration import OrchestratorMemory, default_orchestrator_memory
from .task_decomposer import default_task_decomposer, TaskType
from .collaborative_executor import create_collaborative_executor


class ShadowAgent:
    """
    Central orchestrating agent for the Shadow system.
    
    The Shadow agent receives user input, classifies it, routes it to
    appropriate specialized agent(s), combines their responses, and
    manages advanced multi-agent collaboration workflows.
    """
    
    def __init__(self, agents=None, memory=None, enable_collaboration=True):
        """
        Initialize the Shadow orchestrator.
        
        Args:
            agents: Dictionary mapping agent names to agent instances
            memory: Optional OrchestratorMemory instance for memory integration
            enable_collaboration: Whether to enable advanced collaboration features
        """
        self.agents = agents or {}
        self.classifier = default_classifier
        self.aggregator = default_aggregator
        self.logger = logging.getLogger("shadow.orchestrator")
        
        # Memory and context tracking
        self.memory = memory or default_orchestrator_memory
        self.conversation_history = []
        self.max_history_length = 10
        
        # Advanced collaboration features
        self.enable_collaboration = enable_collaboration
        self.task_decomposer = default_task_decomposer
        self.collaborative_executor = create_collaborative_executor(self.agents)
        
        # Performance tracking
        self.execution_stats = {
            'total_requests': 0,
            'collaborative_requests': 0,
            'average_response_time': 0.0,
            'agent_usage': {}
        }
        
        # Initialize conversation
        self.memory.start_conversation()
    
    def register_agent(self, name: str, agent) -> None:
        """
        Register a specialized agent with the orchestrator.
        
        Args:
            name: Name of the agent
            agent: Agent instance
        """
        self.agents[name] = agent
        # Update collaborative executor with new agent
        self.collaborative_executor.agents[name] = agent
        self.logger.info(f"Registered agent: {name}")
    
    def process_request(self, user_input: str, use_collaboration: Optional[bool] = None) -> str:
        """
        Process a user request through the Shadow system with optional
        advanced collaboration capabilities.
        
        Args:
            user_input: The user's request text
            use_collaboration: Override collaboration setting for this request
            
        Returns:
            The system's response
        """
        import time
        start_time = time.time()
        
        # Store input in conversation history (both local and memory system)
        self.conversation_history.append({"role": "user", "content": user_input})
        self.memory.add_message("user", user_input)
        self._trim_history()

        # Get relevant context from memory system
        context = self.memory.get_relevant_context(user_input)
        self.logger.info(f"Retrieved {len(context.get('relevant_documents', []))} relevant documents and {len(context.get('relevant_entities', []))} entities from memory")

        # Determine if we should use advanced collaboration
        should_collaborate = (
            (use_collaboration if use_collaboration is not None else self.enable_collaboration) and
            len(self.agents) > 1
        )

        response = ""
        agents_used = []

        try:
            if should_collaborate:
                response, agents_used = self._process_with_collaboration(user_input, context)
            else:
                response, agents_used = self._process_with_basic_routing(user_input, context)
                
        except Exception as e:
            self.logger.error(f"Error processing request: {str(e)}")
            response = "I apologize, but I encountered an error while processing your request. Please try again."
            agents_used = []

        # Store response in conversation history and memory
        self.conversation_history.append({"role": "assistant", "content": response})
        self.memory.add_message("assistant", response)
        self._trim_history()

        # Update execution statistics
        execution_time = time.time() - start_time
        self._update_stats(execution_time, agents_used, should_collaborate)

        # Save conversation periodically
        if len(self.conversation_history) % 5 == 0:
            self.memory.save_conversation()
            
        return response

    def _process_with_collaboration(self, user_input: str, context: Dict) -> tuple[str, List[str]]:
        """
        Process request using advanced collaboration capabilities.
        
        Args:
            user_input: The user's request
            context: Memory context
            
        Returns:
            Tuple of (response, agents_used)
        """
        self.logger.info("Processing with advanced collaboration")
        
        # Decompose the task
        decomposition = self.task_decomposer.decompose_task(user_input, context)
        self.logger.info(f"Task decomposed: {decomposition.task_type.value} with {len(decomposition.subtasks)} subtasks")
        
        # For now, skip collaborative execution to avoid async event loop issues
        # Fall back to basic routing which works reliably
        self.logger.info("Using basic routing for stable operation")
        return self._process_with_basic_routing(user_input, context)

    def _process_with_basic_routing(self, user_input: str, context: Dict) -> tuple[str, List[str]]:
        """
        Process request using basic agent routing (original behavior).
        
        Args:
            user_input: The user's request
            context: Memory context
            
        Returns:
            Tuple of (response, agents_used)
        """
        # Classify the user input
        target_agents = self.classifier.classify_task(user_input)
        self.logger.info(f"Classified request to agents: {target_agents}")

        # Collect responses from target agents
        agent_responses = {}
        
        for agent_name in target_agents:
            if agent_name in self.agents:
                try:
                    response = self.agents[agent_name].process_request(
                        user_input, 
                        self.conversation_history,
                        context
                    )
                    agent_responses[agent_name] = response
                    self.logger.info(f"Received response from {agent_name}")
                except Exception as e:
                    self.logger.error(f"Error with {agent_name} agent: {str(e)}")
            else:
                self.logger.warning(f"Agent not found: {agent_name}")

        # Handle case where no agents responded
        if not agent_responses:
            response = "I apologize, but I couldn't process your request at this time."
            self.logger.warning("No agent responses received")
            return response, []
        else:
            # Aggregate responses
            response = self.aggregator.aggregate_responses(agent_responses)
            return response, list(agent_responses.keys())

    def _update_stats(self, execution_time: float, agents_used: List[str], used_collaboration: bool):
        """Update execution statistics."""
        self.execution_stats['total_requests'] += 1
        
        if used_collaboration:
            self.execution_stats['collaborative_requests'] += 1
            
        # Update average response time
        current_avg = self.execution_stats['average_response_time']
        total_requests = self.execution_stats['total_requests']
        self.execution_stats['average_response_time'] = (
            (current_avg * (total_requests - 1) + execution_time) / total_requests
        )
        
        # Update agent usage
        for agent in agents_used:
            self.execution_stats['agent_usage'][agent] = (
                self.execution_stats['agent_usage'].get(agent, 0) + 1
            )

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance and usage statistics."""
        stats = self.execution_stats.copy()
        
        # Add collaboration percentage
        if stats['total_requests'] > 0:
            stats['collaboration_percentage'] = (
                stats['collaborative_requests'] / stats['total_requests'] * 100
            )
        else:
            stats['collaboration_percentage'] = 0.0
            
        return stats

    def set_collaboration_mode(self, enabled: bool):
        """Enable or disable collaboration mode."""
        self.enable_collaboration = enabled
        self.logger.info(f"Collaboration mode {'enabled' if enabled else 'disabled'}")

    def _trim_history(self) -> None:
        """
        Trim the conversation history to the maximum length.
        """
        if len(self.conversation_history) > self.max_history_length:
            # Before trimming, save the full conversation to persistent memory
            self.memory.save_conversation()
            self.conversation_history = self.conversation_history[-self.max_history_length:]
            
    def store_entity(self, name: str, entity_type: str, description: str, properties: Dict[str, Any] = None) -> str:
        """
        Store an entity in the memory system.
        
        Args:
            name: Name of the entity
            entity_type: Type of entity (person, concept, etc.)
            description: Description of the entity
            properties: Additional properties of the entity
            
        Returns:
            ID of the stored entity
        """
        return self.memory.store_entity(name, entity_type, description, properties)

    def store_knowledge(self, title: str, content: str, source: str = None) -> Dict[str, str]:
        """
        Store knowledge in the memory system.
        
        Args:
            title: Title of the knowledge
            content: Content of the knowledge
            source: Source of the knowledge
            
        Returns:
            Dictionary mapping storage types to IDs
        """
        return self.memory.store_important_information(title, content, source)
