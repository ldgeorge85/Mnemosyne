"""
Database Dependencies

This module provides database-related dependencies for FastAPI endpoints.
"""

from typing import AsyncGenerator, Generator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, async_session_maker


def get_db() -> Generator[Session, None, None]:
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


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async database session from the async_session_maker factory.
    
    Yields:
        An SQLAlchemy async session
    """
    async with async_session_maker() as session:
        yield session
