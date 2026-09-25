"""
Import every ORM model here so Alembic's autogenerate (via
app/alembic/env.py's target_metadata = Base.metadata) can discover all
tables in a single, predictable place.
"""

from app.models.audit_log import AuditLog
from app.models.finding import Finding, FindingCategory, FindingStatus, SeverityLevel
from app.models.host import Host
from app.models.port_services import PortService
from app.models.report import Report, ReportFormat
from app.models.scan import Scan, ScanProfile, ScanStatus
from app.models.target import AssetImportance, Target
from app.models.user import User, UserRole
from app.models.vulnerability import Vulnerability

__all__ = [
    "User",
    "UserRole",
    "Target",
    "AssetImportance",
    "Scan",
    "ScanProfile",
    "ScanStatus",
    "Host",
    "PortService",
    "Finding",
    "FindingCategory",
    "FindingStatus",
    "SeverityLevel",
    "Vulnerability",
    "AuditLog",
    "Report",
    "ReportFormat",
]