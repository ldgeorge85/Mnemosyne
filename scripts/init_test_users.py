#!/usr/bin/env python3
"""
Create test users in the database to match the static auth provider
"""
import asyncio
import sys
from pathlib import Path
import uuid

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.core.database import get_db
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def create_test_users():
    """Create test users matching the static auth provider"""
    
    test_users = [
        {
            "id": uuid.UUID("11111111-1111-1111-1111-111111111111"),
            "username": "test",
            "email": "test@mnemosyne.local",
            "hashed_password": get_password_hash("test123"),
            "is_active": True,
            "is_superuser": False
        },
        {
            "id": uuid.UUID("22222222-2222-2222-2222-222222222222"),
            "username": "admin",
            "email": "admin@mnemosyne.local",
            "hashed_password": get_password_hash("admin123"),
            "is_active": True,
            "is_superuser": True
        },
        {
            "id": uuid.UUID("33333333-3333-3333-3333-333333333333"),
            "username": "demo",
            "email": "demo@mnemosyne.local",
            "hashed_password": get_password_hash("demo123"),
            "is_active": True,
            "is_superuser": False
        }
    ]
    
    async for session in get_db():
        try:
            for user_data in test_users:
                # Check if user already exists
                stmt = select(User).where(User.id == user_data["id"])
                result = await session.execute(stmt)
                existing_user = result.scalar_one_or_none()
                
                if existing_user:
                    print(f"User {user_data['username']} already exists with ID {user_data['id']}")
                else:
                    # Create new user
                    user = User(**user_data)
                    session.add(user)
                    print(f"Created user {user_data['username']} with ID {user_data['id']}")
            
            await session.commit()
            print("\nAll test users created successfully!")
            
        except Exception as e:
            print(f"Error creating test users: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
            break  # Exit after first iteration


if __name__ == "__main__":
    asyncio.run(create_test_users())