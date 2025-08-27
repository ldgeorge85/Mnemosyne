"""
Mnemosyne Action Definitions.

Defines all possible actions the agentic system can take.
Each action preserves user sovereignty with override capabilities.
"""

from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel


class MnemosyneAction(str, Enum):
    """All possible actions in the Mnemosyne system."""
    
    # Persona Management
    SELECT_PERSONA = "SELECT_PERSONA"      # LLM-driven mode selection
    SWITCH_MODE = "SWITCH_MODE"            # Change sovereignty level
    
    # Memory Operations  
    SEARCH_MEMORIES = "SEARCH_MEMORIES"    # Parallel vector search
    CREATE_MEMORY = "CREATE_MEMORY"        # Proactive memory creation
    LINK_MEMORIES = "LINK_MEMORIES"        # Connect related memories
    UPDATE_MEMORY = "UPDATE_MEMORY"        # Modify existing memory
    
    # Task Management
    LIST_TASKS = "LIST_TASKS"              # List/search user's tasks
    CREATE_TASK = "CREATE_TASK"            # Generate tasks from context
    DECOMPOSE_TASK = "DECOMPOSE_TASK"      # Break complex tasks down
    UPDATE_TASK = "UPDATE_TASK"            # Modify task status/details
    COMPLETE_TASK = "COMPLETE_TASK"        # Mark task as done
    
    # Agent Activation
    ACTIVATE_SHADOW = "ACTIVATE_SHADOW"    # Technical agents (Engineer, Librarian, Priest)
    ACTIVATE_DIALOGUE = "ACTIVATE_DIALOGUE" # Philosophical agents (50+ debate agents)
    
    # Trust Operations
    UPDATE_TRUST = "UPDATE_TRUST"          # Modify trust relationships
    CREATE_APPEAL = "CREATE_APPEAL"        # Appeal trust decisions
    
    # Analysis & Reflection
    ANALYZE_PATTERNS = "ANALYZE_PATTERNS"  # Pattern recognition
    REFLECT = "REFLECT"                    # Deep reflection
    SUGGEST = "SUGGEST"                    # Proactive suggestions
    
    # Control Actions
    DONE = "DONE"                          # Sufficient information
    NEED_MORE = "NEED_MORE"                # Request additional context
    EXPLAIN = "EXPLAIN"                    # Explain reasoning
    WAIT_USER = "WAIT_USER"                # Wait for user input


class ActionPayload(BaseModel):
    """Payload for an action to execute."""
    
    action: MnemosyneAction
    parameters: Dict[str, Any] = {}
    reasoning: str  # Why this action was chosen
    confidence: float = 0.8  # 0-1 confidence score
    user_override: Optional[Dict[str, Any]] = None  # User can override
    
    class Config:
        use_enum_values = True


class ActionResult(BaseModel):
    """Result from executing an action."""
    
    action: MnemosyneAction
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: int = 0
    receipt_id: Optional[str] = None  # Receipt for transparency
    
    class Config:
        use_enum_values = True


class ActionPlan(BaseModel):
    """Plan of multiple actions to execute."""
    
    query: str  # Original user query
    context: Dict[str, Any] = {}
    reasoning: str  # Overall reasoning for the plan
    actions: list[ActionPayload] = []
    parallel: bool = True  # Execute in parallel vs sequential
    max_iterations: int = 3  # Max reasoning loops
    
    def add_action(self, action: MnemosyneAction, **kwargs):
        """Add an action to the plan."""
        payload = ActionPayload(
            action=action,
            parameters=kwargs.get('parameters', {}),
            reasoning=kwargs.get('reasoning', ''),
            confidence=kwargs.get('confidence', 0.8)
        )
        self.actions.append(payload)
        return self