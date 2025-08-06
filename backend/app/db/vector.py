"""
Vector Database Integration

This module provides functionality for working with vector embeddings using pgvector.
It includes utilities for creating and querying vector embeddings.
"""

import json
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Union

import numpy as np
from sqlalchemy import Column, Float, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import func

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar('T')

# Vector dimension from settings
VECTOR_DIMENSIONS = settings.VECTOR_DIMENSIONS

# Create a special column type for vectors
vector_type = ARRAY(Float, dimensions=1)


class VectorMixin:
    """
    Mixin for models that include vector embeddings.
    Provides common fields and methods for vector operations.
    """
    
    # Vector embedding (from pgvector)
    embedding = Column(vector_type, nullable=True)
    
    # Original text content that was embedded
    content = Column(Text, nullable=False)
    
    # Metadata about the embedding (model, parameters, etc.)
    embedding_metadata = Column(JSONB, nullable=True)


async def ensure_extension(session: AsyncSession) -> bool:
    """
    Ensure the pgvector extension is installed in the database.
    
    Args:
        session: The database session
        
    Returns:
        True if the extension is installed, False otherwise
    """
    try:
        # Check if pgvector extension is installed
        query = text("SELECT * FROM pg_extension WHERE extname = 'vector'")
        result = await session.execute(query)
        extension_exists = result.first() is not None
        
        if not extension_exists:
            # Try to create the extension
            logger.info("Creating pgvector extension")
            await session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            await session.commit()
            return True
        
        return extension_exists
    except Exception as e:
        logger.error(f"Error ensuring pgvector extension: {str(e)}")
        await session.rollback()
        return False


async def create_vector_index(
    session: AsyncSession,
    table_name: str,
    column_name: str = "embedding",
    index_type: str = "hnsw",
    metric: str = "cosine",
) -> bool:
    """
    Create a vector index on a table column.
    
    Args:
        session: The database session
        table_name: The name of the table
        column_name: The name of the column
        index_type: The type of index (ivfflat or hnsw)
        metric: The distance metric (cosine, l2, or ip)
        
    Returns:
        True if the index was created, False otherwise
    """
    try:
        # Generate a consistent index name
        index_name = f"{table_name}_{column_name}_{index_type}_idx"
        
        # Check if index already exists
        query = text(f"""
            SELECT 1 FROM pg_indexes 
            WHERE indexname = '{index_name}'
        """)
        result = await session.execute(query)
        if result.first() is not None:
            logger.info(f"Index {index_name} already exists")
            return True
        
        # Create the appropriate index based on type
        if index_type.lower() == "hnsw":
            # HNSW index with default parameters
            query = text(f"""
                CREATE INDEX {index_name} ON {table_name} 
                USING hnsw({column_name} {metric}_ops)
                WITH (m=16, ef_construction=64)
            """)
        elif index_type.lower() == "ivfflat":
            # IVFFlat index with default parameters
            query = text(f"""
                CREATE INDEX {index_name} ON {table_name} 
                USING ivfflat({column_name} {metric}_ops)
                WITH (lists=100)
            """)
        else:
            logger.error(f"Unsupported index type: {index_type}")
            return False
        
        logger.info(f"Creating {index_type} index on {table_name}.{column_name}")
        await session.execute(query)
        await session.commit()
        return True
    except Exception as e:
        logger.error(f"Error creating vector index: {str(e)}")
        await session.rollback()
        return False


def vector_to_list(vector: np.ndarray) -> List[float]:
    """
    Convert a numpy array to a list of floats.
    
    Args:
        vector: The numpy array
        
    Returns:
        A list of floats
    """
    return vector.tolist()


def list_to_vector(vector_list: List[float]) -> np.ndarray:
    """
    Convert a list of floats to a numpy array.
    
    Args:
        vector_list: The list of floats
        
    Returns:
        A numpy array
    """
    return np.array(vector_list, dtype=np.float32)


async def similarity_search(
    session: AsyncSession,
    model_class: Any,
    query_vector: Union[List[float], np.ndarray],
    filter_condition: Optional[Any] = None,
    limit: int = 10,
    column_name: str = "embedding",
    metric: str = "cosine",
) -> List[Tuple[Any, float]]:
    """
    Perform a similarity search using vector embeddings.
    
    Args:
        session: The database session
        model_class: The SQLAlchemy model class
        query_vector: The query vector
        filter_condition: Optional filter condition
        limit: Maximum number of results
        column_name: The name of the embedding column
        metric: The distance metric (cosine, l2, or ip)
        
    Returns:
        A list of tuples containing the model instance and similarity score
    """
    # Convert query vector to list if it's a numpy array
    if isinstance(query_vector, np.ndarray):
        query_vector = vector_to_list(query_vector)
    
    # Build the query
    embedding_col = getattr(model_class, column_name)
    
    if metric == "cosine":
        # For cosine similarity, 1 is most similar, -1 is least similar
        # The <=> operator is the cosine distance operator from pgvector
        distance_expr = embedding_col.op("<=>")(query_vector)
    elif metric == "l2":
        # For L2 distance, smaller is more similar
        # The <-> operator is the L2 distance operator from pgvector
        distance_expr = embedding_col.op("<->")(query_vector)
    elif metric == "ip":
        # For inner product, larger is more similar
        # The <#> operator is the negative inner product operator from pgvector
        # We negate it to get the inner product (larger is more similar)
        distance_expr = -embedding_col.op("<#>")(query_vector)
    else:
        raise ValueError(f"Unsupported metric: {metric}")
    
    # Create the query
    query = (
        select(model_class, distance_expr.label("similarity"))
        .order_by(distance_expr)
        .limit(limit)
    )
    
    # Add filter if provided
    if filter_condition is not None:
        query = query.filter(filter_condition)
    
    # Execute the query
    result = await session.execute(query)
    
    # Return the results with similarity scores
    return [(row[0], row[1]) for row in result.all()]
