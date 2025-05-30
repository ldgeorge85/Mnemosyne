"""
LLM Response Parsing System

This module provides utilities for parsing and validating responses from
language models, including structured output formats, error handling,
and response transformation.
"""
import re
import json
import logging
from enum import Enum
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, Generic, Callable
from pydantic import BaseModel, Field, ValidationError

# Set up module logger
logger = logging.getLogger(__name__)

# Generic type variable for response models
T = TypeVar('T', bound=BaseModel)


class OutputFormat(str, Enum):
    """Supported output formats for LLM responses."""
    JSON = "json"
    MARKDOWN = "markdown"
    TEXT = "text"
    YAML = "yaml"


class ParsingError(Exception):
    """Error raised when parsing a response fails."""
    pass


class ResponseParsingResult(Generic[T]):
    """
    Result of parsing an LLM response.
    
    Contains the parsed data (if successful), any parsing errors,
    and the original response.
    """
    
    def __init__(
        self,
        original_response: str,
        parsed_data: Optional[T] = None,
        error: Optional[Exception] = None,
        error_message: Optional[str] = None
    ):
        """
        Initialize a response parsing result.
        
        Args:
            original_response: The original response from the LLM
            parsed_data: The parsed data, if parsing was successful
            error: The exception that occurred during parsing, if any
            error_message: A human-readable error message
        """
        self.original_response = original_response
        self.parsed_data = parsed_data
        self.error = error
        self.error_message = error_message or (str(error) if error else None)
    
    @property
    def is_success(self) -> bool:
        """Check if parsing was successful."""
        return self.parsed_data is not None and self.error is None
    
    def __bool__(self) -> bool:
        """Convert to boolean for condition checks."""
        return self.is_success


class ResponseParser:
    """
    Parser for LLM responses that handles various output formats.
    
    This class provides methods to extract structured data from
    LLM responses and convert them to Pydantic models or Python objects.
    """
    
    @staticmethod
    def extract_code_blocks(text: str, language: Optional[str] = None) -> List[str]:
        """
        Extract code blocks from markdown text.
        
        Args:
            text: Text containing markdown code blocks
            language: Specific language to filter by
            
        Returns:
            List of extracted code blocks
        """
        if language:
            pattern = rf"```(?:{language}|{language.lower()})(.*?)```"
        else:
            pattern = r"```(?:\w*)\n?(.*?)```"
            
        matches = re.finditer(pattern, text, re.DOTALL)
        return [match.group(1).strip() for match in matches]
    
    @staticmethod
    def extract_json_blocks(text: str) -> List[str]:
        """
        Extract JSON blocks from text, handling both code blocks and raw JSON.
        
        Args:
            text: Text containing JSON
            
        Returns:
            List of extracted JSON strings
        """
        # First, try to find JSON in code blocks
        json_blocks = ResponseParser.extract_code_blocks(text, "json")
        
        # If no code blocks found, try to find raw JSON
        if not json_blocks:
            # Look for patterns that might indicate JSON objects
            json_patterns = [
                r"\{(?:[^{}]|(?R))*\}",  # Match nested JSON objects
                r"\[(?:[^\[\]]|(?R))*\]"  # Match JSON arrays
            ]
            
            for pattern in json_patterns:
                matches = re.finditer(pattern, text, re.DOTALL)
                json_candidates = [match.group(0) for match in matches]
                
                # Validate each candidate as JSON
                for candidate in json_candidates:
                    try:
                        json.loads(candidate)
                        json_blocks.append(candidate)
                    except json.JSONDecodeError:
                        continue
        
        return json_blocks
    
    @classmethod
    def parse_json_to_model(cls, text: str, model_class: Type[T]) -> ResponseParsingResult[T]:
        """
        Parse JSON from text and convert to a Pydantic model.
        
        Args:
            text: Text containing JSON
            model_class: Pydantic model class to parse into
            
        Returns:
            Parsing result with the model instance if successful
        """
        try:
            # Extract JSON blocks
            json_blocks = cls.extract_json_blocks(text)
            
            if not json_blocks:
                return ResponseParsingResult(
                    original_response=text,
                    error=ParsingError("No JSON found in response"),
                    error_message="Could not find any valid JSON in the response"
                )
            
            # Try each JSON block until one works
            for json_str in json_blocks:
                try:
                    # Parse JSON
                    data = json.loads(json_str)
                    
                    # Convert to model
                    parsed_model = model_class.parse_obj(data)
                    
                    return ResponseParsingResult(
                        original_response=text,
                        parsed_data=parsed_model
                    )
                except json.JSONDecodeError:
                    continue
                except ValidationError as e:
                    logger.warning(f"Validation error parsing JSON to {model_class.__name__}: {e}")
                    continue
            
            # If we got here, none of the JSON blocks were valid
            return ResponseParsingResult(
                original_response=text,
                error=ParsingError("Found JSON but could not parse to the specified model"),
                error_message=f"JSON validation failed for model {model_class.__name__}"
            )
            
        except Exception as e:
            logger.error(f"Error parsing JSON to model: {e}")
            return ResponseParsingResult(
                original_response=text,
                error=e,
                error_message=f"Error parsing response: {str(e)}"
            )
    
    @classmethod
    def parse_json(cls, text: str) -> ResponseParsingResult[Dict[str, Any]]:
        """
        Parse JSON from text.
        
        Args:
            text: Text containing JSON
            
        Returns:
            Parsing result with the parsed JSON if successful
        """
        try:
            # Extract JSON blocks
            json_blocks = cls.extract_json_blocks(text)
            
            if not json_blocks:
                return ResponseParsingResult(
                    original_response=text,
                    error=ParsingError("No JSON found in response"),
                    error_message="Could not find any valid JSON in the response"
                )
            
            # Try each JSON block until one works
            for json_str in json_blocks:
                try:
                    # Parse JSON
                    data = json.loads(json_str)
                    
                    return ResponseParsingResult(
                        original_response=text,
                        parsed_data=data
                    )
                except json.JSONDecodeError:
                    continue
            
            # If we got here, none of the JSON blocks were valid
            return ResponseParsingResult(
                original_response=text,
                error=ParsingError("Found JSON-like content but could not parse it"),
                error_message="JSON parsing failed"
            )
            
        except Exception as e:
            logger.error(f"Error parsing JSON: {e}")
            return ResponseParsingResult(
                original_response=text,
                error=e,
                error_message=f"Error parsing response: {str(e)}"
            )
    
    @staticmethod
    def structure_generation(
        prompt: str,
        output_model: Type[T],
        output_format: OutputFormat = OutputFormat.JSON,
        examples: Optional[List[T]] = None
    ) -> str:
        """
        Generate a structuring prompt to guide the LLM to output in a specific format.
        
        Args:
            prompt: Base prompt for the LLM
            output_model: Pydantic model representing the expected structure
            output_format: Desired output format
            examples: Optional example outputs to demonstrate the format
            
        Returns:
            Modified prompt that guides the LLM to produce structured output
        """
        # Get JSON schema from the model
        schema = output_model.schema()
        
        # Build format instructions
        format_instructions = ""
        if output_format == OutputFormat.JSON:
            format_instructions = (
                f"Return your response as a JSON object with the following structure:\n\n"
                f"{json.dumps(schema, indent=2)}\n\n"
            )
            
            if examples:
                format_instructions += "Here are some examples of valid responses:\n\n"
                for example in examples:
                    format_instructions += f"```json\n{example.json(indent=2)}\n```\n\n"
        
        elif output_format == OutputFormat.MARKDOWN:
            format_instructions = (
                f"Return your response in markdown format, structured according to this schema:\n\n"
                f"```json\n{json.dumps(schema, indent=2)}\n```\n\n"
            )
            
        # Combine with original prompt
        structured_prompt = (
            f"{prompt.strip()}\n\n"
            f"{format_instructions}\n"
            f"Your response must strictly adhere to this format."
        )
        
        return structured_prompt


class StructuredOutputParser:
    """
    Parser for structured output from LLMs based on predefined schemas.
    
    This class helps define expected output structures and parses
    LLM responses accordingly.
    """
    
    def __init__(self, output_model: Type[T]):
        """
        Initialize a structured output parser.
        
        Args:
            output_model: Pydantic model representing the expected structure
        """
        self.output_model = output_model
    
    def parse(self, text: str) -> ResponseParsingResult[T]:
        """
        Parse text into the structured output model.
        
        Args:
            text: Text to parse
            
        Returns:
            Parsing result with the parsed model if successful
        """
        return ResponseParser.parse_json_to_model(text, self.output_model)
    
    def get_format_instructions(self) -> str:
        """
        Get format instructions for the expected output.
        
        Returns:
            Format instructions string
        """
        schema = self.output_model.schema()
        
        instructions = (
            f"You must respond in the following JSON format:\n\n"
            f"```json\n{json.dumps(schema, indent=2)}\n```\n\n"
            f"Ensure your response is valid JSON that matches this schema exactly."
        )
        
        return instructions


# Example models for common structured outputs

class ThoughtProcess(BaseModel):
    """Model for thought process in chain-of-thought reasoning."""
    thoughts: str = Field(..., description="Detailed thought process")
    reasoning: str = Field(..., description="Step-by-step reasoning")
    conclusion: str = Field(..., description="Final conclusion")


class AnalysisResult(BaseModel):
    """Model for analysis results."""
    summary: str = Field(..., description="Brief summary of the analysis")
    key_points: List[str] = Field(..., description="List of key points")
    sentiment: str = Field(..., description="Overall sentiment")
    confidence: float = Field(..., description="Confidence score from 0.0 to 1.0")


class ExtractedEntities(BaseModel):
    """Model for entity extraction."""
    people: List[Dict[str, str]] = Field(default_factory=list, description="People mentioned")
    organizations: List[Dict[str, str]] = Field(default_factory=list, description="Organizations mentioned")
    locations: List[Dict[str, str]] = Field(default_factory=list, description="Locations mentioned")
    dates: List[Dict[str, str]] = Field(default_factory=list, description="Dates mentioned")
    misc: List[Dict[str, str]] = Field(default_factory=list, description="Miscellaneous entities")
