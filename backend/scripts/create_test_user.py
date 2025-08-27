#!/usr/bin/env python3
"""
Create test user for testing
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.models.user import User
from app.core.auth.providers import pwd_context
from app.core.config import settings
import uuid

async def create_test_user():
    # Convert to async URI
    db_uri = str(settings.DATABASE_URI).replace('postgresql://', 'postgresql+asyncpg://')
    engine = create_async_engine(db_uri, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Check if test user exists
        from sqlalchemy import select
        result = await session.execute(
            select(User).where(User.email == "test123@example.com")
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print("Test user already exists")
            return
        
        # Create test user
        user = User(
            id=uuid.uuid4(),
            username="test123",
            email="test123@example.com",
            hashed_password=pwd_context.hash("testpass123"),
            is_active=True
        )
        
        session.add(user)
        await session.commit()
        print(f"✅ Created test user: {user.username}")
        print(f"   ID: {user.id}")

if __name__ == "__main__":
    asyncio.run(create_test_user())