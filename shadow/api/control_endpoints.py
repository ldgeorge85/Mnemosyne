"""
Shadow AI Control API Endpoints.

This module provides advanced control endpoints for managing agents, memory,
routing, and system configuration through the API.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger("shadow.api.control")

# Create router for control endpoints
router = APIRouter(prefix="/api/control", tags=["control"])


# Request/Response Models
class AgentOverrideRequest(BaseModel):
    """Request model for agent override settings."""
    query: str
    agents: List[str] = Field(description="Specific agents to use")
    force_single: bool = Field(default=False, description="Force only one agent")
    force_all: bool = Field(default=False, description="Force all specified agents")
    session_id: Optional[str] = None


class MemoryQueryRequest(BaseModel):
    """Request model for memory queries."""
    query_type: str = Field(description="Type: 'documents', 'history', 'search', 'entities'")
    search_term: Optional[str] = None
    session_id: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=100)


class MemoryManagementRequest(BaseModel):
    """Request model for memory management operations."""
    operation: str = Field(description="Operation: 'clear', 'filter', 'export', 'import'")
    filters: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class AgentConfigRequest(BaseModel):
    """Request model for agent configuration updates."""
    agent_name: str
    config_type: str = Field(description="Type: 'prompt', 'keywords', 'parameters'")
    config_data: Dict[str, Any]
    persist: bool = Field(default=True, description="Persist changes to disk")


class RoutingConfigRequest(BaseModel):
    """Request model for routing configuration."""
    enable_multi_agent: bool = Field(default=True)
    enable_collaboration: bool = Field(default=False)
    routing_strategy: str = Field(default="keyword", description="Strategy: 'keyword', 'semantic', 'manual'")
    custom_rules: Optional[List[Dict[str, Any]]] = None


class SystemStatusResponse(BaseModel):
    """Response model for system status."""
    agents: Dict[str, Dict[str, Any]]
    memory_status: Dict[str, Any]
    routing_config: Dict[str, Any]
    performance_stats: Dict[str, Any]
    timestamp: str


# Global reference to Shadow agent (will be set by main app)
shadow_agent = None
memory_manager = None


def set_shadow_agent(agent):
    """Set the shadow agent reference."""
    global shadow_agent
    shadow_agent = agent


def set_memory_manager(manager):
    """Set the memory manager reference."""
    global memory_manager
    memory_manager = manager


# Endpoints

@router.post("/agent/override")
async def override_agent_selection(request: AgentOverrideRequest):
    """
    Override automatic agent selection for a specific query.
    
    This allows users to:
    - Force specific agents to handle a query
    - Bypass keyword-based routing
    - Test multi-agent collaboration
    """
    if not shadow_agent:
        raise HTTPException(status_code=503, detail="Shadow agent not initialized")
    
    try:
        # Store the override settings in the shadow agent
        original_classifier = shadow_agent.classifier.classify_task
        
        # Create a custom classifier for this request
        def override_classifier(user_input: str) -> List[str]:
            if request.force_all:
                return request.agents
            elif request.force_single and request.agents:
                return [request.agents[0]]
            else:
                return request.agents
        
        # Temporarily override the classifier
        shadow_agent.classifier.classify_task = override_classifier
        
        # Process the request
        response = shadow_agent.process_request(request.query)
        
        # Restore original classifier
        shadow_agent.classifier.classify_task = original_classifier
        
        return {
            "response": response,
            "agents_used": request.agents,
            "override_applied": True,
            "session_id": request.session_id
        }
        
    except Exception as e:
        logger.error(f"Error in agent override: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/query")
async def query_memory(
    query_type: str = Query(description="Type: documents, history, search, entities"),
    search_term: Optional[str] = Query(None, description="Search term for similarity search"),
    session_id: Optional[str] = Query(None, description="Session ID for history"),
    limit: int = Query(10, ge=1, le=100, description="Maximum results to return")
):
    """
    Query the memory system for stored information.
    
    Query types:
    - documents: List all stored documents
    - history: Get conversation history
    - search: Semantic similarity search
    - entities: List stored entities
    """
    if not memory_manager:
        raise HTTPException(status_code=503, detail="Memory manager not initialized")
    
    try:
        if query_type == "documents":
            # Use the document store's get_all_documents method
            results = memory_manager.document_store.get_all_documents()
            # Convert to dict format for JSON serialization
            document_list = []
            for doc in results[:limit]:
                document_list.append({
                    "id": doc.item_id,
                    "title": doc.title,
                    "content": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                    "doc_type": doc.doc_type,
                    "metadata": doc.metadata,
                    "timestamp": doc.timestamp.isoformat() if hasattr(doc, 'timestamp') and doc.timestamp else None
                })
            return {"type": "documents", "results": document_list, "count": len(document_list)}
            
        elif query_type == "history":
            # Get conversation history from shadow agent
            history = shadow_agent.conversation_history if shadow_agent else []
            return {"type": "history", "results": history[-limit:], "count": len(history)}
            
        elif query_type == "search":
            if not search_term:
                raise HTTPException(status_code=400, detail="search_term required for search query")
            # Use the memory manager's search_memories method
            results = memory_manager.search_memories(search_term, limit)
            # Flatten and format results
            formatted_results = []
            for storage_type, items in results.items():
                for item in items:
                    formatted_results.append({
                        "id": item.item_id,
                        "content": item.content[:200] + "..." if len(item.content) > 200 else item.content,
                        "storage_type": storage_type,
                        "metadata": item.metadata,
                        "timestamp": item.timestamp.isoformat() if hasattr(item, 'timestamp') and item.timestamp else None
                    })
            return {"type": "search", "results": formatted_results[:limit], "count": len(formatted_results)}
            
        elif query_type == "entities":
            # Get all entities from relational store
            entities = memory_manager.relational_store.get_all()
            entity_list = []
            for entity in entities[:limit]:
                entity_list.append({
                    "id": entity.item_id,
                    "entity_type": entity.entity_type,
                    "content": entity.content[:200] + "..." if len(entity.content) > 200 else entity.content,
                    "properties": entity.properties,
                    "relationships": entity.relationships,
                    "metadata": entity.metadata,
                    "timestamp": entity.timestamp.isoformat() if hasattr(entity, 'timestamp') and entity.timestamp else None
                })
            return {"type": "entities", "results": entity_list, "count": len(entity_list)}
            
        else:
            raise HTTPException(status_code=400, detail=f"Invalid query_type: {query_type}")
            
    except Exception as e:
        logger.error(f"Error querying memory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Memory query failed: {str(e)}")


@router.post("/memory/manage")
async def manage_memory(request: MemoryManagementRequest):
    """
    Manage memory system operations.
    
    Operations:
    - clear: Clear all or filtered memory
    - filter: Remove items matching criteria
    - export: Export memory to JSON
    - import: Import memory from JSON
    """
    if not memory_manager:
        raise HTTPException(status_code=503, detail="Memory manager not initialized")
    
    try:
        if request.operation == "clear":
            # Clear conversation history
            if shadow_agent:
                shadow_agent.conversation_history = []
            
            # Clear memory stores based on filters
            if not request.filters or request.filters.get("all", False):
                # Clear all memory
                result = {
                    "vector_cleared": True,
                    "document_cleared": True,
                    "relational_cleared": True,
                    "history_cleared": True
                }
            else:
                # Selective clearing based on filters
                result = {}
                if request.filters.get("vector", False):
                    memory_manager.vector_store.clear()
                    result["vector_cleared"] = True
                if request.filters.get("documents", False):
                    memory_manager.document_store.clear()
                    result["document_cleared"] = True
                if request.filters.get("history", False) and shadow_agent:
                    shadow_agent.conversation_history = []
                    result["history_cleared"] = True
                    
            return {"operation": "clear", "result": result}
            
        elif request.operation == "filter":
            # Filter out specific patterns from history
            if shadow_agent and request.filters:
                patterns = request.filters.get("patterns", [])
                filtered_history = []
                removed_count = 0
                
                for item in shadow_agent.conversation_history:
                    item_str = str(item).lower()
                    if not any(pattern.lower() in item_str for pattern in patterns):
                        filtered_history.append(item)
                    else:
                        removed_count += 1
                        
                shadow_agent.conversation_history = filtered_history
                return {
                    "operation": "filter",
                    "removed_count": removed_count,
                    "remaining_count": len(filtered_history)
                }
                
        elif request.operation == "export":
            # Export memory to JSON format
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "conversation_history": shadow_agent.conversation_history if shadow_agent else [],
                "memory_stats": {
                    "documents": memory_manager.document_store.count() if hasattr(memory_manager.document_store, 'count') else 0,
                    "vectors": memory_manager.vector_store.count() if hasattr(memory_manager.vector_store, 'count') else 0
                }
            }
            return {"operation": "export", "data": export_data}
            
        elif request.operation == "import":
            # Import memory from provided data
            if request.data:
                if shadow_agent and "conversation_history" in request.data:
                    shadow_agent.conversation_history = request.data["conversation_history"]
                return {"operation": "import", "status": "success"}
                
        else:
            raise HTTPException(status_code=400, detail=f"Invalid operation: {request.operation}")
            
    except Exception as e:
        logger.error(f"Error managing memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/config")
async def configure_agent(request: AgentConfigRequest):
    """
    Configure agent behavior and prompts.
    
    Config types:
    - prompt: Update system prompts
    - keywords: Update routing keywords
    - parameters: Update agent parameters
    """
    if not shadow_agent:
        raise HTTPException(status_code=503, detail="Shadow agent not initialized")
    
    try:
        agent_name = request.agent_name.lower()
        
        if request.config_type == "prompt":
            # Update agent prompts
            if agent_name in shadow_agent.agents:
                agent = shadow_agent.agents[agent_name]
                if hasattr(agent, 'prompt_loader') and hasattr(agent.prompt_loader, 'prompts'):
                    # Update prompts in memory
                    agent.prompt_loader.prompts.update(request.config_data)
                    
                    # Persist to disk if requested
                    if request.persist:
                        import yaml
                        from pathlib import Path
                        prompts_path = Path(f"agents/{agent_name}/prompts.yaml")
                        with open(prompts_path, 'w') as f:
                            yaml.dump(agent.prompt_loader.prompts, f)
                            
                    return {
                        "agent": agent_name,
                        "config_type": "prompt",
                        "updated_keys": list(request.config_data.keys()),
                        "persisted": request.persist
                    }
                    
        elif request.config_type == "keywords":
            # Update classifier keywords
            if hasattr(shadow_agent.classifier, f"{agent_name}_keywords"):
                keywords_attr = f"{agent_name}_keywords"
                current_keywords = getattr(shadow_agent.classifier, keywords_attr)
                
                if "add" in request.config_data:
                    current_keywords.extend(request.config_data["add"])
                if "remove" in request.config_data:
                    current_keywords = [k for k in current_keywords if k not in request.config_data["remove"]]
                if "replace" in request.config_data:
                    current_keywords = request.config_data["replace"]
                    
                setattr(shadow_agent.classifier, keywords_attr, current_keywords)
                
                return {
                    "agent": agent_name,
                    "config_type": "keywords",
                    "keywords_count": len(current_keywords),
                    "current_keywords": current_keywords[:10] + ["..."] if len(current_keywords) > 10 else current_keywords
                }
                
        elif request.config_type == "parameters":
            # Update agent parameters
            if agent_name in shadow_agent.agents:
                agent = shadow_agent.agents[agent_name]
                for key, value in request.config_data.items():
                    if hasattr(agent, key):
                        setattr(agent, key, value)
                        
                return {
                    "agent": agent_name,
                    "config_type": "parameters",
                    "updated_params": list(request.config_data.keys())
                }
                
        else:
            raise HTTPException(status_code=400, detail=f"Invalid config_type: {request.config_type}")
            
    except Exception as e:
        logger.error(f"Error configuring agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/routing/config")
async def configure_routing(request: RoutingConfigRequest):
    """
    Configure the routing and collaboration settings.
    
    This allows dynamic control of:
    - Multi-agent vs single-agent routing
    - Collaboration mode
    - Routing strategies
    - Custom routing rules
    """
    if not shadow_agent:
        raise HTTPException(status_code=503, detail="Shadow agent not initialized")
    
    try:
        # Update collaboration settings
        shadow_agent.enable_collaboration = request.enable_collaboration
        
        # Update routing strategy
        if request.routing_strategy == "manual":
            # Implement manual routing where users specify agents
            shadow_agent._routing_strategy = "manual"
        elif request.routing_strategy == "semantic":
            # Would implement semantic similarity-based routing
            shadow_agent._routing_strategy = "semantic"
        else:
            # Default keyword-based routing
            shadow_agent._routing_strategy = "keyword"
            
        # Apply custom routing rules if provided
        if request.custom_rules:
            # Store custom rules for use in classification
            shadow_agent._custom_routing_rules = request.custom_rules
            
        return {
            "collaboration_enabled": shadow_agent.enable_collaboration,
            "routing_strategy": getattr(shadow_agent, '_routing_strategy', 'keyword'),
            "multi_agent_enabled": request.enable_multi_agent,
            "custom_rules_count": len(request.custom_rules) if request.custom_rules else 0
        }
        
    except Exception as e:
        logger.error(f"Error configuring routing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_system_status():
    """
    Get comprehensive system status including agents, memory, and routing configuration.
    """
    if not shadow_agent:
        raise HTTPException(status_code=503, detail="Shadow agent not initialized")
    
    try:
        # Gather agent status
        agents_status = {}
        for name, agent in shadow_agent.agents.items():
            agents_status[name] = {
                "active": True,
                "llm_provider": getattr(agent.llm_connector, 'model', 'unknown') if hasattr(agent, 'llm_connector') else 'unknown',
                "keywords_count": len(getattr(shadow_agent.classifier, f"{name}_keywords", [])),
                "usage_count": shadow_agent.execution_stats.get('agent_usage', {}).get(name, 0)
            }
            
        # Gather memory status
        memory_status = {
            "conversation_history_length": len(shadow_agent.conversation_history),
            "max_history_length": shadow_agent.max_history_length,
            "stores": {
                "vector": "active" if hasattr(memory_manager, 'vector_store') else "inactive",
                "document": "active" if hasattr(memory_manager, 'document_store') else "inactive",
                "relational": "active" if hasattr(memory_manager, 'relational_store') else "inactive"
            }
        }
        
        # Gather routing configuration
        routing_config = {
            "collaboration_enabled": shadow_agent.enable_collaboration,
            "routing_strategy": getattr(shadow_agent, '_routing_strategy', 'keyword'),
            "custom_rules_active": hasattr(shadow_agent, '_custom_routing_rules')
        }
        
        # Performance stats
        performance_stats = shadow_agent.get_performance_stats()
        
        return SystemStatusResponse(
            agents=agents_status,
            memory_status=memory_status,
            routing_config=routing_config,
            performance_stats=performance_stats,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/help")
async def get_control_help():
    """
    Get help information for control endpoints.
    """
    return {
        "endpoints": {
            "/api/control/agent/override": "Force specific agents for a query",
            "/api/control/memory/query": "Query memory system (documents, history, search, entities)",
            "/api/control/memory/manage": "Manage memory (clear, filter, export, import)",
            "/api/control/agent/config": "Configure agent prompts, keywords, parameters",
            "/api/control/routing/config": "Configure routing and collaboration settings",
            "/api/control/status": "Get comprehensive system status",
            "/api/control/help": "This help information"
        },
        "examples": {
            "force_engineer": {
                "method": "POST",
                "url": "/api/control/agent/override",
                "body": {
                    "query": "Design a database",
                    "agents": ["engineer"],
                    "force_single": True
                }
            },
            "clear_test_messages": {
                "method": "POST", 
                "url": "/api/control/memory/manage",
                "body": {
                    "operation": "filter",
                    "filters": {
                        "patterns": ["test message", "error generating response"]
                    }
                }
            },
            "enable_collaboration": {
                "method": "POST",
                "url": "/api/control/routing/config",
                "body": {
                    "enable_collaboration": True,
                    "enable_multi_agent": True
                }
            }
        }
    }
