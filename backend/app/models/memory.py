"""
Memory model alias module.

This module provides aliases for memory models from app.db.models.memory
to maintain backward compatibility with existing code.
"""

from app.db.models.memory import Memory, MemoryChunk

# Re-export the models
__all__ = ['Memory', 'MemoryChunk']
