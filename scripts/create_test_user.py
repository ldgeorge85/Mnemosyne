#!/usr/bin/env python3
"""
Create a test user for development and testing
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import backend modules
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.core.database import get_async_session
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy import select
import uuid


async def create_test_user():
    """Create a test user if it doesn't exist"""
    async for session in get_async_session():
        try:
            # Check if test user already exists
            stmt = select(User).where(User.username == "test")
            result = await session.execute(stmt)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print("Test user already exists")
                print(f"  Username: {existing_user.username}")
                print(f"  Email: {existing_user.email}")
                print(f"  ID: {existing_user.id}")
                return
            
            # Create new test user
            test_user = User(
                id=uuid.uuid4(),
                username="test",
                email="test@example.com",
                hashed_password=get_password_hash("test"),
                is_active=True,
                is_superuser=False
            )
            
            session.add(test_user)
            await session.commit()
            
            print("Test user created successfully!")
            print(f"  Username: test")
            print(f"  Password: test")
            print(f"  Email: test@example.com")
            print(f"  ID: {test_user.id}")
            
        except Exception as e:
            print(f"Error creating test user: {e}")
            await session.rollback()
        finally:
            await session.close()


if __name__ == "__main__":
    asyncio.run(create_test_user())