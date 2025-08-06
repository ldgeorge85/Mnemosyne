"""
Base class for all philosophical agents.
Defines the interface for analysis, critique, and state management.
"""

from typing import Any, Dict

class BaseAgent:
    """Base class for philosophical agents."""
    def __init__(self, name: str, archetype: str):
        self.name = name
        self.archetype = archetype
        self.memory = []  # Conversation memory

    def analyze_prompt(self, prompt: str) -> str:
        """
        Analyze the user prompt from this agent's philosophical perspective.
        Should be overridden by subclasses.
        """
        raise NotImplementedError

    def critique(self, other_response: str) -> str:
        """
        Critique another agent's response from this agent's perspective.
        Should be overridden by subclasses.
        """
        raise NotImplementedError

    def update_memory(self, entry: Dict[str, Any]):
        """
        Add an entry to the agent's memory.
        """
        self.memory.append(entry)
