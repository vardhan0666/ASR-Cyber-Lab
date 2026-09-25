"""
Tests for evidence-based security configuration/exposure analysis.

Host/PortService ORM objects are constructed transiently (never added to a
database session) since analyze_host operates purely on in-memory
relationship data.
"""

import uuid

from app.models.finding import FindingCategory, SeverityLevel
from app.models.host import Host
from app.models.port_service import PortService
from app.services.config_analysis_service import analyze_host


def _make_host_with_port(**port_kwargs) -> Host:
    host = Host(
        id=uuid.uuid4(),
        scan_id=uuid.uuid4(),
        ip_address="192.0.2.50",
        status="up",
    )
    defaults = {
        "id": uuid.uuid4(),
        "host_id": host.id,
        "protocol": "tcp",
        "state": "open",
    }
    defaults.update(port_kwargs)
    port = PortService(**defaults)
    host.port_services.append(port)
    return host


def test_cleartext_protocol_detected_for_telnet():
    host = _make_host_with_port(port_number=23, service_name="telnet")
    findings = analyze_host(host)

    matching = [f for f in findings if f.rule_id == "cleartext-protocol-23"]
    assert len(matching) == 1
    assert matching[0].category == FindingCategory.CONFIGURATION
    assert matching[0].base_severity == SeverityLevel.HIGH
    assert matching[0].evidence["port"] == 23
    assert matching[0].evidence["ip_address"] == "192.0.2.50"
    assert matching[0].host_id == str(host.id)


def test_exposed_sensitive_service_detected_for_rdp():
    host = _make_host_with_port(port_number=3389, service_name="ms-wbt-server")
    findings = analyze_host(host)

    matching = [f for f in findings if f.rule_id == "exposed-service-3389"]
    assert len(matching) == 1
    assert matching[0].category == FindingCategory.EXPOSURE
    assert matching[0].base_severity == SeverityLevel.MEDIUM


def test_version_disclosure_detected_when_product_present():
    host = _make_host_with_port(
        port_number=8080, service_name="http", product="Apache httpd", version="2.4.41"
    )
    findings = analyze_host(host)

    matching = [f for f in findings if f.rule_id == "version-disclosure-8080"]
    assert len(matching) == 1
    assert matching[0].base_severity == SeverityLevel.INFO
    assert "Apache httpd" in matching[0].title
    assert "2.4.41" in matching[0].title


def test_no_version_disclosure_without_product_or_version():
    host = _make_host_with_port(port_number=8080, service_name="http")
    findings = analyze_host(host)

    matching = [f for f in findings if f.rule_id.startswith("version-disclosure")]
    assert len(matching) == 0


def test_closed_port_produces_no_findings():
    host = _make_host_with_port(port_number=23, service_name="telnet", state="closed")
    findings = analyze_host(host)
    assert findings == []


def test_multiple_rules_can_fire_for_the_same_port():
    host = _make_host_with_port(
        port_number=3306, service_name="mysql", product="MySQL", version="5.7.30"
    )
    findings = analyze_host(host)

    rule_ids = {f.rule_id for f in findings}
    assert "exposed-service-3306" in rule_ids
    assert "version-disclosure-3306" in rule_ids
    assert len(findings) == 2


def test_port_with_no_matching_rules_produces_no_findings():
    host = _make_host_with_port(port_number=51000, service_name="unknown-service")
    findings = analyze_host(host)
    assert findings == []


def test_multiple_open_ports_are_all_analyzed():
    host = Host(
        id=uuid.uuid4(), scan_id=uuid.uuid4(), ip_address="192.0.2.51", status="up"
    )
    telnet_port = PortService(
        id=uuid.uuid4(),
        host_id=host.id,
        port_number=23,
        protocol="tcp",
        state="open",
        service_name="telnet",
    )
    redis_port = PortService(
        id=uuid.uuid4(),
        host_id=host.id,
        port_number=6379,
        protocol="tcp",
        state="open",
        service_name="redis",
    )
    host.port_services.append(telnet_port)
    host.port_services.append(redis_port)

    findings = analyze_host(host)
    rule_ids = {f.rule_id for f in findings}
    assert "cleartext-protocol-23" in rule_ids
    assert "exposed-service-6379" in rule_ids