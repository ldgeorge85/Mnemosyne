"""
Memory system package for the Shadow AI platform.

This package provides memory storage capabilities for the Shadow system, 
including vector storage, document storage, and relational storage.
"""

from memory.memory_base import MemoryItem, MemorySystem, SearchableMemorySystem, VectorMemorySystem
from memory.memory_manager import MemoryManager, default_memory_manager
from memory.vector_memory import InMemoryVectorStore, EmbeddingService
from memory.document_store import DocumentItem, InMemoryDocumentStore, FileSystemDocumentStore
from memory.relational_store import RelationalItem, InMemoryRelationalStore, SQLiteRelationalStore

__all__ = [
    # Base classes
    'MemoryItem', 'MemorySystem', 'SearchableMemorySystem', 'VectorMemorySystem',
    
    # Memory manager
    'MemoryManager', 'default_memory_manager',
    
    # Vector store
    'InMemoryVectorStore', 'EmbeddingService',
    
    # Document store
    'DocumentItem', 'InMemoryDocumentStore', 'FileSystemDocumentStore',
    
    # Relational store
    'RelationalItem', 'InMemoryRelationalStore', 'SQLiteRelationalStore',
]
