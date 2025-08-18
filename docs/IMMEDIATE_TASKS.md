# Immediate Task Breakdown for Mnemosyne Protocol
*Tactical execution plan with specific, actionable tasks*

## Critical Path Forward

### Phase 0.5: Code Cleanup (URGENT - Do First)

#### Task Group A: Audit Current State
- [ ] List all auth-related files and identify competing patterns
- [ ] Document which auth system is actually running
- [ ] Identify all deprecated imports and dead code
- [ ] Find all hardcoded credentials and dev endpoints
- [ ] List all half-implemented features

#### Task Group B: Delete Ruthlessly  
- [ ] Remove `simple_auth.py` and dev-login endpoint
- [ ] Delete unused auth providers
- [ ] Remove competing auth patterns
- [ ] Strip out dead imports
- [ ] Delete placeholder/mock code
- [ ] Remove half-implemented features

#### Task Group C: Consolidate & Standardize
- [ ] Ensure AuthManager is the ONLY auth system
- [ ] Wire AuthManager into main.py properly
- [ ] Update all endpoints to use auth dependencies
- [ ] Fix import statements throughout
- [ ] Ensure clean startup with zero warnings

**Success Criteria**: 
- System starts with zero deprecation warnings
- Only one auth pattern exists
- All endpoints require authentication
- No dev backdoors remain

---

### Phase 1: Core Foundation (After Cleanup)

#### Task Group D: Frontend Auth Connection
- [ ] Update `AuthContext.tsx` to use `/api/v1/auth/*` endpoints
- [ ] Rewrite `api/auth.ts` for new auth flow
- [ ] Update Login component to use new auth
- [ ] Add token storage (httpOnly cookies or localStorage)
- [ ] Implement logout functionality
- [ ] Add auth refresh logic
- [ ] Test full login/logout cycle

#### Task Group E: Complete Memory CRUD
- [ ] Fix memory model in `models/memory.py`
- [ ] Complete CREATE endpoint with embedding generation
- [ ] Implement READ endpoint with proper filters
- [ ] Add UPDATE endpoint with versioning
- [ ] Create DELETE endpoint with soft delete
- [ ] Add memory search with vector similarity
- [ ] Wire up Qdrant for vector storage
- [ ] Add metadata extraction pipeline

#### Task Group F: Fix Chat System
- [ ] Fix user object handling in chat endpoint
- [ ] Update chat service to use correct user model
- [ ] Ensure chat history is persisted
- [ ] Add streaming response support
- [ ] Connect memory context to chat
- [ ] Test chat with authenticated user

#### Task Group G: Basic Persona Implementation
- [ ] Create `services/persona/` directory structure
- [ ] Implement BasePersona class with four modes
- [ ] Add persona prompts from PERSONA_WORLDVIEW.md
- [ ] Create mode switching logic
- [ ] Integrate persona into chat service
- [ ] Add basic receipts generation
- [ ] Test persona consistency

**Success Criteria**:
- User can login through frontend
- Full memory CRUD works with search
- Chat works with persona flavor
- Basic receipts for transparency

---

### Phase 1.5: Research Track (Parallel to Phase 1)

#### Task Group H: ICV Data Collection Setup
- [ ] Create `services/icv/` directory
- [ ] Build behavioral signal collection pipeline
- [ ] Add user consent flow
- [ ] Implement data collection endpoints
- [ ] Create analysis notebooks
- [ ] Set up metrics tracking
- [ ] Design validation protocol

#### Task Group I: Validation Studies
- [ ] Design ICV compression study (n=10-100)
- [ ] Create stability testing framework
- [ ] Build uniqueness validation tests
- [ ] Set up information retention metrics
- [ ] Prepare research documentation
- [ ] Plan publication strategy

**Success Criteria**:
- Data collection pipeline running
- Initial pilot data collected
- Validation framework ready
- Metrics being tracked

---

## Execution Order

### Week 1 Priority
1. Task Group A (Audit) - Know what we have
2. Task Group B (Delete) - Remove the mess
3. Task Group C (Consolidate) - Single patterns

### Week 2 Priority  
4. Task Group D (Frontend Auth) - Connect UI
5. Task Group F (Fix Chat) - Core feature working

### Week 3 Priority
6. Task Group E (Memory CRUD) - Complete data layer
7. Task Group G (Basic Persona) - Add personality

### Parallel Track
- Task Group H (ICV Setup) - Start data collection
- Task Group I (Validation) - Research framework

---

## Task Dependencies

```
Audit (A) → Delete (B) → Consolidate (C)
                            ↓
                    Frontend Auth (D)
                            ↓
                    Fix Chat (F) → Persona (G)
                            ↓
                    Memory CRUD (E)
                    
[Parallel: ICV Setup (H) → Validation (I)]
```

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
1. Delete `simple_auth.py`
2. Set `AUTH_REQUIRED=True` in config
3. Remove hardcoded credentials
4. Fix deprecation warnings
5. Update frontend auth endpoints

---

## Validation Gates

Before moving to next phase, verify:

### After Phase 0.5:
- [ ] Zero startup warnings
- [ ] Single auth pattern
- [ ] No dev endpoints

### After Phase 1:
- [ ] User can login/logout
- [ ] Chat works with auth
- [ ] Memory CRUD complete
- [ ] Persona integrated

### Before Phase 2:
- [ ] ICV validation data collected
- [ ] Initial results analyzed
- [ ] Go/no-go decision made

---

*This is your tactical execution guide. Work through tasks systematically. Don't skip ahead.*