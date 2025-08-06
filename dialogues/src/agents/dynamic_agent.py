"""
Dynamic agent implementation that can be constructed from file definitions.
"""

from .base import BaseAgent
from .llm_utils import call_openai  # Utility for LLM API calls

class DynamicAgent(BaseAgent):
    """
    Dynamically configured agent that uses provided system prompts for all debate phases.
    Supports opening_statement, rebuttal, analysis, and critique.
    """
    def __init__(self, name: str, archetype: str, analysis_prompt: str, critique_prompt: str, opening_prompt: str = None, rebuttal_prompt: str = None):
        """
        Initialize a DynamicAgent with custom system prompts.
        Args:
            name: Agent name
            archetype: Philosophical archetype/tradition
            analysis_prompt: System prompt for analyzing user input
            critique_prompt: System prompt for critiquing other responses
            opening_prompt: System prompt for opening statement (optional)
            rebuttal_prompt: System prompt for rebuttal (optional)
        """
        super().__init__(name=name, archetype=archetype)
        self.analysis_prompt = analysis_prompt
        self.critique_prompt = critique_prompt
        self.opening_prompt = opening_prompt or analysis_prompt
        self.rebuttal_prompt = rebuttal_prompt or critique_prompt

    def opening_statement(self, prompt: str) -> str:
        """
        Generate an opening statement for the debate. Uses opening_prompt if available, else falls back to analyze_prompt.
        """
        return call_openai(self.opening_prompt, prompt)

    def rebuttal(self, other_opening: str) -> str:
        """
        Generate a rebuttal to another agent's opening statement. Uses rebuttal_prompt if available, else falls back to critique.
        """
        return call_openai(self.rebuttal_prompt, other_opening)

    def analyze_prompt(self, prompt: str) -> str:
        """
        Analyze a prompt using the configured analysis system prompt (legacy compatibility).
        """
        return call_openai(self.analysis_prompt, prompt)

    def critique(self, other_response: str) -> str:
        """
        Critique another response using the configured critique system prompt (legacy compatibility).
        """
        return call_openai(self.critique_prompt, other_response)
