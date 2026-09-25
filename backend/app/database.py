"""
SQLAlchemy engine, session factory, and declarative base.

This module intentionally has no dependency on FastAPI so it can be
imported safely by Alembic migrations, services, and tests alike.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""

    pass


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a DB session and guarantees closure."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()