# ASR-Cyber-Lab Risk Methodology

## Purpose

The risk system converts security evidence into structured finding severity
and risk information.

The purpose is defensive prioritization.

---

# 1. Evidence First

Risk information should be interpreted together with the evidence collected
by the application.

Examples:

- discovered ports
- discovered services
- service state
- security observations
- vulnerability enrichment
- scan information

---

# 2. Severity

The application supports severity levels including:

critical
high
medium
low
info

Severity belongs to the finding.

---

# 3. Finding Status

Finding workflow status is separate from severity.

Supported workflow states include:

open
acknowledged
resolved
false_positive

Changing the workflow status does not automatically change the underlying
security evidence.

---

# 4. Risk Score

Findings contain risk information.

The application supports sorting findings by:

risk_score
created_at
severity
title

The application-specific risk score should not automatically be interpreted
as a CVSS score.

---

# 5. Vulnerability Enrichment

Vulnerability information is separate from the initial security finding.

The current implementation includes a local/static vulnerability reference
dataset.

A missing match does not prove that no vulnerability exists.

---

# 6. Example

If a scan observes an exposed Telnet service, the security-analysis stage can
create a finding describing the exposed service.

The finding can include:

- category
- severity
- evidence
- remediation
- risk information

The analysis path is:

Observed Service
       |
       v
Security Finding
       |
       v
Severity
       |
       v
Risk
       |
       v
Remediation

---

# 7. AI

AI is optional.

The deterministic risk engine remains authoritative.

AI explanations are supporting information.

AI must not be treated as the source of truth for:

- findings
- risk scores
- vulnerability records
- remediation status

---

# 8. False Positives

Findings may require human review.

The application supports:

false_positive

for findings that are determined to be incorrect or irrelevant.

---

# 9. False Negatives

The absence of a finding does not prove that a system is secure.

Detection depends on:

- network reachability
- Nmap visibility
- service detection
- implemented security checks
- vulnerability reference data

---

# 10. Interpretation

Recommended interpretation:

Observed Evidence
       |
       v
Finding
       |
       v
Severity
       |
       v
Risk
       |
       v
Vulnerability Reference
       |
       v
Remediation

AI explanation, when enabled, is additional context.

---

# 11. Limitations

Risk results do not provide:

- complete vulnerability coverage
- guaranteed exploitability assessment
- guaranteed security assurance
- automatic compliance certification

Important findings should be reviewed by an authorized security professional.