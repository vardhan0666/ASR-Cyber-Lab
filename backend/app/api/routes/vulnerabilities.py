"""Vulnerability/CVE enrichment lookup endpoints (read-only)."""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database import get_db
from app.models.user import User
from app.models.vulnerability import Vulnerability
from app.schemas.vulnerability import VulnerabilityResponse
from app.security.auth import get_current_active_user

router = APIRouter(prefix="/vulnerabilities", tags=["vulnerabilities"])


@router.get("", response_model=List[VulnerabilityResponse])
def list_vulnerabilities(
    finding_id: Optional[uuid.UUID] = Query(None),
    cve_id: Optional[str] = Query(None),
    data_available: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[VulnerabilityResponse]:
    """List vulnerability enrichment results, optionally filtered by
    finding, CVE identifier, or data availability."""
    query = db.query(Vulnerability)

    if finding_id is not None:
        query = query.filter(Vulnerability.finding_id == finding_id)
    if cve_id:
        query = query.filter(Vulnerability.cve_id.ilike(f"%{cve_id.strip()}%"))
    if data_available is not None:
        query = query.filter(Vulnerability.data_available == data_available)

    vulnerabilities = (
        query.order_by(Vulnerability.created_at.desc()).offset(skip).limit(limit).all()
    )
    return [VulnerabilityResponse.model_validate(v) for v in vulnerabilities]


@router.get("/{vulnerability_id}", response_model=VulnerabilityResponse)
def get_vulnerability(
    vulnerability_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> VulnerabilityResponse:
    vulnerability = (
        db.query(Vulnerability).filter(Vulnerability.id == vulnerability_id).first()
    )
    if vulnerability is None:
        raise NotFoundError("Vulnerability record not found")
    return VulnerabilityResponse.model_validate(vulnerability)