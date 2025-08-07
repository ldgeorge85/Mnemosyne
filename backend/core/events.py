"""
Event system for Mnemosyne Protocol
Event-driven architecture with Redis Streams
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Callable, Coroutine
from datetime import datetime
from enum import Enum
import traceback

from .redis_client import redis_manager
from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EventType(str, Enum):
    """System event types"""
    # Memory events
    MEMORY_CREATED = "memory.created"
    MEMORY_UPDATED = "memory.updated"
    MEMORY_DELETED = "memory.deleted"
    MEMORY_ACCESSED = "memory.accessed"
    MEMORY_CONSOLIDATED = "memory.consolidated"
    
    # Reflection events
    REFLECTION_TRIGGERED = "reflection.triggered"
    REFLECTION_COMPLETED = "reflection.completed"
    REFLECTION_FAILED = "reflection.failed"
    
    # Signal events
    SIGNAL_EMITTED = "signal.emitted"
    SIGNAL_UPDATED = "signal.updated"
    SIGNAL_DECAY = "signal.decay"
    SIGNAL_RESONANCE = "signal.resonance"
    
    # Agent events
    AGENT_STARTED = "agent.started"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"
    
    # Ritual events
    RITUAL_INITIATED = "ritual.initiated"
    RITUAL_PROGRESSED = "ritual.progressed"
    RITUAL_COMPLETED = "ritual.completed"
    
    # Collective events
    COLLECTIVE_JOINED = "collective.joined"
    COLLECTIVE_SHARED = "collective.shared"
    COLLECTIVE_MATCHED = "collective.matched"
    
    # System events
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"
    SYSTEM_INFO = "system.info"


class Event:
    """Base event class"""
    
    def __init__(
        self,
        event_type: EventType,
        user_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = f"event_{datetime.utcnow().timestamp()}"
        self.event_type = event_type
        self.user_id = user_id
        self.data = data or {}
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'id': self.id,
            'event_type': self.event_type.value,
            'user_id': self.user_id,
            'data': self.data,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """Create event from dictionary"""
        event = cls(
            event_type=EventType(data['event_type']),
            user_id=data.get('user_id'),
            data=data.get('data', {}),
            metadata=data.get('metadata', {})
        )
        event.id = data.get('id')
        if data.get('timestamp'):
            event.timestamp = datetime.fromisoformat(data['timestamp'])
        return event


class EventHandler:
    """Base class for event handlers"""
    
    def __init__(self, name: str):
        self.name = name
        self._logger = logging.getLogger(f"{__name__}.{name}")
    
    async def can_handle(self, event: Event) -> bool:
        """Check if handler can process this event"""
        return True
    
    async def handle(self, event: Event) -> None:
        """Handle the event"""
        raise NotImplementedError
    
    async def on_error(self, event: Event, error: Exception) -> None:
        """Handle errors during event processing"""
        self._logger.error(f"Error handling event {event.id}: {error}")


class EventBus:
    """Central event bus for publishing and subscribing"""
    
    def __init__(self):
        self.handlers: Dict[EventType, List[EventHandler]] = {}
        self.global_handlers: List[EventHandler] = []
        self.consumer_tasks: List[asyncio.Task] = []
        self._running = False
    
    def register_handler(
        self,
        event_type: EventType,
        handler: EventHandler
    ) -> None:
        """Register a handler for specific event type"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
        logger.info(f"Registered handler {handler.name} for {event_type.value}")
    
    def register_global_handler(self, handler: EventHandler) -> None:
        """Register a handler for all events"""
        self.global_handlers.append(handler)
        logger.info(f"Registered global handler {handler.name}")
    
    async def publish(self, event: Event) -> str:
        """Publish an event"""
        try:
            # Determine stream based on event type
            stream_key = self._get_stream_key(event.event_type)
            
            # Publish to Redis stream
            event_id = await redis_manager.publish_event(
                stream_key=stream_key,
                event_type=event.event_type.value,
                data=event.to_dict()
            )
            
            logger.debug(f"Published event {event.event_type.value}: {event_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            raise
    
    async def _process_event(self, event_data: Dict[str, Any]) -> None:
        """Process a single event"""
        try:
            # Parse event
            raw_data = json.loads(event_data.get('data', '{}'))
            event = Event.from_dict(raw_data)
            
            # Get handlers for this event type
            handlers = self.handlers.get(event.event_type, [])
            all_handlers = handlers + self.global_handlers
            
            # Process with each handler
            for handler in all_handlers:
                try:
                    if await handler.can_handle(event):
                        await handler.handle(event)
                except Exception as e:
                    logger.error(f"Handler {handler.name} failed: {e}")
                    await handler.on_error(event, e)
            
        except Exception as e:
            logger.error(f"Failed to process event: {e}\n{traceback.format_exc()}")
    
    def _get_stream_key(self, event_type: EventType) -> str:
        """Get Redis stream key for event type"""
        # Map event types to streams
        if event_type.value.startswith("memory."):
            return "events:memory"
        elif event_type.value.startswith("reflection."):
            return "events:reflection"
        elif event_type.value.startswith("signal."):
            return "events:signal"
        elif event_type.value.startswith("agent."):
            return "events:reflection"  # Agents use reflection stream
        elif event_type.value.startswith("ritual."):
            return "events:ritual"
        elif event_type.value.startswith("collective."):
            return "events:collective"
        else:
            return "events:system"
    
    async def start(self) -> None:
        """Start consuming events"""
        if self._running:
            logger.warning("Event bus already running")
            return
        
        self._running = True
        
        # Register event processor with Redis manager
        for stream in ["events:memory", "events:reflection", "events:signal", 
                      "events:ritual", "events:collective", "events:system"]:
            redis_manager.register_stream_handler(stream, self._process_event)
        
        # Start consumers
        await redis_manager.start_consumers()
        
        logger.info("Event bus started")
    
    async def stop(self) -> None:
        """Stop consuming events"""
        if not self._running:
            return
        
        self._running = False
        
        # Stop Redis consumers
        await redis_manager.stop_consumers()
        
        logger.info("Event bus stopped")


# Specific event handlers

class MemoryEventHandler(EventHandler):
    """Handler for memory-related events"""
    
    def __init__(self):
        super().__init__("memory_events")
    
    async def can_handle(self, event: Event) -> bool:
        """Check if this is a memory event"""
        return event.event_type.value.startswith("memory.")
    
    async def handle(self, event: Event) -> None:
        """Handle memory events"""
        if event.event_type == EventType.MEMORY_CREATED:
            await self._handle_memory_created(event)
        elif event.event_type == EventType.MEMORY_CONSOLIDATED:
            await self._handle_memory_consolidated(event)
    
    async def _handle_memory_created(self, event: Event) -> None:
        """Handle memory creation"""
        memory_id = event.data.get('memory_id')
        user_id = event.user_id
        
        # Trigger reflection pipeline
        reflection_event = Event(
            event_type=EventType.REFLECTION_TRIGGERED,
            user_id=user_id,
            data={'memory_id': memory_id, 'trigger': 'new_memory'}
        )
        
        await event_bus.publish(reflection_event)
        
        self._logger.info(f"Triggered reflection for new memory {memory_id}")
    
    async def _handle_memory_consolidated(self, event: Event) -> None:
        """Handle memory consolidation"""
        memory_ids = event.data.get('memory_ids', [])
        self._logger.info(f"Memories consolidated: {len(memory_ids)} memories")


class ReflectionEventHandler(EventHandler):
    """Handler for reflection events"""
    
    def __init__(self):
        super().__init__("reflection_events")
    
    async def can_handle(self, event: Event) -> bool:
        """Check if this is a reflection event"""
        return event.event_type.value.startswith("reflection.")
    
    async def handle(self, event: Event) -> None:
        """Handle reflection events"""
        if event.event_type == EventType.REFLECTION_TRIGGERED:
            # This would trigger actual reflection processing
            memory_id = event.data.get('memory_id')
            self._logger.info(f"Processing reflection for memory {memory_id}")
        elif event.event_type == EventType.REFLECTION_COMPLETED:
            # Update signal based on reflection
            await self._update_signal_from_reflection(event)
    
    async def _update_signal_from_reflection(self, event: Event) -> None:
        """Update user's signal based on reflection"""
        user_id = event.user_id
        modulation = event.data.get('signal_modulation', 0)
        
        if abs(modulation) > 0.1:
            # Significant modulation - update signal
            signal_event = Event(
                event_type=EventType.SIGNAL_UPDATED,
                user_id=user_id,
                data={'modulation': modulation, 'source': 'reflection'}
            )
            
            await event_bus.publish(signal_event)


class SystemEventHandler(EventHandler):
    """Handler for system events"""
    
    def __init__(self):
        super().__init__("system_events")
    
    async def can_handle(self, event: Event) -> bool:
        """Handle all system events"""
        return event.event_type.value.startswith("system.")
    
    async def handle(self, event: Event) -> None:
        """Log system events"""
        if event.event_type == EventType.SYSTEM_ERROR:
            self._logger.error(f"System error: {event.data}")
        elif event.event_type == EventType.SYSTEM_WARNING:
            self._logger.warning(f"System warning: {event.data}")
        else:
            self._logger.info(f"System info: {event.data}")


# Event publishing shortcuts

async def emit_memory_event(
    event_type: EventType,
    user_id: str,
    data: Dict[str, Any]
) -> str:
    """Emit a memory-related event"""
    event = Event(event_type, user_id, data)
    return await event_bus.publish(event)


async def emit_reflection_event(
    event_type: EventType,
    user_id: str,
    data: Dict[str, Any]
) -> str:
    """Emit a reflection-related event"""
    event = Event(event_type, user_id, data)
    return await event_bus.publish(event)


async def emit_signal_event(
    event_type: EventType,
    user_id: str,
    data: Dict[str, Any]
) -> str:
    """Emit a signal-related event"""
    event = Event(event_type, user_id, data)
    return await event_bus.publish(event)


async def emit_system_event(
    level: str,
    message: str,
    data: Optional[Dict[str, Any]] = None
) -> str:
    """Emit a system event"""
    event_type_map = {
        'error': EventType.SYSTEM_ERROR,
        'warning': EventType.SYSTEM_WARNING,
        'info': EventType.SYSTEM_INFO
    }
    
    event = Event(
        event_type=event_type_map.get(level, EventType.SYSTEM_INFO),
        data={'message': message, **(data or {})}
    )
    
    return await event_bus.publish(event)


# Global event bus instance
event_bus = EventBus()

# Register default handlers
event_bus.register_handler(EventType.MEMORY_CREATED, MemoryEventHandler())
event_bus.register_handler(EventType.MEMORY_CONSOLIDATED, MemoryEventHandler())
event_bus.register_handler(EventType.REFLECTION_TRIGGERED, ReflectionEventHandler())
event_bus.register_handler(EventType.REFLECTION_COMPLETED, ReflectionEventHandler())
event_bus.register_global_handler(SystemEventHandler())


# Initialization
async def init_event_system():
    """Initialize the event system"""
    await event_bus.start()
    logger.info("Event system initialized")


async def shutdown_event_system():
    """Shutdown the event system"""
    await event_bus.stop()
    logger.info("Event system shutdown")


# Export classes and functions
__all__ = [
    'EventType',
    'Event',
    'EventHandler',
    'EventBus',
    'MemoryEventHandler',
    'ReflectionEventHandler',
    'SystemEventHandler',
    'event_bus',
    'emit_memory_event',
    'emit_reflection_event',
    'emit_signal_event',
    'emit_system_event',
    'init_event_system',
    'shutdown_event_system',
]