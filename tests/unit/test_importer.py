"""Tests for data import functionality."""

import json
import os
import tempfile
from unittest import mock

import pytest
from sqlalchemy.orm import Session

from referee_stats_fogis.core.importer import DataImporter
from referee_stats_fogis.data.models import (
    Competition,
    Match,
    MatchResult,
    Person,
    Referee,
    RefereeAssignment,
    Venue,
)


@pytest.fixture
def mock_session() -> mock.MagicMock:
    """Create a mock database session."""
    return mock.MagicMock(spec=Session)


@pytest.fixture
def importer(mock_session: mock.MagicMock) -> DataImporter:
    """Create a data importer with a mock session."""
    return DataImporter(mock_session)


@pytest.fixture
def sample_match_json():
    """Sample match JSON data for testing."""
    return {
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
                "namn": "Test Referee",
            }
        ]
    }


@pytest.fixture
def sample_result_json():
    """Sample match result JSON data for testing."""
    return {
        "__type": "Svenskfotboll.Fogis.Web.FogisMobilDomarKlient.MatchresultatJSON",
        "matchresultatid": 4660867,
        "matchid": 6169913,
        "matchresultattypid": 1,
        "matchresultattypnamn": "Slutresultat",
        "matchlag1mal": 2,
        "matchlag2mal": 2
    }


def test_import_from_csv(importer: DataImporter) -> None:
    """Test importing data from a CSV file."""
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
        temp_file.write(b"name,age,city\nJohn,30,New York\nJane,25,Boston\n")
        temp_path = temp_file.name

    try:
        # Import the data
        record_count = importer.import_from_csv(temp_path)

        # Check the result
        assert record_count == 2
    finally:
        # Clean up
        os.unlink(temp_path)


@mock.patch("referee_stats_fogis.core.importer.get_session")
def test_import_match_json(mock_get_session, sample_match_json):
    """Test importing match data from JSON."""
    # Create a mock session
    mock_session = mock.MagicMock(spec=Session)
    mock_get_session.return_value = mock_session

    # Mock query results
    mock_session.query.return_value.filter.return_value.first.return_value = None

    # Create a temporary JSON file
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
        temp_file.write(json.dumps([sample_match_json]).encode("utf-8"))
        temp_file_path = temp_file.name

    try:
        # Import the data
        with DataImporter(session=mock_session) as importer:
            count = importer.import_from_json(temp_file_path)

        # Check that the correct number of records was imported
        assert count == 1

        # Check that the session was used correctly
        assert mock_session.add.call_count > 0
        assert mock_session.commit.call_count == 1

    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)


@mock.patch("referee_stats_fogis.core.importer.get_session")
def test_import_result_json(mock_get_session, sample_result_json):
    """Test importing match result data from JSON."""
    # Create a mock session
    mock_session = mock.MagicMock(spec=Session)
    mock_get_session.return_value = mock_session

    # Mock query results - match exists
    mock_match = mock.MagicMock(spec=Match)
    mock_match.id = 1
    mock_match.fogis_id = str(sample_result_json["matchid"])

    # Set up the mock to return the match when queried
    def mock_query_side_effect(*args, **kwargs):
        mock_filter = mock.MagicMock()
        mock_filter.first.return_value = mock_match
        return mock_filter

    mock_session.query.return_value.filter.side_effect = mock_query_side_effect

    # Create a temporary JSON file
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
        temp_file.write(json.dumps([sample_result_json]).encode("utf-8"))
        temp_file_path = temp_file.name

    try:
        # Import the data
        with DataImporter(session=mock_session) as importer:
            count = importer.import_from_json(temp_file_path)

        # Check that the correct number of records was imported
        assert count == 1

        # Check that the session was used correctly
        assert mock_session.add.call_count > 0
        assert mock_session.commit.call_count == 1

    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)
