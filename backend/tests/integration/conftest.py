"""
Integration Test Configuration

Provides fixtures and configuration for integration tests.
Uses real database with transaction rollback for isolation.
"""

import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings


# Override database URL for testing
TEST_DATABASE_URL = settings.DATABASE_URI.replace(
    "/mnemosyne", "/mnemosyne_test"
).replace("postgresql://", "postgresql+asyncpg://")


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session with automatic rollback.

    Each test gets a fresh session that rolls back after completion,
    ensuring test isolation.
    """
    # Create session factory
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Create connection and start transaction
    connection = await test_engine.connect()
    transaction = await connection.begin()

    # Create session bound to this connection
    session = async_session(bind=connection)

    try:
        yield session
    finally:
        # Clean up: close session, rollback transaction, close connection
        await session.close()
        await transaction.rollback()
        await connection.close()
