# ASR-Cyber-Lab Architecture

## 1. Overview

ASR-Cyber-Lab is an Automated Security Reconnaissance and Attack-Surface
Reduction Platform for authorized defensive security testing.

High-level architecture:

React Frontend
       |
       | HTTP / JSON
       v
FastAPI Backend
       |
       +---- PostgreSQL
       |
       +---- Nmap
       |
       +---- Security Analysis
       |
       +---- Risk Engine
       |
       +---- Report Generation
       |
       +---- Audit Logging
       |
       +---- Optional AI

---

# 2. Frontend

The frontend uses:

- React
- TypeScript
- Vite
- Tailwind CSS
- Axios
- React Router
- Recharts

The frontend provides the user interface for:

- authentication
- dashboard
- targets
- scans
- hosts
- findings
- reports
- AI assistance where enabled

Development frontend:

http://localhost:5173

---

# 3. Backend

The backend uses:

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- Nmap
- ReportLab

The API is mounted under:

/api

The backend provides:

- authentication
- authorization
- target management
- scan management
- Nmap execution
- result parsing
- security analysis
- vulnerability enrichment
- risk information
- report generation
- audit logging
- optional AI assistance

---

# 4. Database

PostgreSQL is the persistent application database.

Main entities include:

- users
- targets
- scans
- hosts
- port_services
- findings
- vulnerabilities
- audit_logs
- reports

SQLAlchemy is used for ORM/database access.

Alembic manages schema migrations.

---

# 5. Scan Architecture

The scan workflow is:

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

Clients can poll:

GET /api/scans/{scan_id}

for scan status.

---

# 6. Nmap Execution

Nmap is invoked through subprocess execution.

The implementation uses:

subprocess.run(list_of_args, shell=False)

The scan workflow uses fixed, server-defined scan profiles.

Raw user input is not directly converted into arbitrary shell commands.

---

# 7. Docker Architecture

Docker Compose contains:

db
backend
frontend

Database:

postgres:16-alpine

Backend:

Python 3.10 application

Frontend:

Node/Vite application

The backend connects to PostgreSQL through the Docker service:

db

---

# 8. Backend Container Security

The backend Docker image:

- installs Nmap
- installs required PostgreSQL build libraries
- configures Nmap capabilities
- creates a non-root appuser
- runs Uvicorn as the application server

Nmap receives:

cap_net_raw
cap_net_admin

through the image/container configuration required by the supported scan
workflow.

---

# 9. Authentication Architecture

Authentication uses:

- password hashing
- JWT access tokens
- active-user checks
- role-based permission dependencies

Passwords are not stored as plaintext.

---

# 10. Optional AI

AI is an optional assistance layer.

The deterministic security workflow does not depend on AI.

AI does not replace:

- scan evidence
- findings
- risk scoring
- remediation information

When AI is unavailable, the application reports that state rather than
fabricating an answer.