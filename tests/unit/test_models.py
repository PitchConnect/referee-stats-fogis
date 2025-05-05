"""Tests for the data models."""

from datetime import datetime

from referee_stats_fogis.data.models import (
    EventType,
    Match,
    MatchEvent,
    MatchParticipant,
    Person,
    RefereeAssignment,
    Team,
)


def test_person_creation() -> None:
    """Test creating a Person instance."""
    person = Person(
        id=1,
        first_name="John",
        last_name="Doe",
        personal_number="19800101-1234",
        email="john.doe@example.com",
        fogis_id="12345",
    )
    assert person.id == 1
    assert person.first_name == "John"
    assert person.last_name == "Doe"
    assert person.personal_number == "19800101-1234"
    assert person.email == "john.doe@example.com"
    assert person.fogis_id == "12345"


def test_team_creation() -> None:
    """Test creating a Team instance."""
    team = Team(id=1, name="Test FC", club_id=1, fogis_id="T12345")
    assert team.id == 1
    assert team.name == "Test FC"
    assert team.club_id == 1
    assert team.fogis_id == "T12345"


def test_match_creation() -> None:
    """Test creating a Match instance."""
    match_date = datetime(2023, 5, 15, 18, 0)
    match = Match(
        id=1,
        match_nr="12345",
        date=match_date,
        time="18:00",
        venue_id=1,
        competition_id=1,
        football_type_id=1,
        spectators=1000,
        status="normal",
        is_walkover=False,
        fogis_id="M12345",
    )
    assert match.id == 1
    assert match.match_nr == "12345"
    assert match.date == match_date
    assert match.time == "18:00"
    assert match.venue_id == 1
    assert match.competition_id == 1
    assert match.football_type_id == 1
    assert match.spectators == 1000
    assert match.status == "normal"
    assert match.is_walkover is False
    assert match.fogis_id == "M12345"


def test_referee_assignment_creation() -> None:
    """Test creating a RefereeAssignment instance."""
    assignment = RefereeAssignment(
        id=1, match_id=1, referee_id=1, role_id=1, status="Tilldelat"
    )
    assert assignment.id == 1
    assert assignment.match_id == 1
    assert assignment.referee_id == 1
    assert assignment.role_id == 1
    assert assignment.status == "Tilldelat"


def test_card_event_creation() -> None:
    """Test creating a card event."""
    # First create an event type for cards
    card_type = EventType(
        id=1,
        name="Yellow Card",
        is_card=True,
        is_goal=False,
        is_substitution=False,
        is_control_event=False,
        affects_score=False,
    )

    # Create a match participant
    participant = MatchParticipant(
        id=1,
        match_id=1,
        match_team_id=1,
        player_id=2,
        jersey_number=10,
        is_captain=False,
        is_substitute=False,
    )

    # Create the card event
    card_event = MatchEvent(
        id=1,
        match_id=1,
        participant_id=participant.id,
        event_type_id=card_type.id,
        match_team_id=1,
        minute=35,
        period=1,
        comment="Unsporting behavior",
    )

    assert card_event.id == 1
    assert card_event.match_id == 1
    assert card_event.participant_id == participant.id
    assert card_event.event_type_id == card_type.id
    assert card_event.minute == 35
    assert card_event.comment == "Unsporting behavior"


def test_goal_event_creation() -> None:
    """Test creating a goal event."""
    # First create an event type for goals
    goal_type = EventType(
        id=2,
        name="Regular Goal",
        is_card=False,
        is_goal=True,
        is_penalty=False,
        is_substitution=False,
        is_control_event=False,
        affects_score=True,
    )

    # Create a match participant (scorer)
    participant = MatchParticipant(
        id=2,
        match_id=1,
        match_team_id=1,
        player_id=3,
        jersey_number=9,
        is_captain=False,
        is_substitute=False,
    )

    # Create the goal event
    goal_event = MatchEvent(
        id=2,
        match_id=1,
        participant_id=participant.id,
        event_type_id=goal_type.id,
        match_team_id=1,
        minute=42,
        period=1,
        home_score=1,
        away_score=0,
    )

    assert goal_event.id == 2
    assert goal_event.match_id == 1
    assert goal_event.participant_id == participant.id
    assert goal_event.event_type_id == goal_type.id
    assert goal_event.match_team_id == 1
    assert goal_event.minute == 42
    assert goal_event.home_score == 1
    assert goal_event.away_score == 0
