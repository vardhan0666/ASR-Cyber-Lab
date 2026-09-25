"""Role-based authorization dependencies built on top of get_current_active_user."""

from typing import Callable

from fastapi import Depends

from app.core.exceptions import ForbiddenError
from app.models.user import User, UserRole
from app.security.auth import get_current_active_user


def require_role(*allowed_roles: UserRole) -> Callable[..., User]:
    """Dependency factory: returns a FastAPI dependency that only allows
    requests from users whose role is in allowed_roles.

    Usage:
        @router.post("/targets", dependencies=[Depends(require_analyst_or_admin)])
    """

    def dependency(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            allowed_names = ", ".join(role.value for role in allowed_roles)
            raise ForbiddenError(
                f"This action requires one of the following roles: {allowed_names}"
            )
        return current_user

    return dependency


# Pre-built dependencies for the most common authorization checks used
# across route modules (Batches 6-7).
require_admin = require_role(UserRole.ADMIN)
require_analyst_or_admin = require_role(UserRole.ADMIN, UserRole.ANALYST)