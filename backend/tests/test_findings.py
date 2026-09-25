"""Tests for security finding listing, filtering, sorting, and triage-status endpoints."""

import json
import uuid

from app.models.finding import Finding, FindingCategory, FindingStatus, SeverityLevel
from app.models.scan import Scan, ScanProfile, ScanStatus
from app.models.target import Target


def _create_scan_with_findings(db_session, admin_user):
    target = Target(
        id=uuid.uuid4(),
        name="Findings Target",
        address="203.0.113.60",
        is_authorized=True,
        is_active=True,
        created_by_id=admin_user.id,
    )
    db_session.add(target)
    db_session.commit()

    scan = Scan(
        id=uuid.uuid4(),
        target_id=target.id,
        initiated_by_id=admin_user.id,
        profile=ScanProfile.QUICK,
        status=ScanStatus.COMPLETED,
    )
    db_session.add(scan)
    db_session.commit()

    high_finding = Finding(
        id=uuid.uuid4(),
        scan_id=scan.id,
        category=FindingCategory.EXPOSURE,
        title="Exposed Redis service",
        description="Redis is directly reachable.",
        evidence=json.dumps({"port": 6379, "service_name": "redis"}),
        severity=SeverityLevel.HIGH,
        risk_score=75.0,
        risk_explanation=json.dumps(["EVIDENCE: high severity exposure"]),
        status=FindingStatus.OPEN,
        remediation="Restrict Redis access.",
    )
    low_finding = Finding(
        id=uuid.uuid4(),
        scan_id=scan.id,
        category=FindingCategory.CONFIGURATION,
        title="Service version disclosed",
        description="Version banner exposed.",
        evidence=json.dumps({"port": 80, "product": "nginx"}),
        severity=SeverityLevel.INFO,
        risk_score=5.0,
        risk_explanation=json.dumps(["EVIDENCE: informational disclosure"]),
        status=FindingStatus.OPEN,
        remediation="Suppress version banners.",
    )
    db_session.add_all([high_finding, low_finding])
    db_session.commit()

    return scan, high_finding, low_finding


def test_list_findings_returns_all(client, viewer_headers, db_session, admin_user):
    scan, high_finding, low_finding = _create_scan_with_findings(db_session, admin_user)

    response = client.get(
        "/api/findings", params={"scan_id": str(scan.id)}, headers=viewer_headers
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2
    ids = {r["id"] for r in results}
    assert str(high_finding.id) in ids
    assert str(low_finding.id) in ids


def test_list_findings_filter_by_severity(client, viewer_headers, db_session, admin_user):
    scan, high_finding, low_finding = _create_scan_with_findings(db_session, admin_user)

    response = client.get(
        "/api/findings",
        params={"scan_id": str(scan.id), "severity": "high"},
        headers=viewer_headers,
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["id"] == str(high_finding.id)


def test_list_findings_search_by_title(client, viewer_headers, db_session, admin_user):
    scan, high_finding, _ = _create_scan_with_findings(db_session, admin_user)

    response = client.get(
        "/api/findings", params={"search": "Redis"}, headers=viewer_headers
    )
    assert response.status_code == 200
    results = response.json()
    assert any(r["id"] == str(high_finding.id) for r in results)


def test_list_findings_sorted_by_risk_score_desc(
    client, viewer_headers, db_session, admin_user
):
    scan, high_finding, low_finding = _create_scan_with_findings(db_session, admin_user)

    response = client.get(
        "/api/findings",
        params={"scan_id": str(scan.id), "sort_by": "risk_score", "sort_order": "desc"},
        headers=viewer_headers,
    )
    results = response.json()
    assert results[0]["id"] == str(high_finding.id)
    assert results[1]["id"] == str(low_finding.id)


def test_get_finding_parses_evidence_and_explanation(
    client, viewer_headers, db_session, admin_user
):
    _, high_finding, _ = _create_scan_with_findings(db_session, admin_user)

    response = client.get(f"/api/findings/{high_finding.id}", headers=viewer_headers)
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["evidence"], dict)
    assert body["evidence"]["port"] == 6379
    assert isinstance(body["risk_explanation"], list)
    assert len(body["risk_explanation"]) == 1


def test_get_nonexistent_finding_returns_404(client, viewer_headers):
    response = client.get(f"/api/findings/{uuid.uuid4()}", headers=viewer_headers)
    assert response.status_code == 404


def test_viewer_cannot_update_finding_status(
    client, viewer_headers, db_session, admin_user
):
    _, high_finding, _ = _create_scan_with_findings(db_session, admin_user)

    response = client.patch(
        f"/api/findings/{high_finding.id}/status",
        json={"status": "resolved"},
        headers=viewer_headers,
    )
    assert response.status_code == 403


def test_analyst_can_update_finding_status(
    client, analyst_headers, viewer_headers, db_session, admin_user
):
    _, high_finding, _ = _create_scan_with_findings(db_session, admin_user)

    response = client.patch(
        f"/api/findings/{high_finding.id}/status",
        json={"status": "resolved"},
        headers=analyst_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "resolved"

    get_resp = client.get(f"/api/findings/{high_finding.id}", headers=viewer_headers)
    assert get_resp.json()["status"] == "resolved"