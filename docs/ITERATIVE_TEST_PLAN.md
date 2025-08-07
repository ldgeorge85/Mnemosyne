# Iterative Development & Testing Plan

## Philosophy
- Test early, test often
- Get to "working" ASAP, then iterate
- Real functionality only (no mocking)

---

## Iteration 1: Backend Health Check (15 mins)

### Goal
Verify backend starts and responds

### Steps
```bash
# 1. Create .env from example
cp .env.example .env
# Edit .env with API keys

# 2. Start just postgres and redis
docker compose up -d postgres redis

# 3. Check they're running
docker compose ps

# 4. Start backend
docker compose up backend

# 5. Test health endpoint
curl http://localhost:8000/health
```

### Success Criteria
- [ ] PostgreSQL running
- [ ] Redis running
- [ ] Backend starts without errors
- [ ] Health endpoint returns 200

---

## Iteration 2: Authentication Test (30 mins)

### Goal
Can create user and login

### Steps
```bash
# 1. Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "password": "testpass123"}'

# 2. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "password": "testpass123"}'

# Save the token for next tests
```

### Success Criteria
- [ ] User registration works
- [ ] Login returns JWT token
- [ ] Token can be used for authenticated requests

---

## Iteration 3: Chat Functionality (30 mins)

### Goal
Have a conversation and verify memory capture

### Steps
```bash
# 1. Start a conversation
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, remember that I like Python programming"}'

# 2. Check memories were created
curl http://localhost:8000/api/v1/memories \
  -H "Authorization: Bearer $TOKEN"

# 3. Continue conversation
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "What programming language do I like?"}'
```

### Success Criteria
- [ ] Chat responds appropriately
- [ ] Memories are captured
- [ ] AI remembers previous context

---

## Iteration 4: Minimal Frontend (2 hours)

### Goal
Basic chat UI that works

### Components Needed
```
1. Login screen
2. Chat interface
3. Message input
4. Conversation display
```

### Steps
```bash
# 1. Create React app
cd frontend
npm create vite@latest . -- --template react-ts

# 2. Install minimal deps
npm install axios

# 3. Create components
# - Login.tsx
# - Chat.tsx
# - App.tsx

# 4. Test connection to backend
npm run dev
```

### Success Criteria
- [ ] Can login from UI
- [ ] Can send messages
- [ ] Can see responses
- [ ] Conversation persists

---

## Iteration 5: Memory Sidebar (1 hour)

### Goal
Show relevant memories during chat

### Steps
1. Add memory fetch to chat component
2. Create sidebar component
3. Display relevant memories
4. Update on new messages

### Success Criteria
- [ ] Memories visible in sidebar
- [ ] Updates as conversation progresses
- [ ] Shows relevance/importance

---

## Iteration 6: Deep Signal Generation (2 hours)

### Goal
Generate and display user's Deep Signal

### Backend Steps
1. Create signal generation endpoint
2. Analyze user's memories
3. Generate glyphs and coherence

### Frontend Steps
1. Add signal display component
2. Create kartouche visualization
3. Add to user profile area

### Success Criteria
- [ ] Signal generates from memories
- [ ] Kartouche displays correctly
- [ ] Updates as user evolves

---

## Testing Checkpoints

### After Each Iteration
1. ✅ Does it work?
2. ✅ Does it break anything?
3. ✅ Is it better than before?
4. ✅ Should we continue or fix?

### Daily Checkpoint
- What's working?
- What's broken?
- What's next priority?
- Any blockers?

### MVP Checkpoint
- [ ] Can register/login
- [ ] Can chat with memory
- [ ] Can see context
- [ ] Feels like "my AI"

---

## Current Status

**Where we are**: Iteration 1 - Need to test backend health

**Next step**: 
```bash
cp .env.example .env
nano .env  # Add API keys
docker compose up -d postgres redis
docker compose up backend
```

**Blocker**: Need API keys in .env file

---

## Notes

- Each iteration should be shippable
- If something breaks, we can roll back
- Document what works after each iteration
- Keep momentum - don't over-engineer
- "Working badly" > "Perfect plan"