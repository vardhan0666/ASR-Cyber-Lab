"""
Vulnerability/CVE enrichment service.

IMPORTANT — DATA SOURCE TRANSPARENCY:
This service enriches findings using a SMALL, STATIC, LOCAL reference
dataset containing a small number of extremely well-documented, publicly
known CVEs, bundled with this project for demonstration purposes. It is
NOT a live feed and does NOT query the National Vulnerability Database
(NVD) or any other external vulnerability intelligence service at runtime.

For any product/version combination not present in the local reference
dataset, this service returns an EXPLICIT "unavailable" result. Callers
and the API MUST surface this as "vulnerability data unavailable" and
MUST NOT interpret it as "no vulnerabilities exist," and MUST NOT
fabricate a substitute result.

Entries are only added to LOCAL_REFERENCE_DATASET when:
  1. They correspond to a real, independently verifiable, publicly
     documented CVE, AND
  2. The match can be made against a SPECIFIC version string that Nmap's
     service/version detection is actually capable of reporting (i.e. the
     match is evidence-based, not an inference from service name alone).
"""

from dataclasses import dataclass
from typing import List, Optional

from app.models.finding import SeverityLevel

SOURCE_LOCAL = (
    "Local static reference dataset (offline, demonstration data derived "
    "from public CVE records)"
)
SOURCE_UNAVAILABLE = "none"


@dataclass
class CVEMatch:
    cve_id: Optional[str]
    description: str
    cvss_score: Optional[float]
    severity: Optional[SeverityLevel]
    reference_url: Optional[str]
    source: str
    data_available: bool


@dataclass
class _LocalCVEEntry:
    product_match: str  # lowercase substring matched against reported product
    version_match: Optional[str]  # lowercase substring matched against reported version
    cve_id: str
    description: str
    cvss_score: Optional[float]
    severity: SeverityLevel
    reference_url: str


# A deliberately small, manually curated set of extremely well-known,
# publicly documented vulnerabilities, matched only against SPECIFIC
# version strings Nmap can actually report. This dataset is NOT exhaustive
# and MUST NOT be treated as authoritative — always verify against the
# live NVD record at the reference_url before making security decisions.
LOCAL_REFERENCE_DATASET: List[_LocalCVEEntry] = [
    _LocalCVEEntry(
        product_match="vsftpd",
        version_match="2.3.4",
        cve_id="CVE-2011-2523",
        description=(
            "vsftpd 2.3.4, as distributed from a compromised upload "
            "archive in 2011, contained a backdoor that could grant a "
            "remote attacker a command shell. This is one of the most "
            "widely documented backdoor incidents in public vulnerability "
            "databases and is matched here because the exact vulnerable "
            "version string ('2.3.4') was reported by the scan."
        ),
        cvss_score=10.0,
        severity=SeverityLevel.CRITICAL,
        reference_url="https://nvd.nist.gov/vuln/detail/CVE-2011-2523",
    ),
]


def lookup_vulnerabilities(
    product: Optional[str], version: Optional[str]
) -> List[CVEMatch]:
    """Look up known vulnerabilities for a given product/version pair
    against the local static reference dataset.

    Returns EITHER:
      - one or more real CVEMatch entries with data_available=True, or
      - a single CVEMatch with data_available=False, cve_id=None,
        explicitly stating that no local reference data was available.

    Returns an empty list ONLY when `product` is None/blank, since there is
    no evidence at all on which to attempt a match.
    """
    if not product or not product.strip():
        return []

    normalized_product = product.strip().lower()
    normalized_version = version.strip().lower() if version else None

    matches: List[CVEMatch] = []
    for entry in LOCAL_REFERENCE_DATASET:
        if entry.product_match not in normalized_product:
            continue
        if entry.version_match is not None:
            if normalized_version is None or entry.version_match not in normalized_version:
                continue

        matches.append(
            CVEMatch(
                cve_id=entry.cve_id,
                description=entry.description,
                cvss_score=entry.cvss_score,
                severity=entry.severity,
                reference_url=entry.reference_url,
                source=SOURCE_LOCAL,
                data_available=True,
            )
        )

    if matches:
        return matches

    version_display = version if version else "unknown"
    return [
        CVEMatch(
            cve_id=None,
            description=(
                f"No local reference data is available for product "
                f"'{product}' version '{version_display}'. This platform "
                "uses a small local static dataset and does not query a "
                "live vulnerability feed in this deployment. This does NOT "
                "mean the service is free of vulnerabilities — it means no "
                "match was found in the local reference data."
            ),
            cvss_score=None,
            severity=None,
            reference_url=None,
            source=SOURCE_UNAVAILABLE,
            data_available=False,
        )
    ]