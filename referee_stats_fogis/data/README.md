# Data Models

This directory contains the data models for the Referee Stats FOGIS application.

## Overview

The data models represent the entities in our database schema, including relationships between models. They are implemented using SQLAlchemy ORM.

## Models

The following models are implemented in `models.py`:

- **Person**: Represents a person (player, referee, etc.)
- **Club**: Represents a club
- **Team**: Represents a team
- **TeamContact**: Represents a contact person for a team
- **Venue**: Represents a venue
- **CompetitionCategory**: Represents a competition category
- **Competition**: Represents a competition
- **Match**: Represents a match
- **MatchTeam**: Represents a team in a specific match
- **ResultType**: Represents a result type
- **MatchResult**: Represents a match result
- **Referee**: Represents a referee
- **RefereeRole**: Represents a referee role
- **RefereeAssignment**: Represents a referee assignment to a match
- **MatchParticipant**: Represents a player participating in a match
- **EventType**: Represents an event type
- **MatchEvent**: Represents an event during a match

## Relationships

The models include relationships between entities, such as:

- A Person can be a Referee
- A Club has many Teams
- A Match has many MatchTeams, MatchParticipants, and MatchEvents
- A MatchParticipant belongs to a Match and a Person
- etc.

## Validation

The models include appropriate validation through SQLAlchemy's column constraints:

- Required fields are marked with `nullable=False`
- Foreign keys ensure referential integrity
- Default values are provided where appropriate

## Usage

To use these models, you can import them from the `referee_stats_fogis.data.models` module:

```python
from referee_stats_fogis.data.models import Person, Team, Match
```

Then use SQLAlchemy's session to query and manipulate the data:

```python
from referee_stats_fogis.data.base import get_session

session = get_session()
person = session.query(Person).filter_by(id=1).first()
```
