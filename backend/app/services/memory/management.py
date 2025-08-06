"""
Memory Management and Pruning

This module provides services for managing memory retention, cleanup, and optimization
to ensure efficient storage and retrieval of memories in the system.
"""
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.vector_store import MemoryVectorStore
from app.services.vector_store.vector_index_manager import vector_index_manager


# Set up module logger
logger = logging.getLogger(__name__)


class RetentionPolicy:
    """
    Defines a retention policy for memories.
    
    A retention policy determines how long memories are kept and
    under what conditions they should be archived or deleted.
    """
    
    def __init__(
        self,
        name: str,
        max_age_days: Optional[int] = None,
        max_count: Optional[int] = None,
        min_access_count: Optional[int] = None,
        importance_threshold: Optional[float] = None,
        archive_enabled: bool = True
    ):
        """
        Initialize a retention policy.
        
        Args:
            name: Name of the policy
            max_age_days: Maximum age in days before memories are considered for pruning
            max_count: Maximum number of memories to keep (oldest will be pruned)
            min_access_count: Minimum number of accesses to keep a memory
            importance_threshold: Minimum importance score to keep a memory
            archive_enabled: Whether to archive memories instead of deleting them
        """
        self.name = name
        self.max_age_days = max_age_days
        self.max_count = max_count
        self.min_access_count = min_access_count
        self.importance_threshold = importance_threshold
        self.archive_enabled = archive_enabled
    
    def should_prune(
        self,
        memory: Dict[str, Any],
        total_count: int
    ) -> Tuple[bool, str]:
        """
        Determine if a memory should be pruned based on this policy.
        
        Args:
            memory: Memory data to evaluate
            total_count: Total count of memories
            
        Returns:
            Tuple of (should_prune, reason)
        """
        reasons = []
        
        # Check age
        if self.max_age_days is not None:
            created_at = memory.get("created_at")
            if created_at:
                age_days = (datetime.now() - created_at).days
                if age_days > self.max_age_days:
                    reasons.append(f"Age ({age_days} days) exceeds maximum ({self.max_age_days} days)")
        
        # Check access count
        if self.min_access_count is not None:
            access_count = memory.get("access_count", 0)
            if access_count < self.min_access_count:
                reasons.append(f"Access count ({access_count}) below minimum ({self.min_access_count})")
        
        # Check importance
        if self.importance_threshold is not None:
            importance = memory.get("importance_score", 0.0)
            if importance < self.importance_threshold:
                reasons.append(f"Importance score ({importance:.2f}) below threshold ({self.importance_threshold:.2f})")
        
        # Check count limit
        if self.max_count is not None and total_count > self.max_count:
            age_rank = memory.get("age_rank", 0)
            if age_rank > self.max_count:
                reasons.append(f"Memory count ({total_count}) exceeds maximum ({self.max_count})")
        
        return bool(reasons), ", ".join(reasons)


class MemoryManagementService:
    """
    Service for managing memory retention and pruning.
    
    This service provides methods for managing memories according to retention policies,
    cleaning up unused or outdated memories, and optimizing the memory storage.
    """
    
    # Default retention policies
    DEFAULT_POLICIES = {
        "standard": RetentionPolicy(
            name="standard",
            max_age_days=365,  # 1 year
            min_access_count=3,
            importance_threshold=0.3,
            archive_enabled=True
        ),
        "important": RetentionPolicy(
            name="important",
            max_age_days=730,  # 2 years
            min_access_count=1,
            importance_threshold=0.7,
            archive_enabled=True
        ),
        "system": RetentionPolicy(
            name="system",
            max_age_days=None,  # Never expire
            min_access_count=None,
            importance_threshold=None,
            archive_enabled=False
        )
    }
    
    def __init__(self):
        """Initialize the memory management service."""
        self.policies = self.DEFAULT_POLICIES.copy()
        self.vector_store = vector_index_manager.get_store("memory")
        if not self.vector_store:
            logger.warning("Memory vector store not found, using default")
            self.vector_store = MemoryVectorStore()
            vector_index_manager.register_store("memory", self.vector_store)
    
    async def run_maintenance(
        self,
        db: AsyncSession,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Run maintenance tasks including pruning and optimization.
        
        Args:
            db: Database session
            dry_run: If True, report what would be done but don't actually do it
            
        Returns:
            Dictionary with maintenance results
        """
        try:
            logger.info("Starting memory maintenance")
            
            # Results to report
            results = {
                "pruned": 0,
                "archived": 0,
                "optimized": 0,
                "pruned_memories": [],
                "archived_memories": [],
                "errors": []
            }
            
            # Step 1: Get memory statistics
            stats = await self._get_memory_statistics(db)
            
            # Step 2: Prune memories based on retention policies
            if not dry_run:
                for user_id, user_stats in stats.get("by_user", {}).items():
                    # Get retention policy for this user (default to standard)
                    policy_name = "standard"  # Could be fetched from user settings
                    policy = self.policies.get(policy_name, self.policies["standard"])
                    
                    # Get memories to prune
                    to_prune = await self._get_memories_to_prune(
                        db=db,
                        user_id=user_id,
                        policy=policy,
                        total_count=user_stats.get("memory_count", 0)
                    )
                    
                    # Process memories
                    for memory in to_prune:
                        if policy.archive_enabled:
                            archived = await self._archive_memory(db, memory["id"])
                            if archived:
                                results["archived"] += 1
                                results["archived_memories"].append({
                                    "id": memory["id"],
                                    "title": memory["title"],
                                    "reason": memory.get("prune_reason", "")
                                })
                        else:
                            pruned = await self._delete_memory(db, memory["id"])
                            if pruned:
                                results["pruned"] += 1
                                results["pruned_memories"].append({
                                    "id": memory["id"],
                                    "title": memory["title"],
                                    "reason": memory.get("prune_reason", "")
                                })
                    
                # Step 3: Optimize storage
                optimized = await self._optimize_storage(db)
                results["optimized"] = optimized
            else:
                # Dry run - just report what would be pruned
                all_to_prune = []
                
                for user_id, user_stats in stats.get("by_user", {}).items():
                    policy_name = "standard"
                    policy = self.policies.get(policy_name, self.policies["standard"])
                    
                    to_prune = await self._get_memories_to_prune(
                        db=db,
                        user_id=user_id,
                        policy=policy,
                        total_count=user_stats.get("memory_count", 0)
                    )
                    all_to_prune.extend(to_prune)
                
                for memory in all_to_prune:
                    policy_name = "standard"
                    policy = self.policies.get(policy_name, self.policies["standard"])
                    
                    if policy.archive_enabled:
                        results["archived"] += 1
                        results["archived_memories"].append({
                            "id": memory["id"],
                            "title": memory["title"],
                            "reason": memory.get("prune_reason", "")
                        })
                    else:
                        results["pruned"] += 1
                        results["pruned_memories"].append({
                            "id": memory["id"],
                            "title": memory["title"],
                            "reason": memory.get("prune_reason", "")
                        })
            
            # Return results
            return {
                **results,
                "stats": stats,
                "dry_run": dry_run
            }
        except Exception as e:
            logger.error(f"Error during memory maintenance: {e}")
            return {
                "error": str(e),
                "pruned": 0,
                "archived": 0,
                "optimized": 0,
                "dry_run": dry_run
            }
    
    async def _get_memory_statistics(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Get memory statistics.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with memory statistics
        """
        try:
            # Get total memory statistics
            total_query = """
                SELECT
                    COUNT(*) as memory_count,
                    SUM(array_length(embedding, 1)) as total_vectors,
                    AVG(access_count) as avg_access_count,
                    MAX(created_at) as newest_memory,
                    MIN(created_at) as oldest_memory
                FROM memories
            """
            
            total_result = await db.execute(total_query)
            total_stats = dict(total_result.mappings().one())
            
            # Get statistics by user
            user_query = """
                SELECT
                    user_id,
                    COUNT(*) as memory_count,
                    AVG(access_count) as avg_access_count,
                    MAX(created_at) as newest_memory,
                    MIN(created_at) as oldest_memory
                FROM memories
                GROUP BY user_id
            """
            
            user_result = await db.execute(user_query)
            user_stats = {}
            
            for row in user_result.mappings():
                user_stats[row["user_id"]] = dict(row)
            
            return {
                "total": total_stats,
                "by_user": user_stats
            }
        except Exception as e:
            logger.error(f"Error getting memory statistics: {e}")
            return {"error": str(e)}
    
    async def _get_memories_to_prune(
        self,
        db: AsyncSession,
        user_id: str,
        policy: RetentionPolicy,
        total_count: int
    ) -> List[Dict[str, Any]]:
        """
        Get memories that should be pruned based on the policy.
        
        Args:
            db: Database session
            user_id: ID of the user whose memories to check
            policy: Retention policy to apply
            total_count: Total count of memories for this user
            
        Returns:
            List of memories to prune with pruning reasons
        """
        try:
            conditions = []
            params = {"user_id": user_id}
            
            # Apply policy conditions
            if policy.max_age_days is not None:
                cutoff_date = datetime.now() - timedelta(days=policy.max_age_days)
                conditions.append("created_at < :cutoff_date")
                params["cutoff_date"] = cutoff_date
            
            if policy.min_access_count is not None:
                conditions.append("access_count < :min_access_count")
                params["min_access_count"] = policy.min_access_count
            
            if policy.importance_threshold is not None:
                conditions.append("importance_score < :importance_threshold")
                params["importance_threshold"] = policy.importance_threshold
            
            # Build query
            query = """
                SELECT
                    id,
                    title,
                    created_at,
                    updated_at,
                    last_accessed_at,
                    access_count,
                    importance_score,
                    ROW_NUMBER() OVER (ORDER BY created_at ASC) as age_rank
                FROM memories
                WHERE user_id = :user_id
            """
            
            if conditions:
                query += " AND " + " AND ".join(conditions)
            
            # Execute query
            result = await db.execute(query, params)
            memories = [dict(row) for row in result.mappings()]
            
            # Apply max_count condition
            if policy.max_count is not None and total_count > policy.max_count:
                # Sort by age (oldest first)
                memories.sort(key=lambda m: m["created_at"])
                # Keep only oldest memories that exceed the count
                memories = memories[:total_count - policy.max_count]
            
            # Add pruning reasons
            for memory in memories:
                _, reason = policy.should_prune(memory, total_count)
                memory["prune_reason"] = reason
            
            return memories
        except Exception as e:
            logger.error(f"Error getting memories to prune: {e}")
            return []
    
    async def _archive_memory(self, db: AsyncSession, memory_id: str) -> bool:
        """
        Archive a memory by moving it to the archive table.
        
        Args:
            db: Database session
            memory_id: ID of the memory to archive
            
        Returns:
            True if the memory was archived
        """
        try:
            # 1. Insert into archive
            archive_query = """
                INSERT INTO memory_archives (
                    id, user_id, title, content, created_at, updated_at,
                    last_accessed_at, access_count, importance_score, tags, metadata
                )
                SELECT 
                    id, user_id, title, content, created_at, updated_at,
                    last_accessed_at, access_count, importance_score, tags, metadata
                FROM memories
                WHERE id = :memory_id
            """
            
            await db.execute(archive_query, {"memory_id": memory_id})
            
            # 2. Delete original memory
            delete_query = """
                DELETE FROM memories
                WHERE id = :memory_id
            """
            
            delete_result = await db.execute(delete_query, {"memory_id": memory_id})
            
            # 3. Delete memory chunks
            delete_chunks_query = """
                DELETE FROM memory_chunks
                WHERE memory_id = :memory_id
            """
            
            await db.execute(delete_chunks_query, {"memory_id": memory_id})
            
            # Commit transaction
            await db.commit()
            
            return delete_result.rowcount > 0
        except Exception as e:
            logger.error(f"Error archiving memory {memory_id}: {e}")
            await db.rollback()
            return False
    
    async def _delete_memory(self, db: AsyncSession, memory_id: str) -> bool:
        """
        Delete a memory and its chunks.
        
        Args:
            db: Database session
            memory_id: ID of the memory to delete
            
        Returns:
            True if the memory was deleted
        """
        try:
            # 1. Delete memory chunks
            delete_chunks_query = """
                DELETE FROM memory_chunks
                WHERE memory_id = :memory_id
            """
            
            await db.execute(delete_chunks_query, {"memory_id": memory_id})
            
            # 2. Delete memory
            delete_query = """
                DELETE FROM memories
                WHERE id = :memory_id
            """
            
            delete_result = await db.execute(delete_query, {"memory_id": memory_id})
            
            # Commit transaction
            await db.commit()
            
            return delete_result.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting memory {memory_id}: {e}")
            await db.rollback()
            return False
    
    async def _optimize_storage(self, db: AsyncSession) -> int:
        """
        Optimize memory storage.
        
        Args:
            db: Database session
            
        Returns:
            Number of optimized items
        """
        try:
            # 1. Run VACUUM ANALYZE on memory tables
            await db.execute("VACUUM ANALYZE memories")
            await db.execute("VACUUM ANALYZE memory_chunks")
            
            # 2. Rebuild indexes if needed
            await vector_index_manager.run_maintenance(db)
            
            # Return 1 for success
            return 1
        except Exception as e:
            logger.error(f"Error optimizing memory storage: {e}")
            return 0


# Create global memory management service instance
memory_management_service = MemoryManagementService()


# Scheduled task for memory maintenance
async def run_scheduled_maintenance():
    """Run scheduled memory maintenance."""
    try:
        # Run maintenance every day
        while True:
            logger.info("Running scheduled memory maintenance")
            async with get_db() as db:
                await memory_management_service.run_maintenance(db)
            
            # Wait for 24 hours
            await asyncio.sleep(24 * 60 * 60)
    except Exception as e:
        logger.error(f"Error in scheduled maintenance: {e}")
