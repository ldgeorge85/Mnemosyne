# Implementation Guide - Dual-Track Architecture

## Building the Mnemosyne Protocol

This guide walks through implementing the dual-track protocol, separating proven Track 1 features from experimental Track 2 research.

---

## Core Philosophy

**Build Real or Defer** - No mocking, no fake implementations. Every feature either works completely or is explicitly deferred.

**Dual-Track Separation**:
- **Track 1**: W3C DIDs, OAuth 2.0, MLS Protocol, proven AI techniques
- **Track 2**: Identity compression, behavioral tracking, symbolic resonance (with hypothesis docs)

---

## Critical Path

### Track 1 (Production) Path:
```
1. W3C DID System → 2. OAuth/WebAuthn → 3. MLS Sharing → 4. Standard Agents
```

### Track 2 (Research) Path:
```
1. Hypothesis Docs → 2. Consent System → 3. Metrics Collection → 4. Validation
```

---

## Phase 1: Personal Memory System (Days 1-3)

### Step 1: Dual-Track Configuration

```python
# core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
from enum import Enum

class TrackMode(str, Enum):
    PRODUCTION = "production"
    RESEARCH = "research"

class Settings(BaseSettings):
    # Track Configuration
    track: TrackMode = TrackMode.PRODUCTION
    experimental_features: bool = False
    consent_required: bool = False
    
    # Core Infrastructure
    database_url: str
    redis_url: str = "redis://redis:6379/0"
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    
    # Authentication (Track 1)
    oauth_client_id: str = ""
    oauth_client_secret: str = ""
    w3c_did_enabled: bool = True
    w3c_did_method: str = "mnem"
    
    # AI Providers
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    
    # Security & Compliance
    encryption_key: str
    eu_ai_act_compliance: bool = True
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
```

### Step 2: Database Setup with Async SQLAlchemy

```python
# models/memory.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import String, Text, JSON, Float, DateTime
import uuid

Base = declarative_base()

class Memory(Base):
    __tablename__ = 'memories'
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    importance: Mapped[float] = mapped_column(Float, default=0.5)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    @classmethod
    async def create(cls, session: AsyncSession, **kwargs):
        memory = cls(**kwargs)
        session.add(memory)
        await session.commit()
        return memory
```

### Step 3: Vector Storage with Track Separation

```python
# core/vectors.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from core.features import FeatureFlags

class VectorStore:
    def __init__(self):
        settings = get_settings()
        self.settings = settings
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port
        )
        self.collection_name = "memories"
        
    async def init_collection(self):
        vectors_config = {
            "content": VectorParams(size=1536, distance=Distance.COSINE),  # Track 1
        }
        
        # Track 2: Additional experimental embeddings
        if self.settings.track == TrackMode.RESEARCH and FeatureFlags.is_enabled("experimental.multi_embedding"):
            vectors_config["semantic"] = VectorParams(size=768, distance=Distance.COSINE)
            vectors_config["behavioral"] = VectorParams(size=384, distance=Distance.COSINE)
        
        await self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=vectors_config
            }
        )
    
    async def store_memory(self, memory_id: str, embeddings: dict, metadata: dict):
        point = PointStruct(
            id=memory_id,
            vector=embeddings,
            payload=metadata
        )
        await self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )
```

### Step 4: Memory Capture Pipeline

```python
# pipelines/memory.py
from abc import ABC, abstractmethod
import asyncio
from typing import Dict, Any, List

class MemoryPipeline(ABC):
    """Base pipeline for async memory processing with track awareness"""
    
    def __init__(self):
        self.settings = get_settings()
        self.vector_store = VectorStore()
        self.track = self.settings.track
        
    @abstractmethod
    async def process(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    def require_consent(self, feature: str) -> bool:
        """Check if experimental feature requires consent"""
        return (
            self.track == TrackMode.RESEARCH and 
            FeatureFlags.is_experimental(feature)
        )
    
    async def run(self, memories: List[Dict]):
        """Process multiple memories concurrently"""
        tasks = [self.process(m) for m in memories]
        return await asyncio.gather(*tasks, return_exceptions=True)

class CaptureMemoryPipeline(MemoryPipeline):
    async def process(self, content: Dict[str, Any]) -> Dict[str, Any]:
        # Concurrent processing stages
        embedding_task = self.generate_embedding(content['text'])
        metadata_task = self.extract_metadata(content)
        
        embedding, metadata = await asyncio.gather(embedding_task, metadata_task)
        
        # Calculate importance
        importance = await self.calculate_importance(content, metadata)
        
        # Store in database and vector store
        memory = await self.store_memory({
            'content': content,
            'embedding': embedding,
            'metadata': metadata,
            'importance': importance
        })
        
        return memory

# services/memory_service.py
class MemoryService:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.embedder = openai.Embedding()
    
    async def capture(self, content: str, metadata: Dict[str, Any] = None) -> Memory:
        # Generate embedding
        embedding = await self.generate_embedding(content)
        
        # Extract domains and entities
        extracted = await self.extract_metadata(content)
        
        # Create memory
        memory = Memory(
            user_id=self.user_id,
            content=content,
            embedding=embedding,
            metadata={**extracted, **(metadata or {})},
            importance=self.calculate_importance(content)
        )
        
        # Store
        await self.store(memory)
        
        return memory
    
    async def generate_embedding(self, text: str) -> np.ndarray:
        response = await openai.Embedding.create(
            model="text-embedding-ada-002",
            input=text
        )
        return np.array(response['data'][0]['embedding'])
    
    def calculate_importance(self, content: str) -> float:
        # Simple heuristic - can be replaced with ML model
        factors = {
            'length': min(len(content) / 1000, 1.0) * 0.3,
            'questions': content.count('?') * 0.1,
            'personal': ('I' in content) * 0.2,
            'technical': any(term in content.lower() 
                for term in ['code', 'system', 'design']) * 0.2
        }
        return min(sum(factors.values()) + 0.3, 1.0)
```

### Step 3: Vector Search

```python
# services/search_service.py
from typing import List
import numpy as np

class SearchService:
    def __init__(self, memory_service: MemoryService):
        self.memory_service = memory_service
    
    async def search(self, query: str, limit: int = 10) -> List[Memory]:
        # Generate query embedding
        query_embedding = await self.memory_service.generate_embedding(query)
        
        # Vector similarity search using pgvector
        results = await self.db.execute(
            """
            SELECT *, 
                   embedding <=> %s::vector as distance
            FROM memories
            WHERE user_id = %s
            ORDER BY distance
            LIMIT %s
            """,
            (query_embedding.tolist(), self.user_id, limit)
        )
        
        return [Memory(**r) for r in results]
    
    async def search_by_domain(self, domain: str) -> List[Memory]:
        results = await self.db.execute(
            """
            SELECT *
            FROM memories
            WHERE user_id = %s
              AND metadata->>'domains' @> %s
            ORDER BY importance DESC
            """,
            (self.user_id, f'["{domain}"]')
        )
        
        return [Memory(**r) for r in results]
```

---

## Phase 2: Agent Orchestra (Days 4-7)

### Step 1: Base Agent Architecture

```python
# agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any
import asyncio

class BaseAgent(ABC):
    def __init__(self, name: str, model: str = "gpt-4"):
        self.name = name
        self.model = model
        self.system_prompt = self.get_system_prompt()
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        pass
    
    async def reflect(self, memory: Memory) -> Dict[str, Any]:
        prompt = f"""
        {self.system_prompt}
        
        Memory: {memory.content}
        Metadata: {memory.metadata}
        
        Provide your reflection:
        """
        
        response = await self.llm_call(prompt)
        
        return {
            'agent': self.name,
            'reflection': response,
            'confidence': self.calculate_confidence(response),
            'timestamp': datetime.now()
        }
    
    async def llm_call(self, prompt: str) -> str:
        # Implement OpenAI/Anthropic/Ollama call
        pass
```

### Step 2: Core Agents

```python
# agents/engineer.py
class EngineerAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """
        You are the Engineer, a technical architect who sees systems and patterns.
        You analyze memories for:
        - Technical insights and connections
        - System design implications  
        - Implementation possibilities
        - Security and privacy considerations
        
        Be precise, practical, and solution-oriented.
        """

# agents/librarian.py  
class LibrarianAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """
        You are the Librarian, keeper of knowledge and connections.
        You analyze memories for:
        - Connections to existing knowledge
        - Categorization and organization
        - Missing information or gaps
        - Relevant references and sources
        
        Be thorough, organized, and cross-referential.
        """

# agents/philosopher.py
class PhilosopherAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """
        You are the Philosopher, seeker of meaning and wisdom.
        You analyze memories for:
        - Deeper meanings and implications
        - Philosophical connections
        - Ethical considerations
        - Existential themes
        
        Be thoughtful, questioning, and profound.
        """
```

### Step 3: Meta-Agent (Mycelium)

```python
# agents/mycelium.py
class MyceliumAgent(BaseAgent):
    def __init__(self, agents: List[BaseAgent]):
        super().__init__("Mycelium")
        self.agents = agents
    
    async def orchestrate(self, memory: Memory) -> Dict[str, Any]:
        # Get reflections from all agents
        reflections = await asyncio.gather(
            *[agent.reflect(memory) for agent in self.agents]
        )
        
        # Analyze coherence
        coherence = self.analyze_coherence(reflections)
        
        # Generate synthesis
        synthesis = await self.synthesize(reflections)
        
        return {
            'reflections': reflections,
            'coherence': coherence,
            'synthesis': synthesis,
            'fracture_index': self.calculate_fracture(reflections)
        }
    
    def calculate_fracture(self, reflections: List[Dict]) -> float:
        # Measure disagreement between agents
        # 0.0 = complete agreement, 1.0 = complete disagreement
        pass
```

---

## Phase 3: Deep Signal Protocol (Days 8-11)

### Step 1: Signal Generation

```python
# services/signal_service.py
from typing import List, Dict
import json
import hashlib

class SignalService:
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    async def generate_signal(self) -> Dict:
        # Analyze user's memories
        memories = await self.get_recent_memories(limit=100)
        
        # Extract patterns
        domains = self.extract_domains(memories)
        personality = await self.analyze_personality(memories)
        coherence = await self.calculate_coherence(memories)
        
        # Generate glyphs based on patterns
        glyphs = self.generate_glyphs(domains, personality)
        
        # Create signal
        signal = {
            'version': '2.1',
            'sigil': self.generate_sigil(self.user_id),
            'domains': domains[:5],  # Top 5 domains
            'personality': personality,
            'coherence': coherence,
            'glyphs': glyphs,
            'flags': {
                'seeking': [],
                'offering': [],
                'crisis_mode': False,
                'intended_silence': False
            },
            'visibility': 0.3,
            'timestamp': datetime.now().isoformat()
        }
        
        # Sign signal
        signal['signature'] = self.sign_signal(signal)
        
        return signal
    
    def generate_sigil(self, user_id: str) -> str:
        # Generate unique symbol from user ID
        symbols = '⊕⊗⊙◈◊◉▲▼◆◇'
        hash_val = int(hashlib.sha256(user_id.encode()).hexdigest()[:8], 16)
        return symbols[hash_val % len(symbols)]
    
    def generate_glyphs(self, domains: List[str], personality: Dict) -> List[str]:
        # Map domains and personality to symbolic representation
        glyph_map = {
            'technical': '⚙',
            'philosophical': '∴',
            'creative': '✧',
            'analytical': '◈',
            'social': '◉'
        }
        
        glyphs = []
        for domain in domains[:3]:
            if domain in glyph_map:
                glyphs.append(glyph_map[domain])
        
        return glyphs
```

### Step 2: Kartouche Visualization

```python
# services/kartouche_service.py
import svgwrite

class KartoucheService:
    def generate_kartouche(self, signal: Dict) -> str:
        # Create SVG
        dwg = svgwrite.Drawing(size=('200px', '100px'))
        
        # Add border
        dwg.add(dwg.rect(
            insert=(5, 5), 
            size=(190, 90),
            fill='none',
            stroke='#333',
            stroke_width=2
        ))
        
        # Add sigil
        dwg.add(dwg.text(
            signal['sigil'],
            insert=(100, 30),
            font_size='24px',
            text_anchor='middle'
        ))
        
        # Add glyphs
        for i, glyph in enumerate(signal['glyphs']):
            dwg.add(dwg.text(
                glyph,
                insert=(50 + i*50, 60),
                font_size='16px'
            ))
        
        # Add fracture visualization
        fracture = signal['coherence']['fracture_index']
        dwg.add(dwg.line(
            start=(20, 80),
            end=(180 * (1 - fracture), 80),
            stroke='green' if fracture < 0.5 else 'orange',
            stroke_width=3
        ))
        
        return dwg.tostring()
```

---

## Phase 4: Collective Intelligence (Days 12-14)

### Step 1: Sharing Contracts

```python
# models/sharing_contract.py
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Literal

@dataclass
class SharingContract:
    id: str
    user_id: str
    collective_id: str
    domains: List[str]
    depth: Literal['summary', 'detailed', 'full']
    duration: timedelta
    revocable: bool = True
    anonymous: bool = False
    k_anonymity: int = 3
    created_at: datetime = None
    expires_at: datetime = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now()
        if not self.expires_at:
            self.expires_at = self.created_at + self.duration
    
    def is_valid(self) -> bool:
        return datetime.now() < self.expires_at
    
    def matches_memory(self, memory: Memory) -> bool:
        # Check if memory matches contract domains
        memory_domains = memory.metadata.get('domains', [])
        return any(d in memory_domains for d in self.domains)
```

### Step 2: Collective Service

```python
# services/collective_service.py
class CollectiveService:
    def __init__(self, collective_id: str):
        self.collective_id = collective_id
        self.k_anonymity_threshold = 3
    
    async def share_memory(
        self, 
        memory: Memory, 
        contract: SharingContract
    ) -> bool:
        # Validate contract
        if not contract.is_valid():
            raise ContractExpiredError()
        
        if not contract.matches_memory(memory):
            return False
        
        # Apply depth filtering
        processed = self.apply_depth_filter(memory, contract.depth)
        
        # Ensure k-anonymity
        if contract.anonymous:
            processed = await self.ensure_k_anonymity(processed)
        
        # Store in collective
        await self.store_collective_memory(processed, contract)
        
        return True
    
    def apply_depth_filter(
        self, 
        memory: Memory, 
        depth: str
    ) -> Memory:
        if depth == 'summary':
            # Summarize content
            memory.content = self.summarize(memory.content, max_length=500)
        elif depth == 'detailed':
            # Remove only sensitive details
            memory.content = self.redact_sensitive(memory.content)
        # 'full' returns unchanged
        
        return memory
    
    async def ensure_k_anonymity(
        self, 
        memory: Memory
    ) -> Memory:
        # Find similar memories
        similar = await self.find_similar_memories(memory)
        
        if len(similar) < self.k_anonymity_threshold:
            # Wait for more similar memories
            raise InsufficientAnonymityError(
                f"Need {self.k_anonymity_threshold} similar memories"
            )
        
        # Generalize quasi-identifiers
        memory = self.generalize_memory(memory, similar)
        
        return memory
```

### Step 3: Collective Agents

```python
# agents/collective_agents.py
class MatchmakerAgent(BaseAgent):
    async def find_matches(
        self, 
        seeking: List[str], 
        collective_signals: List[Dict]
    ) -> List[Dict]:
        matches = []
        
        for signal in collective_signals:
            offering = signal.get('flags', {}).get('offering', [])
            score = self.calculate_match_score(seeking, offering)
            
            if score > 0.7:
                matches.append({
                    'signal': signal,
                    'score': score,
                    'matched_capabilities': list(set(seeking) & set(offering))
                })
        
        return sorted(matches, key=lambda x: x['score'], reverse=True)

class GapFinderAgent(BaseAgent):
    async def find_gaps(
        self, 
        collective_knowledge: List[Memory]
    ) -> List[str]:
        # Analyze what's missing
        domains = self.extract_all_domains(collective_knowledge)
        connections = self.find_connections(domains)
        
        gaps = []
        for domain_pair in connections:
            if not self.has_bridge(domain_pair, collective_knowledge):
                gaps.append(f"Bridge needed: {domain_pair[0]} <-> {domain_pair[1]}")
        
        return gaps
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_memory_service.py
import pytest
from services.memory_service import MemoryService

@pytest.mark.asyncio
async def test_memory_capture():
    service = MemoryService(user_id="test-user")
    
    memory = await service.capture(
        content="Test memory content",
        metadata={"domain": "test"}
    )
    
    assert memory.content == "Test memory content"
    assert memory.embedding is not None
    assert memory.importance > 0

@pytest.mark.asyncio  
async def test_importance_calculation():
    service = MemoryService(user_id="test-user")
    
    # Short content
    importance1 = service.calculate_importance("Short")
    
    # Long technical content with questions
    importance2 = service.calculate_importance(
        "How do I implement a distributed system? " * 50
    )
    
    assert importance2 > importance1
```

### Integration Tests

```python
# tests/test_integration.py
@pytest.mark.asyncio
async def test_full_flow():
    # Create user
    user = await create_test_user()
    
    # Capture memories
    memory_service = MemoryService(user.id)
    memories = []
    for i in range(10):
        memory = await memory_service.capture(f"Memory {i}")
        memories.append(memory)
    
    # Generate signal
    signal_service = SignalService(user.id)
    signal = await signal_service.generate_signal()
    
    assert signal['sigil'] is not None
    assert len(signal['domains']) > 0
    
    # Share with collective
    contract = SharingContract(
        user_id=user.id,
        collective_id="test-collective",
        domains=["test"],
        depth="summary",
        duration=timedelta(days=30)
    )
    
    collective = CollectiveService("test-collective")
    for memory in memories:
        await collective.share_memory(memory, contract)
```

---

## Deployment

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: ankane/pgvector
    environment:
      POSTGRES_DB: mnemosyne
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:alpine
    volumes:
      - redis_data:/data
  
  backend:
    build: ./backend
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres/mnemosyne
      REDIS_URL: redis://redis:6379
    ports:
      - "8000:8000"
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
```

---

## Performance Optimization

### Database Indexes

```sql
-- Optimize vector searches
CREATE INDEX idx_memories_embedding 
  ON memories USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

-- Optimize domain searches
CREATE INDEX idx_memories_domains 
  ON memories USING gin((metadata->'domains'));

-- Optimize user queries
CREATE INDEX idx_memories_user_importance 
  ON memories(user_id, importance DESC);
```

### Caching Strategy

```python
# services/cache_service.py
import redis
import json
from typing import Optional

class CacheService:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.ttl = 3600  # 1 hour
    
    async def get_or_set(
        self, 
        key: str, 
        generator, 
        ttl: Optional[int] = None
    ):
        # Try cache first
        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)
        
        # Generate and cache
        value = await generator()
        self.redis.set(
            key, 
            json.dumps(value), 
            ex=ttl or self.ttl
        )
        
        return value
```

---

## Monitoring

### Metrics Collection

```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge

memory_operations = Counter(
    'memory_operations_total',
    'Total memory operations',
    ['operation']
)

agent_reflection_duration = Histogram(
    'agent_reflection_duration_seconds',
    'Agent reflection duration',
    ['agent']
)

active_users = Gauge(
    'active_users',
    'Number of active users'
)

fracture_index = Gauge(
    'fracture_index',
    'Average fracture index across users'
)
```

---

## Security Checklist

- [ ] All user inputs sanitized
- [ ] SQL injection prevention (use ORM)
- [ ] API rate limiting implemented
- [ ] Authentication on all endpoints
- [ ] Encryption at rest (AES-256)
- [ ] Encryption in transit (HTTPS)
- [ ] K-anonymity enforced
- [ ] Memory revocation working
- [ ] Audit logging enabled
- [ ] Backup strategy defined

---

## Next Steps

1. **Complete MVP** - Get core features working
2. **Add philosophical agents** - Port from Dialogues
3. **Implement rituals** - Add symbolic layer
4. **Deploy to production** - Real users, real feedback
5. **Iterate based on use** - Let emergence guide development

---

*Remember: Build for yourself first. The rest will follow.*