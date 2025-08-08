"""
Dialogue manager for Mnemosyne Protocol
Coordinates multi-agent dialogues and conversations
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict
import json

from .base import BaseAgent, AgentContext, ReflectionFragment
from core.redis_client import redis_manager

logger = logging.getLogger(__name__)


class DialogueTurn:
    """Represents a single turn in a dialogue"""
    
    def __init__(
        self,
        agent_id: str,
        content: str,
        turn_number: int,
        timestamp: datetime = None
    ):
        self.agent_id = agent_id
        self.content = content
        self.turn_number = turn_number
        self.timestamp = timestamp or datetime.utcnow()
        self.metadata: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "agent_id": self.agent_id,
            "content": self.content,
            "turn_number": self.turn_number,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class DialogueSession:
    """Manages a dialogue session between agents"""
    
    def __init__(
        self,
        session_id: str,
        topic: str,
        participants: List[BaseAgent],
        max_turns: int = 10
    ):
        self.session_id = session_id
        self.topic = topic
        self.participants = participants
        self.max_turns = max_turns
        self.turns: List[DialogueTurn] = []
        self.created_at = datetime.utcnow()
        self.metadata: Dict[str, Any] = {}
        self.convergence_score = 0.0
    
    def add_turn(self, turn: DialogueTurn):
        """Add a turn to the dialogue"""
        self.turns.append(turn)
    
    def get_context_for_agent(self, agent: BaseAgent) -> str:
        """Get dialogue context for an agent"""
        context_parts = [f"Topic: {self.topic}\n"]
        
        # Add recent turns
        recent_turns = self.turns[-5:]  # Last 5 turns
        for turn in recent_turns:
            if turn.agent_id == agent.agent_id:
                context_parts.append(f"You said: {turn.content}")
            else:
                context_parts.append(f"{turn.agent_id} said: {turn.content}")
        
        return "\n".join(context_parts)
    
    def calculate_convergence(self) -> float:
        """Calculate dialogue convergence score"""
        if len(self.turns) < 2:
            return 0.0
        
        # Simple convergence: measure similarity of recent responses
        recent_contents = [turn.content for turn in self.turns[-3:]]
        
        # Check for short responses (sign of convergence)
        avg_length = sum(len(c) for c in recent_contents) / len(recent_contents)
        if avg_length < 50:
            return 0.9
        
        # Check for repetition
        unique_words = set()
        total_words = 0
        for content in recent_contents:
            words = content.lower().split()
            unique_words.update(words)
            total_words += len(words)
        
        if total_words > 0:
            uniqueness = len(unique_words) / total_words
            convergence = 1.0 - uniqueness
            return min(convergence * 2, 1.0)  # Scale and cap at 1.0
        
        return 0.0
    
    def should_continue(self) -> bool:
        """Check if dialogue should continue"""
        if len(self.turns) >= self.max_turns:
            return False
        
        self.convergence_score = self.calculate_convergence()
        if self.convergence_score > 0.8:
            return False
        
        return True
    
    def get_summary(self) -> Dict[str, Any]:
        """Get dialogue summary"""
        return {
            "session_id": self.session_id,
            "topic": self.topic,
            "participants": [p.agent_id for p in self.participants],
            "turn_count": len(self.turns),
            "convergence_score": self.convergence_score,
            "created_at": self.created_at.isoformat(),
            "duration_seconds": (
                (self.turns[-1].timestamp - self.created_at).total_seconds()
                if self.turns else 0
            )
        }


class DialogueManager:
    """Manages multi-agent dialogues"""
    
    def __init__(self):
        self.active_sessions: Dict[str, DialogueSession] = {}
        self.session_history: List[str] = []
        self.max_concurrent_sessions = 5
    
    async def start_dialogue(
        self,
        topic: str,
        participants: List[BaseAgent],
        user_id: str,
        max_turns: int = 10,
        structured: bool = False
    ) -> DialogueSession:
        """Start a new dialogue session"""
        # Check concurrent session limit
        if len(self.active_sessions) >= self.max_concurrent_sessions:
            # Remove oldest session
            oldest_id = self.session_history[0]
            await self.end_dialogue(oldest_id)
        
        # Create session
        session_id = f"dialogue_{user_id}_{datetime.utcnow().timestamp()}"
        session = DialogueSession(
            session_id=session_id,
            topic=topic,
            participants=participants,
            max_turns=max_turns
        )
        
        self.active_sessions[session_id] = session
        self.session_history.append(session_id)
        
        logger.info(f"Started dialogue session {session_id} on topic: {topic}")
        
        # Run dialogue
        if structured:
            await self._run_structured_dialogue(session, user_id)
        else:
            await self._run_free_dialogue(session, user_id)
        
        return session
    
    async def _run_free_dialogue(
        self,
        session: DialogueSession,
        user_id: str
    ):
        """Run free-form dialogue"""
        turn_number = 0
        
        while session.should_continue():
            turn_number += 1
            
            # Each participant responds
            for participant in session.participants:
                if not session.should_continue():
                    break
                
                # Build context for agent
                dialogue_context = session.get_context_for_agent(participant)
                
                context = AgentContext(
                    user_id=user_id,
                    trigger_reason=f"Dialogue on: {session.topic}",
                    metadata={
                        "dialogue_context": dialogue_context,
                        "turn_number": turn_number
                    }
                )
                
                # Get agent response
                try:
                    fragments = await participant.reflect(context)
                    
                    if fragments:
                        # Combine fragments into response
                        response = " ".join(f.content for f in fragments)
                        
                        # Add turn
                        turn = DialogueTurn(
                            agent_id=participant.agent_id,
                            content=response,
                            turn_number=turn_number
                        )
                        session.add_turn(turn)
                        
                except Exception as e:
                    logger.error(f"Agent {participant.agent_id} failed in dialogue: {e}")
            
            # Small delay between rounds
            await asyncio.sleep(0.5)
        
        logger.info(f"Dialogue {session.session_id} completed with {len(session.turns)} turns")
    
    async def _run_structured_dialogue(
        self,
        session: DialogueSession,
        user_id: str
    ):
        """Run structured dialogue with specific phases"""
        phases = [
            ("opening", "Present your initial perspective on the topic"),
            ("exploration", "Explore different aspects and implications"),
            ("synthesis", "Synthesize insights from the discussion"),
            ("conclusion", "Provide your final thoughts")
        ]
        
        for phase_name, phase_prompt in phases:
            if not session.should_continue():
                break
            
            # Each participant responds to the phase
            for participant in session.participants:
                context = AgentContext(
                    user_id=user_id,
                    trigger_reason=f"Dialogue phase '{phase_name}': {phase_prompt}",
                    metadata={
                        "topic": session.topic,
                        "phase": phase_name,
                        "dialogue_history": [t.to_dict() for t in session.turns[-5:]]
                    }
                )
                
                try:
                    fragments = await participant.reflect(context)
                    
                    if fragments:
                        response = " ".join(f.content for f in fragments)
                        
                        turn = DialogueTurn(
                            agent_id=participant.agent_id,
                            content=f"[{phase_name.upper()}] {response}",
                            turn_number=len(session.turns) + 1
                        )
                        turn.metadata["phase"] = phase_name
                        session.add_turn(turn)
                        
                except Exception as e:
                    logger.error(f"Agent {participant.agent_id} failed in phase {phase_name}: {e}")
    
    async def moderate_dialogue(
        self,
        session_id: str,
        moderator: BaseAgent
    ) -> List[str]:
        """Have an agent moderate an existing dialogue"""
        session = self.active_sessions.get(session_id)
        if not session:
            return []
        
        # Build moderation context
        dialogue_summary = {
            "topic": session.topic,
            "participants": [p.agent_id for p in session.participants],
            "turn_count": len(session.turns),
            "convergence": session.convergence_score
        }
        
        context = AgentContext(
            user_id="system",
            trigger_reason="Moderate dialogue",
            metadata={
                "dialogue_summary": dialogue_summary,
                "recent_turns": [t.to_dict() for t in session.turns[-5:]]
            }
        )
        
        # Get moderation insights
        fragments = await moderator.reflect(context)
        
        insights = []
        for fragment in fragments:
            if fragment.fragment_type in ["insight", "suggestion"]:
                insights.append(fragment.content)
        
        return insights
    
    async def synthesize_dialogue(
        self,
        session_id: str,
        synthesizer: Optional[BaseAgent] = None
    ) -> Dict[str, Any]:
        """Synthesize insights from a dialogue"""
        session = self.active_sessions.get(session_id)
        if not session:
            # Try to load from history
            return {"error": "Session not found"}
        
        synthesis = {
            "session_id": session_id,
            "topic": session.topic,
            "summary": session.get_summary(),
            "key_points": [],
            "agreements": [],
            "disagreements": [],
            "insights": []
        }
        
        # Extract key points from turns
        for turn in session.turns:
            # Simple extraction - can be enhanced
            if "insight" in turn.content.lower():
                synthesis["insights"].append({
                    "agent": turn.agent_id,
                    "content": turn.content[:200]
                })
            elif "agree" in turn.content.lower():
                synthesis["agreements"].append({
                    "agent": turn.agent_id,
                    "content": turn.content[:200]
                })
            elif "disagree" in turn.content.lower() or "however" in turn.content.lower():
                synthesis["disagreements"].append({
                    "agent": turn.agent_id,
                    "content": turn.content[:200]
                })
        
        # If synthesizer agent provided, get its synthesis
        if synthesizer:
            context = AgentContext(
                user_id="system",
                trigger_reason="Synthesize dialogue",
                metadata={
                    "dialogue_topic": session.topic,
                    "turn_count": len(session.turns),
                    "all_turns": [t.to_dict() for t in session.turns]
                }
            )
            
            fragments = await synthesizer.reflect(context)
            
            for fragment in fragments:
                if fragment.fragment_type == "insight":
                    synthesis["insights"].append({
                        "agent": "synthesizer",
                        "content": fragment.content
                    })
        
        return synthesis
    
    async def end_dialogue(self, session_id: str) -> Dict[str, Any]:
        """End a dialogue session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        # Get final summary
        summary = session.get_summary()
        
        # Store dialogue history
        await self._store_dialogue(session)
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        if session_id in self.session_history:
            self.session_history.remove(session_id)
        
        logger.info(f"Ended dialogue session {session_id}")
        
        return summary
    
    async def _store_dialogue(self, session: DialogueSession):
        """Store dialogue session for later retrieval"""
        try:
            dialogue_data = {
                "session_id": session.session_id,
                "topic": session.topic,
                "participants": [p.agent_id for p in session.participants],
                "turns": [t.to_dict() for t in session.turns],
                "summary": session.get_summary(),
                "created_at": session.created_at.isoformat()
            }
            
            # Store in Redis with TTL
            key = f"dialogue_history:{session.session_id}"
            await redis_manager.cache_set(
                key,
                dialogue_data,
                ttl=86400 * 7  # 7 days
            )
            
        except Exception as e:
            logger.error(f"Failed to store dialogue {session.session_id}: {e}")
    
    async def get_dialogue_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get dialogue history for a user"""
        # This would be implemented with proper Redis scanning
        # For now, return empty list
        return []
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get information about active sessions"""
        return [
            session.get_summary()
            for session in self.active_sessions.values()
        ]


# Global dialogue manager instance
dialogue_manager = DialogueManager()


# Export
__all__ = [
    'DialogueTurn',
    'DialogueSession',
    'DialogueManager',
    'dialogue_manager',
]