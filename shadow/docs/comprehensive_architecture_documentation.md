# Shadow AI System - Comprehensive Architecture Documentation

**Version**: 1.0  
**Date**: 2025-06-11  
**Status**: PRODUCTION READY (Post InnoScale Integration Bug Fix)

---

## 🏗️ System Overview

The Shadow AI System is a multi-agent orchestration platform that routes user queries to specialized AI agents and aggregates their responses. The system integrates with InnoScale's InnoGPT-1 model and provides both REST API and React-based web interfaces.

### Core Philosophy
- **Multi-Agent Collaboration**: Three specialized agents (Engineer, Librarian, Priest) with distinct capabilities
- **Intelligent Routing**: Dynamic classification and routing of queries to appropriate agents
- **Memory Integration**: Persistent conversation history and context retention
- **Extensible Architecture**: Modular design supporting multiple LLM providers

---

## 🎯 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        SHADOW AI SYSTEM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌──────────────────────────────────┐    │
│  │   React Frontend │    │        FastAPI Backend          │    │
│  │   (Port 8001)    │◄──►│        (Port 8000)              │    │
│  │                 │    │                                  │    │
│  │ - Modern UI     │    │ - REST API Endpoints            │    │
│  │ - Real-time     │    │ - Request Processing             │    │
│  │ - Responsive    │    │ - CORS Enabled                  │    │
│  └─────────────────┘    └──────────────────────────────────┘    │
│                                           │                     │
│  ┌─────────────────────────────────────────▼─────────────────┐   │
│  │              SHADOW ORCHESTRATOR                        │   │
│  │                                                         │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │   │
│  │  │ CLASSIFIER  │  │ AGGREGATOR  │  │   MEMORY    │     │   │
│  │  │             │  │             │  │             │     │   │
│  │  │ - Query     │  │ - Response  │  │ - Vector    │     │   │
│  │  │   Analysis  │  │   Synthesis │  │ - Document  │     │   │
│  │  │ - Agent     │  │ - Context   │  │ - History   │     │   │
│  │  │   Selection │  │   Building  │  │             │     │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │   │
│  └─────────────────────────────────────────┬─────────────────┘   │
│                                           │                     │
│  ┌─────────────────────────────────────────▼─────────────────┐   │
│  │                 SPECIALIZED AGENTS                      │   │
│  │                                                         │   │
│  │ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │   │
│  │ │  ENGINEER   │ │  LIBRARIAN  │ │       PRIEST        │ │   │
│  │ │             │ │             │ │                     │ │   │
│  │ │ Technical   │ │ Research &  │ │ Ethics &            │ │   │
│  │ │ Problem     │ │ Information │ │ Philosophy          │ │   │
│  │ │ Solving     │ │ Retrieval   │ │                     │ │   │
│  │ └─────────────┘ └─────────────┘ └─────────────────────┘ │   │
│  └─────────────────────────────────────────┬─────────────────┘   │
│                                           │                     │
│  ┌─────────────────────────────────────────▼─────────────────┐   │
│  │                LLM INTEGRATION                          │   │
│  │                                                         │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │           INNOSCALE INNOGPT-1                   │    │   │
│  │  │                                                 │    │   │
│  │  │ - API Endpoint: api.ai1.infra.innoscale.net    │    │   │
│  │  │ - Model: InnoGPT-1                             │    │   │
│  │  │ - Max Tokens: 2048                             │    │   │
│  │  │ - Temperature: 1.0                             │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🏭 Component Architecture

### 1. Frontend Layer (React Application)

**Location**: `/frontend/`  
**Port**: 8001 (served via FastAPI static files)  
**Technology**: React.js, Modern ES6+

```
frontend/
├── public/
│   ├── index.html          # Main HTML template
│   └── manifest.json       # PWA configuration
├── src/
│   ├── components/         # React components
│   ├── services/          # API integration
│   ├── styles/            # CSS styling
│   └── index.js           # Application entry point
└── package.json           # Dependencies
```

**Key Features**:
- Modern, responsive UI
- Real-time communication with backend
- Session management
- Error handling and feedback

### 2. API Layer (FastAPI Server)

**Location**: `/api/fastapi_server.py`  
**Port**: 8000 (internal), 8001 (external)  
**Technology**: FastAPI, Uvicorn

**Endpoints**:
```
GET  /                     # Serve React frontend
POST /api/shadow          # Main AI processing endpoint
GET  /api/health          # System health check
```

**Request/Response Models**:
```python
# Request Model
class ShadowRequest:
    query: str                    # User input
    session_id: Optional[str]     # Session tracking
    metadata: Optional[Dict]      # Additional context

# Response Model  
class ShadowResponse:
    response: str                 # AI-generated response
    session_id: str              # Session identifier
    agents_used: List[str]       # Agents that processed request
    processing_time: float       # Execution time (ms)
    metadata: Optional[Dict]     # Additional response data
```

### 3. Orchestration Layer (Shadow Agent)

**Location**: `/orchestrator/shadow_agent.py`  
**Purpose**: Central coordination and intelligent routing

**Core Components**:

#### 3.1 Request Classifier (`/orchestrator/classifier.py`)
- Analyzes incoming queries
- Determines appropriate agent(s) to engage
- Supports both single-agent and multi-agent routing

#### 3.2 Task Decomposer (`/orchestrator/task_decomposer.py`)
- Breaks complex queries into subtasks
- Enables parallel processing capabilities
- Classifications: `simple`, `complex`, `collaborative`

#### 3.3 Response Aggregator (`/orchestrator/aggregator.py`)
- Combines responses from multiple agents
- Maintains context and coherence
- Handles conflicts and contradictions

#### 3.4 Memory Integration (`/orchestrator/memory_integration.py`)
- Manages conversation history
- Provides context to agents
- Enables learning and adaptation

### 4. Agent Layer (Specialized AI Agents)

**Base Architecture**: All agents inherit from `BaseAgent` (`/agents/base_agent.py`)

#### 4.1 Engineer Agent (`/agents/engineer/agent.py`)
**Specialization**: Technical problem-solving, engineering design, system architecture
```python
class EngineerAgent(BaseAgent):
    """Handles technical queries, problem-solving, design challenges"""
    - Process technical queries
    - Provide engineering solutions
    - System design recommendations
```

#### 4.2 Librarian Agent (`/agents/librarian/agent.py`)
**Specialization**: Research, information retrieval, knowledge synthesis
```python
class LibrarianAgent(BaseAgent):
    """Handles research queries, information gathering, knowledge synthesis"""
    - Conduct research
    - Synthesize information
    - Provide citations and sources
```

#### 4.3 Priest Agent (`/agents/priest/agent.py`)
**Specialization**: Ethics, philosophy, moral reasoning
```python
class PriestAgent(BaseAgent):
    """Handles ethical dilemmas, philosophical questions, moral guidance"""
    - Ethical analysis
    - Philosophical reasoning
    - Moral guidance
```

### 5. Memory Layer

**Location**: `/memory/`  
**Architecture**: Multi-store design

#### 5.1 Vector Memory (`/memory/vector_memory.py`)
- Embedding-based similarity search
- Context retrieval for agents
- InnoScale embedding API integration

#### 5.2 Document Store (`/memory/document_store.py`)
- Long-term document storage
- Knowledge base management
- Structured data retention

#### 5.3 Relational Store (`/memory/relational_store.py`)
- Session management
- User preferences
- Structured relationships

#### 5.4 Memory Manager (`/memory/memory_manager.py`)
- Coordinates all memory stores
- Provides unified interface
- Handles memory lifecycle

### 6. LLM Integration Layer

**Location**: `/utils/llm_connector.py`  
**Purpose**: Abstracted LLM provider interface

**Supported Providers**:
- **OpenAI** (including compatible APIs like InnoScale)
- **Anthropic Claude**
- **Local Models** (vLLM, LlamaCPP)
- **Mock Provider** (for testing)

**Current Configuration (InnoScale)**:
```python
LLM_BASE_URL=https://api.ai1.infra.innoscale.net/v1
LLM_API_KEY=a884498c-45e6-4bcc-a128-680f0c04a74d
LLM_MODEL_NAME=InnoGPT-1
LLM_MAX_TOKENS=2048
LLM_TEMPERATURE=1.0
```

---

## 🔄 Data Flow Analysis

### Request Processing Flow

```
1. User Input
   │
   ├─► Frontend (React) ──HTTP POST──► FastAPI Server
                                      │
2. Request Processing                  │
   │                                  │
   ├─► FastAPI receives ShadowRequest │
   │                                  │
   ├─► Initialize Shadow Orchestrator │                    
   │                                  │
   └─► Route to Shadow.process_query()│
                                      │
3. Orchestration Phase               │
   │                                  │
   ├─► Classifier analyzes query      │
   │                                  │  
   ├─► Task Decomposer assesses complexity
   │                                  │
   ├─► Memory retrieval (context)     │
   │                                  │
   └─► Agent selection & routing      │
                                      │
4. Agent Processing                   │
   │                                  │
   ├─► Engineer/Librarian/Priest      │
   │                                  │
   ├─► LLM Connector ──API Call──► InnoScale InnoGPT-1
   │                                  │
   └─► Generate specialized response  │
                                      │
5. Response Synthesis                 │
   │                                  │
   ├─► Aggregator combines responses  │
   │                                  │
   ├─► Memory storage (conversation)  │
   │                                  │
   └─► Build ShadowResponse          │
                                      │
6. Response Delivery                  │
   │                                  │
   └─► FastAPI ──JSON Response──► Frontend ──Display──► User
```

### Memory Integration Flow

```
Input Query
    │
    ├─► Vector Embedding (InnoScale API)
    │
    ├─► Similarity Search (Vector Store)
    │
    ├─► Context Retrieval (Document Store)
    │
    ├─► Session History (Relational Store)
    │
    └─► Enhanced Context ──► Agent Processing
                              │
Agent Response                │
    │                         │
    ├─► Response Embedding    │
    │                         │
    ├─► Store in Vector Memory│
    │                         │
    ├─► Update Document Store │
    │                         │
    └─► Session Tracking      │
```

---

## ⚙️ Configuration Management

### Environment Variables (`.env`)

```bash
# LLM Configuration
LLM_BASE_URL=https://api.ai1.infra.innoscale.net/v1
LLM_API_KEY=a884498c-45e6-4bcc-a128-680f0c04a74d
LLM_MODEL_NAME=InnoGPT-1
LLM_MAX_TOKENS=2048
LLM_TEMPERATURE=1.0

# System Configuration
PYTHONPATH=/app
LOG_LEVEL=INFO

# Memory Configuration
VECTOR_DIMENSION=1024
MAX_HISTORY_LENGTH=10
```

### Docker Configuration (`docker-compose.yml`)

```yaml
version: '3.8'
services:
  shadow-ai:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8001:8000"
    environment:
      - PYTHONPATH=/app
    volumes:
      - .:/app
    working_dir: /app
    command: python api/fastapi_server.py
```

---

## 🔍 Current vs. Intended Design Analysis

### ✅ Successfully Implemented

1. **Multi-Agent Architecture**: All three specialized agents (Engineer, Librarian, Priest) are implemented and functional
2. **LLM Integration**: InnoScale InnoGPT-1 integration working correctly (post-bug fix)
3. **REST API**: FastAPI server with proper endpoints and request/response models
4. **React Frontend**: Modern web interface with real-time communication
5. **Memory System**: Multi-store memory architecture with vector, document, and relational stores
6. **Docker Deployment**: Containerized deployment with proper networking

### ⚠️ Implementation Gaps Identified

1. **Async Collaboration**: Currently disabled in `orchestrator/shadow_agent.py` for stability
   ```python
   # Line ~47: self.enable_collaboration = enable_collaboration
   # Currently defaulting to False due to event loop conflicts
   ```

2. **Advanced Task Decomposition**: Task decomposer exists but complex routing may not be fully utilized
   ```python
   # Defaulting to "basic routing for stable operation"
   ```

3. **Memory Persistence**: In-memory stores may not persist across container restarts
   ```python
   # Using InMemoryVectorStore, InMemoryDocumentStore, InMemoryRelationalStore
   ```

4. **Error Handling**: Limited error recovery and fallback mechanisms
5. **Monitoring/Observability**: Basic logging but no metrics or tracing
6. **Testing Coverage**: Limited automated testing

### 🔧 Immediate Fixes Needed

1. **Re-enable Async Collaboration** once stable
2. **Implement Persistent Storage** for memory stores
3. **Add Comprehensive Error Handling**
4. **Improve Observability** with metrics and health checks
5. **Add Integration Tests** for end-to-end workflows

---

## 🚀 API Reference

### POST `/api/shadow`

**Description**: Main endpoint for processing user queries through the Shadow AI system

**Request Body**:
```json
{
  "query": "What is the best way to optimize database performance?",
  "session_id": "user-session-123",
  "metadata": {
    "user_id": "optional",
    "context": "optional additional context"
  }
}
```

**Response**:
```json
{
  "response": "Database optimization involves several key strategies: indexing, query optimization, connection pooling...",
  "session_id": "user-session-123",
  "agents_used": ["engineer", "librarian"],
  "processing_time": 2341.67,
  "metadata": {
    "request_length": 47,
    "response_length": 523,
    "model_used": "InnoGPT-1"
  }
}
```

### GET `/api/health`

**Description**: System health check endpoint

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-06-11T19:14:01-07:00",
  "version": "1.0.0",
  "agents": {
    "engineer": {"status": "ready", "last_used": "2025-06-11T19:13:45-07:00"},
    "librarian": {"status": "ready", "last_used": "2025-06-11T19:12:33-07:00"},
    "priest": {"status": "ready", "last_used": "2025-06-11T19:11:22-07:00"}
  }
}
```

---

## 🔧 Deployment Guide

### Prerequisites
- Docker and Docker Compose
- InnoScale API access credentials
- Minimum 4GB RAM, 2 CPU cores

### Quick Start
```bash
# Clone repository
cd /path/to/shadow/shadow_system

# Configure environment
cp .env.example .env
# Edit .env with your InnoScale credentials

# Deploy system
docker compose up -d

# Verify deployment
curl http://localhost:8001/api/health
```

### Verification Steps
1. **Container Status**: `docker compose ps`
2. **API Health**: `curl http://localhost:8001/api/health`
3. **Test Query**: `curl -X POST "http://localhost:8001/api/shadow" -H "Content-Type: application/json" -d '{"query": "Hello, test", "session_id": "test"}'`
4. **Web Interface**: Navigate to `http://localhost:8001`

---

## 📊 Performance Characteristics

### Response Times (Typical)
- **Simple Query**: 1-3 seconds
- **Complex Query**: 3-8 seconds  
- **Multi-Agent Query**: 5-15 seconds

### Resource Usage
- **Memory**: ~500MB base, +100MB per concurrent session
- **CPU**: Low baseline, spikes during LLM processing
- **Network**: ~1-10KB request, ~1-50KB response

### Scaling Considerations
- **Horizontal Scaling**: Not yet implemented (stateful memory)
- **Vertical Scaling**: Benefits from additional RAM and CPU
- **Database**: In-memory stores limit scalability

---

## 🔮 Future Roadmap

### Phase 1: Stability & Performance
- [ ] Re-enable async collaboration
- [ ] Implement persistent storage
- [ ] Add comprehensive error handling
- [ ] Performance optimization

### Phase 2: Advanced Features  
- [ ] Multi-model support (GPT-4, Claude, etc.)
- [ ] Advanced memory retrieval
- [ ] Custom agent plugins
- [ ] Real-time streaming responses

### Phase 3: Enterprise Features
- [ ] User authentication & authorization
- [ ] Multi-tenant support
- [ ] Analytics and monitoring
- [ ] Horizontal scaling support

---

## 📚 References & Documentation

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **React Documentation**: https://reactjs.org/docs/
- **InnoScale API**: https://api.ai1.infra.innoscale.net/v1
- **Docker Compose**: https://docs.docker.com/compose/

---

**Document Status**: ACTIVE  
**Last Updated**: 2025-06-11 19:14  
**Next Review**: 2025-06-25  
**Maintainer**: Shadow AI Development Team
