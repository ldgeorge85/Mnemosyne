"""
Migration Helpers

This module provides helper functions for working with database migrations.
These helpers are used for common migration tasks in scripts and application code.
"""

import os
import subprocess
from pathlib import Path

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Path to the alembic executable
ALEMBIC_BIN = "alembic"

# Path to the alembic configuration file
ALEMBIC_CONFIG = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "alembic.ini")


def run_migrations(command: str, *args) -> subprocess.CompletedProcess:
    """
    Run an alembic migration command.
    
    Args:
        command: The alembic command to run (e.g., 'upgrade', 'downgrade')
        *args: Additional arguments to pass to the command
        
    Returns:
        The completed process object from running the command
    """
    cmd = [ALEMBIC_BIN, "-c", ALEMBIC_CONFIG, command]
    cmd.extend(args)
    
    logger.info(f"Running migration command: {' '.join(cmd)}")
    
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def create_migration(message: str) -> str:
    """
    Create a new migration revision.
    
    Args:
        message: The migration message/description
        
    Returns:
        The output of the alembic command
    """
    result = run_migrations("revision", "--autogenerate", "-m", message)
    logger.info(f"Created new migration: {message}")
    return result.stdout


def upgrade_database(revision: str = "head") -> str:
    """
    Upgrade the database to the specified revision.
    
    Args:
        revision: The revision to upgrade to, defaults to 'head' (latest)
        
    Returns:
        The output of the alembic command
    """
    result = run_migrations("upgrade", revision)
    logger.info(f"Upgraded database to revision: {revision}")
    return result.stdout


def downgrade_database(revision: str) -> str:
    """
    Downgrade the database to the specified revision.
    
    Args:
        revision: The revision to downgrade to
        
    Returns:
        The output of the alembic command
    """
    result = run_migrations("downgrade", revision)
    logger.info(f"Downgraded database to revision: {revision}")
    return result.stdout


def get_current_revision() -> str:
    """
    Get the current database revision.
    
    Returns:
        The current revision identifier
    """
    result = run_migrations("current")
    return result.stdout.strip()


def get_migration_history() -> str:
    """
    Get the migration history.
    
    Returns:
        The migration history output
    """
    result = run_migrations("history")
    return result.stdout


def init_migration_environment() -> None:
    """
    Initialize the migration environment if it doesn't exist.
    This creates the alembic_version table in the database.
    """
    # Check if the versions directory exists
    versions_dir = Path(__file__).parent / "versions"
    if not versions_dir.exists():
        versions_dir.mkdir(exist_ok=True)
        logger.info("Created migrations versions directory")
    
    # Check if there are any migrations
    if not list(versions_dir.glob("*.py")):
        logger.info("No migrations found, creating initial migration")
        create_migration("Initial migration")
        
    logger.info("Migration environment initialized")
