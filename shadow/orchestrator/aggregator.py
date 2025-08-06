"""
Aggregator module for the Shadow Orchestrator.

This module contains logic for combining responses from multiple specialized
agents into a coherent final response.
"""

from typing import Dict, List


class ResponseAggregator:
    """
    Aggregates responses from multiple specialized agents.
    
    The aggregator combines outputs from Engineer, Librarian, and/or Priest agents,
    providing a unified and coherent response to the user's request.
    """
    
    def __init__(self):
        # Configuration for response formatting
        self.agent_order = ["librarian", "engineer", "priest"]
        self.agent_prefixes = {
            "engineer": "Technical Analysis",
            "librarian": "Information",
            "priest": "Ethical/Philosophical Perspective"
        }
    
    def aggregate_responses(self, agent_responses: Dict[str, str]) -> str:
        """
        Combine multiple agent responses into a single coherent response.
        
        Args:
            agent_responses: Dictionary mapping agent names to their responses
            
        Returns:
            A combined response string
        """
        # If only one agent responded, return its response directly
        if len(agent_responses) == 1:
            agent = list(agent_responses.keys())[0]
            return agent_responses[agent]
        
        # For multiple responses, create a structured output
        response_parts = []
        
        # Add introduction if multiple agents responded
        if len(agent_responses) > 1:
            response_parts.append(
                "I've analyzed your request from multiple perspectives:\n"
            )
        
        # Add responses in the preferred order
        for agent in self.agent_order:
            if agent in agent_responses:
                prefix = self.agent_prefixes.get(agent, agent.capitalize())
                response_parts.append(f"## {prefix}\n\n{agent_responses[agent]}\n")
        
        # Combine all parts
        combined_response = "\n".join(response_parts)
        return combined_response
    
    def weight_and_combine(self, agent_responses: Dict[str, str], 
                          confidence_scores: Dict[str, float]) -> str:
        """
        Weight and combine responses based on confidence scores.
        
        Args:
            agent_responses: Dictionary mapping agent names to their responses
            confidence_scores: Dictionary mapping agent names to confidence scores
            
        Returns:
            A weighted combined response
        """
        # Sort agents by confidence score
        sorted_agents = sorted(
            confidence_scores.keys(),
            key=lambda agent: confidence_scores.get(agent, 0.0),
            reverse=True
        )
        
        # Build response with most confident agent first
        response_parts = []
        
        # Add responses in confidence order
        for agent in sorted_agents:
            if agent in agent_responses:
                prefix = self.agent_prefixes.get(agent, agent.capitalize())
                confidence = confidence_scores.get(agent, 0.0)
                
                # Only include agent responses with non-zero confidence
                if confidence > 0.0:
                    response_parts.append(f"## {prefix}\n\n{agent_responses[agent]}\n")
        
        # Combine all parts
        combined_response = "\n".join(response_parts)
        return combined_response


# Create a default instance for easy import
default_aggregator = ResponseAggregator()


def aggregate_responses(agent_responses: Dict[str, str]) -> str:
    """
    Simple wrapper function to aggregate responses using the default aggregator.
    
    Args:
        agent_responses: Dictionary mapping agent names to their responses
        
    Returns:
        A combined response string
    """
    return default_aggregator.aggregate_responses(agent_responses)
