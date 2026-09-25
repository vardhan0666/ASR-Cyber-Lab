"""
JSON report generation service.

Builds a fully self-contained JSON payload for a scan, combining target
metadata, discovered hosts/ports, findings (with parsed evidence and risk
explanations), and vulnerability enrichment results. This payload is used
both for the JSON report API response and as the data source for PDF
report rendering (app.services.pdf_service).

Every value in the report payload is taken directly from the database —
this service performs no scoring, inference, or enrichment of its own.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.finding import Finding, SeverityLevel
from app.models.host import Host
from app.models.report import Report, ReportFormat
from app.models.scan import Scan
from app.models.target import Target
from app.models.vulnerability import Vulnerability
from app.services.pdf_service import REPORTS_OUTPUT_DIR


def _safe_json_loads(value: Optional[str], default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def _count_by_severity(findings: List[Finding]) -> Dict[str, int]:
    counts = {level.value: 0 for level in SeverityLevel}
    for f in findings:
        counts[f.severity.value] = counts.get(f.severity.value, 0) + 1
    return counts


def build_scan_report(db: Session, scan: Scan) -> Dict[str, Any]:
    """Build the complete JSON report payload for a given scan."""
    target = db.query(Target).filter(Target.id == scan.target_id).first()
    hosts = db.query(Host).filter(Host.scan_id == scan.id).all()
    findings = db.query(Finding).filter(Finding.scan_id == scan.id).all()

    host_payload = []
    for host in hosts:
        ports_payload = [
            {
                "port_number": port.port_number,
                "protocol": port.protocol,
                "state": port.state,
                "service_name": port.service_name,
                "product": port.product,
                "version": port.version,
                "extra_info": port.extra_info,
            }
            for port in host.port_services
        ]
        host_payload.append(
            {
                "id": str(host.id),
                "ip_address": host.ip_address,
                "hostname": host.hostname,
                "status": host.status,
                "os_name": host.os_name,
                "os_accuracy": host.os_accuracy,
                "mac_address": host.mac_address,
                "ports": ports_payload,
            }
        )

    findings_payload = []
    for f in findings:
        vulns = (
            db.query(Vulnerability).filter(Vulnerability.finding_id == f.id).all()
        )
        findings_payload.append(
            {
                "id": str(f.id),
                "host_id": str(f.host_id) if f.host_id else None,
                "category": f.category.value,
                "title": f.title,
                "description": f.description,
                "evidence": _safe_json_loads(f.evidence, {}),
                "severity": f.severity.value,
                "risk_score": f.risk_score,
                "risk_explanation": _safe_json_loads(f.risk_explanation, []),
                "status": f.status.value,
                "remediation": f.remediation,
                "vulnerabilities": [
                    {
                        "cve_id": v.cve_id,
                        "source": v.source,
                        "description": v.description,
                        "cvss_score": v.cvss_score,
                        "severity": v.severity.value if v.severity else None,
                        "reference_url": v.reference_url,
                        "data_available": v.data_available,
                    }
                    for v in vulns
                ],
            }
        )

    return {
        "report_metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "platform": "ASR-Cyber-Lab",
            "disclaimer": (
                "This report reflects only evidence actually observed "
                "during the scan and locally available vulnerability "
                "reference data. It is not a substitute for a full "
                "professional security assessment."
            ),
        },
        "scan": {
            "id": str(scan.id),
            "profile": scan.profile.value,
            "status": scan.status.value,
            "started_at": scan.started_at.isoformat() if scan.started_at else None,
            "completed_at": (
                scan.completed_at.isoformat() if scan.completed_at else None
            ),
        },
        "target": {
            "id": str(target.id) if target else None,
            "name": target.name if target else None,
            "address": target.address if target else None,
            "asset_importance": (
                target.asset_importance.value if target else None
            ),
        },
        "hosts": host_payload,
        "findings": findings_payload,
        "summary": {
            "total_hosts": len(hosts),
            "total_findings": len(findings_payload),
            "findings_by_severity": _count_by_severity(findings),
        },
    }


def save_json_report(report_data: Dict[str, Any], scan_id: str) -> str:
    """Persist the JSON report payload to disk, returning the file path.
    Uses the same output directory as PDF reports (defined once in
    app.services.pdf_service) so all generated report files live together."""
    os.makedirs(REPORTS_OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    filename = f"scan_{scan_id}_{timestamp}.json"
    file_path = os.path.join(REPORTS_OUTPUT_DIR, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, default=str)

    return file_path


def create_report_record(
    db: Session,
    scan_id: uuid.UUID,
    generated_by_id: uuid.UUID,
    report_format: ReportFormat,
    file_path: Optional[str] = None,
) -> Report:
    """Persist metadata about a generated report."""
    report = Report(
        id=uuid.uuid4(),
        scan_id=scan_id,
        generated_by_id=generated_by_id,
        format=report_format,
        file_path=file_path,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report