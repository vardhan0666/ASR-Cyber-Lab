"""
Tests for scan creation/authorization rules (API layer, with Nmap execution
mocked out) and the full scan orchestration pipeline (service layer, with
only the Nmap subprocess call mocked).
"""

import uuid

from app.core.exceptions import NmapExecutionError
from app.models.finding import Finding, SeverityLevel
from app.models.host import Host
from app.models.scan import ScanProfile, ScanStatus
from app.models.target import AssetImportance, Target
from app.services import scan_orchestrator

SAMPLE_NMAP_XML = """<?xml version="1.0"?>
<nmaprun scanner="nmap">
<host>
<status state="up"/>
<address addr="192.0.2.1" addrtype="ipv4"/>
<hostnames><hostname name="lab-host.example"/></hostnames>
<ports>
<port protocol="tcp" portid="23">
<state state="open"/>
<service name="telnet"/>
</port>
<port protocol="tcp" portid="80">
<state state="closed"/>
<service name="http"/>
</port>
</ports>
</host>
</nmaprun>
"""


# ---------------------------------------------------------------------------
# API-layer tests: authorization rules around scan creation.
# Background execution is always patched to a no-op so these tests never
# invoke a real Nmap subprocess.
# ---------------------------------------------------------------------------


def _create_and_authorize_target(client, analyst_headers, address: str) -> str:
    create_resp = client.post(
        "/api/targets",
        json={"name": f"Scan Target {address}", "address": address},
        headers=analyst_headers,
    )
    target_id = create_resp.json()["id"]
    client.post(
        f"/api/targets/{target_id}/authorize",
        json={"is_authorized": True},
        headers=analyst_headers,
    )
    return target_id


def test_create_scan_rejected_for_unauthorized_target(
    client, analyst_headers, monkeypatch
):
    monkeypatch.setattr(
        "app.api.routes.scans._run_scan_background", lambda scan_id: None
    )
    create_resp = client.post(
        "/api/targets",
        json={"name": "Unauthorized Target", "address": "203.0.113.30"},
        headers=analyst_headers,
    )
    target_id = create_resp.json()["id"]

    response = client.post(
        "/api/scans",
        json={"target_id": target_id, "profile": "quick"},
        headers=analyst_headers,
    )
    assert response.status_code == 403


def test_create_scan_rejected_for_nonexistent_target(
    client, analyst_headers, monkeypatch
):
    monkeypatch.setattr(
        "app.api.routes.scans._run_scan_background", lambda scan_id: None
    )
    response = client.post(
        "/api/scans",
        json={"target_id": str(uuid.uuid4()), "profile": "quick"},
        headers=analyst_headers,
    )
    assert response.status_code == 404


def test_create_scan_succeeds_for_authorized_target(
    client, analyst_headers, monkeypatch
):
    monkeypatch.setattr(
        "app.api.routes.scans._run_scan_background", lambda scan_id: None
    )
    target_id = _create_and_authorize_target(client, analyst_headers, "203.0.113.31")

    response = client.post(
        "/api/scans",
        json={"target_id": target_id, "profile": "quick"},
        headers=analyst_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["target_id"] == target_id
    assert body["status"] == "pending"


def test_create_scan_conflicts_when_already_pending(
    client, analyst_headers, monkeypatch
):
    monkeypatch.setattr(
        "app.api.routes.scans._run_scan_background", lambda scan_id: None
    )
    target_id = _create_and_authorize_target(client, analyst_headers, "203.0.113.32")

    first = client.post(
        "/api/scans",
        json={"target_id": target_id, "profile": "quick"},
        headers=analyst_headers,
    )
    assert first.status_code == 201

    second = client.post(
        "/api/scans",
        json={"target_id": target_id, "profile": "quick"},
        headers=analyst_headers,
    )
    assert second.status_code == 409


def test_viewer_cannot_create_scan(client, analyst_headers, viewer_headers, monkeypatch):
    monkeypatch.setattr(
        "app.api.routes.scans._run_scan_background", lambda scan_id: None
    )
    target_id = _create_and_authorize_target(client, analyst_headers, "203.0.113.33")

    response = client.post(
        "/api/scans",
        json={"target_id": target_id, "profile": "quick"},
        headers=viewer_headers,
    )
    assert response.status_code == 403


def test_list_and_get_scan(client, analyst_headers, monkeypatch):
    monkeypatch.setattr(
        "app.api.routes.scans._run_scan_background", lambda scan_id: None
    )
    target_id = _create_and_authorize_target(client, analyst_headers, "203.0.113.34")
    create_resp = client.post(
        "/api/scans",
        json={"target_id": target_id, "profile": "standard"},
        headers=analyst_headers,
    )
    scan_id = create_resp.json()["id"]

    list_resp = client.get(
        "/api/scans", params={"target_id": target_id}, headers=analyst_headers
    )
    assert list_resp.status_code == 200
    assert any(s["id"] == scan_id for s in list_resp.json())

    get_resp = client.get(f"/api/scans/{scan_id}", headers=analyst_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["profile"] == "standard"


def test_get_nonexistent_scan_returns_404(client, viewer_headers):
    response = client.get(f"/api/scans/{uuid.uuid4()}", headers=viewer_headers)
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Service-layer tests: full pipeline execution with only the Nmap subprocess
# call mocked at its usage site inside scan_orchestrator.
# ---------------------------------------------------------------------------


def test_execute_scan_persists_hosts_and_findings(db_session, admin_user, monkeypatch):
    monkeypatch.setattr(
        "app.services.scan_orchestrator.run_nmap_scan",
        lambda target_address, profile: SAMPLE_NMAP_XML,
    )

    target = Target(
        id=uuid.uuid4(),
        name="Orchestrator Target",
        address="203.0.113.40",
        asset_importance=AssetImportance.MEDIUM,
        is_authorized=True,
        is_active=True,
        created_by_id=admin_user.id,
    )
    db_session.add(target)
    db_session.commit()

    scan = scan_orchestrator.create_scan(
        db_session,
        target_id=target.id,
        profile=ScanProfile.QUICK,
        initiated_by_id=admin_user.id,
    )
    assert scan.status == ScanStatus.PENDING

    completed_scan = scan_orchestrator.execute_scan(db_session, scan.id)
    assert completed_scan.status == ScanStatus.COMPLETED
    assert completed_scan.raw_xml_output == SAMPLE_NMAP_XML

    hosts = db_session.query(Host).filter(Host.scan_id == scan.id).all()
    assert len(hosts) == 1
    assert hosts[0].ip_address == "192.0.2.1"
    assert hosts[0].hostname == "lab-host.example"
    # Only the open port (23) should be persisted; nmap still reports the
    # closed port 80, and it is stored too since PortService records every
    # reported port regardless of state (state itself is evidence).
    port_numbers = {p.port_number for p in hosts[0].port_services}
    assert port_numbers == {23, 80}

    findings = db_session.query(Finding).filter(Finding.scan_id == scan.id).all()
    # Only the OPEN telnet port (23) triggers a configuration finding; the
    # closed port 80 is skipped by analyze_host's open-state filter.
    assert len(findings) == 1
    assert findings[0].severity == SeverityLevel.HIGH
    assert "telnet" in findings[0].title.lower()


def test_execute_scan_handles_nmap_execution_failure(db_session, admin_user, monkeypatch):
    def _raise_failure(target_address, profile):
        raise NmapExecutionError("Simulated nmap failure for testing")

    monkeypatch.setattr(
        "app.services.scan_orchestrator.run_nmap_scan", _raise_failure
    )

    target = Target(
        id=uuid.uuid4(),
        name="Failing Target",
        address="203.0.113.41",
        is_authorized=True,
        is_active=True,
        created_by_id=admin_user.id,
    )
    db_session.add(target)
    db_session.commit()

    scan = scan_orchestrator.create_scan(
        db_session,
        target_id=target.id,
        profile=ScanProfile.QUICK,
        initiated_by_id=admin_user.id,
    )

    result = scan_orchestrator.execute_scan(db_session, scan.id)
    assert result.status == ScanStatus.FAILED
    assert result.error_message == "Simulated nmap failure for testing"
    assert result.completed_at is not None


def test_execute_scan_blocks_if_authorization_revoked_before_execution(
    db_session, admin_user, monkeypatch
):
    monkeypatch.setattr(
        "app.services.scan_orchestrator.run_nmap_scan",
        lambda target_address, profile: SAMPLE_NMAP_XML,
    )

    target = Target(
        id=uuid.uuid4(),
        name="Revoked Target",
        address="203.0.113.42",
        is_authorized=True,
        is_active=True,
        created_by_id=admin_user.id,
    )
    db_session.add(target)
    db_session.commit()

    scan = scan_orchestrator.create_scan(
        db_session,
        target_id=target.id,
        profile=ScanProfile.QUICK,
        initiated_by_id=admin_user.id,
    )

    # Simulate authorization being revoked after scan creation but before
    # execution — a real-world race the orchestrator must defend against.
    target.is_authorized = False
    db_session.add(target)
    db_session.commit()

    result = scan_orchestrator.execute_scan(db_session, scan.id)
    assert result.status == ScanStatus.FAILED
    assert "authorization" in result.error_message.lower()