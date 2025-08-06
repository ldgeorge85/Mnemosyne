"""
Pytest configuration file for Mnemosyne backend tests.

This module contains fixtures and configuration for pytest to use in all test modules.
"""

import asyncio
import os
from typing import AsyncGenerator, Dict, Generator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Import settings after setting test environment variables
os.environ['APP_ENV'] = 'testing'
os.environ['OPENAI_API_KEY'] = 'test-api-key'
os.environ['OPENAI_MODEL'] = 'gpt-3.5-turbo'
os.environ['OPENAI_ORG_ID'] = 'test-org-id'
os.environ['DB_DATABASE'] = 'mnemosyne_test'

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app as fastapi_app


# Use test database - constructed from individual components for better control
TEST_DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_DATABASE}"

# Print test configuration for debugging
print(f"Test database URL: {TEST_DATABASE_URL}")
print(f"OpenAI API Key configured: {'Yes' if settings.OPENAI_API_KEY else 'No'}")
print(f"OpenAI Model: {settings.OPENAI_MODEL}")
print(f"API Prefix: {settings.API_PREFIX}")


# Create test database engine
engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Create an instance of the default event loop for each test case.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def app() -> FastAPI:
    """
    Create a FastAPI app instance for testing.
    """
    return fastapi_app


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for a test.
    
    This fixture creates all tables in the test database, 
    yields a session for the test to use, and then drops all tables after the test.
    """
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestingSessionLocal() as session:
        yield session
    
    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(app: FastAPI, db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async test client for testing API endpoints.
    
    This fixture overrides the get_db dependency to use the test database session.
    """
    # Override the get_db dependency to use the test database session
    async def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    
    # Create test client using TestClient for the app and AsyncClient for async tests
    from fastapi.testclient import TestClient
    
    # Create a TestClient that wraps our app
    test_client = TestClient(app)
    
    # For async tests, we'll use AsyncClient without the app parameter
    async with AsyncClient(base_url="http://test") as async_client:
        # Set a reference to the test_client on the async_client for convenience
        async_client.test_client = test_client
        yield async_client
    
    # Clear dependency overrides
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> Dict:
    """
    Create a test user for authentication tests.
    
    This fixture will be expanded once the User model is implemented.
    """
    # This is a placeholder until we implement the User model
    # Will be updated in TASK-003: Implement JWT Authentication
    test_user_data = {
        "id": 1,
        "email": "test@example.com",
        "username": "testuser",
        "is_active": True
    }
    
    return test_user_data


@pytest.fixture(scope="function")
async def auth_headers(test_user: Dict) -> Dict[str, str]:
    """
    Create authentication headers for test requests.
    
    This fixture will be expanded once JWT authentication is implemented.
    """
    # This is a placeholder until we implement JWT authentication
    # Will be updated in TASK-003: Implement JWT Authentication
    return {"Authorization": f"Bearer test-token"}
