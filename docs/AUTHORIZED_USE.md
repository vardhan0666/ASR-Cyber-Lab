# ASR-Cyber-Lab Authorized Use

## Purpose

ASR-Cyber-Lab is intended for authorized defensive security testing.

It helps operators identify:

- exposed services
- discovered assets
- security findings
- attack-surface information
- remediation information

---

# Authorization Requirement

Only scan systems that you own or are explicitly authorized to assess.

Appropriate examples include:

- your own computer
- localhost
- your own virtual machines
- private cybersecurity laboratories
- authorized college/lab systems
- authorized company infrastructure
- dedicated security training environments

A publicly reachable system is not automatically an authorized target.

---

# Target Authorization

The application contains an authorization state for targets.

A target should be explicitly authorized before a scan is launched.

The application-level authorization mechanism does not replace real-world
permission.

Authorization should come from the responsible system owner or organization.

---

# Recommended Development Targets

For development and demonstrations use:

- localhost
- private IP addresses in your own lab
- isolated virtual machines
- authorized training environments

---

# Prohibited Use

Do not use this project for:

- unauthorized scanning
- credential theft
- malware deployment
- persistence
- evasion
- destructive exploitation
- denial-of-service activity
- unauthorized data collection
- bypassing access controls

---

# Nmap Restrictions

The backend invokes Nmap using controlled subprocess execution.

The application does not provide an arbitrary shell command interface.

Server-defined scan profiles are used instead of allowing arbitrary Nmap
arguments.

---

# Sensitive Information

Scan results can contain sensitive infrastructure information.

Examples:

- IP addresses
- hostnames
- ports
- service versions
- findings
- vulnerability information
- reports
- audit logs

Do not publish real organizational scan results publicly.

---

# Safe Demonstration

For a college or GitHub demonstration:

1. Use a local or isolated lab.
2. Register the target.
3. Confirm authorization.
4. Run the supported scan.
5. Review discovered hosts.
6. Review services.
7. Review findings.
8. Review risk information.
9. Generate a report.
10. Remove sensitive information from screenshots before publishing.

---

# Responsibility

The application cannot determine whether the operator has real-world
authorization.

The operator is responsible for ensuring that every target is authorized.