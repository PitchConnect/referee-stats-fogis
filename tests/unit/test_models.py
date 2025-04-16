"""Tests for the data models."""

from datetime import datetime

from referee_stats_fogis.data.models import (
    Card,
    Goal,
    Match,
    MatchOfficial,
    Person,
    Team,
)


def test_person_creation() -> None:
    """Test creating a Person instance."""
    person = Person(id=1, name="John Doe", fogis_id="12345")
    assert person.id == 1
    assert person.name == "John Doe"
    assert person.fogis_id == "12345"


def test_team_creation() -> None:
    """Test creating a Team instance."""
    team = Team(id=1, name="Test FC", fogis_id="T12345")
    assert team.id == 1
    assert team.name == "Test FC"
    assert team.fogis_id == "T12345"


def test_match_creation() -> None:
    """Test creating a Match instance."""
    match_date = datetime(2023, 5, 15, 18, 0)
    match = Match(
        id=1,
        date=match_date,
        home_team_id=1,
        away_team_id=2,
        competition="Test League",
        venue="Test Stadium",
        fogis_id="M12345",
        home_goals=2,
        away_goals=1,
    )
    assert match.id == 1
    assert match.date == match_date
    assert match.home_team_id == 1
    assert match.away_team_id == 2
    assert match.competition == "Test League"
    assert match.venue == "Test Stadium"
    assert match.fogis_id == "M12345"
    assert match.home_goals == 2
    assert match.away_goals == 1


def test_match_official_creation() -> None:
    """Test creating a MatchOfficial instance."""
    official = MatchOfficial(id=1, match_id=1, person_id=1, role="Referee")
    assert official.id == 1
    assert official.match_id == 1
    assert official.person_id == 1
    assert official.role == "Referee"


def test_card_creation() -> None:
    """Test creating a Card instance."""
    card = Card(
        id=1,
        match_id=1,
        person_id=2,
        card_type="Yellow",
        minute=35,
        reason="Unsporting behavior",
    )
    assert card.id == 1
    assert card.match_id == 1
    assert card.person_id == 2
    assert card.card_type == "Yellow"
    assert card.minute == 35
    assert card.reason == "Unsporting behavior"


def test_goal_creation() -> None:
    """Test creating a Goal instance."""
    goal = Goal(
        id=1,
        match_id=1,
        scorer_id=3,
        team_id=1,
        minute=42,
        penalty=False,
        own_goal=False,
    )
    assert goal.id == 1
    assert goal.match_id == 1
    assert goal.scorer_id == 3
    assert goal.team_id == 1
    assert goal.minute == 42
    assert goal.penalty is False
    assert goal.own_goal is False
