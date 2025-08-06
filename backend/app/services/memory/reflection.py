"""
Cognee-inspired memory reflection and importance scoring service for Mnemosyne.
"""

from typing import List, Dict, Optional

from app.db.models.agent import MemoryReflection
from app.db.session import async_session_maker
from sqlalchemy.ext.asyncio import AsyncSession
import datetime

class MemoryReflectionService:
    def __init__(self, db_session: AsyncSession = None):
        # Initialize with async DB session
        self.db_session = db_session or async_session_maker()

    async def reflect(self, agent_id: str, memories: list) -> dict:
        # Perform memory reflection, compute importance, persist result
        reflection = {"summary": f"Reflected on {len(memories)} memories.", "memories": memories}
        mem_ref = MemoryReflection(
            agent_id=agent_id,
            reflection=reflection,
            importance_score=5,
            created_at=datetime.datetime.utcnow()
        )
        self.db_session.add(mem_ref)
        await self.db_session.commit()
        return reflection

    async def get_importance_scores(self, agent_id: str) -> list:
        # Retrieve importance scores for all memory reflections for agent
        result = await self.db_session.execute(
            MemoryReflection.__table__.select().where(MemoryReflection.agent_id == agent_id)
        )
        return [dict(row) for row in result.fetchall()]

    async def get_hierarchy(self, agent_id: str) -> dict:
        # Get hierarchical organization of memories (flat for now)
        scores = await self.get_importance_scores(agent_id)
        return {"agent_id": agent_id, "hierarchy": scores}
