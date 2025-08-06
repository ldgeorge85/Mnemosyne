"""
Vector Store Package

This package provides interfaces for storing and retrieving vector embeddings,
with implementations for various backends including PostgreSQL with pgvector.
"""
from app.services.vector_store.pgvector_store import PGVectorStore, MemoryVectorStore

__all__ = [
    "PGVectorStore",
    "MemoryVectorStore",
]
