"""Alembic environment configuration.

Imports all SQLAlchemy models from app.models to ensure Alembic's autogenerate
can detect schema changes. Reads the database URL from app.config.Settings
to override the static alembic.ini value.
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection, engine_from_config, pool

from app.config import settings

# Import the declarative base that all models inherit from.
# This must be imported BEFORE individual model modules so the
# MetaData object has all table definitions registered.
from app.models.base import Base

# Import ALL model modules so their table definitions are registered
# on Base.metadata. Alembic autogenerate will not detect tables from
# models that have not been imported.
import app.models.project  # noqa: F401 — registers Opportunity, Outcome, OpportunityMetricTimeSeries
import app.models.dependency  # noqa: F401 — registers SelectionDependency, SelectionGroup, GroupMember
import app.models.scenario  # noqa: F401 — registers Scenario, ScenarioInput, ScenarioResult
import app.models.price_deck  # noqa: F401 — registers PriceDeck, MasterDataSet, MasterDataMetric
import app.models.constraint  # noqa: F401 — registers SelectionConstraint, MetricConstraint
import app.models.expression  # noqa: F401 — registers MetricExpression
import app.models.optimization_result  # noqa: F401 — registers OptimizationResult (TimescaleDB)
import app.models.user  # noqa: F401 — registers User

# Alembic Config object — provides access to values in alembic.ini
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the target metadata for autogenerate support
target_metadata = Base.metadata

# Override sqlalchemy.url from application settings
config.set_main_option("sqlalchemy.url", settings.database_url_sync)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Configures the context with just a URL and not an Engine.
    Calls to context.execute() emit the given string to the script output.
    This is useful for generating SQL scripts without a live database.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Execute migrations with a given connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Creates an Engine and associates a connection with the context.
    Uses synchronous psycopg2 driver for Alembic compatibility.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
