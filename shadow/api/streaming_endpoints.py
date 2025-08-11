"""
Streaming API endpoints for the Shadow AI system.

This module provides FastAPI endpoints for streaming chat responses
from the Shadow AI system.
"""

import logging
import time
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from orchestrator.shadow_agent import ShadowAgent
from managers.session_manager import SessionManager
from utils.streaming_llm_connector import StreamingOpenAIConnector
from api.fastapi_server import ShadowRequest, ShadowResponse

# Configure logging
logger = logging.getLogger("shadow.api.streaming")

# Create router
router = APIRouter()

# Global references
shadow_agent = None
session_manager = None


def get_shadow_agent() -> ShadowAgent:
    """Get the global Shadow agent instance."""
    if shadow_agent is None:
        raise HTTPException(
            status_code=503,
            detail="Shadow agent not initialized"
        )
    return shadow_agent


def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    if session_manager is None:
        raise HTTPException(
            status_code=503,
            detail="Session manager not initialized"
        )
    return session_manager


def set_streaming_references(shadow: ShadowAgent, sm: SessionManager):
    """Set the global references for streaming endpoints."""
    global shadow_agent, session_manager
    shadow_agent = shadow
    session_manager = sm
    logger.info("Streaming endpoint references initialized")


class StreamingChatRequest(BaseModel):
    """Request model for streaming chat."""
    query: str
    session_id: Optional[str] = None
    user_id: str
    metadata: Optional[Dict] = None


@router.post("/chat/stream")
async def streaming_chat(
    request: StreamingChatRequest,
    shadow: ShadowAgent = Depends(get_shadow_agent),
    sm: SessionManager = Depends(get_session_manager)
):
    """
    Stream a chat response from the Shadow AI system.
    
    Args:
        request: The streaming chat request
        shadow: The Shadow agent
        sm: The session manager
        
    Returns:
        A streaming response with the generated text
    """
    try:
        # Get or create session
        session_id = request.session_id
        if not session_id:
            # Create a new session if none provided
            session = await sm.create_session(request.user_id)
            session_id = session.id
            logger.info(f"Created new session {session_id} for streaming chat")
        else:
            # Verify session exists
            session = await sm.get_session(session_id)
            if not session:
                raise HTTPException(
                    status_code=404,
                    detail=f"Session {session_id} not found"
                )
        
        # Add user message to session
        await sm.add_message(
            session_id=session_id,
            role="user",
            content=request.query,
            metadata=request.metadata
        )
        
        # Get conversation context for the query
        context = await sm.get_conversation_context(session_id, request.query)
        
        # Process query to determine which agents to use
        start_time = time.time()
        classification = shadow.classify_request(request.query, context)
        
        # Get the primary agent for streaming
        primary_agent_name = classification["primary_agent"]
        primary_agent = shadow.agents.get(primary_agent_name)
        
        if not primary_agent:
            raise HTTPException(
                status_code=500,
                detail=f"Primary agent {primary_agent_name} not found"
            )
        
        # Create streaming connector for the primary agent
        if hasattr(primary_agent, "llm"):
            # Create streaming connector from the agent's LLM
            streaming_connector = StreamingOpenAIConnector(primary_agent.llm)
        else:
            # Create a new streaming connector
            streaming_connector = StreamingOpenAIConnector()
        
        # Get system prompt and prepare for streaming
        system_prompt = primary_agent.get_system_prompt()
        
        # Define the streaming response generator
        async def response_generator():
            """Generate streaming response chunks."""
            full_response = ""
            
            # Stream header with metadata
            yield f"data: {{\n"
            yield f"data: \"event\": \"metadata\",\n"
            yield f"data: \"data\": {{\n"
            yield f"data:   \"agent\": \"{primary_agent_name}\",\n"
            yield f"data:   \"session_id\": \"{session_id}\",\n"
            yield f"data:   \"confidence\": {classification.get('confidence', 0.0)}\n"
            yield f"data: }}\n"
            yield f"data: }}\n\n"
            
            # Stream the content
            async for chunk in streaming_connector.generate_text_stream(
                system_prompt=system_prompt,
                user_input=request.query,
                conversation_history=context.get("conversation_history", [])
            ):
                # Accumulate the full response
                full_response += chunk
                
                # Send the chunk as a server-sent event
                escaped_chunk = chunk.replace('"', '\\"')
                yield f"data: {{\n"
                yield f"data: \"event\": \"content\",\n"
                yield f"data: \"data\": \"{escaped_chunk}\"\n"
                yield f"data: }}\n\n"
            
            # Stream completion event
            processing_time = time.time() - start_time
            yield f"data: {{\n"
            yield f"data: \"event\": \"complete\",\n"
            yield f"data: \"data\": {{\n"
            yield f"data:   \"processing_time\": {processing_time}\n"
            yield f"data: }}\n"
            yield f"data: }}\n\n"
            
            # Save the assistant's response to the session
            await sm.add_message(
                session_id=session_id,
                role="assistant",
                content=full_response,
                agent=primary_agent_name,
                metadata={
                    "processing_time": processing_time,
                    "confidence": classification.get("confidence", 0.0)
                }
            )
        
        # Return a streaming response
        return StreamingResponse(
            response_generator(),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        logger.error(f"Error in streaming chat: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating streaming response: {str(e)}"
        )
