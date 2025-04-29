"""Base classes for SQLAlchemy models."""

from typing import Any, Optional

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from referee_stats_fogis.config import config

# Create the SQLAlchemy base class
Base = declarative_base()

# Global session factory
_SessionFactory = None


def get_engine(db_url: str | None = None) -> Any:
    """Get a SQLAlchemy engine.

    Args:
        db_url: Database URL. If None, uses the URL from config.

    Returns:
        SQLAlchemy engine
    """
    if db_url is None:
        db_type = config.get("database.type", "sqlite")
        if db_type == "sqlite":
            db_path = config.get("database.path", "data/referee_stats.db")
            db_url = f"sqlite:///{db_path}"
        elif db_type == "postgresql":
            host = config.get("database.host", "localhost")
            port = config.get("database.port", 5432)
            user = config.get("database.user", "postgres")
            password = config.get("database.password", "")
            database = config.get("database.name", "referee_stats")
            db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    return create_engine(db_url, echo=config.get("database.echo", False))


def init_db(db_url: str | None = None) -> None:
    """Initialize the database.

    Args:
        db_url: Database URL. If None, uses the URL from config.
    """
    global _SessionFactory
    engine = get_engine(db_url)
    _SessionFactory = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)


def get_session() -> Session:
    """Get a database session.

    Returns:
        SQLAlchemy session
    """
    if _SessionFactory is None:
        init_db()
    session_factory = _SessionFactory
    if session_factory is None:
        raise RuntimeError("Session factory is not initialized")
    # Add type annotation to help mypy
    session: Session = session_factory()
    return session
