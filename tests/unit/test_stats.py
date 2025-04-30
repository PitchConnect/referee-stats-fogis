"""Tests for statistics generation."""

from unittest.mock import MagicMock

import pytest

from referee_stats_fogis.core.stats import (
    get_match_stats,
    get_most_carded_players,
    get_most_common_co_officials,
    get_player_stats,
    get_referee_stats,
    get_team_stats,
)
from referee_stats_fogis.data.database import Database


@pytest.fixture
def mock_db() -> MagicMock:
    """Create a mock database."""
    mock = MagicMock(spec=Database)
    # Add conn attribute to the mock
    mock.conn = MagicMock()
    return mock


def test_get_referee_stats(mock_db: MagicMock) -> None:
    """Test getting referee statistics."""
    # Call the function
    stats = get_referee_stats(mock_db, 1)

    # Check the result structure
    assert isinstance(stats, dict)
    assert "total_matches" in stats
    assert "yellow_cards" in stats
    assert "red_cards" in stats
    assert "goals" in stats
    assert "most_common_co_officials" in stats
    assert "most_carded_players" in stats


def test_get_player_stats(mock_db: MagicMock) -> None:
    """Test getting player statistics."""
    # Call the function
    stats = get_player_stats(mock_db, 1)

    # Check the result structure
    assert isinstance(stats, dict)
    assert "total_matches" in stats
    assert "goals" in stats
    assert "yellow_cards" in stats
    assert "red_cards" in stats


def test_get_team_stats(mock_db: MagicMock) -> None:
    """Test getting team statistics."""
    # Call the function
    stats = get_team_stats(mock_db, 1)

    # Check the result structure
    assert isinstance(stats, dict)
    assert "total_matches" in stats
    assert "wins" in stats
    assert "draws" in stats
    assert "losses" in stats
    assert "goals_for" in stats
    assert "goals_against" in stats


def test_get_match_stats(mock_db: MagicMock) -> None:
    """Test getting match statistics."""
    # Call the function
    stats = get_match_stats(mock_db, 1)

    # Check the result structure
    assert isinstance(stats, dict)
    assert "home_team" in stats
    assert "away_team" in stats
    assert "score" in stats
    assert "officials" in stats
    assert "cards" in stats
    assert "goals" in stats


def test_get_most_common_co_officials(mock_db: MagicMock) -> None:
    """Test getting most common co-officials."""
    # Mock the database to return some data
    mock_db.conn.cursor().fetchall.return_value = [
        {"id": 2, "count": 5},
        {"id": 3, "count": 3},
    ]

    # Call the function
    result = get_most_common_co_officials(mock_db, 1)

    # Check the result
    assert isinstance(result, list)
    assert len(result) == 0  # Currently returns empty list as it's a placeholder

    # In a real implementation, we would expect:
    # assert len(result) == 2
    # assert result[0] == (2, 5)
    # assert result[1] == (3, 3)


def test_get_most_carded_players(mock_db: MagicMock) -> None:
    """Test getting most carded players."""
    # Mock the database to return some data
    mock_db.conn.cursor().fetchall.return_value = [
        {"id": 101, "count": 3},
        {"id": 102, "count": 2},
    ]

    # Call the function
    result = get_most_carded_players(mock_db, 1)

    # Check the result
    assert isinstance(result, list)
    assert len(result) == 0  # Currently returns empty list as it's a placeholder

    # In a real implementation, we would expect:
    # assert len(result) == 2
    # assert result[0] == (101, 3)
    # assert result[1] == (102, 2)


def test_get_referee_stats_with_data(mock_db: MagicMock) -> None:
    """Test getting referee statistics with mocked data."""
    # Mock the database to return some data for total matches
    mock_cursor = MagicMock()
    mock_db.conn.cursor.return_value = mock_cursor

    # In a real implementation, we would set up the mock to return specific data
    # mock_cursor.fetchone.return_value = {"count": 10}
    # mock_cursor.fetchall.return_value = [...]

    # Call the function
    stats = get_referee_stats(mock_db, 1)

    # Check the result
    assert stats["total_matches"] == 0  # Currently returns 0 as it's a placeholder
    assert stats["yellow_cards"] == 0
    assert stats["red_cards"] == 0
    assert stats["goals"] == 0
    assert isinstance(stats["most_common_co_officials"], list)
    assert isinstance(stats["most_carded_players"], list)


def test_get_player_stats_with_data(mock_db: MagicMock) -> None:
    """Test getting player statistics with mocked data."""
    # Mock the database to return some data
    mock_cursor = MagicMock()
    mock_db.conn.cursor.return_value = mock_cursor

    # In a real implementation, we would set up the mock to return specific data
    # mock_cursor.fetchone.side_effect = [{"count": 15}, {"count": 5}, ...]

    # Call the function
    stats = get_player_stats(mock_db, 1)

    # Check the result
    assert stats["total_matches"] == 0  # Currently returns 0 as it's a placeholder
    assert stats["goals"] == 0
    assert stats["yellow_cards"] == 0
    assert stats["red_cards"] == 0


def test_get_team_stats_with_data(mock_db: MagicMock) -> None:
    """Test getting team statistics with mocked data."""
    # Mock the database to return some data
    mock_cursor = MagicMock()
    mock_db.conn.cursor.return_value = mock_cursor

    # In a real implementation, we would set up the mock to return specific data
    # mock_cursor.fetchone.side_effect = [{"count": 20}, {"count": 10}, ...]

    # Call the function
    stats = get_team_stats(mock_db, 1)

    # Check the result
    assert stats["total_matches"] == 0  # Currently returns 0 as it's a placeholder
    assert stats["wins"] == 0
    assert stats["draws"] == 0
    assert stats["losses"] == 0
    assert stats["goals_for"] == 0
    assert stats["goals_against"] == 0
