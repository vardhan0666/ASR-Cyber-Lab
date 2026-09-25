"""
Remediation guidance service.

Combines the remediation text produced by configuration analysis
(app.services.config_analysis_service) with any vulnerability-specific
guidance available from CVE enrichment (app.services.cve_service) into a
single remediation string stored on the Finding record.

This module never invents remediation steps for vulnerabilities it has no
evidence for — vulnerability-specific guidance is only appended when a
real, matched CVE (data_available=True) is present.
"""

from typing import List

from app.services.cve_service import CVEMatch


def build_remediation(base_remediation: str, vulnerabilities: List[CVEMatch]) -> str:
    """Build the final remediation text for a finding.

    Args:
        base_remediation: remediation text from the configuration/exposure
            rule that generated the finding (always present).
        vulnerabilities: CVE enrichment results attempted for this finding
            (may be empty if no product/version evidence existed).
    """
    parts = [base_remediation.strip()]

    matched = [v for v in vulnerabilities if v.data_available and v.cve_id]
    if matched:
        for vuln in matched:
            cvss_part = (
                f" (CVSS {vuln.cvss_score:.1f})" if vuln.cvss_score is not None else ""
            )
            parts.append(
                f"This finding is associated with {vuln.cve_id}{cvss_part}. "
                "Apply vendor patches or upgrade the affected software to a "
                f"version that resolves this vulnerability. Reference: "
                f"{vuln.reference_url}"
            )

    unavailable = [v for v in vulnerabilities if not v.data_available]
    if unavailable and not matched:
        parts.append(
            "Vulnerability intelligence for the detected product/version "
            "was not available in this deployment's local reference "
            "dataset; verify the software version against an authoritative "
            "source (e.g. the vendor advisory or NVD) before concluding no "
            "known vulnerabilities apply."
        )

    return " ".join(parts)