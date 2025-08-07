#!/usr/bin/env python3
"""
Database initialization script for Mnemosyne Protocol
Creates all tables and initializes vector stores
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging
from sqlalchemy import text

from backend.core.config import get_settings
from backend.core.database import db_manager, Base
from backend.core.vectors import vector_store
from backend.core.redis_client import redis_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


async def check_database_exists() -> bool:
    """Check if database exists"""
    try:
        async with db_manager.session() as session:
            result = await session.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception:
        return False


async def create_extensions() -> None:
    """Create required PostgreSQL extensions"""
    logger.info("Creating PostgreSQL extensions...")
    
    async with db_manager.session() as session:
        try:
            # Enable UUID extension
            await session.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
            logger.info("✓ UUID extension enabled")
            
            # Enable vector extension for pgvector
            await session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            logger.info("✓ Vector extension enabled")
            
            # Enable pg_trgm for text search
            await session.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
            logger.info("✓ pg_trgm extension enabled")
            
            await session.commit()
            
        except Exception as e:
            logger.error(f"Error creating extensions: {e}")
            raise


async def create_tables() -> None:
    """Create all database tables"""
    logger.info("Creating database tables...")
    
    try:
        await db_manager.create_tables()
        logger.info("✓ All tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise


async def initialize_vector_store() -> None:
    """Initialize Qdrant vector store"""
    logger.info("Initializing vector store...")
    
    try:
        await vector_store.initialize()
        
        # Verify collections
        for collection in ["memories", "reflections", "signals"]:
            info = await vector_store.get_collection_info(collection)
            if info:
                logger.info(f"✓ Collection '{collection}' initialized")
            else:
                logger.error(f"✗ Collection '{collection}' not found")
        
    except Exception as e:
        logger.error(f"Error initializing vector store: {e}")
        raise


async def initialize_redis() -> None:
    """Initialize Redis streams and consumer groups"""
    logger.info("Initializing Redis streams...")
    
    try:
        await redis_manager.initialize()
        
        # Verify streams
        for stream in redis_manager.streams.keys():
            logger.info(f"✓ Stream '{stream}' initialized")
        
        logger.info("✓ Redis initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing Redis: {e}")
        raise


async def create_default_user() -> None:
    """Create a default admin user for testing"""
    logger.info("Creating default admin user...")
    
    try:
        from backend.models.user import User, InitiationLevel
        
        async with db_manager.session() as session:
            # Check if admin exists
            result = await session.execute(
                text("SELECT id FROM users WHERE username = :username"),
                {"username": "admin"}
            )
            
            if result.first():
                logger.info("✓ Admin user already exists")
                return
            
            # Create admin user
            admin = User(
                username="admin",
                email="admin@mnemosyne.local",
                display_name="System Administrator",
                initiation_level=InitiationLevel.KEEPER,
                sigil="⊕",
                glyphs=["∴", "⊙", "◈"],
                domains=["system", "administration", "protocol"],
                is_verified=True,
                trust_score=1.0,
                reputation=1.0
            )
            admin.set_password("changeme123")  # Default password
            
            session.add(admin)
            await session.commit()
            
            logger.info("✓ Admin user created (username: admin, password: changeme123)")
            logger.warning("⚠ Please change the admin password immediately!")
            
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        raise


async def verify_initialization() -> None:
    """Verify all components are initialized"""
    logger.info("\nVerifying initialization...")
    
    # Check database
    if await db_manager.health_check():
        logger.info("✓ Database is healthy")
    else:
        logger.error("✗ Database health check failed")
        return False
    
    # Check vector store
    if await vector_store.health_check():
        logger.info("✓ Vector store is healthy")
    else:
        logger.error("✗ Vector store health check failed")
        return False
    
    # Check Redis
    if await redis_manager.health_check():
        logger.info("✓ Redis is healthy")
    else:
        logger.error("✗ Redis health check failed")
        return False
    
    return True


async def main():
    """Main initialization function"""
    logger.info("=" * 60)
    logger.info("Mnemosyne Protocol Database Initialization")
    logger.info("=" * 60)
    
    try:
        # Initialize database manager
        logger.info("\n1. Initializing database connection...")
        await db_manager.initialize()
        logger.info("✓ Database connection established")
        
        # Create extensions
        logger.info("\n2. Creating PostgreSQL extensions...")
        await create_extensions()
        
        # Create tables
        logger.info("\n3. Creating database tables...")
        await create_tables()
        
        # Initialize vector store
        logger.info("\n4. Initializing vector store...")
        await initialize_vector_store()
        
        # Initialize Redis
        logger.info("\n5. Initializing Redis...")
        await initialize_redis()
        
        # Create default user
        logger.info("\n6. Creating default user...")
        await create_default_user()
        
        # Verify everything
        logger.info("\n7. Final verification...")
        if await verify_initialization():
            logger.info("\n" + "=" * 60)
            logger.info("✅ Database initialization completed successfully!")
            logger.info("=" * 60)
            
            logger.info("\nNext steps:")
            logger.info("1. Change the admin password")
            logger.info("2. Start the backend service: docker-compose up backend")
            logger.info("3. Access the API at: http://localhost:8000")
            logger.info("4. View API docs at: http://localhost:8000/docs")
        else:
            logger.error("\n⚠ Some components failed verification")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"\n❌ Initialization failed: {e}")
        sys.exit(1)
        
    finally:
        # Clean up connections
        await db_manager.close()
        await vector_store.close()
        await redis_manager.close()


if __name__ == "__main__":
    asyncio.run(main())