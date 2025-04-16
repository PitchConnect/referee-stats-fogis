"""Tests for file utility functions."""

import json
import os
import tempfile

from referee_stats_fogis.utils.file_utils import (
    read_csv,
    read_json,
    write_csv,
    write_json,
)


def test_csv_read_write() -> None:
    """Test reading and writing CSV files."""
    # Test data
    data = [
        {"name": "John", "age": "30", "city": "New York"},
        {"name": "Jane", "age": "25", "city": "Boston"},
        {"name": "Bob", "age": "40", "city": "Chicago"},
    ]

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
        temp_path = temp_file.name

    try:
        # Write data to the file
        write_csv(temp_path, data)

        # Read data from the file
        read_data = read_csv(temp_path)

        # Check that the data is the same
        assert len(read_data) == len(data)
        for i, row in enumerate(read_data):
            assert row["name"] == data[i]["name"]
            assert row["age"] == data[i]["age"]
            assert row["city"] == data[i]["city"]
    finally:
        # Clean up
        os.unlink(temp_path)


def test_json_read_write() -> None:
    """Test reading and writing JSON files."""
    # Test data
    data = {
        "name": "John",
        "age": 30,
        "address": {"street": "123 Main St", "city": "New York", "zip": "10001"},
        "phones": ["555-1234", "555-5678"],
    }

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
        temp_path = temp_file.name

    try:
        # Write data to the file
        write_json(temp_path, data)

        # Read data from the file
        read_data = read_json(temp_path)

        # Check that the data is the same
        assert read_data == data

        # Check the file content directly
        with open(temp_path, encoding="utf-8") as f:
            file_content = f.read()
            # Check that the file is properly formatted
            assert json.loads(file_content) == data
    finally:
        # Clean up
        os.unlink(temp_path)
