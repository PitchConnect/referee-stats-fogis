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
    # Mock the session query chain
    mock_query = MagicMock()
    mock_db._get_session = MagicMock(return_value=mock_db)
    mock_db.query = MagicMock(return_value=mock_query)
    mock_query.join = MagicMock(return_value=mock_query)
    mock_query.filter = MagicMock(return_value=mock_query)
    mock_query.subquery = MagicMock(return_value="subquery")

    # Mock the co-officials query chain
    mock_officials_query = MagicMock()
    mock_db.query = MagicMock(return_value=mock_officials_query)
    mock_officials_query.join = MagicMock(return_value=mock_officials_query)
    mock_officials_query.filter = MagicMock(return_value=mock_officials_query)
    mock_officials_query.group_by = MagicMock(return_value=mock_officials_query)
    mock_officials_query.order_by = MagicMock(return_value=mock_officials_query)
    mock_officials_query.limit = MagicMock(return_value=mock_officials_query)

    # Mock the result
    mock_officials_query.all.return_value = [
        (2, "John", "Doe", 5),
        (3, "Jane", "Smith", 3),
    ]

    # Call the function
    result = get_most_common_co_officials(mock_db, 1)

    # Check the result
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0] == (2, "John Doe", 5)
    assert result[1] == (3, "Jane Smith", 3)


def test_get_most_carded_players(mock_db: MagicMock) -> None:
    """Test getting most carded players."""
    # Mock the session query chain
    mock_query = MagicMock()
    mock_db._get_session = MagicMock(return_value=mock_db)
    mock_db.query = MagicMock(return_value=mock_query)
    mock_query.join = MagicMock(return_value=mock_query)
    mock_query.filter = MagicMock(return_value=mock_query)
    mock_query.subquery = MagicMock(return_value="subquery")

    # Mock the carded players query chain
    mock_players_query = MagicMock()
    mock_db.query = MagicMock(return_value=mock_players_query)
    mock_players_query.join = MagicMock(return_value=mock_players_query)
    mock_players_query.filter = MagicMock(return_value=mock_players_query)
    mock_players_query.group_by = MagicMock(return_value=mock_players_query)
    mock_players_query.order_by = MagicMock(return_value=mock_players_query)
    mock_players_query.limit = MagicMock(return_value=mock_players_query)

    # Mock the result
    mock_players_query.all.return_value = [
        (101, "Player", "One", 3),
        (102, "Player", "Two", 2),
    ]

    # Call the function
    result = get_most_carded_players(mock_db, 1)

    # Check the result
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0] == (101, "Player One", 3)
    assert result[1] == (102, "Player Two", 2)


def test_get_referee_stats_with_data(mock_db: MagicMock) -> None:
    """Test getting referee statistics with mocked data."""
    # Mock the session and query chain
    mock_db._get_session = MagicMock(return_value=mock_db)

    # Mock the referee query
    mock_referee_query = MagicMock()
    mock_db.query = MagicMock(return_value=mock_referee_query)
    mock_referee_query.filter_by = MagicMock(return_value=mock_referee_query)
    mock_referee_query.first = MagicMock(return_value=MagicMock())

    # Mock the total matches query
    mock_matches_query = MagicMock()
    mock_db.query = MagicMock(return_value=mock_matches_query)
    mock_matches_query.filter = MagicMock(return_value=mock_matches_query)
    mock_matches_query.scalar = MagicMock(return_value=10)

    # Mock the match IDs query
    mock_match_ids_query = MagicMock()
    mock_db.query = MagicMock(return_value=mock_match_ids_query)
    mock_match_ids_query.filter = MagicMock(return_value=mock_match_ids_query)
    mock_match_ids_query.all = MagicMock(return_value=[(1,), (2,), (3,)])

    # Mock the yellow cards query
    mock_yellow_query = MagicMock()
    mock_db.query = MagicMock(return_value=mock_yellow_query)
    mock_yellow_query.join = MagicMock(return_value=mock_yellow_query)
    mock_yellow_query.filter = MagicMock(return_value=mock_yellow_query)
    mock_yellow_query.scalar = MagicMock(return_value=5)

    # Mock the red cards query
    mock_red_query = MagicMock()
    mock_db.query = MagicMock(return_value=mock_red_query)
    mock_red_query.join = MagicMock(return_value=mock_red_query)
    mock_red_query.filter = MagicMock(return_value=mock_red_query)
    mock_red_query.scalar = MagicMock(return_value=2)

    # Mock the goals query
    mock_goals_query = MagicMock()
    mock_db.query = MagicMock(return_value=mock_goals_query)
    mock_goals_query.join = MagicMock(return_value=mock_goals_query)
    mock_goals_query.filter = MagicMock(return_value=mock_goals_query)
    mock_goals_query.scalar = MagicMock(return_value=8)

    # Mock the helper functions
    get_most_common_co_officials_mock = MagicMock(
        return_value=[(2, "John Doe", 5), (3, "Jane Smith", 3)]
    )
    get_most_carded_players_mock = MagicMock(
        return_value=[(101, "Player One", 3), (102, "Player Two", 2)]
    )

    # Patch the helper functions
    import referee_stats_fogis.core.stats

    original_co_officials = referee_stats_fogis.core.stats.get_most_common_co_officials
    original_carded_players = referee_stats_fogis.core.stats.get_most_carded_players
    referee_stats_fogis.core.stats.get_most_common_co_officials = (
        get_most_common_co_officials_mock
    )
    referee_stats_fogis.core.stats.get_most_carded_players = (
        get_most_carded_players_mock
    )

    try:
        # Call the function
        stats = get_referee_stats(mock_db, 1)

        # Check the result
        assert stats["total_matches"] == 10
        assert stats["yellow_cards"] == 5
        assert stats["red_cards"] == 2
        assert stats["goals"] == 8
        assert stats["most_common_co_officials"] == [
            (2, "John Doe", 5),
            (3, "Jane Smith", 3),
        ]
        assert stats["most_carded_players"] == [
            (101, "Player One", 3),
            (102, "Player Two", 2),
        ]
    finally:
        # Restore the original functions
        referee_stats_fogis.core.stats.get_most_common_co_officials = (
            original_co_officials
        )
        referee_stats_fogis.core.stats.get_most_carded_players = original_carded_players


def test_get_player_stats_with_data(mock_db: MagicMock) -> None:
    """Test getting player statistics with mocked data."""
    # Mock the session and query chain
    mock_db._get_session = MagicMock(return_value=mock_db)

    # Mock the player query
    mock_player_query = MagicMock()
    mock_db.query = MagicMock(return_value=mock_player_query)
    mock_player_query.filter_by = MagicMock(return_value=mock_player_query)
    mock_player_query.first = MagicMock(return_value=MagicMock())

    # Mock the total matches query
    mock_matches_query = MagicMock()
    mock_db.query = MagicMock(return_value=mock_matches_query)
    mock_matches_query.filter = MagicMock(return_value=mock_matches_query)
    mock_matches_query.scalar = MagicMock(return_value=15)

    # Mock the goals query
    mock_goals_query = MagicMock()
    mock_db.query = MagicMock(return_value=mock_goals_query)
    mock_goals_query.join = MagicMock(return_value=mock_goals_query)
    mock_goals_query.filter = MagicMock(return_value=mock_goals_query)
    mock_goals_query.scalar = MagicMock(return_value=7)

    # Mock the yellow cards query
    mock_yellow_query = MagicMock()
    mock_db.query = MagicMock(return_value=mock_yellow_query)
    mock_yellow_query.join = MagicMock(return_value=mock_yellow_query)
    mock_yellow_query.filter = MagicMock(return_value=mock_yellow_query)
    mock_yellow_query.scalar = MagicMock(return_value=3)

    # Mock the red cards query
    mock_red_query = MagicMock()
    mock_db.query = MagicMock(return_value=mock_red_query)
    mock_red_query.join = MagicMock(return_value=mock_red_query)
    mock_red_query.filter = MagicMock(return_value=mock_red_query)
    mock_red_query.scalar = MagicMock(return_value=1)

    # Mock the teams query
    mock_teams_query = MagicMock()
    mock_db.query = MagicMock(return_value=mock_teams_query)
    mock_teams_query.join = MagicMock(return_value=mock_teams_query)
    mock_teams_query.filter = MagicMock(return_value=mock_teams_query)
    mock_teams_query.group_by = MagicMock(return_value=mock_teams_query)
    mock_teams_query.order_by = MagicMock(return_value=mock_teams_query)
    mock_teams_query.all = MagicMock(return_value=[(1, "Team A", 10), (2, "Team B", 5)])

    # Call the function
    stats = get_player_stats(mock_db, 1)

    # Check the result
    assert stats["total_matches"] == 15
    assert stats["goals"] == 7
    assert stats["yellow_cards"] == 3
    assert stats["red_cards"] == 1
    assert len(stats["teams"]) == 2
    assert stats["teams"][0]["id"] == 1
    assert stats["teams"][0]["name"] == "Team A"
    assert stats["teams"][0]["matches"] == 10
    assert stats["teams"][1]["id"] == 2
    assert stats["teams"][1]["name"] == "Team B"
    assert stats["teams"][1]["matches"] == 5


def test_get_team_stats_with_data(mock_db: MagicMock) -> None:
    """Test getting team statistics with mocked data."""
    # Mock the session and query chain
    mock_db._get_session = MagicMock(return_value=mock_db)

    # Mock the team query
    mock_team_query = MagicMock()
    mock_db.query = MagicMock(return_value=mock_team_query)
    mock_team_query.filter_by = MagicMock(return_value=mock_team_query)
    mock_team_query.first = MagicMock(return_value=MagicMock())

    # Mock the match teams query
    mock_match_teams_query = MagicMock()
    mock_db.query = MagicMock(return_value=mock_match_teams_query)
    mock_match_teams_query.filter = MagicMock(return_value=mock_match_teams_query)
    mock_match_teams_query.all = MagicMock(
        return_value=[
            (1, 101, True),
            (2, 102, True),
            (3, 103, False),
            (4, 104, False),
            (5, 105, True),
        ]
    )

    # Mock the match results query
    mock_results_query = MagicMock()
    mock_db.query = MagicMock(return_value=mock_results_query)
    mock_results_query.filter = MagicMock(return_value=mock_results_query)
    mock_results_query.all = MagicMock(
        return_value=[
            (101, 2, 0),  # Home win
            (102, 1, 1),  # Home draw
            (103, 1, 2),  # Away win
            (104, 0, 0),  # Away draw
            (105, 0, 3),  # Home loss
        ]
    )

    # Mock the opponents query
    mock_opponents_query = MagicMock()
    mock_db.query = MagicMock(return_value=mock_opponents_query)
    mock_opponents_query.join = MagicMock(return_value=mock_opponents_query)
    mock_opponents_query.filter = MagicMock(return_value=mock_opponents_query)
    mock_opponents_query.group_by = MagicMock(return_value=mock_opponents_query)
    mock_opponents_query.order_by = MagicMock(return_value=mock_opponents_query)
    mock_opponents_query.limit = MagicMock(return_value=mock_opponents_query)
    mock_opponents_query.all = MagicMock(
        return_value=[
            (10, "Opponent A", 3),
            (11, "Opponent B", 2),
        ]
    )

    # Mock the top scorers query
    mock_scorers_query = MagicMock()
    mock_db.query = MagicMock(return_value=mock_scorers_query)
    mock_scorers_query.join = MagicMock(return_value=mock_scorers_query)
    mock_scorers_query.filter = MagicMock(return_value=mock_scorers_query)
    mock_scorers_query.group_by = MagicMock(return_value=mock_scorers_query)
    mock_scorers_query.order_by = MagicMock(return_value=mock_scorers_query)
    mock_scorers_query.limit = MagicMock(return_value=mock_scorers_query)
    mock_scorers_query.all = MagicMock(
        return_value=[
            (201, "Scorer", "One", 3),
            (202, "Scorer", "Two", 2),
        ]
    )

    # Call the function
    stats = get_team_stats(mock_db, 1)

    # Check the result
    assert stats["total_matches"] == 5
    assert stats["wins"] == 2
    assert stats["draws"] == 2
    assert stats["losses"] == 1
    assert stats["goals_for"] == 5
    assert stats["goals_against"] == 4
    assert len(stats["most_common_opponents"]) == 2
    assert stats["most_common_opponents"][0]["id"] == 10
    assert stats["most_common_opponents"][0]["name"] == "Opponent A"
    assert stats["most_common_opponents"][0]["matches"] == 3
    assert len(stats["top_scorers"]) == 2
    assert stats["top_scorers"][0]["id"] == 201
    assert stats["top_scorers"][0]["name"] == "Scorer One"
    assert stats["top_scorers"][0]["goals"] == 3


def test_get_match_stats_with_data(mock_db: MagicMock) -> None:
    """Test getting match statistics with mocked data."""
    # Mock the session and query chain
    mock_db._get_session = MagicMock(return_value=mock_db)

    # Mock the match query
    mock_match_query = MagicMock()
    mock_db.query = MagicMock(return_value=mock_match_query)
    mock_match_query.filter_by = MagicMock(return_value=mock_match_query)
    mock_match_query.first = MagicMock(return_value=MagicMock())

    # Mock the match teams query
    mock_teams_query = MagicMock()
    mock_db.query = MagicMock(return_value=mock_teams_query)
    mock_teams_query.join = MagicMock(return_value=mock_teams_query)
    mock_teams_query.filter = MagicMock(return_value=mock_teams_query)
    mock_teams_query.all = MagicMock(
        return_value=[
            (MagicMock(is_home_team=True), MagicMock(name="Home Team", id=1)),
            (MagicMock(is_home_team=False), MagicMock(name="Away Team", id=2)),
        ]
    )

    # Mock the match result query
    mock_result_query = MagicMock()
    mock_db.query = MagicMock(return_value=mock_result_query)
    mock_result_query.filter = MagicMock(return_value=mock_result_query)
    mock_result_query.first = MagicMock(
        return_value=MagicMock(home_goals=2, away_goals=1)
    )

    # Mock the officials query
    mock_officials_query = MagicMock()
    mock_db.query = MagicMock(return_value=mock_officials_query)
    mock_officials_query.join = MagicMock(return_value=mock_officials_query)
    mock_officials_query.filter = MagicMock(return_value=mock_officials_query)
    mock_officials_query.all = MagicMock(
        return_value=[
            (1, "John", "Doe", "Referee"),
            (2, "Jane", "Smith", "Assistant Referee"),
        ]
    )

    # Mock the cards query
    mock_cards_query = MagicMock()
    mock_db.query = MagicMock(return_value=mock_cards_query)
    mock_cards_query.join = MagicMock(return_value=mock_cards_query)
    mock_cards_query.filter = MagicMock(return_value=mock_cards_query)
    mock_cards_query.all = MagicMock(
        return_value=[
            (1, "Player", "One", "Home Team", "Yellow Card", 30),
            (2, "Player", "Two", "Away Team", "Red Card", 75),
        ]
    )

    # Mock the goals query
    mock_goals_query = MagicMock()
    mock_db.query = MagicMock(return_value=mock_goals_query)
    mock_goals_query.join = MagicMock(return_value=mock_goals_query)
    mock_goals_query.filter = MagicMock(return_value=mock_goals_query)
    mock_goals_query.all = MagicMock(
        return_value=[
            (1, "Scorer", "One", "Home Team", 15, False),
            (2, "Scorer", "Two", "Home Team", 60, True),
            (3, "Scorer", "Three", "Away Team", 80, False),
        ]
    )

    # Call the function
    stats = get_match_stats(mock_db, 1)

    # Check the result
    assert stats["home_team"] == "Home Team"
    assert stats["away_team"] == "Away Team"
    assert stats["home_team_id"] == 1
    assert stats["away_team_id"] == 2
    assert stats["score"] == "2-1"
    assert len(stats["officials"]) == 2
    assert stats["officials"][0]["id"] == 1
    assert stats["officials"][0]["name"] == "John Doe"
    assert stats["officials"][0]["role"] == "Referee"
    assert len(stats["cards"]) == 2
    assert stats["cards"][0]["player"] == "Player One"
    assert stats["cards"][0]["team"] == "Home Team"
    assert stats["cards"][0]["type"] == "Yellow Card"
    assert stats["cards"][0]["minute"] == 30
    assert len(stats["goals"]) == 3
    assert stats["goals"][0]["scorer"] == "Scorer One"
    assert stats["goals"][0]["team"] == "Home Team"
    assert stats["goals"][0]["minute"] == 15
    assert not stats["goals"][0]["is_penalty"]
    assert stats["goals"][1]["is_penalty"] is True
