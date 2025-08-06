"""
Outline knowledge base source.

AI Agents: Import what you need:
    from sources.outline import OutlineSource
    from sources.outline.prompts import get_prompt
"""

from .connector import OutlineSource
from .prompts import get_prompt

__all__ = ["OutlineSource", "get_prompt"]