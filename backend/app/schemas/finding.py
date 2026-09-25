"""Security finding request/response schemas.

evidence and risk_explanation are stored in the database as JSON-encoded
text (see app/models/finding.py). The field validators below deserialize
them back into native dict/list structures for the API response, and fail
safe (empty dict/list) rather than raising on malformed stored data.
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.finding import FindingCategory, FindingStatus, SeverityLevel


class FindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    scan_id: uuid.UUID
    host_id: Optional[uuid.UUID]
    port_service_id: Optional[uuid.UUID]
    category: FindingCategory
    title: str
    description: str
    evidence: Dict[str, Any]
    severity: SeverityLevel
    risk_score: float
    risk_explanation: List[str]
    status: FindingStatus
    remediation: Optional[str]
    created_at: datetime
    updated_at: datetime

    @field_validator("evidence", mode="before")
    @classmethod
    def parse_evidence(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v

    @field_validator("risk_explanation", mode="before")
    @classmethod
    def parse_risk_explanation(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v


class FindingStatusUpdate(BaseModel):
    status: FindingStatus