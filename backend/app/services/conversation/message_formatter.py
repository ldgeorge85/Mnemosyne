"""
Message Formatter Service

This module provides services for formatting and transforming messages
in a consistent way, including message content standardization,
metadata extraction, and format conversion.
"""

import re
import json
import html
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class MessageFormatError(Exception):
    """Exception raised for message formatting errors."""
    pass


class MessageFormatter:
    """
    Service for formatting and transforming messages.
    
    This class provides utilities for:
    1. Standardizing message format
    2. Extracting metadata from messages
    3. Converting between different message formats
    """
    
    def __init__(self):
        """Initialize the message formatter."""
        # Maximum allowed content length
        self.max_content_length = 10000
        
        # Regular expressions for pattern matching
        self.url_pattern = re.compile(r'https?://\S+')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.command_pattern = re.compile(r'^/(\w+)(?:\s+(.*))?$')
    
    def format_message_content(self, content: str) -> str:
        """
        Format message content by trimming, normalizing whitespace, etc.
        
        Args:
            content: The message content to format
            
        Returns:
            The formatted message content
            
        Raises:
            MessageFormatError: If content is invalid or too long
        """
        if not content:
            raise MessageFormatError("Message content cannot be empty")
        
        # Trim whitespace
        formatted = content.strip()
        
        # Check length
        if len(formatted) > self.max_content_length:
            raise MessageFormatError(f"Message content exceeds maximum length of {self.max_content_length} characters")
        
        # Normalize line endings
        formatted = formatted.replace('\r\n', '\n').replace('\r', '\n')
        
        # Optional: HTML-escape content for safety
        # formatted = html.escape(formatted)
        
        return formatted
    
    def extract_urls(self, content: str) -> List[str]:
        """
        Extract URLs from message content.
        
        Args:
            content: The message content to extract from
            
        Returns:
            List of extracted URLs
        """
        return self.url_pattern.findall(content)
    
    def extract_emails(self, content: str) -> List[str]:
        """
        Extract email addresses from message content.
        
        Args:
            content: The message content to extract from
            
        Returns:
            List of extracted email addresses
        """
        return self.email_pattern.findall(content)
    
    def parse_command(self, content: str) -> Optional[Tuple[str, str]]:
        """
        Parse a command from message content.
        
        Args:
            content: The message content to parse
            
        Returns:
            Tuple of (command, arguments) or None if not a command
        """
        match = self.command_pattern.match(content.strip())
        if match:
            command = match.group(1)
            args = match.group(2) or ""
            return command, args
        return None
    
    def to_dict(self, message: Any) -> Dict[str, Any]:
        """
        Convert a message object to a dictionary.
        
        Args:
            message: The message object to convert
            
        Returns:
            Dictionary representation of the message
        """
        if hasattr(message, 'to_dict') and callable(message.to_dict):
            return message.to_dict()
        elif hasattr(message, '__dict__'):
            result = message.__dict__.copy()
            # Convert datetime objects to ISO format
            for key, value in result.items():
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
            return result
        else:
            raise MessageFormatError("Cannot convert message to dictionary")
    
    def from_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize a message dictionary.
        
        Args:
            data: The message data to standardize
            
        Returns:
            Standardized message dictionary
        """
        standardized = data.copy()
        
        # Ensure required fields
        if "content" in standardized:
            standardized["content"] = self.format_message_content(standardized["content"])
        
        # Ensure role is lowercase
        if "role" in standardized:
            standardized["role"] = standardized["role"].lower()
        
        return standardized
    
    def to_json(self, message: Any) -> str:
        """
        Convert a message to JSON.
        
        Args:
            message: The message to convert
            
        Returns:
            JSON string representation of the message
        """
        try:
            message_dict = self.to_dict(message)
            return json.dumps(message_dict)
        except Exception as e:
            raise MessageFormatError(f"Failed to convert message to JSON: {str(e)}")
    
    def from_json(self, json_str: str) -> Dict[str, Any]:
        """
        Parse a message from JSON.
        
        Args:
            json_str: The JSON string to parse
            
        Returns:
            Parsed message dictionary
            
        Raises:
            MessageFormatError: If JSON is invalid
        """
        try:
            data = json.loads(json_str)
            return self.from_dict(data)
        except json.JSONDecodeError as e:
            raise MessageFormatError(f"Invalid JSON: {str(e)}")
    
    def format_system_message(self, content: str) -> Dict[str, Any]:
        """
        Create a formatted system message.
        
        Args:
            content: The message content
            
        Returns:
            Formatted system message dictionary
        """
        return {
            "content": self.format_message_content(content),
            "role": "system",
            "metadata": {
                "formatted_at": datetime.utcnow().isoformat()
            }
        }
    
    def format_user_message(self, content: str, user_id: str) -> Dict[str, Any]:
        """
        Create a formatted user message.
        
        Args:
            content: The message content
            user_id: The ID of the user
            
        Returns:
            Formatted user message dictionary
        """
        formatted_content = self.format_message_content(content)
        
        # Extract metadata
        urls = self.extract_urls(formatted_content)
        emails = self.extract_emails(formatted_content)
        command = self.parse_command(formatted_content)
        
        return {
            "content": formatted_content,
            "role": "user",
            "user_id": user_id,
            "metadata": {
                "urls": urls,
                "emails": emails,
                "is_command": command is not None,
                "command": command[0] if command else None,
                "command_args": command[1] if command else None,
                "formatted_at": datetime.utcnow().isoformat()
            }
        }
    
    def format_assistant_message(self, content: str) -> Dict[str, Any]:
        """
        Create a formatted assistant message.
        
        Args:
            content: The message content
            
        Returns:
            Formatted assistant message dictionary
        """
        return {
            "content": self.format_message_content(content),
            "role": "assistant",
            "metadata": {
                "formatted_at": datetime.utcnow().isoformat()
            }
        }
