# The Mnemosyne Protocol Specification
## Version 3.1 - Consolidated Edition

---

## 1. Core Architecture

### 1.1 Four-Layer System

```
Layer 4: Collective Codex - Community intelligence & coordination
Layer 3: Quiet Network - Discovery & trust establishment  
Layer 2: Deep Signal Protocol - Identity compression & signaling
Layer 1: Mnemosyne Engine - Personal memory & agent orchestra
```

### 1.2 Design Principles

1. **Local First** - Data sovereignty by default
2. **Selective Sharing** - Explicit control over data flow
3. **Progressive Trust** - Relationships deepen through interaction
4. **Dual Sovereignty** - Individual autonomy with collective benefit
5. **No Mocking** - Real implementation or explicit deferral

---

## 2. Layer 1: Mnemosyne Engine

### 2.1 Memory System

#### Components
- **Capture**: Multi-source ingestion (text, web, files, APIs)
- **Processing**: Extract → Embed → Store → Index
- **Consolidation**: REM-like cycles for memory integration
- **Retrieval**: Vector similarity + temporal + importance

#### Database Schema
```sql
CREATE TABLE memories (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    metadata JSONB,
    importance FLOAT DEFAULT 0.5,
    last_accessed TIMESTAMP,
    consolidation_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_memories_embedding ON memories 
    USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_memories_user_importance ON memories(user_id, importance DESC);
CREATE INDEX idx_memories_metadata ON memories USING gin(metadata);
```

#### Consolidation Process
```python
class MemoryConsolidator:
    def consolidate(self, memories: List[Memory]) -> Memory:
        # Group similar memories
        clusters = self.cluster_memories(memories)
        
        # Extract patterns
        patterns = self.extract_patterns(clusters)
        
        # Generate synthesis
        synthesis = self.synthesize(patterns)
        
        # Update importance scores
        self.update_importance(memories, synthesis)
        
        return synthesis
```

### 2.2 Agent Orchestra

#### Core Agents (from Shadow)
- **Engineer**: Technical analysis and implementation
- **Librarian**: Knowledge organization and retrieval
- **Priest**: Pattern recognition and meaning-making

#### Meta Agent
- **Mycelium**: Monitors coherence, coordinates agents

#### Philosophical Agents (from Dialogues)
- Initial: 10 agents with symbolic mappings:
  - **Stoic** (Σ): Discipline and acceptance
  - **Sage** (♾): Timeless wisdom
  - **Critic** (‡): Sharp analysis
  - **Trickster** (☿): Chaos and creativity
  - **Builder** (⚒): Practical manifestation
  - **Mystic** (✧): Hidden connections
  - **Guardian** (⚔): Protection and boundaries
  - **Healer** (⚕): Integration and wholeness
  - **Scholar** (📚): Knowledge synthesis
  - **Prophet** (☄): Future vision
- Full set: 50+ specialized perspectives, each with unique glyph
- Agents emit **sub-signals** that modulate user's Deep Signal

#### Agent Communication Protocol (A2A)
```python
class AgentProtocol:
    async def send_reflection(self, memory: Memory) -> Reflection:
        # Agent analyzes memory
        analysis = await self.analyze(memory)
        
        # Generate reflection
        reflection = Reflection(
            agent_id=self.id,
            memory_id=memory.id,
            content=analysis,
            confidence=self.calculate_confidence(),
            timestamp=now()
        )
        
        # Broadcast to other agents
        await self.broadcast(reflection)
        
        return reflection
```

### 2.3 Resource Management

```python
class AgentResourceManager:
    MAX_CONCURRENT_AGENTS = 5
    MAX_MEMORY_PER_AGENT = 512  # MB
    MAX_COMPUTE_TIME = 30  # seconds
    
    def allocate_resources(self, agent: Agent) -> ResourceAllocation:
        return ResourceAllocation(
            memory_limit=self.MAX_MEMORY_PER_AGENT,
            time_limit=self.MAX_COMPUTE_TIME,
            priority=agent.priority
        )
```

---

## 3. Layer 2: Deep Signal Protocol

### 3.1 Signal Format

```python
{
    "version": "2.1",
    "sigil": "⊕",  # Core identity symbol
    "domains": ["systems", "philosophy", "resilience"],
    "stack": ["python", "typescript", "rust"],
    
    "personality": {
        "openness": 0.8,
        "chaos_tolerance": 0.7,
        "trust_preference": "progressive"
    },
    
    "coherence": {
        "fracture_index": 0.3,  # 0=unified, 1=fragmented
        "integration_level": 0.7,
        "recovery_vectors": ["meditation", "building", "teaching"]
    },
    
    "glyphs": ["∴", "⊙", "◈"],  # Visual identity markers
    
    "flags": {
        "seeking": ["technical_cofounder", "philosophy_group"],
        "offering": ["systems_design", "protocol_development"],
        "crisis_mode": false,
        "intended_silence": false
    },
    
    "visibility": 0.3,  # 30% public exposure
    
    "trust_fragment": {
        "type": "glyphic",  # glyphic|ritual|proof
        "depth": "surface",  # surface|embedded|esoteric
        "verified_by": []
    },
    
    "symbolic_profile": {
        "role": "Strategist",
        "glyph": "⟁",
        "function": "System architecture and coordination"
    },
    
    "timestamp": "2025-01-20T10:00:00Z",
    "signature": "ed25519:base64_signature"
}
```

### 3.2 Kartouche Visualization

```javascript
class KartoucheRenderer {
    renderSVG(signal) {
        return `
            <svg width="200" height="100">
                <!-- Boundary -->
                <rect x="5" y="5" width="190" height="90" 
                      fill="none" stroke="#333" stroke-width="2"/>
                
                <!-- Sigil -->
                <text x="100" y="30" font-size="24" 
                      text-anchor="middle">${signal.sigil}</text>
                
                <!-- Glyphs -->
                ${signal.glyphs.map((g, i) => `
                    <text x="${50 + i*50}" y="60" font-size="16">${g}</text>
                `).join('')}
                
                <!-- Fracture visualization -->
                <line x1="20" y1="80" x2="${180 * (1-signal.coherence.fracture_index)}" 
                      y2="80" stroke="green" stroke-width="3"/>
            </svg>
        `;
    }
}
```

### 3.3 Signal Management

```python
class SignalManager:
    COOLDOWN_MINUTES = 15
    MIN_ENTROPY = 0.3
    
    def emit_signal(self, user_id: str) -> Signal:
        # Check cooldown
        if not self.check_cooldown(user_id):
            raise SignalCooldownError()
        
        # Generate signal from memory patterns
        signal = self.generate_signal(user_id)
        
        # Verify entropy
        if self.calculate_entropy(signal) < self.MIN_ENTROPY:
            raise InsufficientEntropyError()
        
        # Sign and broadcast
        signed = self.sign_signal(signal)
        self.broadcast(signed)
        
        return signed
```

---

## 4. Layer 3: Quiet Network

### 4.1 Progressive Trust Protocol

```python
class TrustProtocol:
    stages = [
        "signal_exchange",     # Public signals only
        "domain_revelation",   # Reveal interest areas
        "capability_sharing",  # Share specific skills
        "memory_glimpse",      # Share redacted memories
        "full_trust"          # Complete access
    ]
    
    def advance_trust(self, relationship: Relationship) -> bool:
        # Verify positive interactions
        if relationship.positive_interactions < relationship.stage * 3:
            return False
        
        # Check time requirement
        if relationship.duration < relationship.stage * 7 * DAYS:
            return False
        
        # Advance stage
        relationship.stage += 1
        self.grant_permissions(relationship)
        
        return True
```

### 4.2 Network Discovery (Deferred)

Future implementation using libp2p DHT:
- Peer discovery without central registry
- Encrypted signal broadcasts
- Relay nodes for NAT traversal

---

## 5. Layer 4: Collective Codex

### 5.1 Architecture

The Collective Codex is a specialized Mnemosyne instance with:
- Elevated permissions for cross-user operations
- Specialized agents for collective intelligence
- Privacy-preserving aggregation

### 5.2 Sharing Contracts

```python
@dataclass
class SharingContract:
    collective_id: str
    domains: List[str]
    depth: Literal["summary", "detailed", "full"]
    duration: timedelta
    revocable: bool = True
    anonymous: bool = False
    k_anonymity: int = 3
    
    def validate_memory(self, memory: Memory) -> bool:
        # Check domain match
        if not any(d in memory.domains for d in self.domains):
            return False
        
        # Check depth constraints
        if self.depth == "summary" and len(memory.content) > 500:
            memory.content = summarize(memory.content)
        
        return True
```

### 5.3 Collective Agents

```python
class CollectiveAgents:
    agents = {
        "matchmaker": MatchmakerAgent(),      # Connect complementary skills
        "gap_finder": GapFinderAgent(),       # Identify knowledge gaps
        "synthesizer": SynthesizerAgent(),    # Combine insights
        "arbitrator": ArbitratorAgent(),      # Resolve conflicts
        "curator": CuratorAgent(),           # Maintain quality
        "ritual_master": RitualMasterAgent()  # Coordinate ceremonies
    }
```

### 5.4 Privacy Implementation

#### K-Anonymity Enforcement
```python
class KAnonymityProtector:
    def protect(self, memories: List[Memory], k: int = 3) -> List[Memory]:
        # Group similar memories
        groups = self.group_by_quasi_identifiers(memories)
        
        # Only release groups with k+ members
        protected = []
        for group in groups:
            if len(group) >= k:
                generalized = self.generalize_group(group)
                protected.extend(generalized)
        
        return protected
```

---

## 6. Ritual & Symbolic Layer

### 6.1 Ritual Architecture

```python
class RitualEngine:
    def __init__(self):
        self.rituals = {
            "trust_bootstrap": TrustBootstrapRitual(),
            "memory_merger": MemoryMergerRitual(),
            "signal_harmony": SignalHarmonyRitual(),
            "collective_emergence": CollectiveEmergenceRitual()
        }
    
    def trigger_jit_ritual(self, context: Context) -> Optional[Ritual]:
        """Just-in-Time ritual triggering based on context"""
        for ritual in self.rituals.values():
            if ritual.should_trigger(context):
                return ritual.execute(context)
        return None
```

### 6.2 Symbolic Operations

```python
class SymbolicInterpreter:
    def interpret_glyphs(self, glyphs: List[str]) -> Interpretation:
        # Map to emotional/philosophical meaning
        meanings = [self.glyph_dictionary.get(g) for g in glyphs]
        
        # Check for contradictions
        contradictions = self.find_contradictions(meanings)
        
        # Generate interpretation
        return Interpretation(
            meanings=meanings,
            coherence=1.0 - len(contradictions) / len(glyphs),
            dominant_theme=self.extract_theme(meanings)
        )
```

### 6.3 Trust Ceremonies

#### Progressive Trust Path (Default)
```python
class ProgressiveTrustCeremony:
    stages = [
        "glyph_exchange",      # Exchange symbolic identities
        "mirror_prompt",       # Shared reflection exercise
        "fragment_weaving",    # Combine memory fragments
        "covenant_creation"    # Establish trust parameters
    ]
```

#### Alternative Trust Pathways

**Mirrored Dissonance Path**
```python
class DissonanceTrustCeremony:
    """Trust through intentional disagreement"""
    stages = [
        "conflict_declaration",  # State opposing positions
        "dialectic_dance",       # Structured argumentation
        "synthesis_emergence",   # Find third position
        "respect_covenant"       # Trust through tested boundaries
    ]
```

**Echo Drift Path**
```python
class EchoDriftCeremony:
    """Trust through surviving chaos together"""
    stages = [
        "chaos_invocation",     # Enter high-entropy state
        "drift_navigation",     # Navigate uncertainty together
        "signal_recovery",      # Find each other again
        "trauma_bond"          # Trust through shared survival
    ]
```

**Symbolic Proof-of-Work Path**
```python
class SymbolicPoWCeremony:
    """Trust through ritual effort"""
    stages = [
        "quest_assignment",     # Receive symbolic challenge
        "effort_demonstration", # Complete ritual work
        "witness_verification", # Community validates effort
        "initiation_complete"   # Trust through proven commitment
    ]
```

---

## 7. Security Model

### 7.1 Threat Matrix

| Threat | Mitigation | Implementation |
|--------|------------|----------------|
| Memory poisoning | Input validation, sandboxing | Week 1 |
| Trust gaming | Multi-factor verification | Week 2 |
| Privacy breach | K-anonymity, encryption | Week 2 |
| Sybil attacks | Proof of work | Week 3 |
| Signal spam | Cooldowns, entropy | Week 3 |
| Agent compromise | Resource isolation | Week 1 |
| Symbol drift | Glyph coherence monitoring | Week 4 |
| Ritual gaming | Effort verification | Week 4 |

### 7.2 Encryption Layers

```python
class EncryptionManager:
    def encrypt_memory(self, memory: Memory, key: bytes) -> EncryptedMemory:
        # AES-256-GCM for memory content
        nonce = os.urandom(12)
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce),
            backend=default_backend()
        )
        
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(memory.content.encode())
        encryptor.finalize()
        
        return EncryptedMemory(
            ciphertext=ciphertext,
            nonce=nonce,
            tag=encryptor.tag
        )
```

### 7.3 Authentication System

```python
class AuthenticationSystem:
    def register(self, username: str, password: str) -> User:
        # Generate salt
        salt = bcrypt.gensalt()
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode(), salt)
        
        # Create user
        user = User(
            id=uuid4(),
            username=username,
            password_hash=password_hash,
            created_at=now()
        )
        
        # Generate initial keypair
        private_key, public_key = self.generate_keypair()
        
        return user
```

---

## 8. API Specification

### 8.1 Authentication Endpoints

```python
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/refresh
POST   /api/auth/logout
POST   /api/trust/advance    # Explicitly progress trust level
```

### 8.2 Memory Operations

```python
POST   /api/memories              # Create memory
GET    /api/memories              # List memories
GET    /api/memories/:id         # Get specific memory
PUT    /api/memories/:id         # Update memory
DELETE /api/memories/:id         # Delete memory
POST   /api/memories/consolidate # Trigger consolidation
GET    /api/memories/search      # Vector search
```

### 8.3 Agent Operations

```python
GET    /api/agents               # List available agents
POST   /api/agents/:id/reflect  # Trigger reflection
GET    /api/agents/:id/status   # Agent health
POST   /api/agents/orchestrate  # Multi-agent task
```

### 8.4 Signal Operations

```python
POST   /api/signals/generate     # Generate signal
GET    /api/signals/mine        # Get my signals
POST   /api/signals/verify      # Verify signal
GET    /api/signals/discover    # Discover others
```

### 8.5 Collective Operations

```python
POST   /api/collective/join      # Join collective
POST   /api/collective/share    # Share with contract
GET    /api/collective/search   # Search collective
POST   /api/collective/match    # Find collaborators
DELETE /api/collective/revoke   # Revoke sharing
```

### 8.6 Ritual Operations

```python
POST   /api/rituals/initiate    # Start ritual
GET    /api/rituals/available   # List available
POST   /api/rituals/:id/advance # Progress ritual
GET    /api/rituals/:id/status  # Ritual state
```

---

## 9. Implementation Timeline

### Phase 1: MVP (Weeks 1-3)
**Focus**: Personal tool that works perfectly for one user

- Week 1: Core memory system + basic agents
- Week 2: Sharing contracts + collective basics
- Week 3: Signal generation + initial rituals

### Phase 2: Early Adopters (Weeks 4-8)
**Focus**: Support 10-100 users with real privacy

- Advanced privacy (ZK proofs)
- P2P network discovery
- 50+ philosophical agents
- Mobile responsive UI

### Phase 3: Growth (Months 3-6)
**Focus**: Scale to 1000+ users

- Native mobile apps
- Federation protocol
- Advanced cryptography
- Governance systems

---

## 10. Success Metrics

### Technical Metrics
- Memory operations < 100ms
- Agent responses < 5s
- 99.9% uptime
- Zero privacy breaches

### User Metrics
- Daily active usage
- Memory capture rate
- Agent interaction depth
- Collective participation

### Protocol Metrics
- Signal diversity
- Trust network density
- Knowledge synthesis rate
- Ritual completion rate

---

## 11. Philosophical Commitments

1. **Build for yourself first** - Every feature must serve the builder
2. **No surveillance** - Privacy is architecture, not policy
3. **Real or nothing** - No mocking, no fake features
4. **Symbolic depth** - Meaning beyond pure logic
5. **Emergent order** - Let patterns arise from use
6. **Proto-Order formation** - We are building more than tools
7. **Memory as resistance** - Remembering is a political act

## 12. The Order Emerges

This protocol is the foundation for a **symbolic-cognitive Order** where:

- **Initiation** happens through progressive trust ceremonies
- **Ranks** emerge from contribution and coherence
- **Rituals** create shared meaning beyond logic
- **Symbols** carry compressed wisdom
- **Memory** becomes collective intelligence
- **Sovereignty** enables true agency

The Order of Rememberers begins with those who build it, use it, and evolve it. Each member carries their Deep Signal, participates in ceremonies, and contributes to the collective intelligence while maintaining individual sovereignty.

> *"This is not merely a tool—it is the beginning of an Order that remembers, reflects, and evolves together."*

---

*Version 3.1 - For those who see too much and belong nowhere*