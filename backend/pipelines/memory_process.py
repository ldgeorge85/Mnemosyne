"""
Memory processing pipeline stages for Mnemosyne Protocol
Advanced processing including embedding, importance calculation, and storage
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np

from .base import Pipeline, PipelineStage
from .memory_capture import ProcessedMemory
from models.memory import Memory, MemoryStatus
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class MemoryWithEmbeddings(ProcessedMemory):
    """Memory with computed embeddings"""
    embedding_content: Optional[List[float]] = None
    embedding_semantic: Optional[List[float]] = None
    embedding_contextual: Optional[List[float]] = None
    similar_memory_ids: List[str] = []
    consolidation_candidates: List[str] = []


class EmbeddingStage(PipelineStage[ProcessedMemory, MemoryWithEmbeddings]):
    """Generate embeddings for memory"""
    
    def __init__(self, embedding_service=None):
        super().__init__("embedding_generation", required=True)
        self.embedding_service = embedding_service  # Will be injected
    
    async def process(self, data: ProcessedMemory, context: Dict[str, Any]) -> MemoryWithEmbeddings:
        """Generate multi-embeddings for memory"""
        # Create enhanced memory object
        memory_with_embeddings = MemoryWithEmbeddings(**data.dict())
        
        # Generate embeddings (placeholder - actual implementation in embedding service)
        # In production, this would call the embedding service
        if self.embedding_service:
            # Generate content embedding (OpenAI/primary model)
            memory_with_embeddings.embedding_content = await self.embedding_service.generate_embedding(
                data.content,
                model='content'
            )
            
            # Generate semantic embedding (local model for semantic similarity)
            memory_with_embeddings.embedding_semantic = await self.embedding_service.generate_embedding(
                data.content,
                model='semantic'
            )
            
            # Generate contextual embedding (smaller, context-focused)
            context_text = f"{' '.join(data.tags)} {' '.join(data.domains)} {data.summary or ''}"
            memory_with_embeddings.embedding_contextual = await self.embedding_service.generate_embedding(
                context_text,
                model='contextual'
            )
        else:
            # Dummy embeddings for testing
            memory_with_embeddings.embedding_content = [0.1] * 1536
            memory_with_embeddings.embedding_semantic = [0.2] * 768
            memory_with_embeddings.embedding_contextual = [0.3] * 384
        
        # Store embeddings in context for similarity search
        context['embeddings'] = {
            'content': memory_with_embeddings.embedding_content,
            'semantic': memory_with_embeddings.embedding_semantic,
            'contextual': memory_with_embeddings.embedding_contextual
        }
        
        return memory_with_embeddings


class SimilaritySearchStage(PipelineStage[MemoryWithEmbeddings, MemoryWithEmbeddings]):
    """Find similar memories for context and deduplication"""
    
    def __init__(self, search_service=None):
        super().__init__("similarity_search", required=False)
        self.search_service = search_service  # Will be injected
    
    async def process(self, data: MemoryWithEmbeddings, context: Dict[str, Any]) -> MemoryWithEmbeddings:
        """Search for similar memories"""
        if not self.search_service:
            return data
        
        # Search for similar memories using embeddings
        embeddings = context.get('embeddings', {})
        
        if embeddings.get('content'):
            similar_memories = await self.search_service.search_similar(
                user_id=data.user_id,
                embedding=embeddings['content'],
                limit=10,
                threshold=0.8
            )
            
            # Extract IDs of similar memories
            data.similar_memory_ids = [m['id'] for m in similar_memories]
            
            # Check for potential duplicates (very high similarity)
            duplicates = [m for m in similar_memories if m.get('score', 0) > 0.95]
            if duplicates:
                context['potential_duplicates'] = duplicates
                logger.warning(f"Found {len(duplicates)} potential duplicate memories")
            
            # Find consolidation candidates (moderate similarity)
            consolidation_candidates = [
                m for m in similar_memories 
                if 0.7 < m.get('score', 0) < 0.95
            ]
            data.consolidation_candidates = [m['id'] for m in consolidation_candidates]
        
        return data


class ImportanceCalculationStage(PipelineStage[MemoryWithEmbeddings, MemoryWithEmbeddings]):
    """Calculate dynamic importance score"""
    
    def __init__(self):
        super().__init__("importance_calculation", required=False)
    
    async def process(self, data: MemoryWithEmbeddings, context: Dict[str, Any]) -> MemoryWithEmbeddings:
        """Calculate importance based on various factors"""
        importance = data.importance  # Start with initial importance
        
        # Factor 1: Content length (longer = more substantial)
        content_length = len(data.content)
        if content_length > 1000:
            importance += 0.1
        elif content_length < 100:
            importance -= 0.1
        
        # Factor 2: Number of domains (interdisciplinary = important)
        if len(data.domains) >= 3:
            importance += 0.15
        
        # Factor 3: Emotional intensity
        emotional_intensity = abs(data.emotional_valence)
        if emotional_intensity > 0.5:
            importance += emotional_intensity * 0.2
        
        # Factor 4: Tags indicating importance
        important_tags = {'important', 'critical', 'urgent', 'remember', 'milestone'}
        if any(tag in important_tags for tag in data.tags):
            importance += 0.2
        
        # Factor 5: Questions (learning moments)
        if 'question' in data.tags:
            importance += 0.1
        
        # Factor 6: Code or technical content
        if 'code' in data.tags or 'technology' in data.domains:
            importance += 0.05
        
        # Factor 7: Time-based (recent = slightly more important)
        hours_old = (datetime.utcnow() - data.occurred_at).total_seconds() / 3600
        if hours_old < 1:
            importance += 0.05
        elif hours_old > 168:  # Older than a week
            importance -= 0.05
        
        # Factor 8: Relationships (has parent or similar memories)
        if data.parent_memory_id:
            importance += 0.05
        if len(data.similar_memory_ids) > 3:
            importance += 0.05
        
        # Normalize to 0-1 range
        data.importance = max(0.0, min(1.0, importance))
        
        # Calculate relevance (simplified - would use user context in production)
        data.relevance = data.importance * 0.7 + emotional_intensity * 0.3
        
        # Adjust confidence based on completeness
        confidence = 0.8
        if data.summary:
            confidence += 0.05
        if data.title:
            confidence += 0.05
        if len(data.tags) > 3:
            confidence += 0.05
        if len(data.domains) > 0:
            confidence += 0.05
        
        data.confidence = min(1.0, confidence)
        
        return data


class PrivacyAssessmentStage(PipelineStage[MemoryWithEmbeddings, MemoryWithEmbeddings]):
    """Assess privacy level and sharing potential"""
    
    def __init__(self):
        super().__init__("privacy_assessment", required=False)
    
    async def process(self, data: MemoryWithEmbeddings, context: Dict[str, Any]) -> MemoryWithEmbeddings:
        """Determine privacy and sharing levels"""
        # Default to private
        data.is_private = True
        data.sharing_level = 0
        
        content_lower = data.content.lower()
        
        # Check for sensitive content markers
        sensitive_markers = [
            'password', 'secret', 'private', 'confidential',
            'personal', 'sensitive', 'api key', 'token'
        ]
        
        if any(marker in content_lower for marker in sensitive_markers):
            data.is_private = True
            data.sharing_level = 0
            data.tags.append('sensitive')
            return data
        
        # Check for shareable content
        shareable_markers = [
            'public', 'share', 'blog', 'article', 'tutorial',
            'guide', 'documentation', 'reference'
        ]
        
        if any(marker in content_lower for marker in shareable_markers):
            data.sharing_level = 2  # Moderate sharing
        
        # Technical content might be shareable
        if 'technology' in data.domains or 'code' in data.tags:
            data.sharing_level = max(data.sharing_level, 1)
        
        # Philosophy and ideas might be shareable
        if 'philosophy' in data.domains or 'idea' in data.tags:
            data.sharing_level = max(data.sharing_level, 2)
        
        # Questions are often shareable
        if 'question' in data.tags:
            data.sharing_level = max(data.sharing_level, 1)
        
        # High importance might be worth sharing
        if data.importance > 0.7:
            data.sharing_level = max(data.sharing_level, 1)
        
        return data


class DriftDetectionStage(PipelineStage[MemoryWithEmbeddings, MemoryWithEmbeddings]):
    """Detect semantic drift from previous memories"""
    
    def __init__(self):
        super().__init__("drift_detection", required=False)
    
    async def process(self, data: MemoryWithEmbeddings, context: Dict[str, Any]) -> MemoryWithEmbeddings:
        """Calculate drift from similar memories"""
        if not data.similar_memory_ids:
            data.metadata['drift_index'] = 0.0
            return data
        
        # In production, would fetch similar memories and compare
        # For now, simulate drift calculation
        similar_memories = context.get('similar_memories', [])
        
        if similar_memories:
            # Calculate average semantic distance
            # This is simplified - real implementation would use embeddings
            drift_scores = []
            for memory in similar_memories:
                # Simulate cosine distance
                drift = np.random.uniform(0, 0.5)  # Placeholder
                drift_scores.append(drift)
            
            avg_drift = np.mean(drift_scores) if drift_scores else 0.0
        else:
            # No similar memories = potentially new topic = higher drift
            avg_drift = 0.7
        
        data.metadata['drift_index'] = float(avg_drift)
        
        # High drift might indicate:
        # - New topic/domain
        # - Changed perspective
        # - Evolving understanding
        if avg_drift > 0.6:
            data.tags.append('high_drift')
            data.metadata['drift_indicators'] = ['potential_new_topic']
        
        return data


class StoragePreparationStage(PipelineStage[MemoryWithEmbeddings, Dict[str, Any]]):
    """Prepare memory for storage in database and vector store"""
    
    def __init__(self):
        super().__init__("storage_preparation", required=True)
    
    async def process(self, data: MemoryWithEmbeddings, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare for storage"""
        # Prepare database record
        db_record = {
            'user_id': data.user_id,
            'content': data.content,
            'summary': data.summary,
            'title': data.title,
            'memory_type': data.memory_type,
            'status': MemoryStatus.PROCESSED,
            'source': data.source,
            'source_url': data.source_url,
            'source_metadata': data.source_metadata,
            'occurred_at': data.occurred_at,
            'metadata': data.metadata,
            'tags': data.tags,
            'domains': data.domains,
            'entities': data.entities,
            'importance': data.importance,
            'relevance': data.relevance,
            'emotional_valence': data.emotional_valence,
            'confidence': data.confidence,
            'drift_index': data.metadata.get('drift_index', 0.0),
            'parent_memory_id': data.parent_memory_id,
            'is_private': data.is_private,
            'sharing_level': data.sharing_level,
            'consolidation_count': 0,
            'access_count': 0
        }
        
        # Prepare vector store record
        vector_record = {
            'content': data.content,
            'summary': data.summary or data.content[:200],
            'memory_type': data.memory_type.value,
            'importance': data.importance,
            'domains': data.domains,
            'tags': data.tags,
            'occurred_at': data.occurred_at.isoformat(),
            'metadata': data.metadata,
            'embeddings': {
                'content': data.embedding_content,
                'semantic': data.embedding_semantic,
                'contextual': data.embedding_contextual
            }
        }
        
        return {
            'db_record': db_record,
            'vector_record': vector_record,
            'similar_memory_ids': data.similar_memory_ids,
            'consolidation_candidates': data.consolidation_candidates,
            'content_hash': data.content_hash
        }


class MemoryProcessingPipeline(Pipeline[ProcessedMemory, Dict[str, Any]]):
    """Complete memory processing pipeline"""
    
    def __init__(self, embedding_service=None, search_service=None):
        stages = [
            EmbeddingStage(embedding_service),
            SimilaritySearchStage(search_service),
            ImportanceCalculationStage(),
            PrivacyAssessmentStage(),
            DriftDetectionStage(),
            StoragePreparationStage()
        ]
        
        super().__init__(
            name="memory_processing",
            stages=stages,
            parallel=False,
            continue_on_error=False
        )
    
    async def process_batch(
        self,
        memories: List[ProcessedMemory],
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """Process multiple memories with concurrency control"""
        results = await self.execute_batch(memories, max_concurrent)
        
        processed = []
        for result in results:
            if result.status in ['completed', 'partial'] and result.data:
                processed.append(result.data)
            else:
                logger.error(f"Failed to process memory: {result.error}")
        
        return processed


class AsyncMemoryProcessor:
    """High-level async memory processor"""
    
    def __init__(self, embedding_service=None, search_service=None):
        self.pipeline = MemoryProcessingPipeline(embedding_service, search_service)
    
    async def process_memory(self, memory: ProcessedMemory) -> Optional[Dict[str, Any]]:
        """Process a single memory"""
        result = await self.pipeline.execute(memory)
        
        if result.status == 'completed' and result.data:
            return result.data
        
        logger.error(f"Memory processing failed: {result.error}")
        return None
    
    async def process_memories(
        self,
        memories: List[ProcessedMemory],
        batch_size: int = 10
    ) -> List[Dict[str, Any]]:
        """Process memories in batches"""
        all_processed = []
        
        for i in range(0, len(memories), batch_size):
            batch = memories[i:i + batch_size]
            processed = await self.pipeline.process_batch(batch)
            all_processed.extend(processed)
            
            # Small delay between batches to prevent overload
            if i + batch_size < len(memories):
                await asyncio.sleep(0.1)
        
        return all_processed


# Export classes
__all__ = [
    'MemoryWithEmbeddings',
    'EmbeddingStage',
    'SimilaritySearchStage',
    'ImportanceCalculationStage',
    'PrivacyAssessmentStage',
    'DriftDetectionStage',
    'StoragePreparationStage',
    'MemoryProcessingPipeline',
    'AsyncMemoryProcessor',
]