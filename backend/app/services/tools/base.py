"""
Base Tool Interface for Mnemosyne Tools & Plugin System

All tools (simple functions, agents, external APIs, composite orchestrations)
must implement this interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import asyncio
from pydantic import BaseModel, Field


class ToolCategory(str, Enum):
    """Categories of tools available in the system"""
    SIMPLE = "simple"          # Direct function implementations
    AGENT = "agent"            # LLM-powered sub-agents
    EXTERNAL = "external"      # API integrations (REST, GraphQL)
    COMPOSITE = "composite"    # Tools that orchestrate other tools
    PIPELINE = "pipeline"      # Tools that chain other tools
    PROTOCOL = "protocol"      # Protocol adapters (MCP, A2A, OpenAPI)


class ToolVisibility(str, Enum):
    """Visibility levels for tools"""
    PRIVATE = "private"        # Only available to owner
    LOCAL = "local"           # Available on local network
    PARTNER = "partner"       # Available to trusted partners
    PUBLIC = "public"         # Publicly available


@dataclass
class ToolMetadata:
    """Metadata about a tool"""
    name: str                          # Unique identifier
    display_name: str                  # Human-readable name
    description: str                   # What it does
    category: ToolCategory             # Tool category
    version: str = "1.0.0"            # Tool version
    author: str = "mnemosyne"         # Tool author
    capabilities: List[str] = field(default_factory=list)  # What it can help with
    tags: List[str] = field(default_factory=list)         # Searchable tags
    
    # Configuration
    requires_auth: bool = False        # Needs API keys?
    cost_estimate: float = 0.0         # Computational/API cost
    timeout: int = 30                  # Max execution time in seconds
    max_retries: int = 3               # Max retry attempts
    
    # Visibility & Privacy
    visibility: ToolVisibility = ToolVisibility.PRIVATE
    exposes_user_data: bool = False    # Does it share user data?
    privacy_preserving: bool = True     # Does it protect privacy?
    
    # UI Integration
    icon: Optional[str] = None          # Icon identifier for UI
    color: Optional[str] = None         # Color theme
    ui_schema: Optional[Dict] = None    # JSON schema for UI form generation


class ToolInput(BaseModel):
    """Standard input format for all tools"""
    query: str                         # Primary input/query
    parameters: Dict[str, Any] = {}    # Tool-specific parameters
    context: Dict[str, Any] = {}       # Conversation/execution context
    options: Dict[str, Any] = {}       # Execution options (timeout, retries, etc.)
    
    # Authentication & Privacy
    auth_token: Optional[str] = None   # For external tools
    privacy_level: str = "strict"      # Privacy enforcement level
    
    # Tracing
    trace_id: Optional[str] = None     # For distributed tracing
    parent_tool: Optional[str] = None  # If called by another tool


class ToolOutput(BaseModel):
    """Standard output format for all tools"""
    success: bool                      # Execution successful?
    result: Any                        # Tool-specific output
    error: Optional[str] = None        # Error message if failed
    
    # Metadata
    metadata: Dict[str, Any] = {}      # Execution metadata
    display_format: str = "text"       # How to render (text|json|markdown|html)
    confidence: float = 1.0            # Result confidence (0-1)
    
    # Attribution & Cost
    sources: List[str] = []            # Data sources used
    cost: float = 0.0                 # Actual cost incurred
    tokens_used: Optional[int] = None  # LLM tokens consumed
    
    # Timing
    execution_time: Optional[float] = None  # Seconds
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Suggestions
    follow_up_tools: List[str] = []    # Suggested next tools
    related_tools: List[str] = []      # Related tools to consider


class BaseTool(ABC):
    """
    Abstract base class for all tools in the Mnemosyne system.
    
    Every tool must implement this interface, whether it's a simple function,
    an LLM agent, an external API, or a composite orchestration.
    """
    
    def __init__(self, metadata: Optional[ToolMetadata] = None):
        """Initialize the tool with metadata"""
        self.metadata = metadata or self._get_default_metadata()
        self._initialized = False
        self._cache = {}
        
    @abstractmethod
    def _get_default_metadata(self) -> ToolMetadata:
        """Return default metadata for this tool"""
        pass
        
    async def initialize(self) -> None:
        """
        Initialize the tool (load models, connect to APIs, etc.)
        Called once before first use.
        """
        self._initialized = True
        
    async def cleanup(self) -> None:
        """
        Cleanup resources (close connections, free memory, etc.)
        Called when tool is being unloaded.
        """
        self._cache.clear()
        self._initialized = False
    
    @abstractmethod
    async def can_handle(self, query: str, context: Dict) -> float:
        """
        Returns confidence (0-1) that this tool is relevant for the query.
        Used by the tool selector to determine which tools to use.
        
        Args:
            query: The user's query/request
            context: Current conversation/execution context
            
        Returns:
            Confidence score between 0 and 1
        """
        pass
    
    @abstractmethod
    async def execute(self, input: ToolInput) -> ToolOutput:
        """
        Execute the tool with given input.
        
        This is the main entry point for tool execution. Should handle
        all tool-specific logic including error handling and retries.
        
        Args:
            input: Standardized tool input
            
        Returns:
            Standardized tool output
        """
        pass
    
    async def validate_input(self, input: ToolInput) -> bool:
        """
        Validate input before execution.
        Override for tool-specific validation.
        
        Args:
            input: Input to validate
            
        Returns:
            True if valid, raises ToolValidationError otherwise
        """
        if not input.query and not input.parameters:
            from .exceptions import ToolValidationError
            raise ToolValidationError("Tool input must have either query or parameters")
        return True
    
    def get_ui_schema(self) -> Dict:
        """
        Returns JSON schema for UI form generation.
        Used to generate tool-specific configuration forms.
        
        Returns:
            JSON schema dict
        """
        return self.metadata.ui_schema or {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "title": "Query",
                    "description": f"Input for {self.metadata.display_name}"
                }
            }
        }
    
    def format_output_for_display(self, output: ToolOutput) -> str:
        """
        Format output for display in chat or UI.
        Override for tool-specific formatting.
        
        Args:
            output: Tool output to format
            
        Returns:
            Formatted string for display
        """
        if output.display_format == "json":
            import json
            return f"```json\n{json.dumps(output.result, indent=2)}\n```"
        elif output.display_format == "markdown":
            return str(output.result)
        else:
            return str(output.result)
    
    async def estimate_cost(self, input: ToolInput) -> float:
        """
        Estimate the cost of executing this tool.
        Override for tools with variable costs.
        
        Args:
            input: Tool input
            
        Returns:
            Estimated cost
        """
        return self.metadata.cost_estimate
    
    async def __call__(self, input: ToolInput) -> ToolOutput:
        """
        Make tool callable directly.
        Handles initialization, validation, execution with timeout.
        """
        # Initialize if needed
        if not self._initialized:
            await self.initialize()
        
        # Validate input
        await self.validate_input(input)
        
        # Execute with timeout
        try:
            import time
            start_time = time.time()
            
            result = await asyncio.wait_for(
                self.execute(input),
                timeout=input.options.get("timeout", self.metadata.timeout)
            )
            
            result.execution_time = time.time() - start_time
            return result
            
        except asyncio.TimeoutError:
            from .exceptions import ToolTimeoutError
            raise ToolTimeoutError(
                f"Tool {self.metadata.name} timed out after {self.metadata.timeout} seconds"
            )
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name='{self.metadata.name}' category='{self.metadata.category}'>"