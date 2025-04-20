"""Command-line interface for the referee stats application."""

import argparse
import logging
import sys
from pathlib import Path

from referee_stats_fogis.config import config


def setup_logging() -> None:
    """Set up logging for the application."""
    log_level = getattr(logging, config.get("logging.level", "INFO"))
    log_file = config.get("logging.file")

    # Ensure log directory exists
    if log_file:
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file) if log_file else logging.NullHandler(),
            logging.StreamHandler(),
        ],
    )


def import_command(args: argparse.Namespace) -> int:
    """Import data from a file.

    Args:
        args: Command-line arguments

    Returns:
        Exit code
    """
    print(f"Importing data from {args.file}")

    if args.dry_run:
        print("Dry run mode: No changes will be made to the database")

    from referee_stats_fogis.core.importer import DataImporter
    from referee_stats_fogis.utils.file_utils import read_json, read_csv

    try:
        # First check if the file exists and can be read
        if args.file.lower().endswith(".csv"):
            data = read_csv(args.file)
            if not data:
                print("CSV file is empty or could not be parsed")
                return 1
        elif args.file.lower().endswith(".json"):
            data = read_json(args.file)
            if not data:
                print("JSON file is empty or could not be parsed")
                return 1
        else:
            print(f"Unsupported file format: {args.file}")
            print("Supported formats: .csv, .json")
            return 1

        # If it's a dry run, just print some info about the data
        if args.dry_run:
            if args.file.lower().endswith(".csv"):
                print(f"CSV file contains {len(data)} records")
                if data and len(data) > 0:
                    print("Sample fields:", list(data[0].keys()))
            elif args.file.lower().endswith(".json"):
                if isinstance(data, list):
                    print(f"JSON file contains {len(data)} records")
                    if data and len(data) > 0 and "__type" in data[0]:
                        print(f"Data type: {data[0]['__type']}")
                elif isinstance(data, dict):
                    print("JSON file contains a single record")
                    if "__type" in data:
                        print(f"Data type: {data['__type']}")
            return 0

        # Otherwise, import the data
        with DataImporter() as importer:
            if args.file.lower().endswith(".csv"):
                count = importer.import_from_csv(args.file)
            elif args.file.lower().endswith(".json"):
                count = importer.import_from_json(args.file)

            print(f"Successfully imported {count} records")
            return 0
    except Exception as e:
        print(f"Error importing data: {e}")
        import traceback
        traceback.print_exc()
        return 1


def stats_command(args: argparse.Namespace) -> int:
    """Generate statistics.

    Args:
        args: Command-line arguments

    Returns:
        Exit code
    """
    print(f"Generating statistics for {args.type}")
    # Implementation would go here
    return 0


def init_db_command(args: argparse.Namespace) -> int:
    """Initialize the database.

    Args:
        args: Command-line arguments

    Returns:
        Exit code
    """
    print("Initializing database...")
    from referee_stats_fogis.data.db_manager import create_database

    create_database()
    return 0


def migrate_db_command(args: argparse.Namespace) -> int:
    """Run database migrations.

    Args:
        args: Command-line arguments

    Returns:
        Exit code
    """
    from referee_stats_fogis.data.db_manager import run_migrations

    revision = args.revision if hasattr(args, "revision") else None
    run_migrations(revision)
    return 0


def create_migration_command(args: argparse.Namespace) -> int:
    """Create a new database migration.

    Args:
        args: Command-line arguments

    Returns:
        Exit code
    """
    from referee_stats_fogis.data.db_manager import create_migration

    create_migration(args.message)
    return 0


def reset_db_command(args: argparse.Namespace) -> int:
    """Reset the database.

    Args:
        args: Command-line arguments

    Returns:
        Exit code
    """
    if (
        not args.force
        and input(
            "Are you sure you want to reset the database? "
            "This will delete all data. (y/N) "
        ).lower()
        != "y"
    ):
        print("Database reset cancelled.")
        return 0

    from referee_stats_fogis.data.db_manager import reset_database

    reset_database()
    return 0


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the application.

    Args:
        argv: Command-line arguments

    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(description="Referee Stats FOGIS")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Import command
    import_parser = subparsers.add_parser("import", help="Import data from FOGIS")
    import_parser.add_argument("file", help="File to import (CSV or JSON)")
    import_parser.add_argument(
        "--type",
        choices=["match", "results", "events", "players", "team-staff"],
        help="Specify the type of data being imported (optional, auto-detected from JSON content)"
    )
    import_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse the file but don't modify the database"
    )
    import_parser.set_defaults(func=import_command)

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Generate statistics")
    stats_parser.add_argument(
        "type",
        choices=["referee", "player", "team", "match"],
        help="Type of statistics to generate",
    )
    stats_parser.set_defaults(func=stats_command)

    # Database commands
    db_subparsers = subparsers.add_parser("db", help="Database operations")
    db_commands = db_subparsers.add_subparsers(
        dest="db_command", help="Database command to run"
    )

    # Init DB command
    init_db_parser = db_commands.add_parser("init", help="Initialize the database")
    init_db_parser.set_defaults(func=init_db_command)

    # Migrate DB command
    migrate_db_parser = db_commands.add_parser(
        "migrate", help="Run database migrations"
    )
    migrate_db_parser.add_argument("--revision", help="Specific revision to migrate to")
    migrate_db_parser.set_defaults(func=migrate_db_command)

    # Create Migration command
    create_migration_parser = db_commands.add_parser(
        "create-migration", help="Create a new database migration"
    )
    create_migration_parser.add_argument("message", help="Migration message")
    create_migration_parser.set_defaults(func=create_migration_command)

    # Reset DB command
    reset_db_parser = db_commands.add_parser("reset", help="Reset the database")
    reset_db_parser.add_argument(
        "--force", action="store_true", help="Force reset without confirmation"
    )
    reset_db_parser.set_defaults(func=reset_db_command)

    args = parser.parse_args(argv)

    # Set up logging
    setup_logging()

    # Run the command
    if hasattr(args, "func"):
        return_code: int = args.func(args)
        return return_code
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
