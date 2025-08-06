"""
Database Connection Management

This module provides functionality for managing database connections,
including connection pooling and health checks.
"""

import time
from contextlib import contextmanager
from typing import Generator, Optional

import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.pool import ThreadedConnectionPool
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Connection pool
_pool: Optional[ThreadedConnectionPool] = None

# Maximum number of retries for connection attempts
MAX_RETRIES = 5

# Base delay between retries in seconds
BASE_RETRY_DELAY = 1


def init_connection_pool(
    min_connections: int = 1,
    max_connections: int = 10,
    retry: bool = True,
) -> ThreadedConnectionPool:
    """
    Initialize the database connection pool.
    
    Args:
        min_connections: Minimum number of connections in the pool
        max_connections: Maximum number of connections in the pool
        retry: Whether to retry failed connection attempts
        
    Returns:
        The connection pool
    """
    global _pool
    
    if _pool is not None:
        logger.debug("Connection pool already initialized")
        return _pool
    
    logger.info(f"Initializing connection pool with {min_connections} to {max_connections} connections")
    
    # Parse connection parameters from DATABASE_URI
    db_params = {
        "dbname": settings.DB_DATABASE,
        "user": settings.DB_USERNAME,
        "password": settings.DB_PASSWORD,
        "host": settings.DB_HOST,
        "port": settings.DB_PORT,
    }
    
    if retry:
        retries = 0
        last_error = None
        
        while retries < MAX_RETRIES:
            try:
                _pool = ThreadedConnectionPool(
                    min_connections,
                    max_connections,
                    **db_params,
                )
                logger.info("Connection pool initialized successfully")
                return _pool
            except Exception as e:
                retries += 1
                last_error = e
                retry_delay = BASE_RETRY_DELAY * (2 ** retries)  # Exponential backoff
                
                logger.warning(
                    f"Failed to initialize connection pool (attempt {retries}/{MAX_RETRIES}): {str(e)}. "
                    f"Retrying in {retry_delay} seconds..."
                )
                
                time.sleep(retry_delay)
        
        # If we get here, we've exhausted our retries
        logger.error(f"Failed to initialize connection pool after {MAX_RETRIES} attempts: {str(last_error)}")
        raise last_error
    else:
        # No retry, just try once
        _pool = ThreadedConnectionPool(
            min_connections,
            max_connections,
            **db_params,
        )
        logger.info("Connection pool initialized successfully")
        return _pool


@contextmanager
def get_connection() -> Generator:
    """
    Get a connection from the pool and ensure it's returned.
    
    Yields:
        A database connection
    """
    global _pool
    
    # Initialize the pool if it doesn't exist
    if _pool is None:
        init_connection_pool()
    
    # Get a connection from the pool
    conn = _pool.getconn()
    
    try:
        # Yield the connection
        yield conn
    finally:
        # Return the connection to the pool
        _pool.putconn(conn)


@contextmanager
def get_cursor(cursor_factory=DictCursor) -> Generator:
    """
    Get a database cursor with automatic cleanup.
    
    Args:
        cursor_factory: The cursor factory to use
        
    Yields:
        A database cursor
    """
    with get_connection() as conn:
        # Create a cursor
        cursor = conn.cursor(cursor_factory=cursor_factory)
        
        try:
            # Yield the cursor
            yield cursor
            # Commit the transaction
            conn.commit()
        except Exception:
            # Roll back the transaction on error
            conn.rollback()
            raise
        finally:
            # Close the cursor
            cursor.close()


def connection_health_check() -> bool:
    """
    Check if the database connection is healthy.
    
    Returns:
        True if the connection is healthy, False otherwise
    """
    try:
        with get_cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            return result[0] == 1
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False


def close_connection_pool() -> None:
    """
    Close the connection pool and release all connections.
    Should be called when the application is shutting down.
    """
    global _pool
    
    if _pool is not None:
        logger.info("Closing connection pool")
        _pool.closeall()
        _pool = None
        logger.info("Connection pool closed")


def setup_engine_events(engine: Engine) -> None:
    """
    Set up SQLAlchemy engine events for monitoring and debugging.
    
    Args:
        engine: The SQLAlchemy engine
    """
    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        conn.info.setdefault("query_start_time", []).append(time.time())
        if settings.APP_DEBUG:
            logger.debug(f"Executing query: {statement}")
    
    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        total_time = time.time() - conn.info["query_start_time"].pop()
        if settings.APP_DEBUG:
            logger.debug(f"Query executed in {total_time:.4f}s")


def get_engine(connection_string: Optional[str] = None) -> Engine:
    """
    Create a SQLAlchemy engine with appropriate configuration.
    
    Args:
        connection_string: Optional connection string, defaults to settings.DATABASE_URI
        
    Returns:
        A configured SQLAlchemy engine
    """
    connection_string = connection_string or settings.DATABASE_URI
    
    engine = create_engine(
        connection_string,
        pool_pre_ping=True,  # Detect and recover from disconnects
        pool_size=5,  # Number of connections to keep open
        max_overflow=10,  # Maximum number of connections above pool_size
        pool_timeout=30,  # Timeout for getting a connection from the pool
        pool_recycle=1800,  # Recycle connections after 30 minutes
        echo=settings.APP_DEBUG,  # Log SQL if in debug mode
    )
    
    # Set up engine events
    setup_engine_events(engine)
    
    return engine


def get_session(engine: Optional[Engine] = None) -> Session:
    """
    Get a new SQLAlchemy session.
    
    Args:
        engine: Optional SQLAlchemy engine, created if not provided
        
    Returns:
        A new SQLAlchemy session
    """
    if engine is None:
        engine = get_engine()
    
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return session_factory()
