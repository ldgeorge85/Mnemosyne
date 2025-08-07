"""
Redis client and streams setup for Mnemosyne
Event-driven architecture with Redis Streams
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timedelta
import uuid

import redis.asyncio as redis
from redis.asyncio.client import Redis, PubSub
from redis.exceptions import RedisError, ConnectionError as RedisConnectionError

from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RedisManager:
    """Manages Redis connections and operations"""
    
    def __init__(self):
        self.client: Optional[Redis] = None
        self.pubsub: Optional[PubSub] = None
        self._initialized = False
        self._stream_handlers: Dict[str, List[Callable]] = {}
        self._consumer_tasks: List[asyncio.Task] = []
        
        # Stream configuration
        self.streams = {
            "events:memory": "Memory processing events",
            "events:reflection": "Agent reflection events",
            "events:signal": "Deep Signal events",
            "events:ritual": "Ritual and ceremony events",
            "events:collective": "Collective sharing events",
            "events:system": "System-wide events"
        }
        
        # Consumer groups
        self.consumer_groups = {
            "events:memory": "memory-processors",
            "events:reflection": "reflection-processors",
            "events:signal": "signal-processors",
            "events:ritual": "ritual-processors",
            "events:collective": "collective-processors",
            "events:system": "system-processors"
        }
    
    async def initialize(self) -> None:
        """Initialize Redis client and streams"""
        if self._initialized:
            return
        
        try:
            # Create Redis client
            self.client = await redis.from_url(
                settings.redis_url,
                max_connections=settings.redis_max_connections,
                decode_responses=settings.redis_decode_responses,
                health_check_interval=30,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            await self.client.ping()
            
            # Create pubsub client
            self.pubsub = self.client.pubsub()
            
            # Create consumer groups
            await self._create_consumer_groups()
            
            self._initialized = True
            logger.info("Redis manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise
    
    async def _create_consumer_groups(self) -> None:
        """Create consumer groups for streams"""
        for stream_key, group_name in self.consumer_groups.items():
            try:
                # Try to create consumer group
                await self.client.xgroup_create(
                    stream_key,
                    group_name,
                    id="0",
                    mkstream=True
                )
                logger.info(f"Created consumer group {group_name} for stream {stream_key}")
            except redis.ResponseError as e:
                if "BUSYGROUP" in str(e):
                    logger.debug(f"Consumer group {group_name} already exists")
                else:
                    logger.error(f"Error creating consumer group: {e}")
    
    async def publish_event(
        self,
        stream_key: str,
        event_type: str,
        data: Dict[str, Any],
        max_len: int = 10000
    ) -> str:
        """Publish an event to a Redis stream"""
        try:
            # Prepare event data
            event_data = {
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": json.dumps(data)
            }
            
            # Add to stream with automatic trimming
            event_id = await self.client.xadd(
                stream_key,
                event_data,
                maxlen=max_len,
                approximate=True
            )
            
            logger.debug(f"Published event {event_type} to {stream_key}: {event_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            raise
    
    async def consume_stream(
        self,
        stream_key: str,
        handler: Callable,
        consumer_name: Optional[str] = None,
        batch_size: int = 10,
        block_ms: int = 1000
    ) -> None:
        """Consume events from a stream"""
        consumer_name = consumer_name or f"consumer-{uuid.uuid4().hex[:8]}"
        group_name = self.consumer_groups.get(stream_key)
        
        if not group_name:
            logger.error(f"No consumer group defined for stream {stream_key}")
            return
        
        logger.info(f"Starting consumer {consumer_name} for stream {stream_key}")
        
        while True:
            try:
                # Read from stream
                messages = await self.client.xreadgroup(
                    group_name,
                    consumer_name,
                    {stream_key: ">"},
                    count=batch_size,
                    block=block_ms
                )
                
                if not messages:
                    continue
                
                # Process messages
                for stream, stream_messages in messages:
                    for message_id, data in stream_messages:
                        try:
                            # Parse event data
                            event_type = data.get("event_type")
                            event_data = json.loads(data.get("data", "{}"))
                            timestamp = data.get("timestamp")
                            
                            # Call handler
                            await handler({
                                "id": message_id,
                                "type": event_type,
                                "data": event_data,
                                "timestamp": timestamp,
                                "stream": stream_key
                            })
                            
                            # Acknowledge message
                            await self.client.xack(stream_key, group_name, message_id)
                            
                        except Exception as e:
                            logger.error(f"Error processing message {message_id}: {e}")
                            # Message will be redelivered
                
            except asyncio.CancelledError:
                logger.info(f"Consumer {consumer_name} cancelled")
                break
            except Exception as e:
                logger.error(f"Error in consumer {consumer_name}: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    def register_stream_handler(self, stream_key: str, handler: Callable) -> None:
        """Register a handler for stream events"""
        if stream_key not in self._stream_handlers:
            self._stream_handlers[stream_key] = []
        self._stream_handlers[stream_key].append(handler)
    
    async def start_consumers(self) -> None:
        """Start all registered stream consumers"""
        for stream_key, handlers in self._stream_handlers.items():
            for handler in handlers:
                task = asyncio.create_task(
                    self.consume_stream(stream_key, handler)
                )
                self._consumer_tasks.append(task)
        
        logger.info(f"Started {len(self._consumer_tasks)} stream consumers")
    
    async def stop_consumers(self) -> None:
        """Stop all stream consumers"""
        for task in self._consumer_tasks:
            task.cancel()
        
        if self._consumer_tasks:
            await asyncio.gather(*self._consumer_tasks, return_exceptions=True)
            self._consumer_tasks.clear()
        
        logger.info("Stopped all stream consumers")
    
    # Cache operations
    async def cache_set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        namespace: str = "cache"
    ) -> bool:
        """Set a value in cache"""
        try:
            cache_key = f"{namespace}:{key}"
            
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            if ttl:
                return await self.client.setex(cache_key, ttl, value)
            else:
                return await self.client.set(cache_key, value)
                
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    async def cache_get(
        self,
        key: str,
        namespace: str = "cache",
        parse_json: bool = True
    ) -> Optional[Any]:
        """Get a value from cache"""
        try:
            cache_key = f"{namespace}:{key}"
            value = await self.client.get(cache_key)
            
            if value and parse_json:
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass
            
            return value
            
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    async def cache_delete(self, key: str, namespace: str = "cache") -> bool:
        """Delete a cache key"""
        try:
            cache_key = f"{namespace}:{key}"
            result = await self.client.delete(cache_key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    # Queue operations
    async def queue_push(
        self,
        queue_name: str,
        data: Dict[str, Any],
        priority: int = 0
    ) -> int:
        """Push item to queue"""
        try:
            queue_key = f"queue:{queue_name}"
            item = {
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "priority": priority
            }
            
            if priority > 0:
                # Use sorted set for priority queue
                return await self.client.zadd(
                    f"{queue_key}:priority",
                    {json.dumps(item): priority}
                )
            else:
                # Use list for FIFO queue
                return await self.client.lpush(queue_key, json.dumps(item))
                
        except Exception as e:
            logger.error(f"Error pushing to queue {queue_name}: {e}")
            raise
    
    async def queue_pop(
        self,
        queue_name: str,
        timeout: int = 0
    ) -> Optional[Dict[str, Any]]:
        """Pop item from queue"""
        try:
            queue_key = f"queue:{queue_name}"
            
            # Check priority queue first
            priority_key = f"{queue_key}:priority"
            item = await self.client.zpopmax(priority_key)
            
            if item:
                return json.loads(item[0][0])
            
            # Fall back to regular queue
            if timeout > 0:
                result = await self.client.brpop(queue_key, timeout)
                if result:
                    return json.loads(result[1])
            else:
                result = await self.client.rpop(queue_key)
                if result:
                    return json.loads(result)
            
            return None
            
        except Exception as e:
            logger.error(f"Error popping from queue {queue_name}: {e}")
            return None
    
    # Rate limiting
    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int
    ) -> bool:
        """Check if rate limit is exceeded"""
        try:
            rate_key = f"rate:{key}"
            current = await self.client.incr(rate_key)
            
            if current == 1:
                await self.client.expire(rate_key, window_seconds)
            
            return current <= limit
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return True  # Allow on error
    
    # Distributed locking
    async def acquire_lock(
        self,
        lock_name: str,
        timeout: int = 10,
        blocking: bool = True,
        blocking_timeout: int = 5
    ) -> bool:
        """Acquire a distributed lock"""
        try:
            lock_key = f"lock:{lock_name}"
            lock_value = str(uuid.uuid4())
            
            if blocking:
                end_time = datetime.utcnow() + timedelta(seconds=blocking_timeout)
                while datetime.utcnow() < end_time:
                    if await self.client.set(
                        lock_key,
                        lock_value,
                        nx=True,
                        ex=timeout
                    ):
                        return True
                    await asyncio.sleep(0.1)
                return False
            else:
                return await self.client.set(
                    lock_key,
                    lock_value,
                    nx=True,
                    ex=timeout
                )
                
        except Exception as e:
            logger.error(f"Error acquiring lock {lock_name}: {e}")
            return False
    
    async def release_lock(self, lock_name: str) -> bool:
        """Release a distributed lock"""
        try:
            lock_key = f"lock:{lock_name}"
            return await self.client.delete(lock_key) > 0
            
        except Exception as e:
            logger.error(f"Error releasing lock {lock_name}: {e}")
            return False
    
    # Session management
    async def store_session(
        self,
        session_id: str,
        data: Dict[str, Any],
        ttl: int = 3600
    ) -> bool:
        """Store session data"""
        return await self.cache_set(
            f"session:{session_id}",
            data,
            ttl=ttl,
            namespace="sessions"
        )
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        return await self.cache_get(
            f"session:{session_id}",
            namespace="sessions"
        )
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session data"""
        return await self.cache_delete(
            f"session:{session_id}",
            namespace="sessions"
        )
    
    # Health check
    async def health_check(self) -> bool:
        """Check Redis health"""
        try:
            return await self.client.ping()
        except Exception:
            return False
    
    async def close(self) -> None:
        """Close Redis connections"""
        await self.stop_consumers()
        
        if self.pubsub:
            await self.pubsub.close()
        
        if self.client:
            await self.client.close()
        
        self._initialized = False
        logger.info("Redis connections closed")


# Global Redis manager instance
redis_manager = RedisManager()


# Event publishing shortcuts
async def publish_memory_event(event_type: str, data: Dict[str, Any]) -> str:
    """Publish a memory processing event"""
    return await redis_manager.publish_event("events:memory", event_type, data)


async def publish_reflection_event(event_type: str, data: Dict[str, Any]) -> str:
    """Publish an agent reflection event"""
    return await redis_manager.publish_event("events:reflection", event_type, data)


async def publish_signal_event(event_type: str, data: Dict[str, Any]) -> str:
    """Publish a Deep Signal event"""
    return await redis_manager.publish_event("events:signal", event_type, data)


async def publish_ritual_event(event_type: str, data: Dict[str, Any]) -> str:
    """Publish a ritual event"""
    return await redis_manager.publish_event("events:ritual", event_type, data)


async def publish_collective_event(event_type: str, data: Dict[str, Any]) -> str:
    """Publish a collective sharing event"""
    return await redis_manager.publish_event("events:collective", event_type, data)


async def publish_system_event(event_type: str, data: Dict[str, Any]) -> str:
    """Publish a system event"""
    return await redis_manager.publish_event("events:system", event_type, data)


# Initialization
async def init_redis() -> None:
    """Initialize Redis manager"""
    await redis_manager.initialize()


async def close_redis() -> None:
    """Close Redis connections"""
    await redis_manager.close()


# Export key items
__all__ = [
    "RedisManager",
    "redis_manager",
    "init_redis",
    "close_redis",
    "publish_memory_event",
    "publish_reflection_event",
    "publish_signal_event",
    "publish_ritual_event",
    "publish_collective_event",
    "publish_system_event",
]