"""
Memory schemas for request/response validation and serialization.

This module defines Pydantic models for memory-related data structures
used in API requests and responses.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator, field_validator, ConfigDict


class MemoryChunkBase(BaseModel):
    """Base schema for memory chunk data."""
    content: str = Field(..., description="The text content of this chunk")
    chunk_index: int = Field(..., description="Position in the original memory")
    token_count: Optional[int] = Field(None, description="Number of tokens in this chunk")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class MemoryChunkCreate(MemoryChunkBase):
    """Schema for creating a new memory chunk."""
    memory_id: str = Field(..., description="ID of the parent memory")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding of content")
    embedding_model: Optional[str] = Field(None, description="Name of the embedding model used")


class MemoryChunkUpdate(BaseModel):
    """Schema for updating an existing memory chunk."""
    content: Optional[str] = Field(None, description="The text content of this chunk")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding of content")
    embedding_model: Optional[str] = Field(None, description="Name of the embedding model used")
    token_count: Optional[int] = Field(None, description="Number of tokens in this chunk")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class MemoryChunkResponse(MemoryChunkBase):
    """Schema for responding with memory chunk data."""
    id: str = Field(..., description="Unique ID of the memory chunk")
    memory_id: str = Field(..., description="ID of the parent memory")
    created_at: datetime = Field(..., description="Time when the chunk was created")
    updated_at: datetime = Field(..., description="Time when the chunk was last updated")
    embedding_model: Optional[str] = Field(None, description="Name of the embedding model used")
    
    # Don't include the actual embedding in responses to save bandwidth
    has_embedding: bool = Field(False, description="Whether this chunk has an embedding")
    
    class Config:
        from_attributes = True
        
    @validator("id", "memory_id", pre=True)
    def convert_uuid_to_string(cls, v):
        """Convert UUID objects to strings."""
        if v is None:
            return v
        return str(v)
        
    @validator("has_embedding", pre=True, always=True)
    def set_has_embedding(cls, v, values):
        """Set has_embedding based on whether the embedding exists in the data."""
        # This special validator sets has_embedding based on the embedding field
        # which isn't actually returned in the response
        return "embedding" in values and values["embedding"] is not None


class MemoryBase(BaseModel):
    """Base schema for memory data."""
    title: str = Field(..., description="Title of the memory")
    content: str = Field(..., description="Text content of the memory")
    source: Optional[str] = Field(None, description="Source of the memory")
    source_type: Optional[str] = Field(None, description="Type of source (conversation, document, etc.)")
    source_id: Optional[str] = Field(None, description="ID of the source if applicable")
    tags: Optional[List[str]] = Field(None, description="Tags for categorizing the memory")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    importance: Optional[float] = Field(0.5, description="Importance score from 0.0 to 1.0")


class MemoryCreate(MemoryBase):
    """Schema for creating a new memory."""
    user_id: str = Field(..., description="ID of the user who owns this memory")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding of content")
    embedding_model: Optional[str] = Field(None, description="Name of the embedding model used")


class MemoryUpdate(BaseModel):
    """Schema for updating an existing memory."""
    title: Optional[str] = Field(None, description="Title of the memory")
    content: Optional[str] = Field(None, description="Text content of the memory")
    tags: Optional[List[str]] = Field(None, description="Tags for categorizing the memory")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    importance: Optional[float] = Field(None, description="Importance score from 0.0 to 1.0")
    is_active: Optional[bool] = Field(None, description="Whether this memory is active")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding of content")
    embedding_model: Optional[str] = Field(None, description="Name of the embedding model used")


class MemoryResponse(MemoryBase):
    """Schema for responding with memory data."""
    id: str = Field(..., description="Unique ID of the memory")
    user_id: str = Field(..., description="ID of the user who owns this memory")
    created_at: datetime = Field(..., description="Time when the memory was created")
    updated_at: datetime = Field(..., description="Time when the memory was last updated")
    last_accessed_at: Optional[datetime] = Field(None, description="Time when the memory was last accessed")
    access_count: int = Field(0, description="Number of times this memory has been accessed")
    is_active: bool = Field(True, description="Whether this memory is active")
    embedding_model: Optional[str] = Field(None, description="Name of the embedding model used")
    
    # Don't include the actual embedding in responses to save bandwidth
    has_embedding: bool = Field(False, description="Whether this memory has an embedding")
    
    class Config:
        from_attributes = True
        populate_by_name = True  # Allow field population by alias
        
    @validator("id", "user_id", "source_id", pre=True)
    def convert_uuid_to_string(cls, v):
        """Convert UUID objects to strings."""
        if v is None:
            return v
        return str(v)
    
    @validator("metadata", pre=True)
    def handle_metadata_field(cls, v, values):
        """Handle metadata field which might be memory_metadata in DB."""
        # If metadata is None but memory_metadata exists, use that
        if v is None and "memory_metadata" in values:
            return values["memory_metadata"]
        # If v is a SQLAlchemy MetaData object, return None
        if v is not None and not isinstance(v, dict):
            return None
        return v
        
    @validator("has_embedding", pre=True, always=True)
    def set_has_embedding(cls, v, values):
        """Set has_embedding based on whether the embedding exists in the data."""
        # This special validator sets has_embedding based on the embedding field
        # which isn't actually returned in the response
        return "embedding" in values and values["embedding"] is not None


class MemoryWithChunksResponse(MemoryResponse):
    """Schema for responding with memory data including its chunks."""
    chunks: List[MemoryChunkResponse] = Field([], description="Chunks of this memory")


class MemorySearchQuery(BaseModel):
    """Schema for memory search queries."""
    query: str = Field(..., description="Search query text")
    user_id: str = Field(..., description="ID of the user whose memories to search")
    limit: Optional[int] = Field(20, description="Maximum number of results to return")
    include_chunks: Optional[bool] = Field(False, description="Whether to include chunks in the response")
    include_inactive: Optional[bool] = Field(False, description="Whether to include inactive memories")
    
    @validator("limit")
    def validate_limit(cls, v):
        """Validate that limit is within a reasonable range."""
        if v < 1:
            return 1
        if v > 100:
            return 100
        return v


class MemorySearchResponse(BaseModel):
    """Schema for memory search responses."""
    query: str = Field(..., description="Original search query")
    results: List[Union[MemoryResponse, MemoryWithChunksResponse]] = Field(
        [], description="Search results"
    )
    total: int = Field(0, description="Total number of matching results")


class MemoryStatistics(BaseModel):
    """Schema for memory system statistics."""
    total_memories: int = Field(0, description="Total number of memories")
    total_chunks: int = Field(0, description="Total number of memory chunks")
    active_memories: int = Field(0, description="Number of active memories")
    inactive_memories: int = Field(0, description="Number of inactive memories")
    avg_importance: float = Field(0.0, description="Average importance score")
    avg_chunks_per_memory: float = Field(0.0, description="Average chunks per memory")
    memories_by_source_type: Dict[str, int] = Field({}, description="Count of memories by source type")
    memories_by_tag: Dict[str, int] = Field({}, description="Count of memories by tag")
