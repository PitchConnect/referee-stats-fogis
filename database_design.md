# Referee Stats FOGIS - Database Design Document

## Overview

This document outlines the database design for the Referee Stats FOGIS application, which will store and analyze referee statistics from FOGIS (Swedish Football Association's information system).

## Data Sources

The application will import data from JSON objects provided by FOGIS API, including:
- Match information
- Team and player details
- Match events (goals, cards, substitutions)
- Match results
- Referee assignments

## Database Schema

### Core Entities

#### Match
```sql
CREATE TABLE matches (
    match_id INTEGER PRIMARY KEY,
    match_nr VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    venue_id INTEGER,
    competition_id INTEGER NOT NULL,
    football_type_id INTEGER NOT NULL,  -- 1 for football, 2 for futsal
    spectators INTEGER,
    status VARCHAR(20),  -- normal, postponed, abandoned, etc.
    is_walkover BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (venue_id) REFERENCES venues(venue_id),
    FOREIGN KEY (competition_id) REFERENCES competitions(competition_id)
);
```

#### Team
```sql
CREATE TABLE teams (
    team_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    club_id INTEGER NOT NULL,
    FOREIGN KEY (club_id) REFERENCES clubs(club_id)
);
```

#### Club
```sql
CREATE TABLE clubs (
    club_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);
```

#### Person
```sql
CREATE TABLE persons (
    person_id INTEGER PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    personal_number VARCHAR(20),
    email VARCHAR(100),
    phone VARCHAR(20),
    address VARCHAR(200),
    postal_code VARCHAR(20),
    city VARCHAR(50),
    country VARCHAR(50)
);
```

#### Venue
```sql
CREATE TABLE venues (
    venue_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7)
);
```

#### Competition
```sql
CREATE TABLE competitions (
    competition_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    season VARCHAR(20),
    category_id INTEGER,
    gender_id INTEGER,
    age_category_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES competition_categories(category_id)
);
```

#### CompetitionCategory
```sql
CREATE TABLE competition_categories (
    category_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);
```

### Relationship Entities

#### MatchTeam
```sql
CREATE TABLE match_teams (
    match_team_id INTEGER PRIMARY KEY,  -- matchlagid from JSON
    match_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    is_home_team BOOLEAN NOT NULL,
    FOREIGN KEY (match_id) REFERENCES matches(match_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    UNIQUE (match_id, team_id)
);
```

#### MatchResult
```sql
CREATE TABLE match_results (
    result_id INTEGER PRIMARY KEY,
    match_id INTEGER NOT NULL,
    result_type_id INTEGER NOT NULL,
    home_goals INTEGER NOT NULL,
    away_goals INTEGER NOT NULL,
    FOREIGN KEY (match_id) REFERENCES matches(match_id),
    FOREIGN KEY (result_type_id) REFERENCES result_types(result_type_id)
);
```

#### ResultType
```sql
CREATE TABLE result_types (
    result_type_id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);
```

#### MatchParticipant
```sql
CREATE TABLE match_participants (
    participant_id INTEGER PRIMARY KEY,  -- matchdeltagareid from JSON
    match_id INTEGER NOT NULL,
    match_team_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    jersey_number INTEGER,
    is_captain BOOLEAN DEFAULT FALSE,
    is_substitute BOOLEAN DEFAULT FALSE,
    substitution_in_minute INTEGER,  -- byte1 in JSON
    substitution_out_minute INTEGER,  -- byte2 in JSON
    team_section_id INTEGER DEFAULT 0,  -- lagdelid in JSON (1=goalkeeper, 2=defender, etc.)
    position_number INTEGER DEFAULT 0,  -- positionsnummerhv in JSON (field position)
    ejection_info TEXT,  -- utvisning in JSON
    is_playing_leader BOOLEAN DEFAULT FALSE,  -- arSpelandeLedare in JSON
    is_responsible BOOLEAN DEFAULT FALSE,  -- ansvarig in JSON
    accumulated_warnings INTEGER DEFAULT 0,  -- spelareAntalAckumuleradeVarningar in JSON
    suspension_description TEXT,  -- spelareAvstangningBeskrivning in JSON
    FOREIGN KEY (match_id) REFERENCES matches(match_id),
    FOREIGN KEY (match_team_id) REFERENCES match_teams(match_team_id),
    FOREIGN KEY (player_id) REFERENCES persons(person_id)
);
```

#### Referee
```sql
CREATE TABLE referees (
    referee_id INTEGER PRIMARY KEY,
    person_id INTEGER NOT NULL,
    referee_number VARCHAR(20),
    FOREIGN KEY (person_id) REFERENCES persons(person_id)
);
```

#### RefereeRole
```sql
CREATE TABLE referee_roles (
    role_id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    short_name VARCHAR(10)
);
```

#### RefereeAssignment
```sql
CREATE TABLE referee_assignments (
    assignment_id INTEGER PRIMARY KEY,
    match_id INTEGER NOT NULL,
    referee_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    status VARCHAR(20),
    FOREIGN KEY (match_id) REFERENCES matches(match_id),
    FOREIGN KEY (referee_id) REFERENCES referees(referee_id),
    FOREIGN KEY (role_id) REFERENCES referee_roles(role_id)
);
```

#### EventType
```sql
CREATE TABLE event_types (
    event_type_id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    is_goal BOOLEAN NOT NULL DEFAULT FALSE,
    is_penalty BOOLEAN NOT NULL DEFAULT FALSE,
    is_card BOOLEAN NOT NULL DEFAULT FALSE,
    is_substitution BOOLEAN NOT NULL DEFAULT FALSE,
    is_control_event BOOLEAN NOT NULL DEFAULT FALSE,
    affects_score BOOLEAN NOT NULL DEFAULT FALSE,
    description TEXT
);
```

#### MatchEvent
```sql
CREATE TABLE match_events (
    event_id INTEGER PRIMARY KEY,
    match_id INTEGER NOT NULL,
    participant_id INTEGER NOT NULL,
    event_type_id INTEGER NOT NULL,
    match_team_id INTEGER NOT NULL,
    minute INTEGER,
    period INTEGER,
    comment TEXT,
    home_score INTEGER NOT NULL,
    away_score INTEGER NOT NULL,
    position_x INTEGER,
    position_y INTEGER,
    related_event_id INTEGER,
    FOREIGN KEY (match_id) REFERENCES matches(match_id),
    FOREIGN KEY (participant_id) REFERENCES match_participants(participant_id),
    FOREIGN KEY (event_type_id) REFERENCES event_types(event_type_id),
    FOREIGN KEY (match_team_id) REFERENCES match_teams(match_team_id),
    FOREIGN KEY (related_event_id) REFERENCES match_events(event_id)
);
```

#### TeamContact
```sql
CREATE TABLE team_contacts (
    team_id INTEGER NOT NULL,
    person_id INTEGER NOT NULL,
    is_reserve BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (team_id, person_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    FOREIGN KEY (person_id) REFERENCES persons(person_id)
);
```

## Event Types

The system supports various event types, categorized as follows:

### Goals
- Regular Goal (6)
- Header Goal (39)
- Corner Goal (28)
- Free Kick Goal (29)
- Own Goal (15)
- Penalty Goal (14)

### Penalties
- Penalty Missing Goal (18)
- Penalty Save (19)
- Penalty Hitting the Frame (26)

### Cards
- Yellow Card (20)
- Red Card - Denying Goal Opportunity (8)
- Red Card - Other Reasons (9)

### Substitutions
- Substitution Out (16)
- Substitution In (17)

### Control Events
- Period Start (31)
- Period End (32)
- Match End (23)

## Implementation Notes

### Data Import Process
1. Import matches, competitions, venues
2. Import teams and clubs
3. Import persons (players, referees)
4. Import match teams and match participants
5. Import referee assignments
6. Import match events and results

### Player Roster and Substitution Handling

The player roster data contains several important fields that require special handling:

- **Substitutions**:
  - `byte1` indicates when a player was substituted in or out
  - For starting players who were substituted out, this is their exit minute
  - For substitutes who entered the game, this is their entry minute
  - `byte2` would be used if a player is subbed in and then subbed out (rare, usually for injuries)

- **Team Sections and Positions**:
  - `lagdelid` appears to indicate player position categories (1 = goalkeeper)
  - `positionsnummerhv` likely indicates specific field positions (h = right, v = left)
  - These fields are not consistently used in the data but should be preserved

- **Disciplinary Information**:
  - `spelareAntalAckumuleradeVarningar` tracks accumulated warnings/yellow cards
  - This is important for tracking suspensions due to accumulated cards

### Historical Data Handling
- Design tables with minimal required fields
- Use nullable fields for data that might not be available in older records
- Implement validation that's aware of the data's time period

### Indexing Strategy
- Index on `match_id` in all related tables
- Index on `player_id` in the MatchParticipant table
- Composite indexes for common query patterns

## Common Queries

```sql
-- Get all matches for a specific referee
SELECT m.*
FROM matches m
JOIN referee_assignments ra ON m.match_id = ra.match_id
WHERE ra.referee_id = ?;

-- Get all goals in a match
SELECT me.*
FROM match_events me
JOIN event_types et ON me.event_type_id = et.event_type_id
WHERE me.match_id = ? AND et.is_goal = TRUE;

-- Get all cards for a player across all matches
SELECT me.*
FROM match_events me
JOIN event_types et ON me.event_type_id = et.event_type_id
JOIN match_participants mp ON me.participant_id = mp.participant_id
WHERE mp.player_id = ? AND et.is_card = TRUE;

-- Get referee statistics (matches, cards, goals)
SELECT
    r.referee_id,
    p.first_name || ' ' || p.last_name AS referee_name,
    COUNT(DISTINCT ra.match_id) AS total_matches,
    SUM(CASE WHEN et.is_card = TRUE THEN 1 ELSE 0 END) AS total_cards,
    SUM(CASE WHEN et.is_goal = TRUE THEN 1 ELSE 0 END) AS total_goals
FROM referees r
JOIN persons p ON r.person_id = p.person_id
JOIN referee_assignments ra ON r.referee_id = ra.referee_id
JOIN matches m ON ra.match_id = m.match_id
LEFT JOIN match_events me ON m.match_id = me.match_id
LEFT JOIN event_types et ON me.event_type_id = et.event_type_id
WHERE ra.role_id = 1  -- Main referee
GROUP BY r.referee_id, referee_name;
```

## Future Enhancements

1. Add support for additional event types as they are discovered
2. Implement views for common statistics queries
3. Add indexes based on query performance analysis
4. Consider partitioning for large datasets (e.g., by season)
