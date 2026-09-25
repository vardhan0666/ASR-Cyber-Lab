# ASR-Cyber-Lab Security Model

## Purpose

ASR-Cyber-Lab is a defensive security reconnaissance platform.

---

# Authentication

The application uses JWT access tokens.

Passwords are hashed using bcrypt through Passlib.

Plaintext passwords are not stored.

---

# Authorization

Protected operations use role-based permission dependencies.

Administrator functionality includes:

- administrator-managed user registration
- audit-log access

Security operations require the appropriate authenticated role.

---

# Input Validation

FastAPI and Pydantic validate request data.

Pagination and query parameters also have validation limits.

---

# Nmap Execution

Nmap is invoked using:

subprocess.run(list_of_args, shell=False)

The scan workflow uses fixed server-defined scan profiles.

The API does not provide an arbitrary shell command interface.

---

# Docker Security

The backend image:

- installs Nmap
- configures Nmap capabilities
- creates a non-root application user

The Docker Compose backend service also receives the capabilities required by
the supported Nmap workflow.

---

# Secrets

Sensitive configuration is supplied through environment variables.

Sensitive values include:

- SECRET_KEY
- POSTGRES_PASSWORD
- INITIAL_ADMIN_PASSWORD
- AI_API_KEY

The `.env` file should not be committed.

---

# CORS

CORS is configured through:

CORS_ORIGINS

Development value:

http://localhost:5173

---

# Audit Logging

Security-relevant actions are recorded through the audit logging service.

Audit logs are administrator-controlled because they may contain sensitive
operational information.

---

# AI Security Boundary

AI is optional.

The deterministic workflow remains authoritative.

AI cannot replace:

- findings
- evidence
- risk scores
- vulnerability information
- remediation status

If AI is disabled or unavailable, the application explicitly reports that
state.

---

# Threat Model

Important threats include:

1. Unauthorized scanning
2. Compromised credentials
3. Secret leakage
4. Malicious API input
5. Unsafe subprocess execution
6. Unauthorized report access
7. Unauthorized audit-log access
8. Incorrect interpretation of findings

Controls include:

- authentication
- authorization
- validation
- controlled subprocess execution
- environment-based secrets
- audit logging
- target authorization

---

# Defensive Scope

The project does not implement:

- credential theft
- malware
- persistence
- evasion
- arbitrary shell execution
- destructive exploitation

---

# Production Security

The development deployment should not automatically be considered a
production security baseline.

Production should separately review:

- TLS
- reverse proxy
- secrets management
- database access
- network segmentation
- backups
- monitoring
- container hardening
- access control