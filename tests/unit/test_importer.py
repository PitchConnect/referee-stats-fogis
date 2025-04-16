"""Tests for data import functionality."""

import json
import os
import tempfile
from unittest.mock import MagicMock

import pytest

from referee_stats_fogis.core.importer import DataImporter
from referee_stats_fogis.data.database import Database


@pytest.fixture
def mock_db() -> MagicMock:
    """Create a mock database."""
    return MagicMock(spec=Database)


@pytest.fixture
def importer(mock_db: MagicMock) -> DataImporter:
    """Create a data importer with a mock database."""
    return DataImporter(mock_db)


def test_import_from_csv(importer: DataImporter) -> None:
    """Test importing data from a CSV file."""
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
        temp_file.write(b"name,age,city\nJohn,30,New York\nJane,25,Boston\n")
        temp_path = temp_file.name

    try:
        # Import the data
        record_count = importer.import_from_csv(temp_path)

        # Check the result
        assert record_count == 2
    finally:
        # Clean up
        os.unlink(temp_path)


def test_import_from_json_list(importer: DataImporter) -> None:
    """Test importing data from a JSON file containing a list."""
    # Create a temporary JSON file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
        data = [
            {"name": "John", "age": 30, "city": "New York"},
            {"name": "Jane", "age": 25, "city": "Boston"},
        ]
        temp_file.write(json.dumps(data).encode("utf-8"))
        temp_path = temp_file.name

    try:
        # Import the data
        record_count = importer.import_from_json(temp_path)

        # Check the result
        assert record_count == 2
    finally:
        # Clean up
        os.unlink(temp_path)


def test_import_from_json_dict(importer: DataImporter) -> None:
    """Test importing data from a JSON file containing a dictionary."""
    # Create a temporary JSON file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
        data = {"name": "John", "age": 30, "city": "New York"}
        temp_file.write(json.dumps(data).encode("utf-8"))
        temp_path = temp_file.name

    try:
        # Import the data
        record_count = importer.import_from_json(temp_path)

        # Check the result
        assert record_count == 1
    finally:
        # Clean up
        os.unlink(temp_path)
