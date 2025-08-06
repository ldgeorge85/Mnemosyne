#!/usr/bin/env python
"""
Create Superuser Script

This script creates a superuser account for the Mnemosyne application.
It should be run after the database migrations have been applied.
"""

import asyncio
import argparse
import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.db.models.user import User
from app.db.session import async_session_maker


async def create_superuser(username: str, email: str, password: str, full_name: str = None) -> None:
    """
    Create a superuser account.
    
    Args:
        username: Username for the superuser
        email: Email address for the superuser
        password: Password for the superuser
        full_name: Full name for the superuser (optional)
    """
    async with async_session_maker() as session:
        # Check if user already exists
        from sqlalchemy import text
        result = await session.execute(
            text("SELECT id FROM users WHERE username = :username OR email = :email"),
            {"username": username, "email": email}
        )
        existing_user = result.first()
        
        if existing_user:
            print(f"User with username '{username}' or email '{email}' already exists.")
            return
        
        # Create new superuser
        user = User(
            id=uuid.uuid4(),
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_active=True,
            is_superuser=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        session.add(user)
        await session.commit()
        
        print(f"Superuser '{username}' created successfully!")


async def main() -> None:
    """Main function to parse arguments and create the superuser."""
    parser = argparse.ArgumentParser(description="Create a superuser for Mnemosyne")
    parser.add_argument("--username", required=True, help="Username for the superuser")
    parser.add_argument("--email", required=True, help="Email address for the superuser")
    parser.add_argument("--password", required=True, help="Password for the superuser")
    parser.add_argument("--full-name", help="Full name for the superuser")
    
    args = parser.parse_args()
    
    await create_superuser(
        username=args.username,
        email=args.email,
        password=args.password,
        full_name=args.full_name,
    )


if __name__ == "__main__":
    asyncio.run(main())
