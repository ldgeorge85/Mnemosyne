# MVP Requirements & Status

## What We Have (From Existing Mnemosyne)

### Working Backend Features ✅
- **Authentication**: JWT-based auth with refresh tokens
- **Chat Interface**: Enhanced chat with streaming responses
- **Memory System**: 
  - Capture and storage with pgvector
  - Vector embeddings for semantic search
  - Memory extraction from conversations
  - Importance scoring
- **Task Management**: CRUD operations with scheduling
- **LLM Integration**: OpenAI, vLLM, Ollama support
- **Database**: PostgreSQL with pgvector extension

### Backend Endpoints Available
- `/api/v1/auth/*` - Authentication
- `/api/v1/chat/*` - Chat conversations
- `/api/v1/memories/*` - Memory operations
- `/api/v1/tasks/*` - Task management
- `/api/v1/agents/*` - Agent interactions
- `/api/v1/llm/*` - LLM operations

---

## What We Need for Protocol MVP

### Phase 1: Get Basic Chat Working (Day 1-2)

**Backend Tasks:**
1. ✅ Backend already functional
2. ⚠️ Update configuration for new deployment
3. ⚠️ Ensure database migrations are current

**Frontend Tasks:**
1. ❌ Create minimal React frontend with chat UI
2. ❌ Implement authentication flow
3. ❌ Basic chat conversation display
4. ❌ Message input and streaming response

**Deployment Tasks:**
1. ❌ Update docker-compose.yml for unified deployment
2. ❌ Configure environment variables
3. ❌ Set up nginx for routing

### Phase 2: Add Protocol Layers (Day 3-5)

**Memory & Context:**
1. ❌ Add memory sidebar showing relevant context
2. ❌ Display task list in UI
3. ❌ Search memories interface

**Deep Signal Generation:**
1. ❌ Create signal generation endpoint
2. ❌ Build kartouche visualization
3. ❌ Display user's Deep Signal

**Agent Reflection:**
1. ❌ Port Shadow agents (Engineer, Librarian, Priest)
2. ❌ Add reflection UI panel
3. ❌ Mycelium coherence monitoring

### Phase 3: Collective Features (Day 6-7)

1. ❌ Sharing contracts implementation
2. ❌ K-anonymity enforcement
3. ❌ Basic collective view
4. ❌ Trust ceremony initiation

---

## Immediate Action Plan

### Step 1: Set Up Unified Deployment (2 hours)
```bash
# Copy Mnemosyne backend to protocol
cp -r /home/lewis/dev/personal/mnemosyne/backend /home/lewis/dev/personal/protocol/

# Update docker-compose.yml
# Configure environment variables
# Test deployment
```

### Step 2: Create Minimal Frontend (4 hours)
```bash
# Set up React with Vite
cd /home/lewis/dev/personal/protocol/frontend
npm create vite@latest . -- --template react-ts

# Install dependencies
npm install axios @chakra-ui/react zustand

# Create basic chat components
```

### Step 3: Connect & Test (2 hours)
- Wire up authentication
- Test chat functionality
- Verify memory capture
- Check task extraction

---

## File Structure for MVP

```
protocol/
├── backend/          # Copy from Mnemosyne
│   ├── app/
│   ├── alembic/
│   └── requirements.txt
├── frontend/         # New minimal UI
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat.tsx
│   │   │   ├── Login.tsx
│   │   │   └── MemorySidebar.tsx
│   │   ├── stores/
│   │   └── api/
│   └── package.json
├── docker-compose.yml
├── .env
└── docs/

```

---

## Success Criteria for Day 1 MVP

✅ **Must Have:**
- User can register/login
- User can have a conversation with AI
- AI remembers previous conversations
- Memories are being captured and stored
- Basic task extraction works

🔄 **Nice to Have:**
- Memory sidebar showing context
- Task list visible
- Search functionality

❌ **Can Wait:**
- Deep Signals
- Agent reflections
- Collective features
- Ritual ceremonies

---

## Commands to Get Started

```bash
# Never use docker-compose! Use docker compose
cd /home/lewis/dev/personal/protocol

# Step 1: Copy backend
cp -r ../mnemosyne/backend .
cp ../mnemosyne/.env.example .env

# Step 2: Update configuration
nano .env  # Add API keys

# Step 3: Start services
docker compose up -d postgres redis
docker compose up backend

# Step 4: In another terminal, set up frontend
cd frontend
npm create vite@latest . -- --template react-ts
npm install
npm run dev
```

---

## Time Estimate

**Realistic timeline to working MVP:**
- **Today (4-6 hours)**: Get backend running, create basic frontend
- **Tomorrow (4-6 hours)**: Polish UI, add memory sidebar, test thoroughly
- **Day 3**: Add Deep Signal generation
- **Day 4**: Add agent reflections
- **Week 2**: Collective features

**Absolute minimum to "working"**: 4-6 hours

The existing Mnemosyne backend is ~70% of what we need. We just need a frontend that embraces the chat-first philosophy!