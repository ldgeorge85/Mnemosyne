"""
Database Session Management

This module handles SQLAlchemy session management and provides
utilities for database access.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URI,
    pool_pre_ping=True,  # Enable reconnection on stale connections
    echo=settings.APP_DEBUG,  # Log SQL if in debug mode
    future=True,  # Use SQLAlchemy 2.0 style
)

# Create async SQLAlchemy engine
async_engine = create_async_engine(
    settings.DATABASE_URI.replace("postgresql://", "postgresql+asyncpg://"),
    pool_pre_ping=True,
    echo=settings.APP_DEBUG,
)

# Create session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
async_session_maker = sessionmaker(
    class_=AsyncSession, 
    autocommit=False, 
    autoflush=False, 
    bind=async_engine
)

# Create declarative base for models
Base = declarative_base()


def get_db():
    """
    Get a database session from the SessionLocal factory.
    
    Yields:
        An SQLAlchemy session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize the database, creating tables if they don't exist.
    Only used for development and testing environments.
    """
    if settings.APP_ENV != "production":
        logger.info("Creating database tables")
        # Import all models to ensure they're registered with Base
        from app.db import models  # noqa
        
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created")
