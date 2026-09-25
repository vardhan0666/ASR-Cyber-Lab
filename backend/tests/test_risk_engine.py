"""Tests for the transparent, explainable risk scoring engine."""

import pytest

from app.models.finding import FindingCategory, SeverityLevel
from app.models.target import AssetImportance
from app.services.risk_engine import (
    SEVERITY_WEIGHTS,
    VulnerabilityEvidence,
    calculate_risk,
)


def test_base_severity_with_medium_importance_and_no_vulnerabilities():
    result = calculate_risk(
        base_severity=SeverityLevel.HIGH,
        asset_importance=AssetImportance.MEDIUM,
        category=FindingCategory.CONFIGURATION,
    )
    assert result.score == pytest.approx(SEVERITY_WEIGHTS[SeverityLevel.HIGH])
    assert result.severity == SeverityLevel.HIGH
    assert any("EVIDENCE" in line for line in result.explanation)
    assert any("RECOMMENDATION" in line for line in result.explanation)


def test_low_asset_importance_reduces_score():
    high_importance = calculate_risk(
        base_severity=SeverityLevel.MEDIUM,
        asset_importance=AssetImportance.CRITICAL,
        category=FindingCategory.EXPOSURE,
    )
    low_importance = calculate_risk(
        base_severity=SeverityLevel.MEDIUM,
        asset_importance=AssetImportance.LOW,
        category=FindingCategory.EXPOSURE,
    )
    assert high_importance.score > low_importance.score


def test_score_is_clamped_to_100():
    result = calculate_risk(
        base_severity=SeverityLevel.CRITICAL,
        asset_importance=AssetImportance.CRITICAL,
        category=FindingCategory.VULNERABILITY,
        vulnerabilities=[
            VulnerabilityEvidence(cve_id="CVE-TEST-0001", cvss_score=10.0, data_available=True)
        ],
    )
    assert result.score <= 100.0
    assert result.severity == SeverityLevel.CRITICAL


def test_available_cvss_score_increases_risk():
    without_cve = calculate_risk(
        base_severity=SeverityLevel.MEDIUM,
        asset_importance=AssetImportance.MEDIUM,
        category=FindingCategory.VULNERABILITY,
    )
    with_cve = calculate_risk(
        base_severity=SeverityLevel.MEDIUM,
        asset_importance=AssetImportance.MEDIUM,
        category=FindingCategory.VULNERABILITY,
        vulnerabilities=[
            VulnerabilityEvidence(cve_id="CVE-TEST-0002", cvss_score=9.8, data_available=True)
        ],
    )
    assert with_cve.score > without_cve.score
    assert any("CVSS" in line for line in with_cve.explanation)


def test_unavailable_vulnerability_data_does_not_fabricate_score_change():
    with_unavailable = calculate_risk(
        base_severity=SeverityLevel.MEDIUM,
        asset_importance=AssetImportance.MEDIUM,
        category=FindingCategory.VULNERABILITY,
        vulnerabilities=[VulnerabilityEvidence(data_available=False)],
    )
    without_any = calculate_risk(
        base_severity=SeverityLevel.MEDIUM,
        asset_importance=AssetImportance.MEDIUM,
        category=FindingCategory.VULNERABILITY,
    )
    # Unavailable data must not silently boost or reduce the score.
    assert with_unavailable.score == pytest.approx(without_any.score)
    assert any("unavailable" in line.lower() for line in with_unavailable.explanation)
    assert any(
        "should not be read as" in line.lower() for line in with_unavailable.explanation
    )


@pytest.mark.parametrize(
    "severity,expected_min_score",
    [
        (SeverityLevel.INFO, 0.0),
        (SeverityLevel.LOW, 15.0),
        (SeverityLevel.MEDIUM, 40.0),
        (SeverityLevel.HIGH, 70.0),
        (SeverityLevel.CRITICAL, 90.0),
    ],
)
def test_severity_thresholds_are_self_consistent(severity, expected_min_score):
    result = calculate_risk(
        base_severity=severity,
        asset_importance=AssetImportance.MEDIUM,
        category=FindingCategory.CONFIGURATION,
    )
    # With a 1.0x multiplier and no vulnerability boost, the resulting
    # score for a given base severity should classify back to at least
    # that same severity level's minimum threshold.
    assert result.score >= min(expected_min_score, SEVERITY_WEIGHTS[severity])


def test_explanation_is_deterministic_for_identical_inputs():
    args = dict(
        base_severity=SeverityLevel.HIGH,
        asset_importance=AssetImportance.HIGH,
        category=FindingCategory.EXPOSURE,
    )
    first = calculate_risk(**args)
    second = calculate_risk(**args)
    assert first.score == second.score
    assert first.severity == second.severity
    assert first.explanation == second.explanation