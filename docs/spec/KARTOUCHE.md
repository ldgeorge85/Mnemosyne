# Kartouche Visualization Specification
## Visual Identity System for Mnemosyne Protocol

---

## Overview

The Kartouche is a visual representation system that can operate in two modes:

1. **Track 1 (Proven)**: Standard user avatars and identity visualization using established design patterns
2. **Track 2 (Experimental)**: Symbolic representation of theoretical "Deep Signals" (REQUIRES VALIDATION)

## Track 1: Standard Identity Visualization

### User Avatar System

A proven, accessible identity visualization using standard web technologies:

```html
<!-- Standard Avatar Component -->
<div class="user-avatar">
  <img src="{did_avatar_url}" alt="User Avatar" />
  <div class="trust-indicator" data-score="{trust_score}">
    <span class="ability">{ability}</span>
    <span class="benevolence">{benevolence}</span>
    <span class="integrity">{integrity}</span>
  </div>
  <div class="verification-badge" data-verified="{vc_status}">
    ✓ Verified
  </div>
</div>
```

### Trust Visualization

Based on Lee & See framework and MDS ABI model:

```python
class TrustVisualization:
    """Standard trust indicator based on proven research"""
    
    def render_trust_gauge(self, trust_score: TrustScore) -> SVG:
        # Simple, clear visualization
        return f"""
        <svg class="trust-gauge" width="200" height="100">
          <!-- Ability bar -->
          <rect x="10" y="10" width="{trust_score.ability * 180}" height="20" 
                fill="#4CAF50" />
          <text x="10" y="45">Ability: {trust_score.ability:.1%}</text>
          
          <!-- Benevolence bar -->
          <rect x="10" y="35" width="{trust_score.benevolence * 180}" height="20"
                fill="#2196F3" />
          <text x="10" y="70">Benevolence: {trust_score.benevolence:.1%}</text>
          
          <!-- Integrity bar -->
          <rect x="10" y="60" width="{trust_score.integrity * 180}" height="20"
                fill="#FF9800" />
          <text x="10" y="95">Integrity: {trust_score.integrity:.1%}</text>
        </svg>
        """
```

### Accessibility Requirements

All Track 1 visualizations must meet WCAG 2.1 AA standards:

- Minimum contrast ratio 4.5:1
- Alternative text for all visual elements
- Keyboard navigable
- Screen reader compatible
- No reliance on color alone

---

## Track 2: Experimental Symbolic Visualization

⚠️ **WARNING: EXPERIMENTAL FEATURE**  
The following symbolic system is based on unvalidated hypotheses about identity compression and behavioral patterns. It should not be used in production without proper validation.

### Hypothesis

**Claim**: Identity patterns can be represented through symbolic glyphs  
**Status**: UNVALIDATED  
**Required Validation**: Cross-cultural symbol recognition > 70%, Consistency over time ICC > 0.7

### Experimental Glyph System

```python
class ExperimentalKartouche(ExperimentalPlugin):
    """
    EXPERIMENTAL: Symbolic identity visualization
    Hypothesis: Identity can be represented through archetypal symbols
    Status: REQUIRES VALIDATION
    """
    
    hypothesis_doc = "docs/hypotheses/symbolic_representation.md"
    
    def __init__(self):
        super().__init__()
        self.require_consent("experimental.symbolic_visualization")
        self.glyphs = {
            # These mappings are THEORETICAL and UNVALIDATED
            'analytical': '∑',  # Hypothetical mapping
            'creative': '☿',    # Requires validation
            'protective': '⚔',  # No empirical basis
            'nurturing': '⚕',   # Speculative assignment
        }
    
    def render_experimental(self, compressed_identity: bytes) -> SVG:
        """
        Generate symbolic representation (EXPERIMENTAL)
        
        WARNING: This visualization is based on unproven theories
        about identity compression and should not be used for
        decision-making without validation.
        """
        if not self.has_experimental_consent():
            return self.render_standard_avatar()
        
        # Emit research metric
        self.emit_metric("kartouche.render", {
            "user_consented": True,
            "validation_status": "pending"
        })
        
        # Theoretical visualization (NO PROVEN VALIDITY)
        return self.create_symbolic_svg(compressed_identity)
```

### Experimental SVG Structure

```xml
<!-- EXPERIMENTAL VISUALIZATION - NOT VALIDATED -->
<svg class="experimental-kartouche" data-warning="EXPERIMENTAL">
  <defs>
    <pattern id="experimental-pattern">
      <!-- Unvalidated symbolic patterns -->
    </pattern>
  </defs>
  
  <g class="warning-frame">
    <rect x="0" y="0" width="300" height="300" 
          stroke="orange" stroke-width="3" stroke-dasharray="5,5"/>
    <text x="150" y="15" text-anchor="middle" fill="orange" font-size="12">
      EXPERIMENTAL - NOT VALIDATED
    </text>
  </g>
  
  <!-- Hypothetical symbolic elements -->
  <g class="experimental-symbols">
    <!-- Symbol placement based on unproven theories -->
  </g>
</svg>
```

### Research Metrics Collection

```python
class KartoucheMetrics:
    """Collect data for validation studies"""
    
    async def track_recognition(self, user_id: str, kartouche: Kartouche):
        # Measure if users recognize their own symbolic representation
        recognition_score = await self.get_user_recognition_rating()
        
        # Measure cross-cultural validity
        cultural_context = await self.get_cultural_context(user_id)
        
        # Emit for research
        await self.emit_research_event({
            "type": "kartouche.recognition",
            "score": recognition_score,
            "culture": cultural_context,
            "timestamp": datetime.utcnow()
        })
    
    async def track_consistency(self, user_id: str, kartouche_history: List):
        # Measure symbol stability over time
        icc = self.calculate_temporal_icc(kartouche_history)
        
        await self.emit_research_event({
            "type": "kartouche.stability",
            "icc": icc,
            "period_days": len(kartouche_history)
        })
```

---

## Implementation Guidelines

### For Track 1 (Production)

1. Use standard web components
2. Follow accessibility guidelines
3. Implement proven trust visualization
4. Use W3C DIDs for identity
5. Display verification status clearly

### For Track 2 (Experimental)

1. Require explicit opt-in consent
2. Display clear "EXPERIMENTAL" warnings
3. Collect metrics for validation
4. Do not use for critical decisions
5. Prepare migration path to Track 1

### Progressive Enhancement Strategy

```javascript
class KartoucheRenderer {
  render(identity) {
    // Always start with Track 1 (proven)
    let visualization = this.renderStandardAvatar(identity);
    
    // Only add experimental if conditions met
    if (this.userHasConsented() && 
        this.experimentalFeaturesEnabled() &&
        this.hasRequiredData()) {
      
      // Add experimental overlay with clear labeling
      visualization = this.addExperimentalOverlay(visualization);
      
      // Track for research
      this.emitResearchMetric('experimental_render');
    }
    
    return visualization;
  }
}
```

---

## Validation Requirements

Before any Track 2 features can move to Track 1:

1. **Recognition Study**: Users must recognize their representation > 80% of the time
2. **Cross-Cultural Validation**: Symbols must work across 3+ distinct cultures
3. **Temporal Stability**: ICC > 0.7 over 6 months
4. **Accessibility Review**: Must meet WCAG standards
5. **User Preference**: Users must prefer it over standard (p < 0.05)

---

## Current Status

- **Track 1 Components**: ✅ Ready for production use
- **Track 2 Components**: ⚠️ EXPERIMENTAL - Requires validation studies

---

*For production use, only implement Track 1 components. Track 2 is for research purposes only.*