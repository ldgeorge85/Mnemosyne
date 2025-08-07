# Memory Dynamics and Forgetting Curves Research

## Executive Summary

Memory in Mnemosyne follows biological principles discovered by Ebbinghaus and confirmed by modern neuroscience. We implement a multi-factor decay system with consolidation mechanisms inspired by REM sleep and spaced repetition research from 2024.

## The Ebbinghaus Forgetting Curve

### Original Findings (1885, Validated 2024)

Hermann Ebbinghaus discovered that memory retention follows a predictable exponential decay:

**Classic Formula**:
```
R = e^(-t/S)
```
Where:
- R = memory retention
- t = time elapsed
- S = strength of memory
- e = Euler's number

**Key Retention Points**:
- 20 minutes: 58% retained
- 1 hour: 44% retained
- 24 hours: 33% retained
- 6 days: 25% retained
- 31 days: 21% retained

### 2024 Neuroscience Updates

Recent research reveals:
- **Sleep critical**: Memory consolidation requires sleep cycles
- **Emotional weighting**: Emotionally charged memories decay 40% slower
- **Structural brain changes**: Repeated exposure creates lasting neural pathways
- **ROI proven**: 35-50% increase in training retention with spaced repetition

## Memory Consolidation Mechanisms

### Biological Model (Standard Consolidation Theory)

**Three Stages**:
1. **Encoding**: Initial formation (hippocampus)
2. **Consolidation**: Transfer to long-term (during sleep)
3. **Retrieval**: Reactivation strengthens pathways

**Mnemosyne Implementation**:
```python
class MemoryConsolidation:
    def __init__(self):
        self.stages = {
            'sensory': 0.5,    # seconds
            'short_term': 30,   # seconds
            'working': 300,     # 5 minutes
            'long_term': float('inf')
        }
    
    def consolidate(self, memory):
        # Synaptic consolidation (immediate)
        memory.strength *= 1 + memory.importance
        
        # Systems consolidation (delayed)
        if memory.age > self.stages['working']:
            memory.transfer_to_long_term()
        
        # REM-like consolidation (periodic)
        if memory.reflection_count > 3:
            memory.strength *= 1.5
```

### REM Consolidation Cycles

**Biological REM Function**:
- Processes emotional memories
- Creates novel connections
- Prunes unnecessary details
- Strengthens important patterns

**Mnemosyne REM Simulation**:
```python
async def rem_cycle(user_memories):
    # Happens during "quiet" periods
    memories = select_for_consolidation(user_memories)
    
    for memory in memories:
        # Extract patterns across memories
        patterns = find_patterns(memory, user_memories)
        
        # Create synthesis (like dreams)
        synthesis = synthesize_memories(patterns)
        
        # Update importance based on connections
        memory.importance = calculate_network_importance(memory)
        
        # Decay unimportant fragments
        if memory.importance < 0.3:
            memory.strength *= 0.7
```

## Spaced Repetition Algorithm

### Optimal Review Intervals

**Based on 2024 Medical Education Research**:
1. Initial review: Within 1 hour
2. First repetition: Within 24 hours
3. Second repetition: Within 1 week
4. Third repetition: Within 1 month
5. Fourth repetition: Within 3 months

**Mnemosyne Spacing Formula**:
```python
def calculate_next_review(memory):
    base_interval = 1  # day
    
    # Fibonacci-like progression
    intervals = [1, 1, 2, 5, 13, 34, 89]  # days
    
    # Modify based on performance
    if memory.recall_success > 0.8:
        interval = intervals[memory.review_count] * 1.3
    elif memory.recall_success < 0.5:
        interval = intervals[max(0, memory.review_count - 1)] * 0.7
    else:
        interval = intervals[memory.review_count]
    
    # Apply importance modifier
    interval *= (2 - memory.importance)  # Important = more frequent
    
    return interval
```

## Multi-Factor Decay Model

### Factors Affecting Decay

1. **Time** (Primary factor)
2. **Importance** (Subjective value)
3. **Emotional intensity** (Arousal during encoding)
4. **Interference** (Similar memories competing)
5. **Retrieval frequency** (Use strengthens)
6. **Social reinforcement** (Collective echo)

### Composite Decay Function

```python
def calculate_retention(memory, current_time):
    # Base Ebbinghaus decay
    time_factor = exp(-(current_time - memory.created) / memory.strength)
    
    # Importance modifier (0.5 to 2.0x)
    importance_factor = 0.5 + (memory.importance * 1.5)
    
    # Emotional modifier (0.8 to 1.5x)
    emotion_factor = 0.8 + (memory.emotional_intensity * 0.7)
    
    # Retrieval strength (logarithmic growth)
    retrieval_factor = 1 + log(1 + memory.access_count) * 0.1
    
    # Social reinforcement (network effect)
    social_factor = 1 + (memory.echo_count * 0.05)
    
    # Interference penalty
    interference = calculate_interference(memory)
    interference_factor = 1 / (1 + interference * 0.1)
    
    retention = (
        time_factor * 
        importance_factor * 
        emotion_factor * 
        retrieval_factor * 
        social_factor * 
        interference_factor
    )
    
    return bounded(retention, 0, 1)
```

## Memory Pinning Mechanisms

### Permanent Memory Criteria

**Never Decay** (Pin Level 3):
- Initiation memories
- Identity-core memories (trauma, breakthrough)
- Ritual completions
- Trust covenant signatures

**Slow Decay** (Pin Level 2):
- High importance (> 0.9)
- Frequent access (daily)
- Multiple agent reflections
- Collective resonance

**Protected** (Pin Level 1):
- Recent consolidation
- Active project context
- Emotional peaks

### Implementation

```python
class MemoryPinning:
    def __init__(self):
        self.pin_levels = {
            'permanent': float('inf'),  # Never decays
            'anchored': 365 * 10,        # 10 year half-life
            'protected': 365,            # 1 year half-life
            'normal': 30                 # 30 day half-life
        }
    
    def determine_pin_level(self, memory):
        # Permanent pins
        if memory.is_initiation or memory.is_covenant:
            return 'permanent'
        
        # Anchored pins
        if memory.importance > 0.9 or memory.daily_accessed:
            return 'anchored'
        
        # Protected pins
        if memory.recent_consolidation or memory.emotional_peak:
            return 'protected'
        
        return 'normal'
```

## Collective Memory Pressure

### Network Effects on Retention

**Positive Pressure** (Strengthens memory):
- Others reflect on similar memories
- Collective resonance detected
- Shared in trust ceremony
- Part of group narrative

**Negative Pressure** (Weakens memory):
- Contradicted by collective
- No resonance found
- Isolated/unique memory
- Marked as noise

### Collective Decay Modifier

```python
def apply_collective_pressure(memory, collective_context):
    # Calculate resonance with collective
    resonance = calculate_semantic_similarity(
        memory.embedding,
        collective_context.centroid
    )
    
    # High resonance strengthens
    if resonance > 0.7:
        memory.decay_rate *= 0.5  # Slower decay
    
    # Low resonance weakens
    elif resonance < 0.3:
        memory.decay_rate *= 1.5  # Faster decay
    
    # Echo count effect
    echo_modifier = 1 - (memory.echo_count * 0.02)  # Max 50% reduction
    memory.decay_rate *= max(0.5, echo_modifier)
```

## Agent Memory Interactions

### Agent-Driven Consolidation

Different agents affect memory differently:

```python
AGENT_MEMORY_EFFECTS = {
    'Magician': {'importance': 1.2, 'clarity': 1.1},      # Makes memories actionable
    'High Priestess': {'depth': 1.3, 'mystery': 1.2},    # Adds hidden layers
    'Hermit': {'consolidation': 1.5, 'isolation': 0.8},  # Deep but isolated
    'Death': {'transformation': 2.0, 'decay': 1.5},      # Transform or destroy
    'Star': {'hope': 1.3, 'inspiration': 1.2},           # Brightens memories
    'Moon': {'illusion': 0.7, 'dream': 1.4},            # Questions or deepens
}
```

### Reflection Impact on Decay

```python
def apply_agent_reflection(memory, agent_type, reflection):
    effects = AGENT_MEMORY_EFFECTS[agent_type]
    
    for attribute, modifier in effects.items():
        if hasattr(memory, attribute):
            setattr(memory, attribute, 
                   getattr(memory, attribute) * modifier)
    
    # Reflection always reduces decay somewhat
    memory.decay_rate *= 0.9
    
    # But may fragment if conflicting
    if reflection.conflicts_with_memory:
        memory.fracture_index += 0.1
```

## Implementation Timeline

### Phase 1 (MVP)
- Basic Ebbinghaus curve
- Simple importance weighting
- Manual pinning

### Phase 2 (Enhanced)
- Multi-factor decay
- REM consolidation cycles
- Collective pressure

### Phase 3 (Advanced)
- Predictive decay modeling
- Interference calculation
- Agent-specific effects

## Key Insights from Research

1. **Sleep is critical**: Schedule consolidation during low-activity periods
2. **Emotion matters**: 40% slower decay for emotional memories
3. **Spacing beats massing**: Distributed practice 2x more effective
4. **Social reinforcement works**: Collective echo extends retention 50%
5. **Interference is real**: Similar memories compete and accelerate decay

## References

- Ebbinghaus, H. (1885). "Memory: A Contribution to Experimental Psychology"
- Murre, J. M., & Dros, J. (2015). "Replication and Analysis of Ebbinghaus' Forgetting Curve"
- 2024 Nature Neuroscience: "Sleep-dependent memory consolidation mechanisms"
- 2024 Deloitte Report: "35-50% ROI increase with spaced repetition training"
- Wozniak, P. A. (1990). "Optimization of learning" (SuperMemo algorithm)
- Medical Education 2024: "Spaced repetition in residency training programs"

---

*"Memory is not about perfect recall, but about meaningful consolidation and timely forgetting."*