"""Database interface for the referee stats application."""

import sqlite3
from pathlib import Path
from typing import Any, Generic, List, Optional, TypeVar, Union

from referee_stats_fogis.config import config
from referee_stats_fogis.data.models import Person

T = TypeVar("T")


class Database:
    """Database interface for the referee stats application."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        """Initialize the database interface.

        Args:
            db_path: Path to the database file. If None, uses the path from config.
        """
        if db_path is None:
            db_path = config.get("database.path")

        # Ensure the directory exists
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._initialize_db()

    def _initialize_db(self) -> None:
        """Initialize the database schema if it doesn't exist."""
        cursor = self.conn.cursor()

        # Create tables
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS person (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                fogis_id TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS team (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                fogis_id TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS match (
                id INTEGER PRIMARY KEY,
                date TEXT NOT NULL,
                home_team_id INTEGER NOT NULL,
                away_team_id INTEGER NOT NULL,
                competition TEXT NOT NULL,
                venue TEXT NOT NULL,
                fogis_id TEXT,
                home_goals INTEGER,
                away_goals INTEGER,
                FOREIGN KEY (home_team_id) REFERENCES team (id),
                FOREIGN KEY (away_team_id) REFERENCES team (id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS match_official (
                id INTEGER PRIMARY KEY,
                match_id INTEGER NOT NULL,
                person_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                FOREIGN KEY (match_id) REFERENCES match (id),
                FOREIGN KEY (person_id) REFERENCES person (id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS card (
                id INTEGER PRIMARY KEY,
                match_id INTEGER NOT NULL,
                person_id INTEGER NOT NULL,
                card_type TEXT NOT NULL,
                minute INTEGER,
                reason TEXT,
                FOREIGN KEY (match_id) REFERENCES match (id),
                FOREIGN KEY (person_id) REFERENCES person (id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS goal (
                id INTEGER PRIMARY KEY,
                match_id INTEGER NOT NULL,
                scorer_id INTEGER NOT NULL,
                team_id INTEGER NOT NULL,
                minute INTEGER,
                penalty BOOLEAN NOT NULL,
                own_goal BOOLEAN NOT NULL,
                FOREIGN KEY (match_id) REFERENCES match (id),
                FOREIGN KEY (scorer_id) REFERENCES person (id),
                FOREIGN KEY (team_id) REFERENCES team (id)
            )
            """
        )

        self.conn.commit()

    def close(self) -> None:
        """Close the database connection."""
        self.conn.close()

    def __enter__(self) -> "Database":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager."""
        self.close()


class Repository(Generic[T]):
    """Generic repository for database operations."""

    def __init__(self, db: Database, model_class: type[T], table_name: str) -> None:
        """Initialize the repository.

        Args:
            db: Database instance
            model_class: Model class
            table_name: Table name
        """
        self.db = db
        self.model_class = model_class
        self.table_name = table_name

    def create(self, entity: T) -> int:
        """Create a new entity in the database.

        Args:
            entity: Entity to create

        Returns:
            ID of the created entity
        """
        # Implementation would depend on the specific model
        raise NotImplementedError

    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Get an entity by ID.

        Args:
            entity_id: Entity ID

        Returns:
            Entity if found, None otherwise
        """
        cursor = self.db.conn.cursor()
        cursor.execute(
            f"SELECT * FROM {self.table_name} WHERE id = ?",
            (entity_id,),
        )
        row = cursor.fetchone()
        if row:
            return self._row_to_entity(row)
        return None

    def get_all(self) -> List[T]:
        """Get all entities.

        Returns:
            List of entities
        """
        cursor = self.db.conn.cursor()
        cursor.execute(f"SELECT * FROM {self.table_name}")
        rows = cursor.fetchall()
        return [self._row_to_entity(row) for row in rows]

    def _row_to_entity(self, row: sqlite3.Row) -> T:
        """Convert a database row to an entity.

        Args:
            row: Database row

        Returns:
            Entity
        """
        # Implementation would depend on the specific model
        raise NotImplementedError


# Specific repositories could be implemented for each model
class PersonRepository(Repository[Person]):
    """Repository for Person entities."""

    def __init__(self, db: Database) -> None:
        """Initialize the repository.

        Args:
            db: Database instance
        """
        super().__init__(db, Person, "person")

    def create(self, entity: Person) -> int:
        """Create a new person in the database.

        Args:
            entity: Person to create

        Returns:
            ID of the created person
        """
        cursor = self.db.conn.cursor()
        cursor.execute(
            "INSERT INTO person (name, fogis_id) VALUES (?, ?)",
            (entity.name, entity.fogis_id),
        )
        self.db.conn.commit()
        return cursor.lastrowid or 0

    def _row_to_entity(self, row: sqlite3.Row) -> Person:
        """Convert a database row to a Person entity.

        Args:
            row: Database row

        Returns:
            Person entity
        """
        return Person(
            id=row["id"],
            name=row["name"],
            fogis_id=row["fogis_id"],
        )
