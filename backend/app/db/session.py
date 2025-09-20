"""
Database connection and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from ..core.config import settings
from ..models.database import Base


class DatabaseManager:
    """Database connection manager."""

    def __init__(self):
        # SQLite specific configuration for development
        if settings.database_url.startswith("sqlite"):
            self.engine = create_engine(
                settings.database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=settings.debug,
            )
        else:
            # PostgreSQL or other databases
            self.engine = create_engine(settings.database_url, echo=settings.debug)

        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()


# Global database manager instance
db_manager = DatabaseManager()


def get_db() -> Session:
    """
    Dependency function to get database session.
    Use this with FastAPI's Depends().
    """
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    db_manager.create_tables()
