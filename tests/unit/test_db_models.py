"""Tests for database models."""

import os
import tempfile
import unittest
from datetime import datetime
from typing import Any, cast

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from referee_stats_fogis.data.base import Base
from referee_stats_fogis.data.models import (
    Club,
    Competition,
    CompetitionCategory,
    EventType,
    Match,
    MatchEvent,
    MatchParticipant,
    MatchResult,
    MatchTeam,
    Person,
    Referee,
    RefereeAssignment,
    RefereeRole,
    ResultType,
    Team,
    Venue,
)


class TestDatabaseModels(unittest.TestCase):
    """Test database models."""

    db_fd: int
    db_path: str
    engine: Any
    session: Session

    def setUp(self) -> None:
        """Set up test database."""
        # Create a temporary SQLite database
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = cast(Session, Session())

    def tearDown(self) -> None:
        """Clean up test database."""
        self.session.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_person_model(self) -> None:
        """Test Person model."""
        # Create a person
        person = Person(
            first_name="John",
            last_name="Doe",
            personal_number="19800101-1234",
            email="john.doe@example.com",
            phone="123456789",
            address="123 Main St",
            postal_code="12345",
            city="Stockholm",
            country="Sweden",
            fogis_id="P12345",
        )
        self.session.add(person)
        self.session.commit()

        # Retrieve the person
        retrieved_person = self.session.query(Person).filter_by(id=person.id).first()
        assert retrieved_person is not None
        assert retrieved_person.first_name == "John"
        assert retrieved_person.last_name == "Doe"
        assert retrieved_person.personal_number == "19800101-1234"
        assert retrieved_person.email == "john.doe@example.com"
        assert retrieved_person.fogis_id == "P12345"

    def test_club_and_team_models(self) -> None:
        """Test Club and Team models."""
        # Create a club
        club = Club(name="Test FC", fogis_id="C12345")
        self.session.add(club)
        self.session.commit()

        # Create a team
        team = Team(name="Test FC First Team", club_id=club.id, fogis_id="T12345")
        self.session.add(team)
        self.session.commit()

        # Retrieve the team with its club
        retrieved_team = self.session.query(Team).filter_by(id=team.id).first()
        assert retrieved_team is not None
        assert retrieved_team.name == "Test FC First Team"
        assert retrieved_team.fogis_id == "T12345"
        assert retrieved_team.club_id == club.id
        assert retrieved_team.club.name == "Test FC"

    def test_match_and_related_models(self) -> None:
        """Test Match and related models."""
        # Create a venue
        venue = Venue(name="Test Stadium", latitude=59.3293, longitude=18.0686)
        self.session.add(venue)

        # Create a competition category
        category = CompetitionCategory(name="Division 1")
        self.session.add(category)

        # Create a competition
        competition = Competition(
            name="Division 1 North",
            season="2023",
            category_id=category.id,
            gender_id=1,
            age_category_id=4,
            fogis_id="C12345",
        )
        self.session.add(competition)

        # Create clubs and teams
        home_club = Club(name="Home FC")
        away_club = Club(name="Away FC")
        self.session.add_all([home_club, away_club])
        self.session.commit()

        home_team = Team(name="Home FC First Team", club_id=home_club.id)
        away_team = Team(name="Away FC First Team", club_id=away_club.id)
        self.session.add_all([home_team, away_team])
        self.session.commit()

        # Create a match
        match = Match(
            match_nr="12345",
            date=datetime(2023, 5, 15, 18, 0),
            time="18:00",
            venue_id=venue.id,
            competition_id=competition.id,
            football_type_id=1,
            spectators=1000,
            status="normal",
            is_walkover=False,
            fogis_id="M12345",
        )
        self.session.add(match)
        self.session.commit()

        # Create match teams
        home_match_team = MatchTeam(
            match_id=match.id,
            team_id=home_team.id,
            is_home_team=True,
            fogis_id="MT12345",
        )
        away_match_team = MatchTeam(
            match_id=match.id,
            team_id=away_team.id,
            is_home_team=False,
            fogis_id="MT12346",
        )
        self.session.add_all([home_match_team, away_match_team])
        self.session.commit()

        # Create a result type
        result_type = ResultType(name="Final Result")
        self.session.add(result_type)
        self.session.commit()

        # Create a match result
        match_result = MatchResult(
            match_id=match.id,
            result_type_id=result_type.id,
            home_goals=2,
            away_goals=1,
            fogis_id="MR12345",
        )
        self.session.add(match_result)
        self.session.commit()

        # Retrieve the match with its relationships
        retrieved_match = self.session.query(Match).filter_by(id=match.id).first()
        assert retrieved_match is not None
        assert retrieved_match.match_nr == "12345"
        assert retrieved_match.venue.name == "Test Stadium"
        assert retrieved_match.competition.name == "Division 1 North"
        assert len(retrieved_match.match_teams) == 2
        assert retrieved_match.match_results[0].home_goals == 2
        assert retrieved_match.match_results[0].away_goals == 1

    def test_referee_and_assignment_models(self) -> None:
        """Test Referee and RefereeAssignment models."""
        # Create a person
        person = Person(first_name="John", last_name="Doe")
        self.session.add(person)
        self.session.commit()

        # Create a referee
        referee = Referee(
            person_id=person.id,
            referee_number="R12345",
            fogis_id="RF12345",
        )
        self.session.add(referee)

        # Create a referee role
        role = RefereeRole(name="Huvuddomare", short_name="Dom")
        self.session.add(role)

        # Create a match (simplified)
        venue = Venue(name="Test Stadium")
        category = CompetitionCategory(name="Division 1")
        competition = Competition(name="Division 1 North", category_id=category.id)
        self.session.add_all([venue, category, competition])
        self.session.commit()

        match = Match(
            match_nr="12345",
            date=datetime(2023, 5, 15, 18, 0),
            time="18:00",
            venue_id=venue.id,
            competition_id=competition.id,
            football_type_id=1,
        )
        self.session.add(match)
        self.session.commit()

        # Create a referee assignment
        assignment = RefereeAssignment(
            match_id=match.id,
            referee_id=referee.id,
            role_id=role.id,
            status="Tilldelat",
            fogis_id="RA12345",
        )
        self.session.add(assignment)
        self.session.commit()

        # Retrieve the assignment with its relationships
        retrieved_assignment = (
            self.session.query(RefereeAssignment).filter_by(id=assignment.id).first()
        )
        assert retrieved_assignment is not None
        assert retrieved_assignment.referee.person.first_name == "John"
        assert retrieved_assignment.role.name == "Huvuddomare"
        assert retrieved_assignment.match.match_nr == "12345"

    def test_event_models(self) -> None:
        """Test EventType and MatchEvent models."""
        # Create an event type
        event_type = EventType(
            name="Regular Goal",
            is_goal=True,
            is_penalty=False,
            is_card=False,
            is_substitution=False,
            is_control_event=False,
            affects_score=True,
        )
        self.session.add(event_type)

        # Create a match (simplified)
        venue = Venue(name="Test Stadium")
        category = CompetitionCategory(name="Division 1")
        competition = Competition(name="Division 1 North", category_id=category.id)
        self.session.add_all([venue, category, competition])
        self.session.commit()

        match = Match(
            match_nr="12345",
            date=datetime(2023, 5, 15, 18, 0),
            time="18:00",
            venue_id=venue.id,
            competition_id=competition.id,
            football_type_id=1,
        )
        self.session.add(match)

        # Create clubs and teams
        club = Club(name="Test FC")
        self.session.add(club)
        self.session.commit()

        team = Team(name="Test FC First Team", club_id=club.id)
        self.session.add(team)
        self.session.commit()

        match_team = MatchTeam(
            match_id=match.id,
            team_id=team.id,
            is_home_team=True,
        )
        self.session.add(match_team)

        # Create a person and match participant
        person = Person(first_name="John", last_name="Doe")
        self.session.add(person)
        self.session.commit()

        participant = MatchParticipant(
            match_id=match.id,
            match_team_id=match_team.id,
            player_id=person.id,
            jersey_number=10,
            is_captain=True,
            is_substitute=False,
        )
        self.session.add(participant)
        self.session.commit()

        # Create a match event
        event = MatchEvent(
            match_id=match.id,
            participant_id=participant.id,
            event_type_id=event_type.id,
            match_team_id=match_team.id,
            minute=30,
            period=1,
            comment="Great goal!",
            home_score=1,
            away_score=0,
            position_x=80,
            position_y=50,
            fogis_id="ME12345",
        )
        self.session.add(event)
        self.session.commit()

        # Retrieve the event with its relationships
        retrieved_event = self.session.query(MatchEvent).filter_by(id=event.id).first()
        assert retrieved_event is not None
        assert retrieved_event.minute == 30
        assert retrieved_event.event_type.name == "Regular Goal"
        assert retrieved_event.participant.player.first_name == "John"
        assert retrieved_event.match_team.team.name == "Test FC First Team"
        assert retrieved_event.home_score == 1
        assert retrieved_event.away_score == 0
