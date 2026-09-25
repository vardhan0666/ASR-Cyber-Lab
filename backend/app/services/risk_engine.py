"""
Transparent, explainable risk scoring engine.

Every risk score produced here is accompanied by a human-readable
explanation list describing exactly which factors contributed to the
score, each explicitly labeled as EVIDENCE, INFERENCE, NOTE, or
RECOMMENDATION so consumers (API, UI, reports, AI summaries) can always
distinguish observed fact from derived judgment.

Factors considered:
  - the base severity of the underlying evidence (a configuration issue or
    exposure, as classified by app.services.config_analysis_service)
  - the business importance of the affected asset
  - known vulnerability (CVE/CVSS) data, when available

This module never invents or guesses evidence. If vulnerability data is
unavailable, that fact is reflected explicitly in the explanation instead
of silently contributing (or omitting) a score component.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from app.models.finding import FindingCategory, SeverityLevel
from app.models.target import AssetImportance

# Base numeric weight (0-100 scale) assigned to each severity level. This is
# the starting point before asset importance / vulnerability adjustments.
SEVERITY_WEIGHTS: Dict[SeverityLevel, float] = {
    SeverityLevel.INFO: 5.0,
    SeverityLevel.LOW: 25.0,
    SeverityLevel.MEDIUM: 50.0,
    SeverityLevel.HIGH: 75.0,
    SeverityLevel.CRITICAL: 95.0,
}

# Multiplier applied based on how important the affected asset is to the
# organization. A misconfiguration on a CRITICAL asset is treated as more
# urgent than the identical misconfiguration on a LOW-importance asset.
ASSET_IMPORTANCE_MULTIPLIERS: Dict[AssetImportance, float] = {
    AssetImportance.LOW: 0.8,
    AssetImportance.MEDIUM: 1.0,
    AssetImportance.HIGH: 1.2,
    AssetImportance.CRITICAL: 1.4,
}

# Score thresholds used to translate a final numeric score back into a
# discrete severity label. Evaluated top-down; first matching (inclusive)
# lower bound wins.
SCORE_TO_SEVERITY_THRESHOLDS: List[Tuple[float, SeverityLevel]] = [
    (90.0, SeverityLevel.CRITICAL),
    (70.0, SeverityLevel.HIGH),
    (40.0, SeverityLevel.MEDIUM),
    (15.0, SeverityLevel.LOW),
    (0.0, SeverityLevel.INFO),
]


@dataclass
class VulnerabilityEvidence:
    """Minimal shape of vulnerability data the risk engine considers.
    Constructed by callers (cve_service, scan_orchestrator) from actual
    Vulnerability rows — this dataclass is never populated with fabricated
    values by the risk engine itself."""

    cve_id: Optional[str] = None
    cvss_score: Optional[float] = None
    data_available: bool = True


@dataclass
class RiskResult:
    score: float
    severity: SeverityLevel
    explanation: List[str] = field(default_factory=list)


def _score_to_severity(score: float) -> SeverityLevel:
    for threshold, severity in SCORE_TO_SEVERITY_THRESHOLDS:
        if score >= threshold:
            return severity
    return SeverityLevel.INFO


def calculate_risk(
    base_severity: SeverityLevel,
    asset_importance: AssetImportance,
    category: FindingCategory,
    vulnerabilities: Optional[List[VulnerabilityEvidence]] = None,
) -> RiskResult:
    """Compute a transparent, explainable risk score for a single finding.

    Returns a RiskResult whose `explanation` field documents exactly how
    the final score/severity were derived, in the order the factors were
    applied. This function is deterministic and pure — calling it twice
    with the same inputs always yields the same result, which is what
    makes the risk model auditable.
    """
    explanation: List[str] = []
    vulnerabilities = vulnerabilities or []

    base_weight = SEVERITY_WEIGHTS[base_severity]
    explanation.append(
        f"EVIDENCE: Base severity for this {category.value} finding is "
        f"'{base_severity.value}' (base weight {base_weight:.1f}/100), "
        "determined directly from the scan evidence."
    )

    multiplier = ASSET_IMPORTANCE_MULTIPLIERS[asset_importance]
    adjusted_score = base_weight * multiplier
    explanation.append(
        f"INFERENCE: Affected asset is marked '{asset_importance.value}' "
        f"importance, applying a {multiplier:.1f}x multiplier "
        f"({base_weight:.1f} -> {adjusted_score:.1f})."
    )

    available_cvss_scores = [
        v.cvss_score
        for v in vulnerabilities
        if v.data_available and v.cvss_score is not None
    ]

    if available_cvss_scores:
        max_cvss = max(available_cvss_scores)
        # CVSS is 0-10; scale its contribution to a 0-30 point boost so a
        # critical CVE (CVSS 10.0) meaningfully raises the score without
        # single-handedly dominating the final result.
        cvss_boost = (max_cvss / 10.0) * 30.0
        adjusted_score += cvss_boost
        explanation.append(
            f"EVIDENCE: A known vulnerability with CVSS score {max_cvss:.1f} "
            f"is associated with this finding, adding {cvss_boost:.1f} "
            "points to the risk score."
        )
    else:
        checked_but_unavailable = any(not v.data_available for v in vulnerabilities)
        if checked_but_unavailable:
            explanation.append(
                "NOTE: Vulnerability intelligence was checked for this "
                "finding but was unavailable; no CVSS-based adjustment was "
                "applied. This should NOT be read as 'no vulnerabilities "
                "exist' — only that data could not be retrieved."
            )
        else:
            explanation.append(
                "NOTE: No known-vulnerability data is associated with this "
                "finding; the score reflects configuration/exposure "
                "evidence only."
            )

    final_score = max(0.0, min(100.0, adjusted_score))
    final_severity = _score_to_severity(final_score)

    explanation.append(
        f"RECOMMENDATION: Final risk score is {final_score:.1f}/100, "
        f"classified as '{final_severity.value}' severity. Prioritize "
        "remediation accordingly relative to other open findings."
    )

    return RiskResult(score=final_score, severity=final_severity, explanation=explanation)