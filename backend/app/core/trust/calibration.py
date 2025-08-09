"""
Trust Calibration Implementation
Based on Lee & See (2004) trust calibration framework
Track 1: Production-ready trust mechanisms
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field, validator
from enum import Enum
import math


class TrustDimension(str, Enum):
    """Dimensions of trust in automation"""
    PERFORMANCE = "performance"  # How well the system performs
    PURPOSE = "purpose"  # What the system is designed to do
    PROCESS = "process"  # How the system works


class CalibrationLevel(str, Enum):
    """Trust calibration levels"""
    UNDERTRUST = "undertrust"  # Trust < actual reliability
    CALIBRATED = "calibrated"  # Trust ≈ actual reliability
    OVERTRUST = "overtrust"  # Trust > actual reliability
    DISTRUST = "distrust"  # Very low trust regardless of reliability
    BLIND_TRUST = "blind_trust"  # Very high trust regardless of reliability


class TrustSignal(BaseModel):
    """Individual trust signal/evidence"""
    dimension: TrustDimension
    signal_type: str  # e.g., "success", "failure", "explanation"
    value: float  # -1 to 1 (negative = distrust, positive = trust)
    weight: float = 1.0  # Importance of this signal
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    context: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('value')
    def validate_value(cls, v):
        if not -1 <= v <= 1:
            raise ValueError("Trust signal value must be between -1 and 1")
        return v


class TrustState(BaseModel):
    """Current trust state for a system/component"""
    
    # Trust scores by dimension (0-1 scale)
    performance_trust: float = 0.5
    purpose_trust: float = 0.5
    process_trust: float = 0.5
    
    # Overall trust (weighted average)
    overall_trust: float = 0.5
    
    # Actual system reliability (if known)
    actual_reliability: Optional[float] = None
    
    # Calibration assessment
    calibration: CalibrationLevel = CalibrationLevel.CALIBRATED
    calibration_gap: float = 0.0  # Difference between trust and reliability
    
    # Trust dynamics
    trust_velocity: float = 0.0  # Rate of trust change
    volatility: float = 0.0  # How much trust fluctuates
    
    # History
    signal_count: int = 0
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @validator('performance_trust', 'purpose_trust', 'process_trust', 'overall_trust')
    def validate_trust_scores(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Trust scores must be between 0 and 1")
        return v


class TrustCalibrator:
    """
    Implements Lee & See trust calibration framework
    Helps users maintain appropriate trust in AI systems
    """
    
    def __init__(self, 
                 initial_trust: float = 0.5,
                 learning_rate: float = 0.1,
                 decay_rate: float = 0.01):
        """
        Initialize trust calibrator
        
        Args:
            initial_trust: Starting trust level (0-1)
            learning_rate: How quickly trust updates with new signals
            decay_rate: How quickly trust returns to baseline without signals
        """
        self.initial_trust = initial_trust
        self.learning_rate = learning_rate
        self.decay_rate = decay_rate
        
        # Trust states for different components
        self.trust_states: Dict[str, TrustState] = {}
        
        # Trust history for analysis
        self.signal_history: Dict[str, List[TrustSignal]] = {}
    
    def get_or_create_state(self, component_id: str) -> TrustState:
        """Get or create trust state for a component"""
        if component_id not in self.trust_states:
            self.trust_states[component_id] = TrustState(
                performance_trust=self.initial_trust,
                purpose_trust=self.initial_trust,
                process_trust=self.initial_trust,
                overall_trust=self.initial_trust
            )
            self.signal_history[component_id] = []
        return self.trust_states[component_id]
    
    def add_trust_signal(
        self,
        component_id: str,
        signal: TrustSignal
    ) -> TrustState:
        """
        Process a trust signal and update trust state
        
        Args:
            component_id: ID of the component (e.g., "agent_engineer")
            signal: Trust signal to process
            
        Returns:
            Updated trust state
        """
        state = self.get_or_create_state(component_id)
        
        # Store signal in history
        if component_id not in self.signal_history:
            self.signal_history[component_id] = []
        self.signal_history[component_id].append(signal)
        
        # Update relevant dimension
        old_trust = getattr(state, f"{signal.dimension.value}_trust")
        
        # Calculate trust update using exponential moving average
        trust_delta = signal.value * signal.weight * self.learning_rate
        new_trust = old_trust + trust_delta * (1 - old_trust) if trust_delta > 0 else old_trust + trust_delta * old_trust
        new_trust = max(0, min(1, new_trust))  # Clamp to [0, 1]
        
        # Update trust state
        setattr(state, f"{signal.dimension.value}_trust", new_trust)
        
        # Update overall trust (weighted average)
        state.overall_trust = (
            state.performance_trust * 0.5 +  # Performance heavily weighted
            state.purpose_trust * 0.25 +
            state.process_trust * 0.25
        )
        
        # Calculate trust velocity
        time_delta = (datetime.now(timezone.utc) - state.last_updated).total_seconds()
        if time_delta > 0:
            state.trust_velocity = (new_trust - old_trust) / time_delta
        
        # Update volatility (standard deviation of recent signals)
        recent_signals = self.signal_history[component_id][-20:]  # Last 20 signals
        if len(recent_signals) > 1:
            values = [s.value for s in recent_signals]
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            state.volatility = math.sqrt(variance)
        
        # Update calibration if we have reliability data
        if state.actual_reliability is not None:
            state.calibration_gap = state.overall_trust - state.actual_reliability
            state.calibration = self._assess_calibration(
                state.overall_trust,
                state.actual_reliability
            )
        
        state.signal_count += 1
        state.last_updated = datetime.now(timezone.utc)
        
        return state
    
    def _assess_calibration(
        self,
        trust: float,
        reliability: float,
        threshold: float = 0.15
    ) -> CalibrationLevel:
        """
        Assess trust calibration level
        
        Args:
            trust: Current trust level (0-1)
            reliability: Actual system reliability (0-1)
            threshold: Acceptable calibration gap
            
        Returns:
            Calibration level
        """
        gap = trust - reliability
        
        if trust < 0.2:
            return CalibrationLevel.DISTRUST
        elif trust > 0.9:
            return CalibrationLevel.BLIND_TRUST
        elif abs(gap) <= threshold:
            return CalibrationLevel.CALIBRATED
        elif gap > threshold:
            return CalibrationLevel.OVERTRUST
        else:
            return CalibrationLevel.UNDERTRUST
    
    def decay_trust(self, component_id: str, time_elapsed: float) -> TrustState:
        """
        Apply trust decay over time (trust returns to baseline without signals)
        
        Args:
            component_id: Component ID
            time_elapsed: Time since last update in seconds
            
        Returns:
            Updated trust state
        """
        state = self.get_or_create_state(component_id)
        
        # Apply exponential decay toward initial trust
        decay_factor = math.exp(-self.decay_rate * time_elapsed / 3600)  # Per hour
        
        for dimension in ["performance", "purpose", "process"]:
            current = getattr(state, f"{dimension}_trust")
            decayed = self.initial_trust + (current - self.initial_trust) * decay_factor
            setattr(state, f"{dimension}_trust", decayed)
        
        # Update overall trust
        state.overall_trust = (
            state.performance_trust * 0.5 +
            state.purpose_trust * 0.25 +
            state.process_trust * 0.25
        )
        
        state.last_updated = datetime.now(timezone.utc)
        return state
    
    def get_trust_recommendation(
        self,
        component_id: str
    ) -> Dict[str, Any]:
        """
        Get trust recommendation for user
        
        Args:
            component_id: Component ID
            
        Returns:
            Trust recommendation with explanation
        """
        state = self.get_or_create_state(component_id)
        
        recommendations = []
        
        # Check calibration
        if state.calibration == CalibrationLevel.OVERTRUST:
            recommendations.append({
                "type": "warning",
                "message": "Your trust may be higher than warranted. Verify outputs carefully.",
                "suggestion": "Review recent failures and limitations"
            })
        elif state.calibration == CalibrationLevel.UNDERTRUST:
            recommendations.append({
                "type": "info",
                "message": "The system is more reliable than your trust level suggests.",
                "suggestion": "Review recent successes and capabilities"
            })
        elif state.calibration == CalibrationLevel.DISTRUST:
            recommendations.append({
                "type": "alert",
                "message": "Very low trust detected. Consider if the system is appropriate for your needs.",
                "suggestion": "Review system purpose and alternatives"
            })
        elif state.calibration == CalibrationLevel.BLIND_TRUST:
            recommendations.append({
                "type": "warning",
                "message": "Very high trust detected. Remember to maintain critical oversight.",
                "suggestion": "Stay aware of system limitations"
            })
        
        # Check volatility
        if state.volatility > 0.5:
            recommendations.append({
                "type": "info",
                "message": "Trust levels are fluctuating significantly.",
                "suggestion": "Allow more time to establish stable trust"
            })
        
        # Check specific dimensions
        if state.performance_trust < 0.3:
            recommendations.append({
                "type": "warning",
                "message": "Low performance trust detected.",
                "suggestion": "Review system accuracy and error rates"
            })
        
        if state.purpose_trust < 0.3:
            recommendations.append({
                "type": "info",
                "message": "Unclear about system purpose.",
                "suggestion": "Review documentation about what the system is designed to do"
            })
        
        if state.process_trust < 0.3:
            recommendations.append({
                "type": "info",
                "message": "Low process trust detected.",
                "suggestion": "Learn more about how the system works"
            })
        
        return {
            "component_id": component_id,
            "overall_trust": state.overall_trust,
            "calibration": state.calibration.value,
            "recommendations": recommendations,
            "trust_scores": {
                "performance": state.performance_trust,
                "purpose": state.purpose_trust,
                "process": state.process_trust
            }
        }
    
    def calculate_system_reliability(
        self,
        component_id: str,
        success_count: int,
        total_count: int,
        confidence_level: float = 0.95
    ) -> Tuple[float, Tuple[float, float]]:
        """
        Calculate system reliability with confidence interval
        
        Args:
            component_id: Component ID
            success_count: Number of successful operations
            total_count: Total number of operations
            confidence_level: Confidence level for interval
            
        Returns:
            Tuple of (point estimate, (lower bound, upper bound))
        """
        if total_count == 0:
            return 0.5, (0.0, 1.0)  # Maximum uncertainty
        
        # Point estimate
        reliability = success_count / total_count
        
        # Wilson score interval for confidence interval
        z = 1.96 if confidence_level == 0.95 else 2.58  # z-score
        
        denominator = 1 + z**2 / total_count
        center = (reliability + z**2 / (2 * total_count)) / denominator
        
        margin = z * math.sqrt(
            (reliability * (1 - reliability) + z**2 / (4 * total_count)) / total_count
        ) / denominator
        
        lower = max(0, center - margin)
        upper = min(1, center + margin)
        
        # Update trust state with reliability
        state = self.get_or_create_state(component_id)
        state.actual_reliability = reliability
        state.calibration_gap = state.overall_trust - reliability
        state.calibration = self._assess_calibration(state.overall_trust, reliability)
        
        return reliability, (lower, upper)


# Service layer for trust calibration
class TrustCalibrationService:
    """Service for managing trust calibration"""
    
    def __init__(self):
        self.calibrator = TrustCalibrator()
        
        # Track success/failure for reliability calculation
        self.operation_counts: Dict[str, Dict[str, int]] = {}
    
    async def record_success(
        self,
        component_id: str,
        dimension: TrustDimension = TrustDimension.PERFORMANCE
    ) -> TrustState:
        """Record a successful operation"""
        
        # Track for reliability
        if component_id not in self.operation_counts:
            self.operation_counts[component_id] = {"success": 0, "total": 0}
        self.operation_counts[component_id]["success"] += 1
        self.operation_counts[component_id]["total"] += 1
        
        # Create positive trust signal
        signal = TrustSignal(
            dimension=dimension,
            signal_type="success",
            value=0.1,  # Small positive signal
            context={"operation": "success"}
        )
        
        return self.calibrator.add_trust_signal(component_id, signal)
    
    async def record_failure(
        self,
        component_id: str,
        dimension: TrustDimension = TrustDimension.PERFORMANCE,
        severity: float = 0.5
    ) -> TrustState:
        """Record a failed operation"""
        
        # Track for reliability
        if component_id not in self.operation_counts:
            self.operation_counts[component_id] = {"success": 0, "total": 0}
        self.operation_counts[component_id]["total"] += 1
        
        # Create negative trust signal
        signal = TrustSignal(
            dimension=dimension,
            signal_type="failure",
            value=-0.1 * severity,  # Negative signal scaled by severity
            context={"operation": "failure", "severity": severity}
        )
        
        return self.calibrator.add_trust_signal(component_id, signal)
    
    async def record_explanation(
        self,
        component_id: str,
        quality: float
    ) -> TrustState:
        """Record that system provided an explanation"""
        
        # Explanations improve process trust
        signal = TrustSignal(
            dimension=TrustDimension.PROCESS,
            signal_type="explanation",
            value=0.05 * quality,  # Small positive signal
            context={"explanation_quality": quality}
        )
        
        return self.calibrator.add_trust_signal(component_id, signal)
    
    async def get_trust_state(self, component_id: str) -> TrustState:
        """Get current trust state for a component"""
        return self.calibrator.get_or_create_state(component_id)
    
    async def get_reliability(
        self,
        component_id: str
    ) -> Optional[Tuple[float, Tuple[float, float]]]:
        """Get calculated reliability for a component"""
        
        if component_id not in self.operation_counts:
            return None
        
        counts = self.operation_counts[component_id]
        if counts["total"] == 0:
            return None
        
        return self.calibrator.calculate_system_reliability(
            component_id,
            counts["success"],
            counts["total"]
        )
    
    async def get_recommendations(self, component_id: str) -> Dict[str, Any]:
        """Get trust recommendations for a component"""
        return self.calibrator.get_trust_recommendation(component_id)