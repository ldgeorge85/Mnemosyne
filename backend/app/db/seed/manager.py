"""
Seed Data Manager

This module provides functionality for seeding the database with initial data
for development, testing, and demonstration purposes.
"""

import importlib
import logging
import os
import pkgutil
from enum import Enum
from typing import Dict, List, Optional, Type, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.db.seed.seed_handler import SeedHandler

logger = get_logger(__name__)


class SeedEnvironment(str, Enum):
    """
    Environment types for seed data.
    Different environments may have different seed data requirements.
    """
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEMO = "demo"
    STAGING = "staging"
    PRODUCTION = "production"


class SeedManager:
    """
    Manages the seeding process for different environments.
    Discovers and runs seed handlers in the correct order.
    """
    
    _handlers: Dict[str, Type[SeedHandler]] = {}
    
    @classmethod
    def register_handler(cls, handler_class: Type[SeedHandler]) -> None:
        """
        Register a seed handler with the manager.
        
        Args:
            handler_class: The seed handler class to register
        """
        name = handler_class.__name__
        logger.debug(f"Registering seed handler: {name}")
        cls._handlers[name] = handler_class
    
    @classmethod
    def discover_handlers(cls) -> None:
        """
        Discover all seed handlers in the seed package.
        This uses Python's pkgutil to find all modules in the seed package
        and imports them to trigger registration.
        """
        logger.info("Discovering seed handlers")
        
        # Get the path to the seed package
        seed_path = os.path.dirname(__file__)
        
        # Find all modules in the seed package
        for _, name, is_pkg in pkgutil.iter_modules([seed_path]):
            if not is_pkg and name != "manager" and name != "seed_handler":
                logger.debug(f"Discovered seed module: {name}")
                try:
                    # Import the module to trigger registration
                    importlib.import_module(f"app.db.seed.{name}")
                except ImportError as e:
                    logger.error(f"Error importing seed module {name}: {str(e)}")
    
    @classmethod
    def get_handlers(cls, environment: SeedEnvironment) -> List[Type[SeedHandler]]:
        """
        Get all handlers for the specified environment, sorted by priority.
        
        Args:
            environment: The environment to get handlers for
            
        Returns:
            A list of handler classes, sorted by priority
        """
        # Make sure handlers are discovered
        if not cls._handlers:
            cls.discover_handlers()
        
        # Filter handlers for the specified environment
        handlers = [
            handler for handler in cls._handlers.values()
            if environment.value in handler.environments
        ]
        
        # Sort by priority (lower number = higher priority)
        return sorted(handlers, key=lambda h: h.priority)
    
    @classmethod
    async def seed_database(
        cls,
        session: AsyncSession,
        environment: Optional[SeedEnvironment] = None,
        reset: bool = False,
    ) -> Dict[str, bool]:
        """
        Seed the database with initial data for the specified environment.
        
        Args:
            session: The database session
            environment: The environment to seed for, defaults to app environment
            reset: Whether to reset existing data before seeding
            
        Returns:
            A dictionary of handler names and their success status
        """
        # Use the app environment if none specified
        environment = environment or SeedEnvironment(settings.APP_ENV)
        
        logger.info(f"Seeding database for environment: {environment.value}")
        
        # Get handlers for this environment
        handlers = cls.get_handlers(environment)
        
        if not handlers:
            logger.warning(f"No seed handlers found for environment: {environment.value}")
            return {}
        
        # Track results
        results: Dict[str, bool] = {}
        
        # Run each handler
        for handler_class in handlers:
            handler_name = handler_class.__name__
            logger.info(f"Running seed handler: {handler_name}")
            
            try:
                # Create and run the handler
                handler = handler_class()
                
                # Reset data if requested
                if reset:
                    await handler.reset(session)
                
                # Seed the data
                success = await handler.seed(session)
                results[handler_name] = success
                
                # Commit after each handler
                await session.commit()
                
                logger.info(f"Seed handler {handler_name} completed successfully")
            except Exception as e:
                # Roll back on error
                await session.rollback()
                
                logger.error(f"Error in seed handler {handler_name}: {str(e)}")
                results[handler_name] = False
        
        return results
    
    @classmethod
    def seed_database_sync(
        cls,
        session: Session,
        environment: Optional[SeedEnvironment] = None,
        reset: bool = False,
    ) -> Dict[str, bool]:
        """
        Synchronous version of seed_database for use in scripts and tests.
        
        Args:
            session: The database session
            environment: The environment to seed for, defaults to app environment
            reset: Whether to reset existing data before seeding
            
        Returns:
            A dictionary of handler names and their success status
        """
        # Use the app environment if none specified
        environment = environment or SeedEnvironment(settings.APP_ENV)
        
        logger.info(f"Seeding database for environment: {environment.value}")
        
        # Get handlers for this environment
        handlers = cls.get_handlers(environment)
        
        if not handlers:
            logger.warning(f"No seed handlers found for environment: {environment.value}")
            return {}
        
        # Track results
        results: Dict[str, bool] = {}
        
        # Run each handler
        for handler_class in handlers:
            handler_name = handler_class.__name__
            logger.info(f"Running seed handler: {handler_name}")
            
            try:
                # Create and run the handler
                handler = handler_class()
                
                # Reset data if requested
                if reset:
                    handler.reset_sync(session)
                
                # Seed the data
                success = handler.seed_sync(session)
                results[handler_name] = success
                
                # Commit after each handler
                session.commit()
                
                logger.info(f"Seed handler {handler_name} completed successfully")
            except Exception as e:
                # Roll back on error
                session.rollback()
                
                logger.error(f"Error in seed handler {handler_name}: {str(e)}")
                results[handler_name] = False
        
        return results
