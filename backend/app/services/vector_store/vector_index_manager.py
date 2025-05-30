"""
Vector Index Manager

This module provides services for managing vector indexes, optimizing queries,
and handling vector operations for efficient similarity searches.
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple, Union, Set
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.vector_store.pgvector_store import PGVectorStore, MemoryVectorStore
from app.core.config import settings


# Set up module logger
logger = logging.getLogger(__name__)


class VectorIndexManager:
    """
    Manager for vector indexes and operations.
    
    This class provides high-level operations for managing vector indexes,
    optimizing queries, and maintaining vector store performance.
    """
    
    def __init__(self):
        """Initialize the vector index manager."""
        self._stores: Dict[str, PGVectorStore] = {}
        self._initialized: Set[str] = set()
        self._maintenance_lock = asyncio.Lock()
    
    def register_store(self, name: str, store: PGVectorStore) -> None:
        """
        Register a vector store with the manager.
        
        Args:
            name: Name to identify the store
            store: Vector store instance
        """
        self._stores[name] = store
        logger.info(f"Registered vector store: {name}")
    
    async def initialize_all(self, db: AsyncSession) -> bool:
        """
        Initialize all registered vector stores.
        
        Args:
            db: Database session
            
        Returns:
            True if all stores were initialized successfully
        """
        success = True
        
        for name, store in self._stores.items():
            if name not in self._initialized:
                try:
                    initialized = await store.initialize(db)
                    if initialized:
                        self._initialized.add(name)
                    else:
                        success = False
                except Exception as e:
                    logger.error(f"Error initializing vector store {name}: {e}")
                    success = False
        
        return success
    
    def get_store(self, name: str) -> Optional[PGVectorStore]:
        """
        Get a vector store by name.
        
        Args:
            name: Name of the store to retrieve
            
        Returns:
            Vector store instance, or None if not found
        """
        return self._stores.get(name)
    
    async def run_maintenance(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Run maintenance tasks on vector stores.
        
        This includes rebuilding indexes, vacuuming tables, and
        analyzing query performance.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with maintenance results
        """
        # Avoid running multiple maintenance tasks simultaneously
        async with self._maintenance_lock:
            results = {}
            
            for name, store in self._stores.items():
                try:
                    # Get table statistics
                    stats_query = f"""
                        SELECT 
                            relname as table_name,
                            n_live_tup as row_count,
                            n_dead_tup as dead_tuples,
                            last_analyze,
                            last_vacuum
                        FROM 
                            pg_stat_user_tables
                        WHERE 
                            relname = '{store.table_name}'
                    """
                    stats_result = await db.execute(stats_query)
                    stats = stats_result.mappings().one_or_none()
                    
                    # Rebuild index if needed
                    needs_reindex = False
                    if stats and stats["row_count"] > 1000 and stats["dead_tuples"] > stats["row_count"] * 0.1:
                        needs_reindex = True
                        
                    if needs_reindex:
                        logger.info(f"Rebuilding index for {store.table_name}")
                        # Get index name
                        index_name = f"idx_{store.table_name}_{store.embedding_column}"
                        
                        # Drop and recreate index
                        await db.execute(f"DROP INDEX IF EXISTS {index_name}")
                        
                        # Determine index method
                        if store.distance_strategy == "cosine":
                            index_method = "vector_cosine_ops"
                        elif store.distance_strategy == "l2":
                            index_method = "vector_l2_ops"
                        else:
                            index_method = "vector_ip_ops"
                        
                        # Create index
                        await db.execute(f"""
                            CREATE INDEX {index_name} 
                            ON {store.table_name} 
                            USING ivfflat ({store.embedding_column} {index_method})
                            WITH (lists = 100)
                        """)
                        
                        # Vacuum analyze the table
                        await db.execute(f"VACUUM ANALYZE {store.table_name}")
                        
                    # Store results
                    results[name] = {
                        "stats": dict(stats) if stats else None,
                        "reindexed": needs_reindex
                    }
                    
                except Exception as e:
                    logger.error(f"Error during maintenance for {name}: {e}")
                    results[name] = {"error": str(e)}
            
            await db.commit()
            return results
    
    async def optimize_query(
        self, 
        store_name: str,
        query_type: str,
        query_embedding: List[float],
        filter_criteria: Optional[Dict[str, Any]] = None,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """
        Optimize a query for the given parameters.
        
        Args:
            store_name: Name of the vector store
            query_type: Type of query (e.g., 'similarity', 'knn')
            query_embedding: Query embedding vector
            filter_criteria: Filter criteria for the query
            db: Database session
            
        Returns:
            Dictionary with optimization suggestions
        """
        store = self.get_store(store_name)
        if not store:
            return {"error": f"Store {store_name} not found"}
        
        result = {
            "suggestions": [],
            "query_plan": None
        }
        
        try:
            # Get query plan for similarity search
            query = store._get_distance_function()(query_embedding)
            
            plan_query = f"""
                EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
                SELECT * FROM {store.table_name}
                WHERE {query}
                ORDER BY {query} ASC
                LIMIT 10
            """
            
            plan_result = await db.execute(plan_query)
            query_plan = plan_result.scalar()
            
            result["query_plan"] = query_plan
            
            # Analyze plan for issues
            if "Seq Scan" in str(query_plan):
                result["suggestions"].append({
                    "type": "index",
                    "message": "Query is using sequential scan instead of index.",
                    "action": "Consider rebuilding the index or check filter conditions."
                })
            
            if filter_criteria and len(filter_criteria) > 2:
                result["suggestions"].append({
                    "type": "filter",
                    "message": "Large number of filter criteria may slow down the query.",
                    "action": "Consider using fewer filters or creating a composite index."
                })
            
            # Estimate memory usage
            dimension = store.dimension
            result_size = 10  # Default limit
            memory_estimate = dimension * result_size * 4 / (1024 * 1024)  # in MB
            
            result["memory_estimate"] = {
                "mb": memory_estimate,
                "high_usage": memory_estimate > 100
            }
            
            if result["memory_estimate"]["high_usage"]:
                result["suggestions"].append({
                    "type": "memory",
                    "message": f"Query might use a lot of memory ({memory_estimate:.2f} MB).",
                    "action": "Consider reducing result size or vector dimension."
                })
            
        except Exception as e:
            logger.error(f"Error optimizing query: {e}")
            result["error"] = str(e)
            
        return result


class VectorServiceFactory:
    """
    Factory for creating vector store services.
    
    This class provides methods to create and configure different types
    of vector stores based on application needs.
    """
    
    @staticmethod
    def create_memory_store(dimension: int = 1536) -> MemoryVectorStore:
        """
        Create a memory vector store.
        
        Args:
            dimension: Dimension of the embedding vectors
            
        Returns:
            Configured MemoryVectorStore instance
        """
        return MemoryVectorStore(dimension=dimension)
    
    @staticmethod
    def create_custom_store(
        table_name: str,
        id_column: str,
        embedding_column: str,
        dimension: int = 1536,
        distance_strategy: str = "cosine"
    ) -> PGVectorStore:
        """
        Create a custom vector store.
        
        Args:
            table_name: Name of the database table to use
            id_column: Name of the ID column in the table
            embedding_column: Name of the embedding column in the table
            dimension: Dimension of the embedding vectors
            distance_strategy: Distance strategy to use
            
        Returns:
            Configured PGVectorStore instance
        """
        return PGVectorStore(
            table_name=table_name,
            id_column=id_column,
            embedding_column=embedding_column,
            dimension=dimension,
            distance_strategy=distance_strategy
        )


# Create global index manager instance
vector_index_manager = VectorIndexManager()

# Register default stores
memory_store = VectorServiceFactory.create_memory_store()
vector_index_manager.register_store("memory", memory_store)


# Initialize function to be called at application startup
async def initialize_vector_stores():
    """Initialize all vector stores at application startup."""
    async with get_db() as db:
        await vector_index_manager.initialize_all(db)
