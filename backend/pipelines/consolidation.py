"""
Memory consolidation pipeline for Mnemosyne Protocol
REM-like cycles for memory integration and pattern extraction
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

from pydantic import BaseModel, Field
from backend.pipelines.base import Pipeline, PipelineStage
from backend.models.memory import Memory, MemoryType, MemoryStatus
from backend.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ConsolidationCandidate(BaseModel):
    """Memory eligible for consolidation"""
    memory_id: str
    user_id: str
    content: str
    summary: Optional[str]
    importance: float
    occurred_at: datetime
    consolidation_count: int
    last_accessed_at: Optional[datetime]
    access_count: int
    domains: List[str]
    tags: List[str]
    embedding: Optional[List[float]]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConsolidationGroup(BaseModel):
    """Group of related memories for consolidation"""
    group_id: str
    user_id: str
    memories: List[ConsolidationCandidate]
    common_domains: List[str]
    common_tags: List[str]
    time_span: Tuple[datetime, datetime]
    coherence_score: float = 0.0
    synthesis: Optional[str] = None
    patterns: List[str] = Field(default_factory=list)
    insights: List[str] = Field(default_factory=list)


class ConsolidatedMemory(BaseModel):
    """Result of memory consolidation"""
    user_id: str
    content: str
    title: str
    memory_type: MemoryType = MemoryType.CONSOLIDATION
    parent_memory_ids: List[str]
    domains: List[str]
    tags: List[str]
    patterns: List[str]
    insights: List[str]
    importance: float
    coherence_score: float
    time_span: Tuple[datetime, datetime]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MemorySelectionStage(PipelineStage[str, List[ConsolidationCandidate]]):
    """Select memories eligible for consolidation"""
    
    def __init__(self, memory_service=None):
        super().__init__("memory_selection", required=True)
        self.memory_service = memory_service
    
    async def process(self, user_id: str, context: Dict[str, Any]) -> List[ConsolidationCandidate]:
        """Select consolidation candidates"""
        candidates = []
        
        if self.memory_service:
            # Fetch memories that need consolidation
            memories = await self.memory_service.get_consolidation_candidates(
                user_id=user_id,
                min_age_hours=context.get('min_age_hours', 24),
                max_memories=context.get('max_memories', 100)
            )
            
            for memory in memories:
                candidates.append(ConsolidationCandidate(
                    memory_id=str(memory.id),
                    user_id=str(memory.user_id),
                    content=memory.content,
                    summary=memory.summary,
                    importance=memory.importance,
                    occurred_at=memory.occurred_at,
                    consolidation_count=memory.consolidation_count,
                    last_accessed_at=memory.last_accessed_at,
                    access_count=memory.access_count,
                    domains=memory.domains,
                    tags=memory.tags,
                    embedding=memory.embedding_content,
                    metadata=memory.metadata
                ))
        else:
            # Mock data for testing
            now = datetime.utcnow()
            candidates = [
                ConsolidationCandidate(
                    memory_id=f"mock_{i}",
                    user_id=user_id,
                    content=f"Test memory {i}",
                    summary=f"Summary {i}",
                    importance=0.5 + i * 0.1,
                    occurred_at=now - timedelta(days=i),
                    consolidation_count=0,
                    last_accessed_at=now - timedelta(hours=i * 12),
                    access_count=i,
                    domains=['test'],
                    tags=['test'],
                    embedding=None
                )
                for i in range(3)
            ]
        
        logger.info(f"Selected {len(candidates)} memories for consolidation")
        return candidates


class MemoryClusteringStage(PipelineStage[List[ConsolidationCandidate], List[ConsolidationGroup]]):
    """Cluster related memories into groups"""
    
    def __init__(self):
        super().__init__("memory_clustering", required=True)
    
    def calculate_similarity(self, m1: ConsolidationCandidate, m2: ConsolidationCandidate) -> float:
        """Calculate similarity between two memories"""
        score = 0.0
        
        # Domain overlap
        domain_overlap = len(set(m1.domains) & set(m2.domains))
        score += domain_overlap * 0.3
        
        # Tag overlap
        tag_overlap = len(set(m1.tags) & set(m2.tags))
        score += tag_overlap * 0.2
        
        # Temporal proximity (within 7 days)
        time_diff = abs((m1.occurred_at - m2.occurred_at).days)
        if time_diff <= 7:
            score += (7 - time_diff) / 7 * 0.3
        
        # Importance similarity
        importance_diff = abs(m1.importance - m2.importance)
        score += (1 - importance_diff) * 0.2
        
        # If embeddings available, use cosine similarity
        if m1.embedding and m2.embedding:
            # Simplified cosine similarity
            # In production, use proper vector operations
            score += 0.5  # Placeholder
        
        return min(1.0, score)
    
    async def process(
        self,
        candidates: List[ConsolidationCandidate],
        context: Dict[str, Any]
    ) -> List[ConsolidationGroup]:
        """Group related memories"""
        if not candidates:
            return []
        
        # Simple clustering based on similarity
        groups = []
        used_memories = set()
        min_group_size = context.get('min_group_size', 2)
        
        for i, candidate in enumerate(candidates):
            if candidate.memory_id in used_memories:
                continue
            
            # Start a new group
            group_memories = [candidate]
            used_memories.add(candidate.memory_id)
            
            # Find similar memories
            for j, other in enumerate(candidates[i+1:], i+1):
                if other.memory_id in used_memories:
                    continue
                
                # Calculate average similarity to group
                similarities = [
                    self.calculate_similarity(member, other)
                    for member in group_memories
                ]
                avg_similarity = np.mean(similarities)
                
                if avg_similarity > 0.6:  # Threshold for grouping
                    group_memories.append(other)
                    used_memories.add(other.memory_id)
            
            # Only create group if it has enough members
            if len(group_memories) >= min_group_size:
                # Calculate group properties
                all_domains = []
                all_tags = []
                for mem in group_memories:
                    all_domains.extend(mem.domains)
                    all_tags.extend(mem.tags)
                
                common_domains = list(set(all_domains))
                common_tags = list(set(all_tags))
                
                time_span = (
                    min(m.occurred_at for m in group_memories),
                    max(m.occurred_at for m in group_memories)
                )
                
                group = ConsolidationGroup(
                    group_id=f"group_{datetime.utcnow().timestamp()}_{i}",
                    user_id=candidate.user_id,
                    memories=group_memories,
                    common_domains=common_domains[:5],  # Top 5
                    common_tags=common_tags[:10],  # Top 10
                    time_span=time_span,
                    coherence_score=avg_similarity
                )
                groups.append(group)
        
        logger.info(f"Created {len(groups)} consolidation groups from {len(candidates)} memories")
        return groups


class PatternExtractionStage(PipelineStage[List[ConsolidationGroup], List[ConsolidationGroup]]):
    """Extract patterns and insights from memory groups"""
    
    def __init__(self):
        super().__init__("pattern_extraction", required=False)
    
    async def process(
        self,
        groups: List[ConsolidationGroup],
        context: Dict[str, Any]
    ) -> List[ConsolidationGroup]:
        """Extract patterns from each group"""
        for group in groups:
            patterns = []
            insights = []
            
            # Pattern 1: Recurring themes
            theme_counts = defaultdict(int)
            for memory in group.memories:
                for tag in memory.tags:
                    theme_counts[tag] += 1
            
            recurring_themes = [
                tag for tag, count in theme_counts.items()
                if count >= len(group.memories) * 0.5  # Present in 50%+ memories
            ]
            if recurring_themes:
                patterns.append(f"Recurring themes: {', '.join(recurring_themes)}")
            
            # Pattern 2: Temporal patterns
            time_span_days = (group.time_span[1] - group.time_span[0]).days
            if time_span_days <= 1:
                patterns.append("Concentrated burst of activity")
            elif time_span_days <= 7:
                patterns.append("Weekly reflection cycle")
            else:
                patterns.append(f"Extended exploration over {time_span_days} days")
            
            # Pattern 3: Importance trends
            importances = [m.importance for m in group.memories]
            if len(importances) > 2:
                if importances[-1] > importances[0]:
                    insights.append("Increasing importance over time")
                elif importances[-1] < importances[0]:
                    insights.append("Decreasing importance over time")
            
            # Pattern 4: Domain convergence
            if len(group.common_domains) >= 3:
                insights.append(f"Interdisciplinary convergence: {', '.join(group.common_domains[:3])}")
            
            # Pattern 5: Access patterns
            high_access = [m for m in group.memories if m.access_count > 5]
            if len(high_access) > len(group.memories) * 0.5:
                patterns.append("Frequently revisited topic")
            
            group.patterns = patterns
            group.insights = insights
        
        return groups


class SynthesisGenerationStage(PipelineStage[List[ConsolidationGroup], List[ConsolidationGroup]]):
    """Generate synthesis for each group"""
    
    def __init__(self, llm_service=None):
        super().__init__("synthesis_generation", required=False)
        self.llm_service = llm_service
    
    async def process(
        self,
        groups: List[ConsolidationGroup],
        context: Dict[str, Any]
    ) -> List[ConsolidationGroup]:
        """Generate synthesis for each group"""
        for group in groups:
            # Simple synthesis without LLM
            # In production, would use LLM for intelligent synthesis
            
            # Collect key points from memories
            key_points = []
            for memory in group.memories[:5]:  # Top 5 by importance
                if memory.summary:
                    key_points.append(memory.summary)
                else:
                    key_points.append(memory.content[:200])
            
            # Create basic synthesis
            synthesis_parts = [
                f"Consolidation of {len(group.memories)} related memories",
                f"spanning {(group.time_span[1] - group.time_span[0]).days} days."
            ]
            
            if group.patterns:
                synthesis_parts.append(f"Patterns identified: {'; '.join(group.patterns[:3])}")
            
            if group.insights:
                synthesis_parts.append(f"Key insights: {'; '.join(group.insights[:3])}")
            
            if group.common_domains:
                synthesis_parts.append(f"Primary domains: {', '.join(group.common_domains[:3])}")
            
            synthesis_parts.append(f"Overall coherence: {group.coherence_score:.2f}")
            
            group.synthesis = " ".join(synthesis_parts)
            
            # If LLM available, generate proper synthesis
            if self.llm_service:
                prompt = f"""
                Synthesize the following {len(group.memories)} related memories into a coherent summary:
                
                Key themes: {', '.join(group.common_tags[:5])}
                Domains: {', '.join(group.common_domains)}
                Time span: {group.time_span[0].date()} to {group.time_span[1].date()}
                
                Key points:
                {chr(10).join(f'- {point}' for point in key_points)}
                
                Patterns: {', '.join(group.patterns)}
                Insights: {', '.join(group.insights)}
                
                Create a brief, coherent synthesis that captures the essence and evolution of these memories.
                """
                
                try:
                    group.synthesis = await self.llm_service.generate(prompt, max_tokens=300)
                except Exception as e:
                    logger.warning(f"LLM synthesis failed: {e}, using basic synthesis")
        
        return groups


class ConsolidatedMemoryCreationStage(
    PipelineStage[List[ConsolidationGroup], List[ConsolidatedMemory]]
):
    """Create consolidated memories from groups"""
    
    def __init__(self):
        super().__init__("consolidated_memory_creation", required=True)
    
    async def process(
        self,
        groups: List[ConsolidationGroup],
        context: Dict[str, Any]
    ) -> List[ConsolidatedMemory]:
        """Create consolidated memories"""
        consolidated = []
        
        for group in groups:
            # Calculate consolidated importance
            avg_importance = np.mean([m.importance for m in group.memories])
            # Boost importance for larger groups
            importance_boost = min(0.2, len(group.memories) * 0.02)
            final_importance = min(1.0, avg_importance + importance_boost)
            
            # Create title
            if group.common_domains:
                title = f"Consolidated insights on {', '.join(group.common_domains[:2])}"
            else:
                title = f"Consolidated memories ({group.time_span[0].date()} - {group.time_span[1].date()})"
            
            # Combine content
            content = group.synthesis or "Consolidated memory group"
            
            if group.patterns:
                content += f"\n\nPatterns:\n" + "\n".join(f"- {p}" for p in group.patterns)
            
            if group.insights:
                content += f"\n\nInsights:\n" + "\n".join(f"- {i}" for i in group.insights)
            
            # Add memory summaries
            content += f"\n\nOriginal memories ({len(group.memories)}):\n"
            for memory in group.memories[:10]:  # Limit to 10
                content += f"- [{memory.occurred_at.date()}] {memory.summary or memory.content[:100]}\n"
            
            consolidated_memory = ConsolidatedMemory(
                user_id=group.user_id,
                content=content,
                title=title,
                parent_memory_ids=[m.memory_id for m in group.memories],
                domains=group.common_domains,
                tags=group.common_tags + ['consolidated'],
                patterns=group.patterns,
                insights=group.insights,
                importance=final_importance,
                coherence_score=group.coherence_score,
                time_span=group.time_span,
                metadata={
                    'group_id': group.group_id,
                    'memory_count': len(group.memories),
                    'consolidation_date': datetime.utcnow().isoformat(),
                    'avg_access_count': np.mean([m.access_count for m in group.memories])
                }
            )
            
            consolidated.append(consolidated_memory)
        
        logger.info(f"Created {len(consolidated)} consolidated memories")
        return consolidated


class MemoryConsolidationPipeline(Pipeline[str, List[ConsolidatedMemory]]):
    """Complete memory consolidation pipeline"""
    
    def __init__(self, memory_service=None, llm_service=None):
        stages = [
            MemorySelectionStage(memory_service),
            MemoryClusteringStage(),
            PatternExtractionStage(),
            SynthesisGenerationStage(llm_service),
            ConsolidatedMemoryCreationStage()
        ]
        
        super().__init__(
            name="memory_consolidation",
            stages=stages,
            parallel=False,
            continue_on_error=False
        )
    
    async def consolidate_user_memories(
        self,
        user_id: str,
        min_age_hours: int = 24,
        max_memories: int = 100,
        min_group_size: int = 2
    ) -> List[ConsolidatedMemory]:
        """Consolidate memories for a user"""
        context = {
            'min_age_hours': min_age_hours,
            'max_memories': max_memories,
            'min_group_size': min_group_size
        }
        
        # Store context for stages
        self._context = context
        
        result = await self.execute(user_id)
        
        if result.status == 'completed' and result.data:
            return result.data
        
        logger.error(f"Consolidation failed: {result.error}")
        return []


class REMConsolidationScheduler:
    """Scheduler for REM-like consolidation cycles"""
    
    def __init__(self, consolidation_pipeline: MemoryConsolidationPipeline):
        self.pipeline = consolidation_pipeline
        self.active_cycles = {}
    
    async def schedule_consolidation(
        self,
        user_id: str,
        cycle_hours: int = 24
    ) -> None:
        """Schedule periodic consolidation for a user"""
        if user_id in self.active_cycles:
            logger.warning(f"Consolidation already scheduled for user {user_id}")
            return
        
        self.active_cycles[user_id] = True
        
        while self.active_cycles.get(user_id):
            try:
                # Run consolidation
                consolidated = await self.pipeline.consolidate_user_memories(
                    user_id=user_id,
                    min_age_hours=cycle_hours
                )
                
                logger.info(
                    f"Consolidation cycle completed for user {user_id}: "
                    f"{len(consolidated)} memories consolidated"
                )
                
                # Wait for next cycle
                await asyncio.sleep(cycle_hours * 3600)
                
            except Exception as e:
                logger.error(f"Consolidation cycle failed for user {user_id}: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    def stop_consolidation(self, user_id: str) -> None:
        """Stop consolidation cycles for a user"""
        if user_id in self.active_cycles:
            del self.active_cycles[user_id]
            logger.info(f"Stopped consolidation for user {user_id}")


# Export classes
__all__ = [
    'ConsolidationCandidate',
    'ConsolidationGroup',
    'ConsolidatedMemory',
    'MemorySelectionStage',
    'MemoryClusteringStage',
    'PatternExtractionStage',
    'SynthesisGenerationStage',
    'ConsolidatedMemoryCreationStage',
    'MemoryConsolidationPipeline',
    'REMConsolidationScheduler',
]