#!/usr/bin/env python
"""Example script demonstrating the data import functionality."""

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from referee_stats_fogis.core.importer import DataImporter
from referee_stats_fogis.data.base import get_session


def import_example_data() -> None:
    """Import example data from the examples directory."""
    # Get the examples directory
    examples_dir = Path(__file__).parent

    # Create a session
    session = get_session()

    # Create an importer
    with DataImporter(session=session) as importer:
        # Import match data
        match_file = examples_dir / "match.json"
        if match_file.exists():
            print(f"Importing match data from {match_file}...")
            count = importer.import_from_json(match_file)
            print(f"Imported {count} match records")

        # Import match result data
        result_file = examples_dir / "match_result.json"
        if result_file.exists():
            print(f"Importing match result data from {result_file}...")
            count = importer.import_from_json(result_file)
            print(f"Imported {count} match result records")

        # Import match event data
        event_file = examples_dir / "match_event.json"
        if event_file.exists():
            print(f"Importing match event data from {event_file}...")
            count = importer.import_from_json(event_file)
            print(f"Imported {count} match event records")

        # Import match participant data
        participant_file = examples_dir / "match_participant.json"
        if participant_file.exists():
            print(f"Importing match participant data from {participant_file}...")
            count = importer.import_from_json(participant_file)
            print(f"Imported {count} match participant records")

        # Import player data from CSV
        player_file = examples_dir / "players.csv"
        if player_file.exists():
            print(f"Importing player data from {player_file}...")
            count = importer.import_from_csv(player_file)
            print(f"Imported {count} player records")


if __name__ == "__main__":
    import_example_data()
