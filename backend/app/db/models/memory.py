"""
Memory data models for the Mnemosyne application.

This module defines the SQLAlchemy ORM models for storing and 
retrieving memory data, including vector embeddings.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Text,
    Boolean,
    JSON,
    Index
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from app.db.base_model import BaseModel


class Memory(BaseModel):
    """
    Memory model for storing user memories with vector embeddings.
    
    This model represents a memory entry in the system, which includes
    text content, metadata, and vector embeddings for similarity search.
    """
    __tablename__ = "memories"
    
    # Core memory fields
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    
    # Embedding data
    embedding = Column(ARRAY(Float), nullable=True)  # Legacy, kept for compatibility
    embedding_vector = Column(Vector(1024), nullable=True)  # pgvector column
    embedding_dimension = Column(Integer, nullable=True)
    embedding_model = Column(String(100), nullable=True)
    
    # Metadata
    source = Column(String(100), nullable=True)
    source_type = Column(String(50), nullable=True)  # conversation, document, task, etc.
    source_id = Column(UUID(as_uuid=True), nullable=True)  # ID of the source if applicable
    memory_metadata = Column(JSON, nullable=True)  # Additional metadata as JSON
    
    # Memory management
    importance = Column(Float, default=0.5)  # 0.0 to 1.0
    last_accessed_at = Column(DateTime, nullable=True)
    access_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Tags for categorization
    tags = Column(ARRAY(String), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="memories")
    chunks = relationship("MemoryChunk", back_populates="memory", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index("ix_memories_user_id", "user_id"),
        Index("ix_memories_source_id", "source_id"),
        Index("ix_memories_is_active", "is_active"),
        # Additional indexes will be added for pgvector
    )
    
    def __repr__(self) -> str:
        return f"<Memory {self.id}: {self.title}>"


class MemoryChunk(BaseModel):
    """
    Memory chunk model for storing segmented parts of memories.
    
    Long memories are split into chunks for better processing and retrieval.
    Each chunk has its own embedding for more precise similarity search.
    """
    __tablename__ = "memory_chunks"
    
    memory_id = Column(UUID(as_uuid=True), ForeignKey("memories.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Position in the original text
    content = Column(Text, nullable=False)
    
    # Embedding data
    embedding = Column(ARRAY(Float), nullable=True)  # Legacy, kept for compatibility
    embedding_vector = Column(Vector(1024), nullable=True)  # pgvector column
    embedding_dimension = Column(Integer, nullable=True)
    embedding_model = Column(String(100), nullable=True)
    
    # Metadata
    token_count = Column(Integer, nullable=True)
    chunk_metadata = Column(JSON, nullable=True)  # Additional metadata as JSON
    
    # Relationships
    memory = relationship("Memory", back_populates="chunks")
    
    # Indexes for performance
    __table_args__ = (
        Index("ix_memory_chunks_memory_id", "memory_id"),
        Index("ix_memory_chunks_memory_id_chunk_index", "memory_id", "chunk_index"),
        # Additional indexes will be added for pgvector
    )
    
    def __repr__(self) -> str:
        return f"<MemoryChunk {self.id}: {self.memory_id} #{self.chunk_index}>"
