"""
Action Executors.

Implements specific execution logic for each MnemosyneAction.
Connects to existing services (memory, task, persona, etc.).
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.core.logging import get_logger
from app.services.memory.memory_service import MemoryService
from app.services.task.task_service import TaskService
from app.services.persona.manager import PersonaManager
from app.services.vector_store.qdrant_store import QdrantStore
from app.db.session import get_db
from app.db.models import Memory, Task, User
from .actions import MnemosyneAction, ActionPayload

logger = get_logger(__name__)


class ActionExecutor:
    """
    Executes individual actions by delegating to appropriate services.
    
    Each action respects user sovereignty and can be overridden.
    """
    
    def __init__(self):
        # Services will be injected or lazily loaded
        self.memory_service = None
        self.task_service = None
        self.persona_manager = None
        self.vector_store = None
        
    async def execute(
        self, 
        action: ActionPayload, 
        context: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a single action based on its type.
        
        Args:
            action: Action to execute
            context: Current context
            user_id: User ID for operations
            
        Returns:
            Result data from the action
        """
        # Check for user override
        if action.user_override:
            logger.info(f"User override for action {action.action}")
            return action.user_override
            
        # Route to appropriate executor
        executor_map = {
            # Persona Management
            MnemosyneAction.SELECT_PERSONA: self._select_persona,
            MnemosyneAction.SWITCH_MODE: self._switch_mode,
            
            # Memory Operations
            MnemosyneAction.SEARCH_MEMORIES: self._search_memories,
            MnemosyneAction.CREATE_MEMORY: self._create_memory,
            MnemosyneAction.LINK_MEMORIES: self._link_memories,
            MnemosyneAction.UPDATE_MEMORY: self._update_memory,
            
            # Task Management
            MnemosyneAction.LIST_TASKS: self._list_tasks,
            MnemosyneAction.CREATE_TASK: self._create_task,
            MnemosyneAction.DECOMPOSE_TASK: self._decompose_task,
            MnemosyneAction.UPDATE_TASK: self._update_task,
            MnemosyneAction.COMPLETE_TASK: self._complete_task,
            
            # Tool Operations
            MnemosyneAction.USE_TOOL: self._use_tool,
            MnemosyneAction.SELECT_TOOLS: self._select_tools,
            MnemosyneAction.COMPOSE_TOOLS: self._compose_tools,
            
            # Legacy Agent Activation
            MnemosyneAction.ACTIVATE_SHADOW: self._activate_shadow,
            MnemosyneAction.ACTIVATE_DIALOGUE: self._activate_dialogue,
            
            # Trust Operations
            MnemosyneAction.UPDATE_TRUST: self._update_trust,
            MnemosyneAction.CREATE_APPEAL: self._create_appeal,
            
            # Analysis & Reflection
            MnemosyneAction.ANALYZE_PATTERNS: self._analyze_patterns,
            MnemosyneAction.REFLECT: self._reflect,
            MnemosyneAction.SUGGEST: self._suggest,
            
            # Control Actions
            MnemosyneAction.DONE: self._done,
            MnemosyneAction.NEED_MORE: self._need_more,
            MnemosyneAction.EXPLAIN: self._explain,
            MnemosyneAction.WAIT_USER: self._wait_user
        }
        
        executor = executor_map.get(action.action)
        if not executor:
            raise ValueError(f"No executor for action: {action.action}")
            
        # Execute with parameters
        return await executor(action.parameters, context, user_id)
    
    # ============= Persona Management =============
    
    async def _select_persona(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Select appropriate persona based on context."""
        if not self.persona_manager:
            from app.services.persona.manager import PersonaManager
            self.persona_manager = PersonaManager()
            
        # Get query from context
        query = context.get("query", "")
        
        # Use LLM to select persona (replacing keyword matching)
        selected_mode = await self.persona_manager.select_mode_llm(
            query=query,
            context=context
        )
        
        # Activate the persona
        persona = self.persona_manager.get_persona(selected_mode)
        
        return {
            "selected_mode": selected_mode,
            "persona_name": persona.__class__.__name__ if persona else None,
            "reasoning": f"Selected {selected_mode} mode based on query context"
        }
    
    async def _switch_mode(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Switch sovereignty mode."""
        new_mode = params.get("mode", "guided")
        
        return {
            "previous_mode": context.get("sovereignty_mode", "guided"),
            "new_mode": new_mode,
            "features_enabled": self._get_mode_features(new_mode)
        }
    
    def _get_mode_features(self, mode: str) -> List[str]:
        """Get features for sovereignty mode."""
        features_map = {
            "protected": ["safety_rails", "guided_suggestions", "limited_actions"],
            "guided": ["balanced_autonomy", "contextual_help", "most_features"],
            "sovereign": ["full_control", "all_features", "no_restrictions"]
        }
        return features_map.get(mode, [])
    
    # ============= Memory Operations =============
    
    async def _search_memories(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Search memories using vector similarity."""
        # For now, just return empty results since we need embeddings
        # TODO: Integrate with embedding service
        query = params.get("query", context.get("query", ""))
        
        # Use existing memories from context if available
        memories = context.get("memories", [])
        
        return {
            "memories_found": len(memories),
            "memories": memories,
            "query": query,
            "note": "Using context memories - vector search pending embedding integration"
        }
    
    async def _create_memory(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Create a new memory."""
        from app.db.session import async_session_maker
        from app.services.memory.memory_service import MemoryService
        
        content = params.get("content", "")
        memory_type = params.get("type", "observation")
        tags = params.get("tags", [])
        title = params.get("title", content[:50] + "..." if len(content) > 50 else content)
        
        async with async_session_maker() as db:
            memory_service = MemoryService(db)
            
            # Create memory
            memory = await memory_service.create_memory(
                user_id=user_id,
                title=title,
                content=content,
                source=memory_type,  # Fixed parameter name
                tags=tags,
                importance_score=params.get("importance", 0.5)  # Fixed parameter name and default
                # Note: metadata not supported by current memory service
            )
            
            await db.commit()
            
            return {
                "memory_id": str(memory.id) if memory else None,
                "created": True,
                "type": memory_type,
                "title": title
            }
    
    async def _link_memories(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Link related memories together."""
        memory_ids = params.get("memory_ids", [])
        link_type = params.get("link_type", "related")
        
        # TODO: Implement memory linking in database
        return {
            "linked": len(memory_ids),
            "link_type": link_type,
            "status": "pending_implementation"
        }
    
    async def _update_memory(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Update an existing memory."""
        memory_id = params.get("memory_id")
        updates = params.get("updates", {})
        
        if not self.memory_service:
            from app.services.memory.memory_service import MemoryService
            self.memory_service = MemoryService()
            
        # Update memory
        success = await self.memory_service.update(
            memory_id=memory_id,
            user_id=user_id,
            **updates
        )
        
        return {
            "memory_id": memory_id,
            "updated": success,
            "changes": list(updates.keys())
        }
    
    # ============= Task Management =============
    
    async def _list_tasks(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """List user's tasks."""
        from app.db.session import async_session_maker
        from app.services.task.task_service import TaskService
        from app.db.models.task import TaskStatus
        
        async with async_session_maker() as db:
            task_service = TaskService(db)
            
            # Get filter parameters
            status = params.get("status")  # pending, in_progress, completed
            limit = params.get("limit", 10)
            
            # Get all tasks for user - returns (tasks, count) tuple
            tasks, total_count = await task_service.get_tasks_by_user_id(
                user_id=user_id,
                limit=limit
            )
            
            # Filter by status if specified
            if status:
                try:
                    status_enum = TaskStatus(status.lower())
                    tasks = [t for t in tasks if t.status == status_enum]
                except ValueError:
                    pass  # Invalid status, return all
            
            # Format tasks for response
            task_list = []
            for task in tasks[:limit]:
                task_list.append({
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "status": task.status.value,
                    "priority": task.priority.value if task.priority else "medium",
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "created_at": task.created_at.isoformat() if task.created_at else None
                })
        
        return {
            "tasks": task_list,
            "count": len(task_list),
            "status_filter": status
        }
    
    async def _create_task(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Create a new task."""
        from app.db.session import async_session_maker
        from app.services.task.task_service import TaskService
        from app.db.models.task import TaskPriority
        
        async with async_session_maker() as db:
            task_service = TaskService(db)
            
            title = params.get("title", "")
            description = params.get("description", "")
            priority = TaskPriority(params.get("priority", "medium").lower())
            
            # Create task
            task = await task_service.create_task(
                user_id=user_id,
                title=title,
                description=description,
                priority=priority,
                metadata=params.get("metadata", {})
            )
            await db.commit()
        
        return {
            "task_id": str(task.id) if task else None,
            "created": True,
            "title": title
        }
    
    async def _decompose_task(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Decompose a complex task into subtasks."""
        task_id = params.get("task_id")
        
        # TODO: Use LLM to decompose task
        subtasks = []
        
        return {
            "parent_task_id": task_id,
            "subtasks_created": len(subtasks),
            "subtasks": subtasks
        }
    
    async def _update_task(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Update task status or details."""
        from app.db.session import async_session_maker
        from app.services.task.task_service import TaskService
        
        task_id = params.get("task_id")
        updates = params.get("updates", {})
        
        async with async_session_maker() as db:
            task_service = TaskService(db)
            
            # Update task
            task = await task_service.update_task(
                task_id=task_id,
                **updates
            )
            await db.commit()
            success = task is not None
        
        return {
            "task_id": task_id,
            "updated": success,
            "changes": list(updates.keys())
        }
    
    async def _complete_task(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Mark a task as completed."""
        task_id = params.get("task_id")
        
        return await self._update_task(
            {"task_id": task_id, "updates": {"status": "completed"}},
            context,
            user_id
        )
    
    # ============= Tool Operations =============
    
    async def _use_tool(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Execute a specific tool."""
        from app.services.tools.registry import tool_registry
        from app.services.tools.base import ToolInput
        
        logger.info(f"_use_tool called with params: {params}")
        
        tool_name = params.get("tool_name")
        tool_params = params.get("parameters", {})
        query = params.get("query", "")
        
        logger.info(f"Executing tool: {tool_name} with query: {query[:100]}")
        
        try:
            # Get the tool from registry
            tool = tool_registry.get(tool_name)
            
            # Create tool input
            tool_input = ToolInput(
                query=query,
                parameters=tool_params,
                context=context,
                options=params.get("options", {})
            )
            
            # Execute the tool
            output = await tool_registry.execute_tool(tool_name, tool_input)
            
            return {
                "tool_name": tool_name,
                "success": output.success,
                "result": output.result,
                "error": output.error,
                "metadata": output.metadata,
                "confidence": output.confidence,
                "follow_up_tools": output.follow_up_tools
            }
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                "tool_name": tool_name,
                "success": False,
                "error": str(e)
            }
    
    async def _select_tools(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Select relevant tools for a query."""
        from app.services.tools.registry import tool_registry
        
        query = params.get("query", context.get("query", ""))
        max_tools = params.get("max_tools", 5)
        threshold = params.get("threshold", 0.3)
        
        try:
            # Get relevant tools from registry
            relevant_tools = await tool_registry.get_relevant_tools(
                query=query,
                context=context,
                threshold=threshold,
                max_tools=max_tools
            )
            
            # Format results
            tools = [
                {
                    "name": tool_name,
                    "confidence": confidence,
                    "metadata": tool_registry.get_tool_metadata(tool_name).__dict__
                }
                for tool_name, confidence in relevant_tools
            ]
            
            return {
                "query": query,
                "tools_selected": len(tools),
                "tools": tools
            }
            
        except Exception as e:
            logger.error(f"Error selecting tools: {e}")
            return {
                "query": query,
                "tools_selected": 0,
                "tools": [],
                "error": str(e)
            }
    
    async def _compose_tools(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Compose multiple tools into a workflow."""
        from app.services.tools.registry import tool_registry
        from app.services.tools.base import ToolInput
        
        tools = params.get("tools", [])  # List of {name, parameters}
        parallel = params.get("parallel", True)
        
        try:
            # Prepare tool inputs
            tool_inputs = []
            for tool_spec in tools:
                tool_input = ToolInput(
                    query=tool_spec.get("query", ""),
                    parameters=tool_spec.get("parameters", {}),
                    context=context,
                    options=tool_spec.get("options", {})
                )
                tool_inputs.append((tool_spec["name"], tool_input))
            
            # Execute tools
            results = await tool_registry.execute_multiple(
                tool_inputs=tool_inputs,
                parallel=parallel
            )
            
            # Format results
            formatted_results = []
            for i, result in enumerate(results):
                tool_name = tools[i]["name"]
                if isinstance(result, Exception):
                    formatted_results.append({
                        "tool_name": tool_name,
                        "success": False,
                        "error": str(result)
                    })
                else:
                    formatted_results.append({
                        "tool_name": tool_name,
                        "success": result.success,
                        "result": result.result,
                        "error": result.error
                    })
            
            return {
                "tools_executed": len(formatted_results),
                "parallel": parallel,
                "results": formatted_results
            }
            
        except Exception as e:
            logger.error(f"Error composing tools: {e}")
            return {
                "tools_executed": 0,
                "error": str(e)
            }
    
    # ============= Agent Activation =============
    
    async def _activate_shadow(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Activate Shadow Council agents (Artificer/Archivist/Mystagogue/Tactician/Daemon)."""
        agent_type = params.get("agent_type", "Artificer")
        query = params.get("query", context.get("query", ""))
        
        # TODO: Connect to Shadow agent system
        return {
            "agent_type": agent_type,
            "status": "pending_integration",
            "message": f"Would activate {agent_type} agent for: {query}"
        }
    
    async def _activate_dialogue(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Activate Forum of Echoes for philosophical perspectives (50+ voices)."""
        voices = params.get("voices", ["socrates", "confucius"])
        topic = params.get("topic", context.get("query", ""))
        
        # TODO: Connect to Dialogue agent system
        return {
            "agents": agents,
            "topic": topic,
            "status": "pending_integration",
            "message": f"Would start dialogue between {agents} on: {topic}"
        }
    
    # ============= Trust Operations =============
    
    async def _update_trust(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Update trust relationship."""
        peer_id = params.get("peer_id")
        trust_delta = params.get("delta", 0)
        reason = params.get("reason", "")
        
        # TODO: Implement trust system integration
        return {
            "peer_id": peer_id,
            "trust_delta": trust_delta,
            "reason": reason,
            "status": "pending_implementation"
        }
    
    async def _create_appeal(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Create an appeal for trust decision."""
        decision_id = params.get("decision_id")
        reason = params.get("reason", "")
        
        # TODO: Implement appeals system
        return {
            "appeal_id": f"appeal_{decision_id}",
            "status": "pending_review",
            "reason": reason
        }
    
    # ============= Analysis & Reflection =============
    
    async def _analyze_patterns(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Analyze patterns in user behavior/data."""
        data_type = params.get("data_type", "memories")
        timeframe = params.get("timeframe", "all")
        
        # TODO: Implement pattern analysis
        patterns = {
            "frequency_patterns": [],
            "temporal_patterns": [],
            "semantic_clusters": []
        }
        
        return {
            "data_type": data_type,
            "patterns_found": 0,
            "patterns": patterns
        }
    
    async def _reflect(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Perform deep reflection on memories/experiences."""
        memories = context.get("memories", [])
        reflection_type = params.get("type", "general")
        
        # TODO: Implement reflection with LLM
        return {
            "reflection_type": reflection_type,
            "memories_analyzed": len(memories),
            "insights": [],
            "status": "pending_implementation"
        }
    
    async def _suggest(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Generate proactive suggestions."""
        suggestion_type = params.get("type", "next_action")
        
        suggestions = []
        
        return {
            "suggestion_type": suggestion_type,
            "suggestions": suggestions,
            "optional": True  # Always optional
        }
    
    # ============= Control Actions =============
    
    async def _done(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Signal completion."""
        return {
            "status": "complete",
            "message": params.get("message", "Task completed successfully")
        }
    
    async def _need_more(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Request more information."""
        return {
            "status": "need_more_info",
            "needed": params.get("needed", "Additional context required"),
            "specific_questions": params.get("questions", [])
        }
    
    async def _explain(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Explain reasoning."""
        return {
            "explanation": params.get("explanation", ""),
            "reasoning": params.get("reasoning", context.get("reasoning", "")),
            "confidence": params.get("confidence", 0.8)
        }
    
    async def _wait_user(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Wait for user input."""
        return {
            "status": "waiting_for_user",
            "prompt": params.get("prompt", "Please provide additional information"),
            "timeout_ms": params.get("timeout_ms", 30000)
        }