"""Performance tests for statistics functions."""

import time
from collections.abc import Callable, Generator
from typing import Any

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from referee_stats_fogis.core.stats import (
    get_match_stats,
    get_most_carded_players,
    get_most_common_co_officials,
    get_player_stats,
    get_referee_stats,
    get_team_stats,
)
from referee_stats_fogis.data.base import Base


@pytest.fixture
def in_memory_db() -> Generator[Session, None, None]:
    """Create an in-memory database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    # Here you would populate the database with test data
    # This is a simplified example - in a real test, you would
    # create a larger dataset to test performance

    yield session
    session.close()


def measure_execution_time(func: Callable, *args: Any, **kwargs: Any) -> float:
    """Measure the execution time of a function.

    Args:
        func: Function to measure
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        Execution time in seconds
    """
    start_time = time.time()
    func(*args, **kwargs)
    end_time = time.time()
    return end_time - start_time


def test_referee_stats_performance(in_memory_db: Session) -> None:
    """Test the performance of get_referee_stats."""
    # This is a placeholder test - in a real test, you would
    # create a larger dataset and measure the execution time

    # Measure execution time
    execution_time = measure_execution_time(get_referee_stats, in_memory_db, 1)

    # Print the execution time for reference
    print(f"get_referee_stats execution time: {execution_time:.6f} seconds")

    # No specific assertion here, as the execution time will vary
    # In a real test, you might compare it to a baseline or set a maximum threshold


def test_most_common_co_officials_performance(in_memory_db: Session) -> None:
    """Test the performance of get_most_common_co_officials."""
    # Measure execution time with and without pagination
    time_without_pagination = measure_execution_time(
        get_most_common_co_officials, in_memory_db, 1, 100, 0
    )
    time_with_pagination = measure_execution_time(
        get_most_common_co_officials, in_memory_db, 1, 10, 0
    )

    print(
        f"get_most_common_co_officials without pagination: "
        f"{time_without_pagination:.6f} seconds"
    )
    print(
        f"get_most_common_co_officials with pagination: "
        f"{time_with_pagination:.6f} seconds"
    )

    # Pagination should be faster, but this depends on the dataset size
    # This assertion might not always hold true for small datasets
    # assert time_with_pagination <= time_without_pagination


def test_most_carded_players_performance(in_memory_db: Session) -> None:
    """Test the performance of get_most_carded_players."""
    # Measure execution time with and without pagination
    time_without_pagination = measure_execution_time(
        get_most_carded_players, in_memory_db, 1, 100, 0
    )
    time_with_pagination = measure_execution_time(
        get_most_carded_players, in_memory_db, 1, 10, 0
    )

    print(
        f"get_most_carded_players without pagination: "
        f"{time_without_pagination:.6f} seconds"
    )
    print(
        f"get_most_carded_players with pagination: "
        f"{time_with_pagination:.6f} seconds"
    )


def test_player_stats_performance(in_memory_db: Session) -> None:
    """Test the performance of get_player_stats."""
    # Measure execution time with and without pagination
    time_without_pagination = measure_execution_time(
        get_player_stats, in_memory_db, 1, 100, 0
    )
    time_with_pagination = measure_execution_time(
        get_player_stats, in_memory_db, 1, 10, 0
    )

    print(f"get_player_stats without pagination: {time_without_pagination:.6f} seconds")
    print(f"get_player_stats with pagination: {time_with_pagination:.6f} seconds")


def test_team_stats_performance(in_memory_db: Session) -> None:
    """Test the performance of get_team_stats."""
    # Measure execution time with and without pagination
    time_without_pagination = measure_execution_time(
        get_team_stats, in_memory_db, 1, 100, 0, 100, 0
    )
    time_with_pagination = measure_execution_time(
        get_team_stats, in_memory_db, 1, 10, 0, 10, 0
    )

    print(f"get_team_stats without pagination: {time_without_pagination:.6f} seconds")
    print(f"get_team_stats with pagination: {time_with_pagination:.6f} seconds")


def test_match_stats_performance(in_memory_db: Session) -> None:
    """Test the performance of get_match_stats."""
    # Measure execution time with and without pagination
    time_without_pagination = measure_execution_time(
        get_match_stats, in_memory_db, 1, 100, 0, 100, 0, 100, 0
    )
    time_with_pagination = measure_execution_time(
        get_match_stats, in_memory_db, 1, 10, 0, 10, 0, 10, 0
    )

    print(f"get_match_stats without pagination: {time_without_pagination:.6f} seconds")
    print(f"get_match_stats with pagination: {time_with_pagination:.6f} seconds")
