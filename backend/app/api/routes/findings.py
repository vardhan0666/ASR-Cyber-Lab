"""Security findings endpoints."""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database import get_db
from app.models.finding import Finding, FindingCategory, FindingStatus, SeverityLevel
from app.models.user import User
from app.schemas.finding import FindingResponse, FindingStatusUpdate
from app.security.auth import get_current_active_user
from app.security.permissions import require_analyst_or_admin
from app.services.audit_service import log_action

router = APIRouter(prefix="/findings", tags=["findings"])


def _client_ip(request: Request) -> Optional[str]:
    return request.client.host if request.client else None


@router.get("", response_model=List[FindingResponse])
def list_findings(
    scan_id: Optional[uuid.UUID] = Query(None),
    host_id: Optional[uuid.UUID] = Query(None),
    severity: Optional[SeverityLevel] = Query(None),
    category: Optional[FindingCategory] = Query(None),
    status: Optional[FindingStatus] = Query(None),
    search: Optional[str] = Query(None, description="Search by finding title"),
    sort_by: str = Query(
        "risk_score", pattern="^(risk_score|created_at|severity|title)$"
    ),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[FindingResponse]:
    """List security findings with filtering, search, sorting, and
    pagination."""
    query = db.query(Finding)

    if scan_id is not None:
        query = query.filter(Finding.scan_id == scan_id)
    if host_id is not None:
        query = query.filter(Finding.host_id == host_id)
    if severity is not None:
        query = query.filter(Finding.severity == severity)
    if category is not None:
        query = query.filter(Finding.category == category)
    if status is not None:
        query = query.filter(Finding.status == status)
    if search:
        query = query.filter(Finding.title.ilike(f"%{search.strip()}%"))

    sort_column = getattr(Finding, sort_by)
    query = query.order_by(
        sort_column.desc() if sort_order == "desc" else sort_column.asc()
    )

    findings = query.offset(skip).limit(limit).all()
    return [FindingResponse.model_validate(f) for f in findings]


@router.get("/{finding_id}", response_model=FindingResponse)
def get_finding(
    finding_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> FindingResponse:
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if finding is None:
        raise NotFoundError("Finding not found")
    return FindingResponse.model_validate(finding)


@router.patch("/{finding_id}/status", response_model=FindingResponse)
def update_finding_status(
    finding_id: uuid.UUID,
    payload: FindingStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin),
) -> FindingResponse:
    """Update the triage status of a finding (e.g. acknowledge, resolve,
    mark as false positive). This does not alter the underlying evidence
    or risk score — only the workflow status."""
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if finding is None:
        raise NotFoundError("Finding not found")

    finding.status = payload.status
    db.add(finding)
    db.commit()
    db.refresh(finding)

    log_action(
        db,
        action="finding.status_updated",
        user_id=current_user.id,
        resource_type="finding",
        resource_id=str(finding.id),
        details={"status": payload.status.value},
        ip_address=_client_ip(request),
    )

    return FindingResponse.model_validate(finding)