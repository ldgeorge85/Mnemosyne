"""
Collaborative Execution Engine for the Shadow AI system.

This module manages the execution of decomposed tasks with advanced
multi-agent collaboration, including agent-to-agent communication,
dependency management, and intelligent response synthesis.
"""

import logging
import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed

from .task_decomposer import TaskDecomposition, SubTask, TaskPriority

logger = logging.getLogger("shadow.orchestrator.executor")


class ExecutionStatus(Enum):
    """Status of task execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class ExecutionResult:
    """Result of a subtask execution."""
    subtask_id: str
    status: ExecutionStatus
    response: str
    agent_name: str
    execution_time: float
    context: Dict[str, Any] = field(default_factory=dict)
    dependencies_met: bool = True
    error_message: Optional[str] = None


@dataclass
class AgentContext:
    """Shared context between agents during collaborative execution."""
    previous_findings: Dict[str, str] = field(default_factory=dict)
    shared_data: Dict[str, Any] = field(default_factory=dict)
    cross_references: List[str] = field(default_factory=list)
    collaboration_notes: List[str] = field(default_factory=list)


class CollaborativeExecutor:
    """
    Advanced execution engine for multi-agent collaboration.
    
    This executor manages complex task workflows, enabling agents to
    share context, build on each other's work, and produce synthesized
    responses that leverage the full capabilities of the system.
    """
    
    def __init__(self, agents: Dict[str, Any]):
        """
        Initialize the collaborative executor.
        
        Args:
            agents: Dictionary of available agents {name: agent_instance}
        """
        self.agents = agents
        self.execution_history: List[ExecutionResult] = []
        self.agent_context = AgentContext()
        self.max_parallel_tasks = 3
        
    async def execute_decomposition(self, decomposition: TaskDecomposition, 
                                  memory_context: Optional[Dict] = None) -> str:
        """
        Execute a task decomposition with full collaborative capabilities.
        
        Args:
            decomposition: The task decomposition to execute
            memory_context: Optional memory context from the orchestrator
            
        Returns:
            Synthesized response from all agents
        """
        logger.info(f"Executing {decomposition.task_type.value} task with {len(decomposition.subtasks)} subtasks")
        
        # Reset context for new execution
        self.agent_context = AgentContext()
        self.execution_history = []
        
        # Execute based on strategy
        if decomposition.execution_strategy == "direct":
            results = await self._execute_direct(decomposition.subtasks, memory_context)
        elif decomposition.execution_strategy == "sequential":
            results = await self._execute_sequential(decomposition.subtasks, memory_context)
        elif decomposition.execution_strategy == "parallel":
            results = await self._execute_parallel(decomposition.subtasks, memory_context)
        elif decomposition.execution_strategy == "dependency_based":
            results = await self._execute_dependency_based(decomposition.subtasks, memory_context)
        else:
            # Fallback to parallel execution
            results = await self._execute_parallel(decomposition.subtasks, memory_context)
        
        # Synthesize final response
        final_response = self._synthesize_responses(results, decomposition)
        
        logger.info(f"Collaborative execution completed with {len(results)} results")
        return final_response

    async def _execute_direct(self, subtasks: List[SubTask], 
                            memory_context: Optional[Dict] = None) -> List[ExecutionResult]:
        """Execute a single task directly."""
        if not subtasks:
            return []
            
        subtask = subtasks[0]
        result = await self._execute_subtask(subtask, memory_context)
        return [result]

    async def _execute_sequential(self, subtasks: List[SubTask], 
                                memory_context: Optional[Dict] = None) -> List[ExecutionResult]:
        """Execute subtasks in sequential order, passing context between them."""
        results = []
        
        for subtask in subtasks:
            # Check dependencies
            if not self._dependencies_met(subtask, results):
                logger.warning(f"Dependencies not met for subtask {subtask.id}, skipping")
                continue
            
            # Add context from previous results
            enhanced_context = self._build_enhanced_context(subtask, results, memory_context)
            
            # Execute the subtask
            result = await self._execute_subtask(subtask, enhanced_context)
            results.append(result)
            
            # Update shared context
            self._update_agent_context(result)
            
        return results

    async def _execute_parallel(self, subtasks: List[SubTask], 
                              memory_context: Optional[Dict] = None) -> List[ExecutionResult]:
        """Execute subtasks in parallel where possible."""
        results = []
        
        # Group tasks by dependencies
        independent_tasks = [task for task in subtasks if not task.dependencies]
        dependent_tasks = [task for task in subtasks if task.dependencies]
        
        # Execute independent tasks in parallel
        if independent_tasks:
            parallel_results = await self._execute_tasks_parallel(independent_tasks, memory_context)
            results.extend(parallel_results)
            
            # Update context
            for result in parallel_results:
                self._update_agent_context(result)
        
        # Execute dependent tasks sequentially
        for subtask in dependent_tasks:
            if self._dependencies_met(subtask, results):
                enhanced_context = self._build_enhanced_context(subtask, results, memory_context)
                result = await self._execute_subtask(subtask, enhanced_context)
                results.append(result)
                self._update_agent_context(result)
        
        return results

    async def _execute_dependency_based(self, subtasks: List[SubTask], 
                                      memory_context: Optional[Dict] = None) -> List[ExecutionResult]:
        """Execute subtasks based on their dependencies using topological sorting."""
        results = []
        remaining_tasks = subtasks.copy()
        
        while remaining_tasks:
            # Find tasks that can be executed now
            ready_tasks = [task for task in remaining_tasks 
                          if self._dependencies_met(task, results)]
            
            if not ready_tasks:
                logger.error("Circular dependency or missing dependency detected")
                break
            
            # Execute ready tasks (in parallel if possible)
            if len(ready_tasks) <= self.max_parallel_tasks:
                # Execute all ready tasks in parallel
                parallel_results = await self._execute_tasks_parallel(ready_tasks, memory_context)
                results.extend(parallel_results)
                
                for result in parallel_results:
                    self._update_agent_context(result)
            else:
                # Execute high priority tasks first
                priority_tasks = sorted(ready_tasks, 
                                      key=lambda t: (t.priority.value, t.estimated_complexity), 
                                      reverse=True)
                
                for task in priority_tasks[:self.max_parallel_tasks]:
                    enhanced_context = self._build_enhanced_context(task, results, memory_context)
                    result = await self._execute_subtask(task, enhanced_context)
                    results.append(result)
                    self._update_agent_context(result)
            
            # Remove completed tasks
            completed_ids = [result.subtask_id for result in results 
                           if result.subtask_id in [task.id for task in ready_tasks]]
            remaining_tasks = [task for task in remaining_tasks 
                             if task.id not in completed_ids]
        
        return results

    async def _execute_tasks_parallel(self, tasks: List[SubTask], 
                                    memory_context: Optional[Dict] = None) -> List[ExecutionResult]:
        """Execute multiple tasks in parallel."""
        tasks_with_context = []
        for task in tasks:
            enhanced_context = self._build_enhanced_context(task, [], memory_context)
            tasks_with_context.append((task, enhanced_context))
        
        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=min(len(tasks), self.max_parallel_tasks)) as executor:
            future_to_task = {
                executor.submit(self._execute_subtask_sync, task, context): task 
                for task, context in tasks_with_context
            }
            
            results = []
            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    task = future_to_task[future]
                    logger.error(f"Error executing task {task.id}: {str(e)}")
                    results.append(ExecutionResult(
                        subtask_id=task.id,
                        status=ExecutionStatus.FAILED,
                        response=f"Error: {str(e)}",
                        agent_name=task.target_agents[0] if task.target_agents else "unknown",
                        execution_time=0.0,
                        error_message=str(e)
                    ))
        
        return results

    def _execute_subtask_sync(self, subtask: SubTask, context: Dict) -> ExecutionResult:
        """Synchronous wrapper for subtask execution."""
        # This is a synchronous wrapper - in practice, you'd use asyncio.run()
        # or implement proper async-to-sync conversion
        start_time = time.time()
        
        try:
            # Select the primary agent for this subtask
            primary_agent = subtask.target_agents[0] if subtask.target_agents else "librarian"
            
            if primary_agent not in self.agents:
                raise ValueError(f"Agent {primary_agent} not found")
            
            agent = self.agents[primary_agent]
            
            # Prepare enhanced input with collaboration context
            enhanced_input = self._prepare_collaborative_input(subtask, context)
            
            # Execute the subtask
            response = agent.process_request(
                enhanced_input, 
                conversation_history=context.get('conversation_history', []),
                memory_context=context.get('memory_context', {})
            )
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                subtask_id=subtask.id,
                status=ExecutionStatus.COMPLETED,
                response=response,
                agent_name=primary_agent,
                execution_time=execution_time,
                context={"original_input": subtask.description}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error executing subtask {subtask.id}: {str(e)}")
            
            return ExecutionResult(
                subtask_id=subtask.id,
                status=ExecutionStatus.FAILED,
                response=f"Error processing request: {str(e)}",
                agent_name=primary_agent if 'primary_agent' in locals() else "unknown",
                execution_time=execution_time,
                error_message=str(e)
            )

    async def _execute_subtask(self, subtask: SubTask, context: Dict) -> ExecutionResult:
        """Execute a single subtask with full context."""
        return self._execute_subtask_sync(subtask, context)

    def _dependencies_met(self, subtask: SubTask, completed_results: List[ExecutionResult]) -> bool:
        """Check if all dependencies for a subtask have been completed."""
        if not subtask.dependencies:
            return True
        
        completed_ids = {result.subtask_id for result in completed_results 
                        if result.status == ExecutionStatus.COMPLETED}
        
        return all(dep_id in completed_ids for dep_id in subtask.dependencies)

    def _build_enhanced_context(self, subtask: SubTask, previous_results: List[ExecutionResult], 
                              memory_context: Optional[Dict] = None) -> Dict:
        """Build enhanced context for a subtask including previous findings."""
        context = {
            'memory_context': memory_context or {},
            'conversation_history': [],
            'previous_findings': {},
            'shared_context': self.agent_context.shared_data,
            'collaboration_notes': self.agent_context.collaboration_notes
        }
        
        # Add findings from dependency tasks
        for dep_id in subtask.dependencies:
            dep_result = next((r for r in previous_results if r.subtask_id == dep_id), None)
            if dep_result and dep_result.status == ExecutionStatus.COMPLETED:
                context['previous_findings'][dep_id] = {
                    'agent': dep_result.agent_name,
                    'response': dep_result.response,
                    'execution_time': dep_result.execution_time
                }
        
        return context

    def _prepare_collaborative_input(self, subtask: SubTask, context: Dict) -> str:
        """Prepare input for an agent that includes collaborative context."""
        base_input = subtask.description
        
        # Add context from previous findings
        if context.get('previous_findings'):
            context_str = "\n\nPrevious findings from other agents:\n"
            for task_id, finding in context['previous_findings'].items():
                context_str += f"- {finding['agent'].title()} Agent: {finding['response'][:200]}...\n"
            base_input = context_str + "\n\nYour task: " + base_input
        
        # Add collaboration notes
        if context.get('collaboration_notes'):
            notes_str = "\n\nCollaboration notes:\n" + "\n".join(context['collaboration_notes'])
            base_input += notes_str
        
        return base_input

    def _update_agent_context(self, result: ExecutionResult):
        """Update the shared agent context with new findings."""
        if result.status == ExecutionStatus.COMPLETED:
            # Store the finding
            self.agent_context.previous_findings[result.subtask_id] = result.response
            
            # Extract key insights for cross-reference
            if len(result.response) > 50:
                self.agent_context.cross_references.append(
                    f"{result.agent_name}: {result.response[:100]}..."
                )
            
            # Add execution metadata
            self.agent_context.shared_data[f"{result.subtask_id}_meta"] = {
                'agent': result.agent_name,
                'execution_time': result.execution_time,
                'timestamp': time.time()
            }

    def _synthesize_responses(self, results: List[ExecutionResult], 
                            decomposition: TaskDecomposition) -> str:
        """Synthesize responses from multiple agents into a coherent final response."""
        successful_results = [r for r in results if r.status == ExecutionStatus.COMPLETED]
        
        if not successful_results:
            return "I apologize, but I was unable to process your request due to execution errors."
        
        if len(successful_results) == 1:
            return successful_results[0].response
        
        # Build synthesized response
        synthesis = []
        
        # Add introduction
        synthesis.append(f"I've analyzed your request using {len(successful_results)} specialized perspectives:\n")
        
        # Group responses by agent
        agent_responses = {}
        for result in successful_results:
            if result.agent_name not in agent_responses:
                agent_responses[result.agent_name] = []
            agent_responses[result.agent_name].append(result.response)
        
        # Add agent perspectives
        agent_titles = {
            'engineer': 'Technical Analysis',
            'librarian': 'Information & Research',
            'priest': 'Ethical & Philosophical Perspective'
        }
        
        for agent, responses in agent_responses.items():
            title = agent_titles.get(agent, agent.title())
            synthesis.append(f"\n## {title}\n")
            
            if len(responses) == 1:
                synthesis.append(responses[0])
            else:
                for i, response in enumerate(responses, 1):
                    synthesis.append(f"\n### Analysis {i}\n{response}")
        
        # Add collaborative insights if multiple agents were involved
        if len(agent_responses) > 1:
            synthesis.append(self._generate_collaborative_insights(successful_results))
        
        # Add execution summary
        total_time = sum(r.execution_time for r in successful_results)
        synthesis.append(f"\n\n*Collaborative analysis completed in {total_time:.2f} seconds using {decomposition.collaboration_level} collaboration.*")
        
        return "\n".join(synthesis)

    def _generate_collaborative_insights(self, results: List[ExecutionResult]) -> str:
        """Generate insights from the collaboration between agents."""
        insights = ["\n## Collaborative Insights\n"]
        
        # Find common themes
        all_responses = " ".join([r.response.lower() for r in results])
        
        # Simple keyword analysis for common themes
        common_keywords = ["important", "key", "critical", "essential", "significant", "consider"]
        found_themes = [kw for kw in common_keywords if kw in all_responses]
        
        if found_themes:
            insights.append("Key themes identified across all perspectives:")
            for theme in found_themes[:3]:  # Limit to top 3
                insights.append(f"- {theme.title()} considerations emphasized by multiple agents")
        
        # Add synergy note
        insights.append("\nThis multi-agent analysis provides a comprehensive view that combines technical expertise, research capabilities, and ethical reasoning.")
        
        return "\n".join(insights)


# Create default instance  
def create_collaborative_executor(agents: Dict[str, Any]) -> CollaborativeExecutor:
    """Create a collaborative executor with the given agents."""
    return CollaborativeExecutor(agents)
