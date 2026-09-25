"""Report generation request/response schemas."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.report import ReportFormat


class ReportGenerateRequest(BaseModel):
    scan_id: uuid.UUID
    format: ReportFormat


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    scan_id: uuid.UUID
    generated_by_id: uuid.UUID
    format: ReportFormat
    file_path: Optional[str] = None
    created_at: datetime