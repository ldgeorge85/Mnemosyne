"""
Debate Module for the Priest Agent.

This module provides a framework for simulating philosophical and ethical debates
between multiple perspectives using LLM-based reasoning.
"""

import logging
from typing import Dict, List, Optional, Any
import json

# Configure logging
logger = logging.getLogger("shadow.agents.priest.debate")


class DebateModule:
    """
    Framework for simulating philosophical debates between multiple perspectives.
    
    Uses LLM to generate a structured debate between different philosophical,
    ethical, or religious perspectives on a given issue.
    """
    
    def __init__(self, llm_connector=None):
        """
        Initialize the debate module.
        
        Args:
            llm_connector: Optional LLM connector for generating responses
        """
        self.llm_connector = llm_connector
        self.use_llm = llm_connector is not None
    
    def run_debate(self, issue: str, conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Run a simulated debate on the given issue.
        
        Args:
            issue: The ethical/philosophical issue to debate
            conversation_history: Optional conversation history for context
            
        Returns:
            Formatted debate output as a string
        """
        if self.use_llm:
            try:
                return self._run_llm_debate(issue, conversation_history)
            except Exception as e:
                logger.error(f"Error running LLM debate: {str(e)}. Falling back to mock debate.")
                
        # Fall back to mock debate if LLM is unavailable or fails
        return self._run_mock_debate(issue)
    
    def _run_llm_debate(self, issue: str, conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Run a debate using the LLM to generate multiple perspectives.
        
        Args:
            issue: The ethical/philosophical issue to debate
            conversation_history: Optional conversation history for context
            
        Returns:
            Formatted debate output as a string
        """
        # Specialized prompt for debate generation
        debate_prompt = (
            "You are a philosophical debate moderator tasked with exploring multiple perspectives "
            "on an ethical or philosophical question. Generate a structured debate between three "
            "distinct philosophical positions on the following issue. For each perspective:\n\n"
            "1. Name and introduce the philosophical tradition or worldview\n"
            "2. Present its core argument on the issue\n"
            "3. Respond to potential criticisms\n"
            "4. Summarize its final position\n\n"
            "Finally, analyze the key points of agreement and disagreement between these perspectives.\n\n"
            f"Issue to debate: {issue}"
        )
        
        # Generate debate using LLM
        debate_response = self.llm_connector.generate_text(
            system_prompt=debate_prompt,
            user_input=issue,
            conversation_history=conversation_history
        )
        
        return f"## Multi-Perspective Debate\n\n{issue}\n\n{debate_response}"
    
    def _run_mock_debate(self, issue: str) -> str:
        """
        Generate a mock debate when LLM is unavailable.
        
        Args:
            issue: The ethical/philosophical issue to debate
            
        Returns:
            Formatted mock debate as a string
        """
        perspectives = {
            "Utilitarian Perspective": (
                "From a utilitarian standpoint, the primary consideration should be maximizing "
                "overall well-being and minimizing harm. The right action is one that produces "
                "the greatest good for the greatest number of individuals affected."
            ),
            "Kantian Deontological Perspective": (
                "From a Kantian deontological perspective, we must focus on our duties and act "
                "according to universal principles. Actions should be judged by their inherent "
                "rightness or wrongness, not by their consequences. We should ask whether the "
                "maxim of our action could become a universal law."
            ),
            "Virtue Ethics Perspective": (
                "From a virtue ethics perspective, we should consider what actions reflect good "
                "character traits like wisdom, courage, honesty, and compassion. The right action "
                "is what a virtuous person would do in this situation, focusing on developing "
                "excellent character rather than following rules or calculating consequences."
            )
        }
        
        # Format mock debate
        debate_output = [f"## Mock Multi-Perspective Debate on: {issue}\n"]
        
        for perspective, argument in perspectives.items():
            debate_output.append(f"### {perspective}\n{argument}\n")
        
        debate_output.append(
            "\n### Analysis\nThese three perspectives highlight different ethical approaches: "
            "consequences (utilitarian), principles (deontological), and character (virtue ethics). "
            "In a full implementation, this debate would be generated by an LLM with specialized "
            "philosophical knowledge."
        )
        
        return "\n".join(debate_output)
