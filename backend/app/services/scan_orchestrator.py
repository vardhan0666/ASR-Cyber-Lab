"""
Scan lifecycle orchestration.

Coordinates the full pipeline for a single scan job:
  1. Create a Scan record only against a target that is explicitly
     authorized and active (defense-in-depth: re-checked again at
     execution time in case authorization was revoked between creation
     and execution).
  2. Execute the scan via the validated Nmap service.
  3. Parse Nmap's XML output into normalized hosts/ports.
  4. Run configuration/exposure analysis against each host.
  5. Attempt CVE enrichment for findings that carry product/version
     evidence.
  6. Compute a transparent risk score for every finding.
  7. Persist hosts, ports, findings, and vulnerabilities.
  8. Record audit log entries for both success and failure outcomes.

No step in this module fabricates evidence: hosts/ports come only from
Nmap's own output, vulnerabilities come only from cve_service's local
dataset (explicitly flagged when unavailable), and risk scores are always
accompanied by their engine-generated explanation.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import (
    NmapExecutionError,
    NmapParsingError,
    NotFoundError,
    ScanInProgressError,
    UnsafeTargetError,
    ValidationError,
)
from app.models.finding import Finding, FindingStatus
from app.models.host import Host
from app.models.port_services import PortService
from app.models.scan import Scan, ScanProfile, ScanStatus
from app.models.target import Target
from app.models.vulnerability import Vulnerability
from app.services import audit_service
from app.services.config_analysis_service import ConfigFinding, analyze_host
from app.services.cve_service import lookup_vulnerabilities
from app.services.nmap_parser import ParsedHost, parse_nmap_xml
from app.services.nmap_service import run_nmap_scan
from app.services.remediation_service import build_remediation
from app.services.risk_engine import VulnerabilityEvidence, calculate_risk


def create_scan(
    db: Session, target_id: uuid.UUID, profile: ScanProfile, initiated_by_id: uuid.UUID
) -> Scan:
    """Create a new pending Scan record for an authorized, active target.

    Raises:
        NotFoundError: target does not exist.
        UnsafeTargetError: target is not authorized or is inactive.
        ScanInProgressError: a scan is already pending/running for this target.
    """
    target = db.query(Target).filter(Target.id == target_id).first()
    if target is None:
        raise NotFoundError("Target not found")

    if not target.is_authorized:
        raise UnsafeTargetError(
            "This target has not been marked as authorized for scanning."
        )
    if not target.is_active:
        raise UnsafeTargetError("This target is inactive and cannot be scanned.")

    existing = (
        db.query(Scan)
        .filter(
            Scan.target_id == target.id,
            Scan.status.in_([ScanStatus.PENDING, ScanStatus.RUNNING]),
        )
        .first()
    )
    if existing is not None:
        raise ScanInProgressError(
            "A scan is already pending or running for this target."
        )

    scan = Scan(
        id=uuid.uuid4(),
        target_id=target.id,
        initiated_by_id=initiated_by_id,
        profile=profile,
        status=ScanStatus.PENDING,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    audit_service.log_action(
        db,
        action="scan.created",
        user_id=initiated_by_id,
        resource_type="scan",
        resource_id=str(scan.id),
        details={"target_id": str(target.id), "profile": profile.value},
    )

    return scan


def execute_scan(db: Session, scan_id: uuid.UUID) -> Scan:
    """Execute a previously created scan end-to-end.

    Always leaves the Scan in a terminal, explainable state (COMPLETED or
    FAILED with error_message set) rather than raising past this function
    for expected failure modes, so background execution does not lose the
    error context.
    """
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if scan is None:
        raise NotFoundError("Scan not found")

    target = db.query(Target).filter(Target.id == scan.target_id).first()
    if target is None:
        scan.status = ScanStatus.FAILED
        scan.error_message = "Associated target no longer exists."
        scan.completed_at = datetime.now(timezone.utc)
        db.add(scan)
        db.commit()
        return scan

    # Defense-in-depth: re-verify authorization in case it was revoked
    # after the scan was created but before it began executing.
    if not target.is_authorized or not target.is_active:
        scan.status = ScanStatus.FAILED
        scan.error_message = (
            "Target authorization was revoked or the target was deactivated "
            "before this scan could execute."
        )
        scan.completed_at = datetime.now(timezone.utc)
        db.add(scan)
        db.commit()
        audit_service.log_action(
            db,
            action="scan.blocked_unauthorized",
            user_id=scan.initiated_by_id,
            resource_type="scan",
            resource_id=str(scan.id),
        )
        return scan

    scan.status = ScanStatus.RUNNING
    scan.started_at = datetime.now(timezone.utc)
    db.add(scan)
    db.commit()

    raw_xml: Optional[str] = None

    try:
        raw_xml = run_nmap_scan(target.address, scan.profile)
        parsed_hosts = parse_nmap_xml(raw_xml)

        for parsed_host in parsed_hosts:
            host = _persist_host(db, scan.id, parsed_host)
            _process_host_findings(db, scan, target, host)

        scan.raw_xml_output = raw_xml
        scan.status = ScanStatus.COMPLETED
        scan.completed_at = datetime.now(timezone.utc)
        db.add(scan)
        db.commit()

        audit_service.log_action(
            db,
            action="scan.completed",
            user_id=scan.initiated_by_id,
            resource_type="scan",
            resource_id=str(scan.id),
            details={"host_count": len(parsed_hosts)},
        )

    except (ValidationError, NmapExecutionError, NmapParsingError) as exc:
        db.rollback()
        scan.status = ScanStatus.FAILED
        scan.error_message = getattr(exc, "message", str(exc))
        scan.raw_xml_output = raw_xml
        scan.completed_at = datetime.now(timezone.utc)
        db.add(scan)
        db.commit()

        audit_service.log_action(
            db,
            action="scan.failed",
            user_id=scan.initiated_by_id,
            resource_type="scan",
            resource_id=str(scan.id),
            details={"error": scan.error_message},
        )

    except Exception as exc:  # pragma: no cover - unexpected failure safety net
        db.rollback()
        scan.status = ScanStatus.FAILED
        scan.error_message = "An unexpected error occurred during scan execution."
        scan.raw_xml_output = raw_xml
        scan.completed_at = datetime.now(timezone.utc)
        db.add(scan)
        db.commit()

        audit_service.log_action(
            db,
            action="scan.failed_unexpected",
            user_id=scan.initiated_by_id,
            resource_type="scan",
            resource_id=str(scan.id),
            details={"error": str(exc)},
        )
        raise

    return scan


def _persist_host(db: Session, scan_id: uuid.UUID, parsed_host: ParsedHost) -> Host:
    """Create and stage a Host row (and its PortService children) from a
    parsed Nmap host entry. IDs are assigned client-side so they are
    reliably available in memory before any flush occurs."""
    host = Host(
        id=uuid.uuid4(),
        scan_id=scan_id,
        ip_address=parsed_host.ip_address,
        hostname=parsed_host.hostname,
        status=parsed_host.status,
        os_name=parsed_host.os_name,
        os_accuracy=parsed_host.os_accuracy,
        mac_address=parsed_host.mac_address,
    )
    db.add(host)

    for parsed_port in parsed_host.ports:
        port = PortService(
            id=uuid.uuid4(),
            host_id=host.id,
            port_number=parsed_port.port_number,
            protocol=parsed_port.protocol,
            state=parsed_port.state,
            service_name=parsed_port.service_name,
            product=parsed_port.product,
            version=parsed_port.version,
            extra_info=parsed_port.extra_info,
        )
        db.add(port)
        host.port_services.append(port)

    return host


def _process_host_findings(db: Session, scan: Scan, target: Target, host: Host) -> None:
    """Run configuration analysis, CVE enrichment, and risk scoring for a
    single host, persisting the resulting Finding/Vulnerability rows."""
    config_findings: list[ConfigFinding] = analyze_host(host)

    for cf in config_findings:
        product = cf.evidence.get("product")
        version = cf.evidence.get("version")

        vulnerabilities = lookup_vulnerabilities(product, version) if product else []

        vuln_evidence = [
            VulnerabilityEvidence(
                cve_id=v.cve_id,
                cvss_score=v.cvss_score,
                data_available=v.data_available,
            )
            for v in vulnerabilities
        ]

        risk_result = calculate_risk(
            base_severity=cf.base_severity,
            asset_importance=target.asset_importance,
            category=cf.category,
            vulnerabilities=vuln_evidence,
        )

        remediation_text = build_remediation(cf.remediation, vulnerabilities)

        finding = Finding(
            id=uuid.uuid4(),
            scan_id=scan.id,
            host_id=host.id,
            port_service_id=(
                uuid.UUID(cf.port_service_id) if cf.port_service_id else None
            ),
            category=cf.category,
            title=cf.title,
            description=cf.description,
            evidence=json.dumps(cf.evidence),
            severity=risk_result.severity,
            risk_score=risk_result.score,
            risk_explanation=json.dumps(risk_result.explanation),
            status=FindingStatus.OPEN,
            remediation=remediation_text,
        )
        db.add(finding)

        for v in vulnerabilities:
            vuln_row = Vulnerability(
                id=uuid.uuid4(),
                finding_id=finding.id,
                cve_id=v.cve_id,
                source=v.source,
                description=v.description,
                cvss_score=v.cvss_score,
                severity=v.severity,
                reference_url=v.reference_url,
                data_available=v.data_available,
            )
            db.add(vuln_row)