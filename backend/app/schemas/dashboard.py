"""Security dashboard summary schemas."""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

from app.models.scan import ScanStatus


class RecentScanSummary(BaseModel):
    id: uuid.UUID
    target_name: str
    status: ScanStatus
    created_at: datetime


class DashboardSummary(BaseModel):
    total_targets: int
    authorized_targets: int
    total_scans: int
    scans_in_progress: int
    total_hosts: int
    total_findings: int
    findings_by_severity: Dict[str, int]
    recent_scans: List[RecentScanSummary]
    # Set when the CVE enrichment data source could not be reached/loaded,
    # so the dashboard can transparently flag this instead of hiding it.
    cve_data_availability_note: Optional[str] = None