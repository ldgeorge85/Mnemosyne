"""
Async workers for memory processing in Mnemosyne Protocol
Background task processing with Redis queue
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import traceback
import signal

from backend.core.redis_client import redis_manager
from backend.core.events import event_bus, EventType, Event
from backend.core.config import get_settings
from backend.services.memory_service import MemoryService
from backend.services.search_service import vector_search_service
from backend.pipelines.consolidation import MemoryConsolidationPipeline, REMConsolidationScheduler
from backend.pipelines.reflection import ReflectionPipeline, ReflectionLayerManager

logger = logging.getLogger(__name__)
settings = get_settings()


class BaseWorker:
    """Base class for async workers"""
    
    def __init__(self, name: str):
        self.name = name
        self._logger = logging.getLogger(f"{__name__}.{name}")
        self._running = False
        self._tasks: List[asyncio.Task] = []
    
    async def start(self) -> None:
        """Start the worker"""
        if self._running:
            self._logger.warning(f"Worker {self.name} already running")
            return
        
        self._running = True
        self._logger.info(f"Worker {self.name} started")
        
        # Start processing
        task = asyncio.create_task(self.run())
        self._tasks.append(task)
    
    async def stop(self) -> None:
        """Stop the worker"""
        if not self._running:
            return
        
        self._running = False
        
        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        
        self._tasks.clear()
        self._logger.info(f"Worker {self.name} stopped")
    
    async def run(self) -> None:
        """Main worker loop - override in subclasses"""
        raise NotImplementedError
    
    async def process_task(self, task_data: Dict[str, Any]) -> None:
        """Process a single task - override in subclasses"""
        raise NotImplementedError


class MemoryProcessingWorker(BaseWorker):
    """Worker for processing memory operations"""
    
    def __init__(self):
        super().__init__("memory_processor")
        self.memory_service = MemoryService()
        self.queue_name = "memory_processing"
        self.batch_size = 5
    
    async def run(self) -> None:
        """Process memory tasks from queue"""
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
                    await asyncio.sleep(1)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Error in memory processing worker: {e}")
                await asyncio.sleep(5)
    
    async def process_task(self, task_data: Dict[str, Any]) -> None:
        """Process a memory task"""
        try:
            task_type = task_data.get('data', {}).get('type')
            
            if task_type == 'create_memory':
                await self._create_memory(task_data['data'])
            elif task_type == 'update_memory':
                await self._update_memory(task_data['data'])
            elif task_type == 'delete_memory':
                await self._delete_memory(task_data['data'])
            else:
                self._logger.warning(f"Unknown task type: {task_type}")
                
        except Exception as e:
            self._logger.error(f"Failed to process task: {e}\n{traceback.format_exc()}")
    
    async def _create_memory(self, data: Dict[str, Any]) -> None:
        """Create a new memory"""
        memory = await self.memory_service.create_memory(
            user_id=data['user_id'],
            content=data['content'],
            **data.get('kwargs', {})
        )
        
        # Emit event
        await event_bus.publish(Event(
            event_type=EventType.MEMORY_CREATED,
            user_id=data['user_id'],
            data={'memory_id': str(memory.id)}
        ))
    
    async def _update_memory(self, data: Dict[str, Any]) -> None:
        """Update a memory"""
        memory = await self.memory_service.update_memory(
            memory_id=data['memory_id'],
            user_id=data['user_id'],
            **data.get('updates', {})
        )
        
        if memory:
            # Emit event
            await event_bus.publish(Event(
                event_type=EventType.MEMORY_UPDATED,
                user_id=data['user_id'],
                data={'memory_id': str(memory.id)}
            ))
    
    async def _delete_memory(self, data: Dict[str, Any]) -> None:
        """Delete a memory"""
        success = await self.memory_service.delete_memory(
            memory_id=data['memory_id'],
            user_id=data['user_id'],
            soft_delete=data.get('soft_delete', True)
        )
        
        if success:
            # Emit event
            await event_bus.publish(Event(
                event_type=EventType.MEMORY_DELETED,
                user_id=data['user_id'],
                data={'memory_id': data['memory_id']}
            ))


class ReflectionWorker(BaseWorker):
    """Worker for processing reflections"""
    
    def __init__(self):
        super().__init__("reflection_processor")
        self.reflection_pipeline = ReflectionPipeline()
        self.reflection_manager = ReflectionLayerManager(self.reflection_pipeline)
        self.memory_service = MemoryService()
    
    async def run(self) -> None:
        """Process reflection events"""
        # Subscribe to reflection events
        event_bus.register_handler(
            EventType.REFLECTION_TRIGGERED,
            self
        )
        
        # Also process reevaluations
        reevaluation_task = asyncio.create_task(
            self.reflection_manager.process_reevaluations()
        )
        self._tasks.append(reevaluation_task)
        
        # Keep running
        while self._running:
            await asyncio.sleep(1)
    
    async def can_handle(self, event: Event) -> bool:
        """Check if we can handle this event"""
        return event.event_type == EventType.REFLECTION_TRIGGERED
    
    async def handle(self, event: Event) -> None:
        """Handle reflection event"""
        try:
            memory_id = event.data.get('memory_id')
            user_id = event.user_id
            
            # Get the memory
            memory = await self.memory_service.get_memory(memory_id, user_id)
            
            if memory:
                # Trigger reflection
                journal = await self.reflection_manager.trigger_reflection(memory)
                
                # Emit completion event
                await event_bus.publish(Event(
                    event_type=EventType.REFLECTION_COMPLETED,
                    user_id=user_id,
                    data={
                        'memory_id': memory_id,
                        'fragment_count': len(journal.fragments),
                        'overall_drift': journal.overall_drift,
                        'signal_modulation': journal.signal_modulation,
                        'consolidation_eligible': journal.consolidation_eligible
                    }
                ))
                
                self._logger.info(
                    f"Reflection completed for memory {memory_id}: "
                    f"{len(journal.fragments)} fragments, drift={journal.overall_drift:.2f}"
                )
                
        except Exception as e:
            self._logger.error(f"Reflection failed: {e}\n{traceback.format_exc()}")
            
            # Emit failure event
            await event_bus.publish(Event(
                event_type=EventType.REFLECTION_FAILED,
                user_id=event.user_id,
                data={'memory_id': event.data.get('memory_id'), 'error': str(e)}
            ))
    
    async def on_error(self, event: Event, error: Exception) -> None:
        """Handle errors"""
        self._logger.error(f"Reflection error for event {event.id}: {error}")


class ConsolidationWorker(BaseWorker):
    """Worker for memory consolidation"""
    
    def __init__(self):
        super().__init__("consolidation_processor")
        self.memory_service = MemoryService()
        self.consolidation_pipeline = MemoryConsolidationPipeline(
            memory_service=self.memory_service
        )
        self.scheduler = REMConsolidationScheduler(self.consolidation_pipeline)
        self.cycle_hours = settings.memory_consolidation_interval_hours
    
    async def run(self) -> None:
        """Run periodic consolidation cycles"""
        while self._running:
            try:
                # Get all active users (simplified - in production would batch)
                # For now, just run consolidation periodically
                await self._run_consolidation_cycle()
                
                # Wait for next cycle
                await asyncio.sleep(self.cycle_hours * 3600)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Consolidation cycle error: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    async def _run_consolidation_cycle(self) -> None:
        """Run a consolidation cycle"""
        self._logger.info("Starting consolidation cycle")
        
        # In production, would get active users from database
        # For now, this is a placeholder
        
        # Example: consolidate for a specific user
        # user_id = "example_user_id"
        # consolidated = await self.consolidation_pipeline.consolidate_user_memories(
        #     user_id=user_id,
        #     min_age_hours=self.cycle_hours
        # )
        
        # if consolidated:
        #     # Mark original memories as consolidated
        #     memory_ids = []
        #     for cons_memory in consolidated:
        #         memory_ids.extend(cons_memory.parent_memory_ids)
        #     
        #     await self.memory_service.mark_memories_consolidated(
        #         memory_ids=memory_ids,
        #         consolidation_group_id=f"consolidation_{datetime.utcnow().timestamp()}"
        #     )
        #     
        #     # Emit event
        #     await event_bus.publish(Event(
        #         event_type=EventType.MEMORY_CONSOLIDATED,
        #         user_id=user_id,
        #         data={
        #             'memory_ids': memory_ids,
        #             'consolidated_count': len(consolidated)
        #         }
        #     ))
        
        self._logger.info("Consolidation cycle completed")


class WorkerManager:
    """Manages all workers"""
    
    def __init__(self):
        self.workers: Dict[str, BaseWorker] = {}
        self._running = False
    
    def register_worker(self, worker: BaseWorker) -> None:
        """Register a worker"""
        self.workers[worker.name] = worker
        logger.info(f"Registered worker: {worker.name}")
    
    async def start_all(self) -> None:
        """Start all workers"""
        if self._running:
            logger.warning("Workers already running")
            return
        
        self._running = True
        
        # Start all workers
        for worker in self.workers.values():
            await worker.start()
        
        logger.info(f"Started {len(self.workers)} workers")
    
    async def stop_all(self) -> None:
        """Stop all workers"""
        if not self._running:
            return
        
        self._running = False
        
        # Stop all workers
        for worker in self.workers.values():
            await worker.stop()
        
        logger.info("All workers stopped")
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all workers"""
        health = {}
        for name, worker in self.workers.items():
            health[name] = worker._running
        return health


# Global worker manager
worker_manager = WorkerManager()

# Register default workers
worker_manager.register_worker(MemoryProcessingWorker())
worker_manager.register_worker(ReflectionWorker())
worker_manager.register_worker(ConsolidationWorker())


# Signal handlers for graceful shutdown
def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, initiating shutdown...")
    asyncio.create_task(shutdown_workers())


async def shutdown_workers():
    """Graceful shutdown of workers"""
    await worker_manager.stop_all()
    await event_bus.stop()


# Main worker entry point
async def run_workers():
    """Main entry point for running workers"""
    try:
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Initialize event system
        await event_bus.start()
        
        # Start all workers
        await worker_manager.start_all()
        
        # Keep running
        while True:
            # Health check
            health = await worker_manager.health_check()
            healthy_count = sum(1 for h in health.values() if h)
            logger.info(f"Worker health: {healthy_count}/{len(health)} healthy")
            
            # Check every 60 seconds
            await asyncio.sleep(60)
            
    except asyncio.CancelledError:
        logger.info("Worker process cancelled")
    except Exception as e:
        logger.error(f"Worker process error: {e}\n{traceback.format_exc()}")
    finally:
        await shutdown_workers()


# CLI entry point
if __name__ == "__main__":
    import sys
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run workers
    try:
        asyncio.run(run_workers())
    except KeyboardInterrupt:
        logger.info("Worker process interrupted")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Worker process failed: {e}")
        sys.exit(1)


# Export classes and functions
__all__ = [
    'BaseWorker',
    'MemoryProcessingWorker',
    'ReflectionWorker',
    'ConsolidationWorker',
    'WorkerManager',
    'worker_manager',
    'run_workers',
    'shutdown_workers',
]