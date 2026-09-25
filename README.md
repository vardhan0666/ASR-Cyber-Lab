# ASR-Cyber-Lab

**Automated Security Reconnaissance & Attack-Surface Reduction Platform**

A portfolio-grade, defensive-only cybersecurity platform for discovering and
analyzing assets, ports, services, security misconfigurations, and known
vulnerability information on systems you **own or are explicitly authorized
to test**.

> ⚠️ **AUTHORIZED USE ONLY.** This platform performs no exploitation,
> credential attacks, malware, persistence, or evasion. Scanning any target
> without explicit written authorization is illegal in most jurisdictions.
> See [docs/AUTHORIZED_USE.md](docs/AUTHORIZED_USE.md).

## What This Project Does

1. You register **authorized targets** (IP, CIDR range, or hostname you own/control).
2. You launch a **scan** using a fixed, server-validated Nmap profile (no raw flags).
3. Nmap results are parsed and normalized into hosts, ports, and services.
4. Security configuration checks and CVE enrichment run against the evidence.
5. A **transparent risk engine** scores each finding and explains exactly why.
6. Results appear on a **dashboard**, with drill-down into assets/scans/findings.
7. You can export **JSON** and **PDF** reports, and review a full **audit log**.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + TypeScript + Vite + Tailwind CSS |
| Backend | Python + FastAPI + Pydantic + SQLAlchemy + Alembic |
| Database | PostgreSQL |
| Scanning | Nmap (subprocess, argument-allowlisted) |
| Infra | Docker Compose |
| Testing | Pytest (backend), Vitest (frontend) |

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Installation](docs/INSTALLATION.md)
- [Configuration](docs/CONFIGURATION.md)
- [API Reference](docs/API.md)
- [Database Schema](docs/DATABASE.md)
- [Security Model](docs/SECURITY_MODEL.md)
- [Authorized Use Policy](docs/AUTHORIZED_USE.md)
- [Scanning Workflow](docs/SCANNING_WORKFLOW.md)
- [Risk Methodology](docs/RISK_METHODOLOGY.md)
- [Testing Guide](docs/TESTING.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Limitations](docs/LIMITATIONS.md)

## Project Status

This project is under active, incremental development. See
[AI_BUILD_STATE.md](AI_BUILD_STATE.md) for exact build progress. Setup and
run instructions will be published in the README once all planned files are
complete and integration-reviewed.

## Ethical & Legal Notice

Only scan infrastructure you own or have explicit, documented authorization
to test. The maintainers assume no responsibility for misuse. This is a
defensive security engineering project intended for learning, authorized
lab environments, and portfolio demonstration.