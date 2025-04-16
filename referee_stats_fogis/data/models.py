"""Database models for the referee stats application."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Person:
    """Represents a person (player, referee, etc.)."""

    id: int
    name: str
    fogis_id: str | None = None


@dataclass
class Team:
    """Represents a team."""

    id: int
    name: str
    fogis_id: str | None = None


@dataclass
class Match:
    """Represents a match."""

    id: int
    date: datetime
    home_team_id: int
    away_team_id: int
    competition: str
    venue: str
    fogis_id: str | None = None
    home_goals: int | None = None
    away_goals: int | None = None


@dataclass
class MatchOfficial:
    """Represents a match official assignment."""

    id: int
    match_id: int
    person_id: int
    role: str  # e.g., "Referee", "Assistant Referee", etc.


@dataclass
class Card:
    """Represents a card given during a match."""

    id: int
    match_id: int
    person_id: int  # Player who received the card
    card_type: str  # "Yellow" or "Red"
    minute: int | None = None
    reason: str | None = None


@dataclass
class Goal:
    """Represents a goal scored during a match."""

    id: int
    match_id: int
    scorer_id: int
    team_id: int
    minute: int | None = None
    penalty: bool = False
    own_goal: bool = False
