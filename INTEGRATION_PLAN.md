# Mnemosyne Protocol - Integration Plan

## Executive Summary

This document outlines the plan to integrate existing codebases (Mnemosyne, Shadow, Dialogues, Chatter) into the unified Mnemosyne Protocol, with a focus on A2A Protocol integration and collective intelligence features.

## Current Asset Review

### 1. Mnemosyne (Memory Engine) - 70% Complete
**Ready to Use:**
- Memory model with vector embeddings (pgvector)
- User authentication system
- Task management system
- API endpoints for memories
- Frontend with React/TypeScript
- Docker deployment

**Needs Extension:**
- Add sharing contracts to memory model
- Implement selective memory export
- Add revocation mechanism
- Extend for collective instance

### 2. Shadow (Orchestration) - Ready
**Ready to Use:**
- Agent orchestration system (Engineer, Librarian, Priest)
- Collaborative executor for multi-agent tasks
- Memory integration system
- Session management
- Streaming API

**Needs Extension:**
- Add Mycelium meta-agent for coherence
- Integrate with Mnemosyne memory model
- Add collective-specific agents (Matchmaker, Gap Finder)

### 3. Dialogues (Philosophical Agents) - Ready
**Ready to Use:**
- 50+ philosophical agent definitions
- Debate orchestration system
- Memory persistence for agents
- Judge system for evaluation

**Needs Extension:**
- Port to Shadow orchestration framework
- Add to reflection pipeline
- Enable for collective synthesis

### 4. Chatter (Framework) - Template Ready
**Ready to Use:**
- LangChain-based framework
- Template system for new agents
- Docker deployment patterns

**Needs Extension:**
- Use as foundation for new collective agents
- Leverage for A2A Protocol integration

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   User Interfaces                        │
│         Mnemosyne Frontend (React) + New Collective UI   │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                  Service Layer                           │
│   Mnemosyne API | Shadow API | A2A Protocol Handler      │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                   Core Engines                           │
│  Mnemosyne Memory | Shadow Orchestra | Dialogues Agents  │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                  Data Layer                              │
│   PostgreSQL + pgvector | Redis | IPFS (optional)        │
└─────────────────────────────────────────────────────────┘
```

---

## Phase 1: Foundation Merge (Week 1-2)

### Task 1.1: Create Unified Repository ✅ COMPLETED
```bash
mnemosyne-protocol/
├── backend/           # From Mnemosyne - COPIED ✅
├── frontend/          # From Mnemosyne - COPIED ✅
├── shadow/            # From Shadow - COPIED ✅
├── dialogues/         # From Dialogues - COPIED ✅
├── collective/        # New collective layer + Chatter template - COPIED ✅
├── docker/            # Docker configuration files
├── scripts/           # Automation scripts
├── docs/              # Documentation
│   └── archive/       # Previous iterations
├── tests/             # Integration tests
├── docker-compose.yml # Unified deployment - CREATED ✅
├── .env.example       # Environment template - CREATED ✅
├── .gitignore         # Git ignore rules - CREATED ✅
└── README.md          # Main documentation
```

**Repository initialized with git and all codebases integrated!**

### Task 1.2: Extend Memory Model
```python
# Add to mnemosyne/backend/app/db/models/memory.py

class SharingContract(BaseModel):
    __tablename__ = "sharing_contracts"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    collective_id = Column(UUID(as_uuid=True), ForeignKey("collectives.id"))
    domains = Column(ARRAY(String))  # Knowledge domains
    depth = Column(String)  # summary|detailed|full
    duration = Column(DateTime, nullable=True)
    revocable = Column(Boolean, default=True)
    anonymous = Column(Boolean, default=False)
    active = Column(Boolean, default=True)

class SharedMemory(BaseModel):
    __tablename__ = "shared_memories"
    
    memory_id = Column(UUID(as_uuid=True), ForeignKey("memories.id"))
    collective_id = Column(UUID(as_uuid=True), ForeignKey("collectives.id"))
    contract_id = Column(UUID(as_uuid=True), ForeignKey("sharing_contracts.id"))
    shared_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)
```

### Task 1.3: Integrate Shadow Orchestration
```python
# shadow/orchestrator/mnemosyne_integration.py

from mnemosyne.backend.app.db.models import Memory
from shadow_system.orchestrator import ShadowAgent
from dialogues.src.agents import philosophical_agents

class MnemosyneOrchestrator(ShadowAgent):
    def __init__(self):
        super().__init__()
        # Register existing Shadow agents
        self.register_agent("engineer", EngineerAgent())
        self.register_agent("librarian", LibrarianAgent())
        self.register_agent("priest", PriestAgent())
        
        # Register Dialogues agents
        for agent_name, agent_class in philosophical_agents.items():
            self.register_agent(agent_name, agent_class())
        
        # Add Mycelium meta-agent
        self.register_agent("mycelium", MyceliumAgent())
```

---

## Phase 2: A2A Protocol Integration (Week 3-4)

### Task 2.1: Implement A2A Agent Cards
```python
# collective/a2a_integration.py

class A2AProtocolHandler:
    def generate_agent_card(self, agent):
        return {
            "name": f"mnemosyne:{agent.name}",
            "capabilities": agent.get_capabilities(),
            "modalities": ["text", "symbolic"],
            "endpoint": f"/agents/{agent.id}",
            "version": "1.0.0"
        }
    
    def handle_task(self, task_request):
        # Route A2A tasks to appropriate agents
        agent = self.orchestrator.classify(task_request)
        response = agent.process(task_request)
        return self.format_a2a_response(response)
```

### Task 2.2: Create Deep Signal Generator
```python
# collective/deep_signal.py

class DeepSignalGenerator:
    def __init__(self, memory_manager):
        self.memory = memory_manager
        
    def generate_signal(self, user_id):
        memories = self.memory.get_user_memories(user_id)
        
        return DeepSignal(
            sigil=self.generate_sigil(memories),
            domains=self.extract_domains(memories),
            glyphs=self.select_glyphs(memories),
            fracture_index=self.calculate_fracture(memories),
            visibility=self.calculate_visibility(user_id)
        )
    
    def to_kartouche(self, signal):
        # Generate SVG visual representation
        return KartoucheGenerator.generate(signal)
```

---

## Phase 3: Collective Intelligence (Week 5-6)

### Task 3.1: Fork Mnemosyne for Collective
```python
# collective/collective_codex.py

from mnemosyne.backend.app.services.memory import MemoryService

class CollectiveCodex(MemoryService):
    def __init__(self, collective_id):
        super().__init__()
        self.collective_id = collective_id
        self.collective_agents = {
            'matchmaker': MatchmakerAgent(),
            'gap_finder': GapFinderAgent(),
            'synthesizer': SynthesizerAgent()
        }
    
    def receive_share(self, user_id, memory, contract):
        if self.validate_contract(contract, memory):
            knowledge = self.extract_knowledge(memory)
            self.store_collective_knowledge(knowledge)
            if memory.revocable:
                self.store_fragment_reference(user_id, memory.id)
```

### Task 3.2: Implement Privacy Layers
```python
# collective/privacy.py

class PrivacyProtector:
    def __init__(self):
        self.k_anonymity_threshold = 3
        
    def anonymize_query(self, query):
        # Add differential privacy noise
        query = self.add_noise(query)
        
        # Check k-anonymity
        if not self.check_k_anonymity(query):
            raise PrivacyException("Insufficient anonymity")
        
        return query
    
    def protect_response(self, response):
        # Remove identifying information
        response = self.strip_identifiers(response)
        # Aggregate similar responses
        return self.aggregate_responses(response)
```

---

## Phase 4: Trust & Network (Week 7-8)

### Task 4.1: Implement Trust System
```python
# collective/trust.py

class TrustAmplifier:
    def calculate_trust(self, user_id):
        base = self.get_base_trust(user_id)
        contributions = self.get_contribution_quality(user_id)
        verification = self.get_verification_rate(user_id)
        
        score = base * contributions * verification
        
        # Anti-gaming checks
        if self.detect_gaming(user_id):
            score *= 0.1
        
        return min(score, 1.0)
```

### Task 4.2: Add Network Discovery
```python
# collective/network.py

import libp2p

class QuietNetwork:
    def __init__(self):
        self.dht = libp2p.DHT()
        
    def discover_peers(self, signal):
        # Find peers with compatible signals
        return self.dht.find_by_signal(signal)
    
    def establish_trust(self, peer_id):
        # Progressive trust building
        return self.progressive_reveal(peer_id)
```

---

## Deployment Strategy

### Docker Compose Structure
```yaml
version: '3.8'

services:
  # Individual Mnemosyne (existing)
  mnemosyne-backend:
    build: ./backend
    environment:
      - MODE=personal
    
  # Shadow Orchestration (existing)
  shadow-orchestrator:
    build: ./shadow/shadow_system
    
  # Dialogues Agents (existing)
  dialogues-agents:
    build: ./dialogues
    
  # NEW: Collective Codex
  collective-codex:
    build: ./collective
    environment:
      - MODE=collective
    
  # NEW: A2A Protocol Handler
  a2a-handler:
    build: ./collective/a2a
    ports:
      - "8003:8000"
    
  # Existing databases
  postgres:
    image: postgres:15-pgvector
    
  redis:
    image: redis:alpine
```

---

## Critical Path Dependencies

1. **Memory Model Extension** → Sharing Contracts → Collective Instance
2. **Shadow Integration** → Dialogues Port → Mycelium Agent
3. **A2A Protocol** → Agent Cards → Task Routing
4. **Privacy Layer** → K-anonymity → Differential Privacy
5. **Trust System** → Anti-gaming → Network Discovery

---

## Risk Mitigation

### Technical Risks
- **Integration Complexity**: Use adapter pattern for loose coupling
- **Performance Issues**: Implement caching and async processing
- **Privacy Breaches**: Extensive testing with attack scenarios

### Process Risks
- **Scope Creep**: Strict MVP feature set
- **Testing Gaps**: Automated test suite from day 1
- **Documentation Lag**: Update docs with each PR

---

## Success Metrics

### Week 2 Checkpoint
- [ ] Unified repository created
- [ ] Memory model extended
- [ ] Shadow integrated with Mnemosyne

### Week 4 Checkpoint  
- [ ] A2A Protocol working
- [ ] Deep Signals generating
- [ ] Basic collective sharing

### Week 6 Checkpoint
- [ ] Collective synthesis operational
- [ ] Privacy layers active
- [ ] Trust system calculating

### Week 8 Target
- [ ] Full protocol implemented
- [ ] Network discovery working
- [ ] 10+ beta testers active

---

## Next Steps

1. **Immediate**: Create unified repository structure
2. **Day 1-3**: Extend memory model with sharing contracts
3. **Day 4-7**: Integrate Shadow orchestration
4. **Week 2**: Begin A2A Protocol implementation
5. **Week 3**: Start collective layer development

---

*This integration plan leverages 70% existing code to achieve the Mnemosyne Protocol vision in 8 weeks.*