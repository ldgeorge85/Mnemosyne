"""
Async SQLAlchemy database setup for Mnemosyne
Production-ready async database configuration
"""

from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
import logging

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
    AsyncAttrs
)
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool
from sqlalchemy import MetaData, event
from sqlalchemy.exc import SQLAlchemyError
import uuid
from datetime import datetime

from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Naming convention for constraints
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all database models"""
    
    metadata = metadata
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name"""
        return cls.__name__.lower() + "s"
    
    def dict(self) -> dict:
        """Convert model to dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def __repr__(self) -> str:
        """String representation"""
        params = ', '.join(f'{k}={v}' for k, v in self.dict().items())
        return f"{self.__class__.__name__}({params})"


class DatabaseManager:
    """Manages database connections and sessions"""
    
    def __init__(self):
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize database engine and session factory"""
        if self._initialized:
            return
        
        try:
            # Choose pool class based on environment
            if settings.is_production:
                poolclass = AsyncAdaptedQueuePool
                pool_kwargs = {
                    "pool_size": settings.database_pool_size,
                    "max_overflow": settings.database_max_overflow,
                    "pool_timeout": settings.database_pool_timeout,
                    "pool_recycle": 3600,  # Recycle connections after 1 hour
                    "pool_pre_ping": True,  # Test connections before using
                }
            else:
                # Use NullPool for development (no connection pooling)
                poolclass = NullPool
                pool_kwargs = {}
            
            # Create async engine
            self.engine = create_async_engine(
                settings.database_url,
                echo=settings.database_echo,
                poolclass=poolclass,
                future=True,
                **pool_kwargs
            )
            
            # Create session factory
            self.session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )
            
            # Set up event listeners
            self._setup_event_listeners()
            
            self._initialized = True
            logger.info("Database manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def close(self) -> None:
        """Close database connections"""
        if self.engine:
            await self.engine.dispose()
            self._initialized = False
            logger.info("Database connections closed")
    
    async def create_tables(self) -> None:
        """Create all tables"""
        if not self.engine:
            await self.initialize()
        
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created")
    
    async def drop_tables(self) -> None:
        """Drop all tables (use with caution!)"""
        if not self.engine:
            await self.initialize()
        
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            logger.warning("All database tables dropped")
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session"""
        if not self.session_factory:
            await self.initialize()
        
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Database session error: {e}")
                raise
            finally:
                await session.close()
    
    async def get_session(self) -> AsyncSession:
        """Get a new async session (for dependency injection)"""
        if not self.session_factory:
            await self.initialize()
        return self.session_factory()
    
    async def health_check(self) -> bool:
        """Check database health"""
        try:
            async with self.session() as session:
                result = await session.execute("SELECT 1")
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def _setup_event_listeners(self) -> None:
        """Set up SQLAlchemy event listeners"""
        
        @event.listens_for(self.engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            """Enable foreign keys for SQLite"""
            if "sqlite" in settings.database_url:
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
        
        @event.listens_for(self.engine.sync_engine, "connect")
        def set_postgresql_search_path(dbapi_conn, connection_record):
            """Set search path for PostgreSQL"""
            if "postgresql" in settings.database_url:
                with dbapi_conn.cursor() as cursor:
                    cursor.execute("SET search_path TO public")


# Global database manager instance
db_manager = DatabaseManager()


# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with db_manager.session() as session:
        yield session


# Utility functions
async def init_db() -> None:
    """Initialize database (create tables if needed)"""
    await db_manager.initialize()
    await db_manager.create_tables()


async def close_db() -> None:
    """Close database connections"""
    await db_manager.close()


# Base mixins for common fields
class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    
    @declared_attr
    def created_at(cls):
        from sqlalchemy import DateTime, func, Column
        return Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    @declared_attr
    def updated_at(cls):
        from sqlalchemy import DateTime, func, Column
        return Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False
        )


class UUIDMixin:
    """Mixin for UUID primary key"""
    
    @declared_attr
    def id(cls):
        from sqlalchemy import Column, UUID as SQLAlchemyUUID
        return Column(
            SQLAlchemyUUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            nullable=False
        )


class SoftDeleteMixin:
    """Mixin for soft delete functionality"""
    
    @declared_attr
    def deleted_at(cls):
        from sqlalchemy import DateTime, Column
        return Column(DateTime(timezone=True), nullable=True)
    
    @property
    def is_deleted(self) -> bool:
        """Check if record is soft deleted"""
        return self.deleted_at is not None
    
    def soft_delete(self) -> None:
        """Mark record as deleted"""
        self.deleted_at = datetime.utcnow()
    
    def restore(self) -> None:
        """Restore soft deleted record"""
        self.deleted_at = None


# Export key items
__all__ = [
    "Base",
    "DatabaseManager",
    "db_manager",
    "get_db",
    "init_db",
    "close_db",
    "TimestampMixin",
    "UUIDMixin",
    "SoftDeleteMixin",
]