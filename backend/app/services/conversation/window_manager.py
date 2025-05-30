"""
Conversation Window Manager

This module provides services for managing conversation context windows,
including determining what messages to include in a context window based on
token limits, relevance, and conversation flow.
"""

from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime, timedelta

from app.db.models.conversation import Message


class WindowType:
    """Enum-like class defining window selection strategies"""
    RECENT = "recent"
    RELEVANT = "relevant"
    HYBRID = "hybrid"


class ConversationWindowManager:
    """
    Service for managing conversation context windows.
    
    This class handles:
    1. Determining which messages to include in a context window
    2. Managing window size based on token limits
    3. Selecting messages based on relevance and recency
    """
    
    def __init__(self):
        """Initialize the window manager."""
        # Default maximum tokens in a context window
        self.default_max_tokens = 4000
        
        # Average tokens per character (estimation)
        self.avg_tokens_per_char = 0.25
        
        # Default minimum system messages to include
        self.min_system_messages = 1
        
        # Default window selection strategy
        self.default_window_type = WindowType.HYBRID
        
        # Default relevance threshold (0-1)
        self.relevance_threshold = 0.7
    
    def get_context_window(
        self,
        messages: List[Message],
        max_tokens: Optional[int] = None,
        window_type: Optional[str] = None
    ) -> List[Message]:
        """
        Get the messages to include in the context window.
        
        Args:
            messages: List of all messages in the conversation (chronological order)
            max_tokens: Maximum tokens to include (default: self.default_max_tokens)
            window_type: Strategy for selecting messages (default: self.default_window_type)
            
        Returns:
            List of messages to include in the context window
        """
        if not messages:
            return []
        
        # Use defaults if not specified
        max_tokens = max_tokens or self.default_max_tokens
        window_type = window_type or self.default_window_type
        
        # Select messages based on window type
        if window_type == WindowType.RECENT:
            return self._get_recent_window(messages, max_tokens)
        elif window_type == WindowType.RELEVANT:
            return self._get_relevant_window(messages, max_tokens)
        elif window_type == WindowType.HYBRID:
            return self._get_hybrid_window(messages, max_tokens)
        else:
            # Default to recent if unknown window type
            return self._get_recent_window(messages, max_tokens)
    
    def _get_recent_window(self, messages: List[Message], max_tokens: int) -> List[Message]:
        """
        Get the most recent messages that fit in the token limit.
        
        Args:
            messages: List of all messages (chronological order)
            max_tokens: Maximum tokens to include
            
        Returns:
            List of recent messages that fit in the token limit
        """
        # Ensure we always include system messages if possible
        system_messages = [msg for msg in messages if msg.role == "system"]
        selected_system_messages = system_messages[:self.min_system_messages]
        
        # Calculate tokens used by system messages
        system_tokens = sum(self._estimate_tokens(msg.content) for msg in selected_system_messages)
        remaining_tokens = max_tokens - system_tokens
        
        # Get non-system messages in reverse order (newest first)
        non_system_messages = [msg for msg in reversed(messages) if msg.role != "system"]
        
        # Select messages that fit in the remaining token limit
        selected_non_system = []
        for msg in non_system_messages:
            msg_tokens = self._estimate_tokens(msg.content)
            if remaining_tokens - msg_tokens >= 0:
                selected_non_system.insert(0, msg)  # Insert at beginning to restore chronological order
                remaining_tokens -= msg_tokens
            else:
                break
        
        # Combine system messages and selected non-system messages
        return selected_system_messages + selected_non_system
    
    def _get_relevant_window(self, messages: List[Message], max_tokens: int) -> List[Message]:
        """
        Get the most relevant messages that fit in the token limit.
        
        This method is a placeholder - in a real implementation, it would use
        embeddings or another method to calculate message relevance to the
        current conversation context.
        
        Args:
            messages: List of all messages (chronological order)
            max_tokens: Maximum tokens to include
            
        Returns:
            List of relevant messages that fit in the token limit
        """
        # In a real implementation, this would calculate relevance scores
        # For now, we'll use recency as a proxy for relevance
        return self._get_recent_window(messages, max_tokens)
    
    def _get_hybrid_window(self, messages: List[Message], max_tokens: int) -> List[Message]:
        """
        Get a mix of recent and relevant messages that fit in the token limit.
        
        Args:
            messages: List of all messages (chronological order)
            max_tokens: Maximum tokens to include
            
        Returns:
            List of messages that fit in the token limit
        """
        # For now, this is the same as recent since we don't have a real relevance implementation
        # In a real implementation, this would balance recent and relevant messages
        return self._get_recent_window(messages, max_tokens)
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in a text.
        
        Args:
            text: The text to estimate tokens for
            
        Returns:
            Estimated number of tokens
        """
        return int(len(text) * self.avg_tokens_per_char)
    
    def calculate_window_stats(self, messages: List[Message]) -> Dict[str, Any]:
        """
        Calculate statistics for a context window.
        
        Args:
            messages: List of messages in the window
            
        Returns:
            Dictionary of statistics
        """
        if not messages:
            return {
                "message_count": 0,
                "token_count": 0,
                "user_messages": 0,
                "assistant_messages": 0,
                "system_messages": 0,
                "oldest_message": None,
                "newest_message": None,
                "time_span_seconds": 0
            }
        
        # Count messages by role
        user_messages = sum(1 for msg in messages if msg.role == "user")
        assistant_messages = sum(1 for msg in messages if msg.role == "assistant")
        system_messages = sum(1 for msg in messages if msg.role == "system")
        
        # Estimate token count
        token_count = sum(self._estimate_tokens(msg.content) for msg in messages)
        
        # Get time span
        timestamps = [msg.created_at for msg in messages]
        oldest = min(timestamps) if timestamps else None
        newest = max(timestamps) if timestamps else None
        
        time_span = (newest - oldest).total_seconds() if oldest and newest else 0
        
        return {
            "message_count": len(messages),
            "token_count": token_count,
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "system_messages": system_messages,
            "oldest_message": oldest.isoformat() if oldest else None,
            "newest_message": newest.isoformat() if newest else None,
            "time_span_seconds": time_span
        }
    
    def adjust_window_size(
        self, 
        messages: List[Message], 
        max_tokens: int, 
        min_turns: int = 3
    ) -> Tuple[List[Message], int]:
        """
        Adjust the window size to ensure minimum conversation turns.
        
        Args:
            messages: List of all messages (chronological order)
            max_tokens: Maximum tokens to include
            min_turns: Minimum number of conversation turns to include
            
        Returns:
            Tuple of (adjusted message list, actual token count)
        """
        # Get initial window
        window = self._get_recent_window(messages, max_tokens)
        
        # Count conversation turns (user + assistant exchange)
        turns = min(
            sum(1 for msg in window if msg.role == "user"),
            sum(1 for msg in window if msg.role == "assistant")
        )
        
        # If we have enough turns, return the window
        if turns >= min_turns:
            token_count = sum(self._estimate_tokens(msg.content) for msg in window)
            return window, token_count
        
        # Otherwise, adjust token limit to include more messages
        # For simplicity, we'll just use a higher token limit
        adjusted_max_tokens = max_tokens * 1.5
        
        # Try again with adjusted token limit
        adjusted_window = self._get_recent_window(messages, int(adjusted_max_tokens))
        actual_tokens = sum(self._estimate_tokens(msg.content) for msg in adjusted_window)
        
        return adjusted_window, actual_tokens
