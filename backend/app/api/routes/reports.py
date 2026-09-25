"""JSON/PDF report generation and download endpoints."""

import os
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database import get_db
from app.models.report import Report, ReportFormat
from app.models.scan import Scan
from app.models.user import User
from app.schemas.report import ReportGenerateRequest, ReportResponse
from app.security.auth import get_current_active_user
from app.security.permissions import require_analyst_or_admin
from app.services import pdf_service, report_service
from app.services.audit_service import log_action

router = APIRouter(prefix="/reports", tags=["reports"])


def _client_ip(request: Request) -> Optional[str]:
    return request.client.host if request.client else None


@router.post("", response_model=ReportResponse, status_code=201)
def generate_report(
    payload: ReportGenerateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin),
) -> ReportResponse:
    """Generate a JSON or PDF report for a scan. The report reflects
    exactly what is currently stored for the scan at generation time — no
    additional evidence is created."""
    scan = db.query(Scan).filter(Scan.id == payload.scan_id).first()
    if scan is None:
        raise NotFoundError("Scan not found")

    report_data = report_service.build_scan_report(db, scan)

    if payload.format == ReportFormat.PDF:
        file_path = pdf_service.save_pdf_report(report_data, str(scan.id))
    else:
        file_path = report_service.save_json_report(report_data, str(scan.id))

    report = report_service.create_report_record(
        db,
        scan_id=scan.id,
        generated_by_id=current_user.id,
        report_format=payload.format,
        file_path=file_path,
    )

    log_action(
        db,
        action="report.generated",
        user_id=current_user.id,
        resource_type="report",
        resource_id=str(report.id),
        details={"scan_id": str(scan.id), "format": payload.format.value},
        ip_address=_client_ip(request),
    )

    return ReportResponse.model_validate(report)


@router.get("", response_model=List[ReportResponse])
def list_reports(
    scan_id: Optional[uuid.UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[ReportResponse]:
    query = db.query(Report)
    if scan_id is not None:
        query = query.filter(Report.scan_id == scan_id)
    reports = query.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
    return [ReportResponse.model_validate(r) for r in reports]


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ReportResponse:
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise NotFoundError("Report not found")
    return ReportResponse.model_validate(report)


@router.get("/{report_id}/download")
def download_report(
    report_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> FileResponse:
    """Download the previously generated report file from disk."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise NotFoundError("Report not found")

    if not report.file_path or not os.path.isfile(report.file_path):
        raise NotFoundError("Report file is no longer available on disk")

    media_type = (
        "application/pdf" if report.format == ReportFormat.PDF else "application/json"
    )
    filename = os.path.basename(report.file_path)

    return FileResponse(path=report.file_path, media_type=media_type, filename=filename)