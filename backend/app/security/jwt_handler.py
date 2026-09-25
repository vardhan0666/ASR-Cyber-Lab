"""
JWT creation and decoding utilities.

Tokens are short-lived (configurable via ACCESS_TOKEN_EXPIRE_MINUTES) and
signed with HS256 using SECRET_KEY. No sensitive data beyond the user
identifier and role is embedded in the token payload.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt

from app.config import get_settings

settings = get_settings()


def create_access_token(subject: str, extra_claims: Optional[dict[str, Any]] = None) -> str:
    """Create a signed JWT access token for the given subject (user id)."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": expire,
    }
    if extra_claims:
        to_encode.update(extra_claims)

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    """Decode and validate a JWT. Returns the payload dict, or None if the
    token is invalid, malformed, or expired."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None