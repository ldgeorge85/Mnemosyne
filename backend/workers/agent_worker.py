"""
Agent worker for Mnemosyne Protocol
Processes agent tasks asynchronously
"""

import logging
import asyncio
import traceback
from typing import Dict, Any, List
from datetime import datetime

from core.redis_client import redis_manager
from core.events import event_bus, EventType, Event
from services.agent_service import agent_service
from .memory_worker import BaseWorker

logger = logging.getLogger(__name__)


class AgentTaskWorker(BaseWorker):
    """Worker for processing agent tasks"""
    
    def __init__(self):
        super().__init__("agent_task_processor")
        self.queue_name = "agent_tasks"
        self.batch_size = 3
    
    async def run(self) -> None:
        """Process agent tasks from queue"""
        while self._running:
            try:
                # Get tasks from queue
                tasks = []
                for _ in range(self.batch_size):
                    task = await redis_manager.queue_pop(
                        self.queue_name,
                        timeout=1
                    )
                    if task:
                        tasks.append(task)
                    else:
                        break
                
                if tasks:
                    # Process tasks concurrently
                    await asyncio.gather(
                        *[self.process_task(task) for task in tasks],
                        return_exceptions=True
                    )
                else:
                    # No tasks, wait a bit
                    await asyncio.sleep(2)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Error in agent task worker: {e}")
                await asyncio.sleep(5)
    
    async def process_task(self, task_data: Dict[str, Any]) -> None:
        """Process an agent task"""
        try:
            task_type = task_data.get('type')
            data = task_data.get('data', {})
            
            if task_type == 'reflection':
                await self._process_reflection(data)
            elif task_type == 'dialogue':
                await self._process_dialogue(data)
            elif task_type == 'analysis':
                await self._process_analysis(data)
            else:
                self._logger.warning(f"Unknown task type: {task_type}")
                
        except Exception as e:
            self._logger.error(f"Failed to process agent task: {e}\n{traceback.format_exc()}")
    
    async def _process_reflection(self, data: Dict[str, Any]) -> None:
        """Process reflection task"""
        memory_id = data.get('memory_id')
        user_id = data.get('user_id')
        agent_roles = data.get('agent_roles')
        
        if not memory_id or not user_id:
            self._logger.error("Missing required data for reflection")
            return
        
        # Trigger reflection
        result = await agent_service.trigger_reflection(
            memory_id=memory_id,
            user_id=user_id,
            agent_roles=agent_roles,
            trigger_reason=data.get('trigger_reason', 'queued')
        )
        
        if result['success']:
            # Emit completion event
            await event_bus.publish(Event(
                event_type=EventType.AGENT_COMPLETED,
                user_id=user_id,
                data={
                    'task_type': 'reflection',
                    'memory_id': memory_id,
                    'insights': result.get('insights', [])
                }
            ))
        else:
            # Emit failure event
            await event_bus.publish(Event(
                event_type=EventType.AGENT_FAILED,
                user_id=user_id,
                data={
                    'task_type': 'reflection',
                    'memory_id': memory_id,
                    'error': result.get('error')
                }
            ))
    
    async def _process_dialogue(self, data: Dict[str, Any]) -> None:
        """Process dialogue task"""
        topic = data.get('topic')
        user_id = data.get('user_id')
        agent_roles = data.get('agent_roles', ['philosopher', 'mystic'])
        
        if not topic or not user_id:
            self._logger.error("Missing required data for dialogue")
            return
        
        # Trigger dialogue
        result = await agent_service.trigger_dialogue(
            topic=topic,
            user_id=user_id,
            agent_roles=agent_roles,
            max_rounds=data.get('max_rounds', 5)
        )
        
        if result['success']:
            # Store dialogue result
            dialogue_key = f"dialogue:{user_id}:{datetime.utcnow().timestamp()}"
            await redis_manager.cache_set(
                dialogue_key,
                result['dialogue'],
                ttl=86400  # 24 hours
            )
            
            # Emit completion event
            await event_bus.publish(Event(
                event_type=EventType.AGENT_COMPLETED,
                user_id=user_id,
                data={
                    'task_type': 'dialogue',
                    'topic': topic,
                    'dialogue_key': dialogue_key,
                    'rounds': result.get('rounds', 0)
                }
            ))
    
    async def _process_analysis(self, data: Dict[str, Any]) -> None:
        """Process analysis task"""
        memory_id = data.get('memory_id')
        user_id = data.get('user_id')
        analysis_type = data.get('analysis_type', 'comprehensive')
        
        if not memory_id or not user_id:
            self._logger.error("Missing required data for analysis")
            return
        
        # Perform analysis
        result = await agent_service.analyze_memory_with_agents(
            memory_id=memory_id,
            user_id=user_id,
            analysis_type=analysis_type
        )
        
        if result['success']:
            # Store analysis result
            analysis_key = f"analysis:{memory_id}:{analysis_type}"
            await redis_manager.cache_set(
                analysis_key,
                result,
                ttl=3600  # 1 hour
            )
            
            # Emit completion event
            await event_bus.publish(Event(
                event_type=EventType.AGENT_COMPLETED,
                user_id=user_id,
                data={
                    'task_type': 'analysis',
                    'memory_id': memory_id,
                    'analysis_type': analysis_type,
                    'analysis_key': analysis_key
                }
            ))


class AgentEventWorker(BaseWorker):
    """Worker that responds to events with agent actions"""
    
    def __init__(self):
        super().__init__("agent_event_processor")
        self.event_handlers = {
            EventType.MEMORY_CREATED: self._handle_memory_created,
            EventType.REFLECTION_TRIGGERED: self._handle_reflection_triggered,
            EventType.SIGNAL_UPDATED: self._handle_signal_updated
        }
    
    async def run(self) -> None:
        """Process events and trigger agent actions"""
        # Register event handlers
        for event_type, handler in self.event_handlers.items():
            event_bus.register_handler(event_type, self)
        
        # Keep running
        while self._running:
            await asyncio.sleep(1)
    
    async def can_handle(self, event: Event) -> bool:
        """Check if we can handle this event"""
        return event.event_type in self.event_handlers
    
    async def handle(self, event: Event) -> None:
        """Handle an event"""
        handler = self.event_handlers.get(event.event_type)
        if handler:
            try:
                await handler(event)
            except Exception as e:
                self._logger.error(f"Error handling event {event.id}: {e}")
    
    async def on_error(self, event: Event, error: Exception) -> None:
        """Handle event processing errors"""
        self._logger.error(f"Agent event error for {event.id}: {error}")
    
    async def _handle_memory_created(self, event: Event) -> None:
        """Handle memory creation event"""
        memory_id = event.data.get('memory_id')
        user_id = event.user_id
        
        if memory_id and user_id:
            # Queue reflection task
            await redis_manager.queue_push("agent_tasks", {
                'type': 'reflection',
                'data': {
                    'memory_id': memory_id,
                    'user_id': user_id,
                    'trigger_reason': 'new_memory',
                    'agent_roles': ['engineer', 'philosopher']  # Default agents for new memories
                }
            })
    
    async def _handle_reflection_triggered(self, event: Event) -> None:
        """Handle reflection trigger event"""
        memory_id = event.data.get('memory_id')
        user_id = event.user_id
        
        if memory_id and user_id:
            # Queue comprehensive analysis
            await redis_manager.queue_push("agent_tasks", {
                'type': 'analysis',
                'data': {
                    'memory_id': memory_id,
                    'user_id': user_id,
                    'analysis_type': 'comprehensive'
                }
            })
    
    async def _handle_signal_updated(self, event: Event) -> None:
        """Handle signal update event"""
        user_id = event.user_id
        modulation = event.data.get('modulation', 0)
        
        # If significant modulation, trigger mystic analysis
        if abs(modulation) > 0.3:
            await redis_manager.queue_push("agent_tasks", {
                'type': 'dialogue',
                'data': {
                    'topic': f"Signal modulation detected: {modulation:.2f}",
                    'user_id': user_id,
                    'agent_roles': ['mystic', 'philosopher'],
                    'max_rounds': 3
                }
            })


class AgentMaintenanceWorker(BaseWorker):
    """Worker for agent maintenance tasks"""
    
    def __init__(self):
        super().__init__("agent_maintenance")
        self.maintenance_interval = 3600  # 1 hour
    
    async def run(self) -> None:
        """Run maintenance tasks"""
        while self._running:
            try:
                # Perform maintenance
                await self._perform_maintenance()
                
                # Wait for next cycle
                await asyncio.sleep(self.maintenance_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Maintenance error: {e}")
                await asyncio.sleep(600)  # Retry in 10 minutes
    
    async def _perform_maintenance(self) -> None:
        """Perform agent maintenance tasks"""
        self._logger.info("Starting agent maintenance")
        
        # Get agent status
        status = await agent_service.get_agent_status()
        
        # Log status
        self._logger.info(f"Agent status: {status.get('agent_count', 0)} agents active")
        
        # Clean up old dialogue and analysis results
        # This would be implemented with proper Redis key scanning
        
        self._logger.info("Agent maintenance completed")


# Export workers
__all__ = [
    'AgentTaskWorker',
    'AgentEventWorker',
    'AgentMaintenanceWorker',
]