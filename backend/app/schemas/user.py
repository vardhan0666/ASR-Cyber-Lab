"""User request/response schemas."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.exceptions import ValidationError as AppValidationError
from app.core.validators import validate_name_field
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.VIEWER

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        try:
            return validate_name_field(v, field_name="full_name")
        except AppValidationError as exc:
            raise ValueError(str(exc.message)) from exc


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            return validate_name_field(v, field_name="full_name")
        except AppValidationError as exc:
            raise ValueError(str(exc.message)) from exc


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime