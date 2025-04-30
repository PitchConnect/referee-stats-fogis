"""Data import functionality for the referee stats application."""

import datetime
import logging
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from referee_stats_fogis.data.base import get_session
from referee_stats_fogis.data.models import (
    Club,
    Competition,
    CompetitionCategory,
    EventType,
    Match,
    MatchEvent,
    MatchParticipant,
    MatchResult,
    MatchTeam,
    Person,
    Referee,
    RefereeAssignment,
    RefereeRole,
    ResultType,
    Team,
    Venue,
)
from referee_stats_fogis.utils.file_utils import read_csv, read_json

logger = logging.getLogger(__name__)


class DataImporter:
    """Data importer for the referee stats application."""

    def __init__(self, session: Session | None = None) -> None:
        """Initialize the data importer.

        Args:
            session: SQLAlchemy session. If None, a new session will be created.
        """
        self.session = session or get_session()

    def __enter__(self) -> "DataImporter":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager."""
        if exc_type is not None:
            self.session.rollback()
        self.session.close()

    def import_from_csv(self, file_path: str | Path) -> int:
        """Import data from a CSV file.

        Args:
            file_path: Path to the CSV file

        Returns:
            Number of records imported
        """
        logger.info(f"Importing data from CSV file: {file_path}")

        # Read the CSV file
        data = read_csv(file_path)

        # Process the data
        # This is a placeholder implementation
        # In a real implementation, we would parse the data and insert it into the DB

        logger.info(f"Imported {len(data)} records from CSV file")
        return len(data)

    def _determine_data_type(self, data: Any) -> tuple[str, Any]:
        """Determine the type of data and normalize it to a list if needed.

        Args:
            data: Data from the JSON file

        Returns:
            Tuple of (data_type, normalized_data)
        """
        if isinstance(data, list) and len(data) > 0:
            # Check the type of data based on the first item
            if "__type" in data[0]:
                return data[0]["__type"], data
            else:
                logger.warning("Data does not contain __type field")
                return "", data
        elif isinstance(data, dict):
            # Single item
            if "__type" in data:
                return data["__type"], [data]
            else:
                logger.warning("Data does not contain __type field")
                return "", [data]
        else:
            logger.warning(f"Unsupported data format: {type(data)}")
            return "", []

    def _process_data_by_type(self, data_type: str, data: list[dict[str, Any]]) -> int:
        """Process data based on its type.

        Args:
            data_type: Type of the data
            data: Data to process

        Returns:
            Number of records imported
        """
        if "MatchJSON" in data_type:
            return self._import_matches(data)
        elif "MatchresultatJSON" in data_type:
            return self._import_match_results(data)
        elif "MatchhandelseJSON" in data_type:
            return self._import_match_events(data)
        elif "MatchdeltagareJSON" in data_type:
            return self._import_match_participants(data)
        else:
            logger.warning(f"Unknown data type: {data_type}")
            return 0

    def import_from_json(self, file_path: str | Path) -> int:
        """Import data from a JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            Number of records imported
        """
        logger.info(f"Importing data from JSON file: {file_path}")

        # Read the JSON file
        data = read_json(file_path)

        # Determine the type of data and process accordingly
        record_count = 0

        try:
            data_type, normalized_data = self._determine_data_type(data)
            if data_type:
                record_count = self._process_data_by_type(data_type, normalized_data)

            # Commit the changes
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error importing data: {e}")
            raise

        logger.info(f"Imported {record_count} records from JSON file")
        return record_count

    def _import_matches(self, data: list[dict[str, Any]]) -> int:
        """Import match data.

        Args:
            data: List of match data dictionaries

        Returns:
            Number of matches imported
        """
        logger.info(f"Importing {len(data)} matches")
        imported_count = 0

        for match_data in data:
            try:
                # Extract match data
                match_id = match_data.get("matchid")
                if not match_id:
                    logger.warning("Match data missing matchid, skipping")
                    continue

                # Check if match already exists
                existing_match = (
                    self.session.query(Match)
                    .filter(Match.fogis_id == str(match_id))
                    .first()
                )

                # Process venue
                venue = self._get_or_create_venue(match_data)

                # Process competition
                competition = self._get_or_create_competition(match_data)

                # Process teams
                home_team = self._get_or_create_team(match_data, is_home=True)
                away_team = self._get_or_create_team(match_data, is_home=False)

                # Parse date and time
                match_date = self._parse_date(match_data.get("speldatum", ""))
                match_time = match_data.get("avsparkstid", "")

                # Create or update match
                if existing_match:
                    # Update existing match
                    existing_match.match_nr = match_data.get("matchnr", "")
                    existing_match.date = match_date
                    existing_match.time = match_time
                    existing_match.venue_id = venue.id if venue else None
                    existing_match.competition_id = (
                        competition.id if competition else None
                    )
                    existing_match.football_type_id = match_data.get("fotbollstypid", 1)
                    existing_match.spectators = match_data.get("antalaskadare")
                    existing_match.status = "normal"  # Default status
                    existing_match.is_walkover = match_data.get("wo", False)
                    match = existing_match
                else:
                    # Create new match
                    match = Match(
                        match_nr=match_data.get("matchnr", ""),
                        date=match_date,
                        time=match_time,
                        venue_id=venue.id if venue else None,
                        competition_id=competition.id if competition else None,
                        football_type_id=match_data.get("fotbollstypid", 1),
                        spectators=match_data.get("antalaskadare"),
                        status="normal",  # Default status
                        is_walkover=match_data.get("wo", False),
                        fogis_id=str(match_id),
                    )
                    self.session.add(match)
                    self.session.flush()  # Flush to get the match ID

                # Create or update match teams
                self._create_or_update_match_teams(match, home_team, away_team)

                # Process referee assignments
                if (
                    "domaruppdraglista" in match_data
                    and match_data["domaruppdraglista"]
                ):
                    self._process_referee_assignments(
                        match, match_data["domaruppdraglista"]
                    )

                imported_count += 1

            except Exception as e:
                logger.error(f"Error importing match {match_data.get('matchid')}: {e}")
                # Continue with next match instead of failing the entire import
                continue

        return imported_count

    def _get_or_create_venue(self, match_data: dict[str, Any]) -> Venue | None:
        """Get or create a venue from match data.

        Args:
            match_data: Match data dictionary

        Returns:
            Venue object or None if venue data is missing
        """
        venue_id = match_data.get("anlaggningid")
        venue_name = match_data.get("anlaggningnamn")

        if not venue_id or not venue_name:
            return None

        # Check if venue already exists
        venue = self.session.query(Venue).filter(Venue.id == venue_id).first()

        if venue:
            # Update venue data
            venue.name = venue_name
            venue.latitude = match_data.get("anlaggningLatitud")
            venue.longitude = match_data.get("anlaggningLongitud")
        else:
            # Create new venue
            venue = Venue(
                id=venue_id,
                name=venue_name,
                latitude=match_data.get("anlaggningLatitud"),
                longitude=match_data.get("anlaggningLongitud"),
            )
            self.session.add(venue)
            self.session.flush()

        return venue

    def _get_or_create_competition(
        self, match_data: dict[str, Any]
    ) -> Competition | None:
        """Get or create a competition from match data.

        Args:
            match_data: Match data dictionary

        Returns:
            Competition object or None if competition data is missing
        """
        competition_id = match_data.get("tavlingid")
        competition_name = match_data.get("tavlingnamn")

        if not competition_id or not competition_name:
            return None

        # Check if competition already exists
        competition = (
            self.session.query(Competition)
            .filter(Competition.id == competition_id)
            .first()
        )

        # Get or create competition category
        category_id = match_data.get("tavlingskategoriid")
        category_name = match_data.get("tavlingskategorinamn")

        category = None
        if category_id and category_name:
            category = (
                self.session.query(CompetitionCategory)
                .filter(CompetitionCategory.id == category_id)
                .first()
            )

            if not category:
                category = CompetitionCategory(id=category_id, name=category_name)
                self.session.add(category)
                self.session.flush()

        if competition:
            # Update competition data
            competition.name = competition_name
            competition.season = self._extract_season(competition_name)
            competition.category_id = category.id if category else None
            competition.gender_id = match_data.get("tavlingKonId")
            competition.age_category_id = match_data.get("tavlingAlderskategori")
            competition.fogis_id = match_data.get("tavlingnr")
        else:
            # Create new competition
            competition = Competition(
                id=competition_id,
                name=competition_name,
                season=self._extract_season(competition_name),
                category_id=category.id if category else None,
                gender_id=match_data.get("tavlingKonId"),
                age_category_id=match_data.get("tavlingAlderskategori"),
                fogis_id=match_data.get("tavlingnr"),
            )
            self.session.add(competition)
            self.session.flush()

        return competition

    def _get_or_create_team(
        self, match_data: dict[str, Any], is_home: bool
    ) -> Team | None:
        """Get or create a team from match data.

        Args:
            match_data: Match data dictionary
            is_home: Whether this is the home team

        Returns:
            Team object or None if team data is missing
        """
        prefix = "lag1" if is_home else "lag2"

        team_id = match_data.get(f"{prefix}lagid")
        team_name = match_data.get(f"{prefix}namn")
        club_id = match_data.get(f"{prefix}foreningid")

        if not team_id or not team_name or not club_id:
            return None

        # Check if team already exists
        team = self.session.query(Team).filter(Team.id == team_id).first()

        # Get or create club
        club = self.session.query(Club).filter(Club.id == club_id).first()

        if not club:
            club = Club(
                id=club_id,
                name=(
                    team_name.split(" ")[0] if " " in team_name else team_name
                ),  # Use first part of team name as club name
            )
            self.session.add(club)
            self.session.flush()

        if team:
            # Update team data
            team.name = team_name
            team.club_id = club.id
            team.fogis_id = str(team_id)
        else:
            # Create new team
            team = Team(
                id=team_id, name=team_name, club_id=club.id, fogis_id=str(team_id)
            )
            self.session.add(team)
            self.session.flush()

        return team

    def _create_or_update_match_teams(
        self, match: Match, home_team: Team | None, away_team: Team | None
    ) -> None:
        """Create or update match teams.

        Args:
            match: Match object
            home_team: Home team object
            away_team: Away team object
        """
        if home_team:
            # Check if match team already exists
            home_match_team = (
                self.session.query(MatchTeam)
                .filter(
                    MatchTeam.match_id == match.id, MatchTeam.team_id == home_team.id
                )
                .first()
            )

            if home_match_team:
                # Update match team
                home_match_team.is_home_team = True
            else:
                # Create new match team
                home_match_team = MatchTeam(
                    match_id=match.id, team_id=home_team.id, is_home_team=True
                )
                self.session.add(home_match_team)

        if away_team:
            # Check if match team already exists
            away_match_team = (
                self.session.query(MatchTeam)
                .filter(
                    MatchTeam.match_id == match.id, MatchTeam.team_id == away_team.id
                )
                .first()
            )

            if away_match_team:
                # Update match team
                away_match_team.is_home_team = False
            else:
                # Create new match team
                away_match_team = MatchTeam(
                    match_id=match.id, team_id=away_team.id, is_home_team=False
                )
                self.session.add(away_match_team)

        self.session.flush()

    def _process_referee_assignments(
        self, match: Match, referee_data: list[dict[str, Any]]
    ) -> None:
        """Process referee assignments.

        Args:
            match: Match object
            referee_data: List of referee assignment data dictionaries
        """
        for ref_assignment in referee_data:
            try:
                referee_id = ref_assignment.get("domareid")
                person_id = ref_assignment.get("personid")
                role_id = ref_assignment.get("domarrollid")

                if not referee_id or not person_id or not role_id:
                    logger.warning(f"Missing referee data, skipping: {referee_id}")
                    continue

                # Get or create person
                person = self._get_or_create_person(ref_assignment)

                # Get or create referee
                referee = self._get_or_create_referee(referee_id, person)

                # Get or create referee role
                role = (
                    self.session.query(RefereeRole)
                    .filter(RefereeRole.id == role_id)
                    .first()
                )

                if not role:
                    role_name = ref_assignment.get("domarrollnamn", "Unknown")
                    role_short_name = ref_assignment.get("domarrollkortnamn", "")

                    role = RefereeRole(
                        id=role_id, name=role_name, short_name=role_short_name
                    )
                    self.session.add(role)
                    self.session.flush()

                # Check if assignment already exists
                assignment = (
                    self.session.query(RefereeAssignment)
                    .filter(
                        RefereeAssignment.match_id == match.id,
                        RefereeAssignment.referee_id == referee.id,
                        RefereeAssignment.role_id == role.id,
                    )
                    .first()
                )

                assignment_id = ref_assignment.get("domaruppdragid")

                if assignment:
                    # Update assignment
                    assignment.status = ref_assignment.get("domaruppdragstatusnamn", "")
                    if assignment_id:
                        assignment.fogis_id = str(assignment_id)
                else:
                    # Create new assignment
                    assignment = RefereeAssignment(
                        match_id=match.id,
                        referee_id=referee.id,
                        role_id=role.id,
                        status=ref_assignment.get("domaruppdragstatusnamn", ""),
                        fogis_id=str(assignment_id) if assignment_id else None,
                    )
                    self.session.add(assignment)

            except Exception as e:
                logger.error(f"Error processing referee assignment: {e}")
                # Continue with next assignment instead of failing the entire import
                continue

        self.session.flush()

    def _get_or_create_person(self, data: dict[str, Any]) -> Person:
        """Get or create a person from data.

        Args:
            data: Person data dictionary

        Returns:
            Person object
        """
        person_id = data.get("personid")

        if not person_id:
            raise ValueError("Person data missing personid")

        # Check if person already exists
        person = self.session.query(Person).filter(Person.id == person_id).first()

        # Extract name parts
        full_name = data.get("personnamn", "") or data.get("namn", "")
        first_name = data.get("fornamn", "")
        last_name = data.get("efternamn", "")

        if not first_name and not last_name and full_name:
            # Split full name into first and last name
            name_parts = full_name.split(" ")
            if len(name_parts) > 1:
                first_name = name_parts[0]
                last_name = " ".join(name_parts[1:])
            else:
                first_name = full_name
                last_name = ""

        if person:
            # Update person data
            person.first_name = first_name
            person.last_name = last_name
            person.personal_number = data.get("personnr")
            person.email = data.get("epostadress")
            person.phone = data.get("mobiltelefon")
            person.address = data.get("adress")
            person.postal_code = data.get("postnr")
            person.city = data.get("postort")
            person.country = data.get("land", "Sweden")
        else:
            # Create new person
            person = Person(
                id=person_id,
                first_name=first_name,
                last_name=last_name,
                personal_number=data.get("personnr"),
                email=data.get("epostadress"),
                phone=data.get("mobiltelefon"),
                address=data.get("adress"),
                postal_code=data.get("postnr"),
                city=data.get("postort"),
                country=data.get("land", "Sweden"),
            )
            self.session.add(person)
            self.session.flush()

        return person

    def _get_or_create_referee(self, referee_id: int, person: Person) -> Referee:
        """Get or create a referee.

        Args:
            referee_id: Referee ID
            person: Person object

        Returns:
            Referee object
        """
        # Check if referee already exists
        referee = self.session.query(Referee).filter(Referee.id == referee_id).first()

        if referee:
            # Update referee data
            referee.person_id = person.id
        else:
            # Create new referee
            referee = Referee(id=referee_id, person_id=person.id)
            self.session.add(referee)
            self.session.flush()

        return referee

    def _parse_date(self, date_str: str) -> datetime.datetime:
        """Parse a date string into a datetime object.

        Args:
            date_str: Date string in format YYYY-MM-DD

        Returns:
            Datetime object
        """
        try:
            return datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            # Return current date if parsing fails
            logger.warning(f"Failed to parse date: {date_str}, using current date")
            return datetime.datetime.now()

    def _extract_season(self, competition_name: str) -> str:
        """Extract season from competition name.

        Args:
            competition_name: Competition name

        Returns:
            Season string
        """
        # Try to extract a year from the competition name
        import re

        year_match = re.search(r"\b(20\d{2})\b", competition_name)
        if year_match:
            return year_match.group(1)
        return ""

    def _validate_match_result_data(
        self, result_data: dict[str, Any]
    ) -> tuple[bool, str | None, int | None, int | None]:
        """Validate match result data and extract key fields.

        Args:
            result_data: Match result data dictionary

        Returns:
            Tuple of (is_valid, error_message, match_id, result_type_id)
        """
        match_id = result_data.get("matchid")
        result_type_id = result_data.get("matchresultattypid")

        if not match_id or not result_type_id:
            error_msg = "Match result data missing required fields, skipping"
            return False, error_msg, None, None

        return True, None, match_id, result_type_id

    def _get_or_create_result_type(
        self, result_type_id: int, result_data: dict[str, Any]
    ) -> ResultType:
        """Get or create a result type.

        Args:
            result_type_id: Result type ID
            result_data: Match result data dictionary

        Returns:
            ResultType object
        """
        result_type = (
            self.session.query(ResultType)
            .filter(ResultType.id == result_type_id)
            .first()
        )

        if not result_type:
            result_type_name = result_data.get("matchresultattypnamn", "Unknown")
            result_type = ResultType(id=result_type_id, name=result_type_name)
            self.session.add(result_type)
            self.session.flush()

        return result_type

    def _find_existing_result(
        self, result_id: int | None, match_id: int, result_type_id: int
    ) -> MatchResult | None:
        """Find an existing match result.

        Args:
            result_id: Result ID
            match_id: Match ID
            result_type_id: Result type ID

        Returns:
            MatchResult object or None if not found
        """
        existing_result = None

        if result_id:
            existing_result = (
                self.session.query(MatchResult)
                .filter(MatchResult.id == result_id)
                .first()
            )

        if not existing_result:
            # Also check by match and result type
            existing_result = (
                self.session.query(MatchResult)
                .filter(
                    MatchResult.match_id == match_id,
                    MatchResult.result_type_id == result_type_id,
                )
                .first()
            )

        return existing_result

    def _import_match_results(self, data: list[dict[str, Any]]) -> int:
        """Import match results data.

        Args:
            data: List of match result data dictionaries

        Returns:
            Number of match results imported
        """
        logger.info(f"Importing {len(data)} match results")
        imported_count = 0

        for result_data in data:
            try:
                # Validate data
                validation_result = self._validate_match_result_data(result_data)
                is_valid, error_message, match_id, result_type_id = validation_result
                if not is_valid:
                    logger.warning(error_message)
                    continue

                # Check if match exists
                match = (
                    self.session.query(Match)
                    .filter(Match.fogis_id == str(match_id))
                    .first()
                )

                if not match:
                    logger.warning(f"Match ID {match_id} not found, skipping result")
                    continue

                # Get or create result type
                result_type = self._get_or_create_result_type(
                    result_type_id, result_data
                )

                # Check if result already exists
                result_id = result_data.get("matchresultatid")
                existing_result = self._find_existing_result(
                    result_id, match.id, result_type.id
                )

                # Get goals
                home_goals = result_data.get("matchlag1mal", 0)
                away_goals = result_data.get("matchlag2mal", 0)

                if existing_result:
                    # Update existing result
                    existing_result.home_goals = home_goals
                    existing_result.away_goals = away_goals
                    if result_id:
                        existing_result.fogis_id = str(result_id)
                else:
                    # Create new result
                    new_result = MatchResult(
                        id=result_id if result_id else None,
                        match_id=match.id,
                        result_type_id=result_type.id,
                        home_goals=home_goals,
                        away_goals=away_goals,
                        fogis_id=str(result_id) if result_id else None,
                    )
                    self.session.add(new_result)

                imported_count += 1

            except Exception as e:
                logger.error(f"Error importing match result: {e}")
                # Continue with next result instead of failing the entire import
                continue

        return imported_count

    def _validate_match_event_data(
        self, event_data: dict[str, Any]
    ) -> tuple[bool, str | None, dict[str, Any]]:
        """Validate match event data and extract key fields.

        Args:
            event_data: Match event data dictionary

        Returns:
            Tuple of (is_valid, error_message, extracted_data)
        """
        match_id = event_data.get("matchid")
        event_type_id = event_data.get("matchhandelsetypid")
        participant_id = event_data.get("matchdeltagareid")
        match_team_id = event_data.get("matchlagid")

        if not match_id or not event_type_id or not participant_id or not match_team_id:
            return False, "Match event data missing required fields, skipping", {}

        extracted_data = {
            "match_id": match_id,
            "event_type_id": event_type_id,
            "participant_id": participant_id,
            "match_team_id": match_team_id,
        }
        return True, None, extracted_data

    def _get_or_create_event_type(
        self, event_type_id: int, event_data: dict[str, Any]
    ) -> EventType:
        """Get or create an event type.

        Args:
            event_type_id: Event type ID
            event_data: Match event data dictionary

        Returns:
            EventType object
        """
        event_type = (
            self.session.query(EventType).filter(EventType.id == event_type_id).first()
        )

        if not event_type:
            event_type_name = event_data.get("matchhandelsetypnamn", "Unknown")
            affects_score = event_data.get(
                "matchhandelsetypmedforstallningsandring", False
            )

            # Determine event type properties based on name
            name_lower = event_type_name.lower()
            is_goal = "mål" in name_lower or "goal" in name_lower
            is_penalty = "straff" in name_lower or "penalty" in name_lower
            is_card = "kort" in name_lower or "card" in name_lower
            is_substitution = "byte" in name_lower or "substitution" in name_lower

            event_type = EventType(
                id=event_type_id,
                name=event_type_name,
                is_goal=is_goal,
                is_penalty=is_penalty,
                is_card=is_card,
                is_substitution=is_substitution,
                affects_score=affects_score,
            )
            self.session.add(event_type)
            self.session.flush()

        return event_type

    def _check_event_entities(
        self, match_id: int, participant_id: int, match_team_id: int, event_type_id: int
    ) -> tuple[bool, str | None, Match | None]:
        """Check if all required entities for an event exist.

        Args:
            match_id: Match ID
            participant_id: Participant ID
            match_team_id: Match team ID
            event_type_id: Event type ID

        Returns:
            Tuple of (success, error_message, match)
        """
        # Check if match exists
        match = (
            self.session.query(Match).filter(Match.fogis_id == str(match_id)).first()
        )

        if not match:
            return False, f"Match ID {match_id} not found, skipping event", None

        # Check if match participant exists
        participant = (
            self.session.query(MatchParticipant)
            .filter(MatchParticipant.id == participant_id)
            .first()
        )

        if not participant:
            error_msg = f"Participant ID {participant_id} not found, skipping event"
            return False, error_msg, None

        # Check if match team exists
        match_team = (
            self.session.query(MatchTeam).filter(MatchTeam.id == match_team_id).first()
        )

        if not match_team:
            return False, f"Team ID {match_team_id} not found, skipping event", None

        # Get or create event type
        self._get_or_create_event_type(event_type_id, {})

        return True, None, match

    def _extract_event_details(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """Extract event details from event data.

        Args:
            event_data: Event data dictionary

        Returns:
            Dictionary of event details
        """
        minute = event_data.get("matchminut")
        period = event_data.get("period")
        comment = event_data.get("kommentar", "")
        home_score = event_data.get("hemmamal", 0)
        away_score = event_data.get("bortamal", 0)
        position_x = event_data.get("planpositionx", -1)
        position_y = event_data.get("planpositiony", -1)
        related_event_id = event_data.get("relateradTillMatchhandelseID")

        if related_event_id == 0:
            related_event_id = None

        return {
            "minute": minute,
            "period": period,
            "comment": comment,
            "home_score": home_score,
            "away_score": away_score,
            "position_x": position_x,
            "position_y": position_y,
            "related_event_id": related_event_id,
        }

    def _create_or_update_event(
        self,
        event_data: dict[str, Any],
        match: Match,
        extracted_data: dict[str, Any],
        event_details: dict[str, Any],
    ) -> None:
        """Create or update a match event.

        Args:
            event_data: Event data dictionary
            match: Match object
            extracted_data: Extracted data dictionary
            event_details: Event details dictionary
        """
        event_id = event_data.get("matchhandelseid")
        participant_id = extracted_data["participant_id"]
        event_type_id = extracted_data["event_type_id"]
        match_team_id = extracted_data["match_team_id"]

        # Check if event already exists
        existing_event = None
        if event_id:
            existing_event = (
                self.session.query(MatchEvent).filter(MatchEvent.id == event_id).first()
            )

        if existing_event:
            # Update existing event
            existing_event.match_id = match.id
            existing_event.participant_id = participant_id
            existing_event.event_type_id = event_type_id
            existing_event.match_team_id = match_team_id
            existing_event.minute = event_details["minute"]
            existing_event.period = event_details["period"]
            existing_event.comment = event_details["comment"]
            existing_event.home_score = event_details["home_score"]
            existing_event.away_score = event_details["away_score"]
            existing_event.position_x = event_details["position_x"]
            existing_event.position_y = event_details["position_y"]
            existing_event.related_event_id = event_details["related_event_id"]
            if event_id:
                existing_event.fogis_id = str(event_id)
        else:
            # Create new event
            new_event = MatchEvent(
                id=event_id,
                match_id=match.id,
                participant_id=participant_id,
                event_type_id=event_type_id,
                match_team_id=match_team_id,
                minute=event_details["minute"],
                period=event_details["period"],
                comment=event_details["comment"],
                home_score=event_details["home_score"],
                away_score=event_details["away_score"],
                position_x=event_details["position_x"],
                position_y=event_details["position_y"],
                related_event_id=event_details["related_event_id"],
                fogis_id=str(event_id) if event_id else None,
            )
            self.session.add(new_event)

    def _import_match_events(self, data: list[dict[str, Any]]) -> int:
        """Import match events data.

        Args:
            data: List of match event data dictionaries

        Returns:
            Number of match events imported
        """
        logger.info(f"Importing {len(data)} match events")
        imported_count = 0

        for event_data in data:
            try:
                # Validate data
                validation_result = self._validate_match_event_data(event_data)
                is_valid, error_message, extracted_data = validation_result
                if not is_valid:
                    logger.warning(error_message)
                    continue

                # Check if all required entities exist
                check_result = self._check_event_entities(
                    extracted_data["match_id"],
                    extracted_data["participant_id"],
                    extracted_data["match_team_id"],
                    extracted_data["event_type_id"],
                )
                success, error_message, match = check_result

                if not success:
                    logger.warning(error_message)
                    continue

                # Extract event details
                event_details = self._extract_event_details(event_data)

                # Create or update event
                self._create_or_update_event(
                    event_data, match, extracted_data, event_details
                )

                imported_count += 1

            except Exception as e:
                logger.error(f"Error importing match event: {e}")
                # Continue with next event instead of failing the entire import
                continue

        return imported_count

    def _import_match_participants(self, data: list[dict[str, Any]]) -> int:
        """Import match participants data.

        Args:
            data: List of match participant data dictionaries

        Returns:
            Number of match participants imported
        """
        logger.info(f"Importing {len(data)} match participants")
        imported_count = 0

        for participant_data in data:
            try:
                match_id = participant_data.get("matchid")
                match_team_id = participant_data.get("matchlagid")
                player_id = participant_data.get("spelareid")
                participant_id = participant_data.get("matchdeltagareid")

                if (
                    not match_id
                    or not match_team_id
                    or not player_id
                    or not participant_id
                ):
                    logger.warning(
                        "Match participant data missing required fields, skipping"
                    )
                    continue

                # Check if match exists
                match = (
                    self.session.query(Match)
                    .filter(Match.fogis_id == str(match_id))
                    .first()
                )

                if not match:
                    logger.warning(
                        f"Match with ID {match_id} not found, skipping participant"
                    )
                    continue

                # Check if match team exists
                match_team = (
                    self.session.query(MatchTeam)
                    .filter(MatchTeam.id == match_team_id)
                    .first()
                )

                if not match_team:
                    logger.warning(
                        f"Team ID {match_team_id} not found, skipping participant"
                    )
                    continue

                # Get or create person
                person = self._get_or_create_person(participant_data)

                # Check if participant already exists
                existing_participant = (
                    self.session.query(MatchParticipant)
                    .filter(MatchParticipant.id == participant_id)
                    .first()
                )

                jersey_number = participant_data.get("trojnummer")
                is_captain = participant_data.get("lagkapten", False)
                is_substitute = participant_data.get("ersattare", False)
                substitution_in = participant_data.get("byte1", 0)
                substitution_out = participant_data.get("byte2", 0)

                if substitution_in == 0:
                    substitution_in = None
                if substitution_out == 0:
                    substitution_out = None

                is_playing_leader = participant_data.get("arSpelandeLedare", False)
                is_responsible = participant_data.get("ansvarig", False)
                accumulated_warnings = participant_data.get(
                    "spelareAntalAckumuleradeVarningar", 0
                )
                suspension_description = participant_data.get(
                    "spelareAvstangningBeskrivning", ""
                )

                if existing_participant:
                    # Update existing participant
                    existing_participant.match_id = match.id
                    existing_participant.match_team_id = match_team_id
                    existing_participant.player_id = person.id
                    existing_participant.jersey_number = jersey_number
                    existing_participant.is_captain = is_captain
                    existing_participant.is_substitute = is_substitute
                    existing_participant.substitution_in_minute = substitution_in
                    existing_participant.substitution_out_minute = substitution_out
                    existing_participant.is_playing_leader = is_playing_leader
                    existing_participant.is_responsible = is_responsible
                    existing_participant.accumulated_warnings = accumulated_warnings
                    existing_participant.suspension_description = suspension_description
                else:
                    # Create new participant
                    new_participant = MatchParticipant(
                        id=participant_id,
                        match_id=match.id,
                        match_team_id=match_team_id,
                        player_id=person.id,
                        jersey_number=jersey_number,
                        is_captain=is_captain,
                        is_substitute=is_substitute,
                        substitution_in_minute=substitution_in,
                        substitution_out_minute=substitution_out,
                        is_playing_leader=is_playing_leader,
                        is_responsible=is_responsible,
                        accumulated_warnings=accumulated_warnings,
                        suspension_description=suspension_description,
                    )
                    self.session.add(new_participant)

                imported_count += 1

            except Exception as e:
                logger.error(f"Error importing match participant: {e}")
                # Continue with next participant instead of failing the entire import
                continue

        return imported_count
