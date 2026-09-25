"""
Optional AI-assisted finding explanation endpoint.

AI is optional assistance only and is never treated as a source of truth.
This endpoint sends only evidence already computed and stored by the
deterministic risk engine/config analysis to the (optionally configured)
AI provider, and always returns that same evidence alongside any generated
text so the response can be independently verified.
"""

import json
import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database import get_db
from app.models.finding import Finding
from app.models.user import User
from app.models.vulnerability import Vulnerability
from app.security.auth import get_current_active_user
from app.services.ai_service import explain_finding_evidence, is_ai_enabled

router = APIRouter(prefix="/ai", tags=["ai"])


class AIExplainResponse(BaseModel):
    finding_id: uuid.UUID
    available: bool
    summary: Optional[str] = None
    note: str
    evidence_used: Dict[str, Any]


class AIStatusResponse(BaseModel):
    enabled: bool
    note: str


def _safe_json_loads(value: Optional[str], default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def _build_finding_evidence(db: Session, finding: Finding) -> Dict[str, Any]:
    """Assemble the exact, already-computed evidence for a finding — no
    new evidence is generated here."""
    vulnerabilities = (
        db.query(Vulnerability).filter(Vulnerability.finding_id == finding.id).all()
    )

    return {
        "title": finding.title,
        "description": finding.description,
        "category": finding.category.value,
        "severity": finding.severity.value,
        "risk_score": finding.risk_score,
        "risk_explanation": _safe_json_loads(finding.risk_explanation, []),
        "evidence": _safe_json_loads(finding.evidence, {}),
        "status": finding.status.value,
        "remediation": finding.remediation,
        "vulnerabilities": [
            {
                "cve_id": v.cve_id,
                "cvss_score": v.cvss_score,
                "data_available": v.data_available,
                "source": v.source,
            }
            for v in vulnerabilities
        ],
    }


@router.get("/status", response_model=AIStatusResponse)
def get_ai_status(current_user: User = Depends(get_current_active_user)) -> AIStatusResponse:
    """Report whether optional AI assistance is currently enabled/configured."""
    enabled = is_ai_enabled()
    return AIStatusResponse(
        enabled=enabled,
        note=(
            "AI assistance is enabled and configured."
            if enabled
            else "AI assistance is disabled or not configured. All findings, "
            "risk scores, and remediation are produced by the deterministic "
            "risk engine regardless of this setting."
        ),
    )


@router.post("/findings/{finding_id}/explain", response_model=AIExplainResponse)
def explain_finding(
    finding_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AIExplainResponse:
    """Generate an optional, evidence-bound AI summary of a finding. If AI
    is disabled or unavailable, this explicitly reports that instead of
    fabricating an explanation."""
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if finding is None:
        raise NotFoundError("Finding not found")

    evidence_payload = _build_finding_evidence(db, finding)
    result = explain_finding_evidence(evidence_payload)

    return AIExplainResponse(
        finding_id=finding.id,
        available=result.available,
        summary=result.summary,
        note=result.note,
        evidence_used=result.evidence_used,
    )