"""
Agent orchestration endpoints for Mnemosyne Protocol
"""

from typing import List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from api.deps import get_db, get_current_active_user
from models.user import User
from models.reflection import Reflection, AgentType
from services.agent_service import AgentService
from agents.orchestrator import AgentOrchestrator

router = APIRouter()


# Pydantic models
class ReflectionRequest(BaseModel):
    memory_id: str
    agent_types: Optional[List[str]] = None
    async_mode: bool = True


class ReflectionResponse(BaseModel):
    id: str
    memory_id: str
    agent_type: str
    content: str
    confidence: float
    metadata: dict
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrchestrationRequest(BaseModel):
    task: str = Field(..., min_length=1, max_length=5000)
    agents: Optional[List[str]] = None
    max_iterations: int = Field(3, ge=1, le=10)


class AgentStatus(BaseModel):
    agent_type: str
    status: str
    last_activity: Optional[datetime]
    current_task: Optional[str]


@router.get("/", response_model=List[dict])
async def list_available_agents(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    List all available agent types
    """
    agents = [
        {
            "type": AgentType.ENGINEER.value,
            "name": "Engineer",
            "description": "Technical analysis and system design",
            "capabilities": ["code_analysis", "architecture", "debugging"]
        },
        {
            "type": AgentType.LIBRARIAN.value,
            "name": "Librarian",
            "description": "Knowledge organization and retrieval",
            "capabilities": ["research", "categorization", "citation"]
        },
        {
            "type": AgentType.PHILOSOPHER.value,
            "name": "Philosopher",
            "description": "Deep thinking and pattern recognition",
            "capabilities": ["ethics", "meaning", "patterns"]
        },
        {
            "type": AgentType.MYSTIC.value,
            "name": "Mystic",
            "description": "Hidden connections and intuition",
            "capabilities": ["symbolism", "synchronicity", "emergence"]
        },
        {
            "type": AgentType.GUARDIAN.value,
            "name": "Guardian",
            "description": "Security and protection",
            "capabilities": ["threat_analysis", "privacy", "boundaries"]
        }
    ]
    
    # Check user's initiation level for advanced agents
    if current_user.initiation_level.value >= 2:  # FRAGMENTOR or higher
        agents.extend([
            {
                "type": "STRATEGIST",
                "name": "Strategist",
                "description": "Long-term planning and resource allocation",
                "capabilities": ["planning", "optimization", "prediction"]
            },
            {
                "type": "HEALER",
                "name": "Healer",
                "description": "Integration and wholeness",
                "capabilities": ["trauma_processing", "integration", "balance"]
            }
        ])
    
    return agents


@router.post("/{agent_type}/reflect", response_model=ReflectionResponse)
async def trigger_reflection(
    agent_type: str,
    request: ReflectionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Trigger a specific agent to reflect on a memory
    """
    # Validate agent type
    try:
        agent_enum = AgentType(agent_type.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid agent type: {agent_type}"
        )
    
    agent_service = AgentService(db)
    
    if request.async_mode:
        # Queue for background processing
        background_tasks.add_task(
            agent_service.trigger_agent_reflection,
            memory_id=request.memory_id,
            agent_type=agent_enum,
            user_id=current_user.id
        )
        
        # Return placeholder response
        return ReflectionResponse(
            id=str(uuid.uuid4()),
            memory_id=request.memory_id,
            agent_type=agent_type,
            content="Reflection queued for processing",
            confidence=0.0,
            metadata={"status": "processing"},
            created_at=datetime.utcnow()
        )
    else:
        # Process synchronously
        reflection = await agent_service.trigger_agent_reflection(
            memory_id=request.memory_id,
            agent_type=agent_enum,
            user_id=current_user.id
        )
        
        if not reflection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Memory not found or not authorized"
            )
        
        return reflection


@router.post("/orchestrate")
async def orchestrate_agents(
    request: OrchestrationRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Orchestrate multiple agents to work on a complex task
    """
    orchestrator = AgentOrchestrator(db)
    
    # Determine which agents to use
    if request.agents:
        agent_types = []
        for agent_str in request.agents:
            try:
                agent_types.append(AgentType(agent_str.upper()))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid agent type: {agent_str}"
                )
    else:
        # Auto-select agents based on task
        agent_types = await orchestrator.select_agents_for_task(request.task)
    
    # Execute orchestration
    result = await orchestrator.orchestrate(
        task=request.task,
        agent_types=agent_types,
        user_id=current_user.id,
        max_iterations=request.max_iterations
    )
    
    return {
        "task": request.task,
        "agents_used": [a.value for a in agent_types],
        "iterations": result.get("iterations", 0),
        "result": result.get("result"),
        "reflections": result.get("reflections", []),
        "metadata": result.get("metadata", {})
    }


@router.get("/{agent_type}/status", response_model=AgentStatus)
async def get_agent_status(
    agent_type: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get the current status of a specific agent
    """
    # Validate agent type
    try:
        agent_enum = AgentType(agent_type.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid agent type: {agent_type}"
        )
    
    agent_service = AgentService(db)
    status = await agent_service.get_agent_status(agent_enum, current_user.id)
    
    return AgentStatus(
        agent_type=agent_type,
        status=status.get("status", "idle"),
        last_activity=status.get("last_activity"),
        current_task=status.get("current_task")
    )


@router.get("/reflections", response_model=List[ReflectionResponse])
async def get_user_reflections(
    limit: int = 20,
    agent_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get all reflections for the current user
    """
    query = select(Reflection).where(Reflection.user_id == current_user.id)
    
    if agent_type:
        try:
            agent_enum = AgentType(agent_type.upper())
            query = query.where(Reflection.agent_type == agent_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid agent type: {agent_type}"
            )
    
    query = query.order_by(Reflection.created_at.desc()).limit(limit)
    
    result = await db.execute(query)
    reflections = result.scalars().all()
    
    return reflections