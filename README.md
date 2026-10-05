# 🛡️ ASR-Cyber-Lab

### Automated Security Reconnaissance & Attack-Surface Reduction Platform

<p align="center">

**A portfolio-grade defensive cybersecurity platform for discovering, analyzing, prioritizing, and reporting the attack surface of authorized systems.**

</p>

---

## 📌 Abstract

**ASR-Cyber-Lab** is a full-stack defensive cybersecurity platform designed to help security practitioners understand what is exposed in an authorized environment.

The platform provides a controlled workflow for registering authorized targets, performing server-validated Nmap reconnaissance, normalizing discovered hosts/ports/services, analyzing security-relevant configuration information, generating security findings, calculating transparent risk scores, and producing JSON/PDF reports.

Instead of treating reconnaissance as a one-off command-line operation, ASR-Cyber-Lab turns it into a persistent and auditable security workflow.

> **Core idea:**  
> **Discover → Analyze → Prioritize → Report → Remediate → Re-scan**

---

## ⚠️ Authorized Use & Safety

**ASR-Cyber-Lab is strictly for defensive and authorized security testing.**

Only scan:

- Systems you own
- Localhost/lab environments
- Private infrastructure under your control
- Systems for which you have explicit authorization

The platform is not designed for:

- Unauthorized scanning
- Credential theft
- Malware
- Persistence
- Evasion
- Destructive exploitation
- Attacking third-party infrastructure

See [`docs/AUTHORIZED_USE.md`](docs/AUTHORIZED_USE.md) for the project's authorized-use policy.

---

# 🎯 What This Project Does

ASR-Cyber-Lab follows a complete attack-surface assessment workflow:

```text
Authorized Target
       │
       ▼
Target Validation
       │
       ▼
Nmap Reconnaissance
       │
       ▼
Host Discovery
       │
       ▼
Port & Service Enumeration
       │
       ▼
Security Configuration Analysis
       │
       ▼
Vulnerability Enrichment
       │
       ▼
Finding Generation
       │
       ▼
Risk Scoring
       │
       ▼
Dashboard + Reports
       │
       ▼
Audit Log
```

### Core capabilities

- 🔐 JWT-based authentication
- 🎯 Authorized target management
- 🌐 Host discovery
- 🔎 Port and service enumeration
- 🧪 Server-validated Nmap scan profiles
- ⚙️ Security configuration analysis
- 🧩 Vulnerability/CVE enrichment architecture
- 🚨 Finding generation and severity classification
- 📊 Transparent risk scoring
- 📄 JSON report generation
- 📑 PDF report generation
- 🧾 Audit logging
- 🗄️ PostgreSQL persistence
- 🐳 Docker Compose deployment
- 🖥️ React/TypeScript security dashboard
- 🌌 Three.js/WebGL cyber interface

---

# 🧠 Why I Built It

Traditional Nmap output is useful, but raw scan results alone do not provide a complete security-management workflow.

ASR-Cyber-Lab was designed to answer:

> **"What is exposed, how important is it, what security evidence do we have, how risky is it, and can we produce an auditable report?"**

The project combines cybersecurity concepts with full-stack software engineering:

**Cybersecurity + Networking + Backend Engineering + Database Design + Frontend Engineering + DevOps + Security Reporting**

---

# 🏗️ Architecture

```text
                         ┌─────────────────────────┐
                         │      React Frontend     │
                         │ Dashboard / Targets /   │
                         │ Scans / Findings /      │
                         │ Reports / Audit Logs    │
                         └────────────┬────────────┘
                                      │
                                  HTTP / JWT
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │       FastAPI API       │
                         │ Authentication / Routes │
                         │ Validation / Services   │
                         └────────────┬────────────┘
                                      │
                 ┌────────────────────┼────────────────────┐
                 │                    │                    │
                 ▼                    ▼                    ▼
        ┌────────────────┐   ┌────────────────┐   ┌────────────────┐
        │ PostgreSQL     │   │ Scan Engine    │   │ Risk / Finding │
        │ Persistence    │   │ Nmap           │   │ Analysis       │
        └────────────────┘   └───────┬────────┘   └────────────────┘
                                     │
                                     ▼
                           ┌────────────────────┐
                           │ Hosts / Ports /    │
                           │ Services / Evidence│
                           └─────────┬──────────┘
                                     │
                                     ▼
                           ┌────────────────────┐
                           │ JSON / PDF Reports │
                           │ + Audit Events     │
                           └────────────────────┘
```

---

# 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Vite |
| UI | Tailwind CSS |
| Visualization | Recharts |
| 3D UI | Three.js / WebGL |
| API | Python, FastAPI |
| Validation | Pydantic |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Database | PostgreSQL |
| Reconnaissance | Nmap |
| Authentication | JWT |
| Testing | Pytest, Vitest |
| Infrastructure | Docker, Docker Compose |
| Version Control | Git + GitHub |

---

# 🚀 Installation & Running

## Prerequisites

Install:

- Git
- Docker Desktop
- Node.js
- Python 3.10+
- Nmap

Verify:

```powershell
git --version
docker --version
node --version
python --version
nmap --version
```

---

## 1. Clone the repository

```powershell
git clone https://github.com/vardhan0666/ASR-Cyber-Lab.git
cd ASR-Cyber-Lab
```

---

## 2. Configure environment variables

The real `.env` file is intentionally **not committed to GitHub**.

Create your local environment file from the example:

```powershell
Copy-Item .env.example .env
```

Then edit `.env` and configure the local database, backend, frontend, and authentication settings.

**Never commit `.env` to GitHub.**

---

## 3. Start Docker services

From the project root:

```powershell
docker compose up -d
```

Check containers:

```powershell
docker ps
```

---

## 4. Verify the backend

The configured development backend runs on port `8001`.

PowerShell:

```powershell
curl.exe http://localhost:8001/api/health
```

Expected response:

```json
{
  "status": "ok",
  "environment": "development"
}
```

---

## 5. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Vite will display the local URL, normally:

```text
http://localhost:5173
```

If that port is already occupied, Vite may automatically select another port such as `5174`.

---

# 🔄 Typical Usage

1. Sign in to the application.
2. Create an assessment target.
3. Mark the target as authorized.
4. Select an approved scan profile.
5. Start the scan.
6. Review discovered hosts.
7. Review ports and services.
8. Review generated security findings.
9. Inspect severity and risk score.
10. Generate a JSON or PDF report.
11. Review audit logs.
12. Remediate issues in the authorized environment.
13. Re-scan to verify the result.

---

# 🧪 Demonstrated Local-Lab Test

The platform has been tested against an authorized localhost environment:

```text
Target:       127.0.0.1
Profile:      Standard
Host:         localhost
Service:      Uvicorn / HTTP
Port:         TCP/8000
Finding:      Service-version information disclosure
Severity:     Informational
Risk Score:   5.0 / 100
```

The workflow successfully demonstrated:

```text
Target
  ↓
Authorization
  ↓
Nmap Scan
  ↓
Host Discovery
  ↓
Service Discovery
  ↓
Finding
  ↓
Risk Score
  ↓
JSON/PDF Report
  ↓
Audit Log
```

---

# 📊 Risk Model

The platform uses a transparent risk-oriented model rather than hiding the reasoning behind an unexplained score.

Risk can consider factors such as:

- Finding severity
- Asset importance
- Exposure characteristics
- Security evidence
- Vulnerability information where available

The goal is to make the result explainable:

> **A security score should help a defender understand why something deserves attention.**

See [`docs/RISK_METHODOLOGY.md`](docs/RISK_METHODOLOGY.md).

---

# 📁 Repository Structure

```text
ASR-Cyber-Lab/
│
├── backend/
│   ├── app/
│   ├── tests/
│   └── ...
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── ...
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── INSTALLATION.md
│   ├── CONFIGURATION.md
│   ├── API.md
│   ├── DATABASE.md
│   ├── SECURITY_MODEL.md
│   ├── AUTHORIZED_USE.md
│   ├── SCANNING_WORKFLOW.md
│   ├── RISK_METHODOLOGY.md
│   ├── TESTING.md
│   ├── TROUBLESHOOTING.md
│   └── LIMITATIONS.md
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── AI_BUILD_STATE.md
└── README.md
```

---

# 🧪 Testing

Backend tests:

```powershell
docker compose exec backend pytest
```

Frontend build:

```powershell
cd frontend
npm run build
```

For the complete testing procedure, see:

[`docs/TESTING.md`](docs/TESTING.md)

---

# 🐳 Useful Docker Commands

Start:

```powershell
docker compose up -d
```

View containers:

```powershell
docker ps
```

View backend logs:

```powershell
docker compose logs -f backend
```

View all logs:

```powershell
docker compose logs -f
```

Stop:

```powershell
docker compose down
```

Rebuild:

```powershell
docker compose up -d --build
```

---

# 🔐 Security Engineering Principles

ASR-Cyber-Lab follows several defensive principles:

### 1. Explicit authorization

A target should be explicitly authorized before scanning.

### 2. Controlled scan profiles

The backend controls supported scan profiles rather than accepting arbitrary raw Nmap arguments from the client.

### 3. Evidence-based findings

A service/version observation is not automatically treated as proof of a vulnerability.

### 4. Auditability

Important actions are recorded through audit events.

### 5. Secret separation

Local secrets are stored in `.env` and excluded from version control.

---

# 📈 Future Roadmap

Potential future releases include:

- [ ] Historical scan comparison
- [ ] Attack-surface trend dashboards
- [ ] Scheduled recurring scans
- [ ] Expanded CVE/CVSS enrichment
- [ ] Role-based access control
- [ ] Multi-project tenancy
- [ ] Background scan job queues
- [ ] Notification integrations
- [ ] Remediation tracking
- [ ] Advanced security metrics
- [ ] Improved scan-result comparison

---

# 🎓 Portfolio Value

ASR-Cyber-Lab demonstrates practical experience in:

- Cybersecurity reconnaissance
- Attack-surface management
- TCP/IP and network-service concepts
- Nmap integration
- Security findings
- Risk modeling
- Secure API design
- Authentication and authorization
- PostgreSQL database design
- React/TypeScript development
- Dockerized application deployment
- Security reporting
- Audit logging
- Full-stack software engineering

### One-line interview pitch

> **"I built a defensive attack-surface management platform that converts authorized Nmap reconnaissance into persistent security findings, transparent risk scores, reports, and auditable workflows."**

---

# 🔗 Repository

**GitHub:**  
https://github.com/vardhan0666/ASR-Cyber-Lab

---

# 👨‍💻 Author

**Vardhan**

B.Tech Computer Science Engineering  
Cybersecurity • AI • Software Engineering

---

## ⚖️ Legal Notice

ASR-Cyber-Lab is a defensive cybersecurity engineering project.

**Only use this software against systems you own or have explicit authorization to assess.**

The author does not endorse unauthorized scanning, exploitation, credential attacks, malware deployment, persistence, evasion, or disruption of third-party systems.
