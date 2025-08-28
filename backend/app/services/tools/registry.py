"""
Tool Registry for discovering, managing, and executing tools
"""

import asyncio
from typing import Dict, List, Optional, Set, Type
from pathlib import Path
import importlib
import inspect
import logging

from .base import BaseTool, ToolCategory, ToolInput, ToolOutput, ToolMetadata, ToolVisibility
from .exceptions import ToolNotFoundError, ToolExecutionError

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Central registry for all tools in the system.
    Handles discovery, registration, and tool lifecycle management.
    """
    
    def __init__(self):
        """Initialize the tool registry"""
        self.tools: Dict[str, BaseTool] = {}
        self.categories: Dict[ToolCategory, Set[str]] = {
            category: set() for category in ToolCategory
        }
        self.tags: Dict[str, Set[str]] = {}  # tag -> tool names
        self._initialized = False
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        """Initialize the registry and discover tools"""
        async with self._lock:
            if self._initialized:
                return
                
            logger.info("Initializing tool registry...")
            
            # Discover built-in tools
            await self._discover_builtin_tools()
            
            # Discover plugin tools
            await self._discover_plugin_tools()
            
            # Initialize all tools
            await self._initialize_all_tools()
            
            self._initialized = True
            logger.info(f"Tool registry initialized with {len(self.tools)} tools")
    
    async def _discover_builtin_tools(self) -> None:
        """Discover and register built-in tools"""
        # Import built-in tool modules
        builtin_modules = [
            "simple",      # Simple function tools
            "agents",      # Agent-based tools (Shadow Council, Forum of Echoes)
            "composite",   # Composite tools
        ]
        
        for module_name in builtin_modules:
            try:
                module_path = f"app.services.tools.{module_name}"
                module = importlib.import_module(module_path)
                
                # Find all BaseTool subclasses in the module
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, BaseTool) and 
                        obj != BaseTool):
                        
                        # Instantiate and register the tool
                        tool = obj()
                        await self._register_internal(tool)
                        logger.info(f"Registered tool from {module_name}: {name}")
                        
            except ImportError as e:
                logger.info(f"Module {module_name} not found, skipping: {e}")
    
    async def _discover_plugin_tools(self, plugin_dir: Optional[Path] = None) -> None:
        """Discover and register plugin tools from a directory"""
        if plugin_dir is None:
            plugin_dir = Path("tools/plugins")
        
        if not plugin_dir.exists():
            logger.debug(f"Plugin directory {plugin_dir} does not exist")
            return
        
        # TODO: Implement plugin discovery from YAML/Python files
        # This will scan the plugin directory and load tool definitions
        pass
    
    async def _initialize_all_tools(self) -> None:
        """Initialize all registered tools"""
        tasks = []
        for tool in self.tools.values():
            tasks.append(tool.initialize())
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _register_internal(self, tool: BaseTool) -> None:
        """
        Internal registration without lock (used during initialization)
        """
        metadata = tool.metadata
        
        # Check for duplicate
        if metadata.name in self.tools:
            logger.warning(f"Tool {metadata.name} already registered, overwriting")
        
        # Register in main registry
        self.tools[metadata.name] = tool
        
        # Register by category
        self.categories[metadata.category].add(metadata.name)
        
        # Register by tags
        for tag in metadata.tags:
            if tag not in self.tags:
                self.tags[tag] = set()
            self.tags[tag].add(metadata.name)
        
        logger.info(f"Registered tool: {metadata.name} ({metadata.category})")
    
    async def register(self, tool: BaseTool) -> None:
        """
        Register a tool in the registry
        
        Args:
            tool: Tool instance to register
        """
        async with self._lock:
            await self._register_internal(tool)
    
    async def unregister(self, tool_name: str) -> None:
        """
        Unregister a tool from the registry
        
        Args:
            tool_name: Name of tool to unregister
        """
        async with self._lock:
            if tool_name not in self.tools:
                raise ToolNotFoundError(f"Tool {tool_name} not found")
            
            tool = self.tools[tool_name]
            metadata = tool.metadata
            
            # Cleanup the tool
            await tool.cleanup()
            
            # Remove from registries
            del self.tools[tool_name]
            self.categories[metadata.category].discard(tool_name)
            
            for tag in metadata.tags:
                if tag in self.tags:
                    self.tags[tag].discard(tool_name)
            
            logger.info(f"Unregistered tool: {tool_name}")
    
    def get(self, tool_name: str) -> BaseTool:
        """
        Get a tool by name
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool instance
            
        Raises:
            ToolNotFoundError if tool not found
        """
        if tool_name not in self.tools:
            raise ToolNotFoundError(f"Tool {tool_name} not found")
        return self.tools[tool_name]
    
    def list_tools(self, 
                   category: Optional[ToolCategory] = None,
                   tag: Optional[str] = None,
                   visibility: Optional[ToolVisibility] = None) -> List[str]:
        """
        List tools matching the given filters
        
        Args:
            category: Filter by category
            tag: Filter by tag
            visibility: Filter by visibility level
            
        Returns:
            List of tool names
        """
        tools = set(self.tools.keys())
        
        # Filter by category
        if category is not None:
            tools &= self.categories.get(category, set())
        
        # Filter by tag
        if tag is not None:
            tools &= self.tags.get(tag, set())
        
        # Filter by visibility
        if visibility is not None:
            tools = {
                name for name in tools
                if self.tools[name].metadata.visibility == visibility
            }
        
        return sorted(list(tools))
    
    async def get_relevant_tools(self, 
                                  query: str, 
                                  context: Dict,
                                  threshold: float = 0.3,
                                  max_tools: int = 5) -> List[tuple[str, float]]:
        """
        Get tools relevant to a query, sorted by confidence
        
        Args:
            query: User query
            context: Execution context
            threshold: Minimum confidence threshold
            max_tools: Maximum number of tools to return
            
        Returns:
            List of (tool_name, confidence) tuples sorted by confidence
        """
        relevance_scores = []
        
        # Check each tool's relevance
        for tool_name, tool in self.tools.items():
            try:
                confidence = await tool.can_handle(query, context)
                if confidence >= threshold:
                    relevance_scores.append((tool_name, confidence))
            except Exception as e:
                logger.debug(f"Error checking relevance for {tool_name}: {e}")
        
        # Sort by confidence and return top N
        relevance_scores.sort(key=lambda x: x[1], reverse=True)
        return relevance_scores[:max_tools]
    
    async def execute_tool(self, 
                           tool_name: str,
                           input: ToolInput) -> ToolOutput:
        """
        Execute a tool by name
        
        Args:
            tool_name: Name of tool to execute
            input: Tool input
            
        Returns:
            Tool output
            
        Raises:
            ToolNotFoundError if tool not found
            ToolExecutionError if execution fails
        """
        tool = self.get(tool_name)
        
        try:
            output = await tool(input)  # Uses __call__ with timeout
            return output
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            raise ToolExecutionError(f"Failed to execute tool {tool_name}: {str(e)}")
    
    async def execute_multiple(self,
                               tool_inputs: List[tuple[str, ToolInput]],
                               parallel: bool = True) -> List[ToolOutput]:
        """
        Execute multiple tools
        
        Args:
            tool_inputs: List of (tool_name, input) tuples
            parallel: Execute in parallel if True, sequential if False
            
        Returns:
            List of outputs in same order as inputs
        """
        if parallel:
            tasks = [
                self.execute_tool(name, input)
                for name, input in tool_inputs
            ]
            return await asyncio.gather(*tasks, return_exceptions=True)
        else:
            results = []
            for name, input in tool_inputs:
                try:
                    result = await self.execute_tool(name, input)
                    results.append(result)
                except Exception as e:
                    results.append(ToolOutput(
                        success=False,
                        result=None,
                        error=str(e)
                    ))
            return results
    
    def get_tool_metadata(self, tool_name: str) -> ToolMetadata:
        """Get metadata for a tool"""
        tool = self.get(tool_name)
        return tool.metadata
    
    def search_tools(self, search_term: str) -> List[str]:
        """
        Search for tools by name, description, or tags
        
        Args:
            search_term: Term to search for
            
        Returns:
            List of matching tool names
        """
        search_lower = search_term.lower()
        matching_tools = []
        
        for tool_name, tool in self.tools.items():
            metadata = tool.metadata
            
            # Check name
            if search_lower in tool_name.lower():
                matching_tools.append(tool_name)
                continue
            
            # Check display name
            if search_lower in metadata.display_name.lower():
                matching_tools.append(tool_name)
                continue
            
            # Check description
            if search_lower in metadata.description.lower():
                matching_tools.append(tool_name)
                continue
            
            # Check tags
            for tag in metadata.tags:
                if search_lower in tag.lower():
                    matching_tools.append(tool_name)
                    break
        
        return matching_tools
    
    async def cleanup(self) -> None:
        """Cleanup all tools and resources"""
        async with self._lock:
            tasks = []
            for tool in self.tools.values():
                tasks.append(tool.cleanup())
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            self.tools.clear()
            for category_set in self.categories.values():
                category_set.clear()
            self.tags.clear()
            self._initialized = False


# Global registry instance
tool_registry = ToolRegistry()