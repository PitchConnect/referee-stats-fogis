# Example Data Files

This directory contains example data files that can be used with the data import functionality of the Referee Stats FOGIS application.

## JSON Examples

- `match.json`: Example of match data
- `match_result.json`: Example of match result data
- `match_event.json`: Example of match event data (e.g., goals, cards)
- `match_participant.json`: Example of match participant data (players, staff)

## CSV Examples

- `players.csv`: Example of player data in CSV format

## Usage

You can use these example files to test the data import functionality:

```bash
# Import match data
referee-stats-fogis import examples/match.json

# Import match result data
referee-stats-fogis import examples/match_result.json

# Import match event data
referee-stats-fogis import examples/match_event.json

# Import match participant data
referee-stats-fogis import examples/match_participant.json

# Import player data from CSV
referee-stats-fogis import examples/players.csv
```

For more information about the data import functionality, see the [Data Import Documentation](../docs/data_import.md).
