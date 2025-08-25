# Immediate Task Breakdown for Mnemosyne Protocol
*Building Cognitive Sovereignty Through Iterative Development*

## ⭐ CURRENT PRIORITY: Trust Dynamics & Receipt Integration

**Current State (2025-08-25)**: 
- ✅ Memory UI Complete - Full CRUD interface with search
- ✅ Persona System Complete - 4 modes with worldview adapters
- ✅ UI/UX Fixed - Navigation, scrolling, chat history all working
- ✅ Receipts Backend Complete - Database, service, and API endpoints ready

**Immediate Implementation** (Sprint 6 - Accessibility):
- 🔴 Implement graduated sovereignty levels (Protected/Guided/Sovereign)
- 🔴 Create onboarding wizard with 5 personas
- 🔴 Build simplified UI for non-technical users
- 🔴 Add values alignment framework
- 🔴 Design trust event schema with appeals

**Next Sprint** (Sprint 7 - Bridge Building):
- 🟡 Mirror mode for persona (observe-only first)
- 🟡 Community standards layer (optional)
- 🟡 Specialized modes (Operational/Contemplative/Aesthetic)
- 🟡 Safety templates for vulnerable users
- 🟡 Pattern recognition without judgment

**Following Sprint** (Sprint 8 - Full Spectrum):
- 🟢 Trust dynamics with contextual awareness
- 🟢 Spectrum position tracking
- 🟢 User-editable consciousness notes
- 🟢 Insight pacing controls
- 🟢 Therapeutic mode with safeguards

## Critical Path Forward

### Guiding Principles
- **Contextual Presentation**: Adaptive masking based on context, not hierarchy
- **Full Spectrum Awareness**: Acknowledge all aspects of human experience
- **Mirror, Not Judge**: Show patterns without imposing moral values
- **Governance First**: Due process, appeals, and policy versioning
- **Natural Emergence**: Let advanced features grow organically
- **Model Agnostic**: All AI via user-configured API endpoints
- **Observe Before Enforce**: New features run in observe-only mode first

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

### Phase 1: Core Foundation ✅ BACKEND COMPLETE / 🔄 FRONTEND IN PROGRESS

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

#### Task Group G: Persona & Worldview Implementation ✅ COMPLETE (2025-08-25)

#### Task Group H: Accessibility & Onboarding 🆕 NEW (Sprint 6)
- [ ] Create `OnboardingWizard` component with persona selection
- [ ] Implement `SovereigntySelector` (Protected/Guided/Sovereign)
- [ ] Build persona-specific default configurations
- [ ] Create simplified UI components for non-technical users
- [ ] Add mode switching with data preservation
- [ ] Implement values framework importer
- [ ] Design safety templates system
- [ ] Add gradual revelation settings
- [ ] Build insight pacing controls
- [ ] Create therapeutic mode safeguards

#### Task Group I: Trust Dynamics & Governance 🆕 NEW (Sprint 7)
- [ ] Implement trust event system endpoints:
  - `POST /api/v1/trust/event` - Record trust-impacting events
  - `POST /api/v1/trust/appeal` - Appeal trust decisions
  - `GET /api/v1/trust/appeal/{id}` - Check appeal status
- [ ] Add Mirror mode endpoint:
  - `POST /api/v1/persona/mirror` - Pattern reflection
- [ ] Implement database tables:
  - `trust_events` table with neutral language
  - `appeals` table with due process
  - `consciousness_maps` table (opt-in only)
- [ ] Add governance features:
  - Policy versioning on all decisions
  - Separation of duties (reporter ≠ resolver)
  - Contextual visibility controls
  - Rate limiting and idempotency

**Acceptance Criteria**:
- New user can select persona and sovereignty level
- System adapts interface based on selection
- Users can switch modes without losing data
- Non-technical users can navigate easily
- Safety features are optional but discoverable

#### Task Group G: Persona & Worldview Implementation ✅ COMPLETE (2025-08-25)
- [x] Create `services/persona/` directory structure ✅
- [x] Implement BasePersona class with four modes ✅
- [x] Complete worldview adapter integration ✅
- [x] Implement PersonaManager with mode switching ✅
- [x] Create context analysis for auto-mode selection ✅
- [x] Add persona API endpoints ✅
- [x] Integrate with chat endpoint ✅
- [ ] Add productive variation (5% rate) - deferred
- [ ] Implement joy metrics tracking - deferred

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

### Phase 1.1: UI/UX Unification ✅ PHASE 1 & 2 COMPLETE

#### Task Group H: Critical UI Fixes ✅ COMPLETE
- [x] Fix chat scrolling (change to viewport-relative height) ✅
- [x] Fix tip text positioning ✅
- [x] Adjust chat message container for proper internal scrolling ✅
- [x] Test on mobile/tablet viewports ✅

#### Task Group I: Navigation & Shell ✅ COMPLETE
- [x] Create AppShell.tsx wrapper component ✅
- [x] Port Sidebar logic from Chakra to shadcn/ui ✅
- [x] Add chat history/sessions in sidebar ✅
- [x] Implement mobile-responsive navigation ✅
- [x] Wire router to use AppShell ✅

#### Task Group J: Progressive Enhancement (Phase 3)
- [ ] Port EnhancedChat features (intelligence indicators)
- [ ] Integrate existing MessageFormatter/MarkdownRenderer
- [ ] Add context panel (memories/tasks while chatting)
- [ ] Implement keyboard shortcuts (Cmd+K)
- [ ] Unify all pages under consistent navigation

**Success Criteria**:
- Chat works like ChatGPT/Claude (fixed input, scrolling messages)
- Navigation persists across all features
- Can switch between chat sessions
- Mobile responsive

---

### Phase 1.2: Task System Implementation ✅ BACKEND COMPLETE

#### Task Group K: Task System Foundation ✅ CORE COMPLETE
- [x] Create task model and database migrations ✅ COMPLETE
  - Basic fields: id, title, description, user_id, status ✅
  - Time fields: created_at, due_date, completed_at ✅
  - Privacy: visibility_mask ✅
  - Game mechanics, ICV evolution, collaboration fields ✅
- [x] Implement CRUD endpoints ✅ COMPLETE
  - POST /api/v1/tasks - Create with game mechanics ✅
  - GET /api/v1/tasks - List with filtering ✅
  - PATCH /api/v1/tasks/{id}/start - Mark in progress ✅
  - PATCH /api/v1/tasks/{id}/complete - Complete with XP ✅
  - DELETE /api/v1/tasks/{id} - Soft delete ✅
  - XP calculation, reputation tracking ✅

#### Next: Core UI & Testing
- [ ] Connect to receipt system
  - Generate receipt for every task action
  - Link receipts to consent ledger
  - Track task lifecycle events
- [x] Basic frontend integration ✅ COMPLETE
  - Task list component ✅
  - Create task form ✅

---

### Phase 1.3: Memory UI Implementation ✅ COMPLETE (2025-08-25)

#### Task Group L: Memory Interface Components ✅
- [x] Create memory list view ✅
  - Display memories with title, content preview, tags ✅
  - Show source type and importance score ✅
  - Display creation time with relative formatting ✅
  - Delete functionality with confirmation ✅
- [x] Build memory creation form ✅
  - Title and content fields ✅
  - Tag management with add/remove ✅
  - Source type selection ✅
  - Importance slider (0-100%) ✅
- [x] Add memory detail view ✅
  - Full content display ✅
  - Metadata visualization ✅
  - Edit/delete capabilities ✅
  - Navigation between views ✅
- [x] Implement search interface ✅
  - Text search functionality ✅
  - Search results with similarity scores ✅
  - Clear search to return to full list ✅

**Success Criteria Achieved**:
- Users can create, view, edit, and delete memories ✅
- Search works with text search ✅
- Memories properly categorized by source type ✅
- UI displays all relevant metadata ✅
  - Status toggle UI
- [ ] Testing and refinement
  - Integration tests
  - Receipt verification
  - Performance baseline

#### Future Enhancements

**Time Awareness**:
- Calendar integration, recurring tasks, smart scheduling

**Advanced Game Mechanics**:
- Achievement system, reputation building, progress visualization

**Collaboration Features**:
- Shared tasks, trust building, collective goals

**Success Criteria**:
- Tasks serve as action layer for all features
- Natural gamification without manipulation
- Time sovereignty through scheduling
- Trust building through collaboration

---

## Execution Order

### ✅ COMPLETE
1. **Backend Core** - Auth, Memory, Chat, Tasks all working
2. **Task System** - Full CRUD with game mechanics
3. **Production Deployment** - Docker, SSL, automated deployment ready
4. **Memory UI** - Full CRUD interface with search
5. **Persona System** - 4 modes with worldview adapters
6. **Receipts Backend** - Database, service, and API endpoints

### 🔴 IMMEDIATE PRIORITIES
1. **Receipt Integration** - Add generation to all endpoints
2. **Receipt UI** - Build viewing components and page
3. **Auth Providers** - Implement OAuth, API key authentication  
4. **Testing & Quality** - Integration tests, CI/CD pipeline

### 🟡 NEXT PHASE
1. **Time Awareness** - Calendar and scheduling
2. **Advanced Game Mechanics** - Achievements and reputation
3. **Trust Networks** - Progressive relationship building
4. **Agent Integration** - Connect philosophical agents

### Ongoing Parallel
- Natural emergence documentation
- Sovereignty pattern identification
- Joy coefficient optimization
- Resonance measurement

---

## Task Dependencies

```
Backend Foundation ✅
    ├── Auth (D) ✅
    ├── Memory CRUD (E) ✅
    ├── Chat System (F) ✅
    └── Task System (K) ✅
            ↓
    UI/UX Unification 🔴 CURRENT
    ├── Critical Fixes (H) ← IMMEDIATE
    ├── Navigation Shell (I)
    └── Progressive Enhancement (J)
            ↓
    Feature Integration
    ├── Personas (G)
    ├── Receipts/Transparency
    └── Context Awareness
            ↓
    Advanced Features
    ├── Trust Networks
    ├── Collective Intelligence
    └── ICV Validation

[Parallel Research Track: Synthetic Validation → Trust Design → Emergence Studies]
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

### After Phase 0.5: ✅ COMPLETE
- [x] Zero startup warnings
- [x] Single auth pattern
- [x] No dev endpoints

### After Phase 1: 
#### Backend ✅ COMPLETE
- [x] User can login/logout
- [x] Chat works with auth
- [x] Memory CRUD complete
- [x] Task system with XP
- [x] Production deployment ready

#### Frontend 🔄 IN PROGRESS
- [x] Basic pages working
- [ ] Unified navigation
- [ ] Chat UX fixed
- [ ] Mobile responsive
- [ ] All features accessible

### Before Phase 2:
- [ ] ICV validation data collected
- [ ] Initial results analyzed
- [ ] Go/no-go decision made on theoretical concepts
- [ ] Persona system proven valuable

---

*This is your tactical execution guide. Work through tasks systematically. Don't skip ahead.*