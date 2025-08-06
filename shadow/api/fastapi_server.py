"""
FastAPI server for the Shadow AI Agent System.

This module implements a simple REST API for interacting with the
Shadow orchestrator and its specialized agents.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sys
import os
import logging
import time
from typing import Dict, List, Optional
from pathlib import Path

# Add parent directory to path to allow imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import Shadow components
from orchestrator.shadow_agent import ShadowAgent
from agents.engineer.agent import EngineerAgent
from agents.librarian.agent import LibrarianAgent
from agents.priest.agent import PriestAgent
from orchestrator.memory_integration import OrchestratorMemory
from memory.memory_manager import MemoryManager
from memory.vector_memory import InMemoryVectorStore
from memory.document_store import InMemoryDocumentStore
from memory.relational_store import InMemoryRelationalStore
from utils.llm_connector import OpenAIConnector
from api.control_endpoints import router as control_router, set_shadow_agent, set_memory_manager
from api.session_endpoints import router as session_router, set_session_manager
from api.streaming_endpoints import router as streaming_router, set_streaming_references
from managers.session_manager import SessionManager
from storage.in_memory_session_store import InMemorySessionStore

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("shadow.api")


# Define request and response models
class ShadowRequest(BaseModel):
    """Request model for the Shadow API."""
    query: str
    session_id: Optional[str] = None
    metadata: Optional[Dict] = None

class ShadowResponse(BaseModel):
    """Response model for the Shadow API."""
    response: str
    session_id: str
    agents_used: Optional[List[str]] = None
    processing_time: Optional[float] = None
    metadata: Optional[Dict] = None

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    timestamp: str
    version: str
    agents: Dict[str, Dict[str, str]]


# Initialize the Shadow system with all agents and memory
def init_shadow_system():
    """
    Initialize the Shadow system with all agents, memory integration, and session management.
    
    Returns:
        Tuple of (ShadowAgent instance, MemoryManager instance, SessionManager instance)
    """
    logger.info("Initializing Shadow AI system...")
    
    # Initialize memory system
    vector_store = InMemoryVectorStore()
    document_store = InMemoryDocumentStore()
    relational_store = InMemoryRelationalStore()
    
    memory_manager = MemoryManager(
        vector_store=vector_store,
        document_store=document_store,
        relational_store=relational_store
    )
    
    orchestrator_memory = OrchestratorMemory(memory_manager)
    
    # Initialize agents
    engineer = EngineerAgent()
    librarian = LibrarianAgent()
    priest = PriestAgent()
    
    # Create Shadow orchestrator with agents and memory
    shadow = ShadowAgent(
        agents={
            "engineer": engineer,
            "librarian": librarian,
            "priest": priest
        },
        memory=orchestrator_memory
    )
    
    # Initialize session management
    session_store = InMemorySessionStore()
    session_manager = SessionManager(session_store, memory_manager)
    
    logger.info("Shadow AI system initialized successfully")
    return shadow, memory_manager, session_manager


# Create FastAPI app
app = FastAPI(
    title="Shadow AI Agent System",
    description="Multi-agent AI system with specialized cognitive agents",
    version="0.1.0"
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for React frontend
frontend_build_path = project_root / "frontend" / "build"
if frontend_build_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_build_path / "static")), name="static")
    logger.info(f"Mounted static files from {frontend_build_path / 'static'}")
else:
    logger.warning(f"Frontend build directory not found at {frontend_build_path}")

# Initialize the Shadow system
shadow_agent, memory_manager, session_manager = None, None, None

# Include routers
app.include_router(control_router)
app.include_router(session_router, prefix="/api/v1")
app.include_router(streaming_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Initialize control endpoint references when the server starts"""
    global shadow_agent, memory_manager, session_manager
    
    # Initialize the Shadow system
    shadow_agent, memory_manager, session_manager = init_shadow_system()
    
    # Set references for control endpoints
    set_shadow_agent(shadow_agent)
    set_memory_manager(memory_manager)
    set_session_manager(session_manager)
    set_streaming_references(shadow_agent, session_manager)
    
    logger.info("Shadow AI system endpoints initialized with control, session, and streaming support")


@app.get("/")
async def serve_react_app():
    """Serve the React frontend at root."""
    frontend_index = frontend_build_path / "index.html"
    if frontend_index.exists():
        return FileResponse(str(frontend_index))
    else:
        return {
            "name": "Shadow AI Agent System",
            "version": "0.1.0",
            "description": "Multi-agent AI system with specialized cognitive agents",
            "agents": ["engineer", "librarian", "priest"],
            "endpoints": ["/api/shadow", "/api/health"],
            "note": "Frontend not built. React app not available."
        }


@app.post("/api/shadow", response_model=ShadowResponse)
async def process_request(request: ShadowRequest):
    """
    Process a request through the Shadow system.
    
    Args:
        request: The Shadow request object
        
    Returns:
        ShadowResponse with the system's response
    """
    start_time = time.time()
    
    try:
        logger.info(f"Processing request: {request.query[:100]}...")
        
        # Process the request through the Shadow system
        response = shadow_agent.process_request(request.query)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Extract agents used from the response (simple heuristic)
        agents_used = []
        if "Technical Analysis" in response:
            agents_used.append("engineer")
        if "Information" in response:
            agents_used.append("librarian")
        if "Ethical" in response or "Philosophical" in response:
            agents_used.append("priest")
        
        # If no specific agent sections found, assume all were consulted
        if not agents_used:
            agents_used = ["engineer", "librarian", "priest"]
        
        return ShadowResponse(
            response=response,
            session_id=request.session_id or f"session_{int(time.time())}",
            agents_used=agents_used,
            processing_time=round(processing_time, 2),
            metadata={"request_length": len(request.query)}
        )
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Enhanced health check endpoint for frontend integration."""
    return HealthResponse(
        status="online",
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        version="0.1.0",
        agents={
            "engineer": {"status": "available", "description": "Technical problem-solving and design"},
            "librarian": {"status": "available", "description": "Information retrieval and research"},
            "priest": {"status": "available", "description": "Ethical reasoning and philosophy"}
        }
    )


if __name__ == "__main__":
    # For local development
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
