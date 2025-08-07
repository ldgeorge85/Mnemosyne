"""
Memory capture pipeline for Mnemosyne Protocol
Handles ingestion from various sources
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
import hashlib
from urllib.parse import urlparse

from pydantic import BaseModel, Field, validator
from .base import Pipeline, PipelineStage, TransformStage
from ..models.memory import MemoryType, MemoryStatus
from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RawMemoryInput(BaseModel):
    """Raw memory input from various sources"""
    content: str
    source: str = "chat"  # chat, web, file, api, system
    source_url: Optional[str] = None
    user_id: str
    title: Optional[str] = None
    occurred_at: Optional[datetime] = None
    memory_type: MemoryType = MemoryType.CONVERSATION
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    domains: List[str] = Field(default_factory=list)
    importance: Optional[float] = None
    parent_memory_id: Optional[str] = None
    
    @validator('occurred_at', pre=True, always=True)
    def set_occurred_at(cls, v):
        return v or datetime.utcnow()
    
    @validator('importance')
    def validate_importance(cls, v):
        if v is not None:
            return max(0.0, min(1.0, v))
        return v


class ProcessedMemory(BaseModel):
    """Processed memory ready for storage"""
    user_id: str
    content: str
    content_hash: str
    summary: Optional[str] = None
    title: Optional[str] = None
    memory_type: MemoryType
    status: MemoryStatus = MemoryStatus.PENDING
    source: str
    source_url: Optional[str] = None
    source_metadata: Dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    domains: List[str] = Field(default_factory=list)
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    importance: float = 0.5
    relevance: float = 0.5
    emotional_valence: float = 0.0
    confidence: float = 0.8
    parent_memory_id: Optional[str] = None
    is_private: bool = True
    sharing_level: int = 0


class ValidationStage(PipelineStage[RawMemoryInput, RawMemoryInput]):
    """Validate and sanitize input"""
    
    def __init__(self):
        super().__init__("validation", required=True)
    
    async def validate(self, data: RawMemoryInput) -> bool:
        """Validate memory input"""
        # Check content length
        if not data.content or len(data.content.strip()) < 3:
            return False
        
        if len(data.content) > 100000:  # 100KB limit
            return False
        
        # Validate user_id format (UUID)
        try:
            import uuid
            uuid.UUID(data.user_id)
        except ValueError:
            return False
        
        return True
    
    async def process(self, data: RawMemoryInput, context: Dict[str, Any]) -> RawMemoryInput:
        """Sanitize input data"""
        # Strip whitespace
        data.content = data.content.strip()
        
        # Clean tags and domains
        data.tags = [tag.lower().strip() for tag in data.tags if tag.strip()]
        data.domains = [domain.lower().strip() for domain in data.domains if domain.strip()]
        
        # Remove duplicates
        data.tags = list(set(data.tags))
        data.domains = list(set(data.domains))
        
        # Validate URL if present
        if data.source_url:
            try:
                parsed = urlparse(data.source_url)
                if not parsed.scheme:
                    data.source_url = f"https://{data.source_url}"
            except Exception:
                data.source_url = None
        
        return data


class DeduplicationStage(PipelineStage[RawMemoryInput, RawMemoryInput]):
    """Check for duplicate memories"""
    
    def __init__(self):
        super().__init__("deduplication", required=False)
    
    async def process(self, data: RawMemoryInput, context: Dict[str, Any]) -> RawMemoryInput:
        """Generate content hash for deduplication"""
        # Create hash of content for deduplication
        content_hash = hashlib.sha256(
            f"{data.user_id}:{data.content}".encode()
        ).hexdigest()
        
        # Store in context for later use
        context['content_hash'] = content_hash
        
        # TODO: Check against database for existing hash
        # For now, just add hash to metadata
        data.metadata['content_hash'] = content_hash
        
        return data


class MetadataExtractionStage(PipelineStage[RawMemoryInput, RawMemoryInput]):
    """Extract metadata from content"""
    
    def __init__(self):
        super().__init__("metadata_extraction", required=False)
    
    async def process(self, data: RawMemoryInput, context: Dict[str, Any]) -> RawMemoryInput:
        """Extract metadata from content"""
        content = data.content.lower()
        
        # Extract potential domains from content
        domain_keywords = {
            'technology': ['code', 'programming', 'software', 'api', 'database'],
            'philosophy': ['meaning', 'existence', 'consciousness', 'truth', 'reality'],
            'psychology': ['mind', 'behavior', 'emotion', 'feeling', 'think'],
            'science': ['research', 'experiment', 'hypothesis', 'data', 'analysis'],
            'art': ['creative', 'design', 'aesthetic', 'beauty', 'expression'],
            'business': ['market', 'strategy', 'revenue', 'customer', 'product'],
            'health': ['wellness', 'medical', 'treatment', 'diagnosis', 'symptom'],
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in content for keyword in keywords):
                if domain not in data.domains:
                    data.domains.append(domain)
        
        # Extract URLs from content
        import re
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, data.content)
        if urls:
            data.metadata['extracted_urls'] = urls[:10]  # Limit to 10 URLs
        
        # Extract potential entities (simplified - in production use NER)
        # Look for capitalized words that might be names
        words = data.content.split()
        potential_entities = []
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 2:
                # Check if it's potentially a name (next word is also capitalized)
                if i < len(words) - 1 and words[i + 1][0].isupper():
                    potential_entities.append(f"{word} {words[i + 1]}")
        
        if potential_entities:
            data.metadata['potential_entities'] = list(set(potential_entities[:10]))
        
        # Detect questions
        if '?' in data.content:
            data.tags.append('question')
            data.metadata['contains_questions'] = True
        
        # Detect code blocks
        if '```' in data.content or 'def ' in data.content or 'function ' in data.content:
            data.tags.append('code')
            data.domains.append('technology')
        
        # Calculate initial importance based on content characteristics
        importance_factors = 0.5  # Base importance
        
        # Boost for questions
        if 'question' in data.tags:
            importance_factors += 0.1
        
        # Boost for longer content (more substantial)
        if len(data.content) > 500:
            importance_factors += 0.1
        
        # Boost for explicit markers
        important_markers = ['important', 'critical', 'urgent', 'remember', 'todo', 'task']
        if any(marker in content for marker in important_markers):
            importance_factors += 0.2
            data.tags.append('important')
        
        # Set importance if not already set
        if data.importance is None:
            data.importance = min(1.0, importance_factors)
        
        return data


class EmotionalAnalysisStage(PipelineStage[RawMemoryInput, RawMemoryInput]):
    """Analyze emotional content"""
    
    def __init__(self):
        super().__init__("emotional_analysis", required=False)
    
    async def process(self, data: RawMemoryInput, context: Dict[str, Any]) -> RawMemoryInput:
        """Simple emotional valence analysis"""
        content = data.content.lower()
        
        # Positive indicators
        positive_words = [
            'happy', 'joy', 'love', 'excellent', 'wonderful', 'amazing',
            'fantastic', 'great', 'good', 'success', 'achieve', 'win',
            'beautiful', 'perfect', 'brilliant', 'excited', 'grateful'
        ]
        
        # Negative indicators
        negative_words = [
            'sad', 'angry', 'hate', 'terrible', 'awful', 'horrible',
            'bad', 'fail', 'loss', 'pain', 'hurt', 'difficult',
            'problem', 'issue', 'error', 'wrong', 'mistake', 'crisis'
        ]
        
        positive_count = sum(1 for word in positive_words if word in content)
        negative_count = sum(1 for word in negative_words if word in content)
        
        # Calculate valence (-1 to 1)
        if positive_count + negative_count > 0:
            valence = (positive_count - negative_count) / (positive_count + negative_count)
        else:
            valence = 0.0
        
        # Store in metadata
        data.metadata['emotional_valence'] = valence
        data.metadata['emotional_indicators'] = {
            'positive': positive_count,
            'negative': negative_count
        }
        
        # Add emotion tags
        if valence > 0.3:
            data.tags.append('positive')
        elif valence < -0.3:
            data.tags.append('negative')
        
        return data


class SummarizationStage(PipelineStage[RawMemoryInput, ProcessedMemory]):
    """Generate summary and title"""
    
    def __init__(self):
        super().__init__("summarization", required=False)
    
    async def process(self, data: RawMemoryInput, context: Dict[str, Any]) -> ProcessedMemory:
        """Create processed memory with summary"""
        # Simple summarization - take first 200 chars or first paragraph
        summary = None
        if len(data.content) > 200:
            # Try to find first paragraph
            paragraphs = data.content.split('\n\n')
            if paragraphs:
                summary = paragraphs[0][:500]
            else:
                summary = data.content[:200] + "..."
        
        # Generate title if not provided
        title = data.title
        if not title:
            # Take first line or first 50 chars
            lines = data.content.split('\n')
            if lines:
                title = lines[0][:100]
            else:
                title = data.content[:50]
        
        # Create processed memory
        processed = ProcessedMemory(
            user_id=data.user_id,
            content=data.content,
            content_hash=context.get('content_hash', ''),
            summary=summary,
            title=title,
            memory_type=data.memory_type,
            status=MemoryStatus.PENDING,
            source=data.source,
            source_url=data.source_url,
            source_metadata=data.metadata.get('source_metadata', {}),
            occurred_at=data.occurred_at,
            metadata=data.metadata,
            tags=data.tags,
            domains=data.domains,
            entities=data.metadata.get('potential_entities', []),
            importance=data.importance or 0.5,
            relevance=0.5,  # Will be calculated based on context
            emotional_valence=data.metadata.get('emotional_valence', 0.0),
            confidence=0.8,  # Default confidence
            parent_memory_id=data.parent_memory_id,
            is_private=True,
            sharing_level=0
        )
        
        return processed


class MemoryCapturePipeline(Pipeline[RawMemoryInput, ProcessedMemory]):
    """Complete memory capture pipeline"""
    
    def __init__(self):
        super().__init__(
            name="memory_capture",
            stages=[
                ValidationStage(),
                DeduplicationStage(),
                MetadataExtractionStage(),
                EmotionalAnalysisStage(),
                SummarizationStage()
            ],
            parallel=False,
            continue_on_error=False
        )
    
    async def capture_batch(
        self,
        memories: List[RawMemoryInput],
        max_concurrent: int = 10
    ) -> List[ProcessedMemory]:
        """Capture multiple memories concurrently"""
        results = await self.execute_batch(memories, max_concurrent)
        
        processed = []
        for result in results:
            if result.status in ['completed', 'partial'] and result.data:
                processed.append(result.data)
            else:
                logger.warning(f"Failed to capture memory: {result.error}")
        
        return processed


class WebMemoryCapture(Pipeline[Dict[str, Any], ProcessedMemory]):
    """Specialized pipeline for web content"""
    
    def __init__(self):
        # Add web-specific stages
        web_extraction = TransformStage(
            "web_extraction",
            self.extract_web_content
        )
        
        super().__init__(
            name="web_memory_capture",
            stages=[web_extraction],
            parallel=False
        )
        
        # Add standard capture pipeline
        self.capture_pipeline = MemoryCapturePipeline()
    
    async def extract_web_content(self, data: Dict[str, Any]) -> RawMemoryInput:
        """Extract content from web data"""
        # Extract main content from HTML or parsed data
        content = data.get('content', '')
        url = data.get('url', '')
        title = data.get('title', '')
        
        # Create raw memory input
        return RawMemoryInput(
            content=content,
            source='web',
            source_url=url,
            user_id=data['user_id'],
            title=title,
            memory_type=MemoryType.EXTERNAL,
            metadata={
                'web_metadata': {
                    'url': url,
                    'title': title,
                    'extracted_at': datetime.utcnow().isoformat()
                }
            },
            tags=['web', 'external'],
            domains=data.get('domains', [])
        )
    
    async def execute(self, data: Dict[str, Any]) -> ProcessedMemory:
        """Execute web capture pipeline"""
        # First extract web content
        web_result = await super().execute(data)
        
        if web_result.status == 'completed' and web_result.data:
            # Then run through standard capture
            capture_result = await self.capture_pipeline.execute(web_result.data)
            return capture_result.data if capture_result.data else None
        
        return None


# Export classes and pipelines
__all__ = [
    'RawMemoryInput',
    'ProcessedMemory',
    'ValidationStage',
    'DeduplicationStage',
    'MetadataExtractionStage',
    'EmotionalAnalysisStage',
    'SummarizationStage',
    'MemoryCapturePipeline',
    'WebMemoryCapture',
]