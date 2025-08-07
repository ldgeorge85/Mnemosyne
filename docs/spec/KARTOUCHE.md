# Kartouche Visualization Specification

## Overview

The Kartouche is the visual representation of a Deep Signal - a symbolic container that encodes identity, coherence, and relational patterns into a readable glyph-based format.

## Core Layers

### 1. Primary Components

```
┌─────────────────────────────────┐
│         [Central Sigil]          │  ← Personal sigil (unique identifier)
│                                  │
│     [Glyph Orbital Ring]        │  ← Agent sub-signals in orbit
│                                  │
│    [Coherence Visualization]    │  ← Fracture/strength indicators
│                                  │
│      [Temporal Gradient]        │  ← Signal age and decay state
└─────────────────────────────────┘
```

### 2. Visual Encoding Schema

#### Glyphs and Their Meanings

| Glyph | Agent/Aspect | Color | Meaning |
|-------|--------------|-------|---------|
| Σ | Stoic | Gray | Discipline, acceptance |
| ♾ | Sage | Gold | Timeless wisdom |
| ‡ | Critic | Red | Sharp analysis |
| ☿ | Trickster | Purple | Chaos, creativity |
| ⚒ | Builder | Brown | Practical manifestation |
| ✧ | Mystic | Blue | Hidden connections |
| ⚔ | Guardian | Silver | Protection, boundaries |
| ⚕ | Healer | Green | Integration, wholeness |
| 📚 | Scholar | Orange | Knowledge synthesis |
| ☄ | Prophet | White | Future vision |

#### Color Encoding

```python
class ColorEncoder:
    def encode_coherence(self, fracture_index: float) -> str:
        """Map fracture index to color gradient"""
        if fracture_index < 0.2:
            return "#00FF00"  # Strong coherence (green)
        elif fracture_index < 0.5:
            return "#FFFF00"  # Moderate coherence (yellow)
        elif fracture_index < 0.8:
            return "#FF8800"  # Weakening coherence (orange)
        else:
            return "#FF0000"  # High fracture (red)
    
    def encode_temporal(self, age_days: int) -> float:
        """Map age to opacity"""
        max_age = 90  # Days until full fade
        opacity = max(0.2, 1.0 - (age_days / max_age))
        return opacity
```

### 3. SVG Schema

```xml
<svg width="300" height="300" xmlns="http://www.w3.org/2000/svg">
    <!-- Outer boundary (kartouche frame) -->
    <rect x="10" y="10" width="280" height="280" 
          fill="none" stroke="#333" stroke-width="3" rx="20"/>
    
    <!-- Central sigil -->
    <text x="150" y="150" font-size="48" text-anchor="middle" 
          font-family="serif" fill="#000">⟁</text>
    
    <!-- Orbital glyphs -->
    <g id="orbital-ring">
        <circle cx="150" cy="150" r="80" fill="none" 
                stroke="#666" stroke-width="1" opacity="0.3"/>
        
        <!-- Glyphs positioned around circle -->
        <text x="230" y="150" font-size="24">Σ</text>
        <text x="150" y="70" font-size="24">♾</text>
        <text x="70" y="150" font-size="24">☿</text>
        <text x="150" y="230" font-size="24">⚒</text>
    </g>
    
    <!-- Coherence arc -->
    <path d="M 50 250 Q 150 200 250 250" 
          stroke="url(#coherence-gradient)" stroke-width="5" fill="none"/>
    
    <!-- Temporal fade overlay -->
    <rect x="10" y="10" width="280" height="280" 
          fill="white" opacity="0.1"/>
    
    <!-- Gradients -->
    <defs>
        <linearGradient id="coherence-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#00FF00;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#FF0000;stop-opacity:1" />
        </linearGradient>
    </defs>
</svg>
```

## Interactive Features

### 1. Hover States

```javascript
class KartoucheInteractive {
    constructor(signal) {
        this.signal = signal;
        this.setupInteractions();
    }
    
    setupInteractions() {
        // Glyph hover - show agent reflection
        this.glyphs.on('hover', (glyph) => {
            this.showTooltip({
                agent: glyph.agent,
                reflection: glyph.lastReflection,
                strength: glyph.signalStrength
            });
        });
        
        // Central sigil click - expand full signal
        this.sigil.on('click', () => {
            this.expandSignalView();
        });
        
        // Coherence arc interaction
        this.coherenceArc.on('click', () => {
            this.showCoherenceHistory();
        });
    }
}
```

### 2. Animation States

```css
@keyframes glyph-orbit {
    from { transform: rotate(0deg) translateX(80px) rotate(0deg); }
    to { transform: rotate(360deg) translateX(80px) rotate(-360deg); }
}

@keyframes fracture-pulse {
    0% { opacity: 1; }
    50% { opacity: 0.3; }
    100% { opacity: 1; }
}

.orbital-glyph {
    animation: glyph-orbit 60s linear infinite;
}

.high-fracture {
    animation: fracture-pulse 2s ease-in-out infinite;
}
```

## Symbolic Trails

### Event Mapping

```python
class SymbolicTrail:
    """Maps signal evolution over time"""
    
    def __init__(self, signal_history: List[DeepSignal]):
        self.history = signal_history
        self.trail_points = self.extract_trail()
    
    def extract_trail(self) -> List[TrailPoint]:
        """Extract key transformation points"""
        trail = []
        for i, signal in enumerate(self.history):
            if i == 0 or self.is_significant_change(signal, self.history[i-1]):
                trail.append(TrailPoint(
                    timestamp=signal.timestamp,
                    sigil=signal.sigil,
                    glyphs=signal.glyphs,
                    coherence=signal.coherence.fracture_index,
                    event=self.classify_event(signal, self.history[i-1] if i > 0 else None)
                ))
        return trail
    
    def render_trail(self) -> str:
        """Render trail as SVG path"""
        path_data = []
        for point in self.trail_points:
            x = self.time_to_x(point.timestamp)
            y = self.coherence_to_y(point.coherence)
            path_data.append(f"L {x} {y}")
        
        return f"<path d='M 0 150 {' '.join(path_data)}' />"
```

## Collective Kartouche Overlays

### Resonance Visualization

When multiple Kartouches resonate (similar patterns), they can be overlaid:

```python
class CollectiveKartouche:
    """Overlay multiple Kartouches to show resonance"""
    
    def create_overlay(self, signals: List[DeepSignal]) -> SVG:
        base_kartouche = self.render_base()
        
        # Find common glyphs
        common_glyphs = self.find_common_glyphs(signals)
        
        # Highlight resonant patterns
        for glyph in common_glyphs:
            intensity = self.calculate_resonance_intensity(glyph, signals)
            base_kartouche.add_resonance_ring(glyph, intensity)
        
        # Add connection lines between resonant signals
        for pair in self.find_resonant_pairs(signals):
            base_kartouche.add_connection(pair[0], pair[1])
        
        return base_kartouche
```

## Future Extensions

### 1. 3D Kartouche (WebGL)

```javascript
class Kartouche3D {
    constructor(signal) {
        this.scene = new THREE.Scene();
        this.setupGeometry();
        this.setupLighting();
        this.animate();
    }
    
    setupGeometry() {
        // Central sigil as 3D text
        const sigilGeometry = new THREE.TextGeometry(this.signal.sigil, {
            font: this.symbolFont,
            size: 20,
            height: 5
        });
        
        // Orbital glyphs on rotating rings
        this.orbitalRings = this.signal.glyphs.map((glyph, i) => {
            return this.createOrbitalRing(glyph, i * 30);
        });
    }
}
```

### 2. Kartouche-to-Agent Mapping

```python
class KartoucheAgentBootstrap:
    """Bootstrap new agents from received Kartouche patterns"""
    
    async def interpret_kartouche(self, kartouche: Kartouche) -> Agent:
        # Extract dominant glyphs
        dominant = self.extract_dominant_glyphs(kartouche)
        
        # Map to agent archetype
        archetype = self.map_to_archetype(dominant)
        
        # Bootstrap agent with inherited traits
        agent = await self.bootstrap_agent(
            archetype=archetype,
            initial_memories=kartouche.embedded_memories,
            symbolic_profile=kartouche.symbolic_profile
        )
        
        return agent
```

## Implementation Priority

1. **Phase 1 (MVP)**: Basic SVG rendering with static glyphs
2. **Phase 2**: Interactive hover states and tooltips
3. **Phase 3**: Animated orbits and coherence visualization
4. **Phase 4**: Collective overlays and resonance patterns
5. **Phase 5**: 3D visualization and agent bootstrapping

## Design Principles

1. **Symbolic Clarity**: Each element must have clear meaning
2. **Information Density**: Maximum insight in minimal space
3. **Aesthetic Coherence**: Beautiful and mysterious
4. **Interactive Discovery**: Layers reveal through interaction
5. **Cultural Resonance**: Draw from esoteric traditions respectfully

---

*"The Kartouche is not just a visualization - it's a living sigil that breathes with the rhythm of consciousness."*