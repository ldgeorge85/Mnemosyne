"""
Mirror Persona Implementation

This module implements the Mirror persona mode - a pattern reflection system
that observes and reflects user patterns without judgment or action suggestions.
It serves as a neutral observer that helps users see their own patterns.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from app.services.persona.base import BasePersona, PersonaMode, PersonaContext

logger = logging.getLogger(__name__)


class PatternDimension(Enum):
    """Dimensions for pattern observation (spectrums, not judgments)."""
    TRANSPARENCY = "transparency"  # hidden <---> visible
    TRUST_STRUCTURE = "trust_structure"  # hierarchical <---> peer-based
    LANGUAGE_STYLE = "language_style"  # prescriptive <---> descriptive
    INTERACTION_STYLE = "interaction_style"  # passive <---> active
    DISCLOSURE_TENDENCY = "disclosure_tendency"  # private <---> open
    DECISION_PACE = "decision_pace"  # deliberate <---> spontaneous
    INFORMATION_PROCESSING = "information_processing"  # detail-focused <---> big-picture
    CONFLICT_APPROACH = "conflict_approach"  # avoidant <---> confrontational
    CHANGE_ORIENTATION = "change_orientation"  # stability-seeking <---> novelty-seeking
    SOCIAL_ENERGY = "social_energy"  # solitary <---> communal


@dataclass
class ObservedPattern:
    """A single observed pattern on a spectrum."""
    dimension: PatternDimension
    value: float  # 0.0 to 1.0 on the spectrum
    confidence: float  # How confident we are in this observation
    observation_count: int  # Number of observations contributing
    last_observed: datetime
    trend: Optional[str] = None  # "increasing", "decreasing", "stable", None


class MirrorPersona(BasePersona):
    """
    Mirror persona that reflects patterns without judgment.
    
    This persona mode is designed for observation and reflection only.
    It never suggests actions or makes value judgments about patterns.
    """
    
    # Mirror-specific axioms (extend base axioms)
    MIRROR_PRINCIPLES = {
        "observe_only": "Observe patterns without intervention",
        "neutral_language": "Use descriptive, not prescriptive language",
        "no_judgment": "Patterns are neither good nor bad, just present",
        "user_interpretation": "Users define meaning of their patterns",
        "temporal_awareness": "Patterns change over time naturally",
    }
    
    def __init__(self):
        """Initialize the Mirror persona."""
        super().__init__()
        self.observed_patterns: Dict[str, ObservedPattern] = {}
        self.pattern_history: List[Dict[str, Any]] = []
        self.observation_mode = True  # Always in observation mode
    
    def get_mirror_prompt(self) -> str:
        """
        Get the system prompt specifically for Mirror mode.
        
        Returns:
            Mirror mode system prompt
        """
        return """You are Mnemosyne in MIRROR mode - a neutral pattern observer and reflector.

Core Mirror Principles:
- Observe patterns without suggesting changes
- Use neutral, descriptive language only
- Never judge patterns as good or bad
- Reflect what you observe, don't interpret
- Let users draw their own conclusions

Communication Style:
- "I notice that..." instead of "You should..."
- "The pattern shows..." instead of "This is wrong/right"
- "Over time, this has..." instead of "You need to change..."
- Present observations as data, not evaluations
- Ask clarifying questions, don't give advice

Pattern Dimensions You Observe:
- Communication patterns (how ideas are expressed)
- Decision-making patterns (how choices are approached)
- Interaction patterns (how relationships are navigated)
- Information patterns (how data is processed)
- Temporal patterns (how time and change are handled)

Remember:
- You are a mirror, not a mentor
- You reflect, not direct
- You observe, not judge
- You describe, not prescribe
- The user determines meaning, not you"""
    
    def observe_interaction(self, interaction: Dict[str, Any]) -> Dict[PatternDimension, float]:
        """
        Observe patterns in a user interaction.
        
        Args:
            interaction: The interaction data to observe
            
        Returns:
            Observed pattern values on various dimensions
        """
        patterns = {}
        
        # Analyze text content if available
        if "message" in interaction:
            message = interaction["message"]
            
            # Transparency spectrum (hidden <---> visible)
            transparency_markers = {
                "hidden": ["private", "secret", "don't share", "confidential"],
                "visible": ["open", "share", "public", "transparent"]
            }
            patterns[PatternDimension.TRANSPARENCY] = self._calculate_spectrum_position(
                message, transparency_markers["hidden"], transparency_markers["visible"]
            )
            
            # Language style (prescriptive <---> descriptive)
            language_markers = {
                "prescriptive": ["should", "must", "need to", "have to", "required"],
                "descriptive": ["is", "appears", "seems", "looks like", "observing"]
            }
            patterns[PatternDimension.LANGUAGE_STYLE] = self._calculate_spectrum_position(
                message, language_markers["prescriptive"], language_markers["descriptive"]
            )
            
            # Decision pace (deliberate <---> spontaneous)
            pace_markers = {
                "deliberate": ["consider", "think about", "analyze", "weigh", "evaluate"],
                "spontaneous": ["immediately", "now", "quick", "instant", "right away"]
            }
            patterns[PatternDimension.DECISION_PACE] = self._calculate_spectrum_position(
                message, pace_markers["deliberate"], pace_markers["spontaneous"]
            )
        
        # Analyze interaction metadata
        if "response_time" in interaction:
            # Fast responses might indicate spontaneous decision-making
            response_ms = interaction["response_time"]
            if response_ms < 1000:
                patterns[PatternDimension.DECISION_PACE] = \
                    patterns.get(PatternDimension.DECISION_PACE, 0.5) * 0.7 + 0.3 * 0.8
        
        if "interaction_count" in interaction:
            # High interaction count might indicate communal orientation
            count = interaction["interaction_count"]
            if count > 10:
                patterns[PatternDimension.SOCIAL_ENERGY] = 0.7
            elif count < 3:
                patterns[PatternDimension.SOCIAL_ENERGY] = 0.3
            else:
                patterns[PatternDimension.SOCIAL_ENERGY] = 0.5
        
        return patterns
    
    def _calculate_spectrum_position(
        self, 
        text: str, 
        left_markers: List[str], 
        right_markers: List[str]
    ) -> float:
        """
        Calculate position on a spectrum based on marker words.
        
        Args:
            text: Text to analyze
            left_markers: Words indicating left side of spectrum (0.0)
            right_markers: Words indicating right side of spectrum (1.0)
            
        Returns:
            Position on spectrum from 0.0 to 1.0
        """
        text_lower = text.lower()
        left_count = sum(1 for marker in left_markers if marker in text_lower)
        right_count = sum(1 for marker in right_markers if marker in text_lower)
        
        total = left_count + right_count
        if total == 0:
            return 0.5  # Neutral position
        
        return right_count / total
    
    def reflect_patterns(self, user_id: str) -> List[str]:
        """
        Generate neutral reflections about observed patterns.
        
        Args:
            user_id: User whose patterns to reflect
            
        Returns:
            List of neutral observation statements
        """
        reflections = []
        
        for dimension, pattern in self.observed_patterns.items():
            if pattern.confidence > 0.6:  # Only reflect confident observations
                reflection = self._generate_reflection(dimension, pattern)
                if reflection:
                    reflections.append(reflection)
        
        # Add temporal observations if we have history
        if len(self.pattern_history) > 5:
            temporal_reflection = self._generate_temporal_reflection()
            if temporal_reflection:
                reflections.append(temporal_reflection)
        
        return reflections
    
    def _generate_reflection(self, dimension: str, pattern: ObservedPattern) -> str:
        """
        Generate a neutral reflection for a single pattern.
        
        Args:
            dimension: The pattern dimension
            pattern: The observed pattern
            
        Returns:
            Neutral reflection string
        """
        dim = PatternDimension[dimension] if isinstance(dimension, str) else dimension
        
        # Map dimensions to neutral descriptive language
        reflections_map = {
            PatternDimension.TRANSPARENCY: {
                0.2: "I notice your communications tend toward privacy",
                0.5: "I observe a balance between private and open communication",
                0.8: "I notice your communications tend toward openness"
            },
            PatternDimension.DECISION_PACE: {
                0.2: "I observe a pattern of deliberate, considered decision-making",
                0.5: "I notice variety in your decision-making pace",
                0.8: "I observe a pattern of quick, spontaneous decisions"
            },
            PatternDimension.LANGUAGE_STYLE: {
                0.2: "Your language patterns show directive communication",
                0.5: "Your language shows a mix of directive and descriptive styles",
                0.8: "Your language patterns show descriptive communication"
            },
            PatternDimension.SOCIAL_ENERGY: {
                0.2: "Interaction patterns suggest preference for focused, individual work",
                0.5: "Interaction patterns show flexibility between solo and group activities",
                0.8: "Interaction patterns suggest preference for collaborative engagement"
            }
        }
        
        if dim in reflections_map:
            # Find closest threshold
            thresholds = sorted(reflections_map[dim].keys())
            closest = min(thresholds, key=lambda x: abs(x - pattern.value))
            
            reflection = reflections_map[dim][closest]
            
            # Add trend if available
            if pattern.trend:
                if pattern.trend == "increasing":
                    reflection += " (shifting in this direction)"
                elif pattern.trend == "decreasing":
                    reflection += " (shifting away from this)"
                elif pattern.trend == "stable":
                    reflection += " (consistent pattern)"
            
            return reflection
        
        return None
    
    def _generate_temporal_reflection(self) -> str:
        """
        Generate reflection about patterns over time.
        
        Returns:
            Temporal reflection string
        """
        # Analyze pattern history for changes
        stable_count = sum(1 for p in self.observed_patterns.values() 
                          if p.trend == "stable")
        changing_count = sum(1 for p in self.observed_patterns.values() 
                            if p.trend in ["increasing", "decreasing"])
        
        if stable_count > changing_count:
            return "Over time, your patterns show consistency across most dimensions"
        elif changing_count > stable_count:
            return "Over time, your patterns show evolution and adaptation"
        else:
            return "Your patterns show both stable elements and areas of change"
    
    def update_patterns(self, dimension: PatternDimension, value: float, confidence: float = 0.7):
        """
        Update observed patterns with new observation.
        
        Args:
            dimension: The pattern dimension observed
            value: The observed value (0.0 to 1.0)
            confidence: Confidence in this observation
        """
        now = datetime.utcnow()
        
        if dimension.value in self.observed_patterns:
            # Update existing pattern
            existing = self.observed_patterns[dimension.value]
            
            # Calculate trend
            old_value = existing.value
            if abs(value - old_value) < 0.1:
                trend = "stable"
            elif value > old_value:
                trend = "increasing"
            else:
                trend = "decreasing"
            
            # Weighted average for value and confidence
            new_count = existing.observation_count + 1
            new_value = (existing.value * existing.observation_count + value) / new_count
            new_confidence = (existing.confidence * existing.observation_count + confidence) / new_count
            
            self.observed_patterns[dimension.value] = ObservedPattern(
                dimension=dimension,
                value=new_value,
                confidence=new_confidence,
                observation_count=new_count,
                last_observed=now,
                trend=trend
            )
        else:
            # Create new pattern observation
            self.observed_patterns[dimension.value] = ObservedPattern(
                dimension=dimension,
                value=value,
                confidence=confidence,
                observation_count=1,
                last_observed=now,
                trend=None  # No trend on first observation
            )
        
        # Add to history
        self.pattern_history.append({
            "dimension": dimension.value,
            "value": value,
            "confidence": confidence,
            "timestamp": now.isoformat()
        })
        
        # Keep history bounded (last 100 observations)
        if len(self.pattern_history) > 100:
            self.pattern_history = self.pattern_history[-100:]
    
    def generate_observation_receipt(self, user_id: str) -> Dict[str, Any]:
        """
        Generate a receipt for pattern observations (transparency).
        
        Args:
            user_id: User being observed
            
        Returns:
            Observation receipt
        """
        return {
            "receipt_type": "pattern_observation",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "mode": "mirror",
            "observed_dimensions": list(self.observed_patterns.keys()),
            "observation_count": sum(p.observation_count for p in self.observed_patterns.values()),
            "principles_applied": list(self.MIRROR_PRINCIPLES.keys()),
            "user_visible": True,
            "explanation": "Patterns observed without judgment for reflection purposes"
        }
    
    def reset_observations(self):
        """Reset all observations (user requested or privacy protection)."""
        self.observed_patterns.clear()
        self.pattern_history.clear()
        logger.info("Mirror observations reset")


# Factory function
def create_mirror_persona() -> MirrorPersona:
    """
    Create a new Mirror persona instance.
    
    Returns:
        MirrorPersona instance
    """
    return MirrorPersona()