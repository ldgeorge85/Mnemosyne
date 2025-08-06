"""
Memory Relevance Scoring

This module provides services for calculating and updating memory relevance scores
based on various factors such as access patterns, similarity to recent queries,
and temporal decay.
"""
import logging
import math
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.memory.retrieval import memory_retrieval_service
from app.services.llm import OpenAIClient


# Set up module logger
logger = logging.getLogger(__name__)


class ScoringFactor:
    """Base class for scoring factors that contribute to memory relevance."""
    
    def __init__(self, name: str, weight: float = 1.0):
        """
        Initialize a scoring factor.
        
        Args:
            name: Name of this scoring factor
            weight: Weight of this factor in the final score (0.0-1.0)
        """
        self.name = name
        self.weight = weight
    
    async def calculate(self, memory: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Calculate this factor's contribution to the relevance score.
        
        Args:
            memory: Memory to score
            context: Scoring context with additional information
            
        Returns:
            Score contribution (0.0-1.0)
        """
        raise NotImplementedError("Subclasses must implement calculate()")


class RecencyFactor(ScoringFactor):
    """Scoring factor based on memory recency."""
    
    def __init__(self, weight: float = 0.3, max_age_days: int = 365):
        """
        Initialize recency factor.
        
        Args:
            weight: Weight in the final score
            max_age_days: Maximum age in days for normalization
        """
        super().__init__(name="recency", weight=weight)
        self.max_age_days = max_age_days
    
    async def calculate(self, memory: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Calculate recency score based on creation date.
        
        Args:
            memory: Memory to score
            context: Scoring context
            
        Returns:
            Recency score (0.0-1.0)
        """
        created_at = memory.get("created_at")
        if not created_at:
            return 0.0
            
        now = datetime.now()
        age_days = (now - created_at).days
        
        # Normalize: newer = higher score
        if age_days >= self.max_age_days:
            return 0.0
        
        # Exponential decay function
        decay_rate = 3.0 / self.max_age_days  # 95% decay at max_age_days/3
        return math.exp(-decay_rate * age_days)


class AccessFrequencyFactor(ScoringFactor):
    """Scoring factor based on access frequency."""
    
    def __init__(self, weight: float = 0.25, max_count: int = 10):
        """
        Initialize access frequency factor.
        
        Args:
            weight: Weight in the final score
            max_count: Access count that gives maximum score
        """
        super().__init__(name="access_frequency", weight=weight)
        self.max_count = max_count
    
    async def calculate(self, memory: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Calculate score based on access frequency.
        
        Args:
            memory: Memory to score
            context: Scoring context
            
        Returns:
            Access frequency score (0.0-1.0)
        """
        access_count = memory.get("access_count", 0)
        
        # Normalize: more accesses = higher score
        raw_score = min(access_count / self.max_count, 1.0)
        
        # Apply logarithmic curve to emphasize differences at lower counts
        # ln(x+1) / ln(max_count+1) gives a nice curve from 0 to 1
        if raw_score > 0:
            return math.log(access_count + 1) / math.log(self.max_count + 1)
        return 0.0


class RecentAccessFactor(ScoringFactor):
    """Scoring factor based on recency of last access."""
    
    def __init__(self, weight: float = 0.2, recent_days: int = 7):
        """
        Initialize recent access factor.
        
        Args:
            weight: Weight in the final score
            recent_days: Number of days considered "recent"
        """
        super().__init__(name="recent_access", weight=weight)
        self.recent_days = recent_days
    
    async def calculate(self, memory: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Calculate score based on recency of last access.
        
        Args:
            memory: Memory to score
            context: Scoring context
            
        Returns:
            Recent access score (0.0-1.0)
        """
        last_accessed_at = memory.get("last_accessed_at")
        if not last_accessed_at:
            return 0.0
            
        now = datetime.now()
        days_since_access = (now - last_accessed_at).days
        
        # Normalize: more recent access = higher score
        if days_since_access >= self.recent_days:
            return 0.0
        
        return 1.0 - (days_since_access / self.recent_days)


class ExplicitImportanceFactor(ScoringFactor):
    """Scoring factor based on explicit user-defined importance."""
    
    def __init__(self, weight: float = 0.25):
        """
        Initialize explicit importance factor.
        
        Args:
            weight: Weight in the final score
        """
        super().__init__(name="explicit_importance", weight=weight)
    
    async def calculate(self, memory: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Calculate score based on explicit importance.
        
        Args:
            memory: Memory to score
            context: Scoring context
            
        Returns:
            Explicit importance score (0.0-1.0)
        """
        # Check for explicit importance markers
        tags = memory.get("tags", [])
        metadata = memory.get("metadata", {})
        
        # Check for importance in tags
        importance_tags = {
            "critical": 1.0,
            "important": 0.8,
            "high_priority": 0.8,
            "medium_priority": 0.5,
            "low_priority": 0.3
        }
        
        for tag in tags:
            if tag in importance_tags:
                return importance_tags[tag]
        
        # Check for importance in metadata
        if "importance" in metadata and isinstance(metadata["importance"], (int, float)):
            return min(max(float(metadata["importance"]), 0.0), 1.0)
        
        return 0.5  # Default middle importance


class SemanticRelevanceFactor(ScoringFactor):
    """Scoring factor based on semantic relevance to recent queries."""
    
    def __init__(self, weight: float = 0.3):
        """
        Initialize semantic relevance factor.
        
        Args:
            weight: Weight in the final score
        """
        super().__init__(name="semantic_relevance", weight=weight)
        self.openai_client = OpenAIClient()
    
    async def calculate(self, memory: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Calculate score based on semantic relevance to recent queries.
        
        Args:
            memory: Memory to score
            context: Scoring context with recent queries
            
        Returns:
            Semantic relevance score (0.0-1.0)
        """
        # If no recent queries provided, return neutral score
        recent_queries = context.get("recent_queries", [])
        if not recent_queries:
            return 0.5
            
        # If memory already has a relevance score for the current query, use it
        if "relevance_score" in memory:
            return memory["relevance_score"]
            
        # Use most recent query if available
        if "current_query" in context:
            query_embedding = context.get("current_query_embedding")
            memory_embedding = memory.get("embedding")
            
            if query_embedding and memory_embedding:
                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_embedding, memory_embedding)
                return similarity
        
        # Default score if no query context available
        return 0.5
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity (0.0-1.0)
        """
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
            
        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Calculate magnitudes
        mag1 = math.sqrt(sum(a * a for a in vec1))
        mag2 = math.sqrt(sum(b * b for b in vec2))
        
        # Avoid division by zero
        if mag1 * mag2 == 0:
            return 0.0
            
        # Calculate cosine similarity
        return (dot_product / (mag1 * mag2) + 1) / 2  # Normalize to 0-1 range


class MemoryRelevanceScorer:
    """
    Service for calculating and updating memory relevance scores.
    
    This service uses multiple scoring factors to determine the overall
    relevance and importance of memories.
    """
    
    def __init__(self):
        """Initialize the memory relevance scorer with default factors."""
        self.scoring_factors = [
            RecencyFactor(weight=0.25),
            AccessFrequencyFactor(weight=0.20),
            RecentAccessFactor(weight=0.15),
            ExplicitImportanceFactor(weight=0.20),
            SemanticRelevanceFactor(weight=0.30)
        ]
    
    async def score_memory(
        self,
        memory: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate the relevance score for a memory.
        
        Args:
            memory: Memory to score
            context: Optional scoring context with additional information
            
        Returns:
            Tuple of (overall score, factor scores)
        """
        context = context or {}
        factor_scores = {}
        weighted_sum = 0.0
        total_weight = 0.0
        
        # Calculate score for each factor
        for factor in self.scoring_factors:
            try:
                score = await factor.calculate(memory, context)
                factor_scores[factor.name] = score
                weighted_sum += score * factor.weight
                total_weight += factor.weight
            except Exception as e:
                logger.error(f"Error calculating {factor.name} score: {e}")
                factor_scores[factor.name] = 0.0
        
        # Calculate overall score
        if total_weight == 0:
            overall_score = 0.0
        else:
            overall_score = weighted_sum / total_weight
        
        return overall_score, factor_scores
    
    async def update_memory_scores(
        self,
        db: AsyncSession,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Update relevance scores for memories in the database.
        
        Args:
            db: Database session
            user_id: Optional user ID to update only their memories
            limit: Maximum number of memories to update
            
        Returns:
            Dictionary with update results
        """
        try:
            # Build query to get memories to update
            query = """
                SELECT m.*
                FROM memories m
                LEFT JOIN memory_scores ms ON m.id = ms.memory_id
                WHERE ms.last_scored IS NULL OR ms.last_scored < NOW() - INTERVAL '7 days'
            """
            
            params = {}
            
            if user_id:
                query += " AND m.user_id = :user_id"
                params["user_id"] = user_id
                
            query += " ORDER BY ms.last_scored ASC NULLS FIRST LIMIT :limit"
            params["limit"] = limit
            
            # Execute query
            result = await db.execute(query, params)
            memories = [dict(row) for row in result.mappings()]
            
            # Update scores for each memory
            updated_count = 0
            for memory in memories:
                try:
                    # Score the memory
                    overall_score, factor_scores = await self.score_memory(memory)
                    
                    # Update the database
                    update_query = """
                        INSERT INTO memory_scores (
                            memory_id, overall_score, recency_score, access_frequency_score,
                            recent_access_score, explicit_importance_score, semantic_relevance_score,
                            last_scored
                        )
                        VALUES (
                            :memory_id, :overall_score, :recency_score, :access_frequency_score,
                            :recent_access_score, :explicit_importance_score, :semantic_relevance_score,
                            NOW()
                        )
                        ON CONFLICT (memory_id) DO UPDATE SET
                            overall_score = :overall_score,
                            recency_score = :recency_score,
                            access_frequency_score = :access_frequency_score,
                            recent_access_score = :recent_access_score,
                            explicit_importance_score = :explicit_importance_score,
                            semantic_relevance_score = :semantic_relevance_score,
                            last_scored = NOW()
                    """
                    
                    await db.execute(
                        update_query,
                        {
                            "memory_id": memory["id"],
                            "overall_score": overall_score,
                            "recency_score": factor_scores.get("recency", 0.0),
                            "access_frequency_score": factor_scores.get("access_frequency", 0.0),
                            "recent_access_score": factor_scores.get("recent_access", 0.0),
                            "explicit_importance_score": factor_scores.get("explicit_importance", 0.0),
                            "semantic_relevance_score": factor_scores.get("semantic_relevance", 0.0)
                        }
                    )
                    
                    # Update importance_score in memories table too
                    await db.execute(
                        "UPDATE memories SET importance_score = :score WHERE id = :id",
                        {"id": memory["id"], "score": overall_score}
                    )
                    
                    updated_count += 1
                except Exception as e:
                    logger.error(f"Error updating score for memory {memory['id']}: {e}")
            
            # Commit transaction
            await db.commit()
            
            return {
                "updated_count": updated_count,
                "total_memories": len(memories)
            }
        except Exception as e:
            logger.error(f"Error updating memory scores: {e}")
            await db.rollback()
            return {"error": str(e)}
    
    async def get_memory_score(
        self,
        memory_id: str,
        db: AsyncSession,
        recalculate: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Get the relevance score for a specific memory.
        
        Args:
            memory_id: ID of the memory to score
            db: Database session
            recalculate: Whether to recalculate the score
            
        Returns:
            Dictionary with scores or None if memory not found
        """
        try:
            # Get the memory
            memory_query = "SELECT * FROM memories WHERE id = :memory_id"
            memory_result = await db.execute(memory_query, {"memory_id": memory_id})
            memory = memory_result.mappings().one_or_none()
            
            if not memory:
                return None
                
            if not recalculate:
                # Try to get existing score
                score_query = "SELECT * FROM memory_scores WHERE memory_id = :memory_id"
                score_result = await db.execute(score_query, {"memory_id": memory_id})
                existing_score = score_result.mappings().one_or_none()
                
                if existing_score:
                    return dict(existing_score)
            
            # Calculate new score
            overall_score, factor_scores = await self.score_memory(dict(memory))
            
            # Return scores
            return {
                "memory_id": memory_id,
                "overall_score": overall_score,
                "factor_scores": factor_scores,
                "calculated_at": datetime.now()
            }
        except Exception as e:
            logger.error(f"Error getting memory score: {e}")
            return None


# Create global memory relevance scorer instance
memory_relevance_scorer = MemoryRelevanceScorer()


# Scheduled task for updating memory scores
async def run_scheduled_scoring():
    """Run scheduled memory scoring updates."""
    try:
        # Run scoring update every 12 hours
        while True:
            logger.info("Running scheduled memory scoring")
            async with get_db() as db:
                await memory_relevance_scorer.update_memory_scores(db, limit=500)
            
            # Wait for 12 hours
            await asyncio.sleep(12 * 60 * 60)
    except Exception as e:
        logger.error(f"Error in scheduled scoring: {e}")
