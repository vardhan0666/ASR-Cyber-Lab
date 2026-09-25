"""
Scan creation, execution, and history endpoints.

Scans are created synchronously (fast DB write, with authorization checked
immediately) and executed asynchronously via a background task, since
Nmap scans can take from seconds to several minutes depending on the
selected profile. Clients should poll GET /scans/{id} to observe status
transitions (pending -> running -> completed/failed).
"""

import uuid
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database import SessionLocal, get_db
from app.models.scan import Scan, ScanStatus
from app.models.user import User
from app.schemas.scan import ScanCreate, ScanResponse
from app.security.auth import get_current_active_user
from app.security.permissions import require_analyst_or_admin
from app.services import scan_orchestrator

router = APIRouter(prefix="/scans", tags=["scans"])


def _run_scan_background(scan_id: uuid.UUID) -> None:
    """Execute a scan in a dedicated DB session, independent of the
    original request's session lifecycle."""
    db = SessionLocal()
    try:
        scan_orchestrator.execute_scan(db, scan_id)
    finally:
        db.close()


@router.post("", response_model=ScanResponse, status_code=201)
def create_scan(
    payload: ScanCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin),
) -> ScanResponse:
    """Create and launch a new scan against an authorized target.

    Raises 404 if the target does not exist, 403 if it is not authorized
    for scanning, and 409 if a scan is already pending/running for it.
    """
    scan = scan_orchestrator.create_scan(
        db,
        target_id=payload.target_id,
        profile=payload.profile,
        initiated_by_id=current_user.id,
    )
    background_tasks.add_task(_run_scan_background, scan.id)
    return ScanResponse.model_validate(scan)


@router.get("", response_model=List[ScanResponse])
def list_scans(
    target_id: Optional[uuid.UUID] = Query(None),
    status: Optional[ScanStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[ScanResponse]:
    """List scans, optionally filtered by target and/or status, newest first."""
    query = db.query(Scan)
    if target_id is not None:
        query = query.filter(Scan.target_id == target_id)
    if status is not None:
        query = query.filter(Scan.status == status)

    scans = query.order_by(Scan.created_at.desc()).offset(skip).limit(limit).all()
    return [ScanResponse.model_validate(s) for s in scans]


@router.get("/{scan_id}", response_model=ScanResponse)
def get_scan(
    scan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ScanResponse:
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if scan is None:
        raise NotFoundError("Scan not found")
    return ScanResponse.model_validate(scan)