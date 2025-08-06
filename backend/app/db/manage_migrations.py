"""
Migration Management Script

This script provides a command-line interface for managing database migrations.
It can be used to create, apply, and roll back migrations.
"""

import argparse
import sys
from typing import List, Optional

from app.core.logging import configure_logging, get_logger
from app.db.migrations.helpers import (
    create_migration,
    downgrade_database,
    get_current_revision,
    get_migration_history,
    init_migration_environment,
    upgrade_database,
)

# Configure logging
configure_logging()
logger = get_logger(__name__)


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments for the migration management script.
    
    Args:
        args: Command-line arguments (defaults to sys.argv[1:])
        
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Manage database migrations")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Initialize command
    init_parser = subparsers.add_parser("init", help="Initialize migration environment")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new migration")
    create_parser.add_argument("message", help="Migration message/description")
    
    # Upgrade command
    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade database to a revision")
    upgrade_parser.add_argument("--revision", default="head", help="Revision to upgrade to (default: head)")
    
    # Downgrade command
    downgrade_parser = subparsers.add_parser("downgrade", help="Downgrade database to a revision")
    downgrade_parser.add_argument("revision", help="Revision to downgrade to")
    
    # Current command
    subparsers.add_parser("current", help="Show current database revision")
    
    # History command
    subparsers.add_parser("history", help="Show migration history")
    
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the migration management script.
    
    Args:
        args: Command-line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parsed_args = parse_args(args)
    
    try:
        if parsed_args.command == "init":
            init_migration_environment()
            print("Migration environment initialized")
            
        elif parsed_args.command == "create":
            output = create_migration(parsed_args.message)
            print(output)
            
        elif parsed_args.command == "upgrade":
            output = upgrade_database(parsed_args.revision)
            print(output)
            
        elif parsed_args.command == "downgrade":
            output = downgrade_database(parsed_args.revision)
            print(output)
            
        elif parsed_args.command == "current":
            output = get_current_revision()
            print(f"Current revision: {output}")
            
        elif parsed_args.command == "history":
            output = get_migration_history()
            print(output)
            
        else:
            print("No command specified")
            return 1
            
        return 0
        
    except Exception as e:
        logger.exception(f"Error running migration command: {e}")
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
