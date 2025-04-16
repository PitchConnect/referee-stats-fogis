"""Tests for statistics generation."""

from unittest.mock import MagicMock

import pytest

from referee_stats_fogis.core.stats import (
    get_match_stats,
    get_player_stats,
    get_referee_stats,
    get_team_stats,
)
from referee_stats_fogis.data.database import Database


@pytest.fixture
def mock_db() -> MagicMock:
    """Create a mock database."""
    return MagicMock(spec=Database)


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
