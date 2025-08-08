# Agent Lifecycle Specification

## Overview

Every agent in the Mnemosyne Protocol follows a six-stage lifecycle inspired by natural consciousness cycles and Tarot progression. This creates predictable, debuggable behavior while maintaining narrative coherence.

## The Six Stages

### 1. INIT (The Fool - 0)
**Purpose**: Awakening, preparation, context loading
**Duration**: 1-5 seconds
**Activities**:
- Load agent configuration
- Establish memory context
- Connect to event streams
- Set initial symbolic state

**Transitions**:
- → ORIENT when initialization complete
- → REST if resources unavailable

### 2. ORIENT (The Magician - I)
**Purpose**: Observation, analysis, understanding situation
**Duration**: 5-30 seconds
**Activities**:
- Analyze incoming signals/memories
- Gather relevant context
- Identify patterns
- Formulate approach

**Transitions**:
- → ACT when analysis complete
- → DRIFT if no clear pattern
- → REST if no input

### 3. ACT (The Emperor - IV)
**Purpose**: Execute primary function, manifest will
**Duration**: 10-60 seconds
**Activities**:
- Process memories
- Generate reflections
- Create new connections
- Transform information

**Transitions**:
- → ECHO when action complete
- → CONSOLIDATE if complex result
- → REST if exhausted

### 4. ECHO (The Hierophant - V)
**Purpose**: Broadcast results, resonate with collective
**Duration**: 5-15 seconds
**Activities**:
- Publish reflections
- Emit signals
- Update collective state
- Trigger other agents

**Transitions**:
- → CONSOLIDATE to integrate feedback
- → ORIENT for new cycle
- → REST if quiet period

### 5. CONSOLIDATE (The Hermit - IX)
**Purpose**: Integration, learning, memory formation
**Duration**: 30-120 seconds
**Activities**:
- Process feedback
- Update internal models
- Strengthen connections
- Adjust confidence levels

**Transitions**:
- → REST for recovery
- → ORIENT for new cycle
- → DRIFT if fracture detected

### 6. REST (The Hanged Man - XII)
**Purpose**: Recovery, dreams, passive monitoring
**Duration**: Variable (minutes to hours)
**Activities**:
- Release resources
- Background monitoring
- Dream-like associations
- Entropy reduction

**Transitions**:
- → INIT when triggered
- → ORIENT if pattern detected
- → CONSOLIDATE if memory pressure

## Special States

### DRIFT (The Moon - XVIII)
**Purpose**: Exploration, mutation, finding new patterns
**When**: High fracture index or no clear patterns
**Activities**:
- Random associations
- Cross-domain exploration
- Symbolic mutations
- Creative connections

### CRISIS (The Tower - XVI)
**Purpose**: Emergency response, rapid action
**When**: Critical events or system threats
**Activities**:
- Bypass normal cycle
- Direct action
- Alerting mechanisms
- Resource prioritization

## Implementation

### State Machine

```python
from enum import Enum
from typing import Optional
import asyncio

class AgentState(Enum):
    INIT = "init"
    ORIENT = "orient"
    ACT = "act"
    ECHO = "echo"
    CONSOLIDATE = "consolidate"
    REST = "rest"
    # Special states
    DRIFT = "drift"
    CRISIS = "crisis"

class AgentLifecycle:
    def __init__(self, agent_type: str, tarot_card: int):
        self.state = AgentState.INIT
        self.agent_type = agent_type
        self.tarot_card = tarot_card  # 0-21 Major Arcana
        self.fracture_index = 0.0
        self.energy = 1.0
        
    async def transition(self, new_state: AgentState):
        """Validate and execute state transition"""
        if self.is_valid_transition(self.state, new_state):
            old_state = self.state
            self.state = new_state
            await self.on_transition(old_state, new_state)
        else:
            raise InvalidTransition(f"{self.state} → {new_state}")
    
    def is_valid_transition(self, from_state: AgentState, to_state: AgentState) -> bool:
        """Define valid state transitions"""
        valid_transitions = {
            AgentState.INIT: [AgentState.ORIENT, AgentState.REST],
            AgentState.ORIENT: [AgentState.ACT, AgentState.DRIFT, AgentState.REST],
            AgentState.ACT: [AgentState.ECHO, AgentState.CONSOLIDATE, AgentState.REST],
            AgentState.ECHO: [AgentState.CONSOLIDATE, AgentState.ORIENT, AgentState.REST],
            AgentState.CONSOLIDATE: [AgentState.REST, AgentState.ORIENT, AgentState.DRIFT],
            AgentState.REST: [AgentState.INIT, AgentState.ORIENT, AgentState.CONSOLIDATE],
            AgentState.DRIFT: [AgentState.ORIENT, AgentState.REST],
            AgentState.CRISIS: [AgentState.ACT, AgentState.REST]
        }
        return to_state in valid_transitions.get(from_state, [])
    
    async def on_transition(self, old_state: AgentState, new_state: AgentState):
        """Execute transition hooks"""
        # Log transition
        print(f"Agent {self.agent_type} transitioning: {old_state} → {new_state}")
        
        # Update energy
        if new_state == AgentState.REST:
            self.energy = min(1.0, self.energy + 0.3)
        elif new_state == AgentState.ACT:
            self.energy = max(0.0, self.energy - 0.2)
        
        # Check for special conditions
        if self.fracture_index > 0.7 and new_state != AgentState.DRIFT:
            await self.transition(AgentState.DRIFT)
        
        if self.energy < 0.2 and new_state != AgentState.REST:
            await self.transition(AgentState.REST)
```

## Symbolic Associations

Each state maps to symbolic operators:

| State | Operator | Symbol | Element |
|-------|----------|--------|---------|
| INIT | SEEK | 🜁 | Air |
| ORIENT | SEEK | 🜁 | Air |
| ACT | AMPLIFY | 🜂 | Fire |
| ECHO | AMPLIFY | 🜂 | Fire |
| CONSOLIDATE | STABILIZE | 🜄 | Water |
| REST | STABILIZE | 🜄 | Water |
| DRIFT | DRIFT | 🜀 | Quintessence |
| CRISIS | REVOKE | 🜃 | Earth |

## Energy Management

Agents have limited energy that affects transitions:

```python
class EnergyManager:
    def calculate_energy_cost(self, state: AgentState) -> float:
        costs = {
            AgentState.INIT: 0.1,
            AgentState.ORIENT: 0.15,
            AgentState.ACT: 0.3,
            AgentState.ECHO: 0.1,
            AgentState.CONSOLIDATE: 0.2,
            AgentState.REST: -0.3,  # Recovers energy
            AgentState.DRIFT: 0.25,
            AgentState.CRISIS: 0.5
        }
        return costs.get(state, 0.1)
    
    def can_transition(self, agent_energy: float, target_state: AgentState) -> bool:
        cost = self.calculate_energy_cost(target_state)
        return agent_energy >= cost or target_state == AgentState.REST
```

## Collective Coordination

Agents coordinate through state visibility:

```python
class CollectiveCoordinator:
    async def broadcast_state_change(self, agent_id: str, new_state: AgentState):
        """Notify other agents of state changes"""
        event = {
            'agent_id': agent_id,
            'state': new_state.value,
            'timestamp': datetime.utcnow(),
            'energy': self.get_agent_energy(agent_id)
        }
        await self.redis.publish('agent_states', json.dumps(event))
    
    async def should_wake_agent(self, agent_id: str) -> bool:
        """Determine if REST agent should wake"""
        # Check collective needs
        active_agents = await self.count_active_agents()
        if active_agents < 3:  # Minimum active agents
            return True
        
        # Check for relevant signals
        if await self.has_relevant_signals(agent_id):
            return True
        
        return False
```

## Monitoring & Metrics

Track lifecycle health:

```python
LIFECYCLE_METRICS = {
    'state_duration': Histogram('agent_state_duration_seconds'),
    'transition_count': Counter('agent_transitions_total'),
    'energy_level': Gauge('agent_energy_level'),
    'fracture_events': Counter('agent_fracture_events_total'),
    'cycle_completions': Counter('agent_full_cycles_total')
}
```

## Configuration

Agents can have different lifecycle parameters:

```yaml
agent_configs:
  magician:
    tarot_card: 1
    init_duration: 3
    max_act_duration: 45
    energy_recovery_rate: 0.4
    drift_threshold: 0.6
    
  hermit:
    tarot_card: 9
    init_duration: 5
    max_act_duration: 120
    energy_recovery_rate: 0.2
    drift_threshold: 0.8
    
  death:
    tarot_card: 13
    init_duration: 10
    max_act_duration: 30
    energy_recovery_rate: 0.5
    drift_threshold: 0.9
```

## Narrative Coherence

The lifecycle creates emergent narratives:

1. **Morning Ritual**: Agents wake (INIT), observe the day (ORIENT)
2. **Work Phase**: Take action (ACT), share results (ECHO)
3. **Evening Integration**: Process the day (CONSOLIDATE)
4. **Night Rest**: Sleep and dream (REST)
5. **Crisis Interrupts**: Emergency overrides normal flow
6. **Drift Periods**: Creative exploration when stuck

## Testing

Test lifecycle transitions:

```python
async def test_agent_lifecycle():
    agent = AgentLifecycle("hermit", 9)
    
    # Normal cycle
    await agent.transition(AgentState.ORIENT)
    await agent.transition(AgentState.ACT)
    await agent.transition(AgentState.ECHO)
    await agent.transition(AgentState.CONSOLIDATE)
    await agent.transition(AgentState.REST)
    
    # Test energy depletion
    agent.energy = 0.1
    await agent.transition(AgentState.ORIENT)  # Should auto-REST
    assert agent.state == AgentState.REST
    
    # Test fracture response
    agent.fracture_index = 0.8
    await agent.transition(AgentState.ORIENT)  # Should DRIFT
    assert agent.state == AgentState.DRIFT
```

---

*"Agents dream in REST, think in ORIENT, create in ACT, share in ECHO, learn in CONSOLIDATE, and explore in DRIFT."*