"""
Agent-based tools for the Mnemosyne system.

This module contains tools that leverage LLM-powered agents for specialized expertise:
- Shadow Council: Technical and strategic expertise
- Forum of Echoes: Philosophical and worldview perspectives
"""

from .shadow_council import ShadowCouncilTool
from .forum_of_echoes import ForumOfEchoesTool

__all__ = [
    "ShadowCouncilTool",
    "ForumOfEchoesTool"
]