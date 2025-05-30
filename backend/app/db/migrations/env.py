"""
Alembic Migration Environment

This module sets up the environment for database migrations using Alembic.
It connects to the database and provides the context for migrations.
"""

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Import application modules
from app.core.config import settings  # noqa
from app.db.base_model import BaseModel  # noqa
from app.db.session import Base  # noqa

# Import all models to ensure they're registered with Base
# Add all model imports here as they are created

# This is the Alembic Config object, which provides access to the values within the .ini file
config = context.config

# Override the SQLAlchemy URL with our application's database URI
config.set_main_option('sqlalchemy.url', settings.DATABASE_URI)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the target metadata for Alembic
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    
    This configures the context with just a URL and not an Engine, though an Engine
    is acceptable here as well. By skipping the Engine creation we don't even need 
    a DBAPI to be available.
    
    Calls to context.execute() here emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    
    In this scenario we need to create an Engine and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            # Compare_type compares column types and upgrades them if changed
            compare_type=True,
            # Include schema name in table creation
            include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# Run the appropriate migration function
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
