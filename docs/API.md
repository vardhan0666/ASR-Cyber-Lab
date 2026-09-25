# ASR-Cyber-Lab API Reference

## Base URLs

Backend:

http://localhost:8000

API base:

http://localhost:8000/api

Swagger:

http://localhost:8000/api/docs

ReDoc:

http://localhost:8000/api/redoc

OpenAPI:

http://localhost:8000/api/openapi.json

---

# Authentication

The API uses JWT bearer authentication.

Protected requests use:

Authorization: Bearer <access_token>

There is no public self-registration endpoint.

The first administrator can be bootstrapped using:

INITIAL_ADMIN_EMAIL
INITIAL_ADMIN_PASSWORD
INITIAL_ADMIN_FULL_NAME

The bootstrap occurs only when the users table is empty.

---

# Health

## GET /api/health

Returns application health information.

Example:

{
  "status": "ok",
  "environment": "development"
}

---

# Authentication Endpoints

## POST /api/auth/login

Authenticates a user.

The API login endpoint accepts JSON credentials.

A successful login returns an access token.

---

## GET /api/auth/me

Returns the currently authenticated user.

Authentication required.

---

## POST /api/auth/register

Creates a new user.

This operation is administrator-controlled.

There is no public/open self-registration endpoint.

---

# Target Endpoints

Base:

/api/targets

## POST /api/targets

Creates a target.

---

## GET /api/targets

Lists registered targets.

---

## GET /api/targets/{target_id}

Returns a target by ID.

---

## PATCH /api/targets/{target_id}

Updates target information.

---

## POST /api/targets/{target_id}/authorize

Changes the target authorization state.

Authorization changes are recorded in the audit trail.

---

# Scan Endpoints

Base:

/api/scans

## POST /api/scans

Creates a scan against an authorized target.

The scan request contains the target and server-defined scan profile.

The scan is created immediately and executed asynchronously using a FastAPI
background task.

A target must be authorized before scanning.

---

## GET /api/scans

Lists scans.

Supported filters include:

target_id
status
skip
limit

---

## GET /api/scans/{scan_id}

Returns scan information.

Clients can poll this endpoint to observe:

pending
running
completed
failed

---

# Host Endpoints

Base:

/api/hosts

## GET /api/hosts

Lists discovered hosts.

Filtering can include:

scan_id
search
skip
limit

---

## GET /api/hosts/{host_id}

Returns a discovered host.

---

# Finding Endpoints

Base:

/api/findings

## GET /api/findings

Lists security findings.

Supported filtering includes:

scan_id
host_id
severity
category
status
search

Pagination:

skip
limit

Sorting:

risk_score
created_at
severity
title

---

## GET /api/findings/{finding_id}

Returns a finding.

---

## PATCH /api/findings/{finding_id}/status

Updates the workflow status of a finding.

Finding status is separate from severity.

---

# Report Endpoints

Base:

/api/reports

## POST /api/reports

Generates a report for a scan.

Supported report formats include:

JSON
PDF

---

## GET /api/reports

Lists generated reports.

Optional filter:

scan_id

---

## GET /api/reports/{report_id}

Returns report metadata.

---

## GET /api/reports/{report_id}/download

Downloads a generated report.

PDF reports use:

application/pdf

JSON reports use:

application/json

---

# AI Endpoints

AI assistance is optional.

## GET /api/ai/status

Reports whether AI assistance is enabled and configured.

---

## POST /api/ai/findings/{finding_id}/explain

Generates an optional evidence-bound explanation for a finding.

If AI is disabled or unavailable, the API reports that condition instead of
fabricating an explanation.

Deterministic findings and risk scores remain authoritative.

---

# Audit Logs

Base:

/api/audit-logs

## GET /api/audit-logs

Lists audit log entries.

This endpoint is administrator-only.

Supported filters include:

user_id
action
resource_type
skip
limit

---

# API Contract

The generated OpenAPI schema is the authoritative machine-readable API
contract.

Use:

http://localhost:8000/api/docs

to inspect the currently running implementation.