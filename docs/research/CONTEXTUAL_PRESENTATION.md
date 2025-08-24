# Contextual Presentation & Adaptive Masking
*How systems and people present differently based on context, not just trust*

## Core Concept

Everyone adjusts their presentation based on context - this isn't deception, it's natural human behavior. Like code-switching or masking in neurodivergent communities, we all have different facets we show in different situations.

**Key Insight**: You can trust someone completely AND still choose what aspects of yourself to reveal in their context.

## Beyond Trust: The Context Matrix

### Dimensions of Context
```python
class PresentationContext:
    def __init__(self):
        self.relationship_type = None     # Professional, family, romantic, friend
        self.social_setting = None        # Work, home, public, intimate
        self.cultural_context = None      # Different norms and expectations
        self.power_dynamics = None        # Hierarchy, equality, vulnerability
        self.energy_level = None          # How much energy for full presentation
        self.safety_assessment = None     # Psychological, not just trust
```

### Natural Presentation Variations

#### Professional Context
- Competence-focused presentation
- Filtered emotional range
- Strategic vulnerability
- Achievement-oriented narratives

#### Family Context
- Historical self (they knew you before)
- Role-based presentation (child, parent, sibling)
- Involuntary vulnerability
- Pattern-locked behaviors

#### Intimate Context
- Selective deep sharing
- Chosen vulnerability
- Authentic but still contextual
- Reciprocal revelation

#### Public Context
- Protective presentation
- Curated narrative
- Energy conservation
- Strategic opacity

## Masking as Adaptive Strategy

Drawing from autistic masking research, but applicable to everyone:

### Types of Masking
```python
class AdaptiveMasking:
    def __init__(self):
        self.camouflaging = None      # Hiding traits that might be judged
        self.compensation = None      # Working harder to appear "normal"
        self.assimilation = None      # Adopting expected behaviors
        self.selective_sharing = None # Choosing what to reveal when
```

### Energy Cost Model
```python
def calculate_masking_cost(context, authentic_self):
    """Masking has energy costs - important for system design"""
    distance = measure_distance(context.expected, authentic_self)
    duration = context.interaction_length
    stakes = context.consequence_severity
    
    energy_cost = distance * duration * stakes
    return energy_cost
```

## Implementation in Mnemosyne

### Contextual ICV Presentation
```python
class ContextualICV:
    """Identity compression that respects context"""
    
    def __init__(self, full_icv):
        self.core = full_icv.stable_70_percent
        self.contexts = {}
        
    def present_in_context(self, context):
        """Different facets for different contexts"""
        if context not in self.contexts:
            self.contexts[context] = self.generate_contextual_mask(context)
        
        return self.contexts[context]
    
    def generate_contextual_mask(self, context):
        """Not hiding, just selective presentation"""
        mask = {
            'professional': self.core.competence_aspects,
            'family': self.core.historical_self,
            'intimate': self.core.chosen_vulnerable,
            'public': self.core.curated_safe,
            'exhausted': self.core.minimum_viable
        }
        return mask.get(context.type, self.core.default)
```

### Persona Adaptation by Context
```python
class ContextualPersona:
    """Persona system that understands context"""
    
    def adapt_to_context(self, base_persona, context):
        # Not less authentic, just contextually appropriate
        if context.is_professional:
            return base_persona.professional_mode()
        elif context.is_family:
            return base_persona.family_mode()
        elif context.is_low_energy:
            return base_persona.minimal_mode()
        else:
            return base_persona.chosen_mode(context)
```

## Psychological Foundations

### From Psychology Research
- **Code-switching**: Linguistic and behavioral adaptation
- **Impression management**: Goffman's presentation of self
- **Neurodivergent masking**: Autism/ADHD coping strategies
- **Cultural switching**: Bicultural identity navigation

### Healthy vs Unhealthy Masking
```python
def assess_masking_health(presentation_strategy):
    healthy_indicators = [
        'preserves_core_identity',
        'contextually_appropriate',
        'energy_sustainable',
        'maintains_boundaries',
        'allows_growth'
    ]
    
    unhealthy_indicators = [
        'erases_authentic_self',
        'unsustainable_energy_cost',
        'creates_identity_confusion',
        'prevents_genuine_connection',
        'trauma_driven'
    ]
    
    return balance_assessment(healthy_indicators, unhealthy_indicators)
```

## Context-Aware Features

### 1. Presentation Templates
Users can define different presentation modes:
- Work self
- Family self
- Dating self
- Exhausted self
- Public self
- Creative self

### 2. Automatic Context Detection
```python
def detect_context(interaction):
    indicators = {
        'language_formality': analyze_formality(interaction),
        'topic_domain': classify_topic(interaction),
        'relationship_markers': identify_relationship(interaction),
        'time_of_day': consider_energy_patterns(),
        'platform': where_is_interaction()
    }
    return synthesize_context(indicators)
```

### 3. Energy Management
```python
class MaskingEnergyManager:
    """Help users manage presentation energy"""
    
    def suggest_presentation_level(self, user_energy, context_demands):
        if user_energy < threshold and context_demands > threshold:
            return "minimum_viable_presentation"
        elif user_energy > high and context.is_safe:
            return "authentic_full_expression"
        else:
            return "adaptive_contextual_presentation"
```

## Privacy Through Context

### Not Hiding, Selecting
- Every context gets authentic but selective presentation
- No context gets everything
- User controls what each context can access
- Natural boundaries, not artificial walls

### Context-Based Permissions
```python
class ContextualPermissions:
    def get_accessible_features(self, user, context):
        base_features = self.universal_features
        
        if context.is_professional:
            return base_features + self.professional_tools
        elif context.is_creative:
            return base_features + self.creative_tools
        elif context.is_intimate:
            return base_features + self.vulnerability_tools
        else:
            return base_features
```

## Research Questions

1. How do we detect context without surveillance?
2. Can systems learn contextual preferences without profiling?
3. How do we support healthy masking without encouraging hiding?
4. What's the optimal default presentation strategy?
5. How do we handle context switches gracefully?

## Design Principles

### Support Natural Variation
- Everyone presents differently in different contexts
- This is healthy and normal
- Systems should support, not judge

### Respect Energy Limits
- Masking is exhausting
- Provide low-energy modes
- Don't demand full presentation

### Preserve Authenticity
- Different presentations are all authentic
- Not lying, just selective sharing
- Core self remains consistent

## Success Metrics

### Quantitative
- Context detection accuracy
- Energy cost reduction
- Presentation satisfaction scores
- Boundary respect rate

### Qualitative
- Users feel understood not exposed
- Natural presentation switching
- Reduced masking exhaustion
- Maintained authenticity

## Next Steps

1. Research existing masking/code-switching literature
2. Design context detection system
3. Create presentation templates
4. Build energy management tools
5. Test with neurodivergent users first (highest masking costs)

---

*"We all wear masks. The system should help us choose them wisely, not force us to remove them."*