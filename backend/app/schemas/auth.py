"""Authentication request/response schemas."""

from pydantic import BaseModel, EmailStr

from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class CurrentUserResponse(UserResponse):
    """Response for GET /api/auth/me — identical shape to UserResponse,
    kept as a distinct type for API clarity and future extension."""

    pass