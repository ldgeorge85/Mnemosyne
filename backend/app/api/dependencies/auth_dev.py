"""
Development authentication dependency that always returns a mock user
"""

import uuid
from datetime import datetime
from typing import Optional

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models.user import User
from app.db.session import get_async_db


async def get_current_user_dev(
    request: Request = None,
    db: AsyncSession = Depends(get_async_db),
    token: Optional[str] = None
) -> User:
    """
    Development-only dependency that always returns a mock user.
    This bypasses all authentication for development purposes.
    
    WARNING: This should NEVER be used in production!
    """
    if settings.ENVIRONMENT != "development":
        raise RuntimeError("Development auth dependency used in non-development environment!")
    
    # Always return a mock user in development
    mock_user = User(
        id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
        email="dev@mnemosyne.local",
        username="dev_user",
        hashed_password="",
        is_active=True,
        is_superuser=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    return mock_user


# Alias for compatibility
get_current_user_optional = get_current_user_dev