"""Database models for the referee stats application."""


from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from referee_stats_fogis.data.base import Base


class Person(Base):
    """Represents a person (player, referee, etc.)."""

    __tablename__ = "persons"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    personal_number = Column(String(20))
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(String(200))
    postal_code = Column(String(20))
    city = Column(String(50))
    country = Column(String(50), default="Sweden")
    fogis_id = Column(String(20))

    # Relationships
    referee = relationship("Referee", back_populates="person", uselist=False)
    match_participants = relationship("MatchParticipant", back_populates="player")
    team_contacts = relationship("TeamContact", back_populates="person")

    def __repr__(self) -> str:
        """Return string representation of the person."""
        return f"<Person(id={self.id}, name='{self.first_name} {self.last_name}')>"


class Club(Base):
    """Represents a club."""

    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    fogis_id = Column(String(20))

    # Relationships
    teams = relationship("Team", back_populates="club")

    def __repr__(self) -> str:
        """Return string representation of the club."""
        return f"<Club(id={self.id}, name='{self.name}')>"


class Team(Base):
    """Represents a team."""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False)
    fogis_id = Column(String(20))

    # Relationships
    club = relationship("Club", back_populates="teams")
    match_teams = relationship("MatchTeam", back_populates="team")
    team_contacts = relationship("TeamContact", back_populates="team")

    def __repr__(self) -> str:
        """Return string representation of the team."""
        return f"<Team(id={self.id}, name='{self.name}')>"


class TeamContact(Base):
    """Represents a contact person for a team."""

    __tablename__ = "team_contacts"

    team_id = Column(Integer, ForeignKey("teams.id"), primary_key=True)
    person_id = Column(Integer, ForeignKey("persons.id"), primary_key=True)
    is_reserve = Column(Boolean, default=False)

    # Relationships
    team = relationship("Team", back_populates="team_contacts")
    person = relationship("Person", back_populates="team_contacts")

    def __repr__(self) -> str:
        """Return string representation of the team contact."""
        return f"<TeamContact(team_id={self.team_id}, person_id={self.person_id})>"


class Venue(Base):
    """Represents a venue."""

    __tablename__ = "venues"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)

    # Relationships
    matches = relationship("Match", back_populates="venue")

    def __repr__(self) -> str:
        """Return string representation of the venue."""
        return f"<Venue(id={self.id}, name='{self.name}')>"


class CompetitionCategory(Base):
    """Represents a competition category."""

    __tablename__ = "competition_categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    # Relationships
    competitions = relationship("Competition", back_populates="category")

    def __repr__(self) -> str:
        """Return string representation of the competition category."""
        return f"<CompetitionCategory(id={self.id}, name='{self.name}')>"


class Competition(Base):
    """Represents a competition."""

    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    season = Column(String(20))
    category_id = Column(Integer, ForeignKey("competition_categories.id"))
    gender_id = Column(Integer)
    age_category_id = Column(Integer)
    fogis_id = Column(String(20))

    # Relationships
    category = relationship("CompetitionCategory", back_populates="competitions")
    matches = relationship("Match", back_populates="competition")

    def __repr__(self) -> str:
        """Return string representation of the competition."""
        return f"<Competition(id={self.id}, name='{self.name}')>"


class Match(Base):
    """Represents a match."""

    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)
    match_nr = Column(String(20), nullable=False)
    date = Column(DateTime, nullable=False)
    time = Column(String(10), nullable=False)
    venue_id = Column(Integer, ForeignKey("venues.id"))
    competition_id = Column(Integer, ForeignKey("competitions.id"), nullable=False)
    football_type_id = Column(Integer, nullable=False)  # 1 for football, 2 for futsal
    spectators = Column(Integer)
    status = Column(String(20), default="normal")
    is_walkover = Column(Boolean, default=False)
    fogis_id = Column(String(20))

    # Relationships
    venue = relationship("Venue", back_populates="matches")
    competition = relationship("Competition", back_populates="matches")
    match_teams = relationship("MatchTeam", back_populates="match")
    match_results = relationship("MatchResult", back_populates="match")
    referee_assignments = relationship("RefereeAssignment", back_populates="match")
    match_participants = relationship("MatchParticipant", back_populates="match")
    match_events = relationship("MatchEvent", back_populates="match")

    def __repr__(self) -> str:
        """Return string representation of the match."""
        return f"<Match(id={self.id}, match_nr='{self.match_nr}', date='{self.date}')>"


class MatchTeam(Base):
    """Represents a team in a specific match."""

    __tablename__ = "match_teams"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    is_home_team = Column(Boolean, nullable=False)
    fogis_id = Column(String(20))

    # Relationships
    match = relationship("Match", back_populates="match_teams")
    team = relationship("Team", back_populates="match_teams")
    match_participants = relationship("MatchParticipant", back_populates="match_team")
    match_events = relationship("MatchEvent", back_populates="match_team")

    def __repr__(self) -> str:
        """Return string representation of the match team."""
        return (
            f"<MatchTeam(id={self.id}, match_id={self.match_id}, "
            f"team_id={self.team_id})>"
        )


class ResultType(Base):
    """Represents a result type."""

    __tablename__ = "result_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    # Relationships
    match_results = relationship("MatchResult", back_populates="result_type")

    def __repr__(self) -> str:
        """Return string representation of the result type."""
        return f"<ResultType(id={self.id}, name='{self.name}')>"


class MatchResult(Base):
    """Represents a match result."""

    __tablename__ = "match_results"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    result_type_id = Column(Integer, ForeignKey("result_types.id"), nullable=False)
    home_goals = Column(Integer, nullable=False)
    away_goals = Column(Integer, nullable=False)
    fogis_id = Column(String(20))

    # Relationships
    match = relationship("Match", back_populates="match_results")
    result_type = relationship("ResultType", back_populates="match_results")

    def __repr__(self) -> str:
        """Return string representation of the match result."""
        return (
            f"<MatchResult(id={self.id}, match_id={self.match_id}, "
            f"score={self.home_goals}-{self.away_goals})>"
        )


class Referee(Base):
    """Represents a referee."""

    __tablename__ = "referees"

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False)
    referee_number = Column(String(20))
    fogis_id = Column(String(20))

    # Relationships
    person = relationship("Person", back_populates="referee")
    referee_assignments = relationship("RefereeAssignment", back_populates="referee")

    def __repr__(self) -> str:
        """Return string representation of the referee."""
        return f"<Referee(id={self.id}, person_id={self.person_id})>"


class RefereeRole(Base):
    """Represents a referee role."""

    __tablename__ = "referee_roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    short_name = Column(String(10))

    # Relationships
    referee_assignments = relationship("RefereeAssignment", back_populates="role")

    def __repr__(self) -> str:
        """Return string representation of the referee role."""
        return f"<RefereeRole(id={self.id}, name='{self.name}')>"


class RefereeAssignment(Base):
    """Represents a referee assignment to a match."""

    __tablename__ = "referee_assignments"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    referee_id = Column(Integer, ForeignKey("referees.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("referee_roles.id"), nullable=False)
    status = Column(String(20))
    fogis_id = Column(String(20))

    # Relationships
    match = relationship("Match", back_populates="referee_assignments")
    referee = relationship("Referee", back_populates="referee_assignments")
    role = relationship("RefereeRole", back_populates="referee_assignments")

    def __repr__(self) -> str:
        """Return string representation of the referee assignment."""
        return (
            f"<RefereeAssignment(id={self.id}, match_id={self.match_id}, "
            f"referee_id={self.referee_id})>"
        )


class MatchParticipant(Base):
    """Represents a player participating in a match."""

    __tablename__ = "match_participants"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    match_team_id = Column(Integer, ForeignKey("match_teams.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("persons.id"), nullable=False)
    jersey_number = Column(Integer)
    is_captain = Column(Boolean, default=False)
    is_substitute = Column(Boolean, default=False)
    substitution_in_minute = Column(Integer)
    substitution_out_minute = Column(Integer)
    team_section_id = Column(Integer, default=0)
    position_number = Column(Integer, default=0)
    ejection_info = Column(Text)
    is_playing_leader = Column(Boolean, default=False)
    is_responsible = Column(Boolean, default=False)
    accumulated_warnings = Column(Integer, default=0)
    suspension_description = Column(Text)
    fogis_id = Column(String(20))

    # Relationships
    match = relationship("Match", back_populates="match_participants")
    match_team = relationship("MatchTeam", back_populates="match_participants")
    player = relationship("Person", back_populates="match_participants")
    match_events = relationship("MatchEvent", back_populates="participant")

    def __repr__(self) -> str:
        """Return string representation of the match participant."""
        return (
            f"<MatchParticipant(id={self.id}, match_id={self.match_id}, "
            f"player_id={self.player_id})>"
        )


class EventType(Base):
    """Represents an event type."""

    __tablename__ = "event_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    is_goal = Column(Boolean, default=False)
    is_penalty = Column(Boolean, default=False)
    is_card = Column(Boolean, default=False)
    is_substitution = Column(Boolean, default=False)
    is_control_event = Column(Boolean, default=False)
    affects_score = Column(Boolean, default=False)
    description = Column(Text)

    # Relationships
    match_events = relationship("MatchEvent", back_populates="event_type")

    def __repr__(self) -> str:
        """Return string representation of the event type."""
        return f"<EventType(id={self.id}, name='{self.name}')>"


class MatchEvent(Base):
    """Represents an event during a match."""

    __tablename__ = "match_events"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    participant_id = Column(
        Integer, ForeignKey("match_participants.id"), nullable=False
    )
    event_type_id = Column(Integer, ForeignKey("event_types.id"), nullable=False)
    match_team_id = Column(Integer, ForeignKey("match_teams.id"), nullable=False)
    minute = Column(Integer)
    period = Column(Integer)
    comment = Column(Text)
    home_score = Column(Integer, nullable=False)
    away_score = Column(Integer, nullable=False)
    position_x = Column(Integer)
    position_y = Column(Integer)
    related_event_id = Column(Integer, ForeignKey("match_events.id"))
    fogis_id = Column(String(20))

    # Relationships
    match = relationship("Match", back_populates="match_events")
    participant = relationship("MatchParticipant", back_populates="match_events")
    event_type = relationship("EventType", back_populates="match_events")
    match_team = relationship("MatchTeam", back_populates="match_events")
    related_event = relationship(
        "MatchEvent", remote_side=[id], backref="related_events"
    )

    def __repr__(self) -> str:
        """Return string representation of the match event."""
        return (
            f"<MatchEvent(id={self.id}, match_id={self.match_id}, "
            f"event_type_id={self.event_type_id})>"
        )
