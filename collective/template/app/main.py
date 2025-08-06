"""
Chatter Knowledge Platform API

AI Agents: This is the main entry point. Key endpoints:
- /sources: List available data sources
- /ingest/{source}: Ingest data from a source
- /search: Search across ingested knowledge
- /health: System health check
"""

import os
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import structlog

from sources import list_sources, get_source
from storage.vectors import VectorStore
from processors.summarizer import DocumentSummarizer

# Configure logging
logger = structlog.get_logger()

# Initialize FastAPI
app = FastAPI(
    title="Chatter Knowledge Platform",
    description="AI-agent-friendly knowledge ingestion and retrieval",
    version="0.1.0"
)

# Initialize components (in production, use dependency injection)
vector_store = None
summarizer = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global vector_store, summarizer
    
    logger.info("Initializing Chatter Knowledge Platform")
    
    # Initialize vector store
    vector_store = VectorStore()
    await vector_store.initialize()
    
    # Initialize processor
    summarizer = DocumentSummarizer()
    
    logger.info("Initialization complete")


# Request/Response models
class IngestRequest(BaseModel):
    """Request to ingest data from a source."""
    source: str
    query_type: str = "list_documents"
    query_params: Dict[str, Any] = {}
    process: bool = True
    collection: Optional[str] = None


class SearchRequest(BaseModel):
    """Search request across knowledge base."""
    query: str
    collections: Optional[List[str]] = None
    limit: int = 10


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Chatter Knowledge Platform",
        "version": "0.1.0",
        "docs": "/docs",
        "sources": "/sources"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    AI Agents: Use this to verify system status.
    """
    health_status = {
        "status": "healthy",
        "services": {
            "api": "up",
            "vector_store": "up" if vector_store and await vector_store.health_check() else "down",
            "postgres": "up",  # TODO: Implement actual check
            "redis": "up"      # TODO: Implement actual check
        }
    }
    
    # Overall health
    all_up = all(status == "up" for status in health_status["services"].values())
    health_status["status"] = "healthy" if all_up else "degraded"
    
    return health_status


@app.get("/sources")
async def get_sources():
    """
    List available data sources.
    
    Returns information about each source including:
    - Description
    - Required authentication
    - Available queries
    
    AI Agents: Start here to discover what sources are available.
    """
    return list_sources()


@app.post("/ingest/{source_name}")
async def ingest_data(
    source_name: str,
    request: IngestRequest,
    background_tasks: BackgroundTasks
):
    """
    Ingest data from a specified source.
    
    AI Agents: This triggers data ingestion. Example:
        POST /ingest/outline
        {
            "query_type": "list_documents",
            "query_params": {"limit": 50},
            "process": true
        }
    """
    try:
        # Get source
        source = get_source(source_name)
        
        # Test connection
        if not source.test_connection():
            raise HTTPException(status_code=503, detail=f"Cannot connect to {source_name}")
        
        # Execute query
        query_method = getattr(source, request.query_type, None)
        if not query_method:
            raise HTTPException(
                status_code=400, 
                detail=f"Query type '{request.query_type}' not available for {source_name}"
            )
        
        # Get data
        data = query_method(**request.query_params)
        
        # Process in background if requested
        if request.process:
            background_tasks.add_task(
                process_and_store,
                source_name=source_name,
                data=data,
                collection=request.collection
            )
            
            return {
                "status": "ingestion_started",
                "source": source_name,
                "items_queued": len(data),
                "message": "Processing in background"
            }
        else:
            return {
                "status": "data_retrieved",
                "source": source_name,
                "items": data
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ingestion error for {source_name}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search")
async def search_knowledge(request: SearchRequest):
    """
    Search across ingested knowledge.
    
    AI Agents: Search the knowledge base. Example:
        POST /search
        {
            "query": "deployment process",
            "collections": ["outline_documents"],
            "limit": 10
        }
    """
    try:
        results = await vector_store.search(
            query=request.query,
            collections=request.collections,
            limit=request.limit
        )
        
        return {
            "query": request.query,
            "results": results,
            "total": len(results)
        }
        
    except Exception as e:
        logger.error("Search error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/collections")
async def list_collections():
    """List all vector collections with statistics."""
    collections = await vector_store.list_collections()
    return {"collections": collections}


# Background task functions
async def process_and_store(
    source_name: str, 
    data: List[Dict[str, Any]], 
    collection: Optional[str] = None
):
    """
    Process and store data in background.
    
    AI Agents: This runs automatically after ingestion.
    """
    logger.info(f"Processing {len(data)} items from {source_name}")
    
    try:
        # Get source for configuration
        source = get_source(source_name)
        collections = source.get_collections()
        
        # Determine target collection
        if not collection and collections:
            collection = collections[0].name
        
        # Process each item
        processed_items = []
        for item in data:
            # Summarize if it's a document
            if "text" in item or "content" in item:
                summary = await summarizer.process(
                    content=item.get("text") or item.get("content"),
                    metadata=item
                )
                processed_items.append(summary)
            else:
                processed_items.append(item)
        
        # Store in vector database
        await vector_store.add_documents(
            documents=processed_items,
            collection=collection
        )
        
        logger.info(f"Stored {len(processed_items)} items in {collection}")
        
    except Exception as e:
        logger.error(f"Processing error for {source_name}", error=str(e))


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error("Unhandled exception", error=str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)