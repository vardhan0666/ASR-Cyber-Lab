"""
Central import point for FastAPI dependencies used across API routes.

Route modules should import from here (`from app.dependencies import ...`)
rather than reaching into app.database or app.security directly. This keeps
a single, stable dependency surface and makes it easy to see, at a glance,
every dependency the API layer relies on.
"""

from app.database import get_db
from app.security.auth import get_current_active_user, get_current_user
from app.security.permissions import (
    require_admin,
    require_analyst_or_admin,
    require_role,
)

__all__ = [
    "get_db",
    "get_current_user",
    "get_current_active_user",
    "require_role",
    "require_admin",
    "require_analyst_or_admin",
]