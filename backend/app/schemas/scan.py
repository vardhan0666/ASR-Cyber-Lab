"""Scan job request/response schemas."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.scan import ScanProfile, ScanStatus


class ScanCreate(BaseModel):
    target_id: uuid.UUID
    profile: ScanProfile


class ScanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    target_id: uuid.UUID
    initiated_by_id: uuid.UUID
    profile: ScanProfile
    status: ScanStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime