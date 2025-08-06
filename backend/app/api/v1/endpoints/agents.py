"""
API endpoints for agent orchestration (Phase 3, CrewAI integration).
"""
from fastapi import APIRouter, HTTPException
from typing import List

from app.services.agent.agent_manager import AgentManager
from fastapi import Depends, HTTPException, APIRouter, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session_maker

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("/")
async def create_agent(config: dict = Body(...)):
    """
    Define a new agent (role, config, capabilities).
    """
    async with async_session_maker() as db:
        manager = AgentManager(db)
        agent_id = await manager.create_agent(config)
    return {"agent_id": agent_id}

@router.post("/{id}/link")
async def link_agents(id: str, child_id: str = Body(...)):
    """
    Link agents (parent/child, team structures).
    """
    async with async_session_maker() as db:
        manager = AgentManager(db)
        await manager.link_agents(id, child_id)
    return {"message": "Agents linked"}

@router.post("/{id}/task")
async def assign_task(id: str, task: dict = Body(...)):
    """
    Assign a task to an agent.
    """
    async with async_session_maker() as db:
        manager = AgentManager(db)
        log_id = await manager.assign_task(id, task)
    return {"log_id": log_id}

@router.get("/{id}/status")
async def get_status(id: str):
    """
    Monitor agent/task status.
    """
    async with async_session_maker() as db:
        manager = AgentManager(db)
        status_dict = await manager.get_status(id)
    if "error" in status_dict:
        raise HTTPException(status_code=404, detail=status_dict["error"])
    return status_dict

@router.get("/")
async def list_agents():
    """
    List all agents and their state.
    """
    async with async_session_maker() as db:
        manager = AgentManager(db)
        agents = await manager.list_agents()
    return {"agents": agents}

@router.post("/{id}/spawn")
async def spawn_subagent(id: str, config: dict = Body(...)):
    """
    Create sub-agents recursively.
    """
    async with async_session_maker() as db:
        manager = AgentManager(db)
        subagent_id = await manager.spawn_subagent(id, config)
    return {"subagent_id": subagent_id}

@router.get("/{id}/logs")
async def get_logs(id: str):
    """
    Retrieve agent/task logs.
    """
    async with async_session_maker() as db:
        manager = AgentManager(db)
        logs = await manager.get_logs(id)
    return {"logs": logs}
