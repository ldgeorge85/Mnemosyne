# Shadow AI Implementation Task Tracker

## Overview
This document provides detailed, step-by-step implementation tasks for enhancing the Shadow AI system. Each task includes specific files to modify, code snippets, and verification steps.

---

## Phase 1: Core Enhancements (Backend Infrastructure)

### 1.1 Implement Chat Session Storage Backend

**Status:** ⬜ Not Started

**Prerequisites:** None

**Tasks:**

1. **Create Session Model** ⬜
   - File: `shadow_system/models/session.py` (new)
   - Implementation:
   ```python
   from datetime import datetime
   from typing import List, Dict, Optional
   from pydantic import BaseModel, Field
   from uuid import uuid4
   
   class ChatMessage(BaseModel):
       role: str  # "user" or "assistant"
       content: str
       agent: Optional[str] = None
       timestamp: datetime = Field(default_factory=datetime.now)
       metadata: Optional[Dict] = None
   
   class ChatSession(BaseModel):
       id: str = Field(default_factory=lambda: str(uuid4()))
       user_id: str
       title: str = "New Chat"
       created_at: datetime = Field(default_factory=datetime.now)
       updated_at: datetime = Field(default_factory=datetime.now)
       messages: List[ChatMessage] = []
       metadata: Dict = {}
       is_active: bool = True
   ```

2. **Create Session Storage Interface** ⬜
   - File: `shadow_system/storage/session_store.py` (new)
   - Implementation:
   ```python
   from abc import ABC, abstractmethod
   from typing import List, Optional
   from models.session import ChatSession
   
   class SessionStore(ABC):
       @abstractmethod
       async def create_session(self, session: ChatSession) -> str:
           pass
       
       @abstractmethod
       async def get_session(self, session_id: str) -> Optional[ChatSession]:
           pass
       
       @abstractmethod
       async def update_session(self, session: ChatSession) -> bool:
           pass
       
       @abstractmethod
       async def delete_session(self, session_id: str) -> bool:
           pass
       
       @abstractmethod
       async def list_user_sessions(self, user_id: str) -> List[ChatSession]:
           pass
   ```

3. **Implement In-Memory Session Store** ⬜
   - File: `shadow_system/storage/in_memory_session_store.py` (new)
   - Basic implementation for testing
   - Store sessions in a dictionary

4. **Create Session Manager** ⬜
   - File: `shadow_system/managers/session_manager.py` (new)
   - Handles business logic for sessions
   - Integrates with memory system

5. **Add Session API Endpoints** ⬜
   - File: `shadow_system/api/session_endpoints.py` (new)
   - Endpoints:
     - POST `/api/sessions` - Create new session
     - GET `/api/sessions/{user_id}` - List user sessions
     - GET `/api/sessions/detail/{session_id}` - Get session details
     - PUT `/api/sessions/{session_id}` - Update session (title, metadata)
     - DELETE `/api/sessions/{session_id}` - Delete session
     - POST `/api/sessions/{session_id}/messages` - Add message to session

6. **Update FastAPI Server** ⬜
   - File: `shadow_system/api/fastapi_server.py`
   - Add: `from api.session_endpoints import router as session_router`
   - Add: `app.include_router(session_router, prefix="/api")`

7. **Test Session CRUD Operations** ⬜
   - Create test file: `shadow_system/tests/test_sessions.py`
   - Test all CRUD operations
   - Verify session persistence

---

### 1.2 Add Streaming Support to LLM Connector

**Status:** ⬜ Not Started

**Prerequisites:** None

**Tasks:**

1. **Update LLM Connector Interface** ⬜
   - File: `shadow_system/utils/llm_connector.py`
   - Add streaming method to `LLMConnector` base class:
   ```python
   async def generate_stream(self, messages: List[Dict]) -> AsyncIterator[str]:
       """Generate streaming response from LLM"""
       raise NotImplementedError
   ```

2. **Implement Streaming for OpenAI Connector** ⬜
   - File: `shadow_system/utils/llm_connector.py`
   - Update `OpenAIConnector` class:
   ```python
   async def generate_stream(self, messages: List[Dict]) -> AsyncIterator[str]:
       import aiohttp
       import json
       
       async with aiohttp.ClientSession() as session:
           async with session.post(
               f"{self.api_base}/chat/completions",
               json={
                   "model": self.model,
                   "messages": messages,
                   "stream": True,
                   "temperature": self.temperature,
                   "max_tokens": self.max_tokens
               },
               headers={"Authorization": f"Bearer {self.api_key}"}
           ) as response:
               async for line in response.content:
                   if line.startswith(b'data: '):
                       if line.strip() == b'data: [DONE]':
                           break
                       try:
                           data = json.loads(line[6:])
                           if 'choices' in data and data['choices']:
                               content = data['choices'][0].get('delta', {}).get('content', '')
                               if content:
                                   yield content
                       except json.JSONDecodeError:
                           continue
   ```

3. **Add Streaming to Shadow Agent** ⬜
   - File: `shadow_system/orchestrator/shadow_agent.py`
   - Add method:
   ```python
   async def process_request_stream(self, user_input: str, session_id: str = None):
       """Process request with streaming response"""
       # Store user message
       # Classify request
       # Stream from selected agent(s)
       # Yield chunks with agent attribution
   ```

4. **Create Streaming API Endpoint** ⬜
   - File: `shadow_system/api/fastapi_server.py`
   - Add endpoint:
   ```python
   from fastapi.responses import StreamingResponse
   
   @app.post("/api/shadow/stream")
   async def stream_chat(request: ShadowRequest):
       async def generate():
           async for chunk in shadow_agent.process_request_stream(
               request.query, 
               request.session_id
           ):
               yield f"data: {json.dumps(chunk)}\n\n"
           yield "data: [DONE]\n\n"
       
       return StreamingResponse(
           generate(),
           media_type="text/event-stream"
       )
   ```

5. **Test Streaming Functionality** ⬜
   - Create test script: `shadow_system/tests/test_streaming.py`
   - Test with curl: `curl -X POST http://localhost:8001/api/shadow/stream -H "Content-Type: application/json" -d '{"query":"test"}'`
   - Verify chunks arrive incrementally

---

## Phase 2: Intelligence Layer

### 2.1 Implement LLM-Based Classifier

**Status:** ⬜ Not Started

**Prerequisites:** Phase 1.2 (LLM Streaming)

**Tasks:**

1. **Create LLM Classifier** ⬜
   - File: `shadow_system/orchestrator/llm_classifier.py` (new)
   - Implementation structure:
   ```python
   class LLMClassifier:
       def __init__(self, llm_connector):
           self.llm = llm_connector
           self.system_prompt = self._load_classification_prompt()
       
       async def classify_task(self, query: str, context: Dict = None) -> Dict:
           """Returns: {"agents": ["agent1", "agent2"], "reasoning": "...", "confidence": 0.9}"""
           pass
   ```

2. **Create Classification Prompt** ⬜
   - File: `shadow_system/orchestrator/prompts/classifier.yaml` (new)
   - Define system prompt for agent selection
   - Include examples of queries and expected classifications

3. **Update Shadow Agent** ⬜
   - File: `shadow_system/orchestrator/shadow_agent.py`
   - Add configuration option: `use_llm_classifier: bool = False`
   - Conditionally use LLM classifier vs static classifier

4. **Add Classification Caching** ⬜
   - Cache recent classifications to reduce LLM calls
   - Implement TTL-based cache expiration

5. **Create Classification Tests** ⬜
   - File: `shadow_system/tests/test_llm_classifier.py`
   - Test various query types
   - Verify multi-agent selection works

---

### 2.2 Implement Memory-Aware Agent Processing

**Status:** ⬜ Not Started

**Prerequisites:** Phase 1.1 (Session Management)

**Tasks:**

1. **Create Memory Context Builder** ⬜
   - File: `shadow_system/memory/context_builder.py` (new)
   - Builds relevant context for queries:
   ```python
   class MemoryContextBuilder:
       def __init__(self, memory_manager):
           self.memory = memory_manager
       
       async def build_context(self, query: str, session_id: str) -> Dict:
           """Build context from conversation history, memories, and entities"""
           pass
   ```

2. **Update Base Agent Class** ⬜
   - File: `shadow_system/agents/base_agent.py`
   - Add memory context parameter to process_request
   - Update all agent implementations

3. **Implement Memory Extraction** ⬜
   - File: `shadow_system/memory/memory_extractor.py` (new)
   - Extract important facts from conversations
   - Use LLM to identify key insights

4. **Add Memory Storage Pipeline** ⬜
   - Automatically extract and store memories after each interaction
   - Tag memories with session and agent context

5. **Test Memory Integration** ⬜
   - Verify agents use memory context
   - Test memory extraction accuracy

---

## Phase 3: Frontend UI/UX

### 3.1 Build Session Management UI

**Status:** ⬜ Not Started

**Prerequisites:** Phase 1.1 (Session Backend)

**Tasks:**

1. **Create Session List Component** ⬜
   - File: `frontend/src/components/SessionList.js` (new)
   - Display user's chat sessions
   - Show title, date, preview

2. **Create Session Sidebar** ⬜
   - File: `frontend/src/components/SessionSidebar.js` (new)
   - New chat button
   - Session list
   - Search sessions

3. **Add Session Management Actions** ⬜
   - File: `frontend/src/actions/sessionActions.js` (new)
   - CRUD operations for sessions
   - Redux/Context integration

4. **Update Chat Interface** ⬜
   - File: `frontend/src/components/ChatInterface.js`
   - Add session context
   - Load/save messages to sessions

5. **Add Session Title Editing** ⬜
   - Inline editing for session titles
   - Auto-save on blur

---

### 3.2 Implement Streaming Chat UI

**Status:** ⬜ Not Started

**Prerequisites:** Phase 1.2 (Streaming Backend)

**Tasks:**

1. **Update Message Display** ⬜
   - File: `frontend/src/components/MessageList.js`
   - Support partial messages
   - Show typing indicator

2. **Implement SSE Client** ⬜
   - File: `frontend/src/utils/streamingClient.js` (new)
   - Handle Server-Sent Events
   - Parse streaming chunks

3. **Update Chat Service** ⬜
   - File: `frontend/src/services/shadowService.js`
   - Add streaming API call
   - Handle connection errors

4. **Add Streaming State Management** ⬜
   - Track streaming status
   - Handle abort/cancel

---

### 3.3 Add Agent Attribution Display

**Status:** ⬜ Not Started

**Prerequisites:** Phase 2.1 (LLM Classifier)

**Tasks:**

1. **Create Agent Badge Component** ⬜
   - File: `frontend/src/components/AgentBadge.js` (new)
   - Show agent name and confidence
   - Color-coded by agent type

2. **Update Message Component** ⬜
   - File: `frontend/src/components/Message.js`
   - Display agent attribution
   - Show multiple agents if applicable

3. **Add Attribution Styles** ⬜
   - File: `frontend/src/styles/AgentAttribution.css` (new)
   - Agent-specific colors
   - Hover effects

---

## Phase 4: Advanced Features

### 4.1 Multi-Agent Collaboration

**Status:** ⬜ Not Started

**Prerequisites:** Phase 2 Complete

**Tasks:**

1. **Fix Async Collaboration** ⬜
   - File: `shadow_system/orchestrator/collaborative_executor.py`
   - Resolve event loop issues
   - Implement proper async handling

2. **Create Collaboration Patterns** ⬜
   - Sequential execution
   - Parallel execution
   - Debate/consensus patterns

3. **Add Collaboration Monitoring** ⬜
   - Track agent interactions
   - Log collaboration decisions

---

## Verification Checklist

After each phase, verify:

1. **Code Quality** ⬜
   - All functions have docstrings
   - Type hints are used
   - Error handling is implemented

2. **Testing** ⬜
   - Unit tests pass
   - Integration tests pass
   - Manual testing completed

3. **Documentation** ⬜
   - README updated
   - API documentation current
   - Source of truth updated

4. **Performance** ⬜
   - Response times acceptable
   - Memory usage stable
   - No blocking operations

---

## Progress Summary

**Overall Progress:** 0/35 tasks completed (0%)

- Phase 1: 0/12 tasks (0%)
- Phase 2: 0/10 tasks (0%)
- Phase 3: 0/9 tasks (0%)
- Phase 4: 0/4 tasks (0%)

**Next Action:** Start with Task 1.1.1 - Create Session Model

---

## Notes for Implementers

1. Each task should be completed in order within its phase
2. Test after each task to ensure functionality
3. Update this tracker with ✅ when tasks are complete
4. Add any blockers or issues encountered
5. Follow the user rules regarding code comments and documentation updates
