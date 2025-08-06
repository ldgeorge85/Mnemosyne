"""
Advanced Task Decomposition module for the Shadow AI system.

This module provides sophisticated task breakdown capabilities,
enabling complex queries to be intelligently divided into
specialized subtasks for optimal agent collaboration.
"""

import logging
import re
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("shadow.orchestrator.decomposer")


class TaskType(Enum):
    """Types of tasks that can be identified and decomposed."""
    SIMPLE = "simple"
    COMPLEX = "complex"
    MULTI_DOMAIN = "multi_domain"
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"


class TaskPriority(Enum):
    """Priority levels for subtasks."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class SubTask:
    """Represents a decomposed subtask."""
    id: str
    description: str
    target_agents: List[str]
    priority: TaskPriority
    dependencies: List[str]  # IDs of subtasks that must complete first
    context: Dict[str, Any]
    estimated_complexity: float  # 0.0 to 1.0


@dataclass
class TaskDecomposition:
    """Represents the complete decomposition of a user query."""
    original_query: str
    task_type: TaskType
    subtasks: List[SubTask]
    execution_strategy: str
    estimated_total_time: float
    collaboration_level: str  # "none", "light", "heavy"


class AdvancedTaskDecomposer:
    """
    Advanced task decomposition engine for multi-agent collaboration.
    
    This decomposer analyzes user queries and breaks them down into
    optimal subtasks for specialized agent processing.
    """
    
    def __init__(self):
        self.complexity_indicators = {
            "technical": ["design", "build", "calculate", "optimize", "engineer", "system", "architecture"],
            "research": ["research", "find", "compare", "analyze", "evaluate", "investigate"],
            "ethical": ["should", "right", "wrong", "ethical", "moral", "philosophy", "values"],
            "multi_step": ["and then", "after", "next", "following", "subsequently"],
            "comparison": ["compare", "contrast", "versus", "vs", "better", "worse"],
            "complex_reasoning": ["why", "how", "explain", "justify", "reasoning", "because"]
        }
        
        self.agent_specializations = {
            "engineer": {
                "domains": ["technical", "design", "systems", "optimization", "calculations"],
                "keywords": ["build", "design", "calculate", "optimize", "engineer", "technical", "system"],
                "complexity_weight": 0.8
            },
            "librarian": {
                "domains": ["research", "information", "data", "facts", "sources"],
                "keywords": ["research", "find", "information", "data", "source", "facts"],
                "complexity_weight": 0.6
            },
            "priest": {
                "domains": ["ethics", "philosophy", "values", "morality", "reasoning"],
                "keywords": ["ethics", "moral", "philosophy", "values", "should", "right"],
                "complexity_weight": 0.7
            }
        }

    def decompose_task(self, user_query: str, context: Optional[Dict] = None) -> TaskDecomposition:
        """
        Decompose a user query into optimal subtasks for agent collaboration.
        
        Args:
            user_query: The user's input query
            context: Optional context from previous interactions
            
        Returns:
            TaskDecomposition object with subtasks and execution strategy
        """
        logger.info(f"Decomposing task: {user_query[:100]}...")
        
        # Analyze query complexity and type
        task_type = self._analyze_task_type(user_query)
        complexity_score = self._calculate_complexity_score(user_query)
        
        # Determine if decomposition is beneficial
        if not self._should_decompose(user_query, complexity_score, task_type):
            return self._create_simple_task(user_query, task_type)
        
        # Perform advanced decomposition
        subtasks = self._create_subtasks(user_query, task_type, complexity_score, context)
        execution_strategy = self._determine_execution_strategy(subtasks, task_type)
        collaboration_level = self._assess_collaboration_level(subtasks)
        
        decomposition = TaskDecomposition(
            original_query=user_query,
            task_type=task_type,
            subtasks=subtasks,
            execution_strategy=execution_strategy,
            estimated_total_time=self._estimate_total_time(subtasks),
            collaboration_level=collaboration_level
        )
        
        logger.info(f"Task decomposed into {len(subtasks)} subtasks with {collaboration_level} collaboration")
        return decomposition

    def _analyze_task_type(self, query: str) -> TaskType:
        """Analyze the type of task based on query characteristics."""
        query_lower = query.lower()
        
        # Count domain indicators
        domain_matches = {}
        for domain, keywords in self.complexity_indicators.items():
            matches = sum(1 for keyword in keywords if keyword in query_lower)
            if matches > 0:
                domain_matches[domain] = matches
        
        # Determine task type based on analysis
        if len(domain_matches) == 0:
            return TaskType.SIMPLE
        elif len(domain_matches) == 1:
            return TaskType.SIMPLE
        elif len(domain_matches) >= 3:
            return TaskType.MULTI_DOMAIN
        elif "multi_step" in domain_matches:
            return TaskType.SEQUENTIAL
        elif len(query.split()) > 25:
            return TaskType.COMPLEX
        else:
            return TaskType.PARALLEL

    def _calculate_complexity_score(self, query: str) -> float:
        """Calculate a complexity score for the query (0.0 to 1.0)."""
        score = 0.0
        query_lower = query.lower()
        
        # Length factor
        word_count = len(query.split())
        score += min(word_count / 50.0, 0.3)  # Max 0.3 from length
        
        # Complexity indicators
        for domain, keywords in self.complexity_indicators.items():
            matches = sum(1 for keyword in keywords if keyword in query_lower)
            score += matches * 0.05  # Each match adds 0.05
        
        # Question complexity
        question_words = ["why", "how", "what", "when", "where", "who"]
        question_count = sum(1 for word in question_words if word in query_lower)
        score += question_count * 0.1
        
        # Multi-domain complexity
        domain_count = len([domain for domain, keywords in self.complexity_indicators.items() 
                           if any(keyword in query_lower for keyword in keywords)])
        score += domain_count * 0.15
        
        return min(score, 1.0)

    def _should_decompose(self, query: str, complexity_score: float, task_type: TaskType) -> bool:
        """Determine if a task should be decomposed."""
        # Simple heuristics for decomposition decision
        if task_type == TaskType.SIMPLE and complexity_score < 0.3:
            return False
        if len(query.split()) < 10:
            return False
        if task_type in [TaskType.MULTI_DOMAIN, TaskType.SEQUENTIAL, TaskType.COMPLEX]:
            return True
        if complexity_score > 0.5:
            return True
        return False

    def _create_simple_task(self, query: str, task_type: TaskType) -> TaskDecomposition:
        """Create a simple, non-decomposed task."""
        # Determine which agents should handle this
        target_agents = self._identify_target_agents(query)
        
        subtask = SubTask(
            id="main_task",
            description=query,
            target_agents=target_agents,
            priority=TaskPriority.HIGH,
            dependencies=[],
            context={},
            estimated_complexity=0.3
        )
        
        return TaskDecomposition(
            original_query=query,
            task_type=task_type,
            subtasks=[subtask],
            execution_strategy="direct",
            estimated_total_time=2.0,
            collaboration_level="light"
        )

    def _create_subtasks(self, query: str, task_type: TaskType, complexity_score: float, 
                        context: Optional[Dict] = None) -> List[SubTask]:
        """Create optimized subtasks based on query analysis."""
        subtasks = []
        
        if task_type == TaskType.MULTI_DOMAIN:
            subtasks = self._create_multi_domain_subtasks(query, complexity_score)
        elif task_type == TaskType.SEQUENTIAL:
            subtasks = self._create_sequential_subtasks(query, complexity_score)
        elif task_type == TaskType.COMPLEX:
            subtasks = self._create_complex_subtasks(query, complexity_score)
        else:
            subtasks = self._create_parallel_subtasks(query, complexity_score)
        
        return subtasks

    def _create_multi_domain_subtasks(self, query: str, complexity_score: float) -> List[SubTask]:
        """Create subtasks for multi-domain queries."""
        subtasks = []
        query_lower = query.lower()
        
        # Information gathering phase
        if any(keyword in query_lower for keyword in ["research", "find", "information", "data"]):
            subtasks.append(SubTask(
                id="info_gathering",
                description=f"Research and gather relevant information about: {query}",
                target_agents=["librarian"],
                priority=TaskPriority.HIGH,
                dependencies=[],
                context={"phase": "research"},
                estimated_complexity=0.4
            ))
        
        # Technical analysis phase
        if any(keyword in query_lower for keyword in ["design", "build", "technical", "system"]):
            subtasks.append(SubTask(
                id="technical_analysis",
                description=f"Provide technical analysis and design considerations for: {query}",
                target_agents=["engineer"],
                priority=TaskPriority.HIGH,
                dependencies=["info_gathering"] if subtasks else [],
                context={"phase": "technical"},
                estimated_complexity=0.6
            ))
        
        # Ethical evaluation phase
        if any(keyword in query_lower for keyword in ["should", "ethical", "moral", "right"]):
            subtasks.append(SubTask(
                id="ethical_evaluation",
                description=f"Evaluate ethical implications and considerations for: {query}",
                target_agents=["priest"],
                priority=TaskPriority.MEDIUM,
                dependencies=[task.id for task in subtasks],
                context={"phase": "ethics"},
                estimated_complexity=0.5
            ))
        
        # Synthesis phase
        if len(subtasks) > 1:
            subtasks.append(SubTask(
                id="synthesis",
                description=f"Synthesize findings from all perspectives for: {query}",
                target_agents=["engineer", "librarian", "priest"],
                priority=TaskPriority.HIGH,
                dependencies=[task.id for task in subtasks],
                context={"phase": "synthesis"},
                estimated_complexity=0.7
            ))
        
        return subtasks

    def _create_sequential_subtasks(self, query: str, complexity_score: float) -> List[SubTask]:
        """Create subtasks for sequential processing."""
        # For now, create a simplified sequential approach
        return self._create_multi_domain_subtasks(query, complexity_score)

    def _create_complex_subtasks(self, query: str, complexity_score: float) -> List[SubTask]:
        """Create subtasks for complex queries."""
        # Break down complex queries into manageable pieces
        return self._create_multi_domain_subtasks(query, complexity_score)

    def _create_parallel_subtasks(self, query: str, complexity_score: float) -> List[SubTask]:
        """Create subtasks that can be processed in parallel."""
        subtasks = []
        target_agents = self._identify_target_agents(query)
        
        for i, agent in enumerate(target_agents):
            subtasks.append(SubTask(
                id=f"{agent}_analysis",
                description=f"Analyze from {agent} perspective: {query}",
                target_agents=[agent],
                priority=TaskPriority.HIGH,
                dependencies=[],
                context={"perspective": agent},
                estimated_complexity=complexity_score / len(target_agents)
            ))
        
        return subtasks

    def _identify_target_agents(self, query: str) -> List[str]:
        """Identify which agents should handle a query."""
        query_lower = query.lower()
        agents = []
        
        for agent, spec in self.agent_specializations.items():
            if any(keyword in query_lower for keyword in spec["keywords"]):
                agents.append(agent)
        
        # Default to all agents if none specifically identified
        if not agents:
            agents = ["engineer", "librarian", "priest"]
        
        return agents

    def _determine_execution_strategy(self, subtasks: List[SubTask], task_type: TaskType) -> str:
        """Determine the optimal execution strategy for subtasks."""
        if len(subtasks) == 1:
            return "direct"
        elif task_type == TaskType.SEQUENTIAL:
            return "sequential"
        elif any(task.dependencies for task in subtasks):
            return "dependency_based"
        else:
            return "parallel"

    def _assess_collaboration_level(self, subtasks: List[SubTask]) -> str:
        """Assess the level of collaboration required."""
        if len(subtasks) == 1:
            return "none"
        elif len(subtasks) <= 2:
            return "light"
        else:
            return "heavy"

    def _estimate_total_time(self, subtasks: List[SubTask]) -> float:
        """Estimate total processing time in seconds."""
        if not subtasks:
            return 1.0
        
        # Simple estimation based on complexity and dependencies
        base_time = sum(task.estimated_complexity * 3.0 for task in subtasks)
        dependency_overhead = len([task for task in subtasks if task.dependencies]) * 0.5
        
        return base_time + dependency_overhead


# Create default instance
default_task_decomposer = AdvancedTaskDecomposer()
