"""
Demo Seed Handler

This module provides seed data for demonstration environments.
It creates more comprehensive sample data suitable for demos and presentations.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.seed.seed_handler import SeedHandler

logger = get_logger(__name__)


class DemoSeedHandler(SeedHandler):
    """
    Seed handler for demonstration environments.
    
    This handler provides comprehensive sample data for demonstrations,
    including realistic examples of conversations, memories, and embeddings.
    """
    
    # Run after development seed
    priority = 20
    
    # Only run in demo environment
    environments = ["demo"]
    
    async def seed(self, session: AsyncSession) -> bool:
        """
        Seed the database with demo data.
        
        Args:
            session: The database session
            
        Returns:
            True if seeding was successful, False otherwise
        """
        logger.info("Seeding demo data")
        
        try:
            # Seed system settings
            await self._seed_system_settings(session)
            
            # Seed sample conversations (when models are implemented)
            await self._seed_sample_conversations(session)
            
            # Seed sample memories (when models are implemented)
            await self._seed_sample_memories(session)
            
            # Add more seed methods as needed
            
            logger.info("Demo seed completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error seeding demo data: {str(e)}")
            return False
    
    async def reset(self, session: AsyncSession) -> None:
        """
        Reset existing demo data before seeding.
        
        Args:
            session: The database session
        """
        logger.info("Resetting demo data")
        
        try:
            # Reset sample data (when models are implemented)
            await self._reset_sample_conversations(session)
            await self._reset_sample_memories(session)
            
            # Add more reset methods as needed
            
            logger.info("Demo data reset successfully")
        except Exception as e:
            logger.error(f"Error resetting demo data: {str(e)}")
            raise
    
    async def _seed_system_settings(self, session: AsyncSession) -> None:
        """
        Seed demo-specific system settings.
        
        Args:
            session: The database session
        """
        # Example of how to seed demo-specific system settings
        query = text("""
            INSERT INTO system_settings (key, value, description)
            VALUES 
                ('demo_mode', 'true', 'Demo mode flag'),
                ('demo_user', 'demo@example.com', 'Demo user email'),
                ('demo_started_at', CURRENT_TIMESTAMP, 'Demo start timestamp')
            ON CONFLICT (key) DO UPDATE 
            SET value = EXCLUDED.value, description = EXCLUDED.description
        """)
        
        try:
            # Check if the table exists first
            check_query = text("SELECT to_regclass('system_settings')")
            result = await session.execute(check_query)
            table_exists = result.scalar() is not None
            
            if table_exists:
                await session.execute(query)
                logger.info("Demo system settings seeded successfully")
            else:
                logger.warning("System settings table does not exist yet")
        except Exception as e:
            logger.error(f"Error seeding demo system settings: {str(e)}")
            raise
    
    async def _seed_sample_conversations(self, session: AsyncSession) -> None:
        """
        Seed sample conversations for demo purposes.
        
        Args:
            session: The database session
        """
        logger.info("Seeding sample conversations")
        
        # This is a placeholder until we have actual models
        # In the future, we'll create actual conversation objects with messages
        logger.info("Sample conversations placeholder")
    
    async def _seed_sample_memories(self, session: AsyncSession) -> None:
        """
        Seed sample memories for demo purposes.
        
        Args:
            session: The database session
        """
        logger.info("Seeding sample memories")
        
        # This is a placeholder until we have actual models
        # In the future, we'll create actual memory objects with embeddings
        logger.info("Sample memories placeholder")
    
    async def _reset_sample_conversations(self, session: AsyncSession) -> None:
        """
        Reset sample conversations.
        
        Args:
            session: The database session
        """
        logger.info("Resetting sample conversations")
        
        # This is a placeholder until we have actual models
        # In the future, we'll delete actual conversation objects
        logger.info("Sample conversations reset placeholder")
    
    async def _reset_sample_memories(self, session: AsyncSession) -> None:
        """
        Reset sample memories.
        
        Args:
            session: The database session
        """
        logger.info("Resetting sample memories")
        
        # This is a placeholder until we have actual models
        # In the future, we'll delete actual memory objects
        logger.info("Sample memories reset placeholder")
    
    def seed_sync(self, session: Session) -> bool:
        """
        Synchronous version of seed for use in scripts and tests.
        
        Args:
            session: The database session
            
        Returns:
            True if seeding was successful, False otherwise
        """
        logger.info("Seeding demo data (sync)")
        
        try:
            # Implement synchronous versions of seed methods as needed
            logger.info("Demo seed completed successfully (sync)")
            return True
        except Exception as e:
            logger.error(f"Error seeding demo data: {str(e)}")
            return False
    
    def reset_sync(self, session: Session) -> None:
        """
        Synchronous version of reset for use in scripts and tests.
        
        Args:
            session: The database session
        """
        logger.info("Resetting demo data (sync)")
        
        try:
            # Implement synchronous versions of reset methods as needed
            logger.info("Demo data reset successfully (sync)")
        except Exception as e:
            logger.error(f"Error resetting demo data: {str(e)}")
            raise
