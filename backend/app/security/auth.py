"""Authentication logic: credential verification and current-user resolution."""

import uuid as uuid_lib
from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError
from app.database import get_db
from app.models.user import User
from app.security.jwt_handler import decode_access_token
from app.security.password import verify_password

# tokenUrl is used only for OpenAPI docs' "Authorize" button; the actual
# route is registered in app/api/routes/auth.py (Batch 6).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Look up a user by email and verify their password.

    Returns None on ANY failure (unknown email, wrong password, disabled
    account) — callers must never reveal which specific check failed, to
    avoid user-enumeration.
    """
    normalized_email = email.lower().strip()
    user = db.query(User).filter(User.email == normalized_email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the currently authenticated user from a bearer JWT.

    Raises UnauthorizedError for any of: missing token, invalid/expired
    token, malformed subject claim, or unknown/disabled user.
    """
    credentials_error = UnauthorizedError("Could not validate credentials")

    if not token:
        raise credentials_error

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_error

    raw_subject = payload.get("sub")
    if raw_subject is None:
        raise credentials_error

    try:
        user_uuid = uuid_lib.UUID(str(raw_subject))
    except (ValueError, TypeError):
        raise credentials_error

    user = db.query(User).filter(User.id == user_uuid).first()
    if user is None:
        raise credentials_error
    if not user.is_active:
        raise UnauthorizedError("User account is disabled")

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Thin wrapper kept as its own dependency for clarity at call sites and
    to allow future extension (e.g., MFA/step-up auth) without touching
    every route signature."""
    if not current_user.is_active:
        raise UnauthorizedError("User account is disabled")
    return current_user