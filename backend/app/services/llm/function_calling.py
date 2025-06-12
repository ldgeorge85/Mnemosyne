"""
Function Calling Framework

This module provides a framework for defining, registering, and executing
tool functions that can be called by language models.
"""
import inspect
import json
import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Type, Union, get_type_hints
from functools import wraps

from pydantic import BaseModel, Field, create_model

from app.services.llm.response_parser import ResponseParser


# Set up module logger
logger = logging.getLogger(__name__)


class FunctionCallMode(str, Enum):
    """Function calling modes for the OpenAI API."""
    NONE = "none"  # Do not call functions
    AUTO = "auto"  # Automatically call functions when appropriate
    REQUIRED = "required"  # Always require a function call


class FunctionDefinition(BaseModel):
    """Definition of a function that can be called by an LLM."""
    name: str
    description: str
    parameters: Dict[str, Any]
    required_params: List[str] = Field(default_factory=list)


class FunctionRegistry:
    """
    Registry for functions that can be called by LLMs.
    
    This class maintains a registry of functions and their definitions,
    provides serialization to OpenAI's function calling format, and
    handles execution of function calls.
    """
    
    def __init__(self):
        """Initialize an empty function registry."""
        self._functions: Dict[str, Callable] = {}
        self._definitions: Dict[str, FunctionDefinition] = {}
    
    def register(
        self,
        func: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Callable:
        """
        Register a function that can be called by LLMs.
        
        Can be used as a decorator or as a regular function.
        
        Args:
            func: Function to register
            name: Override function name
            description: Override function description
            
        Returns:
            Original function (for decorator use)
            
        Example:
            @registry.register
            def get_weather(location: str, unit: str = "celsius") -> Dict[str, Any]:
                '''Get weather for a location.'''
                # Function implementation
                return {"temperature": 22.5, "conditions": "sunny"}
        """
        def _register(f: Callable) -> Callable:
            func_name = name or f.__name__
            func_desc = description or inspect.getdoc(f) or "No description"
            
            # Get type hints
            hints = get_type_hints(f)
            return_type = hints.pop('return', Any)
            
            # Get signature
            sig = inspect.signature(f)
            
            # Build parameters schema
            parameters = {
                "type": "object",
                "properties": {},
                "required": []
            }
            
            for param_name, param in sig.parameters.items():
                param_type = hints.get(param_name, Any)
                
                # Skip self/cls parameters
                if param_name in ("self", "cls"):
                    continue
                
                # Convert type to JSON schema type
                json_type = self._type_to_json_schema_type(param_type)
                
                # Add parameter to schema
                parameters["properties"][param_name] = json_type
                
                # Check if parameter is required
                if param.default == inspect.Parameter.empty:
                    parameters["required"].append(param_name)
            
            # Create function definition
            definition = FunctionDefinition(
                name=func_name,
                description=func_desc,
                parameters=parameters,
                required_params=parameters["required"]
            )
            
            # Register function and definition
            self._functions[func_name] = f
            self._definitions[func_name] = definition
            
            return f
        
        if func is None:
            # Used as factory: @register(name="foo")
            return _register
        else:
            # Used as decorator: @register
            return _register(func)
    
    def _type_to_json_schema_type(self, type_hint: Type) -> Dict[str, Any]:
        """
        Convert a Python type hint to a JSON schema type.
        
        Args:
            type_hint: Python type hint
            
        Returns:
            JSON schema type definition
        """
        # Handle simple types
        if type_hint == str:
            return {"type": "string"}
        elif type_hint == int:
            return {"type": "integer"}
        elif type_hint == float:
            return {"type": "number"}
        elif type_hint == bool:
            return {"type": "boolean"}
        elif type_hint == Any:
            return {"type": "object"}
        
        # Handle lists
        origin = getattr(type_hint, "__origin__", None)
        if origin == list:
            args = getattr(type_hint, "__args__", [Any])
            item_type = self._type_to_json_schema_type(args[0])
            return {
                "type": "array",
                "items": item_type
            }
        
        # Handle dictionaries
        if origin == dict:
            return {"type": "object"}
        
        # Handle optional types
        if origin == Union:
            args = getattr(type_hint, "__args__", [])
            # Check if this is an Optional[T] (Union[T, None])
            if len(args) == 2 and args[1] == type(None):
                return self._type_to_json_schema_type(args[0])
        
        # Handle Pydantic models
        if hasattr(type_hint, "schema") and callable(getattr(type_hint, "schema")):
            return type_hint.schema()
        
        # Handle enums
        if issubclass(type_hint, Enum):
            return {
                "type": "string",
                "enum": [e.value for e in type_hint]
            }
        
        # Default to object
        return {"type": "object"}
    
    def get_definitions(self) -> List[FunctionDefinition]:
        """
        Get all function definitions.
        
        Returns:
            List of function definitions
        """
        return list(self._definitions.values())
    
    def get_openai_schema(self) -> List[Dict[str, Any]]:
        """
        Get function definitions in OpenAI's format.
        
        Returns:
            List of function definitions in OpenAI's format
        """
        result = []
        
        for name, definition in self._definitions.items():
            result.append({
                "name": definition.name,
                "description": definition.description,
                "parameters": definition.parameters
            })
            
        return result
    
    def execute(self, name: str, params: Dict[str, Any]) -> Any:
        """
        Execute a registered function with the given parameters.
        
        Args:
            name: Name of the function to execute
            params: Parameters to pass to the function
            
        Returns:
            Result of the function
            
        Raises:
            ValueError: If the function is not registered or parameters are invalid
        """
        if name not in self._functions:
            raise ValueError(f"Function '{name}' is not registered")
        
        func = self._functions[name]
        definition = self._definitions[name]
        
        # Validate required parameters
        for param in definition.required_params:
            if param not in params:
                raise ValueError(f"Missing required parameter '{param}' for function '{name}'")
        
        try:
            # Execute function
            result = func(**params)
            return result
        except Exception as e:
            logger.error(f"Error executing function '{name}': {e}")
            raise
    
    def parse_and_execute(self, llm_response: str) -> Optional[Any]:
        """
        Parse an LLM response and execute the function call if present.
        
        Args:
            llm_response: Response from the LLM
            
        Returns:
            Result of the function call, or None if no function call was present
        """
        # Extract function call from response
        function_call = self._extract_function_call(llm_response)
        
        if not function_call:
            return None
        
        # Extract function name and parameters
        name = function_call.get("name")
        
        if not name:
            logger.warning("Function call found but no name specified")
            return None
        
        # Get parameters
        params_str = function_call.get("arguments", "{}")
        
        try:
            # Parse parameters
            params = json.loads(params_str)
            
            # Execute function
            result = self.execute(name, params)
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing function call parameters: {e}")
            return None
        except Exception as e:
            logger.error(f"Error executing function call: {e}")
            return None
    
    def _extract_function_call(self, llm_response: str) -> Optional[Dict[str, Any]]:
        """
        Extract function call from LLM response.
        
        Args:
            llm_response: Response from the LLM
            
        Returns:
            Function call information, or None if not found
        """
        # Try to extract JSON from response
        json_blocks = ResponseParser.extract_json_blocks(llm_response)
        
        for block in json_blocks:
            try:
                data = json.loads(block)
                
                # Check if this is a function call
                if "function_call" in data:
                    return data["function_call"]
                
                # Also check if it's directly a function call
                if "name" in data and "arguments" in data:
                    return data
            except Exception:
                continue
        
        # Try regex patterns for function calls
        import re
        patterns = [
            r'function_call\s*:\s*{\s*"name"\s*:\s*"([^"]+)"\s*,\s*"arguments"\s*:\s*({[^}]+})\s*}',
            r'{\s*"name"\s*:\s*"([^"]+)"\s*,\s*"arguments"\s*:\s*({[^}]+})\s*}'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, llm_response, re.DOTALL)
            if match:
                try:
                    name = match.group(1)
                    args_str = match.group(2)
                    return {
                        "name": name,
                        "arguments": args_str
                    }
                except Exception:
                    continue
        
        return None


# Global function registry
function_registry = FunctionRegistry()


class ToolExecutor:
    """
    Executor for tool functions called by an LLM.
    
    This class handles the flow of function calling, including
    prompting the LLM with available functions and processing
    the resulting function calls.
    """
    
    def __init__(self, registry: Optional[FunctionRegistry] = None):
        """
        Initialize a tool executor.
        
        Args:
            registry: Function registry to use
        """
        self.registry = registry or function_registry
    
    def get_openai_parameters(
        self,
        mode: FunctionCallMode = FunctionCallMode.AUTO,
        function_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get parameters for the OpenAI API to enable function calling.
        
        Args:
            mode: Function calling mode
            function_names: Names of functions to include (or all if None)
            
        Returns:
            Parameters for the OpenAI API
        """
        params = {
            "functions": self.registry.get_openai_schema()
        }
        
        # Filter functions if specified
        if function_names:
            params["functions"] = [
                f for f in params["functions"]
                if f["name"] in function_names
            ]
        
        # Add function_call parameter
        if mode == FunctionCallMode.NONE:
            params["function_call"] = "none"
        elif mode == FunctionCallMode.REQUIRED:
            params["function_call"] = "required"
        else:
            params["function_call"] = "auto"
        
        return params
    
    async def run_conversation(
        self,
        openai_client: Any,
        messages: List[Dict[str, str]],
        available_functions: Optional[List[str]] = None,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_turns: int = 5
    ) -> Dict[str, Any]:
        """
        Run a conversation with function calling.
        
        Args:
            openai_client: OpenAI client instance
            messages: Initial messages
            available_functions: List of available function names
            system_prompt: System prompt to use
            model: Model to use
            max_turns: Maximum number of turns
            
        Returns:
            Result of the conversation
        """
        # Create a copy of the messages
        conversation_messages = messages.copy()
        
        # Add system prompt if provided
        if system_prompt and not any(m.get("role") == "system" for m in conversation_messages):
            conversation_messages.insert(0, {
                "role": "system",
                "content": system_prompt
            })
        
        # Get OpenAI parameters
        openai_params = self.get_openai_parameters(
            mode=FunctionCallMode.AUTO,
            function_names=available_functions
        )
        
        # Run the conversation
        for _ in range(max_turns):
            # Call the API
            response = await openai_client.chat_completion(
                messages=conversation_messages,
                model=model,
                stream=False,
                **openai_params
            )
            
            # Extract content and function call
            assistant_message = {
                "role": "assistant",
                "content": response
            }
            conversation_messages.append(assistant_message)
            
            # Check for function calls
            function_call = self.registry.parse_and_execute(response)
            
            if not function_call:
                # No function call, we're done
                return {
                    "messages": conversation_messages,
                    "function_calls": []
                }
            
            # Add function call to messages
            function_message = {
                "role": "function",
                "name": function_call.get("name"),
                "content": json.dumps(function_call.get("result"))
            }
            conversation_messages.append(function_message)
        
        # Max turns reached
        return {
            "messages": conversation_messages,
            "function_calls": [m for m in conversation_messages if m.get("role") == "function"],
            "truncated": True
        }


# Example function definitions

@function_registry.register
def get_current_weather(location: str, unit: str = "celsius") -> Dict[str, Any]:
    """
    Get the current weather for a location.
    
    Args:
        location: The location to get weather for
        unit: The unit to use (celsius or fahrenheit)
        
    Returns:
        Weather information
    """
    # This is a demo function that would be implemented with a real API
    return {
        "location": location,
        "temperature": 22.5 if unit == "celsius" else 72.5,
        "unit": unit,
        "condition": "sunny",
        "humidity": 50
    }


@function_registry.register
def search_database(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search the knowledge database for information.
    
    Args:
        query: Search query
        limit: Maximum number of results to return
        
    Returns:
        List of search results
    """
    # This is a demo function that would be implemented with a real database
    return [
        {
            "id": "1",
            "title": "Example document",
            "content": "This is an example search result.",
            "relevance": 0.95
        }
    ]
