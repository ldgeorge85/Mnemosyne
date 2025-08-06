"""
Storage backends for the knowledge platform.

AI Agents: Available storage:
- VectorStore: Qdrant-based vector storage for semantic search
- (Future) StructuredStore: PostgreSQL for metadata

Example:
    from storage import VectorStore
    
    store = VectorStore()
    await store.initialize()
    await store.add_documents(docs, collection="outline_docs")
"""

from .vectors import VectorStore

__all__ = ["VectorStore"]