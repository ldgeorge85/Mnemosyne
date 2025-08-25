# Immediate Task Breakdown for Mnemosyne Protocol
*Building Cognitive Sovereignty Through Iterative Development*

## ⭐ NEW PRIORITY: Task System as Foundation

**Critical Insight**: Tasks are the action layer that unifies all features:
- **Memories** (past) → **Tasks** (present/future) → **Trust** (relationships)
- Natural gamification through quest mechanics
- Time sovereignty through calendaring
- Collective coordination substrate

**4-Week Sprint Plan**:
1. **Week 1**: Basic task CRUD with receipts
2. **Week 2**: Time awareness and scheduling
3. **Week 3**: Game mechanics integration
4. **Week 4**: Collaboration features

## Critical Path Forward

### Guiding Principles
- **Contextual Presentation**: Adaptive masking based on context, not hierarchy
- **Accelerated Personas**: Worldview integration moved to immediate priority
- **Synthetic Validation**: Test with synthetic identities before real users
- **Joy as Metric**: Track unexpected delight and creativity spikes
- **Natural Emergence**: Let advanced features grow organically
- **Model Agnostic**: All AI via user-configured API endpoints

### Phase 0.5: Code Cleanup ✅ COMPLETE

#### Task Group A: Audit Current State ✅
- [x] List all auth-related files and identify competing patterns
- [x] Document which auth system is actually running (AUTH_AUDIT_REPORT.md)
- [x] Identify all deprecated imports and dead code
- [x] Find all hardcoded credentials and dev endpoints
- [x] List all half-implemented features

#### Task Group B: Delete Ruthlessly ✅
- [x] Remove `simple_auth.py` and dev-login endpoint
- [x] Delete unused auth providers (auth_dev.py)
- [x] Remove competing auth patterns
- [x] Strip out dead imports
- [x] Delete placeholder/mock code
- [x] Remove duplicate API directory

#### Task Group C: Consolidate & Standardize ✅
- [x] Ensure AuthManager is the ONLY auth system
- [x] Wire AuthManager into main.py properly
- [x] Update all endpoints to use auth dependencies
- [x] Fix import statements throughout
- [x] Authentication now required (401 responses)

**Success Criteria**: 
- System starts with zero deprecation warnings
- Only one auth pattern exists
- All endpoints require authentication
- No dev backdoors remain

---

### Phase 1: Core Foundation (Current Focus)

#### Task Group D: Frontend Auth Connection ✅ COMPLETE (2025-08-22)
- [x] Update `AuthContext.tsx` to use `/api/v1/auth/*` endpoints
- [x] Rewrite `api/auth.ts` for new auth flow
- [x] Update Login component to use new auth
- [x] Add token storage (httpOnly cookies or localStorage)
- [x] Implement logout functionality
- [x] Add auth refresh logic
- [x] Test full login/logout cycle

#### Task Group E: Complete Memory CRUD ✅ COMPLETE (2025-08-24)
- [x] All CRUD operations working (CREATE/READ/UPDATE/DELETE)
- [x] Embeddings with external API (1024d vectors)
- [x] Qdrant integration storing vectors successfully
- [x] Authentication properly integrated
- [ ] Add vector similarity search (next priority)
- [ ] Add metadata extraction (enhancement)

**Environment Status**:
- OpenAI LLM: ✅ Configured (InnoGPT)
- Embeddings: ✅ External API working (`embedding-inno1` 1024d)
- Qdrant: ✅ Running and storing vectors
- PostgreSQL: ✅ Running
- Redis: ✅ Running

#### Task Group F: Fix Chat System 🔄 UPDATED (2025-08-24)
- [x] Fix user object handling in chat endpoint (uses AuthUser)
- [x] Update chat service to use correct user model
- [x] Integrate persona support (base implementation)
- [x] Test chat with authenticated user ✅ WORKING
- [x] Ensure chat history is persisted ✅ SAVING TO DB
- [ ] Add streaming response support (enhancement)
- [ ] Connect memory context to chat (next priority)

#### Task Group G: Persona & Worldview Implementation 🔴 ACCELERATED PRIORITY
- [x] Create `services/persona/` directory structure
- [x] Implement BasePersona class with four modes
- [ ] **IMMEDIATE**: Complete worldview adapter integration
- [ ] **IMMEDIATE**: Implement contextual presentation system
- [ ] **IMMEDIATE**: Add productive variation (5% rate)
- [ ] Create mode switching logic (Confidant/Mentor/Mediator/Guardian)
- [ ] Build receipts and transparency system
- [ ] Implement joy metrics tracking

**Success Criteria**:
- User can login through frontend
- Full memory CRUD works with search
- Chat works with persona flavor
- Basic receipts for transparency

---

### Phase 1.5: Research Track (Parallel - START IMMEDIATELY)

#### Task Group H: Synthetic ICV Validation 🔴 HIGH PRIORITY
- [ ] **IMMEDIATE**: Generate synthetic identities for testing
- [ ] **IMMEDIATE**: Validate compression algorithms before real users
- [ ] Test holographic properties (each part contains whole)
- [ ] Measure temporal stability (70/30 model)
- [ ] Implement productive variation testing
- [ ] Create analysis notebooks
- [ ] Design joy metric framework

#### Task Group I: Trust Network Design
- [ ] Design progressive trust exchange protocol
- [ ] Create cryptographic commitment schemes
- [ ] Define trust decay mechanisms
- [ ] Build trust visualization concepts
- [ ] Plan pilot with 10-50 users

#### Task Group J: Natural Emergence Studies
- [ ] Observe organic trust network formation
- [ ] Document clustering patterns
- [ ] Measure resonance between synthetic identities
- [ ] Track emergence of coordination
- [ ] Identify sovereignty preservation patterns
- [ ] Create metrics for system health

**Success Criteria**:
- Data collection pipeline running
- Initial pilot data collected
- Validation framework ready
- Metrics being tracked

---

### Phase 1.2: Task System Implementation ⭐ NEW PRIORITY

#### Task Group K: Task System Foundation (Week 1)
- [ ] **Day 1**: Create task model and database migrations
  - Basic fields: id, title, description, user_id, status
  - Time fields: created_at, due_date, completed_at
  - Privacy: visibility_mask
- [ ] **Day 2**: Implement CRUD endpoints
  - POST /api/v1/tasks - Create with receipt
  - GET /api/v1/tasks - List with filtering
  - PATCH /api/v1/tasks/{id} - Update status
  - DELETE /api/v1/tasks/{id} - Soft delete
- [ ] **Day 3**: Connect to receipt system
  - Generate receipt for every task action
  - Link receipts to consent ledger
  - Track task lifecycle events
- [ ] **Day 4**: Basic frontend integration
  - Task list component
  - Create task form
  - Status toggle UI
- [ ] **Day 5**: Testing and refinement
  - Integration tests
  - Receipt verification
  - Performance baseline

#### Task Group L: Time Awareness (Week 2)
- [ ] **Calendar Integration**
  - Add scheduling fields to task model
  - Create calendar view endpoint (iCal format)
  - Frontend calendar component
- [ ] **Recurring Tasks**
  - RRULE support for recurrence patterns
  - Template system for habits
  - Automatic instance generation
- [ ] **Smart Scheduling**
  - Peak performance window detection
  - Energy-aware scheduling
  - Conflict detection
- [ ] **Time Tracking**
  - Estimated vs actual duration
  - Time investment analytics
  - Productivity patterns

#### Task Group M: Game Mechanics (Week 3)
- [ ] **Quest Classification**
  - Classify tasks as quest types
  - Difficulty rating system
  - Reward calculation
- [ ] **Achievement System**
  - Pattern detection in task completion
  - Achievement unlocking
  - Capability grants
- [ ] **Reputation Building**
  - Multi-dimensional reputation model
  - Task-based reputation gains
  - Decay implementation
- [ ] **Progress Visualization**
  - XP and level tracking
  - Progress bars and streaks
  - Achievement gallery

#### Task Group N: Collaboration (Week 4)
- [ ] **Shared Tasks**
  - Multi-assignee support
  - Progress synchronization
  - Completion consensus
- [ ] **Trust Building Tasks**
  - Paired challenge templates
  - Trust impact calculation
  - Reciprocity tracking
- [ ] **Collective Goals**
  - Break down group objectives
  - Role-based task assignment
  - Dependency management
- [ ] **Coordination Tools**
  - Find common availability
  - Sync point scheduling
  - Progress dashboards

**Success Criteria**:
- Tasks serve as action layer for all features
- Natural gamification without manipulation
- Time sovereignty through scheduling
- Trust building through collaboration

---

## Execution Order (UPDATED - With Task System)

### Immediate Priority (This Week) ⭐ NEW PRIORITY
1. **Task Group K** (Task System Foundation) - Action layer for everything
2. **Task Group G** (Personas) - Guides task suggestions
3. **Task Group L** (Consent Ledger) - Every task generates receipts
4. **Task Group H** (Synthetic ICV) - Validation through task patterns
5. Contextual presentation design - Tasks respect masks

### Next Sprint (Weeks 2-3)
6. Trust network protocol design
7. Natural clustering observation
8. Worldview adapter completion (3+ contexts)
9. Receipts and transparency system
10. Vector similarity search for memories

### Following Month
11. Trust exchange implementation
12. Agent communication protocols
13. Reputation and trust scoring
14. Progressive disclosure mechanisms

### Ongoing Parallel
- Natural emergence documentation
- Sovereignty pattern identification
- Joy coefficient optimization
- Resonance measurement

---

## Task Dependencies

```
Audit (A) → Delete (B) → Consolidate (C) ✅
                            ↓
                    Frontend Auth (D) ✅
                            ↓
                    Memory CRUD (E) ✅
                            ↓
                    Task System (K) ← NEW FOUNDATION
                    ↙        ↓        ↘
            Personas (G)  Time (L)  Game Mechanics (M)
                    ↓        ↓        ↓
                    Collaboration (N)
                            ↓
                    Trust Networks → Collective Intelligence
                    
[Parallel: ICV Setup (H) → Trust Design (I) → Emergence Studies (J)]
```

---

---

## For Each Task Session

When starting a task, provide this context to AI:

```markdown
PROJECT: Mnemosyne Protocol
CURRENT PHASE: [Phase 0.5/1/1.5]
TASK GROUP: [A-I]
SPECIFIC TASK: [exact task from list]
FILES INVOLVED: [list files]
DEPENDENCIES: [what must be done first]
SUCCESS CRITERIA: [how to know it's done]
TEST COMMAND: [how to verify]
```

---

## Red Flags to Stop Work

STOP and reassess if you encounter:
- More than 3 competing patterns for same feature
- Critical security vulnerability in running code  
- Database schema fundamentally broken
- Missing critical dependencies
- Tests failing on main branch

---

## Quick Wins First

These can be done immediately:
1. ✅ Delete `simple_auth.py` (DONE)
2. ✅ Set `AUTH_REQUIRED=True` in config (DONE)
3. ✅ Remove hardcoded credentials (DONE)
4. ✅ Fix deprecation warnings (DONE)
5. ✅ Update frontend auth endpoints (DONE)

---

## Validation Gates

Before moving to next phase, verify:

### After Phase 0.5:
- [ ] Zero startup warnings
- [ ] Single auth pattern
- [ ] No dev endpoints

### After Phase 1:
- [x] User can login/logout
- [x] Chat works with auth
- [x] Memory CRUD complete
- [ ] Persona fully integrated
- [ ] Worldview adapters active
- [ ] ICV validation data collected

### Before Phase 2:
- [ ] ICV validation data collected
- [ ] Initial results analyzed
- [ ] Go/no-go decision made on theoretical concepts
- [ ] Persona system proven valuable

---

*This is your tactical execution guide. Work through tasks systematically. Don't skip ahead.*