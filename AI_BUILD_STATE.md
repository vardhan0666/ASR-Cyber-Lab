# ASR-Cyber-Lab — Build State

_Last updated: Batch 1_

## Total Project Files (planned)
147

## Current Batch
Batch 1 of ~13 — Root config & backend foundation

## Files Completed (21)
- AI_BUILD_STATE.md
- README.md
- docker-compose.yml
- .env.example
- .gitignore
- backend/requirements.txt
- backend/requirements-dev.txt
- backend/Dockerfile
- backend/.dockerignore
- backend/alembic.ini
- backend/pytest.ini
- backend/app/__init__.py
- backend/app/config.py
- backend/app/database.py
- backend/app/core/__init__.py
- backend/app/core/exceptions.py
- backend/app/core/logging_config.py
- backend/app/core/validators.py
- backend/app/security/__init__.py
- backend/app/security/password.py
- backend/app/security/jwt_handler.py

## Files Modified
(none — first batch)

## Database Changes
None yet. Models start in Batch 2, migration in Batch 3.

## API Endpoints Implemented
None yet (routes start Batch 6).

## Dependencies Declared
**backend/requirements.txt:** fastapi, uvicorn[standard], sqlalchemy, alembic,
psycopg2-binary, pydantic, pydantic-settings, python-jose[cryptography],
passlib[bcrypt], bcrypt==4.0.1 (pinned for passlib compatibility),
python-multipart, reportlab, email-validator, python-dotenv

**backend/requirements-dev.txt:** pytest, pytest-asyncio, httpx, pytest-cov, faker

## Environment Variables Defined (.env.example)
ENVIRONMENT, LOG_LEVEL, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB,
POSTGRES_PORT, DATABASE_URL, SECRET_KEY, ALGORITHM,
ACCESS_TOKEN_EXPIRE_MINUTES, BACKEND_PORT, CORS_ORIGINS, NMAP_PATH,
NMAP_TIMEOUT_SECONDS, AI_ENABLED, AI_PROVIDER, AI_API_KEY, FRONTEND_PORT,
VITE_API_BASE_URL

## Tests
None written yet (backend/tests/ starts Batch 7-8).

## Test Results
N/A

## Known Bugs
None identified in current files.

## Design Notes Locked In
- Nmap is invoked via `subprocess.run(list_of_args, shell=False)` — never shell strings.
- Scan "profiles" (fixed, server-defined argument sets) will be enforced in
  `nmap_service.py` (Batch 4) — user input never becomes raw CLI flags.
- Backend Docker image installs nmap and applies
  `setcap cap_net_raw,cap_net_admin+eip` to the nmap binary so scans work
  without running the container as root (paired with `cap_add` in
  docker-compose.yml).
- bcrypt pinned to 4.0.1 due to a known incompatibility between
  passlib 1.7.4's version probe and bcrypt >= 4.1.
- SECRET_KEY is validated at startup (must be set, >= 16 chars) — app will
  fail fast rather than run insecurely.

## Remaining Files
126

## Exact Next Batch
**Batch 2** — `backend/app/dependencies.py`, `backend/app/security/auth.py`,
`backend/app/security/permissions.py`, and all 10 files in `backend/app/models/`.