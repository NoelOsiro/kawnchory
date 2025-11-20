"""Alembic environment configuration for database migrations.

This module configures the Alembic context, ensures a synchronous
SQLAlchemy URL is available when an async driver is used, and imports
the project's metadata for autogeneration of migration scripts.
"""

from __future__ import annotations

import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context

# add project path so we can import agent.services.config_store
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# this is the Alembic Config object, which provides access to the values
# within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import metadata from our models
try:
    from agent.services.config_store import Base
    target_metadata = Base.metadata
except Exception:
    target_metadata = None

# Provide a synchronous URL for Alembic if an async URL is present
def _sqla_url_from_env():
    url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    if not url:
        return url
    # Convert async drivers to sync equivalents for migrations
    if url.startswith("sqlite+aiosqlite://"):
        return url.replace("sqlite+aiosqlite://", "sqlite://")
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    if url.startswith("mysql+asyncmy://"):
        return url.replace("mysql+asyncmy://", "mysql+pymysql://")
    return url

# other values from the config, defined by the needs of env.py, can be acquired:
config.set_main_option("sqlalchemy.url", _sqla_url_from_env() or config.get_main_option("sqlalchemy.url"))


def run_migrations_offline():
    """Run migrations in "offline" mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable here as well.
    By skipping the Engine creation we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in "online" mode.

    In this scenario we need to create an Engine and associate a connection with the context.
    """
    connectable = create_engine(config.get_main_option("sqlalchemy.url"), poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
