# ASR-Cyber-Lab Scanning Workflow

## Overview

The scanning workflow is:

Authorized Target
       |
       v
Create Scan
       |
       v
Pending
       |
       v
Background Task
       |
       v
Nmap
       |
       v
XML Output
       |
       v
Parser
       |
       +---- Hosts
       |
       +---- Port Services
       |
       +---- Findings
       |
       +---- Vulnerability Enrichment
       |
       +---- Risk
       |
       v
PostgreSQL
       |
       +---- Dashboard
       +---- Findings
       +---- Reports

---

# 1. Target Registration

A target is registered through the target-management API.

A target contains information required by the scanning workflow.

The target has an authorization state.

---

# 2. Target Authorization

The target must be authorized before scanning.

The scan creation service checks target authorization.

Unauthorized targets cannot proceed through the normal scan creation flow.

---

# 3. Scan Creation

The client submits a scan request.

The scan uses:

- target ID
- server-defined scan profile

The application does not expose arbitrary Nmap command-line flags.

---

# 4. Scan States

A scan can transition through:

pending
running
completed

or:

pending
running
failed

The client can poll:

GET /api/scans/{scan_id}

---

# 5. Background Execution

The API creates the scan database record first.

The Nmap operation is then executed asynchronously through a FastAPI
background task.

This prevents the initial HTTP request from having to remain open for the
entire scan.

---

# 6. Nmap Execution

Nmap is invoked through controlled subprocess execution.

The application uses:

subprocess.run(list_of_args, shell=False)

Scan profiles are fixed by the server.

Raw user input does not become arbitrary shell commands.

---

# 7. Timeout

The configured timeout is:

NMAP_TIMEOUT_SECONDS

Default development value:

600

A timeout prevents a scan process from running indefinitely.

---

# 8. Nmap XML

Nmap produces XML output for the parser.

The parser extracts information such as:

- hosts
- IP addresses
- hostnames
- ports
- port states
- services
- service information

---

# 9. Host Normalization

Discovered hosts are normalized into host records.

Hosts are associated with the scan that discovered them.

---

# 10. Service Normalization

Port/service records represent discovered services.

These records provide evidence for later security analysis.

---

# 11. Security Analysis

The security-analysis stage evaluates discovered evidence.

It can produce findings containing:

- title
- description
- category
- severity
- evidence
- remediation
- risk information

---

# 12. Vulnerability Enrichment

The application can associate vulnerability information with applicable
findings.

The current implementation contains a local/static vulnerability reference
dataset.

---

# 13. Database Persistence

The scan workflow stores results in PostgreSQL.

Important records include:

- scans
- hosts
- port services
- findings
- vulnerabilities
- reports

---

# 14. Reports

After scan processing, reports can be generated.

Supported formats include:

JSON
PDF

---

# 15. Failure Handling

If Nmap execution fails, the scan is marked as failed.

A failed scan must not be interpreted as a successful security assessment.

Backend logs:

docker compose logs backend

---

# 16. Safe Testing

Use only authorized targets.

Recommended development targets:

- localhost
- private lab systems
- isolated virtual machines
- authorized training systems