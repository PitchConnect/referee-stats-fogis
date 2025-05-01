"""Statistics generation for the referee stats application."""

from typing import Any

from sqlalchemy import desc, func

from referee_stats_fogis.data.base import get_session
from referee_stats_fogis.data.models import (
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
    Team,
)


def get_referee_stats(db: Any, referee_id: int) -> dict[str, Any]:
    """Get statistics for a specific referee.

    Args:
        db: Database instance (can be either Database or Session)
        referee_id: ID of the referee

    Returns:
        Dictionary of statistics
    """
    # If db is a Database instance, get a session
    session = _get_session(db)

    # Get the referee
    referee = session.query(Referee).filter_by(id=referee_id).first()
    if not referee:
        return {
            "error": f"Referee with ID {referee_id} not found",
            "total_matches": 0,
            "yellow_cards": 0,
            "red_cards": 0,
            "goals": 0,
            "most_common_co_officials": [],
            "most_carded_players": [],
        }

    # Get total matches
    total_matches = (
        session.query(func.count(RefereeAssignment.id))
        .filter(RefereeAssignment.referee_id == referee_id)
        .scalar()
        or 0
    )

    # Get matches refereed
    match_ids = (
        session.query(RefereeAssignment.match_id)
        .filter(RefereeAssignment.referee_id == referee_id)
        .all()
    )
    match_ids_list = [m[0] for m in match_ids]

    # Get yellow cards
    yellow_cards = (
        session.query(func.count(MatchEvent.id))
        .join(EventType, MatchEvent.event_type_id == EventType.id)
        .filter(
            MatchEvent.match_id.in_(match_ids_list),
            EventType.is_card.is_(True),
            EventType.name.like("%Yellow%"),
        )
        .scalar()
        or 0
    )

    # Get red cards
    red_cards = (
        session.query(func.count(MatchEvent.id))
        .join(EventType, MatchEvent.event_type_id == EventType.id)
        .filter(
            MatchEvent.match_id.in_(match_ids_list),
            EventType.is_card.is_(True),
            EventType.name.like("%Red%"),
        )
        .scalar()
        or 0
    )

    # Get goals
    goals = (
        session.query(func.count(MatchEvent.id))
        .join(EventType, MatchEvent.event_type_id == EventType.id)
        .filter(
            MatchEvent.match_id.in_(match_ids_list),
            EventType.is_goal.is_(True),
        )
        .scalar()
        or 0
    )

    return {
        "total_matches": total_matches,
        "yellow_cards": yellow_cards,
        "red_cards": red_cards,
        "goals": goals,
        "most_common_co_officials": get_most_common_co_officials(db, referee_id),
        "most_carded_players": get_most_carded_players(db, referee_id),
    }


def get_most_common_co_officials(
    db: Any, referee_id: int, limit: int = 5
) -> list[tuple[int, str, int]]:
    """Get the most common co-officials for a referee.

    Args:
        db: Database instance (can be either Database or Session)
        referee_id: ID of the referee
        limit: Maximum number of co-officials to return

    Returns:
        List of tuples containing (official_id, official_name, count)
    """
    # If db is a Database instance, get a session
    session = _get_session(db)

    # Get matches where the referee was assigned
    referee_matches = (
        session.query(RefereeAssignment.match_id)
        .filter(RefereeAssignment.referee_id == referee_id)
        .subquery()
    )

    # Get co-officials from those matches
    co_officials = (
        session.query(
            Referee.id,
            Person.first_name,
            Person.last_name,
            func.count(RefereeAssignment.id).label("count"),
        )
        .join(RefereeAssignment, Referee.id == RefereeAssignment.referee_id)
        .join(Person, Referee.person_id == Person.id)
        .filter(
            RefereeAssignment.match_id.in_(referee_matches),
            Referee.id != referee_id,
        )
        .group_by(Referee.id)
        .order_by(desc("count"))
        .limit(limit)
        .all()
    )

    # Format the results
    return [(r[0], f"{r[1]} {r[2]}", r[3]) for r in co_officials]


def get_most_carded_players(
    db: Any, referee_id: int, limit: int = 5
) -> list[tuple[int, str, int]]:
    """Get the most carded players for a referee.

    Args:
        db: Database instance (can be either Database or Session)
        referee_id: ID of the referee
        limit: Maximum number of players to return

    Returns:
        List of tuples containing (player_id, player_name, card_count)
    """
    # If db is a Database instance, get a session
    session = _get_session(db)

    # Get matches where the referee was assigned
    referee_matches = (
        session.query(RefereeAssignment.match_id)
        .filter(RefereeAssignment.referee_id == referee_id)
        .subquery()
    )

    # Get players with the most cards in those matches
    carded_players = (
        session.query(
            Person.id,
            Person.first_name,
            Person.last_name,
            func.count(MatchEvent.id).label("card_count"),
        )
        .join(MatchParticipant, Person.id == MatchParticipant.player_id)
        .join(MatchEvent, MatchParticipant.id == MatchEvent.participant_id)
        .join(EventType, MatchEvent.event_type_id == EventType.id)
        .filter(
            MatchEvent.match_id.in_(referee_matches),
            EventType.is_card.is_(True),
        )
        .group_by(Person.id)
        .order_by(desc("card_count"))
        .limit(limit)
        .all()
    )

    # Format the results
    return [(p[0], f"{p[1]} {p[2]}", p[3]) for p in carded_players]


def get_player_stats(db: Any, player_id: int) -> dict[str, Any]:
    """Get statistics for a specific player.

    Args:
        db: Database instance (can be either Database or Session)
        player_id: ID of the player

    Returns:
        Dictionary of statistics
    """
    # If db is a Database instance, get a session
    session = _get_session(db)

    # Get the player
    player = session.query(Person).filter_by(id=player_id).first()
    if not player:
        return {
            "error": f"Player with ID {player_id} not found",
            "total_matches": 0,
            "goals": 0,
            "yellow_cards": 0,
            "red_cards": 0,
            "teams": [],
        }

    # Get total matches
    total_matches = (
        session.query(func.count(MatchParticipant.id))
        .filter(MatchParticipant.player_id == player_id)
        .scalar()
        or 0
    )

    # Get goals
    goals = (
        session.query(func.count(MatchEvent.id))
        .join(MatchParticipant, MatchEvent.participant_id == MatchParticipant.id)
        .join(EventType, MatchEvent.event_type_id == EventType.id)
        .filter(
            MatchParticipant.player_id == player_id,
            EventType.is_goal.is_(True),
        )
        .scalar()
        or 0
    )

    # Get yellow cards
    yellow_cards = (
        session.query(func.count(MatchEvent.id))
        .join(MatchParticipant, MatchEvent.participant_id == MatchParticipant.id)
        .join(EventType, MatchEvent.event_type_id == EventType.id)
        .filter(
            MatchParticipant.player_id == player_id,
            EventType.is_card.is_(True),
            EventType.name.like("%Yellow%"),
        )
        .scalar()
        or 0
    )

    # Get red cards
    red_cards = (
        session.query(func.count(MatchEvent.id))
        .join(MatchParticipant, MatchEvent.participant_id == MatchParticipant.id)
        .join(EventType, MatchEvent.event_type_id == EventType.id)
        .filter(
            MatchParticipant.player_id == player_id,
            EventType.is_card.is_(True),
            EventType.name.like("%Red%"),
        )
        .scalar()
        or 0
    )

    # Get teams the player has played for
    teams = (
        session.query(
            Team.id, Team.name, func.count(MatchParticipant.id).label("matches")
        )
        .join(MatchTeam, Team.id == MatchTeam.team_id)
        .join(MatchParticipant, MatchTeam.id == MatchParticipant.match_team_id)
        .filter(MatchParticipant.player_id == player_id)
        .group_by(Team.id)
        .order_by(desc("matches"))
        .all()
    )

    # Format the teams
    teams_list = [{"id": t[0], "name": t[1], "matches": t[2]} for t in teams]

    return {
        "total_matches": total_matches,
        "goals": goals,
        "yellow_cards": yellow_cards,
        "red_cards": red_cards,
        "teams": teams_list,
    }


def get_team_stats(db: Any, team_id: int) -> dict[str, Any]:
    """Get statistics for a specific team.

    Args:
        db: Database instance (can be either Database or Session)
        team_id: ID of the team

    Returns:
        Dictionary of statistics
    """
    # If db is a Database instance, get a session
    session = _get_session(db)

    # Get the team
    team = session.query(Team).filter_by(id=team_id).first()
    if not team:
        return {
            "error": f"Team with ID {team_id} not found",
            "total_matches": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goals_for": 0,
            "goals_against": 0,
            "most_common_opponents": [],
            "top_scorers": [],
        }

    # Get match teams for this team
    match_teams = (
        session.query(MatchTeam.id, MatchTeam.match_id, MatchTeam.is_home_team)
        .filter(MatchTeam.team_id == team_id)
        .all()
    )

    # Get match IDs
    match_ids = [mt[1] for mt in match_teams]
    match_team_ids = [mt[0] for mt in match_teams]

    # Create a mapping of match_id to is_home_team
    is_home_team_map = {mt[1]: mt[2] for mt in match_teams}

    # Get total matches
    total_matches = len(match_ids)

    # Get match results
    match_results = (
        session.query(
            MatchResult.match_id,
            MatchResult.home_goals,
            MatchResult.away_goals,
        )
        .filter(MatchResult.match_id.in_(match_ids))
        .all()
    )

    # Calculate wins, draws, losses, goals for, goals against
    wins = 0
    draws = 0
    losses = 0
    goals_for = 0
    goals_against = 0

    for mr in match_results:
        match_id, home_goals, away_goals = mr
        is_home = is_home_team_map.get(match_id, False)

        if is_home:
            goals_for += home_goals
            goals_against += away_goals
            if home_goals > away_goals:
                wins += 1
            elif home_goals == away_goals:
                draws += 1
            else:
                losses += 1
        else:
            goals_for += away_goals
            goals_against += home_goals
            if away_goals > home_goals:
                wins += 1
            elif away_goals == home_goals:
                draws += 1
            else:
                losses += 1

    # Get most common opponents
    opponents = (
        session.query(
            Team.id,
            Team.name,
            func.count(MatchTeam.id).label("matches"),
        )
        .join(MatchTeam, Team.id == MatchTeam.team_id)
        .filter(
            MatchTeam.match_id.in_(match_ids),
            MatchTeam.team_id != team_id,
        )
        .group_by(Team.id)
        .order_by(desc("matches"))
        .limit(5)
        .all()
    )

    # Format the opponents
    opponents_list = [{"id": o[0], "name": o[1], "matches": o[2]} for o in opponents]

    # Get top scorers
    top_scorers = (
        session.query(
            Person.id,
            Person.first_name,
            Person.last_name,
            func.count(MatchEvent.id).label("goals"),
        )
        .join(MatchParticipant, Person.id == MatchParticipant.player_id)
        .join(MatchEvent, MatchParticipant.id == MatchEvent.participant_id)
        .join(EventType, MatchEvent.event_type_id == EventType.id)
        .filter(
            MatchParticipant.match_team_id.in_(match_team_ids),
            EventType.is_goal.is_(True),
        )
        .group_by(Person.id)
        .order_by(desc("goals"))
        .limit(5)
        .all()
    )

    # Format the top scorers
    scorers_list = [
        {"id": s[0], "name": f"{s[1]} {s[2]}", "goals": s[3]} for s in top_scorers
    ]

    return {
        "total_matches": total_matches,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "goals_for": goals_for,
        "goals_against": goals_against,
        "most_common_opponents": opponents_list,
        "top_scorers": scorers_list,
    }


def get_match_stats(db: Any, match_id: int) -> dict[str, Any]:
    """Get statistics for a specific match.

    Args:
        db: Database instance (can be either Database or Session)
        match_id: ID of the match

    Returns:
        Dictionary of statistics
    """
    # If db is a Database instance, get a session
    session = _get_session(db)

    # Get the match
    match = session.query(Match).filter_by(id=match_id).first()
    if not match:
        return {
            "error": f"Match with ID {match_id} not found",
            "home_team": "",
            "away_team": "",
            "score": "0-0",
            "officials": [],
            "cards": [],
            "goals": [],
        }

    # Get match teams
    match_teams = (
        session.query(MatchTeam, Team)
        .join(Team, MatchTeam.team_id == Team.id)
        .filter(MatchTeam.match_id == match_id)
        .all()
    )

    home_team = ""
    away_team = ""
    home_team_id = 0
    away_team_id = 0

    for mt, team in match_teams:
        if mt.is_home_team:
            home_team = team.name
            home_team_id = team.id
        else:
            away_team = team.name
            away_team_id = team.id

    # Get match result
    match_result = (
        session.query(MatchResult).filter(MatchResult.match_id == match_id).first()
    )

    score = "0-0"
    if match_result:
        score = f"{match_result.home_goals}-{match_result.away_goals}"

    # Get officials
    officials = (
        session.query(
            Referee.id,
            Person.first_name,
            Person.last_name,
            RefereeRole.name,
        )
        .join(RefereeAssignment, Referee.id == RefereeAssignment.referee_id)
        .join(Person, Referee.person_id == Person.id)
        .join(RefereeRole, RefereeAssignment.role_id == RefereeRole.id)
        .filter(RefereeAssignment.match_id == match_id)
        .all()
    )

    # Format the officials
    officials_list = [
        {
            "id": o[0],
            "name": f"{o[1]} {o[2]}",
            "role": o[3],
        }
        for o in officials
    ]

    # Get cards
    cards = (
        session.query(
            MatchEvent.id,
            Person.first_name,
            Person.last_name,
            Team.name,
            EventType.name,
            MatchEvent.minute,
        )
        .join(MatchParticipant, MatchEvent.participant_id == MatchParticipant.id)
        .join(Person, MatchParticipant.player_id == Person.id)
        .join(MatchTeam, MatchEvent.match_team_id == MatchTeam.id)
        .join(Team, MatchTeam.team_id == Team.id)
        .join(EventType, MatchEvent.event_type_id == EventType.id)
        .filter(
            MatchEvent.match_id == match_id,
            EventType.is_card.is_(True),
        )
        .all()
    )

    # Format the cards
    cards_list = [
        {
            "id": c[0],
            "player": f"{c[1]} {c[2]}",
            "team": c[3],
            "type": c[4],
            "minute": c[5],
        }
        for c in cards
    ]

    # Get goals
    goals = (
        session.query(
            MatchEvent.id,
            Person.first_name,
            Person.last_name,
            Team.name,
            MatchEvent.minute,
            EventType.is_penalty,
        )
        .join(MatchParticipant, MatchEvent.participant_id == MatchParticipant.id)
        .join(Person, MatchParticipant.player_id == Person.id)
        .join(MatchTeam, MatchEvent.match_team_id == MatchTeam.id)
        .join(Team, MatchTeam.team_id == Team.id)
        .join(EventType, MatchEvent.event_type_id == EventType.id)
        .filter(
            MatchEvent.match_id == match_id,
            EventType.is_goal.is_(True),
        )
        .all()
    )

    # Format the goals
    goals_list = [
        {
            "id": g[0],
            "scorer": f"{g[1]} {g[2]}",
            "team": g[3],
            "minute": g[4],
            "is_penalty": g[5],
        }
        for g in goals
    ]

    return {
        "home_team": home_team,
        "away_team": away_team,
        "home_team_id": home_team_id,
        "away_team_id": away_team_id,
        "score": score,
        "officials": officials_list,
        "cards": cards_list,
        "goals": goals_list,
    }


def _get_session(db: Any) -> Any:
    """Get a SQLAlchemy session from the database instance.

    Args:
        db: Database instance (can be either Database or Session)

    Returns:
        SQLAlchemy session or mock
    """
    # For testing, if db has a _get_session method, use it
    if hasattr(db, "_get_session"):
        return db

    # For normal operation
    if hasattr(db, "conn"):
        # It's a Database instance, create a new session
        return get_session()
    else:
        # It's already a session
        return db  # type: ignore
