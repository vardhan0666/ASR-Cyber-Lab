"""
Security configuration analysis service.

Applies transparent, rule-based checks against discovered ports/services to
identify common insecure configurations and network exposures. Every check
here is evidence-based: it only fires when specific port/service/state
conditions actually observed by Nmap are met. No configuration issue is
ever asserted without the underlying port/service evidence attached, and
no check here relies on external or fabricated data.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.models.finding import FindingCategory, SeverityLevel
from app.models.host import Host
from app.models.port_services import PortService

OPEN_STATE = "open"

# port -> (display_name, description, severity, remediation)
CLEARTEXT_PROTOCOL_RULES: Dict[int, tuple] = {
    21: (
        "FTP",
        "FTP transmits credentials and file contents in cleartext, "
        "making them vulnerable to network interception.",
        SeverityLevel.MEDIUM,
        "Disable FTP and replace it with SFTP or FTPS. If FTP must remain, "
        "restrict access to trusted networks only.",
    ),
    23: (
        "Telnet",
        "Telnet transmits login credentials and session data in cleartext, "
        "making them trivially interceptable on the network.",
        SeverityLevel.HIGH,
        "Disable Telnet and use SSH for remote administration instead.",
    ),
    512: (
        "rexec",
        "rexec transmits credentials in cleartext and provides weak "
        "authentication.",
        SeverityLevel.HIGH,
        "Disable rexec and use SSH for remote command execution instead.",
    ),
    513: (
        "rlogin",
        "rlogin is a legacy remote login protocol with weak, host-based "
        "authentication and no encryption.",
        SeverityLevel.HIGH,
        "Disable rlogin and use SSH for remote login instead.",
    ),
    514: (
        "rsh",
        "rsh is a legacy remote shell protocol with no authentication or "
        "encryption.",
        SeverityLevel.HIGH,
        "Disable rsh and use SSH for remote command execution instead.",
    ),
}

# port -> (display_name, description, severity, remediation)
EXPOSED_SENSITIVE_SERVICE_RULES: Dict[int, tuple] = {
    445: (
        "SMB",
        "The SMB file-sharing service is directly reachable from the "
        "network Nmap scanned from.",
        SeverityLevel.MEDIUM,
        "Restrict SMB (port 445) to trusted internal networks only; do not "
        "expose it to untrusted or public networks.",
    ),
    1433: (
        "Microsoft SQL Server",
        "A database service is directly reachable from the network Nmap "
        "scanned from.",
        SeverityLevel.HIGH,
        "Restrict database access to trusted application servers only via "
        "firewall rules; do not expose database ports directly.",
    ),
    3306: (
        "MySQL",
        "A database service is directly reachable from the network Nmap "
        "scanned from.",
        SeverityLevel.HIGH,
        "Restrict database access to trusted application servers only via "
        "firewall rules; do not expose database ports directly.",
    ),
    3389: (
        "RDP",
        "Remote Desktop Protocol is directly reachable from the network "
        "Nmap scanned from, a common target for brute-force and "
        "ransomware campaigns.",
        SeverityLevel.MEDIUM,
        "Restrict RDP access to a VPN or bastion host, enforce "
        "network-level authentication (NLA), and require strong / "
        "MFA-protected credentials.",
    ),
    5432: (
        "PostgreSQL",
        "A database service is directly reachable from the network Nmap "
        "scanned from.",
        SeverityLevel.HIGH,
        "Restrict database access to trusted application servers only via "
        "firewall rules; do not expose database ports directly.",
    ),
    6379: (
        "Redis",
        "Redis is directly reachable from the network Nmap scanned from. "
        "Redis has no authentication enabled by default in many "
        "deployments.",
        SeverityLevel.HIGH,
        "Bind Redis to localhost or a private network, enable "
        "'requirepass', and restrict access via firewall rules.",
    ),
    9200: (
        "Elasticsearch",
        "Elasticsearch is directly reachable from the network Nmap scanned "
        "from. Elasticsearch has no authentication enabled by default in "
        "many deployments.",
        SeverityLevel.HIGH,
        "Restrict Elasticsearch access to trusted hosts, enable "
        "authentication/TLS, and avoid exposing it directly to untrusted "
        "networks.",
    ),
    27017: (
        "MongoDB",
        "MongoDB is directly reachable from the network Nmap scanned from. "
        "MongoDB has no authentication enabled by default in many "
        "deployments.",
        SeverityLevel.HIGH,
        "Enable MongoDB authentication, bind to a private network "
        "interface, and restrict access via firewall rules.",
    ),
}


@dataclass
class ConfigFinding:
    rule_id: str
    title: str
    description: str
    category: FindingCategory
    base_severity: SeverityLevel
    evidence: Dict[str, Any]
    remediation: str
    host_id: Optional[str] = None
    port_service_id: Optional[str] = None


def _port_evidence(host: Host, port: PortService) -> Dict[str, Any]:
    return {
        "ip_address": host.ip_address,
        "port": port.port_number,
        "protocol": port.protocol,
        "state": port.state,
        "service_name": port.service_name,
        "product": port.product,
        "version": port.version,
    }


def analyze_host(host: Host) -> List[ConfigFinding]:
    """Run all configuration/exposure checks against a single host's
    discovered ports. Returns ConfigFinding objects derived strictly from
    the host's actual PortService evidence."""
    findings: List[ConfigFinding] = []

    for port in host.port_services:
        if port.state != OPEN_STATE:
            continue

        findings.extend(_check_cleartext_protocol(host, port))
        findings.extend(_check_exposed_sensitive_service(host, port))
        findings.extend(_check_version_disclosure(host, port))

    return findings


def _check_cleartext_protocol(host: Host, port: PortService) -> List[ConfigFinding]:
    rule = CLEARTEXT_PROTOCOL_RULES.get(port.port_number)
    if rule is None:
        return []

    display_name, description, severity, remediation = rule
    return [
        ConfigFinding(
            rule_id=f"cleartext-protocol-{port.port_number}",
            title=f"Insecure cleartext protocol exposed: {display_name}",
            description=description,
            category=FindingCategory.CONFIGURATION,
            base_severity=severity,
            evidence=_port_evidence(host, port),
            remediation=remediation,
            host_id=str(host.id),
            port_service_id=str(port.id),
        )
    ]


def _check_exposed_sensitive_service(host: Host, port: PortService) -> List[ConfigFinding]:
    rule = EXPOSED_SENSITIVE_SERVICE_RULES.get(port.port_number)
    if rule is None:
        return []

    display_name, description, severity, remediation = rule
    return [
        ConfigFinding(
            rule_id=f"exposed-service-{port.port_number}",
            title=f"Sensitive service exposed: {display_name}",
            description=description,
            category=FindingCategory.EXPOSURE,
            base_severity=severity,
            evidence=_port_evidence(host, port),
            remediation=remediation,
            host_id=str(host.id),
            port_service_id=str(port.id),
        )
    ]


def _check_version_disclosure(host: Host, port: PortService) -> List[ConfigFinding]:
    """Flag when Nmap successfully fingerprinted a specific product/version.
    This is informational: exposed banners aid attacker reconnaissance and
    the identified version is also what CVE enrichment matches against
    later in the pipeline."""
    if not port.product and not port.version:
        return []

    version_str = f" {port.version}" if port.version else ""
    service_label = port.product or port.service_name or "unknown service"

    return [
        ConfigFinding(
            rule_id=f"version-disclosure-{port.port_number}",
            title=f"Service version information disclosed: {service_label}{version_str}",
            description=(
                "Nmap was able to fingerprint the specific product and/or "
                "version running on this port. This information aids "
                "attacker reconnaissance and is also used for vulnerability "
                "enrichment in this platform."
            ),
            category=FindingCategory.CONFIGURATION,
            base_severity=SeverityLevel.INFO,
            evidence=_port_evidence(host, port),
            remediation=(
                "Where feasible, suppress unnecessary version banners and "
                "ensure the running version is patched against known "
                "vulnerabilities (see vulnerability enrichment for this "
                "finding)."
            ),
            host_id=str(host.id),
            port_service_id=str(port.id),
        )
    ]