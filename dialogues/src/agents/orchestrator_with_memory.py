"""
Enhanced orchestrator agent with memory integration for the Philosophical Multi-Agent Debate System.
Manages debate flow and provides agents with access to their memory of past debates.
"""

import json
import os
import concurrent.futures
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path

from .base import BaseAgent
from .synthesis import SynthesisAgent
from .agent_loader import load_agents_from_directory
from ..memory.memory_manager import MemoryManager


class OrchestratorWithMemory:
    """
    Enhanced orchestrator that manages conversation flow and coordinates all philosophical agents,
    while providing access to persistent memory of past debates.
    """
    def __init__(self, 
                 agent_definitions_dir: Optional[str] = None, 
                 memory_dir: Optional[str] = None):
        """
        Initialize the orchestrator with dynamically loaded agents and memory management.
        
        Args:
            agent_definitions_dir: Directory containing agent definition files
                                  If None, default to "agent_definitions"
            memory_dir: Directory for storing memory files
                        If None, default to {project_root}/memory/
        """
        # Path to agent definitions
        if agent_definitions_dir is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            agent_definitions_dir = os.path.join(project_root, "agent_definitions")
        
        # Load agents dynamically
        self.agents = load_agents_from_directory(agent_definitions_dir)
        self.synthesizer = SynthesisAgent()
        
        # Initialize memory manager
        self.memory_manager = MemoryManager(memory_dir)
        
    def run(self, prompt: str, max_parallel: int = 1):
        """
        Run a single round of multi-agent debate with memory access.
        
        Args:
            prompt (str): The philosophical prompt to debate
            max_parallel (int): Maximum number of parallel API calls (default: 1)
        """
        # Find relevant past debates for context
        relevant_debates = self.memory_manager.get_relevant_debates(prompt)
        debate_context = self._prepare_debate_context(relevant_debates)
        
        responses = []
        critiques = []
        
        # Analysis phase: each agent responds to the prompt (potentially in parallel)
        if max_parallel <= 1:
            # Sequential processing
            for agent in self.agents:
                # Get agent's past positions on related topics for context
                agent_memory = self.memory_manager.get_agent_memory(agent.name)
                
                # Enhanced prompt with memory context
                contextualized_prompt = self._enhance_prompt_with_memory(
                    prompt, agent.name, debate_context, agent_memory
                )
                
                response = agent.analyze_prompt(contextualized_prompt)
                print(f"{agent.name} ({agent.archetype}): {response}")
                responses.append((agent, response))
        else:
            # Parallel processing with memory context
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_parallel) as executor:
                future_to_agent = {}
                
                # Submit all analysis tasks with memory context
                for agent in self.agents:
                    # Get agent's past positions for context
                    agent_memory = self.memory_manager.get_agent_memory(agent.name)
                    
                    # Enhanced prompt with memory context
                    contextualized_prompt = self._enhance_prompt_with_memory(
                        prompt, agent.name, debate_context, agent_memory
                    )
                    
                    future = executor.submit(agent.analyze_prompt, contextualized_prompt)
                    future_to_agent[future] = agent
                
                # Process results as they complete
                for future in concurrent.futures.as_completed(future_to_agent):
                    agent = future_to_agent[future]
                    try:
                        response = future.result()
                        print(f"{agent.name} ({agent.archetype}): {response}")
                        responses.append((agent, response))
                    except Exception as e:
                        print(f"{agent.name} generated an error: {e}")
        
        # Critique phase: each agent critiques all others (potentially in parallel)
        if max_parallel <= 1:
            # Sequential processing for critiques
            for agent, response in responses:
                for other_agent, other_response in responses:
                    if agent != other_agent:
                        # Add context about agent's past critiques of this agent/position
                        critique_context = self._get_critique_context(agent.name, other_agent.name)
                        critique = agent.critique(other_response + "\n\n" + critique_context)
                        print(f"{agent.name} critiques {other_agent.name}: {critique}")
                        critiques.append((agent, other_agent, critique))
        else:
            # Parallel processing for critiques
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_parallel) as executor:
                futures = []
                critique_mapping = {}
                
                for agent, response in responses:
                    for other_agent, other_response in responses:
                        if agent != other_agent:
                            # Add context about agent's past critiques of this agent/position
                            critique_context = self._get_critique_context(agent.name, other_agent.name)
                            future = executor.submit(
                                agent.critique, other_response + "\n\n" + critique_context
                            )
                            futures.append(future)
                            critique_mapping[future] = (agent, other_agent)
                
                # Process critique results as they complete
                for future in concurrent.futures.as_completed(futures):
                    agent, other_agent = critique_mapping[future]
                    try:
                        critique = future.result()
                        print(f"{agent.name} critiques {other_agent.name}: {critique}")
                        critiques.append((agent, other_agent, critique))
                    except Exception as e:
                        print(f"{agent.name} generated an error while critiquing {other_agent.name}: {e}")
        
        # Synthesis phase: summarize the debate
        summary = self.synthesizer.summarize(responses)
        print("\n" + summary)
        
        # Persist the debate in memory
        debate_data = {
            "prompt": prompt,
            "responses": [
                {"agent": agent.name, "archetype": agent.archetype, "response": response}
                for agent, response in responses
            ],
            "critiques": [
                {"critic": agent.name, "target": other_agent.name, "critique": critique}
                for agent, other_agent, critique in critiques
            ],
            "summary": summary,
            "related_debates": [d.get("debate_id") for d in relevant_debates]
        }
        
        debate_id = self.memory_manager.save_debate(debate_data)
        print(f"\nDebate saved with ID: {debate_id}")
        
        return {
            "debate_id": debate_id,
            "responses": responses,
            "summary": summary
        }
    
    def _prepare_debate_context(self, relevant_debates: List[Dict[str, Any]]) -> str:
        """
        Prepare a concise context summary from relevant past debates.
        
        Args:
            relevant_debates: List of relevant debate data
            
        Returns:
            String with debate context information
        """
        if not relevant_debates:
            return ""
            
        context_parts = ["Previous relevant debates on this topic:"]
        for i, debate in enumerate(relevant_debates, 1):
            prompt = debate.get("prompt", "")
            if len(prompt) > 100:
                prompt = prompt[:97] + "..."
                
            context_parts.append(f"{i}. Prompt: \"{prompt}\"")
            
            # Add a few key positions from this debate
            responses = debate.get("responses", [])
            if responses:
                context_parts.append("   Key positions:")
                for j, resp in enumerate(responses[:3], 1):  # Limit to 3 responses
                    agent = resp.get("agent", "Unknown")
                    response = resp.get("response", "")
                    if len(response) > 100:
                        response = response[:97] + "..."
                    context_parts.append(f"   {j}. {agent}: \"{response}\"")
        
        return "\n".join(context_parts)
    
    def _enhance_prompt_with_memory(self, prompt: str, agent_name: str, 
                                   debate_context: str, agent_memory: Dict[str, Any]) -> str:
        """
        Enhance a prompt with memory context for a particular agent.
        
        Args:
            prompt: Original debate prompt
            agent_name: Name of the agent
            debate_context: Context from relevant debates
            agent_memory: Agent's memory data
            
        Returns:
            Enhanced prompt with memory context
        """
        # Extract topics from prompt
        topics = self.memory_manager._extract_topics(prompt)
        
        context_parts = [prompt, "\n"]
        
        # Add context about relevant debates, if available
        if debate_context:
            context_parts.append("\n===== DEBATE CONTEXT =====")
            context_parts.append(debate_context)
        
        # Add context about agent's past positions on related topics, if available
        past_positions = []
        for topic in topics:
            position = self.memory_manager.get_agent_position(agent_name, topic)
            if position:
                if len(position) > 150:  # Limit length for brevity
                    position = position[:147] + "..."
                past_positions.append(f"- On \"{topic}\": {position}")
        
        if past_positions:
            context_parts.append("\n===== YOUR PAST POSITIONS =====")
            context_parts.append("You have previously expressed these views:")
            context_parts.extend(past_positions)
            context_parts.append("\nYou should maintain philosophical consistency with these positions unless you have a strong reason to evolve your thinking.")
        
        return "\n".join(context_parts)
    
    def _get_critique_context(self, critic_name: str, target_name: str) -> str:
        """
        Get context about past critiques between two agents.
        
        Args:
            critic_name: Name of the critiquing agent
            target_name: Name of the agent being critiqued
            
        Returns:
            Context string about past critiques
        """
        # In a more sophisticated implementation, we would search for past critiques
        # between these specific agents. For now, we'll return a generic reminder.
        return f"\nNote: Maintain consistency with your philosophical perspective when critiquing."
