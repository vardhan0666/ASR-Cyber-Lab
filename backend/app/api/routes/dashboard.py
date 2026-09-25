"""Security dashboard summary endpoint."""

from typing import Dict

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.finding import Finding, SeverityLevel
from app.models.host import Host
from app.models.scan import Scan, ScanStatus
from app.models.target import Target
from app.models.user import User
from app.schemas.dashboard import DashboardSummary, RecentScanSummary
from app.security.auth import get_current_active_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

RECENT_SCANS_LIMIT = 5


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DashboardSummary:
    """Aggregate, evidence-based summary of the platform's current
    security posture across all authorized targets and scans."""
    total_targets = db.query(Target).count()
    authorized_targets = db.query(Target).filter(Target.is_authorized.is_(True)).count()
    total_scans = db.query(Scan).count()
    scans_in_progress = (
        db.query(Scan)
        .filter(Scan.status.in_([ScanStatus.PENDING, ScanStatus.RUNNING]))
        .count()
    )
    total_hosts = db.query(Host).count()
    total_findings = db.query(Finding).count()

    findings_by_severity: Dict[str, int] = {level.value: 0 for level in SeverityLevel}
    severity_rows = (
        db.query(Finding.severity, func.count(Finding.id))
        .group_by(Finding.severity)
        .all()
    )
    for severity, count in severity_rows:
        findings_by_severity[severity.value] = count

    recent_rows = (
        db.query(Scan, Target.name)
        .join(Target, Scan.target_id == Target.id)
        .order_by(Scan.created_at.desc())
        .limit(RECENT_SCANS_LIMIT)
        .all()
    )
    recent_scans = [
        RecentScanSummary(
            id=scan.id,
            target_name=target_name,
            status=scan.status,
            created_at=scan.created_at,
        )
        for scan, target_name in recent_rows
    ]

    return DashboardSummary(
        total_targets=total_targets,
        authorized_targets=authorized_targets,
        total_scans=total_scans,
        scans_in_progress=scans_in_progress,
        total_hosts=total_hosts,
        total_findings=total_findings,
        findings_by_severity=findings_by_severity,
        recent_scans=recent_scans,
        cve_data_availability_note=(
            "Vulnerability enrichment in this deployment uses a small, "
            "local, static reference dataset rather than a live feed. "
            "Findings without a matched CVE are not confirmed to be "
            "vulnerability-free — see each finding's vulnerability data "
            "for details."
        ),
    )