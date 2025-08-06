"""
Database Backup Utilities

This module provides functionality for backing up and restoring the database.
It includes utilities for creating backups, scheduling backups, and restoring from backups.
"""

import datetime
import os
import subprocess
from pathlib import Path
from typing import List, Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Default backup directory
DEFAULT_BACKUP_DIR = Path("/backups") if os.environ.get("DOCKER_ENV") else Path("./backups")


def ensure_backup_directory(backup_dir: Optional[Path] = None) -> Path:
    """
    Ensure the backup directory exists.
    
    Args:
        backup_dir: Optional backup directory path, defaults to DEFAULT_BACKUP_DIR
        
    Returns:
        The backup directory path
    """
    backup_dir = backup_dir or DEFAULT_BACKUP_DIR
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def create_backup(
    backup_dir: Optional[Path] = None,
    db_name: Optional[str] = None,
    db_user: Optional[str] = None,
    db_host: Optional[str] = None,
    db_port: Optional[str] = None,
    compress: bool = True,
) -> Path:
    """
    Create a database backup using pg_dump.
    
    Args:
        backup_dir: Optional backup directory path, defaults to DEFAULT_BACKUP_DIR
        db_name: Optional database name, defaults to settings.DB_DATABASE
        db_user: Optional database user, defaults to settings.DB_USERNAME
        db_host: Optional database host, defaults to settings.DB_HOST
        db_port: Optional database port, defaults to settings.DB_PORT
        compress: Whether to compress the backup
        
    Returns:
        The path to the created backup file
    """
    # Use default values if not provided
    db_name = db_name or settings.DB_DATABASE
    db_user = db_user or settings.DB_USERNAME
    db_host = db_host or settings.DB_HOST
    db_port = db_port or settings.DB_PORT
    
    # Ensure the backup directory exists
    backup_dir = ensure_backup_directory(backup_dir)
    
    # Generate a timestamp for the backup filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Set the backup filename
    extension = "sql.gz" if compress else "sql"
    backup_file = backup_dir / f"{db_name}_{timestamp}.{extension}"
    
    # Build the pg_dump command
    cmd = [
        "pg_dump",
        f"--dbname={db_name}",
        f"--username={db_user}",
        f"--host={db_host}",
        f"--port={db_port}",
        "--format=plain",
        "--no-owner",
        "--no-acl",
    ]
    
    # Add compression if requested
    if compress:
        cmd = cmd + ["--compress=9"]
    
    # Add the output file
    cmd = cmd + [f"--file={backup_file}"]
    
    logger.info(f"Creating backup: {backup_file}")
    
    try:
        # Run the pg_dump command
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info(f"Backup created successfully: {backup_file}")
        return backup_file
    except subprocess.CalledProcessError as e:
        logger.error(f"Error creating backup: {str(e)}")
        if e.stderr:
            logger.error(f"Error details: {e.stderr.decode()}")
        raise


def restore_backup(
    backup_file: Path,
    db_name: Optional[str] = None,
    db_user: Optional[str] = None,
    db_host: Optional[str] = None,
    db_port: Optional[str] = None,
) -> bool:
    """
    Restore a database from a backup file.
    
    Args:
        backup_file: Path to the backup file
        db_name: Optional database name, defaults to settings.DB_DATABASE
        db_user: Optional database user, defaults to settings.DB_USERNAME
        db_host: Optional database host, defaults to settings.DB_HOST
        db_port: Optional database port, defaults to settings.DB_PORT
        
    Returns:
        True if the restore was successful, False otherwise
    """
    # Check if the backup file exists
    if not backup_file.exists():
        logger.error(f"Backup file not found: {backup_file}")
        return False
    
    # Use default values if not provided
    db_name = db_name or settings.DB_DATABASE
    db_user = db_user or settings.DB_USERNAME
    db_host = db_host or settings.DB_HOST
    db_port = db_port or settings.DB_PORT
    
    logger.info(f"Restoring backup from {backup_file} to database {db_name}")
    
    try:
        # Determine if the backup is compressed
        is_compressed = str(backup_file).endswith(".gz")
        
        if is_compressed:
            # Use zcat to decompress the backup and pipe it to psql
            cmd = f"zcat {backup_file} | psql --dbname={db_name} --username={db_user} --host={db_host} --port={db_port}"
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
        else:
            # Use psql directly for uncompressed backups
            cmd = [
                "psql",
                f"--dbname={db_name}",
                f"--username={db_user}",
                f"--host={db_host}",
                f"--port={db_port}",
                f"--file={backup_file}",
            ]
            subprocess.run(cmd, check=True, capture_output=True)
        
        logger.info(f"Backup restored successfully from {backup_file}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error restoring backup: {str(e)}")
        if e.stderr:
            logger.error(f"Error details: {e.stderr.decode()}")
        return False


def list_backups(backup_dir: Optional[Path] = None) -> List[Path]:
    """
    List all available backup files.
    
    Args:
        backup_dir: Optional backup directory path, defaults to DEFAULT_BACKUP_DIR
        
    Returns:
        A list of paths to backup files, sorted by modification time (newest first)
    """
    # Ensure the backup directory exists
    backup_dir = ensure_backup_directory(backup_dir)
    
    # Find all backup files
    backup_files = list(backup_dir.glob("*.sql*"))
    
    # Sort by modification time (newest first)
    backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    return backup_files


def setup_scheduled_backups():
    """
    Set up scheduled backups using a cron job.
    This should be called during application startup.
    """
    # This is a placeholder for setting up scheduled backups
    # In a production environment, you would typically use a task scheduler
    # like cron, systemd timers, or a job scheduler within the application
    
    logger.info("Setting up scheduled backups (placeholder)")
    
    # Example implementation:
    # 1. Create a backup script that calls this module
    # 2. Add a cron job to run the script at the desired schedule
    # 3. Log the backup results
