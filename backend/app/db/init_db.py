"""
Database Initialization

This module provides functions to initialize the database with required tables and extensions.
It should be run when the application starts or via a dedicated script.
"""

import asyncio
import logging
from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.db.session import async_session_maker
from app.db.vector import ensure_extension

# Configure logging
configure_logging()
logger = get_logger(__name__)


async def create_tables(session: AsyncSession) -> bool:
    """
    Create initial tables required for the application.
    This is a temporary solution until we have models and migrations set up.
    
    Args:
        session: The database session
        
    Returns:
        True if tables were created successfully, False otherwise
    """
    try:
        # Create system_settings table for seed data
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS system_settings (
                key VARCHAR(255) PRIMARY KEY,
                value TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Create a sample items table for testing
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS items (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        await session.commit()
        logger.info("Initial tables created successfully")
        return True
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating tables: {str(e)}")
        return False


async def init_db() -> bool:
    """
    Initialize the database with required extensions and tables.
    
    Returns:
        True if initialization was successful, False otherwise
    """
    logger.info("Initializing database")
    
    async with async_session_maker() as session:
        session: AsyncSession = session
        
        # Ensure the pgvector extension is installed
        vector_extension_enabled = await ensure_extension(session)
        if not vector_extension_enabled:
            logger.error("Failed to enable pgvector extension")
            return False
        
        # Create initial tables
        tables_created = await create_tables(session)
        if not tables_created:
            logger.error("Failed to create initial tables")
            return False
        
        logger.info("Database initialized successfully")
        return True


async def main() -> None:
    """
    Main entry point for database initialization.
    """
    success = await init_db()
    if not success:
        logger.error("Database initialization failed")
        exit(1)
    
    logger.info("Database initialization completed successfully")


if __name__ == "__main__":
    asyncio.run(main())
