"""
Authentication endpoints: login, current-user identification, and
admin-managed user registration.

Note: there is no public/open self-registration endpoint. The very first
administrator account is created automatically at application startup from
INITIAL_ADMIN_EMAIL / INITIAL_ADMIN_PASSWORD environment variables (see
app.main._bootstrap_initial_admin), only when the users table is empty.
All subsequent accounts must be created by an existing administrator via
POST /auth/register.

Note on Swagger UI: the "Authorize" button uses OAuth2PasswordBearer's
tokenUrl for documentation purposes, but this API's /auth/login endpoint
accepts JSON (not form-encoded credentials) for consistency with the rest
of the API. Obtain a token via POST /auth/login and paste it into the
"Authorize" dialog as a bearer token.
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.exceptions import ConflictError, UnauthorizedError
from app.database import get_db
from app.models.user import User
from app.schemas.auth import CurrentUserResponse, LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.security.auth import authenticate_user, get_current_active_user
from app.security.jwt_handler import create_access_token
from app.security.password import hash_password
from app.security.permissions import require_admin
from app.services.audit_service import log_action

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


def _client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest, request: Request, db: Session = Depends(get_db)
) -> TokenResponse:
    """Authenticate with email/password and receive a JWT access token."""
    user = authenticate_user(db, payload.email, payload.password)

    if user is None:
        log_action(
            db,
            action="auth.login_failed",
            user_id=None,
            resource_type="user",
            resource_id=payload.email,
            ip_address=_client_ip(request),
        )
        raise UnauthorizedError("Incorrect email or password")

    token = create_access_token(
        subject=str(user.id), extra_claims={"role": user.role.value}
    )

    log_action(
        db,
        action="auth.login_success",
        user_id=user.id,
        resource_type="user",
        resource_id=str(user.id),
        ip_address=_client_ip(request),
    )

    return TokenResponse(
        access_token=token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=CurrentUserResponse)
def get_me(current_user: User = Depends(get_current_active_user)) -> CurrentUserResponse:
    """Return the currently authenticated user's profile."""
    return CurrentUserResponse.model_validate(current_user)


@router.post("/register", response_model=UserResponse, status_code=201)
def register_user(
    payload: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> UserResponse:
    """Create a new user account. Restricted to administrators."""
    normalized_email = payload.email.lower().strip()
    existing = db.query(User).filter(User.email == normalized_email).first()
    if existing is not None:
        raise ConflictError("A user with this email already exists")

    new_user = User(
        email=normalized_email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    log_action(
        db,
        action="user.created",
        user_id=current_user.id,
        resource_type="user",
        resource_id=str(new_user.id),
        details={"created_email": normalized_email, "role": payload.role.value},
        ip_address=_client_ip(request),
    )

    return UserResponse.model_validate(new_user)