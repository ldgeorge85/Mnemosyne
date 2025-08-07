"""
Reflection layer pipeline for Mnemosyne Protocol
Manages journaling, reflection fragments, and drift detection
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from enum import Enum

from pydantic import BaseModel, Field
from .base import Pipeline, PipelineStage
from ..models.memory import Memory
from ..models.reflection import Reflection, AgentType, ReflectionType
from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ReflectionFragment(BaseModel):
    """A fragment of reflection from an agent"""
    memory_id: str
    user_id: str
    agent_type: AgentType
    agent_id: str
    content: str
    confidence: float = 0.7
    relevance: float = 0.5
    coherence: float = 0.8
    reflection_type: ReflectionType = ReflectionType.ANALYSIS
    patterns: List[str] = Field(default_factory=list)
    connections: List[str] = Field(default_factory=list)
    questions: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    sub_signal: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DriftIndicator(BaseModel):
    """Indicator of semantic drift"""
    memory_id: str
    drift_index: float
    drift_type: str  # semantic, temporal, importance, emotional
    indicators: List[str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    requires_reevaluation: bool = False


class ReflectionJournal(BaseModel):
    """Journal entry for reflection cycle"""
    user_id: str
    memory_id: str
    fragments: List[ReflectionFragment]
    drift_indicators: List[DriftIndicator]
    overall_drift: float
    coherence_score: float
    signal_modulation: float
    consolidation_eligible: bool
    decay_timer_days: int = 7
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FragmentGenerationStage(PipelineStage[Memory, List[ReflectionFragment]]):
    """Generate reflection fragments from agents"""
    
    def __init__(self, agent_service=None):
        super().__init__("fragment_generation", required=True)
        self.agent_service = agent_service
    
    async def process(self, memory: Memory, context: Dict[str, Any]) -> List[ReflectionFragment]:
        """Generate fragments from different agents"""
        fragments = []
        
        # Select agents based on memory characteristics
        selected_agents = self.select_agents(memory)
        
        if self.agent_service:
            # Get reflections from actual agents
            agent_reflections = await self.agent_service.reflect_on_memory(
                memory=memory,
                agents=selected_agents
            )
            
            for reflection in agent_reflections:
                fragment = ReflectionFragment(
                    memory_id=str(memory.id),
                    user_id=str(memory.user_id),
                    agent_type=reflection.agent_type,
                    agent_id=reflection.agent_id,
                    content=reflection.content,
                    confidence=reflection.confidence,
                    relevance=reflection.relevance,
                    coherence=reflection.coherence,
                    reflection_type=reflection.reflection_type,
                    patterns=reflection.patterns,
                    connections=reflection.connections,
                    questions=reflection.questions,
                    recommendations=reflection.recommendations,
                    sub_signal=reflection.sub_signal,
                    metadata=reflection.metadata
                )
                fragments.append(fragment)
        else:
            # Generate mock fragments for testing
            for agent_type in selected_agents:
                fragment = self.generate_mock_fragment(memory, agent_type)
                fragments.append(fragment)
        
        logger.info(f"Generated {len(fragments)} reflection fragments for memory {memory.id}")
        return fragments
    
    def select_agents(self, memory: Memory) -> List[AgentType]:
        """Select appropriate agents based on memory content"""
        agents = []
        
        # Always include core agents
        agents.extend([AgentType.LIBRARIAN, AgentType.MYCELIUM])
        
        # Add domain-specific agents
        if 'technology' in memory.domains or 'code' in memory.tags:
            agents.append(AgentType.ENGINEER)
        
        if 'philosophy' in memory.domains or 'meaning' in memory.tags:
            agents.append(AgentType.SAGE)
            agents.append(AgentType.MYSTIC)
        
        if memory.emotional_valence > 0.5 or memory.emotional_valence < -0.5:
            agents.append(AgentType.HEALER)
        
        if 'question' in memory.tags:
            agents.append(AgentType.SCHOLAR)
            agents.append(AgentType.CRITIC)
        
        if memory.importance > 0.7:
            agents.append(AgentType.PROPHET)
        
        if 'conflict' in memory.tags or 'problem' in memory.tags:
            agents.append(AgentType.GUARDIAN)
            agents.append(AgentType.ARBITRATOR)
        
        # Limit to max agents
        max_agents = context.get('max_agents', settings.max_concurrent_agents)
        return list(set(agents[:max_agents]))
    
    def generate_mock_fragment(self, memory: Memory, agent_type: AgentType) -> ReflectionFragment:
        """Generate mock fragment for testing"""
        agent_perspectives = {
            AgentType.ENGINEER: {
                'content': f"Technical analysis: {memory.content[:100]}",
                'type': ReflectionType.ANALYSIS,
                'patterns': ['structured_thinking', 'systematic_approach'],
                'confidence': 0.8
            },
            AgentType.LIBRARIAN: {
                'content': f"Knowledge organization: {memory.content[:100]}",
                'type': ReflectionType.CONNECTION,
                'connections': ['related_concept_1', 'related_concept_2'],
                'confidence': 0.85
            },
            AgentType.SAGE: {
                'content': f"Timeless wisdom in: {memory.content[:100]}",
                'type': ReflectionType.INSIGHT,
                'patterns': ['universal_truth', 'recurring_pattern'],
                'confidence': 0.75
            },
            AgentType.MYSTIC: {
                'content': f"Hidden connections: {memory.content[:100]}",
                'type': ReflectionType.PATTERN,
                'patterns': ['synchronicity', 'emergence'],
                'confidence': 0.7
            },
            AgentType.CRITIC: {
                'content': f"Critical examination: {memory.content[:100]}",
                'type': ReflectionType.QUESTION,
                'questions': ['What assumptions are made?', 'What is missing?'],
                'confidence': 0.9
            }
        }
        
        perspective = agent_perspectives.get(
            agent_type,
            {
                'content': f"Reflection on: {memory.content[:100]}",
                'type': ReflectionType.ANALYSIS,
                'confidence': 0.7
            }
        )
        
        return ReflectionFragment(
            memory_id=str(memory.id),
            user_id=str(memory.user_id),
            agent_type=agent_type,
            agent_id=f"{agent_type.value}_001",
            content=perspective['content'],
            confidence=perspective.get('confidence', 0.7),
            relevance=0.5 + memory.importance * 0.3,
            coherence=0.8,
            reflection_type=perspective.get('type', ReflectionType.ANALYSIS),
            patterns=perspective.get('patterns', []),
            connections=perspective.get('connections', []),
            questions=perspective.get('questions', []),
            recommendations=perspective.get('recommendations', []),
            sub_signal={
                'agent': agent_type.value,
                'symbol': agent_type.symbol,
                'modulation': 0.1
            }
        )


class DriftCalculationStage(PipelineStage[Tuple[Memory, List[ReflectionFragment]], List[DriftIndicator]]):
    """Calculate semantic drift from reflections"""
    
    def __init__(self):
        super().__init__("drift_calculation", required=True)
    
    async def process(
        self,
        data: Tuple[Memory, List[ReflectionFragment]],
        context: Dict[str, Any]
    ) -> List[DriftIndicator]:
        """Calculate drift indicators"""
        memory, fragments = data
        drift_indicators = []
        
        # Semantic drift from reflections
        if fragments:
            confidence_scores = [f.confidence for f in fragments]
            coherence_scores = [f.coherence for f in fragments]
            
            # Low confidence indicates drift
            avg_confidence = np.mean(confidence_scores)
            semantic_drift = 1.0 - avg_confidence
            
            if semantic_drift > 0.3:
                drift_indicators.append(DriftIndicator(
                    memory_id=str(memory.id),
                    drift_index=semantic_drift,
                    drift_type='semantic',
                    indicators=['low_agent_confidence', 'divergent_interpretations'],
                    requires_reevaluation=semantic_drift > 0.7
                ))
            
            # Coherence drift
            avg_coherence = np.mean(coherence_scores)
            coherence_drift = 1.0 - avg_coherence
            
            if coherence_drift > 0.3:
                drift_indicators.append(DriftIndicator(
                    memory_id=str(memory.id),
                    drift_index=coherence_drift,
                    drift_type='coherence',
                    indicators=['fragmented_understanding'],
                    requires_reevaluation=coherence_drift > 0.6
                ))
        
        # Temporal drift (memory age)
        if memory.occurred_at:
            age_days = (datetime.utcnow() - memory.occurred_at).days
            if age_days > 30:
                temporal_drift = min(1.0, age_days / 365)  # Max drift at 1 year
                drift_indicators.append(DriftIndicator(
                    memory_id=str(memory.id),
                    drift_index=temporal_drift,
                    drift_type='temporal',
                    indicators=[f'memory_age_{age_days}_days'],
                    requires_reevaluation=age_days > 90
                ))
        
        # Importance drift (decreasing relevance)
        if memory.last_accessed_at:
            days_since_access = (datetime.utcnow() - memory.last_accessed_at).days
            if days_since_access > 14:
                importance_drift = min(1.0, days_since_access / 60)
                drift_indicators.append(DriftIndicator(
                    memory_id=str(memory.id),
                    drift_index=importance_drift,
                    drift_type='importance',
                    indicators=['low_access_frequency'],
                    requires_reevaluation=days_since_access > 30
                ))
        
        # Emotional drift (valence changes)
        if fragments:
            fragment_valences = []
            for fragment in fragments:
                # Extract emotional indicators from fragment
                if 'emotional_valence' in fragment.metadata:
                    fragment_valences.append(fragment.metadata['emotional_valence'])
            
            if fragment_valences and memory.emotional_valence is not None:
                avg_fragment_valence = np.mean(fragment_valences)
                emotional_drift = abs(memory.emotional_valence - avg_fragment_valence)
                
                if emotional_drift > 0.3:
                    drift_indicators.append(DriftIndicator(
                        memory_id=str(memory.id),
                        drift_index=emotional_drift,
                        drift_type='emotional',
                        indicators=['valence_shift'],
                        requires_reevaluation=emotional_drift > 0.6
                    ))
        
        return drift_indicators


class SignalModulationStage(PipelineStage[Tuple[List[ReflectionFragment], List[DriftIndicator]], float]):
    """Calculate signal modulation from reflections"""
    
    def __init__(self):
        super().__init__("signal_modulation", required=False)
    
    async def process(
        self,
        data: Tuple[List[ReflectionFragment], List[DriftIndicator]],
        context: Dict[str, Any]
    ) -> float:
        """Calculate how reflections modulate user's Deep Signal"""
        fragments, drift_indicators = data
        
        if not fragments:
            return 0.0
        
        # Base modulation from fragment sub-signals
        modulations = []
        for fragment in fragments:
            if fragment.sub_signal:
                modulations.append(fragment.sub_signal.get('modulation', 0))
        
        base_modulation = np.mean(modulations) if modulations else 0.0
        
        # Adjust for drift
        if drift_indicators:
            avg_drift = np.mean([d.drift_index for d in drift_indicators])
            # High drift reduces positive modulation, increases negative
            if base_modulation > 0:
                base_modulation *= (1 - avg_drift * 0.5)
            else:
                base_modulation *= (1 + avg_drift * 0.5)
        
        # Adjust for fragment confidence
        avg_confidence = np.mean([f.confidence for f in fragments])
        base_modulation *= avg_confidence
        
        # Clamp to -1 to 1
        return max(-1.0, min(1.0, base_modulation))


class JournalCreationStage(PipelineStage[Dict[str, Any], ReflectionJournal]):
    """Create reflection journal entry"""
    
    def __init__(self):
        super().__init__("journal_creation", required=True)
    
    async def process(self, data: Dict[str, Any], context: Dict[str, Any]) -> ReflectionJournal:
        """Create journal entry from reflection data"""
        memory = data['memory']
        fragments = data['fragments']
        drift_indicators = data['drift_indicators']
        signal_modulation = data['signal_modulation']
        
        # Calculate overall drift
        if drift_indicators:
            overall_drift = np.mean([d.drift_index for d in drift_indicators])
        else:
            overall_drift = 0.0
        
        # Calculate coherence score
        if fragments:
            coherence_scores = [f.coherence for f in fragments]
            coherence_score = np.mean(coherence_scores)
        else:
            coherence_score = 1.0
        
        # Determine if eligible for consolidation
        consolidation_eligible = (
            len(fragments) >= 3 and
            coherence_score > 0.6 and
            overall_drift < 0.5 and
            memory.consolidation_count < 3
        )
        
        # Calculate decay timer based on importance and drift
        base_decay = 7  # days
        if memory.importance > 0.7:
            base_decay = 14
        elif memory.importance < 0.3:
            base_decay = 3
        
        # Adjust for drift
        if overall_drift > 0.5:
            base_decay = max(1, base_decay // 2)
        
        journal = ReflectionJournal(
            user_id=str(memory.user_id),
            memory_id=str(memory.id),
            fragments=fragments,
            drift_indicators=drift_indicators,
            overall_drift=overall_drift,
            coherence_score=coherence_score,
            signal_modulation=signal_modulation,
            consolidation_eligible=consolidation_eligible,
            decay_timer_days=base_decay,
            metadata={
                'memory_importance': memory.importance,
                'memory_type': memory.memory_type.value,
                'fragment_count': len(fragments),
                'drift_count': len(drift_indicators),
                'requires_reevaluation': any(d.requires_reevaluation for d in drift_indicators)
            }
        )
        
        return journal


class ReflectionPipeline(Pipeline[Memory, ReflectionJournal]):
    """Complete reflection pipeline"""
    
    def __init__(self, agent_service=None):
        self.fragment_stage = FragmentGenerationStage(agent_service)
        self.drift_stage = DriftCalculationStage()
        self.modulation_stage = SignalModulationStage()
        self.journal_stage = JournalCreationStage()
        
        super().__init__(
            name="reflection_pipeline",
            stages=[],  # Will compose manually
            parallel=False,
            continue_on_error=False
        )
    
    async def execute(self, memory: Memory) -> ReflectionJournal:
        """Execute reflection pipeline"""
        try:
            # Generate fragments
            fragments_result = await self.fragment_stage.execute(memory, self._context)
            if fragments_result.status != 'completed':
                raise Exception(f"Fragment generation failed: {fragments_result.error}")
            fragments = fragments_result.data
            
            # Calculate drift
            drift_result = await self.drift_stage.execute((memory, fragments), self._context)
            if drift_result.status != 'completed':
                raise Exception(f"Drift calculation failed: {drift_result.error}")
            drift_indicators = drift_result.data
            
            # Calculate signal modulation
            modulation_result = await self.modulation_stage.execute(
                (fragments, drift_indicators),
                self._context
            )
            signal_modulation = modulation_result.data if modulation_result.status == 'completed' else 0.0
            
            # Create journal
            journal_data = {
                'memory': memory,
                'fragments': fragments,
                'drift_indicators': drift_indicators,
                'signal_modulation': signal_modulation
            }
            
            journal_result = await self.journal_stage.execute(journal_data, self._context)
            if journal_result.status != 'completed':
                raise Exception(f"Journal creation failed: {journal_result.error}")
            
            return journal_result.data
            
        except Exception as e:
            logger.error(f"Reflection pipeline failed: {e}")
            raise


class ReflectionLayerManager:
    """Manages the reflection layer for memories"""
    
    def __init__(self, reflection_pipeline: ReflectionPipeline):
        self.pipeline = reflection_pipeline
        self.active_reflections = {}
        self.reevaluation_queue = asyncio.Queue()
    
    async def trigger_reflection(self, memory: Memory) -> ReflectionJournal:
        """Trigger reflection on a memory"""
        memory_id = str(memory.id)
        
        # Check if reflection already in progress
        if memory_id in self.active_reflections:
            logger.warning(f"Reflection already in progress for memory {memory_id}")
            return await self.active_reflections[memory_id]
        
        # Start reflection
        reflection_task = asyncio.create_task(self.pipeline.execute(memory))
        self.active_reflections[memory_id] = reflection_task
        
        try:
            journal = await reflection_task
            
            # Check if reevaluation needed
            if journal.metadata.get('requires_reevaluation'):
                await self.reevaluation_queue.put(memory)
            
            return journal
            
        finally:
            # Clean up
            if memory_id in self.active_reflections:
                del self.active_reflections[memory_id]
    
    async def process_reevaluations(self):
        """Process memories that need reevaluation"""
        while True:
            try:
                memory = await self.reevaluation_queue.get()
                logger.info(f"Reevaluating memory {memory.id} due to high drift")
                
                # Trigger new reflection
                await self.trigger_reflection(memory)
                
                # Small delay between reevaluations
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Reevaluation failed: {e}")
                await asyncio.sleep(5)


# Export classes
__all__ = [
    'ReflectionFragment',
    'DriftIndicator',
    'ReflectionJournal',
    'FragmentGenerationStage',
    'DriftCalculationStage',
    'SignalModulationStage',
    'JournalCreationStage',
    'ReflectionPipeline',
    'ReflectionLayerManager',
]