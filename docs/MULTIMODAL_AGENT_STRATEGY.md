# Mnemosyne Multimodal & Multi-Agent Strategy
*Comprehensive plan for data library, multimedia support, and orchestrated agent systems*
*Created: August 24, 2025*

## Executive Summary

This document outlines the strategic expansion of Mnemosyne to support:
1. **Multimodal Data Library** - First-class support for documents, images, audio, video
2. **Generation API Integration** - Connect to image/video generation endpoints
3. **Multi-Agent Orchestration** - Distributed agents via model API endpoints
4. **Task Queue Architecture** - Scalable processing pipelines

**Critical Note**: Mnemosyne is **model-agnostic**. We interface with AI models through API endpoints only. Users are responsible for running or accessing their chosen model services (local or remote). Mnemosyne provides the orchestration, not the models.

## Part 1: Multimodal Data Architecture

### Core Philosophy
"Your memories, your models, your choice" - Data stays under user control, models are accessed through user-configured endpoints. Every operation generates receipts for transparency.

### 1.1 Data Vault (Object Storage)

#### Technology Choice: MinIO
```yaml
vault:
  type: MinIO  # S3-compatible, self-hosted
  features:
    - Content-addressed storage (SHA-256)
    - Versioning & lifecycle policies
    - Server-side encryption (SSE)
    - Bucket policies for access control
  
  integration:
    - Separate blob storage from metadata
    - PostgreSQL tracks references
    - AES-256-GCM encryption at rest
    - Per-user envelope keys
```

#### Data Model
```sql
-- Core asset storage
CREATE TABLE assets (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    blob_key TEXT NOT NULL,  -- S3 key
    mime_type TEXT NOT NULL,
    size_bytes BIGINT,
    sha256 TEXT NOT NULL,
    encryption_key_id UUID,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Extracted metadata
CREATE TABLE asset_metadata (
    asset_id UUID REFERENCES assets(id),
    metadata_type TEXT,  -- 'exif', 'ocr', 'transcript', 'caption'
    content JSONB,
    extracted_text TEXT,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- Vector embeddings per modality
CREATE TABLE asset_vectors (
    asset_id UUID REFERENCES assets(id),
    modality TEXT,  -- 'text', 'image', 'audio', 'video'
    vector_id TEXT,  -- Qdrant ID
    dimensions INT,
    model_name TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Granular permissions
CREATE TABLE asset_permissions (
    asset_id UUID REFERENCES assets(id),
    principal_id UUID,  -- User or agent
    scope TEXT,  -- 'read', 'write', 'generate', 'share'
    granted_at TIMESTAMP DEFAULT NOW()
);
```

### 1.2 Ingestion Pipelines

#### Document Pipeline
```python
class DocumentPipeline:
    """PDF/DOC/TXT → Text → Chunks → Embeddings"""
    
    tools = {
        'parser': 'unstructured',  # Robust parsing
        'ocr': 'Tesseract/PaddleOCR',  # For scanned docs
        'chunker': 'recursive_character_splitter',
        'embedder': 'sentence-transformers (1024d)'
    }
    
    async def process(self, document):
        # 1. Hash and store in MinIO
        blob_key = await self.store_blob(document)
        
        # 2. Extract text (native or OCR)
        text = await self.extract_text(document)
        
        # 3. Chunk intelligently
        chunks = self.chunk_text(text)
        
        # 4. Generate embeddings
        embeddings = await self.embed_chunks(chunks)
        
        # 5. Store in Qdrant
        await self.index_vectors(embeddings)
        
        # 6. Generate receipt
        return self.create_receipt(document, embeddings)
```

#### Image Pipeline
```python
class ImagePipeline:
    """Images → EXIF + Captions + Embeddings"""
    
    tools = {
        'exif': 'piexif/exiftool',
        'thumbs': 'Pillow',
        'caption': 'BLIP-2/LLaVA-Next',
        'embedder': 'OpenCLIP/SigLIP',
        'dedup': 'imagehash (pHash)'
    }
    
    async def process(self, image):
        # Extract metadata
        exif = self.extract_exif(image)
        
        # Generate thumbnail
        thumbnail = self.create_thumbnail(image)
        
        # Generate caption
        caption = await self.generate_caption(image)
        
        # Create embeddings (image + text)
        image_embedding = await self.embed_image(image)
        text_embedding = await self.embed_text(caption)
        
        # Check for duplicates
        if await self.is_duplicate(image):
            return self.handle_duplicate(image)
        
        return self.store_all(image, exif, caption, embeddings)
```

#### Audio/Video Pipeline
```python
class MediaPipeline:
    """Audio/Video → Transcripts + Keyframes + Embeddings"""
    
    tools = {
        'demux': 'FFmpeg/PyAV',
        'asr': 'faster-whisper',
        'keyframes': 'PySceneDetect',
        'caption': 'BLIP-2',
        'audio_embed': 'LAION-CLAP'
    }
    
    async def process(self, media):
        # Extract audio track
        audio = await self.extract_audio(media)
        
        # Transcribe
        transcript = await self.transcribe(audio)
        
        if media.is_video:
            # Extract keyframes
            keyframes = await self.extract_keyframes(media)
            
            # Caption keyframes
            captions = await self.caption_frames(keyframes)
            
            # Combine transcript + visual captions
            combined = self.fuse_modalities(transcript, captions)
        
        # Multi-modal indexing
        await self.index_all_modalities(media, transcript, keyframes)
```

### 1.3 Generation API Integration

#### Image Generation Interface
```python
class ImageGenerationInterface:
    """Interface to image generation API endpoints"""
    
    def __init__(self, endpoint_url: str, api_key: Optional[str] = None):
        self.endpoint = endpoint_url  # User-provided endpoint
        self.api_key = api_key  # If required by endpoint
        self.supported_params = self.discover_capabilities()
    
    async def generate(self, prompt, references=None):
        # Build API request based on endpoint capabilities
        request = self.build_request(prompt, references)
        
        # Call generation endpoint
        result = await self.call_endpoint(request)
        
        # Store as new asset
        asset = await self.store_generated(result)
        
        # Create receipt with full provenance
        receipt = self.create_generation_receipt(
            prompt, references, result, asset
        )
        
        return asset, receipt
```

#### Video Generation Interface
```python
class VideoGenerationInterface:
    """Interface to video generation API endpoints"""
    
    def __init__(self, endpoint_url: str):
        self.endpoint = endpoint_url
        self.capabilities = self.query_capabilities()
    
    async def generate_video(self, input_type, input_data):
        if input_type == 'image':
            return await self.image_to_video(input_data)
        elif input_type == 'text':
            # Text → Image → Video (two-stage)
            image = await self.text_to_image(input_data)
            return await self.image_to_video(image)
```

## Part 2: Multi-Agent Architecture

### 2.1 Agent Orchestration Framework

#### Core Architecture
```python
class AgentOrchestrator:
    """Manages multiple agents with different models and tasks"""
    
    def __init__(self):
        self.agents = {}
        self.task_queue = RedisQueue()
        self.model_registry = ModelRegistry()
        self.resource_manager = ResourceManager()
    
    async def register_agent(self, agent_config):
        """Register agent with specific model and capabilities"""
        agent = Agent(
            name=agent_config.name,
            model=self.model_registry.get(agent_config.model),
            capabilities=agent_config.capabilities,
            resource_limits=agent_config.limits
        )
        self.agents[agent.id] = agent
        return agent.id
    
    async def dispatch_task(self, task):
        """Route task to appropriate agent based on capabilities"""
        suitable_agents = self.find_capable_agents(task)
        
        if task.requires_consensus:
            # Multi-agent consensus
            results = await self.parallel_execute(suitable_agents, task)
            return self.synthesize_consensus(results)
        else:
            # Single agent execution
            agent = self.select_optimal_agent(suitable_agents, task)
            return await agent.execute(task)
```

#### Agent Types & Model Endpoints
```yaml
agent_types:
  philosophical:
    - name: "Bostrom Agent"
      endpoint: "${USER_CONFIGURED_LLM_ENDPOINT}"
      worldview: "bostrom_adapter"
      capabilities: ["existential_risk", "AI_safety"]
    
    - name: "Lanier Agent"
      endpoint: "${USER_CONFIGURED_LLM_ENDPOINT}"
      worldview: "lanier_adapter"
      capabilities: ["human_centric", "creativity"]
    
    - name: "Harari Agent"
      endpoint: "${USER_CONFIGURED_LLM_ENDPOINT}"
      worldview: "harari_adapter"
      capabilities: ["historical_analysis", "narrative"]
  
  specialized:
    - name: "Memory Curator"
      endpoint: "${USER_CONFIGURED_LLM_ENDPOINT}"
      capabilities: ["memory_synthesis", "pattern_recognition"]
    
    - name: "Privacy Guardian"
      endpoint: "${USER_CONFIGURED_LLM_ENDPOINT}"
      capabilities: ["consent_verification", "data_minimization"]
    
    - name: "Creative Director"
      endpoint: "${USER_IMAGE_GEN_ENDPOINT}"
      capabilities: ["image_generation", "style_transfer"]
  
  utility:
    - name: "Document Analyzer"
      endpoint: "${USER_EMBEDDING_ENDPOINT}"
      capabilities: ["OCR", "summarization", "extraction"]
    
    - name: "Media Processor"
      endpoint: "${USER_TRANSCRIPTION_ENDPOINT}"
      capabilities: ["transcription", "captioning"]
```

### 2.2 Task Queue Architecture

#### Queue System
```python
class TaskQueueSystem:
    """Distributed task processing with priority and routing"""
    
    def __init__(self):
        self.queues = {
            'urgent': RedisQueue(priority=1),
            'normal': RedisQueue(priority=5),
            'batch': RedisQueue(priority=10),
            'generation': RedisQueue(priority=7)
        }
        self.workers = {}
    
    async def submit_task(self, task):
        """Submit task to appropriate queue"""
        queue = self.select_queue(task)
        
        # Add sovereignty metadata
        task.receipt_id = generate_receipt_id()
        task.consent_token = await self.get_consent(task)
        
        await queue.enqueue(task)
        return task.receipt_id
    
    async def process_tasks(self):
        """Worker process for task execution"""
        while True:
            task = await self.get_next_task()
            
            try:
                # Select appropriate agent/model
                agent = await self.orchestrator.select_agent(task)
                
                # Execute with monitoring
                result = await self.execute_with_monitoring(agent, task)
                
                # Store result and receipt
                await self.store_result(result)
                
            except Exception as e:
                await self.handle_failure(task, e)
```

#### Task Types
```python
@dataclass
class Task:
    id: str
    type: TaskType
    priority: int
    payload: Dict
    constraints: Dict
    receipt_id: str
    consent_token: str
    
class TaskType(Enum):
    # Memory operations
    MEMORY_INGEST = "memory_ingest"
    MEMORY_SYNTHESIS = "memory_synthesis"
    MEMORY_SEARCH = "memory_search"
    
    # Generation
    IMAGE_GENERATION = "image_generation"
    VIDEO_GENERATION = "video_generation"
    TEXT_GENERATION = "text_generation"
    
    # Analysis
    DOCUMENT_ANALYSIS = "document_analysis"
    MEDIA_TRANSCRIPTION = "media_transcription"
    PATTERN_RECOGNITION = "pattern_recognition"
    
    # Philosophical
    WORLDVIEW_TRANSLATION = "worldview_translation"
    ETHICAL_REVIEW = "ethical_review"
    CONSENSUS_BUILDING = "consensus_building"
```

### 2.3 Model Endpoint Management

#### Endpoint Registry
```python
class EndpointRegistry:
    """Manages API endpoints for various AI services"""
    
    def __init__(self):
        self.endpoints = {}  # User-configured endpoints
        self.capabilities = {}
        # No hardcoded models - all user-provided
    
    def register_endpoint(self, endpoint_config):
        """Register a user-provided API endpoint"""
        endpoint = Endpoint(
            name=endpoint_config.name,
            url=endpoint_config.url,  # User-provided URL
            type=endpoint_config.type,  # LLM, embedding, generation, etc.
            auth=endpoint_config.auth_method,
            capabilities=endpoint_config.capabilities
        )
        self.endpoints[endpoint.name] = endpoint
    
    def select_model(self, task_requirements):
        """Select optimal model for task requirements"""
        candidates = self.find_capable_models(task_requirements)
        
        # Optimize for: capability match, cost, latency, sovereignty
        return self.optimize_selection(candidates, task_requirements)
```

#### Endpoint Configuration (User-Provided)
```yaml
# Example configuration - users provide their own endpoints
user_endpoints:
  llm:
    - name: "primary_llm"
      endpoint: "${LLM_ENDPOINT_URL}"  # User configures
      type: "LLM"
      auth: "${LLM_API_KEY}"  # Optional, user-provided
      capabilities: ["general", "reasoning"]
    
  embedding:
    - name: "embedding_service"
      endpoint: "${EMBEDDING_ENDPOINT_URL}"
      type: "embedding"
      auth: "${EMBEDDING_API_KEY}"
      capabilities: ["text_embedding", "semantic_search"]
    
  generation:
    - name: "image_generator"
      endpoint: "${IMAGE_GEN_ENDPOINT_URL}"
      type: "generation"
      auth: "${IMAGE_GEN_API_KEY}"
      capabilities: ["image_generation"]
  
  transcription:
    - name: "speech_to_text"
      endpoint: "${STT_ENDPOINT_URL}"
      type: "transcription"
      capabilities: ["audio_transcription"]

# Note: Mnemosyne does not provide or recommend specific models.
# Users choose and configure their own AI service endpoints.
```

## Part 3: Integration Strategy

### 3.1 Phased Implementation

#### Phase 1.5: Data Foundation (Immediate)
**Task Group J - Vault & Ingestion**
- [ ] Set up MinIO for object storage
- [ ] Implement document ingestion pipeline
- [ ] Add image processing with EXIF
- [ ] Create endpoint configuration system
- [ ] Wire into existing memory CRUD

#### Phase 2: Media & Agents (Next Quarter)
**Task Group K - Vision & AV Pipeline**
- [ ] Add transcription API integration
- [ ] Implement video keyframe extraction
- [ ] Multi-modal search interface
- [ ] Consent-based retrieval in chat

**Task Group M - Agent Orchestration**
- [ ] Build agent registry
- [ ] Implement task queue system
- [ ] Add model endpoint management
- [ ] Create agent consensus mechanisms

#### Phase 2.5: Generation (Following Quarter)
**Task Group L - Generation Integration**
- [ ] Configure generation API endpoints
- [ ] Implement generation request interface
- [ ] Add generation result storage
- [ ] Receipt system for all generations

### 3.2 Technical Architecture Updates

#### Service Additions
```yaml
services:
  # Existing
  - postgres
  - redis
  - qdrant
  - backend
  - frontend
  
  # New additions
  - minio:  # Object storage
      image: minio/minio
      volumes:
        - minio_data:/data
      environment:
        - MINIO_ROOT_USER=${MINIO_USER}
        - MINIO_ROOT_PASSWORD=${MINIO_PASSWORD}
  
  - task_worker:  # Background processing
      build: ./workers
      depends_on:
        - redis
        - postgres
        - minio
      environment:
        - WORKER_TYPE=general
  
  # Note: AI model services are user-provided
  # Users must configure and run their own:
  # - LLM service (Ollama, vLLM, etc.)
  # - Embedding service
  # - Generation service (ComfyUI, A1111, etc.)
  # - Transcription service
```

#### API Structure
```
/api/v1/
├── assets/
│   ├── upload/          # Multipart upload
│   ├── {id}/            # Asset retrieval
│   ├── {id}/metadata/   # Metadata CRUD
│   └── search/          # Multi-modal search
├── generation/
│   ├── image/           # Image generation
│   ├── video/           # Video generation
│   └── status/{id}/     # Generation status
├── agents/
│   ├── registry/        # Available agents
│   ├── tasks/           # Task submission
│   └── consensus/       # Multi-agent ops
└── receipts/
    ├── {id}/            # Receipt retrieval
    └── verify/          # Receipt verification
```

### 3.3 Privacy & Sovereignty Considerations

#### Data Sovereignty
```python
class SovereigntyEnforcer:
    """Ensures all operations respect user sovereignty"""
    
    def before_operation(self, operation):
        # Verify consent
        if not self.has_consent(operation):
            raise ConsentRequired()
        
        # Check data locality
        if operation.requires_external:
            self.request_explicit_consent()
        
        # Generate receipt header
        receipt = self.start_receipt(operation)
        return receipt
    
    def after_operation(self, operation, result):
        # Complete receipt
        receipt = self.complete_receipt(operation, result)
        
        # Store immutably
        self.store_receipt(receipt)
        
        # Notify user if configured
        if self.user.wants_notifications:
            self.notify_user(receipt)
```

#### Consent Management
```yaml
consent_levels:
  local_only:
    - description: "All processing stays on your machine"
    - external_calls: false
    - data_sharing: false
    
  selective_external:
    - description: "Some features use external services"
    - external_calls: true
    - requires_per_operation_consent: true
    
  trusted_services:
    - description: "Pre-approved external services"
    - external_calls: true
    - whitelist: ["anthropic", "openai"]
    - audit_log: true
```

## Part 4: Research Directions

### 4.1 Advanced Multi-Agent Patterns

#### Consensus Mechanisms
- Byzantine fault tolerance for agent disagreement
- Weighted voting based on expertise domains
- Emergent consensus through iterative refinement

#### Agent Specialization
- Domain-specific fine-tuning
- Capability composition through agent teams
- Dynamic agent spawning for complex tasks

#### Communication Protocols
- Inter-agent message passing
- Shared memory architectures
- Blackboard systems for collaborative problem-solving

### 4.2 Advanced Data Capabilities

#### Homomorphic Operations
- Search on encrypted data
- Privacy-preserving analytics
- Secure multi-party computation

#### Federated Learning
- Learn from user data without centralizing
- Differential privacy guarantees
- Personalized models that stay local

#### Semantic Understanding
- Cross-modal reasoning
- Temporal pattern recognition
- Narrative extraction from multimedia

## Part 5: Success Metrics

### Technical Metrics
- Ingestion throughput (docs/images per second)
- Search latency (<100ms p95)
- Generation quality (user satisfaction scores)
- Agent coordination efficiency

### Sovereignty Metrics
- Local processing percentage (>95%)
- Consent compliance rate (100%)
- Receipt generation coverage (100%)
- Data portability success rate

### User Experience Metrics
- Time to first value (<5 minutes)
- Feature discovery rate
- Trust in system decisions
- Joy coefficient (delight moments)

## Implementation Priorities

### Immediate (Week 1-2)
1. Set up MinIO and basic ingestion
2. Document pipeline with OCR
3. Extend existing memory system
4. Basic receipt generation

### Short Term (Month 1)
1. Image pipeline with EXIF/captions
2. Task queue system
3. Multi-modal search
4. Agent registry prototype

### Medium Term (Months 2-3)
1. Audio/video pipelines
2. ComfyUI integration
3. Multi-agent consensus
4. Advanced consent management

### Long Term (Months 4-6)
1. Full generation studio
2. Federated learning
3. Homomorphic search
4. Complete sovereignty toolkit

## Conclusion

This expansion maintains Mnemosyne's core sovereignty principles while dramatically expanding capabilities. The multimodal data library provides the foundation for rich memory preservation, while the multi-agent architecture enables sophisticated reasoning and generation capabilities.

Key principles maintained:
- **Model Agnostic**: Works with any API-compatible AI service
- **User Choice**: Users select and configure their own endpoints
- **Consent Required**: Every operation needs permission
- **Receipts Always**: Full transparency through audit logs
- **Joy Embedded**: Delightful interactions throughout

The architecture is designed to orchestrate any combination of AI services while preserving user sovereignty over both data and model choices.

---

*"Your memories, your endpoints, your sovereignty - Mnemosyne orchestrates, you control."*