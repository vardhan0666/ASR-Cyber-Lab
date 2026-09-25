# ASR-Cyber-Lab Database

## Database Engine

ASR-Cyber-Lab uses PostgreSQL.

Docker Compose uses:

postgres:16-alpine

Persistent storage is provided through the Docker volume:

asr_postgres_data

---

# ORM

The backend uses:

SQLAlchemy

Database migrations use:

Alembic

Apply migrations:

docker compose exec backend alembic upgrade head

---

# Main Tables

The database contains the following major entities:

- users
- targets
- scans
- hosts
- port_services
- findings
- vulnerabilities
- audit_logs
- reports

---

# Relationships

Conceptually:

users
 |
 +---- targets
 |
 +---- scans
 |
 +---- audit_logs

targets
 |
 +---- scans

scans
 |
 +---- hosts
 |
 +---- findings
 |
 +---- reports

hosts
 |
 +---- port_services

findings
 |
 +---- vulnerabilities

---

# Users

Users contain authentication and authorization information.

Passwords are stored as password hashes.

Plaintext passwords are not stored.

Roles are used by the permission dependencies.

---

# Targets

Targets represent assets registered for scanning.

Target information includes information such as:

- name
- address
- description
- asset importance
- authorization state
- creator
- timestamps

Targets must be authorized before scanning.

---

# Scans

A scan records a reconnaissance operation.

Important relationships include:

- target
- initiating user
- hosts
- findings
- reports

Scan status includes:

pending
running
completed
failed

---

# Hosts

Hosts represent systems discovered during a scan.

Hosts belong to scans.

Information can include:

- IP address
- hostname
- discovery information

---

# Port Services

Port/service records represent discovered network services.

They are associated with discovered hosts.

These records are used as evidence for security analysis.

---

# Findings

Findings represent security observations.

They contain information such as:

- title
- description
- severity
- category
- status
- evidence
- remediation
- risk score

Finding workflow states include:

open
acknowledged
resolved
false_positive

---

# Vulnerabilities

Vulnerability records provide vulnerability-enrichment information associated
with findings.

The implementation contains a local/static vulnerability reference dataset.

A missing match does not prove that a target has no vulnerabilities.

---

# Audit Logs

Audit logs record security-relevant application actions.

Examples include:

- authentication events
- user creation
- target authorization changes
- finding status changes
- report generation

Audit-log access is administrator-controlled.

---

# Reports

Reports store generated report metadata.

Supported formats include:

JSON
PDF

Generated report files are stored using the application's report storage
configuration.

---

# Migrations

Use Alembic for schema changes.

Apply:

docker compose exec backend alembic upgrade head

Do not manually create application tables when using the migration system.