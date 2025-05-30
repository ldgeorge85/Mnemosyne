"""
Common Utilities

This module contains common utility functions that are used throughout the application.
"""

import hashlib
import json
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar, Union

T = TypeVar('T')


def generate_uuid() -> str:
    """
    Generate a random UUID string.
    
    Returns:
        str: A new UUID as a string
    """
    return str(uuid.uuid4())


def slugify(text: str) -> str:
    """
    Convert a string to a URL-friendly slug.
    
    Args:
        text: The text to convert
        
    Returns:
        A URL-friendly slug version of the text
    """
    # Convert to lowercase
    slug = text.lower()
    
    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)
    
    # Remove special characters
    slug = re.sub(r'[^a-z0-9\-]', '', slug)
    
    # Remove multiple consecutive hyphens
    slug = re.sub(r'\-+', '-', slug)
    
    # Remove leading and trailing hyphens
    slug = slug.strip('-')
    
    return slug


def utc_now() -> datetime:
    """
    Get the current UTC datetime.
    
    Returns:
        The current UTC datetime
    """
    return datetime.utcnow()


def compute_hash(data: Union[str, bytes, Dict[str, Any], List[Any]]) -> str:
    """
    Compute a SHA-256 hash of the input data.
    
    Args:
        data: The data to hash, can be a string, bytes, dict, or list
        
    Returns:
        The hexadecimal hash string
    """
    if isinstance(data, (dict, list)):
        # Convert to a consistent string representation
        data = json.dumps(data, sort_keys=True)
    
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    return hashlib.sha256(data).hexdigest()


def safe_get(obj: Any, path: str, default: Optional[T] = None) -> Union[Any, T]:
    """
    Safely access a nested attribute in an object using dot notation.
    
    Args:
        obj: The object to access
        path: The path to the attribute using dot notation (e.g., "user.address.city")
        default: The default value to return if the path doesn't exist
        
    Returns:
        The value at the path or the default value if not found
    """
    parts = path.split('.')
    current = obj
    
    try:
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                current = getattr(current, part)
                
            if current is None:
                return default
        return current
    except (AttributeError, KeyError, TypeError):
        return default


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length, adding a suffix if truncated.
    
    Args:
        text: The text to truncate
        max_length: The maximum length
        suffix: The suffix to add if truncated
        
    Returns:
        The truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
