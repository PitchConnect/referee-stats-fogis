"""Database management utilities."""

import os
import subprocess
from pathlib import Path
from typing import List, Optional

from referee_stats_fogis.config import config
from referee_stats_fogis.data.base import get_engine, init_db
from referee_stats_fogis.data.init_data import init_all


def create_database() -> None:
    """Create the database and initialize it with tables and default data."""
    # Initialize the database
    init_db()
    print("Database schema created")

    # Initialize default data
    init_all()


def run_migrations(revision: str | None = None) -> None:
    """Run database migrations.

    Args:
        revision: Specific revision to migrate to. If None, migrates to the latest
            revision.
    """
    cmd = ["alembic", "upgrade"]
    if revision:
        cmd.append(revision)
    else:
        cmd.append("head")

    subprocess.run(cmd, check=True)
    print(f"Migrations applied successfully{' to ' + revision if revision else ''}")


def create_migration(message: str) -> None:
    """Create a new migration.

    Args:
        message: Migration message
    """
    cmd = ["alembic", "revision", "--autogenerate", "-m", message]
    subprocess.run(cmd, check=True)
    print(f"Migration created: {message}")


def get_migration_history() -> list[str]:
    """Get the migration history.

    Returns:
        List of migration revisions
    """
    result = subprocess.run(
        ["alembic", "history"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip().split("\n")


def reset_database() -> None:
    """Reset the database by dropping all tables and recreating them."""
    # Get the database path
    db_type = config.get("database.type", "sqlite")
    if db_type == "sqlite":
        db_path = config.get("database.path", "data/referee_stats.db")
        # Delete the file if it exists
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"Deleted database file: {db_path}")
    elif db_type == "postgresql":
        # For PostgreSQL, we drop and recreate all tables
        from referee_stats_fogis.data.base import Base

        engine = get_engine()
        Base.metadata.drop_all(engine)
        print("Dropped all tables")

    # Recreate the database
    create_database()
    print("Database reset complete")
