"""
PGVector Storage Interface

This module provides an interface for storing and retrieving vector embeddings
using PostgreSQL with the pgvector extension, implementing efficient vector
operations and similarity search capabilities.
"""
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union, TypeVar, Generic
from sqlalchemy import text, func, Column, Float, cast
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.core.config import settings


# Set up module logger
logger = logging.getLogger(__name__)

# Type variables
T = TypeVar('T')  # Generic type for the item being stored


class PGVectorStore(Generic[T]):
    """
    PostgreSQL vector store for embeddings using pgvector extension.
    
    This class provides an interface for storing and retrieving vector embeddings
    using PostgreSQL with the pgvector extension, implementing efficient vector
    operations and similarity search.
    """
    
    def __init__(
        self,
        table_name: str,
        id_column: str,
        embedding_column: str,
        dimension: int = 1536,  # Default for OpenAI ada-002 embeddings
        distance_strategy: str = "cosine"  # Options: cosine, l2, inner_product
    ):
        """
        Initialize a PGVector store.
        
        Args:
            table_name: Name of the database table to use
            id_column: Name of the ID column in the table
            embedding_column: Name of the embedding column in the table
            dimension: Dimension of the embedding vectors
            distance_strategy: Distance strategy to use for similarity search
        """
        self.table_name = table_name
        self.id_column = id_column
        self.embedding_column = embedding_column
        self.dimension = dimension
        self.distance_strategy = distance_strategy
    
    async def initialize(self, db: AsyncSession) -> bool:
        """
        Initialize the vector store, ensuring pgvector extension is installed and indexes are created.
        
        Args:
            db: Database session
            
        Returns:
            True if initialization was successful
        """
        try:
            # Check if pgvector extension is installed
            query = text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')")
            result = await db.execute(query)
            extension_exists = result.scalar_one()
            
            if not extension_exists:
                # Create pgvector extension
                await db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                await db.commit()
                logger.info("Created pgvector extension")
            
            # Create index based on distance strategy
            index_name = f"idx_{self.table_name}_{self.embedding_column}"
            
            if self.distance_strategy == "cosine":
                index_method = "vector_cosine_ops"
            elif self.distance_strategy == "l2":
                index_method = "vector_l2_ops"
            elif self.distance_strategy == "inner_product":
                index_method = "vector_ip_ops"
            else:
                raise ValueError(f"Unsupported distance strategy: {self.distance_strategy}")
                
            # Create index query
            await db.execute(text(
                f"CREATE INDEX IF NOT EXISTS {index_name} ON {self.table_name} "
                f"USING ivfflat ({self.embedding_column} {index_method}) "
                f"WITH (lists = 100)"
            ))
            await db.commit()
            
            logger.info(f"Initialized PGVector store for table {self.table_name}")
            return True
        except Exception as e:
            logger.error(f"Error initializing PGVector store: {e}")
            await db.rollback()
            return False
    
    def _get_distance_function(self) -> Any:
        """
        Get the appropriate distance function based on the strategy.
        
        Returns:
            SQLAlchemy function call for the distance calculation
        """
        embedding_col = text(f"{self.embedding_column}::vector")
        
        if self.distance_strategy == "cosine":
            # cosine distance = 1 - cosine similarity
            # Lower values are more similar (closer to 0)
            return lambda query_vector: func.cosine_distance(embedding_col, query_vector)
        elif self.distance_strategy == "l2":
            # Euclidean distance
            # Lower values are more similar (closer to 0)
            return lambda query_vector: func.l2_distance(embedding_col, query_vector)
        elif self.distance_strategy == "inner_product":
            # Inner product (dot product)
            # Higher values are more similar, so we negate for consistent ordering
            return lambda query_vector: -func.inner_product(embedding_col, query_vector)
        else:
            raise ValueError(f"Unsupported distance strategy: {self.distance_strategy}")
    
    async def similarity_search(
        self,
        query_embedding: List[float],
        db: AsyncSession,
        filter_criteria: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Tuple[Any, float]]:
        """
        Perform a similarity search using the query embedding.
        
        Args:
            query_embedding: The embedding vector to search with
            db: Database session
            filter_criteria: Optional criteria to filter results
            limit: Maximum number of results to return
            offset: Offset for pagination
            
        Returns:
            List of tuples containing the item and its similarity score
        """
        try:
            # Convert the query embedding to the appropriate format
            query_vector = cast(query_embedding, ARRAY(Float))
            
            # Get the distance function
            distance_func = self._get_distance_function()
            
            # Build the base query
            query = (
                select(text(f"*, {distance_func(query_vector)} as distance"))
                .select_from(text(self.table_name))
                .order_by(text("distance"))  # Sort by distance (ascending)
                .limit(limit)
                .offset(offset)
            )
            
            # Add filter criteria if provided
            if filter_criteria:
                conditions = []
                for field, value in filter_criteria.items():
                    conditions.append(f"{field} = :{field}")
                
                if conditions:
                    where_clause = " AND ".join(conditions)
                    query = query.where(text(where_clause))
                    
            # Execute the query
            result = await db.execute(query, filter_criteria or {})
            rows = result.all()
            
            # Convert to list of tuples (item, distance)
            results = [(dict(row), float(row.distance)) for row in rows]
            
            return results
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []
    
    async def batch_add_embeddings(
        self,
        items: List[Dict[str, Any]],
        embeddings: List[List[float]],
        db: AsyncSession,
        extra_fields: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Add multiple embeddings to the vector store.
        
        Args:
            items: List of items to store
            embeddings: List of embedding vectors
            db: Database session
            extra_fields: Optional extra fields to include in the stored items
            
        Returns:
            List of IDs of the stored items
        """
        try:
            if len(items) != len(embeddings):
                raise ValueError("Number of items and embeddings must match")
                
            ids = []
            for i, (item, embedding) in enumerate(zip(items, embeddings)):
                # Prepare item data
                item_data = {**item}
                if extra_fields:
                    item_data.update(extra_fields)
                
                # Add embedding
                item_data[self.embedding_column] = embedding
                
                # Generate columns and values for INSERT
                columns = ", ".join(item_data.keys())
                placeholders = ", ".join(f":{key}" for key in item_data.keys())
                
                # Create insert query
                query = text(
                    f"INSERT INTO {self.table_name} ({columns}) "
                    f"VALUES ({placeholders}) "
                    f"RETURNING {self.id_column}"
                )
                
                # Execute query
                result = await db.execute(query, item_data)
                item_id = result.scalar_one()
                ids.append(item_id)
            
            # Commit transaction
            await db.commit()
            
            return ids
        except Exception as e:
            logger.error(f"Error in batch_add_embeddings: {e}")
            await db.rollback()
            return []
    
    async def delete_embeddings(
        self,
        ids: List[str],
        db: AsyncSession
    ) -> int:
        """
        Delete embeddings from the vector store.
        
        Args:
            ids: List of IDs to delete
            db: Database session
            
        Returns:
            Number of deleted embeddings
        """
        try:
            # Create placeholders for IDs
            placeholders = ", ".join(f":id_{i}" for i in range(len(ids)))
            params = {f"id_{i}": id_ for i, id_ in enumerate(ids)}
            
            # Create delete query
            query = text(
                f"DELETE FROM {self.table_name} "
                f"WHERE {self.id_column} IN ({placeholders})"
            )
            
            # Execute query
            result = await db.execute(query, params)
            await db.commit()
            
            return result.rowcount
        except Exception as e:
            logger.error(f"Error in delete_embeddings: {e}")
            await db.rollback()
            return 0
    
    async def update_embedding(
        self,
        id_: str,
        embedding: List[float],
        db: AsyncSession,
        extra_fields: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update an embedding in the vector store.
        
        Args:
            id_: ID of the item to update
            embedding: New embedding vector
            db: Database session
            extra_fields: Optional extra fields to update
            
        Returns:
            True if update was successful
        """
        try:
            # Prepare update data
            update_data = {self.embedding_column: embedding}
            if extra_fields:
                update_data.update(extra_fields)
            
            # Generate SET clause
            set_clause = ", ".join(f"{key} = :{key}" for key in update_data.keys())
            
            # Create update query
            query = text(
                f"UPDATE {self.table_name} "
                f"SET {set_clause} "
                f"WHERE {self.id_column} = :id"
            )
            
            # Execute query
            params = {**update_data, "id": id_}
            result = await db.execute(query, params)
            await db.commit()
            
            return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error in update_embedding: {e}")
            await db.rollback()
            return False
    
    async def get_embeddings(
        self,
        ids: List[str],
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """
        Get embeddings from the vector store by IDs.
        
        Args:
            ids: List of IDs to retrieve
            db: Database session
            
        Returns:
            List of embeddings
        """
        try:
            # Create placeholders for IDs
            placeholders = ", ".join(f":id_{i}" for i in range(len(ids)))
            params = {f"id_{i}": id_ for i, id_ in enumerate(ids)}
            
            # Create select query
            query = text(
                f"SELECT * FROM {self.table_name} "
                f"WHERE {self.id_column} IN ({placeholders})"
            )
            
            # Execute query
            result = await db.execute(query, params)
            rows = result.all()
            
            # Convert to dictionaries
            embeddings = [dict(row) for row in rows]
            
            return embeddings
        except Exception as e:
            logger.error(f"Error in get_embeddings: {e}")
            return []


class MemoryVectorStore(PGVectorStore):
    """
    Vector store implementation specifically for memory storage.
    
    This class extends PGVectorStore with memory-specific operations.
    """
    
    def __init__(self, dimension: int = 1536):
        """
        Initialize a memory vector store.
        
        Args:
            dimension: Dimension of the embedding vectors
        """
        super().__init__(
            table_name="memory_chunks",
            id_column="id",
            embedding_column="embedding",
            dimension=dimension,
            distance_strategy="cosine"
        )
    
    async def search_memories(
        self,
        query_embedding: List[float],
        user_id: str,
        db: AsyncSession,
        limit: int = 10,
        offset: int = 0,
        min_relevance_score: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search memories by vector similarity.
        
        Args:
            query_embedding: The embedding vector to search with
            user_id: ID of the user whose memories to search
            db: Database session
            limit: Maximum number of results to return
            offset: Offset for pagination
            min_relevance_score: Minimum relevance score (1 - cosine distance)
            
        Returns:
            List of memory chunks with their relevance scores
        """
        filter_criteria = {"user_id": user_id}
        
        # Search for similar memories
        results = await self.similarity_search(
            query_embedding=query_embedding,
            db=db,
            filter_criteria=filter_criteria,
            limit=limit,
            offset=offset
        )
        
        # Filter by minimum relevance score
        filtered_results = []
        for item, distance in results:
            # Convert distance to relevance score (1 - cosine distance)
            relevance_score = 1.0 - float(distance)
            
            if relevance_score >= min_relevance_score:
                item["relevance_score"] = relevance_score
                filtered_results.append(item)
        
        return filtered_results
    
    async def upsert_memory_chunks(
        self,
        memory_id: str,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]],
        user_id: str,
        db: AsyncSession
    ) -> List[str]:
        """
        Add or update memory chunks with their embeddings.
        
        Args:
            memory_id: ID of the parent memory
            chunks: List of memory chunk data
            embeddings: List of embedding vectors for each chunk
            user_id: ID of the user who owns the memory
            db: Database session
            
        Returns:
            List of chunk IDs
        """
        # First, delete any existing chunks for this memory
        await db.execute(
            text(f"DELETE FROM {self.table_name} WHERE memory_id = :memory_id"),
            {"memory_id": memory_id}
        )
        
        # Add common fields to all chunks
        extra_fields = {
            "memory_id": memory_id,
            "user_id": user_id,
            "created_at": func.now(),
            "updated_at": func.now()
        }
        
        # Add new chunks with embeddings
        return await self.batch_add_embeddings(
            items=chunks,
            embeddings=embeddings,
            db=db,
            extra_fields=extra_fields
        )
