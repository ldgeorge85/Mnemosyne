"""
Simple function-based tools for the Mnemosyne system.

These are basic tools that can be executed directly without external dependencies.
"""

import json
import re
from typing import Dict, Any
from datetime import datetime
import logging

from .base import BaseTool, ToolCategory, ToolMetadata, ToolInput, ToolOutput, ToolVisibility

logger = logging.getLogger(__name__)


class CalculatorTool(BaseTool):
    """Simple calculator tool for basic arithmetic operations."""
    
    def _get_default_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="calculator",
            display_name="Calculator",
            description="Performs basic arithmetic calculations",
            category=ToolCategory.SIMPLE,
            capabilities=["math", "calculations", "arithmetic"],
            tags=["math", "utility", "calculator"],
            visibility=ToolVisibility.PUBLIC
        )
    
    async def can_handle(self, query: str, context: Dict) -> float:
        """Check if query involves mathematical operations."""
        math_keywords = ["calculate", "compute", "add", "subtract", "multiply", 
                        "divide", "sum", "average", "mean", "math", "+", "-", "*", "/"]
        
        query_lower = query.lower()
        
        # Check for math patterns
        if re.search(r'\d+\s*[\+\-\*/]\s*\d+', query):
            return 0.9
        
        # Check for keywords
        for keyword in math_keywords:
            if keyword in query_lower:
                return 0.7
        
        return 0.0
    
    async def execute(self, input: ToolInput) -> ToolOutput:
        """Execute the calculation."""
        try:
            expression = input.query or input.parameters.get("expression", "")
            
            if not expression:
                return ToolOutput(
                    success=False,
                    result=None,
                    error="No expression provided"
                )
            
            # Safety check - only allow basic math operations
            allowed_chars = "0123456789+-*/.() "
            if not all(c in allowed_chars for c in expression.replace(" ", "")):
                return ToolOutput(
                    success=False,
                    result=None,
                    error="Invalid characters in expression"
                )
            
            # Evaluate the expression
            result = eval(expression)
            
            return ToolOutput(
                success=True,
                result=result,
                metadata={
                    "expression": expression,
                    "type": "calculation"
                },
                display_format="text"
            )
            
        except Exception as e:
            return ToolOutput(
                success=False,
                result=None,
                error=f"Calculation error: {str(e)}"
            )


class TextFormatterTool(BaseTool):
    """Tool for formatting text in various ways."""
    
    def _get_default_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="text_formatter",
            display_name="Text Formatter",
            description="Formats text (uppercase, lowercase, title case, etc.)",
            category=ToolCategory.SIMPLE,
            capabilities=["text formatting", "case conversion", "text manipulation"],
            tags=["text", "utility", "formatting"],
            visibility=ToolVisibility.PUBLIC
        )
    
    async def can_handle(self, query: str, context: Dict) -> float:
        """Check if query involves text formatting."""
        format_keywords = ["format", "uppercase", "lowercase", "capitalize", 
                          "title case", "snake_case", "camelCase", "reverse"]
        
        query_lower = query.lower()
        
        for keyword in format_keywords:
            if keyword.lower() in query_lower:
                return 0.8
        
        return 0.0
    
    async def execute(self, input: ToolInput) -> ToolOutput:
        """Execute the text formatting."""
        try:
            text = input.query or input.parameters.get("text", "")
            format_type = input.parameters.get("format", "uppercase")
            
            if not text:
                return ToolOutput(
                    success=False,
                    result=None,
                    error="No text provided"
                )
            
            # Apply formatting
            if format_type == "uppercase":
                result = text.upper()
            elif format_type == "lowercase":
                result = text.lower()
            elif format_type == "title":
                result = text.title()
            elif format_type == "capitalize":
                result = text.capitalize()
            elif format_type == "reverse":
                result = text[::-1]
            elif format_type == "snake_case":
                result = re.sub(r'[\s\-]+', '_', text).lower()
            elif format_type == "camelCase":
                words = re.split(r'[\s\-_]+', text)
                result = words[0].lower() + ''.join(w.capitalize() for w in words[1:])
            else:
                result = text
            
            return ToolOutput(
                success=True,
                result=result,
                metadata={
                    "original": text,
                    "format": format_type
                },
                display_format="text"
            )
            
        except Exception as e:
            return ToolOutput(
                success=False,
                result=None,
                error=f"Formatting error: {str(e)}"
            )


class JSONFormatterTool(BaseTool):
    """Tool for formatting and validating JSON."""
    
    def _get_default_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="json_formatter",
            display_name="JSON Formatter",
            description="Formats, validates, and prettifies JSON data",
            category=ToolCategory.SIMPLE,
            capabilities=["json formatting", "json validation", "prettify"],
            tags=["json", "utility", "formatting", "validation"],
            visibility=ToolVisibility.PUBLIC
        )
    
    async def can_handle(self, query: str, context: Dict) -> float:
        """Check if query involves JSON operations."""
        json_keywords = ["json", "format json", "validate json", "prettify", "parse"]
        
        query_lower = query.lower()
        
        for keyword in json_keywords:
            if keyword in query_lower:
                return 0.8
        
        # Check if the query contains JSON-like structure
        if "{" in query and "}" in query:
            return 0.6
        
        return 0.0
    
    async def execute(self, input: ToolInput) -> ToolOutput:
        """Execute JSON formatting/validation."""
        try:
            json_str = input.query or input.parameters.get("json", "")
            indent = input.parameters.get("indent", 2)
            
            if not json_str:
                return ToolOutput(
                    success=False,
                    result=None,
                    error="No JSON provided"
                )
            
            # Try to parse the JSON
            try:
                parsed = json.loads(json_str)
                formatted = json.dumps(parsed, indent=indent, sort_keys=True)
                
                return ToolOutput(
                    success=True,
                    result=formatted,
                    metadata={
                        "valid": True,
                        "keys": len(parsed) if isinstance(parsed, dict) else None,
                        "type": type(parsed).__name__
                    },
                    display_format="json"
                )
                
            except json.JSONDecodeError as e:
                return ToolOutput(
                    success=False,
                    result=None,
                    error=f"Invalid JSON: {str(e)}",
                    metadata={
                        "valid": False,
                        "error_position": e.pos if hasattr(e, 'pos') else None
                    }
                )
            
        except Exception as e:
            return ToolOutput(
                success=False,
                result=None,
                error=f"Processing error: {str(e)}"
            )


class DateTimeTool(BaseTool):
    """Tool for date and time operations."""
    
    def _get_default_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="datetime",
            display_name="Date & Time",
            description="Get current time, format dates, calculate time differences",
            category=ToolCategory.SIMPLE,
            capabilities=["current time", "date formatting", "time calculations"],
            tags=["date", "time", "utility", "timestamp"],
            visibility=ToolVisibility.PUBLIC
        )
    
    async def can_handle(self, query: str, context: Dict) -> float:
        """Check if query involves date/time operations."""
        time_keywords = ["time", "date", "now", "today", "yesterday", "tomorrow",
                        "timestamp", "day", "month", "year", "hour", "minute"]
        
        query_lower = query.lower()
        
        for keyword in time_keywords:
            if keyword in query_lower:
                return 0.7
        
        return 0.0
    
    async def execute(self, input: ToolInput) -> ToolOutput:
        """Execute date/time operation."""
        try:
            operation = input.parameters.get("operation", "now")
            
            if operation == "now":
                now = datetime.utcnow()
                result = {
                    "utc": now.isoformat(),
                    "unix": int(now.timestamp()),
                    "formatted": now.strftime("%Y-%m-%d %H:%M:%S UTC")
                }
            elif operation == "format":
                date_str = input.parameters.get("date", datetime.utcnow().isoformat())
                format_str = input.parameters.get("format", "%Y-%m-%d %H:%M:%S")
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                result = dt.strftime(format_str)
            else:
                result = datetime.utcnow().isoformat()
            
            return ToolOutput(
                success=True,
                result=result,
                metadata={
                    "operation": operation
                },
                display_format="json" if isinstance(result, dict) else "text"
            )
            
        except Exception as e:
            return ToolOutput(
                success=False,
                result=None,
                error=f"Date/time error: {str(e)}"
            )


class WordCounterTool(BaseTool):
    """Tool for counting words, characters, and lines in text."""
    
    def _get_default_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="word_counter",
            display_name="Word Counter",
            description="Count words, characters, lines, and analyze text statistics",
            category=ToolCategory.SIMPLE,
            capabilities=["word count", "character count", "text analysis"],
            tags=["text", "analysis", "utility", "statistics"],
            visibility=ToolVisibility.PUBLIC
        )
    
    async def can_handle(self, query: str, context: Dict) -> float:
        """Check if query involves counting text elements."""
        count_keywords = ["count", "how many", "words", "characters", "lines",
                         "length", "statistics", "analyze text"]
        
        query_lower = query.lower()
        
        for keyword in count_keywords:
            if keyword in query_lower:
                return 0.7
        
        return 0.0
    
    async def execute(self, input: ToolInput) -> ToolOutput:
        """Execute text counting/analysis."""
        try:
            text = input.query or input.parameters.get("text", "")
            
            if not text:
                return ToolOutput(
                    success=False,
                    result=None,
                    error="No text provided"
                )
            
            # Calculate statistics
            words = text.split()
            lines = text.split('\n')
            
            result = {
                "words": len(words),
                "characters": len(text),
                "characters_no_spaces": len(text.replace(" ", "")),
                "lines": len(lines),
                "paragraphs": len([p for p in text.split('\n\n') if p.strip()]),
                "average_word_length": sum(len(w) for w in words) / len(words) if words else 0,
                "unique_words": len(set(w.lower() for w in words))
            }
            
            return ToolOutput(
                success=True,
                result=result,
                metadata={
                    "text_preview": text[:100] + "..." if len(text) > 100 else text
                },
                display_format="json"
            )
            
        except Exception as e:
            return ToolOutput(
                success=False,
                result=None,
                error=f"Analysis error: {str(e)}"
            )