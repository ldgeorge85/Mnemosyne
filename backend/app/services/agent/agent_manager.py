"""
AgentManager service for CrewAI-based agent orchestration in Mnemosyne.
Handles agent lifecycle, sub-agent spawning, task delegation, and DB-backed state.
"""

from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.agent import Agent, AgentLink, AgentLog
from app.db.session import async_session_maker
# from crewai import Crew  # Uncomment when CrewAI is available
import uuid
import datetime

class AgentManager:
    """
    Orchestrates agent lifecycle, sub-agent creation, task assignment, and state persistence.
    Integrates CrewAI for recursive agent orchestration.
    """
    def __init__(self, db_session: Optional[AsyncSession] = None):
        """
        Initialize the AgentManager with a DB session and (optionally) CrewAI integration.
        Args:
            db_session: Optional SQLAlchemy async session for DB operations.
        """
        self.db_session = db_session or async_session_maker()
        # self.crew = Crew()  # Placeholder for CrewAI integration

    async def create_agent(self, config: dict) -> str:
        """
        Create a new agent with the given configuration and persist to DB.
        Args:
            config: Dictionary with agent configuration parameters.
        Returns:
            The ID of the newly created agent.
        """
        agent_id = str(uuid.uuid4())
        agent = Agent(id=agent_id, name=config.get('name', 'Agent'), config=config, created_at=datetime.datetime.utcnow())
        self.db_session.add(agent)
        await self.db_session.commit()
        return agent_id

    async def link_agents(self, parent_id: str, child_id: str) -> None:
        """
        Link parent and child agents (hierarchical/team structures) in the DB.
        Args:
            parent_id: The ID of the parent agent.
            child_id: The ID of the child agent.
        """
        link = AgentLink(parent_id=parent_id, child_id=child_id)
        self.db_session.add(link)
        await self.db_session.commit()

    async def assign_task(self, agent_id: str, task: dict) -> str:
        """
        Assign a task to an agent and log the assignment.
        Args:
            agent_id: The ID of the agent.
            task: Task details as a dictionary.
        Returns:
            The ID of the created AgentLog entry.
        """
        log = AgentLog(agent_id=agent_id, log=task, timestamp=datetime.datetime.utcnow())
        self.db_session.add(log)
        await self.db_session.commit()
        return str(log.id)

    async def get_status(self, agent_id: str) -> dict:
        """
        Retrieve agent/task status from the DB.
        Args:
            agent_id: The ID of the agent.
        Returns:
            Dictionary with agent status and recent logs.
        """
        agent = await self.db_session.get(Agent, agent_id)
        if not agent:
            return {"error": "Agent not found"}
        logs = await self.db_session.execute(
            AgentLog.__table__.select().where(AgentLog.agent_id == agent_id)
        )
        log_list = [dict(row) for row in logs.fetchall()]
        return {"id": agent.id, "name": agent.name, "status": agent.status, "logs": log_list}

    async def spawn_subagent(self, agent_id: str, config: dict) -> str:
        """
        Recursively create a sub-agent under the given agent and link them.
        Args:
            agent_id: The ID of the parent agent.
            config: Configuration for the sub-agent.
        Returns:
            The ID of the newly created sub-agent.
        """
        subagent_id = await self.create_agent(config)
        await self.link_agents(agent_id, subagent_id)
        return subagent_id

    async def get_logs(self, agent_id: str) -> List[dict]:
        """
        Retrieve logs for an agent and its tasks from the DB.
        Args:
            agent_id: The ID of the agent.
        Returns:
            List of log entries as dictionaries.
        """
        logs = await self.db_session.execute(
            AgentLog.__table__.select().where(AgentLog.agent_id == agent_id)
        )
        return [dict(row) for row in logs.fetchall()]

    async def list_agents(self) -> List[dict]:
        """
        List all agents with their current state.
        Returns:
            List of agents with their details.
        """
        from sqlalchemy import select
        result = await self.db_session.execute(select(Agent))
        agents = result.scalars().all()
        return [
            {
                "id": agent.id,
                "name": agent.name,
                "status": agent.status,
                "created_at": agent.created_at.isoformat() if agent.created_at else None,
                "config": agent.config
            }
            for agent in agents
        ]
