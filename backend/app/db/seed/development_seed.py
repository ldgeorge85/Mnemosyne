"""
Development Seed Handler

This module provides seed data for development environments.
It creates sample data for testing and development purposes.
"""

from sqlalchemy import delete, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.seed.seed_handler import SeedHandler

logger = get_logger(__name__)


class DevelopmentSeedHandler(SeedHandler):
    """
    Seed handler for development environments.
    
    This handler provides basic sample data for development and testing.
    It is designed to create a minimal set of data needed for the application to function.
    """
    
    # Run early in the seed process
    priority = 10
    
    # Only run in development and testing environments
    environments = ["development", "testing"]
    
    async def seed(self, session: AsyncSession) -> bool:
        """
        Seed the database with development data.
        
        Args:
            session: The database session
            
        Returns:
            True if seeding was successful, False otherwise
        """
        logger.info("Seeding development data")
        
        try:
            # Seed system settings
            await self._seed_system_settings(session)
            
            # Seed sample users (when user model is implemented)
            # await self._seed_users(session)
            
            # Add more seed methods as needed
            
            logger.info("Development seed completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error seeding development data: {str(e)}")
            return False
    
    async def reset(self, session: AsyncSession) -> None:
        """
        Reset existing development data before seeding.
        
        Args:
            session: The database session
        """
        logger.info("Resetting development data")
        
        try:
            # Reset system settings
            await self._reset_system_settings(session)
            
            # Reset sample users (when user model is implemented)
            # await self._reset_users(session)
            
            # Add more reset methods as needed
            
            logger.info("Development data reset successfully")
        except Exception as e:
            logger.error(f"Error resetting development data: {str(e)}")
            raise
    
    async def _seed_system_settings(self, session: AsyncSession) -> None:
        """
        Seed system settings data.
        
        Args:
            session: The database session
        """
        # Example of how to seed system settings
        # This is a placeholder until we have actual models
        query = text("""
            INSERT INTO system_settings (key, value, description)
            VALUES 
                ('app_name', 'Mnemosyne', 'Application name'),
                ('app_version', '0.1.0', 'Application version'),
                ('debug_mode', 'true', 'Debug mode flag')
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
                logger.info("System settings seeded successfully")
            else:
                logger.warning("System settings table does not exist yet")
        except Exception as e:
            logger.error(f"Error seeding system settings: {str(e)}")
            raise
    
    async def _reset_system_settings(self, session: AsyncSession) -> None:
        """
        Reset system settings data.
        
        Args:
            session: The database session
        """
        # Example of how to reset system settings
        # This is a placeholder until we have actual models
        query = text("DELETE FROM system_settings WHERE key IN ('app_name', 'app_version', 'debug_mode')")
        
        try:
            # Check if the table exists first
            check_query = text("SELECT to_regclass('system_settings')")
            result = await session.execute(check_query)
            table_exists = result.scalar() is not None
            
            if table_exists:
                await session.execute(query)
                logger.info("System settings reset successfully")
            else:
                logger.warning("System settings table does not exist yet")
        except Exception as e:
            logger.error(f"Error resetting system settings: {str(e)}")
            raise
    
    def seed_sync(self, session: Session) -> bool:
        """
        Synchronous version of seed for use in scripts and tests.
        
        Args:
            session: The database session
            
        Returns:
            True if seeding was successful, False otherwise
        """
        logger.info("Seeding development data (sync)")
        
        try:
            # Implement synchronous versions of seed methods as needed
            logger.info("Development seed completed successfully (sync)")
            return True
        except Exception as e:
            logger.error(f"Error seeding development data: {str(e)}")
            return False
    
    def reset_sync(self, session: Session) -> None:
        """
        Synchronous version of reset for use in scripts and tests.
        
        Args:
            session: The database session
        """
        logger.info("Resetting development data (sync)")
        
        try:
            # Implement synchronous versions of reset methods as needed
            logger.info("Development data reset successfully (sync)")
        except Exception as e:
            logger.error(f"Error resetting development data: {str(e)}")
            raise
