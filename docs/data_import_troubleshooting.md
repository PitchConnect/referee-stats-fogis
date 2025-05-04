# Data Import Troubleshooting Guide

This guide provides detailed information about troubleshooting common issues with the data import functionality in the Referee Stats FOGIS application.

## Table of Contents

1. [Common Errors](#common-errors)
2. [Troubleshooting Process](#troubleshooting-process)
3. [Data Validation Issues](#data-validation-issues)
4. [Database Consistency](#database-consistency)
5. [Common FOGIS Import Pitfalls](#common-fogis-import-pitfalls)
6. [Logging and Debugging](#logging-and-debugging)

## Common Errors

### File Format Errors

#### Error: `Error importing data: File is empty or could not be parsed`

**Cause**: The file is empty or not in a valid JSON/CSV format.

**Solution**:
- Verify that the file is not empty
- For JSON files, use a JSON validator (e.g., [JSONLint](https://jsonlint.com/)) to check the format
- For CSV files, ensure proper delimiter usage and column headers
- Check for encoding issues (use UTF-8 encoding)

**Example Log Output**:
```
ERROR - referee_stats_fogis.core.importer - Error importing data: File is empty or could not be parsed
Traceback (most recent call last):
  File "referee_stats_fogis/core/importer.py", line 123, in import_from_json
    data = read_json(file_path)
  File "referee_stats_fogis/utils/file_utils.py", line 52, in read_json
    return json.load(f)
  File "/usr/lib/python3.10/json/__init__.py", line 293, in load
    return loads(fp.read(),
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

#### Error: `Error importing data: Unsupported file format: .txt`

**Cause**: The file has an unsupported extension.

**Solution**:
- Use only supported file formats: JSON (.json) or CSV (.csv)
- Rename the file with the correct extension if the content is valid

### Data Type Errors

#### Error: `Error importing data: Unknown data type`

**Cause**: The JSON data doesn't contain a recognized `__type` field.

**Solution**:
- Ensure the JSON data includes the `__type` field with one of the following values:
  - `Svenskfotboll.Fogis.Web.FogisMobilDomarKlient.MatchJSON`
  - `Svenskfotboll.Fogis.Web.FogisMobilDomarKlient.MatchresultatJSON`
  - `Svenskfotboll.Fogis.Web.FogisMobilDomarKlient.MatchhandelseJSON`
  - `Svenskfotboll.Fogis.Web.FogisMobilDomarKlient.MatchdeltagareJSON`

**Example of correct JSON data**:
```json
{
  "__type": "Svenskfotboll.Fogis.Web.FogisMobilDomarKlient.MatchJSON",
  "matchid": 6169913,
  "matchnr": "000026015",
  ...
}
```

### Missing Required Fields

#### Error: `Match data missing required fields, skipping`

**Cause**: The data is missing required fields for the specific data type.

**Solution**:
- Ensure all required fields are present in the data
- Required fields for match data:
  - `matchid`
  - `matchnr`
  - `lag1namn` (home team name)
  - `lag2namn` (away team name)
  - `speldatum` (match date)
  - `tavlingnamn` (competition name)

**Example Log Output**:
```
WARNING - referee_stats_fogis.core.importer - Match data missing required fields, skipping
```

#### Error: `Match result data missing required fields, skipping`

**Cause**: The match result data is missing required fields.

**Solution**:
- Ensure the match result data includes:
  - `matchid`
  - `matchresultattypid`

### Reference Errors

#### Error: `Match ID 6169913 not found, skipping result`

**Cause**: The match referenced by a result, event, or participant doesn't exist in the database.

**Solution**:
- Import matches before importing results, events, or participants
- Verify that the match ID exists in the database
- Use the `--dry-run` option to check for references before importing

**Example Log Output**:
```
WARNING - referee_stats_fogis.core.importer - Match ID 6169913 not found, skipping result
```

#### Error: `Match team with ID 54321 not found, skipping participant`

**Cause**: The match team referenced by a participant doesn't exist in the database.

**Solution**:
- Ensure the match has been imported successfully
- Verify that the match team ID is correct

### Duplicate Records

#### Error: `Match with ID 6169913 already exists, updating`

**Cause**: A record with the same ID already exists in the database.

**Solution**:
- This is not an error but a warning that the existing record will be updated
- Use the `--dry-run` option to check for duplicates before importing
- If you don't want to update existing records, filter them out before importing

## Troubleshooting Process

Follow these steps to troubleshoot data import issues:

### 1. Validate Your Data Files

Before attempting to import, validate your data files:

```bash
# Validate JSON files
referee-stats-fogis import matches.json --dry-run

# Validate CSV files
referee-stats-fogis import players.csv --type players --dry-run
```

The `--dry-run` option will parse and validate the data without modifying the database.

### 2. Check the Logs

Enable detailed logging to see more information about the import process:

```bash
# Set log level to DEBUG
export LOG_LEVEL=DEBUG

# Run the import with detailed logging
referee-stats-fogis import matches.json
```

Log files are typically located in:
- Linux/macOS: `~/.local/share/referee-stats-fogis/logs/`
- Windows: `%APPDATA%\referee-stats-fogis\logs\`

### 3. Inspect the Database

Check the database to see if records were imported correctly:

```bash
# Open the SQLite database
sqlite3 ~/.local/share/referee-stats-fogis/database.sqlite

# List tables
.tables

# Count records in a table
SELECT COUNT(*) FROM matches;

# View the most recent records
SELECT * FROM matches ORDER BY id DESC LIMIT 5;
```

### 4. Try Importing in Smaller Batches

If you're having issues with large files, try splitting them into smaller batches:

```bash
# Split a large JSON file into smaller files
python -c "import json; data=json.load(open('large_file.json')); [json.dump(data[i:i+100], open(f'batch_{i//100}.json', 'w'), indent=2) for i in range(0, len(data), 100)]"

# Import each batch separately
for batch in batch_*.json; do
    referee-stats-fogis import "$batch"
done
```

## Data Validation Issues

### JSON Schema Validation

The application validates JSON data against expected schemas. Here are common validation issues:

#### Invalid Data Types

**Example Error**: `Field 'matchid' expected integer but got string '6169913'`

**Solution**:
- Ensure all fields have the correct data types
- Common type issues:
  - IDs should be integers, not strings
  - Dates should be in the format "YYYY-MM-DD"
  - Boolean values should be `true` or `false`, not strings

#### Missing Required Fields

**Example Error**: `Required field 'matchid' is missing`

**Solution**:
- Check the [Data Import Documentation](data_import.md) for the required fields for each data type
- Ensure all required fields are present in your data

### CSV Validation

For CSV files, common validation issues include:

#### Header Row Issues

**Example Error**: `CSV header does not match expected fields`

**Solution**:
- Ensure the CSV file has a header row
- Header names should match the field names in the corresponding JSON format
- Check for typos in header names

#### Data Type Conversion

**Example Error**: `Could not convert value 'abc' to integer for field 'matchid'`

**Solution**:
- Ensure all values in the CSV file have the correct format for their data type
- Use quotes around string values that contain commas or special characters

## Database Consistency

After importing data, it's important to check database consistency to ensure all references are valid.

### Check for Orphaned Records

Records that reference non-existent entities can cause issues:

```sql
-- Check for match results with non-existent matches
SELECT mr.id, mr.fogis_id, mr.match_id
FROM match_results mr
LEFT JOIN matches m ON mr.match_id = m.id
WHERE m.id IS NULL;

-- Check for match events with non-existent matches
SELECT me.id, me.fogis_id, me.match_id
FROM match_events me
LEFT JOIN matches m ON me.match_id = m.id
WHERE m.id IS NULL;

-- Check for match participants with non-existent matches
SELECT mp.id, mp.fogis_id, mp.match_id
FROM match_participants mp
LEFT JOIN matches m ON mp.match_id = m.id
WHERE m.id IS NULL;
```

### Check for Duplicate Records

Duplicate records can cause inconsistencies:

```sql
-- Check for duplicate matches
SELECT fogis_id, COUNT(*) as count
FROM matches
GROUP BY fogis_id
HAVING count > 1;

-- Check for duplicate match results
SELECT match_id, result_type_id, COUNT(*) as count
FROM match_results
GROUP BY match_id, result_type_id
HAVING count > 1;
```

### Fix Database Inconsistencies

If you find inconsistencies, you can fix them using SQL commands:

```sql
-- Delete orphaned match results
DELETE FROM match_results
WHERE match_id NOT IN (SELECT id FROM matches);

-- Delete duplicate match results (keeping the most recent)
DELETE FROM match_results
WHERE id NOT IN (
    SELECT MAX(id)
    FROM match_results
    GROUP BY match_id, result_type_id
);
```

## Common FOGIS Import Pitfalls

### Character Encoding Issues

FOGIS data may contain Swedish characters (å, ä, ö) which can cause encoding issues.

**Symptoms**:
- Garbled text in imported data
- JSON parsing errors

**Solution**:
- Ensure files are saved with UTF-8 encoding
- When exporting data from FOGIS, specify UTF-8 encoding if possible
- For CSV files, add the BOM (Byte Order Mark) if needed: `\ufeff`

### Date Format Differences

FOGIS uses different date formats in different contexts.

**Symptoms**:
- Date parsing errors
- Incorrect dates in the database

**Solution**:
- Ensure dates are in the format "YYYY-MM-DD"
- Convert dates to the correct format before importing
- Example conversion in Python:
  ```python
  from datetime import datetime
  # Convert from DD/MM/YYYY to YYYY-MM-DD
  date_str = "31/12/2023"
  converted_date = datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
  ```

### ID Mismatches

FOGIS may use different IDs for the same entity in different contexts.

**Symptoms**:
- Reference errors when importing related data
- Missing relationships between entities

**Solution**:
- Use the FOGIS ID (`fogis_id`) consistently across all data
- Map IDs correctly when importing from multiple sources
- Create a mapping table if needed to track different ID representations

### Incomplete Data

FOGIS exports may not include all required fields.

**Symptoms**:
- Missing required fields errors
- Incomplete records in the database

**Solution**:
- Check the exported data for completeness before importing
- Add missing fields with default values where appropriate
- Use the `--dry-run` option to identify missing fields

## Logging and Debugging

### Enable Detailed Logging

To get more information about the import process, enable detailed logging:

```bash
# Set log level to DEBUG
export LOG_LEVEL=DEBUG

# Run the import with detailed logging
referee-stats-fogis import matches.json
```

### Log Output Examples

Here are examples of log output for common scenarios:

#### Successful Import

```
INFO - referee_stats_fogis.core.importer - Importing data from JSON file: matches.json
INFO - referee_stats_fogis.core.importer - Importing 10 matches
INFO - referee_stats_fogis.core.importer - Imported 10 records from JSON file
```

#### File Format Error

```
ERROR - referee_stats_fogis.core.importer - Error importing data: File is empty or could not be parsed
Traceback (most recent call last):
  File "referee_stats_fogis/core/importer.py", line 123, in import_from_json
    data = read_json(file_path)
  File "referee_stats_fogis/utils/file_utils.py", line 52, in read_json
    return json.load(f)
  File "/usr/lib/python3.10/json/__init__.py", line 293, in load
    return loads(fp.read(),
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

#### Missing Reference Error

```
WARNING - referee_stats_fogis.core.importer - Match ID 6169913 not found, skipping result
```

#### Data Validation Error

```
WARNING - referee_stats_fogis.core.importer - Match result data missing required fields, skipping
DEBUG - referee_stats_fogis.core.importer - Missing fields: matchid, matchresultattypid
```

### Using the Python Debugger

For advanced troubleshooting, you can use the Python debugger:

```bash
# Install the debugger
pip install ipdb

# Run the import with the debugger
python -m ipdb -c continue -m referee_stats_fogis.cli import matches.json
```

When an error occurs, the debugger will stop at the error location. You can then:
- Examine variables: `print(variable_name)`
- Step through code: `n` (next), `s` (step into), `c` (continue)
- View the call stack: `w` (where)
- Quit the debugger: `q` (quit)

### Creating a Minimal Reproducible Example

If you're having trouble with a specific import, create a minimal example that reproduces the issue:

1. Extract a small subset of your data that shows the problem
2. Create a simple script that imports just this data
3. Run the script with detailed logging enabled

Example script:

```python
#!/usr/bin/env python
from pathlib import Path
from referee_stats_fogis.core.importer import DataImporter
from referee_stats_fogis.data.base import get_session
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create a session
session = get_session()

# Create an importer
with DataImporter(session=session) as importer:
    # Import from JSON
    count = importer.import_from_json("problem_data.json")
    print(f"Imported {count} records")
```

Save this as `debug_import.py` and run it:

```bash
python debug_import.py
```

This will provide detailed information about the import process and any errors that occur.
