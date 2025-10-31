"""
Background Scheduler Service

Handles periodic background jobs with distributed locking to ensure
single execution across multiple instances (e.g., Docker Swarm).
"""

import logging
import uuid
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis import asyncio as aioredis
from typing import Callable, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class SchedulerService:
    """Background job scheduler with distributed locking via Redis."""

    def __init__(self, redis_url: Optional[str] = None):
        """Initialize the scheduler service.

        Args:
            redis_url: Redis connection URL (defaults to settings.REDIS_URI)
        """
        self.scheduler = AsyncIOScheduler()
        self.redis: Optional[aioredis.Redis] = None
        self.instance_id = str(uuid.uuid4())
        self.redis_url = redis_url or settings.REDIS_URI
        logger.info(f"Scheduler initialized with instance ID: {self.instance_id}")

    async def start(self):
        """Initialize Redis connection and start the scheduler with all jobs."""
        # Connect to Redis for distributed locking
        self.redis = await aioredis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        logger.info("Scheduler connected to Redis")

        # Register periodic jobs
        self._register_jobs()

        # Start the scheduler
        self.scheduler.start()
        logger.info("Background scheduler started")

    def _register_jobs(self):
        """Register all periodic background jobs."""
        # Negotiation timeout checker - every 5 minutes
        self.scheduler.add_job(
            self.run_with_lock,
            args=["timeout_checker", self.check_negotiation_timeouts],
            trigger="interval",
            minutes=5,
            id="timeout_checker",
            max_instances=1,
            replace_existing=True
        )
        logger.info("Registered job: timeout_checker (every 5 minutes)")

        # Receipt checkpoint creator - every 30 minutes
        self.scheduler.add_job(
            self.run_with_lock,
            args=["receipt_checkpoint", self.create_receipt_checkpoints],
            trigger="interval",
            minutes=30,
            id="receipt_checkpoint",
            max_instances=1,
            replace_existing=True
        )
        logger.info("Registered job: receipt_checkpoint (every 30 minutes)")

    async def run_with_lock(self, job_name: str, func: Callable):
        """Execute a job with distributed lock to prevent duplicate execution.

        Only one instance across all servers will execute the job at a time.

        Args:
            job_name: Unique name for the job (used as lock key)
            func: Async function to execute
        """
        if not self.redis:
            logger.error(f"Redis not initialized, cannot run job {job_name}")
            return

        lock_key = f"scheduler:lock:{job_name}"

        # Try to acquire lock with 5-minute expiry
        acquired = await self.redis.set(
            lock_key,
            self.instance_id,
            nx=True,  # Only set if key doesn't exist
            ex=300    # 5-minute timeout (in case job hangs)
        )

        if not acquired:
            logger.debug(f"Job {job_name} already running on another instance, skipping")
            return

        logger.info(f"Acquired lock for job {job_name}")

        try:
            # Execute the job
            await func()
            logger.info(f"Job {job_name} completed successfully")

        except Exception as e:
            logger.error(f"Job {job_name} failed: {e}", exc_info=True)

        finally:
            # Release lock only if we still own it
            try:
                current_value = await self.redis.get(lock_key)
                if current_value == self.instance_id:
                    await self.redis.delete(lock_key)
                    logger.info(f"Released lock for job {job_name}")
            except Exception as e:
                logger.error(f"Error releasing lock for {job_name}: {e}")

    async def check_negotiation_timeouts(self):
        """Check and expire timed-out negotiations."""
        from app.db.session import async_session_maker
        from app.services.negotiation_service import NegotiationService

        async with async_session_maker() as session:
            try:
                service = NegotiationService(session)
                result = await service.check_timeouts()

                negotiation_timeouts = result.get('negotiation_timeouts', [])
                finalization_timeouts = result.get('finalization_timeouts', [])

                total_expired = len(negotiation_timeouts) + len(finalization_timeouts)

                if total_expired > 0:
                    logger.info(
                        f"Expired {len(negotiation_timeouts)} negotiation(s) "
                        f"and {len(finalization_timeouts)} finalization(s)"
                    )
                else:
                    logger.debug("No negotiations timed out")

            except Exception as e:
                logger.error(f"Error checking negotiation timeouts: {e}", exc_info=True)
                raise

    async def create_receipt_checkpoints(self):
        """Create verification checkpoints for receipt chains.

        This is a placeholder for Phase 1. Full implementation will be added
        when receipt checkpoint system is implemented.
        """
        logger.debug("Receipt checkpoint job triggered (not yet implemented)")
        # TODO: Implement checkpoint creation logic
        # Will create checkpoints every 100 receipts per user
        pass

    async def shutdown(self):
        """Shutdown the scheduler gracefully."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            logger.info("Scheduler stopped")

        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")
