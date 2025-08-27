"""
Agentic Chat Endpoint with ReAct Pattern

Implements intelligent multi-action planning and parallel execution
for enhanced chat responses.
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, AsyncGenerator, Dict, Any
import json
import asyncio
import time
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.auth.manager import get_current_user, get_optional_user
from app.core.auth.base import AuthUser
from app.core.logging import get_logger
from app.db.session import get_async_db

from app.services.agentic import AgenticFlowController, MnemosyneAction
from app.services.agentic.actions import ActionPayload
from app.services.llm.service import LLMService
from app.services.receipt_service import ReceiptService
from app.services.persona.manager import PersonaManager
from app.services.memory.context import MemoryContextService
from app.db.models.receipt import ReceiptType

logger = get_logger(__name__)
router = APIRouter()


class AgenticChatRequest(BaseModel):
    """Request model for agentic chat."""
    messages: List[Dict[str, str]]
    use_agentic: bool = True  # Allow opting out
    max_iterations: int = 3
    stream_status: bool = True  # Stream status updates
    include_reasoning: bool = True  # Include reasoning in response
    parallel_actions: bool = True  # Execute actions in parallel


class AgenticChatResponse(BaseModel):
    """Response model for agentic chat."""
    response: str
    reasoning: Optional[str] = None
    actions_taken: List[Dict[str, Any]] = []
    suggestions: List[Dict[str, Any]] = []
    receipt_id: Optional[str] = None
    persona_mode: str
    duration_ms: int


async def stream_agentic_response(
    query: str,
    messages: List[Dict[str, str]],
    user_id: Optional[str],
    db: AsyncSession,
    request_params: AgenticChatRequest
) -> AsyncGenerator[str, None]:
    """
    Stream agentic chat response with status updates.
    
    Yields Server-Sent Events with different event types:
    - status: Status updates during processing
    - content: Actual response content
    - reasoning: Reasoning explanation
    - suggestions: Proactive suggestions
    - done: Completion signal
    """
    start_time = time.time()
    
    # Initialize services
    llm_service = LLMService()
    receipt_service = ReceiptService(db)
    persona_manager = PersonaManager(db)
    memory_service = MemoryContextService(db)
    
    # Initialize flow controller
    flow_controller = AgenticFlowController(
        llm_service=llm_service,
        receipt_service=receipt_service
    )
    
    # Initialize persona for user
    if user_id:
        await persona_manager.initialize_for_user(user_id)
    
    # Build context
    context = {
        "user_id": user_id,
        "messages": messages,
        "max_iterations": request_params.max_iterations,
        "parallel": request_params.parallel_actions,
        "query": query,  # Add the query to context for later use
        "original_query": query  # Keep original for reference
    }
    
    # Get memory context if user is authenticated
    if user_id:
        # Yield status
        yield f"event: status\ndata: {json.dumps({'status': 'Retrieving relevant memories...'})}\n\n"
        
        relevant_memories = await memory_service.get_relevant_memories(
            query=query,
            user_id=user_id,
            limit=5,
            score_threshold=0.3
        )
        
        if relevant_memories:
            # get_relevant_memories returns List[Dict], not ORM objects
            context["memories"] = [
                {
                    "id": str(m.get("memory_id", m.get("id", ""))),
                    "content": m.get("content", ""),
                    "type": m.get("memory_type", "general"),
                    "importance": m.get("importance_score", 0.5)
                }
                for m in relevant_memories
            ]
            yield f"event: status\ndata: {json.dumps({'status': f'Found {len(relevant_memories)} relevant memories'})}\n\n"
    
    # Use LLM to select persona mode (replacing keywords)
    yield f"event: status\ndata: {json.dumps({'status': 'Selecting optimal persona mode...'})}\n\n"
    
    selected_mode = await persona_manager.select_mode_llm(query, context)
    
    if persona_manager.persona.current_mode != selected_mode:
        await persona_manager.switch_mode(selected_mode, "Agentic analysis")
    
    context["persona_mode"] = selected_mode.value
    
    yield f"event: status\ndata: {json.dumps({'status': f'Activated {selected_mode.value} mode'})}\n\n"
    
    # Execute agentic flow
    try:
        # Custom streaming for status updates
        iteration = 0
        max_iterations = request_params.max_iterations
        
        # Initialize action plan
        from app.services.agentic.actions import ActionPlan
        plan = ActionPlan(
            query=query,
            context=context,
            actions=[], 
            reasoning="",
            parallel=request_params.parallel_actions,
            max_iterations=request_params.max_iterations
        )
        
        while iteration < max_iterations:
            iteration += 1
            
            # Step 1: Reasoning
            yield f"event: status\ndata: {json.dumps({'status': f'Analyzing query (iteration {iteration})...'})}\n\n"
            
            reasoning = await flow_controller.reason_about_query(query, context, plan)
            plan.reasoning = reasoning
            
            if request_params.include_reasoning and iteration == 1:
                yield f"event: reasoning\ndata: {json.dumps({'reasoning': reasoning[:500]})}\n\n"
            
            # Step 2: Planning
            yield f"event: status\ndata: {json.dumps({'status': 'Planning actions...'})}\n\n"
            
            actions = await flow_controller.plan_actions(reasoning, context)
            plan.actions = actions
            
            # Show planned actions
            action_names = [a.action for a in actions]
            action_list = ", ".join(action_names)
            yield f"event: status\ndata: {json.dumps({'status': f'Executing {len(actions)} actions: {action_list}'})}\n\n"
            
            # Check for completion
            if any(a.action == MnemosyneAction.DONE for a in actions):
                break
            
            # Step 3: Parallel execution
            if request_params.parallel_actions and len(actions) > 1:
                tasks = [
                    flow_controller.execute_action(action, context, user_id)
                    for action in actions
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)
            else:
                results = []
                for action in actions:
                    result = await flow_controller.execute_action(action, context, user_id)
                    results.append(result)
            
            # Update context with results
            context["previous_results"] = [r for r in results if not isinstance(r, Exception)]
            
            # Check if more needed
            needs_more = await flow_controller.needs_more_info(results, context)
            
            if not needs_more:
                break
        
        # Generate final response
        yield f"event: status\ndata: {json.dumps({'status': 'Generating response...'})}\n\n"
        
        # Get enhanced prompt and LLM config for final response
        system_prompt = persona_manager.get_enhanced_prompt()
        llm_config = persona_manager.get_llm_config(settings.LLM_MODEL_PROFILE)
        
        # Add action results to the conversation context if any
        if context.get("previous_results"):
            # Create a system message with the task results
            task_results_msg = {
                "role": "system", 
                "content": f"Action results from system: {json.dumps(context['previous_results'], default=str)}"
            }
            messages = messages + [task_results_msg]
        
        # Handle system prompt based on mode
        if llm_config.get("system_prompt_mode") == "embedded":
            # For models like Gemma that don't support separate system prompt
            # Prepend system prompt to first user message
            modified_messages = []
            for i, msg in enumerate(messages):
                if i == 0 and msg.get("role") == "user":
                    modified_messages.append({
                        "role": "user",
                        "content": f"{system_prompt}\n\n{msg['content']}"
                    })
                else:
                    modified_messages.append(msg)
            messages_to_send = modified_messages
            system_to_send = None
        else:
            # Use separate system prompt (default)
            messages_to_send = messages
            system_to_send = system_prompt + "\n\nIMPORTANT: Provide only a natural conversational response. Do not include memory logs, JSON, or any technical formatting."
        
        # Stream the actual response with proper temperature
        async for chunk in llm_service.stream_complete(
            messages=messages_to_send,
            system=system_to_send,
            temperature=llm_config.get("temperature"),
            **{k: v for k, v in llm_config.items() if k not in ["temperature", "system_prompt_mode", "system_prompt_prefix"]}
        ):
            if chunk:
                yield f"event: content\ndata: {json.dumps({'content': chunk})}\n\n"
        
        # Generate suggestions
        yield f"event: status\ndata: {json.dumps({'status': 'Generating suggestions...'})}\n\n"
        
        suggestions = await flow_controller.get_proactive_suggestions(
            plan.actions,  # Use plan.actions which persists outside the loop
            context.get("previous_results", []),
            context
        )
        
        if suggestions:
            yield f"event: suggestions\ndata: {json.dumps({'suggestions': suggestions})}\n\n"
        
        # Create final receipt
        if user_id:
            receipt = await flow_controller.create_decision_receipt(
                reasoning=reasoning,
                actions=plan.actions,  # Use plan.actions which persists
                results=context.get("previous_results", []),
                user_id=user_id,
                duration_ms=int((time.time() - start_time) * 1000)
            )
            
            if receipt:
                yield f"event: receipt\ndata: {json.dumps({'receipt_id': str(receipt.id)})}\n\n"
        
        # Send completion
        duration_ms = int((time.time() - start_time) * 1000)
        yield f"event: done\ndata: {json.dumps({'duration_ms': duration_ms, 'iterations': iteration})}\n\n"
        
    except Exception as e:
        logger.error(f"Agentic flow error: {e}")
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"


@router.post("/chat/agentic/stream")
async def stream_agentic_chat(
    request: AgenticChatRequest,
    user: AuthUser = Depends(get_current_user if settings.AUTH_REQUIRED else get_optional_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Streaming agentic chat with ReAct pattern.
    
    Features:
    - LLM-driven persona selection
    - Parallel action execution
    - Memory context retrieval
    - Proactive suggestions
    - Transparent reasoning receipts
    - Real-time status updates via SSE
    """
    # Extract last user message as query
    logger.info(f"Received agentic request with {len(request.messages)} messages")
    logger.info(f"Message types: {[type(m).__name__ for m in request.messages]}")
    if request.messages:
        logger.info(f"First message: {request.messages[0]}")
    
    query = ""
    for msg in reversed(request.messages):
        # Handle both dict and object formats
        if isinstance(msg, dict):
            if msg.get("role") == "user":
                query = msg.get("content", "")
                break
        else:
            if getattr(msg, "role", None) == "user":
                query = getattr(msg, "content", "")
                break
    
    if not query:
        # More helpful error message
        user_messages = [msg for msg in request.messages if isinstance(msg, dict) and msg.get("role") == "user"]
        raise HTTPException(
            status_code=400, 
            detail=f"No user message found. Messages received: {len(request.messages)}, User messages: {len(user_messages)}. Please send a user message to use agentic mode."
        )
    
    user_id = str(user.user_id) if user else None
    
    # Return SSE stream
    return StreamingResponse(
        stream_agentic_response(
            query=query,
            messages=request.messages,
            user_id=user_id,
            db=db,
            request_params=request
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.post("/chat/agentic/complete")
async def complete_agentic_chat(
    request: AgenticChatRequest,
    user: AuthUser = Depends(get_current_user if settings.AUTH_REQUIRED else get_optional_user),
    db: AsyncSession = Depends(get_async_db)
) -> AgenticChatResponse:
    """
    Non-streaming agentic chat endpoint.
    
    Returns complete response with all reasoning and actions.
    """
    # Extract query
    query = ""
    for msg in reversed(request.messages):
        if msg.get("role") == "user":
            query = msg.get("content", "")
            break
    
    if not query:
        raise HTTPException(status_code=400, detail="No user message found")
    
    user_id = str(user.user_id) if user else None
    
    # Initialize services
    llm_service = LLMService()
    receipt_service = ReceiptService(db) if user_id else None
    flow_controller = AgenticFlowController(
        llm_service=llm_service,
        receipt_service=receipt_service
    )
    
    # Build context
    persona_manager = PersonaManager(db)
    if user_id:
        await persona_manager.initialize_for_user(user_id)
    
    memory_service = MemoryContextService(db)
    context = {
        "user_id": user_id,
        "messages": request.messages,
        "max_iterations": request.max_iterations
    }
    
    # Add memory context
    if user_id:
        memories = await memory_service.get_relevant_memories(
            query=query,
            user_id=user_id,
            limit=5
        )
        if memories:
            context["memories"] = [
                {"id": str(m.id), "content": m.content}
                for m in memories
            ]
    
    # Execute flow
    result = await flow_controller.execute_flow(
        query=query,
        context=context,
        user_id=user_id,
        stream=False
    )
    
    # Get final persona mode
    persona_mode = persona_manager.persona.current_mode.value if persona_manager.persona.current_mode else "confidant"
    
    return AgenticChatResponse(
        response=json.dumps(result.get("response", {})),
        reasoning=result.get("reasoning") if request.include_reasoning else None,
        actions_taken=[],  # TODO: Extract from results
        suggestions=result.get("suggestions", []),
        receipt_id=result.get("receipt_id"),
        persona_mode=persona_mode,
        duration_ms=result.get("duration_ms", 0)
    )