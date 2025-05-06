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

The statistics functions are optimized for performance with large datasets. Here are some best practices to ensure optimal performance:

### Pagination

All statistics functions support pagination to limit the amount of data returned:

```bash
# Get team statistics with pagination for opponents and scorers
referee-stats team --id 789 --opponent-limit 10 --opponent-offset 0 --scorer-limit 5 --scorer-offset 0

# Get referee statistics with pagination for co-officials and carded players
referee-stats referee --id 123 --official-limit 5 --official-offset 0 --player-limit 10 --player-offset 0

# Get player statistics with pagination for teams
referee-stats player --id 456 --team-limit 5 --team-offset 0

# Get match statistics with pagination for officials, cards, and goals
referee-stats match --id 101 --official-limit 5 --official-offset 0 --card-limit 10 --card-offset 0 --goal-limit 10 --goal-offset 0
```

For programmatic access, each function supports pagination parameters:

```python
# Get referee statistics with pagination
referee_stats = get_referee_stats(db_session, referee_id=123)

# Get most common co-officials with pagination
co_officials = get_most_common_co_officials(db_session, referee_id=123, limit=5, offset=0)

# Get most carded players with pagination
carded_players = get_most_carded_players(db_session, referee_id=123, limit=5, offset=0)

# Get player statistics with pagination for teams
player_stats = get_player_stats(db_session, player_id=456, team_limit=5, team_offset=0)

# Get team statistics with pagination for opponents and scorers
team_stats = get_team_stats(
    db_session, team_id=789,
    opponent_limit=10, opponent_offset=0,
    scorer_limit=5, scorer_offset=0
)

# Get match statistics with pagination
match_stats = get_match_stats(
    db_session, match_id=101,
    official_limit=5, official_offset=0,
    card_limit=10, card_offset=0,
    goal_limit=10, goal_offset=0
)
```

### Query Optimization

The statistics functions use optimized database queries to minimize the number of database calls:

1. **Subqueries**: Reusing subqueries to avoid redundant database calls
2. **Conditional Aggregation**: Using SQL's conditional aggregation to get multiple counts in a single query
3. **Joins**: Using appropriate joins to fetch related data efficiently
4. **Indexing**: Ensuring that commonly queried fields are properly indexed

### Large Datasets

When working with large datasets, consider these additional tips:

1. **Limit Result Sets**: Always use pagination to limit the amount of data returned
2. **Filter Data**: Use date ranges or other filters to reduce the dataset size
3. **Asynchronous Loading**: For UI applications, load data asynchronously in chunks
4. **Caching**: Consider caching frequently accessed statistics
