"""
Shared pytest fixtures for the backend test suite.

IMPORTANT: The application's models use PostgreSQL-specific column types
(UUID, native ENUM), so tests require a reachable PostgreSQL instance —
they cannot run against SQLite. By default this points at a local
"asr_cyber_lab_test" database; override with the TEST_DATABASE_URL
environment variable to point elsewhere (e.g. the Dockerized Postgres
service used in development).

Required environment variables (SECRET_KEY, ENVIRONMENT, DATABASE_URL) are
set via os.environ.setdefault() BEFORE any `app.*` module is imported,
since app.database reads settings at import time.

Note: INITIAL_ADMIN_EMAIL / INITIAL_ADMIN_PASSWORD must remain unset in
the test environment; otherwise app.main's startup lifespan would attempt
to bootstrap an admin account against the real DATABASE_URL rather than
the isolated test session used by these fixtures.
"""

import os
import uuid
from typing import Generator

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://asr_user:asr_password@localhost:5432/asr_cyber_lab_test",
)

os.environ.setdefault(
    "SECRET_KEY", "test_secret_key_for_pytest_only_do_not_use_in_production"
)
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("DATABASE_URL", TEST_DATABASE_URL)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, event  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402

from app import models as _models  # noqa: E402,F401 - registers all tables on Base.metadata
from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402
from app.security.jwt_handler import create_access_token  # noqa: E402
from app.security.password import hash_password  # noqa: E402

engine = create_engine(TEST_DATABASE_URL, future=True, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, future=True)


@pytest.fixture(scope="session", autouse=True)
def setup_database() -> Generator[None, None, None]:
    """Create all tables once for the test session and drop them afterward."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """Provide a database session isolated via a SAVEPOINT-based nested
    transaction, so that even if application code calls db.commit()
    (which most write endpoints do), the entire test's changes are rolled
    back at teardown."""
    connection = engine.connect()
    outer_transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _restart_savepoint(sess: Session, trans) -> None:
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    session.close()
    outer_transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient with the get_db dependency overridden to use the
    isolated per-test database session."""

    def _override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _create_user(
    db_session: Session,
    email: str,
    role: UserRole,
    password: str = "TestPassword123",
) -> User:
    user = User(
        id=uuid.uuid4(),
        email=email,
        hashed_password=hash_password(password),
        full_name="Test User",
        role=role,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _auth_headers(user: User) -> dict:
    token = create_access_token(
        subject=str(user.id), extra_claims={"role": user.role.value}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def admin_user(db_session: Session) -> User:
    return _create_user(db_session, "admin@test.local", UserRole.ADMIN)


@pytest.fixture()
def analyst_user(db_session: Session) -> User:
    return _create_user(db_session, "analyst@test.local", UserRole.ANALYST)


@pytest.fixture()
def viewer_user(db_session: Session) -> User:
    return _create_user(db_session, "viewer@test.local", UserRole.VIEWER)


@pytest.fixture()
def admin_headers(admin_user: User) -> dict:
    return _auth_headers(admin_user)


@pytest.fixture()
def analyst_headers(analyst_user: User) -> dict:
    return _auth_headers(analyst_user)


@pytest.fixture()
def viewer_headers(viewer_user: User) -> dict:
    return _auth_headers(viewer_user)