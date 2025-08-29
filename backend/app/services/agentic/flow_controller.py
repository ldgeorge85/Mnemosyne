"""
Agentic Flow Controller.

Implements ReAct pattern for intelligent multi-action planning and execution.
Preserves user sovereignty through transparent reasoning and receipts.
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime
from uuid import uuid4

from app.core.logging import get_logger
from app.core.config import settings
from app.services.llm.service import LLMService
from app.services.receipt_service import ReceiptService
from app.db.models.receipt import ReceiptType
from app.db.session import get_db
from .actions import MnemosyneAction, ActionPayload, ActionResult, ActionPlan
from .executors import ActionExecutor

logger = get_logger(__name__)


class AgenticFlowController:
    """
    Orchestrates multi-agent reasoning with parallel execution.
    
    Uses ReAct (Reasoning + Acting) pattern to:
    1. Analyze user queries with LLM
    2. Plan multiple actions
    3. Execute in parallel
    4. Check if more needed
    5. Generate proactive suggestions
    6. Create transparency receipts
    """
    
    def __init__(
        self, 
        llm_service: LLMService,
        receipt_service: ReceiptService,
        executor: Optional[ActionExecutor] = None,
        llm_config: Optional[Dict[str, Any]] = None
    ):
        self.llm_service = llm_service
        self.receipt_service = receipt_service
        self.executor = executor or ActionExecutor()
        self.llm_config = llm_config or {}
        
    async def execute_flow(
        self, 
        query: str, 
        context: Dict[str, Any],
        user_id: Optional[str] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a complete agentic flow.
        
        Args:
            query: User's input query
            context: Current context (memories, persona, etc.)
            user_id: User ID for receipts
            stream: Whether to stream status updates
            
        Returns:
            Dict with response, suggestions, reasoning, and receipt_id
        """
        start_time = time.time()
        iteration = 0
        max_iterations = context.get('max_iterations', 3)
        
        # Initialize action plan
        plan = ActionPlan(query=query, context=context)
        
        while iteration < max_iterations:
            iteration += 1
            
            # Step 1: LLM reasons about what actions to take
            if stream:
                await self._stream_status(f"🤔 Analyzing query (iteration {iteration})...")
            
            reasoning = await self.reason_about_query(query, context, plan)
            plan.reasoning = reasoning
            
            # Step 2: Plan multiple actions based on reasoning
            if stream:
                await self._stream_status("📋 Planning actions...")
                
            actions = await self.plan_actions(reasoning, context)
            plan.actions = actions
            
            # Check if we're done
            if any(a.action == MnemosyneAction.DONE for a in actions):
                logger.info(f"Flow complete after {iteration} iterations")
                break
            
            # Step 3: Execute actions in parallel (or sequential if specified)
            if stream:
                action_names = [a.action.value if hasattr(a.action, 'value') else str(a.action) for a in actions]
                await self._stream_status(f"⚡ Executing {len(actions)} actions: {action_names}")
            
            action_names = [a.action.value if hasattr(a.action, 'value') else str(a.action) for a in actions]
            logger.info(f"About to execute {len(actions)} actions: {action_names}")
            for action in actions:
                action_name = action.action.value if hasattr(action.action, 'value') else str(action.action)
                logger.info(f"Action details: {action_name} with params: {action.parameters}")
                
            if plan.parallel and len(actions) > 1:
                # Parallel execution
                tasks = [
                    self.execute_action(action, context, user_id) 
                    for action in actions
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)
            else:
                # Sequential execution
                results = []
                for action in actions:
                    result = await self.execute_action(action, context, user_id)
                    results.append(result)
                    
            # Process results
            successful_results = [
                r for r in results 
                if isinstance(r, ActionResult) and r.success
            ]
            
            # Update context with results
            context['previous_actions'] = actions
            context['previous_results'] = successful_results
            
            # Step 4: Check if more information needed
            if stream:
                await self._stream_status("🔍 Checking if more needed...")
                
            needs_more = await self.needs_more_info(results, context)
            
            if not needs_more:
                logger.info(f"Sufficient information after {iteration} iterations")
                break
                
        # Step 5: Generate proactive suggestions
        if stream:
            await self._stream_status("💡 Generating suggestions...")
            
        suggestions = await self.get_proactive_suggestions(
            plan.actions, 
            context.get('previous_results', []), 
            context
        )
        
        # Step 6: Create receipt for transparency
        receipt = await self.create_decision_receipt(
            reasoning=plan.reasoning,
            actions=plan.actions,
            results=context.get('previous_results', []),
            user_id=user_id,
            duration_ms=int((time.time() - start_time) * 1000)
        )
        
        return {
            "response": self._format_response(context.get('previous_results', [])),
            "suggestions": suggestions,
            "reasoning": plan.reasoning,
            "receipt_id": receipt.id if receipt else None,
            "iterations": iteration,
            "duration_ms": int((time.time() - start_time) * 1000)
        }
    
    async def reason_about_query(
        self, 
        query: str, 
        context: Dict[str, Any],
        plan: ActionPlan
    ) -> str:
        """
        Use LLM to reason about the query and context.
        
        Returns reasoning text explaining what needs to be done.
        """
        logger.info("Starting reason_about_query...")
        # Load reasoning prompt
        # Try simpler prompt for InnoGPT-1
        try:
            prompt = await self._load_prompt("agentic_reasoning_simple")
        except:
            prompt = await self._load_prompt("agentic_reasoning")
        logger.info(f"Loaded prompt, length: {len(prompt)}")
        
        # Get available tools
        available_tools = await self._get_available_tools()
        
        # Build context for LLM
        llm_context = {
            "query": query,
            "current_persona": context.get("persona_mode", "confidant"),
            "available_memories": len(context.get("memories", [])),
            "active_tasks": len(context.get("tasks", [])),
            "previous_actions": [a.action for a in plan.actions],
            "available_actions": [a.value for a in MnemosyneAction],
            "available_tools": available_tools
        }
        
        # Get LLM reasoning (use limited tokens for efficiency)
        logger.info("Calling LLM for reasoning...")
        try:
            # Format the prompt with context
            try:
                formatted_prompt = prompt.format(**llm_context)
            except KeyError as ke:
                logger.error(f"Missing key in prompt template: {ke}")
                logger.error(f"Available keys: {llm_context.keys()}")
                logger.error(f"Prompt template: {prompt[:200]}")
                raise
                
            logger.info(f"Formatted prompt length: {len(formatted_prompt)}")
            logger.info(f"First 500 chars of prompt: {formatted_prompt[:500]}")
            
            response = await self.llm_service.complete(
                prompt=formatted_prompt,
                system="You are an intelligent assistant that reasons about user queries and determines what actions to take.",
                max_tokens=settings.OPENAI_MAX_TOKENS_REASONING,
                **self.llm_config  # Pass the LLM config (includes system_prompt_mode for InnoGPT)
            )
            logger.info(f"LLM response received: {response is not None}")
            reasoning_content = response.get("content", "") if response else ""
            logger.info(f"Reasoning content: {reasoning_content[:500]}")
            return reasoning_content
        except Exception as e:
            logger.error(f"Error in reason_about_query LLM call: {e}")
            return f"Error reasoning about query: {str(e)}"
    
    async def plan_actions(
        self, 
        reasoning: str, 
        context: Dict[str, Any]
    ) -> List[ActionPayload]:
        """
        Convert reasoning into specific actions to execute.
        
        Returns list of ActionPayload objects.
        """
        # Load action planning prompt
        prompt = await self._load_prompt("agentic_planning")
        
        # Get available tools
        available_tools = await self._get_available_tools()
        
        # If reasoning is empty or contains error, provide fallback that includes the query
        if not reasoning or "error" in reasoning.lower():
            logger.warning(f"Reasoning was empty or contained error: {reasoning}")
            # Include the actual query in the fallback so the LLM knows what to do
            query = context.get('query', context.get('original_query', 'user request'))
            reasoning = f"User asked: '{query}'. Need to determine appropriate action based on this request."
        
        # Get LLM to plan actions (use limited tokens for efficiency)
        logger.info(f"Planning with reasoning: {reasoning[:200]}")
        logger.info(f"Planning with context keys: {context.keys()}")
        logger.info(f"Query from context: {context.get('query', 'N/A')[:100]}")
        
        response = await self.llm_service.complete(
            prompt=prompt.format(
                reasoning=reasoning,
                available_actions=[a.value for a in MnemosyneAction],
                available_tools=available_tools,
                context=json.dumps(context, default=str)[:1000]  # Truncate for token limits
            ),
            max_tokens=settings.OPENAI_MAX_TOKENS_REASONING,
            system="Convert reasoning into a specific action plan. Return JSON array of actions.",
            **self.llm_config  # Pass the LLM config
        )
        
        try:
            # Parse JSON response
            content = response.get("content", "[]")
            logger.info(f"Action planning LLM response: {content[:500]}")
            actions_data = json.loads(content)
            
            # Convert to ActionPayload objects
            actions = []
            for action_dict in actions_data:
                if isinstance(action_dict, dict):
                    # Get action string and ensure it's a valid enum member
                    action_str = action_dict.get("action", "DONE")
                    try:
                        action_enum = MnemosyneAction(action_str)
                    except ValueError:
                        logger.warning(f"Invalid action '{action_str}', defaulting to DONE")
                        action_enum = MnemosyneAction.DONE
                    
                    action = ActionPayload(
                        action=action_enum,
                        parameters=action_dict.get("parameters", {}),
                        reasoning=action_dict.get("reasoning", ""),
                        confidence=action_dict.get("confidence", 0.8)
                    )
                    actions.append(action)
                    
            # If no actions planned, default to DONE
            if not actions:
                actions = [ActionPayload(
                    action=MnemosyneAction.DONE,
                    reasoning="No specific actions needed",
                    confidence=1.0
                )]
                
            return actions
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse action plan: {e}")
            logger.error(f"Raw LLM response: {content[:1000]}")
            # Fallback to simple response
            return [ActionPayload(
                action=MnemosyneAction.EXPLAIN,
                reasoning=reasoning,
                confidence=0.5
            )]
    
    async def execute_action(
        self, 
        action: ActionPayload, 
        context: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> ActionResult:
        """
        Execute a single action.
        
        Delegates to specific executors based on action type.
        """
        start_time = time.time()
        
        # action.action is already a string due to use_enum_values=True in ActionPayload
        action_str = action.action if isinstance(action.action, str) else action.action.value
        logger.info(f"execute_action called with: {action_str}, params: {action.parameters}")
        
        try:
            # Execute through the executor
            logger.info(f"Calling executor.execute for {action_str}")
            result_data = await self.executor.execute(action, context, user_id)
            logger.info(f"Executor returned: {str(result_data)[:200]}")
            
            # Create result
            result = ActionResult(
                action=action.action,
                success=True,
                data=result_data,
                duration_ms=int((time.time() - start_time) * 1000)
            )
            
            # Create receipt for this action
            if user_id and self.receipt_service:
                receipt = await self.receipt_service.create_receipt(
                    user_id=user_id,
                    receipt_type=ReceiptType.AGENT_ACTION,
                    action=f"agentic.{action.action}",
                    context={
                        "parameters": action.parameters,
                        "reasoning": action.reasoning,
                        "confidence": action.confidence,
                        "result": result_data
                    }
                )
                result.receipt_id = receipt.id if receipt else None
                
            return result
            
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return ActionResult(
                action=action.action,
                success=False,
                error=str(e),
                duration_ms=int((time.time() - start_time) * 1000)
            )
    
    async def needs_more_info(
        self, 
        results: List[ActionResult], 
        context: Dict[str, Any]
    ) -> bool:
        """
        Determine if more information/actions are needed.
        
        Uses LLM to analyze results and decide.
        """
        # Check for explicit completion
        if any(r.action == MnemosyneAction.DONE for r in results):
            return False
            
        # Check for explicit need for more
        if any(r.action == MnemosyneAction.NEED_MORE for r in results):
            return True
            
        # Use LLM to determine
        prompt = await self._load_prompt("agentic_needs_more")
        
        response = await self.llm_service.complete(
            prompt=prompt.format(
                actions_executed=json.dumps([r.action for r in results], default=str),
                results=json.dumps([r.dict() for r in results], default=str)[:2000],
                query=context.get("original_query", ""),
                context=json.dumps(context, default=str)[:1000]
            ),
            system="Determine if more information is needed. Respond with YES or NO.",
            max_tokens=50  # Simple YES/NO response
        )
        
        content = response.get("content")
        if content is None:
            logger.warning("No content in needs_more_info response, defaulting to NO")
            return False
        answer = content.strip().upper()
        return answer.startswith("YES")
    
    async def get_proactive_suggestions(
        self, 
        actions: List[ActionPayload],
        results: List[ActionResult],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate proactive suggestions based on results.
        
        Respects user sovereignty - suggestions not commands.
        """
        prompt = await self._load_prompt("agentic_suggestions")
        
        response = await self.llm_service.complete(
            prompt=prompt.format(
                actions=[a.action for a in actions],
                results=json.dumps([r.dict() for r in results], default=str)[:2000],
                context=json.dumps(context, default=str)[:1000],
                query=context.get("query", context.get("original_query", ""))
            ),
            max_tokens=settings.OPENAI_MAX_TOKENS_REASONING,
            system="Generate helpful suggestions. Return JSON array. Each suggestion should respect user agency."
        )
        
        try:
            content = response.get("content", "[]")
            if not content or content == "null":
                return []
                
            suggestions = json.loads(content)
            if not isinstance(suggestions, list):
                logger.warning(f"Suggestions not a list: {type(suggestions)}")
                return []
            
            # Ensure suggestions respect sovereignty
            validated_suggestions = []
            for suggestion in suggestions:
                if isinstance(suggestion, dict):
                    # Handle both "text" and "suggestion" fields from LLM
                    text = suggestion.get("text") or suggestion.get("suggestion", "")
                    if text:  # Only add if there's actual text
                        validated_suggestions.append({
                            "text": text,
                            "action": suggestion.get("action") or suggestion.get("type"),
                            "reasoning": suggestion.get("reasoning", ""),
                            "optional": True  # Always optional
                        })
                    
            return validated_suggestions[:5]  # Max 5 suggestions
            
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to parse suggestions: {e}")
            return []
    
    async def create_decision_receipt(
        self,
        reasoning: str,
        actions: List[ActionPayload],
        results: List[ActionResult],
        user_id: Optional[str],
        duration_ms: int
    ) -> Optional[Any]:
        """
        Create a comprehensive receipt for the entire flow.
        
        Ensures transparency and user trust.
        """
        if not user_id or not self.receipt_service:
            return None
            
        receipt_data = {
            "type": "agentic_flow",
            "reasoning": reasoning,
            "actions": [
                {
                    "action": a.action,
                    "parameters": a.parameters,
                    "reasoning": a.reasoning,
                    "confidence": a.confidence
                }
                for a in actions
            ],
            "results": [
                {
                    "action": r.action,
                    "success": r.success,
                    "error": r.error,
                    "duration_ms": r.duration_ms
                }
                for r in results
            ],
            "duration_ms": duration_ms,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        receipt = await self.receipt_service.create_receipt(
            user_id=user_id,
            receipt_type=ReceiptType.AGENT_ACTION,
            action="agentic.flow.complete",
            context=receipt_data
        )
        
        return receipt
    
    async def _get_available_tools(self) -> str:
        """Get list of available tools for the prompts."""
        try:
            from app.services.tools.registry import tool_registry
            
            # Initialize the registry if needed
            if not tool_registry._initialized:
                await tool_registry.initialize()
            
            available_tools = tool_registry.list_tools()
            
            # Build tool descriptions
            tool_descriptions = []
            for tool_name in available_tools:
                try:
                    tool = tool_registry.tools[tool_name]
                    metadata = tool.metadata
                    tool_descriptions.append(f"  - {tool_name}: {metadata.description}")
                except:
                    tool_descriptions.append(f"  - {tool_name}: (description unavailable)")
            
            return "\n".join(tool_descriptions) if tool_descriptions else "  - shadow_council: Technical and strategic expertise\n  - forum_of_echoes: Philosophical perspectives"
        except Exception as e:
            logger.warning(f"Failed to load tool descriptions: {e}")
            return "  - shadow_council: Technical and strategic expertise\n  - forum_of_echoes: Philosophical perspectives"
    
    async def _load_prompt(self, name: str) -> str:
        """Load a prompt template from file."""
        import os
        import aiofiles
        prompt_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "prompts", f"{name}.txt"
        )
        try:
            # Try async file reading first
            try:
                async with aiofiles.open(prompt_path, "r") as f:
                    return await f.read()
            except:
                # Fallback to sync reading if aiofiles not available
                with open(prompt_path, "r") as f:
                    return f.read()
        except FileNotFoundError:
            logger.error(f"CRITICAL: Prompt {name} not found at {prompt_path}")
            raise FileNotFoundError(f"Required prompt file missing: {prompt_path}")
    
    def _format_response(self, results: List[ActionResult]) -> Dict[str, Any]:
        """Format results into user-friendly response."""
        response = {
            "summary": [],
            "details": {},
            "errors": []
        }
        
        for result in results:
            if result.success:
                response["summary"].append(f"✓ {result.action}: Success")
                if result.data:
                    response["details"][result.action] = result.data
            else:
                response["errors"].append(f"✗ {result.action}: {result.error}")
                
        return response
    
    async def _stream_status(self, status: str):
        """Stream a status update (placeholder for SSE integration)."""
        logger.info(f"Stream status: {status}")
        # TODO: Integrate with SSE streaming endpoint