"""
Seed Handler Base Class

This module defines the base class for all seed handlers.
Seed handlers are responsible for seeding specific types of data.
"""

import abc
from typing import ClassVar, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.logging import get_logger

logger = get_logger(__name__)


class SeedHandler(abc.ABC):
    """
    Base class for all seed handlers.
    
    All seed handlers should:
    1. Inherit from this class
    2. Set appropriate class variables (priority, environments)
    3. Implement the seed and reset methods
    4. Register themselves with the SeedManager
    
    Example:
        class UserSeedHandler(SeedHandler):
            priority = 10
            environments = ["development", "testing"]
            
            async def seed(self, session):
                # Create users
                return True
                
            async def reset(self, session):
                # Delete existing users
                pass
    """
    
    # Class variables to be overridden by subclasses
    priority: ClassVar[int] = 100  # Default priority (lower = runs earlier)
    environments: ClassVar[List[str]] = []  # Environments this handler runs in
    
    @abc.abstractmethod
    async def seed(self, session: AsyncSession) -> bool:
        """
        Seed the database with data.
        
        Args:
            session: The database session
            
        Returns:
            True if seeding was successful, False otherwise
        """
        pass
    
    @abc.abstractmethod
    async def reset(self, session: AsyncSession) -> None:
        """
        Reset existing data before seeding.
        
        Args:
            session: The database session
        """
        pass
    
    def seed_sync(self, session: Session) -> bool:
        """
        Synchronous version of seed for use in scripts and tests.
        
        Args:
            session: The database session
            
        Returns:
            True if seeding was successful, False otherwise
        """
        logger.warning(f"Using default synchronous seed method for {self.__class__.__name__}")
        return False
    
    def reset_sync(self, session: Session) -> None:
        """
        Synchronous version of reset for use in scripts and tests.
        
        Args:
            session: The database session
        """
        logger.warning(f"Using default synchronous reset method for {self.__class__.__name__}")
        pass
    
    @classmethod
    def __init_subclass__(cls, **kwargs):
        """
        Register the handler with the SeedManager when subclassed.
        This is called automatically when a class inherits from SeedHandler.
        """
        super().__init_subclass__(**kwargs)
        
        # Import here to avoid circular imports
        from app.db.seed.manager import SeedManager
        
        # Register with the manager
        SeedManager.register_handler(cls)
