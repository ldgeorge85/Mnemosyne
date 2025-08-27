# Mnemosyne Protocol: Technical Roadmap
*Building Cognitive Sovereignty Infrastructure*

## Overview

This roadmap implements **cognitive sovereignty** through iterative development, with each phase adding depth while maintaining utility. The system grows from personal tool to collective intelligence platform through natural emergence rather than forced complexity.

**Development Philosophy**: Build useful infrastructure that inherently preserves sovereignty. Advanced features emerge organically as trust and adoption grow.

## Current Status

### Backend Complete ✅
- ✅ **Authentication System** - Secure multi-provider auth
- ✅ **Memory CRUD** - Complete with vector embeddings
- ✅ **Chat System** - Authenticated conversations with persistence
  - ✅ Local conversation history tracking (localStorage)
  - ✅ SSE streaming endpoint `/api/v1/chat/stream`
  - ✅ Conversation creation and management UI
  - ✅ Persona mode switching in chat interface
- ✅ **Task System** - Full CRUD with game mechanics and XP
- ✅ **Infrastructure** - Docker, PostgreSQL, Redis, Qdrant operational
- ✅ **Production Deployment** - SSL, automated deployment ready

### Frontend Complete ✅
- ✅ **Basic Pages** - Login, Dashboard, Chat, Tasks, Memories all working
- ✅ **UI/UX Issues Fixed** - Chat scrolling fixed, persistent navigation added
- ✅ **Shell Navigation** - AppShell with sidebar, chat history working
- ✅ **Task UI** - Complete with list and creation forms
- ✅ **Memory UI** - Full CRUD interface implemented (Phase 1.3)
- ✅ **Chat Streaming** - Server-sent events with SSE endpoint working (2025-08-26)
- ✅ **UI Library** - shadcn/ui migration complete (Chakra removed)
- ✅ **UI Standardization** - Tasks, Memories, Receipts pages unified (2025-08-27)
- ✅ **Pagination** - "Load More" functionality prevents bottlenecks (2025-08-27)
- ✅ **Token Management** - 64k context window with smart truncation (2025-08-27)
- ✅ **Persona Badges** - Per-message mode display (2025-08-27)

### Completed Features
- ✅ **Persona System** - Complete with 5 modes (including Mirror), worldview adapters, chat integration
- ✅ **Receipts System** - FULL STACK COMPLETE - Database, API, and UI viewer working!
- ✅ **Trust System** - Database models, migrations, and API endpoints complete
- ✅ **Task System** - FULL STACK COMPLETE - Backend, API, UI with forms and lists!
- ✅ **Memory System** - FULL STACK COMPLETE - CRUD, embeddings, UI with search!
- ✅ **Mirror Mode** - Pattern reflection without judgment (2025-08-26)
- ✅ **Agentic Flow** - ReAct pattern with LLM reasoning (2025-08-26)
- ✅ **LLM Persona Selection** - 92% confidence achieved replacing keywords
- ✅ **Parallel Action Execution** - asyncio.gather() for efficiency
- ✅ **Proactive Suggestions** - Context-aware next steps
- ✅ **LIST_TASKS Action** - WIRED to task service, retrieves and displays tasks!
- ✅ **Task Queries** - Agentic chat properly handles task-related questions!

### In Development
- 🚀 **Phase 1.B: Shadow/Dialogue Integration** - AGENTS EXIST, need connection (NEXT PRIORITY)
- ❌ **Auth Providers** - Only Static works, OAuth/DID/API are stubs
- 🟡 **Shadow Agents** - Engineer, Librarian, Priest agents exist but not connected
- 🟡 **Dialogue Agents** - 50+ philosophical agents exist but not connected

### Research Track (Parallel)
- 🔬 **Identity Compression** - Holographic representation validation
- 🔬 **Game Mechanics** - Task gamification and engagement patterns
- 🔬 **Productive Variation** - Creative randomness (5% target rate)
- 🔬 **Natural Clustering** - Organic group formation
- 🔬 **Joy Metrics** - System delight measurement

## Development Philosophy

### Understanding Spectrum
- **Everyone**: Full access to all features and capabilities
- **Some**: Understand sovereignty architecture connections
- **Few**: Grasp complete liberation framework

### Design Principles
- **Useful First**: Every feature provides immediate value
- **Sovereignty Embedded**: Privacy and control in architecture
- **Natural Emergence**: Advanced features grow organically
- **Full Spectrum Awareness**: Acknowledge all aspects of human experience
- **Progressive Complexity**: Simple core, validated additions
- **Model Agnostic**: Interface with AI via user-configured endpoints
- **Mirror, Not Judge**: Show patterns without imposing values
- **Architectural Defense**: Make authoritarian use structurally difficult
- **Pattern Observation**: Track spectrums, not good/evil
- **User Interpretation**: System observes, users determine meaning

## Phase Structure

### Phase 0: Security Activation ✅ COMPLETE
**Status**: COMPLETED
**Goal**: Activate existing security components to eliminate vulnerabilities

#### Tasks Completed:
1. ✅ Enable AuthManager in main.py
2. ✅ Wire AuthManager into application startup  
3. ✅ Configure Static auth provider for development
4. ✅ Remove dev-login endpoints
5. ✅ Fix user object handling in chat endpoint
6. ⏳ Add rate limiting middleware (deferred to Phase 1)
7. ✅ CORS configured properly
8. ✅ Set AUTH_REQUIRED=True

#### Success Criteria Achieved:
- ✅ All API endpoints require authentication
- ✅ No hardcoded credentials in codebase
- ✅ Zero critical security vulnerabilities
- ✅ User object properly passed to all handlers

**See**: [SECURITY_ACTIVATION_LOG.md](SECURITY_ACTIVATION_LOG.md) for details

---

### Phase 0.5: Code Cleanup & Consolidation ✅ COMPLETE
**Status**: COMPLETED - August 18, 2025
**Goal**: Strip down to genuinely useful components, delete all half-implementations

#### What We Kept:
- [x] AuthManager (sophisticated multi-provider system)
- [x] Docker/database setup (working infrastructure)
- [x] Config structure (settings management)
- [x] Basic FastAPI skeleton
- [x] Error handling and logging setup

#### What We Deleted:
- [x] All three competing auth dependency systems
- [x] simple_auth.py and auth_dev.py
- [x] Mock user logic and dev bypasses
- [x] Duplicate API directory (backend/api/)
- [x] Test/dev shortcuts and hardcoded values

#### Clean Implementation Achieved:
- [x] One auth pattern everywhere (AuthManager)
- [x] Clean API structure with consistent auth
- [x] All endpoints using AuthUser from AuthManager
- [x] Proper separation of concerns
- [x] Authentication enforced (401 on unauthenticated)

#### Success Criteria:
- [x] Auth consolidated to single pattern
- [ ] All endpoints use same auth pattern
- [ ] Can build and run without errors
- [ ] Clean, understandable codebase
- [ ] Ready for fresh development

---

### Phase 1: Core Foundation + Accessibility
**Status**: Phase 1.A COMPLETE ✅, Phase 1.B Shadow/Dialogue integration NEXT
**Goal**: Sovereign personal AI accessible to diverse worldviews

#### Phase 1.A: Agentic Enhancement ✅ COMPLETE (2025-08-27)
- ✅ Memory CRUD with embeddings
- ✅ Chat system with authentication and persistence
- ✅ Task system with game mechanics
- ✅ Vector storage integration
- ✅ Authentication system
- ✅ Production deployment ready
- ✅ **Agentic Flow with ReAct pattern**
- ✅ **LLM-driven persona selection (92% confidence)**
- ✅ **Parallel action execution**
- ✅ **Proactive suggestions**
- ✅ **Configurable LLM temperatures per persona**
- ✅ **Flexible system prompt modes (embedded/separate)**
- ✅ **Reasoning level support for advanced models**
- ✅ **SSE streaming with status updates**

#### Phase 1.B: Shadow & Dialogue Integration (NEXT PRIORITY)
- 🔴 Connect Shadow agents (Engineer, Librarian, Priest) - agents exist, need wiring
- 🔴 Connect Dialogue agents (50+ philosophical) - agents exist, need wiring
- 🔴 Wire up CREATE_MEMORY action to executor
- 🔴 Wire up UPDATE_TASK action to executor
- 🔴 Implement DECOMPOSE_TASK for complex tasks
- 🔴 Add ANALYZE_PATTERNS with real analysis
- 🔴 Test multi-agent collaboration
- 🔴 Add agent-specific prompts

#### Phase 1.D: Accessibility Layer
- 🔴 **Graduated Sovereignty**: Protected/Guided/Sovereign modes
- 🔴 **Onboarding Personas**: 5 worldview-specific entry points
- 🔴 **Values Alignment**: Import moral/ethical frameworks
- 🔴 **Simplified UI**: Non-technical user interfaces
- 🔴 **Safety Templates**: Optional protection for vulnerable users

#### Success Metrics
- User satisfaction with persona interactions
- Successful cross-cultural adaptations
- Trust network formation rate
- Joy coefficient (unexpected delight events)

#### Memory System with ICV
- [x] Complete memory CRUD operations ✅ COMPLETE (2025-08-24)
- [ ] Implement ICV-aware memory storage
- [x] Wire up vector embeddings ✅ (using Qdrant with 1024d vectors)
- [x] Add semantic search ✅ (text search working)
- [ ] Add worldview context to search
- [ ] Implement importance scoring based on user values
- [ ] Create receipts for memory operations

#### Chat System ✅ COMPLETE
- [x] Chat endpoint with proper user context ✅
- [x] Streaming endpoint working with SSE ✅
- [x] Conversation persistence in database ✅
- [x] Message history stored and retrievable ✅
- [x] Implement persona voice ✅ (5 modes including Mirror)
- [x] Create mode switching ✅ (PersonaManager with API)
- [x] Add receipts for transparency ✅ (receipts generated for chat)

#### Frontend Integration
- [x] Complete auth flow with backend ✅
- [x] Chat interface with streaming ✅
- [x] Task management UI ✅
- [x] Implement memory UI components ✅ COMPLETE (2025-08-25)
- [x] Add memory search interface ✅ COMPLETE (2025-08-25)
- [x] Receipt viewer UI ✅ COMPLETE (2025-08-26)
- [ ] Add user settings page

#### Testing & Quality
- [ ] Achieve 60% test coverage
- [ ] Add integration tests for critical paths
- [ ] Setup CI/CD pipeline (GitHub Actions)
- [ ] Add error monitoring (Sentry)
- [ ] Test LLM responses with new model

---

### Phase 1.2: Task System - Action Layer ⭐ CORE COMPLETE
**Status**: Backend complete, needs frontend
**Goal**: Unified task tracking with time awareness and game mechanics

#### Complete
- [x] Task model with game mechanics ✅
- [x] CRUD endpoints with XP calculation ✅
- [x] Start/complete task flow ✅
- [x] Quest types and difficulty levels ✅
- [x] Experience point calculation ✅

#### Immediate Needs (for MVP)
- [ ] Basic frontend task components
- [ ] Connect to existing UI
- [ ] Deploy for testing

#### Future Enhancements
- [ ] Receipt system for transparency
- [ ] Time awareness and scheduling
- [ ] Achievement system
- [ ] Collaboration features

#### Integration Points
- **Persona System**: Tasks suggested by persona mode
- **Memory System**: Completed tasks become memories
- **Trust Networks**: Shared tasks build trust
- **ICV Evolution**: Task patterns shape identity
- **Receipts**: Every task action logged

#### Success Metrics
- Tasks bridge past (memories) to future (intentions)
- Natural gamification without dark patterns
- Trust building through concrete collaboration
- Time sovereignty through scheduling control

---

### Phase 1.5: Research Track - Sovereignty & Governance
**Parallel to Phase 1 and 1.A**
**Goal**: Validate cognitive sovereignty with robust governance
**Track**: Research with immediate application

#### Trust Dynamics & Governance ✅ COMPLETE (2025-08-26)
- [x] Implement trust event system with neutral language ✅
- [x] Build appeals process with due process guarantees ✅
- [x] Add policy versioning for all decisions ✅
- [x] Create separation of duties (reporter ≠ resolver) ✅
- [x] Design contextual visibility controls ✅
- [x] Implement bounded trust parameters (max 20% monthly change) ✅
- [x] Add progressive trust exchange protocol (5 levels) ✅

##### Trust Progression Levels
1. **Awareness** - Agents have met (zero-knowledge proof)
2. **Recognition** - Minimal verified disclosure
3. **Familiarity** - Shared interaction history
4. **Shared Memory** - Mutual experiences established
5. **Deep Trust** - Full alignment and revelation

##### Database Schema for Trust System
```sql
-- Trust events tracking (neutral language)
CREATE TABLE trust_events (
    id UUID PRIMARY KEY,
    actor_id UUID REFERENCES users(id),
    subject_id UUID REFERENCES users(id),
    event_type VARCHAR(50) NOT NULL,  -- 'disclosure', 'interaction', 'conflict'
    trust_delta FLOAT,  -- Can be positive or negative
    context JSONB,
    -- Governance fields
    reporter_id UUID REFERENCES users(id),
    resolver_id UUID REFERENCES users(id),  -- Must be different from reporter
    appeal_id UUID REFERENCES appeals(id),
    policy_version VARCHAR(20) DEFAULT 'v1',
    -- Sovereignty preservation
    visibility_scope VARCHAR(20) DEFAULT 'private',
    user_consent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Appeals process with due process
CREATE TABLE appeals (
    id UUID PRIMARY KEY,
    trust_event_id UUID REFERENCES trust_events(id),
    appellant_id UUID REFERENCES users(id),
    status VARCHAR(20) NOT NULL,
    appeal_reason TEXT,
    resolution TEXT,
    submitted_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    -- Due process fields
    evidence JSONB,
    witness_ids UUID[],
    review_board_ids UUID[]  -- Multiple reviewers for important cases
);
```

#### Spectrum Awareness Features
- [x] Track behavioral patterns on spectrums ✅ COMPLETE (2025-08-26)
- [x] Build Mirror mode for persona (reflection without judgment) ✅ COMPLETE (2025-08-26)
- [x] Create consciousness mapping (opt-in only) ✅ COMPLETE (2025-08-26)
- [x] Implement pattern recognition without moral judgment ✅ COMPLETE (2025-08-26)
- [ ] Add user-editable notes on their patterns

##### Database Schema for Consciousness Mapping
```sql
-- Consciousness mapping (opt-in, not "shadow profiles")
CREATE TABLE consciousness_maps (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    conscious_values JSONB,
    observed_patterns JSONB,
    emerging_patterns JSONB,
    integration_score FLOAT DEFAULT 0.0,
    last_updated TIMESTAMP,
    user_consent BOOLEAN NOT NULL DEFAULT FALSE,
    user_notes TEXT  -- User can add their own context
);
```

#### Synthetic ICV Pilots (Accelerated)
- Generate synthetic identities for testing
- Validate compression before real users
- Test holographic properties (each part contains whole)
- Measure temporal stability (70/30 model)
- Include shadow aspects in compression

#### Natural Clustering Studies
- Observe organic group formation
- Measure trust network emergence
- Identify resonance patterns
- Add spectrum diversity indicators (descriptive only)

#### Voice & Archetype Refinement
- [ ] Tune persona voice for each mode
- [ ] Implement Mirror mode for pattern reflection
- [ ] Create aesthetic customization options
- [ ] Build neutral observation language
- [ ] Test reflection vs judgment balance

#### ICV Blending Engine
- [ ] Create rules engine for ICV adaptation
- [ ] Implement value weighting system
- [ ] Build preference learning from interactions
- [ ] Create user override mechanisms
- [ ] Implement reset/recalibration functions

#### Receipts Visualization
- [ ] Expand receipts with decision trees
- [ ] Create transparency dashboard
- [ ] Build trust metrics visualization
- [ ] Implement influence tracking
- [ ] Add exportable trust logs

#### Philosophical Integration
- [ ] Deepen Stoic resilience patterns
- [ ] Implement Confucian harmony in mediations
- [ ] Add Sufi compassion to guardian mode
- [ ] Integrate Buddhist mindfulness prompts
- [ ] Balance Western humanist agency

---

### Phase 2: Trust Networks & Advanced Features
**Prerequisites**: Phase 1 complete
**Goal**: Enable natural group formation and advanced capabilities
**Timeline**: Months 2-4

#### Trust Network Implementation
- Progressive trust building (5 phases)
- Natural cluster formation
- Resonance detection algorithms
- Advanced features for high-trust groups

#### Productive Variation System
- Implement 5% controlled randomness
- Semantic jitter for creativity
- Paradox injection for flexibility
- Silence as sovereign response

#### Contextual Presentation
- Professional context (competence focus)
- Personal context (chosen vulnerability)
- Public context (protective masking)
- Core contributor view (full depth)
- Dynamic depth adjustment

---

### Phase 2.5: Research Track - Trust & Resonance Validation
**Parallel to Phase 2**
**Goal**: Validate Progressive Trust Exchange and Resonance models
**Track**: Research/experimental

#### Validation Protocol
- Test trust progression in controlled interactions
- Measure resonance predictions vs actual compatibility
- Validate cryptographic commitment schemes
- Test privacy-preserving computation

### Phase 3: Emergence & Liberation
**Prerequisites**: Phase 2 complete
**Goal**: Natural emergence of advanced capabilities
**Timeline**: Months 9-12

#### Advanced Trust Features
- High-trust clusters unlock special capabilities
- Natural emergence of coordination patterns
- Organic cell formation without central planning
- Sovereignty features activate progressively

#### Privacy Through Architecture
- Zero-knowledge proofs for sensitive operations
- Encrypted identity compression
- User-owned model weights
- Proof-carrying actions for all operations

---

### Phase 4: Collective Intelligence
**Prerequisites**: Phase 3 trust networks established
**Goal**: Enable collective cognition while preserving sovereignty
**Timeline**: Year 2+

#### Natural Collective Formation
- Groups form through resonance, not assignment
- Collective memory emerges from individual contributions
- Shared decision-making without central control
- Time-bounded collaborations

#### Governance Without Control
- Consensus through resonance
- Natural leadership emergence
- Conflict resolution through multi-perspective validation
- Dissolution when purpose completes

---

### Phase 5: Agent Communication & Networks
**Prerequisites**: Phase 4 complete
**Goal**: Enable agent-to-agent communication
**Track**: Conditional on prior validations

#### Agent Communication
- [ ] Define agent communication protocol
- [ ] Implement secure message passing
- [ ] Add agent discovery mechanism
- [ ] Create handshake protocol

#### Trust Mechanics
- [ ] Implement trust scoring algorithm
- [ ] Add reputation tracking
- [ ] Create trust decay mechanism
- [ ] Build trust visualization

#### Progressive Disclosure
- [ ] Implement zero-knowledge proofs
- [ ] Add graduated information sharing
- [ ] Create privacy negotiation
- [ ] Build trust-based access control

---

### Phase 6: Collective Intelligence Experiments
**Prerequisites**: Phase 5 complete, strong research validation
**Goal**: Test collective intelligence emergence
**Track**: Highly experimental

#### Group Mechanics
- [ ] Implement collective creation
- [ ] Add membership management
- [ ] Create role-based permissions
- [ ] Build invitation system

#### Collective Intelligence
- [ ] Implement voting mechanisms
- [ ] Add consensus algorithms
- [ ] Create shared memory pool
- [ ] Build collective decision tracking

#### Governance
- [ ] Implement quadratic voting
- [ ] Add proposal system
- [ ] Create treasury management
- [ ] Build dispute resolution

---

### Phase 7: Federation & Scale
**Prerequisites**: Phase 6 validated
**Goal**: Enable inter-collective coordination
**Track**: Future vision

#### Federation Protocol
- [ ] Define inter-collective protocol
- [ ] Implement collective discovery
- [ ] Add federation handshake
- [ ] Create resource sharing

#### Distributed Systems
- [ ] Add distributed consensus (Tendermint)
- [ ] Implement state synchronization
- [ ] Create conflict resolution
- [ ] Build federation governance

---

### Phase 8: Production Scale
**Prerequisites**: Core features stable
**Goal**: Optimize for production scale
**Track**: Engineering optimization

#### Performance Optimization
- [ ] Implement caching strategies
- [ ] Add database indexing
- [ ] Optimize vector searches
- [ ] Create load balancing

#### Infrastructure
- [ ] Migrate to Kubernetes
- [ ] Add horizontal scaling
- [ ] Implement service mesh
- [ ] Create monitoring dashboard

---

## Technology Stack

### Track 1 - Proven Technologies
- **Backend**: FastAPI, PostgreSQL, Async SQLAlchemy, Redis/KeyDB
- **Frontend**: React, TypeScript, shadcn/ui (migration complete)
- **Vector Store**: Qdrant for embeddings
- **AI Integration**: Model-agnostic API endpoints (user-configured)
- **Infrastructure**: Docker, docker compose
- **Testing**: Pytest, no mocks policy

### Track 2 - Research/Experimental
- **Identity Compression**: Custom algorithms [THEORETICAL]
- **Trust Exchange**: ZK proofs, Pedersen commitments [THEORETICAL]
- **Resonance**: Multi-model computation [THEORETICAL]
- **Collective Intelligence**: Synchronization models [THEORETICAL]

### Future Considerations
- **Identity**: W3C DIDs when needed
- **Storage**: IPFS if decentralization required
- **Scale**: Kubernetes when load demands

## Risk Mitigation

### Technical Risks
| Risk | Mitigation |
|------|------------|
| Security vulnerabilities | Immediate Phase 0 activation |
| Scalability issues | Progressive optimization |
| Integration failures | Incremental development |
| Privacy breaches | Formal verification |

### Execution Risks
| Risk | Mitigation |
|------|------------|
| Scope creep | Strict phase boundaries |
| Integration debt | Continuous integration |
| Documentation lag | Doc-as-code approach |
| Testing gaps | TDD for critical paths |

## Success Metrics

### Phase Completion Criteria
- Phase 0: Zero security vulnerabilities
- Phase 1: Working single-user application with persona
- Phase 2: Trust networks forming naturally
- Phase 3: Cryptographic privacy active
- Phase 4: DID authentication working
- Phase 5: Two agents exchanging trust
- Phase 6: First collective decision
- Phase 7: Two collectives interacting
- Phase 8: 1000+ concurrent agents

### Key Performance Indicators
- User retention: >60% monthly active
- Agent interactions: >100 daily per user
- Trust formations: >10 per user
- Collective decisions: >1 per week
- System uptime: >99.9%

## Implementation Order

### Immediate Priority (Current Sprint)
1. **UI/UX Unification** - Fix critical issues, add navigation shell
   - Phase 1: Critical fixes (chat scrolling, layout)
   - Phase 2: Navigation shell (sidebar, chat history)
   - Phase 3: Progressive enhancement (port best features)
2. **Frontend Integration** - Connect all backend features in UI
3. **Persona System** - Complete 4-mode implementation
4. **Receipts & Transparency** - Add audit trail

### Parallel Research Track
- Game mechanics integration
- ICV validation studies
- Trust protocol testing
- Resonance correlation analysis

### Conditional Development
- Only implement theoretical features after validation
- Maintain fallback strategies
- Build on proven foundations

### Decision Gates
Between phases, evaluate:
- Did research validation succeed?
- Are users finding value?
- Should we pivot or proceed?

## Critical Dependencies

The theoretical concepts have cascading dependencies:
```
Identity Compression (ICV)
    ↓ enables
Progressive Trust Exchange
    ↓ enables  
Resonance Compatibility
    ↓ enables
Agent Communication
    ↓ enables
Collective Intelligence
```

If ICV validation fails, the entire theoretical stack must be reconsidered.

## Next Actions

### Immediate (This Sprint)
1. **Fix chat UI** - Viewport-relative height, proper scrolling
2. **Create AppShell** - Unified navigation wrapper
3. **Port Sidebar** - From Chakra logic to shadcn/ui
4. **Add chat history** - Sessions in sidebar
5. **Test mobile** - Ensure responsive design

### Next Sprint
1. **Complete persona system** - 4 modes with worldview
2. **Add receipts** - Transparency for all actions
3. **Integrate context panels** - Memories while chatting
4. **Polish UI** - Animations, keyboard shortcuts

### Research Track (Parallel)
1. Begin synthetic ICV validation studies
2. Test game mechanics with real usage
3. Design trust network protocols
4. Make go/no-go decisions on theoretical features

---

*This roadmap prioritizes delivering value with proven technologies while validating ambitious theoretical concepts through rigorous research.*