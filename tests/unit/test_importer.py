"""Tests for data import functionality."""

import datetime
import json
import os
import tempfile
from unittest import mock

import pytest
from sqlalchemy.orm import Session

from referee_stats_fogis.core.importer import DataImporter
from referee_stats_fogis.data.models import (
    EventType,
    Match,
    MatchEvent,
    MatchParticipant,
    MatchResult,
    MatchTeam,
    ResultType,
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
def sample_match_json() -> dict:
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
        ],
    }


@pytest.fixture
def sample_result_json() -> dict:
    """Sample match result JSON data for testing."""
    return {
        "__type": "Svenskfotboll.Fogis.Web.FogisMobilDomarKlient.MatchresultatJSON",
        "matchresultatid": 4660867,
        "matchid": 6169913,
        "matchresultattypid": 1,
        "matchresultattypnamn": "Slutresultat",
        "matchlag1mal": 2,
        "matchlag2mal": 2,
    }


@pytest.fixture
def sample_event_json() -> dict:
    """Sample match event JSON data for testing."""
    return {
        "__type": "Svenskfotboll.Fogis.Web.FogisMobilDomarKlient.MatchhandelseJSON",
        "matchhandelseid": 12345,
        "matchid": 6169913,
        "matchhandelsetypid": 1,
        "matchhandelsetypnamn": "Mål",
        "matchhandelsetypmedforstallningsandring": True,
        "matchdeltagareid": 67890,
        "matchlagid": 54321,
        "matchminut": 45,
        "period": 1,
        "kommentar": "Test comment",
        "hemmamal": 1,
        "bortamal": 0,
        "planpositionx": 50,
        "planpositiony": 50,
        "relateradTillMatchhandelseID": 0,
    }


@pytest.fixture
def sample_participant_json() -> dict:
    """Sample match participant JSON data for testing."""
    return {
        "__type": "Svenskfotboll.Fogis.Web.FogisMobilDomarKlient.MatchdeltagareJSON",
        "matchdeltagareid": 67890,
        "matchid": 6169913,
        "matchlagid": 54321,
        "spelareid": 12345,
        "personid": 12345,
        "personnamn": "Test Player",
        "fornamn": "Test",
        "efternamn": "Player",
        "trojnummer": 10,
        "lagkapten": True,
        "ersattare": False,
        "byte1": 0,
        "byte2": 75,
        "arSpelandeLedare": False,
        "ansvarig": False,
        "spelareAntalAckumuleradeVarningar": 1,
        "spelareAvstangningBeskrivning": "",
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
def test_import_match_json(
    mock_get_session: mock.MagicMock, sample_match_json: dict
) -> None:
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


def test_determine_data_type(importer: DataImporter) -> None:
    """Test determining data type from JSON data."""
    # Test with list of items with __type
    data = [{"__type": "TestType", "value": 1}, {"__type": "TestType", "value": 2}]
    data_type, normalized_data = importer._determine_data_type(data)
    assert data_type == "TestType"
    assert normalized_data == data

    # Test with single item with __type
    data = {"__type": "SingleType", "value": 1}
    data_type, normalized_data = importer._determine_data_type(data)
    assert data_type == "SingleType"
    assert normalized_data == [data]

    # Test with list of items without __type
    data = [{"value": 1}, {"value": 2}]
    data_type, normalized_data = importer._determine_data_type(data)
    assert data_type == ""
    assert normalized_data == data

    # Test with single item without __type
    data = {"value": 1}
    data_type, normalized_data = importer._determine_data_type(data)
    assert data_type == ""
    assert normalized_data == [data]

    # Test with unsupported data format
    data = "not a dict or list"
    data_type, normalized_data = importer._determine_data_type(data)
    assert data_type == ""
    assert normalized_data == []


def test_parse_date(importer: DataImporter) -> None:
    """Test parsing date strings."""
    # Test with valid date
    date_str = "2025-04-11"
    result = importer._parse_date(date_str)
    assert isinstance(result, datetime.datetime)
    assert result.year == 2025
    assert result.month == 4
    assert result.day == 11

    # Test with invalid date
    date_str = "invalid-date"
    result = importer._parse_date(date_str)
    assert isinstance(result, datetime.datetime)
    # Should return current date
    assert result.year >= 2023  # This test will work for many years


def test_extract_season(importer: DataImporter) -> None:
    """Test extracting season from competition name."""
    # Test with year in the name
    competition_name = "Div 2 Västra Götaland, herr 2025"
    result = importer._extract_season(competition_name)
    assert result == "2025"

    # Test without year in the name
    competition_name = "Div 2 Västra Götaland, herr"
    result = importer._extract_season(competition_name)
    assert result == ""


def test_validate_match_result_data(importer: DataImporter, sample_result_json: dict) -> None:
    """Test validating match result data."""
    # Test with valid data
    is_valid, error_message, match_id, result_type_id = importer._validate_match_result_data(
        sample_result_json
    )
    assert is_valid is True
    assert error_message is None
    assert match_id == sample_result_json["matchid"]
    assert result_type_id == sample_result_json["matchresultattypid"]

    # Test with missing match ID
    invalid_data = sample_result_json.copy()
    del invalid_data["matchid"]
    is_valid, error_message, match_id, result_type_id = importer._validate_match_result_data(
        invalid_data
    )
    assert is_valid is False
    assert error_message is not None
    assert match_id is None
    assert result_type_id is None

    # Test with missing result type ID
    invalid_data = sample_result_json.copy()
    del invalid_data["matchresultattypid"]
    is_valid, error_message, match_id, result_type_id = importer._validate_match_result_data(
        invalid_data
    )
    assert is_valid is False
    assert error_message is not None
    assert match_id is None
    assert result_type_id is None


def test_validate_match_event_data(importer: DataImporter, sample_event_json: dict) -> None:
    """Test validating match event data."""
    # Test with valid data
    is_valid, error_message, extracted_data = importer._validate_match_event_data(
        sample_event_json
    )
    assert is_valid is True
    assert error_message is None
    assert extracted_data["match_id"] == sample_event_json["matchid"]
    assert extracted_data["event_type_id"] == sample_event_json["matchhandelsetypid"]
    assert extracted_data["participant_id"] == sample_event_json["matchdeltagareid"]
    assert extracted_data["match_team_id"] == sample_event_json["matchlagid"]

    # Test with missing match ID
    invalid_data = sample_event_json.copy()
    del invalid_data["matchid"]
    is_valid, error_message, extracted_data = importer._validate_match_event_data(
        invalid_data
    )
    assert is_valid is False
    assert error_message is not None
    assert extracted_data == {}

    # Test with missing event type ID
    invalid_data = sample_event_json.copy()
    del invalid_data["matchhandelsetypid"]
    is_valid, error_message, extracted_data = importer._validate_match_event_data(
        invalid_data
    )
    assert is_valid is False
    assert error_message is not None
    assert extracted_data == {}


def test_extract_event_details(importer: DataImporter, sample_event_json: dict) -> None:
    """Test extracting event details."""
    details = importer._extract_event_details(sample_event_json)
    assert details["minute"] == sample_event_json["matchminut"]
    assert details["period"] == sample_event_json["period"]
    assert details["comment"] == sample_event_json["kommentar"]
    assert details["home_score"] == sample_event_json["hemmamal"]
    assert details["away_score"] == sample_event_json["bortamal"]
    assert details["position_x"] == sample_event_json["planpositionx"]
    assert details["position_y"] == sample_event_json["planpositiony"]
    assert details["related_event_id"] is None  # 0 should be converted to None

    # Test with non-zero related event ID
    modified_data = sample_event_json.copy()
    modified_data["relateradTillMatchhandelseID"] = 123
    details = importer._extract_event_details(modified_data)
    assert details["related_event_id"] == 123


@mock.patch("referee_stats_fogis.core.importer.get_session")
def test_import_result_json(
    mock_get_session: mock.MagicMock, sample_result_json: dict
) -> None:
    """Test importing match result data from JSON."""
    # Create a mock session
    mock_session = mock.MagicMock(spec=Session)
    mock_get_session.return_value = mock_session

    # Mock query results - match exists
    mock_match = mock.MagicMock(spec=Match)
    mock_match.id = 1
    mock_match.fogis_id = str(sample_result_json["matchid"])

    # Create different query responses based on the queried class
    def mock_query_side_effect(queried_class: type) -> mock.MagicMock:
        mock_query = mock.MagicMock()

        def mock_filter_side_effect(*args: object, **kwargs: object) -> mock.MagicMock:
            mock_filter = mock.MagicMock()

            if queried_class == Match:
                mock_filter.first.return_value = mock_match
            elif queried_class == ResultType:
                # Return None for ResultType to trigger creation of a new one
                mock_filter.first.return_value = None
            else:
                mock_filter.first.return_value = None

            return mock_filter

        mock_query.filter.side_effect = mock_filter_side_effect
        return mock_query

    mock_session.query.side_effect = mock_query_side_effect

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
