# Data Import Functionality

This document provides detailed information about the data import functionality in the Referee Stats FOGIS application.

## Overview

The Referee Stats FOGIS application supports importing data from various sources, primarily from FOGIS (Swedish Football Association's Information System). The import functionality allows you to:

- Import match data
- Import match results
- Import match events (goals, cards, etc.)
- Import match participants (players, staff)

## Supported File Formats

The application supports the following file formats for data import:

- **JSON**: Preferred format for importing data from FOGIS
- **CSV**: Alternative format for importing data from other sources

## Command Line Interface

The application provides a command-line interface for importing data:

```bash
referee-stats-fogis import <file> [--type TYPE] [--dry-run]
```

### Arguments

- `file`: Path to the file to import (required)
- `--type`: Type of data being imported (optional, auto-detected from JSON)
  - Supported types: `match`, `results`, `events`, `players`, `team-staff`
- `--dry-run`: Parse the file but don't modify the database (optional)

### Examples

Import match data from a JSON file:

```bash
referee-stats-fogis import matches.json
```

Import match results with dry run (validation only):

```bash
referee-stats-fogis import results.json --dry-run
```

Import player data with explicit type:

```bash
referee-stats-fogis import players.csv --type players
```

## JSON Format

The application expects JSON files to follow specific formats based on the type of data being imported. Each JSON file should contain either a single object or an array of objects with a `__type` field that indicates the type of data.

### Match Data

Match data should follow this format:

```json
{
  "__type": "Svenskfotboll.Fogis.Web.FogisMobilDomarKlient.MatchJSON",
  "matchid": 6169913,
  "matchnr": "000026015",
  "fotbollstypid": 1,
  "lag1lagid": 61174,
  "lag1foreningid": 11145,
  "lag1namn": "Hestrafors IF",
  "lag2lagid": 30415,
  "lag2foreningid": 9528,
  "lag2namn": "IF Böljan Falkenberg",
  "anlaggningid": 29424,
  "anlaggningnamn": "Bollevi Konstgräs",
  "anlaggningLatitud": 57.71484,
  "anlaggningLongitud": 12.58732,
  "speldatum": "2025-04-11",
  "avsparkstid": "19:00",
  "tavlingid": 123399,
  "tavlingnamn": "Div 2 Västra Götaland, herr 2025",
  "tavlingskategoriid": 728,
  "tavlingskategorinamn": "Division 2, herrar",
  "antalaskadare": 246,
  "domaruppdraglista": [
    {
      "domaruppdragid": 6850301,
      "matchid": 6169913,
      "domarrollid": 1,
      "domarrollnamn": "Huvuddomare",
      "domarrollkortnamn": "Dom",
      "domareid": 6600,
      "personid": 1082017,
      "personnamn": "Test Referee",
      "namn": "Test Referee"
    }
  ]
}
```

### Match Result Data

Match result data should follow this format:

```json
{
  "__type": "Svenskfotboll.Fogis.Web.FogisMobilDomarKlient.MatchresultatJSON",
  "matchresultatid": 4660867,
  "matchid": 6169913,
  "matchresultattypid": 1,
  "matchresultattypnamn": "Slutresultat",
  "matchlag1mal": 2,
  "matchlag2mal": 2
}
```

### Match Event Data

Match event data should follow this format:

```json
{
  "__type": "Svenskfotboll.Fogis.Web.FogisMobilDomarKlient.MatchhandelseJSON",
  "matchhandelseid": 12345678,
  "matchid": 6169913,
  "matchdeltagareid": 87654321,
  "matchlagid": 61174,
  "handelsetypid": 6,
  "handelsetypnamn": "Regular Goal",
  "minut": 23,
  "period": 1,
  "kommentar": "Great shot from outside the box",
  "hemmamal": 1,
  "bortamal": 0,
  "positionx": 75,
  "positiony": 50,
  "relaterad_handelse_id": null
}
```

### Match Participant Data

Match participant data should follow this format:

```json
{
  "__type": "Svenskfotboll.Fogis.Web.FogisMobilDomarKlient.MatchdeltagareJSON",
  "matchdeltagareid": 87654321,
  "matchid": 6169913,
  "matchlagid": 61174,
  "personid": 1234567,
  "fornamn": "John",
  "efternamn": "Doe",
  "personnr": "19900101-1234",
  "epostadress": "john.doe@example.com",
  "mobiltelefon": "0701234567",
  "adress": "Main Street 1",
  "postnr": "12345",
  "postort": "Stockholm",
  "land": "Sweden",
  "tröjnummer": 10,
  "position": "Forward",
  "är_lagkapten": true,
  "är_målvakt": false
}
```

## CSV Format

For CSV imports, the file should have a header row with column names that match the field names in the corresponding JSON format. For example, a match CSV file might look like:

```csv
matchid,matchnr,lag1namn,lag2namn,anlaggningnamn,speldatum,avsparkstid,tavlingnamn
6169913,000026015,Hestrafors IF,IF Böljan Falkenberg,Bollevi Konstgräs,2025-04-11,19:00,Div 2 Västra Götaland herr 2025
6169914,000026016,Team A,Team B,Stadium X,2025-04-12,15:00,Div 2 Västra Götaland herr 2025
```

## Error Handling

### Common Errors

Here are some common errors you might encounter when importing data:

1. **File Format Error**: The file is not in a valid JSON or CSV format.
   - Solution: Check the file format and ensure it's properly formatted.

2. **Missing Required Fields**: The data is missing required fields.
   - Solution: Ensure all required fields are present in the data.

3. **Invalid Data Type**: The data contains fields with invalid types.
   - Solution: Check the data types of all fields.

4. **Duplicate Records**: The data contains records that already exist in the database.
   - Solution: Use the `--dry-run` option to check for duplicates before importing.

5. **Missing Referenced Entities**: The data references entities that don't exist in the database.
   - Solution: Import the referenced entities first.

### Error Messages

The application provides detailed error messages when importing data. Here are some examples:

- `Error importing data: File is empty or could not be parsed`
  - The file is empty or not in a valid format.

- `Error importing data: Unsupported file format: .txt`
  - The file format is not supported. Use JSON or CSV.

- `Error importing data: Unknown data type`
  - The JSON data doesn't contain a recognized `__type` field.

- `Warning: Match ID 6169913 not found, skipping result`
  - The match referenced by a result doesn't exist in the database.

### Detailed Troubleshooting

For a comprehensive guide to troubleshooting data import issues, including:

- Step-by-step debugging approaches
- Examples of log output for common error scenarios
- Solutions for data validation issues
- Database consistency checks
- Common pitfalls when importing data from FOGIS

Please refer to the [Data Import Troubleshooting Guide](data_import_troubleshooting.md).

## Programmatic Usage

You can also use the import functionality programmatically in your Python code:

```python
from referee_stats_fogis.core.importer import DataImporter
from referee_stats_fogis.data.base import get_session

# Create a session
session = get_session()

# Create an importer
with DataImporter(session=session) as importer:
    # Import from JSON
    count = importer.import_from_json("matches.json")
    print(f"Imported {count} records")

    # Import from CSV
    count = importer.import_from_csv("players.csv")
    print(f"Imported {count} records")
```

## Best Practices

1. **Use Dry Run First**: Always use the `--dry-run` option first to validate the data before importing it.

2. **Import in the Right Order**: Import data in the following order to avoid reference errors:
   - Matches
   - Match results
   - Match participants
   - Match events

3. **Back Up Your Database**: Always back up your database before importing large amounts of data.
   ```bash
   # Backup the SQLite database
   cp ~/.local/share/referee-stats-fogis/database.sqlite ~/.local/share/referee-stats-fogis/database.sqlite.backup
   ```

4. **Check Logs**: Check the application logs for warnings and errors during import.
   ```bash
   # View the most recent log file
   tail -f ~/.local/share/referee-stats-fogis/logs/referee-stats-fogis.log
   ```

5. **Validate Data**: Ensure your data is valid and complete before importing it.
   - Use JSON validators for JSON files
   - Use CSV validators for CSV files
   - Check for required fields

6. **Import in Small Batches**: For large datasets, import in smaller batches to make troubleshooting easier.

7. **Verify Database Consistency**: After importing, run consistency checks to ensure all references are valid.
   ```bash
   # Example: Check for orphaned match results
   referee-stats-fogis db-check --orphaned-results
   ```

8. **Document Import Process**: Keep track of what you've imported and any issues encountered for future reference.
