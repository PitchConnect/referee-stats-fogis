"""File utility functions for the referee stats application."""

import csv
import json
from pathlib import Path
from typing import Any


def read_csv(file_path: str | Path) -> list[dict[str, str]]:
    """Read a CSV file and return a list of dictionaries.

    Args:
        file_path: Path to the CSV file

    Returns:
        List of dictionaries, where each dictionary represents a row in the CSV file
    """
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_csv(
    file_path: str | Path,
    data: list[dict[str, Any]],
    fieldnames: list[str] | None = None,
) -> None:
    """Write a list of dictionaries to a CSV file.

    Args:
        file_path: Path to the CSV file
        data: List of dictionaries to write
        fieldnames: List of field names to use as headers. If None, uses the keys of the
            first dictionary.
    """
    if not data:
        return

    if fieldnames is None:
        fieldnames = list(data[0].keys())

    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def read_json(file_path: str | Path) -> Any:
    """Read a JSON file and return the parsed data.

    Args:
        file_path: Path to the JSON file

    Returns:
        Parsed JSON data
    """
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


def write_json(file_path: str | Path, data: Any, indent: int = 2) -> None:
    """Write data to a JSON file.

    Args:
        file_path: Path to the JSON file
        data: Data to write
        indent: Number of spaces to use for indentation
    """
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
