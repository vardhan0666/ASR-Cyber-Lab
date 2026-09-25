"""Authorized target request/response schemas."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.core.exceptions import ValidationError as AppValidationError
from app.core.validators import validate_name_field, validate_target_address
from app.models.target import AssetImportance


class TargetBase(BaseModel):
    name: str
    address: str
    description: Optional[str] = None
    asset_importance: AssetImportance = AssetImportance.MEDIUM

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        try:
            return validate_name_field(v, field_name="name")
        except AppValidationError as exc:
            raise ValueError(str(exc.message)) from exc

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        try:
            return validate_target_address(v)
        except AppValidationError as exc:
            raise ValueError(str(exc.message)) from exc


class TargetCreate(TargetBase):
    """Creating a target never sets is_authorized — authorization is a
    separate, explicit action via TargetAuthorizeRequest."""

    pass


class TargetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    asset_importance: Optional[AssetImportance] = None
    is_active: Optional[bool] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            return validate_name_field(v, field_name="name")
        except AppValidationError as exc:
            raise ValueError(str(exc.message)) from exc


class TargetAuthorizeRequest(BaseModel):
    """Explicit authorization toggle. Restricted to admin/analyst roles at
    the route layer (Batch 6)."""

    is_authorized: bool


class TargetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    address: str
    description: Optional[str]
    asset_importance: AssetImportance
    is_authorized: bool
    is_active: bool
    authorized_by_id: Optional[uuid.UUID]
    authorized_at: Optional[datetime]
    created_by_id: uuid.UUID
    created_at: datetime
    updated_at: datetime