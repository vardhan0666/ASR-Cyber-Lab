# ASR-Cyber-Lab Limitations

## 1. Scope

ASR-Cyber-Lab is a defensive reconnaissance and attack-surface analysis
platform.

It is not a complete enterprise vulnerability-management system or complete
penetration-testing framework.

---

# 2. Authorization

The software cannot determine whether the operator has real-world permission.

The target authorization state is an application safety control.

It does not replace:

- legal authorization
- organizational approval
- network ownership
- rules of engagement

---

# 3. Network Visibility

The scanner can only analyze systems and services that it can reach and
observe.

Firewall rules, routing, segmentation and filtering can result in incomplete
results.

No discovered service does not prove that the service does not exist.

---

# 4. Nmap Dependency

The scanning workflow depends on Nmap.

Scan behavior can depend on:

- target availability
- network connectivity
- firewall rules
- routing
- selected scan profile
- timeout
- container networking

---

# 5. False Positives

Security findings can contain false positives.

Operators should validate important findings before remediation.

The finding workflow supports:

false_positive

---

# 6. False Negatives

The platform cannot guarantee complete detection.

Possible causes include:

- unreachable targets
- filtered ports
- incomplete service detection
- unsupported checks
- incomplete vulnerability data
- scan failures

---

# 7. Vulnerability Data

The current implementation contains a local/static vulnerability reference
dataset.

It is not equivalent to a continuously updated global vulnerability
database.

Therefore:

No vulnerability match

does not mean:

No vulnerability exists.

---

# 8. Risk Scores

Risk information is application-specific.

It should not automatically be interpreted as:

- a CVSS score
- proof of exploitability
- proof of compromise
- compliance certification
- complete security assurance

---

# 9. AI

AI is optional.

The core security workflow does not depend on AI.

AI may be unavailable when:

- AI is disabled
- configuration is missing
- the provider is unavailable
- the API key is invalid

The application should not fabricate AI output when AI is unavailable.

---

# 10. Scalability

The current architecture is suitable for a portfolio-grade defensive
application.

It should not automatically be considered a distributed enterprise scanning
platform.

Large deployments may require additional infrastructure such as:

- durable task queues
- worker pools
- distributed scheduling
- rate limiting
- centralized monitoring
- distributed storage

---

# 11. Report Storage

Generated reports depend on application-managed filesystem storage.

A report record can remain in the database while the associated file is no
longer available on disk.

---

# 12. Production Hardening

The development Docker configuration is not automatically a production
hardening baseline.

Production deployments should separately review:

- HTTPS/TLS
- reverse proxy
- secrets management
- database access
- network segmentation
- backups
- monitoring
- container hardening
- access policies

---

# 13. Security Scope

The project does not provide:

- arbitrary shell execution
- credential theft
- malware
- persistence
- evasion
- destructive exploitation
- guaranteed vulnerability coverage
- guaranteed security assurance