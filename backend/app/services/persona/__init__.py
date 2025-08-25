"""
Persona Service Package

This package implements the Mnemosyne persona system, providing:
- Four operational modes (Confidant, Mentor, Mediator, Guardian)
- Worldview adaptation based on philosophical traditions
- Context-aware mode switching
- Transparency through receipts
"""

from app.services.persona.base import (
    BasePersona,
    PersonaMode,
    PersonaContext,
    get_persona
)

from app.services.persona.worldview import (
    WorldviewAdapter,
    WorldviewProfile,
    PhilosophicalTradition,
    get_worldview_adapter
)

from app.services.persona.manager import PersonaManager

__all__ = [
    "BasePersona",
    "PersonaMode", 
    "PersonaContext",
    "get_persona",
    "WorldviewAdapter",
    "WorldviewProfile",
    "PhilosophicalTradition",
    "get_worldview_adapter",
    "PersonaManager"
]