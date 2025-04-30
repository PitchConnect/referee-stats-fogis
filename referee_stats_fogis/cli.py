"""Command-line interface for the referee stats application."""

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

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


def _validate_file(file_path: str) -> tuple[bool, Any, str]:
    """Validate that the file exists and can be read.

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (success, data, error_message)
    """
    from referee_stats_fogis.utils.file_utils import read_csv, read_json

    if file_path.lower().endswith(".csv"):
        data = read_csv(file_path)
        if not data:
            return False, None, "CSV file is empty or could not be parsed"
        return True, data, ""
    elif file_path.lower().endswith(".json"):
        data = read_json(file_path)
        if not data:
            return False, None, "JSON file is empty or could not be parsed"
        return True, data, ""
    else:
        error_msg = f"Unsupported file format: {file_path}"
        error_msg += "\nSupported formats: .csv, .json"
        return False, None, error_msg


def _print_dry_run_info(file_path: str, data: Any) -> None:
    """Print information about the data for dry run mode.

    Args:
        file_path: Path to the file
        data: Data from the file
    """
    if file_path.lower().endswith(".csv"):
        print(f"CSV file contains {len(data)} records")
        if data and len(data) > 0:
            print("Sample fields:", list(data[0].keys()))
    elif file_path.lower().endswith(".json"):
        if isinstance(data, list):
            print(f"JSON file contains {len(data)} records")
            if data and len(data) > 0 and "__type" in data[0]:
                print(f"Data type: {data[0]['__type']}")
        elif isinstance(data, dict):
            print("JSON file contains a single record")
            if "__type" in data:
                print(f"Data type: {data['__type']}")


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

    try:
        # Validate the file
        success, data, error_message = _validate_file(args.file)
        if not success:
            print(error_message)
            return 1

        # If it's a dry run, just print some info about the data
        if args.dry_run:
            _print_dry_run_info(args.file, data)
            return 0

        # Otherwise, import the data
        from referee_stats_fogis.core.importer import DataImporter

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


def _print_list_item(i: int, item: Any) -> None:
    """Print a list item in a formatted way.

    Args:
        i: Item index
        item: The item to print
    """
    if isinstance(item, tuple):
        print(f"  {i}. {item[1]}: {item[2]}")
    elif isinstance(item, dict):
        if "name" in item and "matches" in item:
            print(f"  {i}. {item['name']}: {item['matches']} matches")
        elif "name" in item and "goals" in item:
            print(f"  {i}. {item['name']}: {item['goals']} goals")
        elif "player" in item and "type" in item:
            print(
                f"  {i}. {item['player']} ({item['team']}): "
                f"{item['type']} at {item['minute']}'"
            )
        elif "scorer" in item:
            penalty = " (penalty)" if item.get("is_penalty") else ""
            print(
                f"  {i}. {item['scorer']} ({item['team']}): "
                f"{item['minute']}'{penalty}"
            )
        elif "name" in item and "role" in item:
            print(f"  {i}. {item['name']} ({item['role']})")
        else:
            print(f"  {i}. {item}")
    else:
        print(f"  {i}. {item}")


def _print_stats_text(stats: dict[str, Any]) -> None:
    """Print statistics in text format.

    Args:
        stats: Statistics dictionary
    """
    print("\nStatistics:")
    for key, value in stats.items():
        if isinstance(value, list):
            print(f"\n{key.replace('_', ' ').title()}:")
            if not value:
                print("  None")
            else:
                for i, item in enumerate(value, 1):
                    _print_list_item(i, item)
        else:
            print(f"{key.replace('_', ' ').title()}: {value}")


def stats_command(args: argparse.Namespace) -> int:
    """Generate statistics.

    Args:
        args: Command-line arguments

    Returns:
        Exit code
    """
    print(f"Generating statistics for {args.type}")

    try:
        import json

        from referee_stats_fogis.core.stats import (
            get_match_stats,
            get_player_stats,
            get_referee_stats,
            get_team_stats,
        )
        from referee_stats_fogis.data.database import Database

        # Create a database connection
        db = Database()

        # Get the ID
        entity_id = args.id

        # Generate the appropriate statistics
        if args.type == "referee":
            stats = get_referee_stats(db, entity_id)
        elif args.type == "player":
            stats = get_player_stats(db, entity_id)
        elif args.type == "team":
            stats = get_team_stats(db, entity_id)
        elif args.type == "match":
            stats = get_match_stats(db, entity_id)
        else:
            print(f"Unknown statistics type: {args.type}")
            return 1

        # Print the statistics
        if args.format == "json":
            print(json.dumps(stats, indent=2))
        else:  # text format
            _print_stats_text(stats)

        return 0
    except Exception as e:
        print(f"Error generating statistics: {e}")
        import traceback

        traceback.print_exc()
        return 1


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
        help="Type of data being imported (auto-detected from JSON if not specified)",
    )
    import_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse the file but don't modify the database",
    )
    import_parser.set_defaults(func=import_command)

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Generate statistics")
    stats_parser.add_argument(
        "type",
        choices=["referee", "player", "team", "match"],
        help="Type of statistics to generate",
    )
    stats_parser.add_argument(
        "id",
        type=int,
        help="ID of the entity to generate statistics for",
    )
    stats_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
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
