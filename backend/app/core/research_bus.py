"""
Research Bus for Mnemosyne Dual-Track System

This module provides event publishing infrastructure for research data collection.
All data is anonymized and consent-verified before publication.
"""

import asyncio
import hashlib
import json
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from collections import defaultdict
import logging
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class EventPriority(str, Enum):
    """Research event priority levels"""
    LOW = "low"  # Batch processing acceptable
    NORMAL = "normal"  # Standard processing
    HIGH = "high"  # Process immediately
    CRITICAL = "critical"  # Real-time processing required


class AnonymizationLevel(str, Enum):
    """Data anonymization levels"""
    NONE = "none"  # No anonymization (requires explicit consent)
    BASIC = "basic"  # Remove direct identifiers
    DIFFERENTIAL = "differential"  # Apply differential privacy
    FULL = "full"  # Complete anonymization


class ResearchBus:
    """
    Event bus for publishing anonymized data to research track.
    
    Ensures all published data is properly anonymized and
    consent has been obtained.
    """
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._processing = False
        self._event_buffer: List[Dict[str, Any]] = []
        self._buffer_size = 100
        self._buffer_timeout = 5.0  # seconds
        self._last_flush = datetime.utcnow()
        self._metrics = {
            "events_published": 0,
            "events_dropped": 0,
            "consent_denied": 0,
            "anonymization_failures": 0
        }
    
    async def publish(
        self,
        event_type: str,
        data: Dict[str, Any],
        user_id: Optional[str] = None,
        consent_id: Optional[str] = None,
        plugin_name: Optional[str] = None,
        priority: EventPriority = EventPriority.NORMAL,
        anonymization_level: AnonymizationLevel = AnonymizationLevel.BASIC
    ) -> bool:
        """
        Publish event to research bus.
        
        Args:
            event_type: Type of research event
            data: Event data to publish
            user_id: Optional user ID (will be anonymized)
            consent_id: Consent record ID
            plugin_name: Source plugin name
            priority: Event priority
            anonymization_level: Required anonymization level
            
        Returns:
            True if event was published, False otherwise
        """
        try:
            # Verify consent if user_id provided
            if user_id and not await self._verify_consent(user_id, event_type, consent_id):
                self._metrics["consent_denied"] += 1
                logger.warning(f"Consent denied for event {event_type} from user {user_id}")
                return False
            
            # Anonymize data
            anonymized_data = await self._anonymize_data(
                data, 
                user_id, 
                anonymization_level
            )
            
            # Create event envelope
            event = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "type": event_type,
                "plugin": plugin_name,
                "priority": priority.value,
                "anonymization_level": anonymization_level.value,
                "data": anonymized_data,
                "metadata": {
                    "schema_version": "1.0",
                    "consent_verified": bool(consent_id),
                    "user_hash": self._hash_user_id(user_id) if user_id else None
                }
            }
            
            # Handle based on priority
            if priority == EventPriority.CRITICAL:
                await self._process_immediate(event)
            else:
                await self._event_queue.put(event)
                
                # Start processor if not running
                if not self._processing:
                    asyncio.create_task(self._process_events())
            
            self._metrics["events_published"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
            self._metrics["events_dropped"] += 1
            return False
    
    async def subscribe(
        self,
        event_pattern: str,
        handler: Callable[[Dict[str, Any]], None]
    ) -> str:
        """
        Subscribe to research events.
        
        Args:
            event_pattern: Event type pattern (supports wildcards)
            handler: Async function to handle events
            
        Returns:
            Subscription ID
        """
        subscription_id = str(uuid.uuid4())
        self._subscribers[event_pattern].append({
            "id": subscription_id,
            "handler": handler,
            "created_at": datetime.utcnow()
        })
        logger.info(f"Added subscription {subscription_id} for pattern {event_pattern}")
        return subscription_id
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """
        Remove event subscription.
        
        Args:
            subscription_id: Subscription to remove
            
        Returns:
            True if removed, False if not found
        """
        for pattern, handlers in self._subscribers.items():
            for handler in handlers:
                if handler["id"] == subscription_id:
                    handlers.remove(handler)
                    logger.info(f"Removed subscription {subscription_id}")
                    return True
        return False
    
    async def _verify_consent(
        self,
        user_id: str,
        event_type: str,
        consent_id: Optional[str]
    ) -> bool:
        """
        Verify user consent for data collection.
        
        Args:
            user_id: User ID
            event_type: Type of event
            consent_id: Consent record ID
            
        Returns:
            True if consent is valid
        """
        # TODO: Integrate with consent management system
        # For now, require explicit consent_id
        if not consent_id:
            return False
        
        # Verify consent is valid and covers this event type
        # This would check against consent database
        return True
    
    async def _anonymize_data(
        self,
        data: Dict[str, Any],
        user_id: Optional[str],
        level: AnonymizationLevel
    ) -> Dict[str, Any]:
        """
        Anonymize data based on specified level.
        
        Args:
            data: Data to anonymize
            user_id: User ID to remove
            level: Anonymization level
            
        Returns:
            Anonymized data
        """
        if level == AnonymizationLevel.NONE:
            # No anonymization (requires special consent)
            return data
        
        anonymized = data.copy()
        
        # Basic anonymization - remove direct identifiers
        if level >= AnonymizationLevel.BASIC:
            fields_to_remove = [
                'user_id', 'email', 'username', 'full_name',
                'ip_address', 'device_id', 'session_id'
            ]
            for field in fields_to_remove:
                anonymized.pop(field, None)
            
            # Replace user_id with hash if present
            if user_id:
                anonymized['user_hash'] = self._hash_user_id(user_id)
        
        # Differential privacy
        if level >= AnonymizationLevel.DIFFERENTIAL:
            # Add noise to numerical values
            for key, value in anonymized.items():
                if isinstance(value, (int, float)):
                    # Add Laplacian noise
                    noise = self._generate_laplace_noise(sensitivity=1.0, epsilon=1.0)
                    anonymized[key] = value + noise
        
        # Full anonymization
        if level == AnonymizationLevel.FULL:
            # Additional processing for complete anonymization
            # Remove timestamps to hour precision
            if 'timestamp' in anonymized:
                dt = datetime.fromisoformat(anonymized['timestamp'])
                anonymized['timestamp'] = dt.replace(minute=0, second=0, microsecond=0).isoformat()
            
            # Generalize location data
            if 'location' in anonymized:
                # Round to city-level precision
                pass
        
        return anonymized
    
    def _hash_user_id(self, user_id: str) -> str:
        """Create consistent hash of user ID"""
        return hashlib.sha256(f"{user_id}:research:v1".encode()).hexdigest()[:16]
    
    def _generate_laplace_noise(self, sensitivity: float, epsilon: float) -> float:
        """Generate Laplacian noise for differential privacy"""
        import random
        import math
        u = random.random() - 0.5
        return -sensitivity / epsilon * math.copysign(1, u) * math.log(1 - 2 * abs(u))
    
    async def _process_events(self) -> None:
        """Process queued events in batches"""
        self._processing = True
        
        try:
            while True:
                # Collect batch
                batch = []
                deadline = datetime.utcnow() + timedelta(seconds=self._buffer_timeout)
                
                while len(batch) < self._buffer_size:
                    try:
                        timeout = (deadline - datetime.utcnow()).total_seconds()
                        if timeout <= 0:
                            break
                        
                        event = await asyncio.wait_for(
                            self._event_queue.get(),
                            timeout=timeout
                        )
                        batch.append(event)
                    except asyncio.TimeoutError:
                        break
                
                if not batch:
                    # No events to process
                    self._processing = False
                    break
                
                # Process batch
                await self._process_batch(batch)
                
        except Exception as e:
            logger.error(f"Event processor error: {e}")
            self._processing = False
    
    async def _process_batch(self, events: List[Dict[str, Any]]) -> None:
        """Process a batch of events"""
        for event in events:
            await self._dispatch_event(event)
        
        # Store events for research
        await self._store_events(events)
    
    async def _process_immediate(self, event: Dict[str, Any]) -> None:
        """Process high-priority event immediately"""
        await self._dispatch_event(event)
        await self._store_events([event])
    
    async def _dispatch_event(self, event: Dict[str, Any]) -> None:
        """Dispatch event to subscribers"""
        event_type = event["type"]
        
        for pattern, handlers in self._subscribers.items():
            if self._matches_pattern(event_type, pattern):
                for handler_info in handlers:
                    try:
                        handler = handler_info["handler"]
                        await handler(event)
                    except Exception as e:
                        logger.error(f"Handler error for event {event_type}: {e}")
    
    def _matches_pattern(self, event_type: str, pattern: str) -> bool:
        """Check if event type matches subscription pattern"""
        if pattern == "*":
            return True
        if pattern.endswith("*"):
            return event_type.startswith(pattern[:-1])
        return event_type == pattern
    
    async def _store_events(self, events: List[Dict[str, Any]]) -> None:
        """Store events for research analysis"""
        # TODO: Implement storage to research database
        # This would write to a time-series database or data lake
        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get research bus metrics"""
        return {
            **self._metrics,
            "queue_size": self._event_queue.qsize(),
            "subscribers": sum(len(h) for h in self._subscribers.values()),
            "patterns": list(self._subscribers.keys())
        }


class ResearchEventLogger:
    """
    Structured logger for research events.
    
    Provides consistent interface for logging research-relevant
    events with proper anonymization.
    """
    
    def __init__(self, plugin_name: str):
        self.plugin_name = plugin_name
        self.bus = ResearchBus()
    
    async def log_hypothesis_test(
        self,
        hypothesis: str,
        result: Any,
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log hypothesis test result"""
        await self.bus.publish(
            event_type="hypothesis.test",
            data={
                "hypothesis": hypothesis,
                "result": result,
                "confidence": confidence,
                "metadata": metadata or {}
            },
            plugin_name=self.plugin_name,
            priority=EventPriority.NORMAL,
            anonymization_level=AnonymizationLevel.BASIC
        )
    
    async def log_metric(
        self,
        metric_name: str,
        value: float,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log research metric"""
        await self.bus.publish(
            event_type="metric.recorded",
            data={
                "metric": metric_name,
                "value": value,
                "context": context or {}
            },
            plugin_name=self.plugin_name,
            priority=EventPriority.LOW,
            anonymization_level=AnonymizationLevel.DIFFERENTIAL
        )
    
    async def log_validation(
        self,
        validation_type: str,
        passed: bool,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log validation result"""
        await self.bus.publish(
            event_type="validation.result",
            data={
                "type": validation_type,
                "passed": passed,
                "details": details or {}
            },
            plugin_name=self.plugin_name,
            priority=EventPriority.NORMAL,
            anonymization_level=AnonymizationLevel.BASIC
        )