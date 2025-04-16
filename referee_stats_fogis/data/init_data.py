"""Initialize database with default data."""

from referee_stats_fogis.data.base import get_session
from referee_stats_fogis.data.models import EventType, RefereeRole, ResultType


def init_event_types() -> None:
    """Initialize event types in the database."""
    session = get_session()

    # Check if event types already exist
    if session.query(EventType).count() > 0:
        print("Event types already initialized, skipping...")
        return

    # Define event types
    event_types = [
        # Goals
        {"id": 6, "name": "Regular Goal", "is_goal": True, "affects_score": True},
        {"id": 39, "name": "Header Goal", "is_goal": True, "affects_score": True},
        {"id": 28, "name": "Corner Goal", "is_goal": True, "affects_score": True},
        {"id": 29, "name": "Free Kick Goal", "is_goal": True, "affects_score": True},
        {"id": 15, "name": "Own Goal", "is_goal": True, "affects_score": True},
        {
            "id": 14,
            "name": "Penalty Goal",
            "is_goal": True,
            "is_penalty": True,
            "affects_score": True,
        },
        # Penalties
        {"id": 18, "name": "Penalty Missing Goal", "is_penalty": True},
        {"id": 19, "name": "Penalty Save", "is_penalty": True},
        {"id": 26, "name": "Penalty Hitting the Frame", "is_penalty": True},
        # Cards
        {"id": 20, "name": "Yellow Card", "is_card": True},
        {"id": 8, "name": "Red Card (Denying Goal Opportunity)", "is_card": True},
        {"id": 9, "name": "Red Card (Other Reasons)", "is_card": True},
        # Substitutions
        {"id": 16, "name": "Substitution Out", "is_substitution": True},
        {"id": 17, "name": "Substitution In", "is_substitution": True},
        # Control events
        {"id": 31, "name": "Period Start", "is_control_event": True},
        {"id": 32, "name": "Period End", "is_control_event": True},
        {"id": 23, "name": "Match End", "is_control_event": True},
    ]

    # Add event types to the database
    for event_type_data in event_types:
        event_type = EventType(**event_type_data)
        session.add(event_type)

    session.commit()
    print(f"Initialized {len(event_types)} event types")


def init_result_types() -> None:
    """Initialize result types in the database."""
    session = get_session()

    # Check if result types already exist
    if session.query(ResultType).count() > 0:
        print("Result types already initialized, skipping...")
        return

    # Define result types
    result_types = [
        {"id": 1, "name": "Final Result"},
        {"id": 2, "name": "Half-time Result"},
        {"id": 3, "name": "Extra Time Result"},
        {"id": 4, "name": "Penalty Shootout Result"},
    ]

    # Add result types to the database
    for result_type_data in result_types:
        result_type = ResultType(**result_type_data)
        session.add(result_type)

    session.commit()
    print(f"Initialized {len(result_types)} result types")


def init_referee_roles() -> None:
    """Initialize referee roles in the database."""
    session = get_session()

    # Check if referee roles already exist
    if session.query(RefereeRole).count() > 0:
        print("Referee roles already initialized, skipping...")
        return

    # Define referee roles
    referee_roles = [
        {"id": 1, "name": "Huvuddomare", "short_name": "Dom"},
        {"id": 2, "name": "Assisterande 1", "short_name": "AD1"},
        {"id": 3, "name": "Assisterande 2", "short_name": "AD2"},
        {"id": 4, "name": "Fjärdedomare", "short_name": "4th"},
    ]

    # Add referee roles to the database
    for role_data in referee_roles:
        role = RefereeRole(**role_data)
        session.add(role)

    session.commit()
    print(f"Initialized {len(referee_roles)} referee roles")


def init_all() -> None:
    """Initialize all default data in the database."""
    init_event_types()
    init_result_types()
    init_referee_roles()
    print("Database initialization complete")


if __name__ == "__main__":
    init_all()
