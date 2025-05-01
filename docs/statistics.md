# Statistics Functionality

This document provides information on how to use the statistics functionality in the Referee Stats FOGIS application.

## Overview

The statistics module provides comprehensive statistics for:
- Referees
- Players
- Teams
- Matches

## CLI Commands

### Referee Statistics

Get statistics for a specific referee:

```bash
referee-stats referee --id <referee_id>
```

Example:
```bash
referee-stats referee --id 123
```

Output:
```
Referee: John Doe
Total Matches: 15
Yellow Cards: 45
Red Cards: 3
Average Cards Per Match: 3.2
```

### Player Statistics

Get statistics for a specific player:

```bash
referee-stats player --id <player_id>
```

Example:
```bash
referee-stats player --id 456
```

Output:
```
Player: Jane Smith
Total Matches: 12
Goals: 7
Yellow Cards: 3
Red Cards: 1
Teams: Team A (10 matches), Team B (2 matches)
```

### Team Statistics

Get statistics for a specific team:

```bash
referee-stats team --id <team_id>
```

Example:
```bash
referee-stats team --id 789
```

Output:
```
Team: Team A
Total Matches: 20
Wins: 12
Draws: 5
Losses: 3
Goals For: 35
Goals Against: 15
Top Scorers:
  - Player One: 10 goals
  - Player Two: 8 goals
Most Played Against:
  - Team B: 4 matches
  - Team C: 3 matches
```

### Match Statistics

Get statistics for a specific match:

```bash
referee-stats match --id <match_id>
```

Example:
```bash
referee-stats match --id 101
```

Output:
```
Match: Team A vs Team B
Date: 2025-04-15
Result: 2-1
Referee: John Doe
Goals:
  - Player One (Team A): 15' 
  - Player Two (Team A): 60' (Penalty)
  - Player Three (Team B): 80'
Cards:
  - Player Four (Team A): Yellow Card (30')
  - Player Five (Team B): Red Card (75')
```

## Python API

You can also access the statistics functionality programmatically:

```python
from referee_stats_fogis.core.stats import (
    get_referee_stats,
    get_player_stats,
    get_team_stats,
    get_match_stats,
)

# Get referee statistics
referee_stats = get_referee_stats(db_session, referee_id=123)

# Get player statistics
player_stats = get_player_stats(db_session, player_id=456)

# Get team statistics
team_stats = get_team_stats(db_session, team_id=789)

# Get match statistics
match_stats = get_match_stats(db_session, match_id=101)
```

## Advanced Usage

### Filtering

Some statistics functions support filtering:

```bash
# Get referee statistics for a specific date range
referee-stats referee --id 123 --from-date 2025-01-01 --to-date 2025-04-30

# Get team statistics for a specific competition
referee-stats team --id 789 --competition "League Cup"
```

### Output Formats

Statistics can be output in different formats:

```bash
# Output as JSON
referee-stats referee --id 123 --format json

# Output as CSV
referee-stats team --id 789 --format csv --output team_stats.csv
```

## Performance Considerations

When working with large datasets, consider using pagination:

```bash
# Get team statistics with pagination
referee-stats team --id 789 --limit 10 --offset 0
```

For programmatic access:

```python
# Get team statistics with pagination
team_stats = get_team_stats(db_session, team_id=789, limit=10, offset=0)
```
