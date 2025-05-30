"""
Seed Command Line Interface

This module provides a command-line interface for managing seed data.
It allows users to seed the database with initial data for different environments.
"""

import argparse
import asyncio
import sys
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.db.seed.manager import SeedEnvironment, SeedManager
from app.db.session import async_session_maker

# Configure logging
configure_logging()
logger = get_logger(__name__)


async def run_seed(
    environment: str = settings.APP_ENV,
    reset: bool = False,
    handlers: Optional[List[str]] = None,
) -> Dict[str, bool]:
    """
    Run the seed process.
    
    Args:
        environment: The environment to seed for
        reset: Whether to reset existing data before seeding
        handlers: Optional list of specific handlers to run
        
    Returns:
        A dictionary of handler names and their success status
    """
    # Convert environment string to enum
    env = SeedEnvironment(environment)
    
    logger.info(f"Starting seed process for environment: {env.value}")
    
    # Create a database session
    async with async_session_maker() as session:
        session: AsyncSession = session
        
        # Run the seed process
        results = await SeedManager.seed_database(session, env, reset)
        
        # Log results
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        if total_count > 0:
            logger.info(f"Seed process completed: {success_count}/{total_count} handlers successful")
        else:
            logger.warning(f"No seed handlers were run for environment: {env.value}")
        
        return results


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Seed the database with initial data")
    
    parser.add_argument(
        "--env",
        "-e",
        choices=[e.value for e in SeedEnvironment],
        default=settings.APP_ENV,
        help=f"Environment to seed (default: {settings.APP_ENV})",
    )
    
    parser.add_argument(
        "--reset",
        "-r",
        action="store_true",
        help="Reset existing data before seeding",
    )
    
    parser.add_argument(
        "--handler",
        "-H",
        action="append",
        help="Specific handler(s) to run (can be specified multiple times)",
    )
    
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List available seed handlers for the specified environment",
    )
    
    return parser.parse_args()


async def main_async() -> int:
    """
    Async entry point for the CLI.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    args = parse_args()
    
    # Validate environment
    try:
        env = SeedEnvironment(args.env)
    except ValueError:
        logger.error(f"Invalid environment: {args.env}")
        return 1
    
    # List handlers if requested
    if args.list:
        handlers = SeedManager.get_handlers(env)
        
        if not handlers:
            logger.info(f"No seed handlers available for environment: {env.value}")
        else:
            logger.info(f"Available seed handlers for environment {env.value}:")
            
            for handler in handlers:
                logger.info(f"  - {handler.__name__} (priority: {handler.priority})")
        
        return 0
    
    # Run seed process
    results = await run_seed(args.env, args.reset, args.handler)
    
    # Determine exit code based on results
    if not results:
        logger.warning("No seed handlers were run")
        return 0
    
    # Return success if all handlers succeeded
    return 0 if all(results.values()) else 1


def main() -> int:
    """
    Entry point for the CLI.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        return asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("Seed process interrupted")
        return 130  # Standard exit code for SIGINT
    except Exception as e:
        logger.exception(f"Unhandled error in seed process: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
