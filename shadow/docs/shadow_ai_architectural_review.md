# Shadow AI Architectural Review & Enhancement Recommendations

## Executive Summary

This document provides a comprehensive review of the Shadow AI system architecture, identifies current limitations, and proposes enhancements for multi-agent orchestration, chat session management, memory integration, agent attribution, and streaming responses.

## Current Architecture Analysis

### 1. Multi-Agent Orchestration

**Current State:**
- Shadow uses static keyword-based classification (see `orchestrator/classifier.py`)
- Agent selection is deterministic based on keyword matching
- No dynamic LLM-driven orchestration
- Collaborative execution exists but is disabled due to async issues

**Key Findings:**
```python
# Current static classification approach
self.engineer_keywords = ["build", "design", "calculate", ...]
self.librarian_keywords = ["reference", "search", "find", ...]
self.priest_keywords = ["ethics", "moral", "philosophy", ...]
```

**Limitations:**
- Cannot adapt to nuanced queries
- No context-aware agent selection
- Cannot leverage multiple agents intelligently
- No true "agentic" behavior - just rule-based routing

### 2. Chat Session Management

**Current State:**
- No session persistence beyond memory
- Each request creates ephemeral session ID
- No UI for managing multiple conversations
- Conversation history limited to in-memory array

**Key Code:**
```python
# From fastapi_server.py
session_id=request.session_id or f"session_{int(time.time())}"
```

### 3. Memory System

**Current State:**
- Three-tier memory: Vector, Document, and Relational stores
- Memory manager coordinates between stores
- Conversation history stored but not effectively used
- Memory context retrieved but not integrated into agent prompts

**Memory Flow:**
1. User input → Store in conversation history
2. Retrieve relevant context from memory
3. Pass to agents (but agents may not use it effectively)
4. Store response in memory

### 4. Agent Attribution

**Current State:**
- Attribution done through response text analysis
- Simple heuristic matching for agent identification
- No explicit agent tagging in responses

```python
# Current heuristic approach
if "Technical Analysis" in response:
    agents_used.append("engineer")
```

### 5. Streaming Responses

**Current State:**
- Synchronous request/response only
- No streaming support in API endpoints
- LLM connector doesn't support streaming

## Recommendations & Implementation Plan

### 1. Dynamic LLM-Driven Orchestration

**Goal:** Transform Shadow into a true agentic orchestrator that uses LLM intelligence for routing.

**Implementation:**

```python
# New LLMClassifier to replace static classifier
class LLMClassifier:
    def __init__(self, llm_connector):
        self.llm = llm_connector
        self.system_prompt = """You are Shadow, an intelligent orchestrator.
        Given a user query, determine which specialist agents should handle it:
        - Engineer: Technical tasks, coding, system design
        - Librarian: Information retrieval, research, documentation
        - Priest: Ethics, philosophy, moral considerations
        
        You may select multiple agents for complex queries.
        Consider the query context and conversation history.
        Output JSON: {"agents": ["agent1", "agent2"], "reasoning": "..."}"""
    
    async def classify_task(self, query: str, context: Dict) -> Dict:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Query: {query}\nContext: {json.dumps(context)}"}
        ]
        response = await self.llm.generate_async(messages)
        return json.loads(response)
```

**Benefits:**
- Context-aware routing
- Can understand nuanced requests
- Adapts based on conversation history
- True agentic behavior

### 2. Multi-Session Chat Management

**Architecture:**

```python
# New session manager
class ChatSessionManager:
    def __init__(self, storage_backend):
        self.storage = storage_backend
        self.active_sessions = {}
    
    async def create_session(self, user_id: str, title: str = None) -> str:
        session = {
            "id": str(uuid4()),
            "user_id": user_id,
            "title": title or "New Chat",
            "created_at": datetime.now(),
            "messages": [],
            "metadata": {}
        }
        await self.storage.save_session(session)
        return session["id"]
    
    async def list_sessions(self, user_id: str) -> List[Dict]:
        return await self.storage.get_user_sessions(user_id)
    
    async def load_session(self, session_id: str) -> Dict:
        return await self.storage.get_session(session_id)
    
    async def add_message(self, session_id: str, role: str, content: str, agent: str = None):
        message = {
            "role": role,
            "content": content,
            "agent": agent,
            "timestamp": datetime.now()
        }
        await self.storage.append_message(session_id, message)
```

**API Endpoints:**
```python
@app.post("/api/sessions/create")
async def create_session(user_id: str, title: Optional[str] = None):
    session_id = await session_manager.create_session(user_id, title)
    return {"session_id": session_id}

@app.get("/api/sessions/list/{user_id}")
async def list_sessions(user_id: str):
    sessions = await session_manager.list_sessions(user_id)
    return {"sessions": sessions}

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    session = await session_manager.load_session(session_id)
    return session

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    await session_manager.delete_session(session_id)
    return {"status": "deleted"}
```

**Frontend Components:**
- Session list sidebar
- New session button
- Session title editing
- Delete session confirmation
- Load session functionality

### 3. Enhanced Memory Integration

**Memory-Aware Agent Architecture:**

```python
class MemoryAwareAgent:
    def __init__(self, base_agent, memory_manager):
        self.agent = base_agent
        self.memory = memory_manager
    
    async def process_with_memory(self, query: str, session_id: str):
        # Get conversation context
        conversation = await self.memory.get_conversation(session_id)
        
        # Get relevant memories
        memories = await self.memory.search_memories(query, limit=5)
        
        # Get related entities
        entities = await self.memory.get_entities_for_query(query)
        
        # Build enhanced prompt
        context = {
            "conversation": conversation[-10:],  # Last 10 messages
            "memories": [m.to_dict() for m in memories],
            "entities": entities
        }
        
        # Process with full context
        response = await self.agent.process(query, context)
        
        # Extract and store new memories
        new_memories = await self.extract_memories(query, response)
        for memory in new_memories:
            await self.memory.store_memory(memory)
        
        return response
```

**Memory Extraction:**
```python
async def extract_memories(self, query: str, response: str) -> List[MemoryItem]:
    prompt = f"""Extract important facts, decisions, or insights from this conversation:
    User: {query}
    Assistant: {response}
    
    Output JSON array of memories with: content, type, tags, importance (0-1)"""
    
    memories_json = await self.llm.generate(prompt)
    return [MemoryItem(**m) for m in json.loads(memories_json)]
```

### 4. Agent Attribution in Responses

**Structured Response Format:**

```python
class AgentResponse:
    def __init__(self, agent_name: str, content: str, confidence: float):
        self.agent = agent_name
        self.content = content
        self.confidence = confidence
        self.timestamp = datetime.now()

class EnhancedShadowAgent:
    async def process_request(self, query: str, session_id: str):
        # Get agent responses with attribution
        agent_responses = []
        
        for agent_name, agent in self.agents.items():
            if agent_name in selected_agents:
                response = await agent.process(query, context)
                agent_responses.append(AgentResponse(
                    agent_name=agent_name,
                    content=response,
                    confidence=0.9
                ))
        
        # Aggregate with attribution
        final_response = await self.aggregate_with_attribution(agent_responses)
        
        return {
            "response": final_response,
            "agents": [
                {
                    "name": ar.agent,
                    "confidence": ar.confidence,
                    "contributed": ar.agent in final_response
                }
                for ar in agent_responses
            ]
        }
```

**Frontend Display:**
```jsx
// Agent attribution component
const AgentAttribution = ({ agents }) => (
    <div className="agent-attribution">
        <span>Answered by: </span>
        {agents.filter(a => a.contributed).map((agent, idx) => (
            <span key={idx} className={`agent-tag ${agent.name}`}>
                {agent.name} ({Math.round(agent.confidence * 100)}%)
            </span>
        ))}
    </div>
);
```

### 5. Streaming Response Implementation

**Backend Streaming:**

```python
from fastapi.responses import StreamingResponse
import asyncio

@app.post("/api/shadow/stream")
async def stream_chat(request: ShadowRequest):
    async def generate():
        # Stream from LLM
        async for chunk in shadow_agent.process_stream(request.query):
            yield f"data: {json.dumps({'chunk': chunk, 'agent': chunk.agent})}\n\n"
        
        # Send completion signal
        yield f"data: {json.dumps({'done': True})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

# Enhanced LLM connector with streaming
class StreamingLLMConnector:
    async def generate_stream(self, messages: List[Dict]):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url,
                json={
                    "messages": messages,
                    "stream": True,
                    "model": self.model
                },
                headers=self.headers
            ) as response:
                async for line in response.content:
                    if line.startswith(b'data: '):
                        data = json.loads(line[6:])
                        if data.get('choices'):
                            yield data['choices'][0]['delta'].get('content', '')
```

**Frontend Streaming:**

```javascript
// Streaming chat component
const StreamingChat = () => {
    const [messages, setMessages] = useState([]);
    const [isStreaming, setIsStreaming] = useState(false);
    
    const sendMessage = async (query) => {
        setIsStreaming(true);
        const currentMessage = { role: 'assistant', content: '', agent: null };
        setMessages(prev => [...prev, { role: 'user', content: query }, currentMessage]);
        
        const eventSource = new EventSource('/api/shadow/stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.done) {
                eventSource.close();
                setIsStreaming(false);
            } else {
                setMessages(prev => {
                    const newMessages = [...prev];
                    newMessages[newMessages.length - 1].content += data.chunk;
                    newMessages[newMessages.length - 1].agent = data.agent;
                    return newMessages;
                });
            }
        };
    };
};
```

## Implementation Priority

1. **Phase 1: Core Enhancements (Week 1-2)**
   - Implement session management backend
   - Add streaming support to LLM connector
   - Create session API endpoints

2. **Phase 2: Intelligence Layer (Week 3-4)**
   - Replace static classifier with LLM classifier
   - Implement memory-aware agent processing
   - Add memory extraction pipeline

3. **Phase 3: UI/UX Improvements (Week 5-6)**
   - Build session management UI
   - Add streaming chat interface
   - Implement agent attribution display

4. **Phase 4: Advanced Features (Week 7-8)**
   - Multi-agent collaboration workflows
   - Advanced memory reasoning
   - Performance optimization

## Technical Considerations

### Performance
- Cache LLM classification results
- Implement request batching for memory queries
- Use connection pooling for streaming

### Scalability
- Session storage should use Redis/PostgreSQL
- Memory vector store should use Pinecone/Weaviate
- Implement rate limiting

### Security
- Authenticate session access
- Sanitize memory extractions
- Implement API key rotation

## Conclusion

The Shadow AI system has a solid foundation but requires significant enhancements to achieve true agentic orchestration. The proposed changes will transform it from a static rule-based system to an intelligent, context-aware AI orchestrator with rich session management and real-time streaming capabilities.

These enhancements will enable:
- Dynamic, intelligent agent routing
- Persistent multi-session conversations
- Context-aware responses with memory integration
- Clear agent attribution
- Real-time streaming for better UX

The modular implementation approach allows for incremental deployment while maintaining system stability.
