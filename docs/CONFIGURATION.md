# ASR-Cyber-Lab Configuration

Configuration is supplied through:

.env

Create it from:

.env.example

PowerShell:

Copy-Item .env.example .env

Never commit the real `.env` file.

---

# General

ENVIRONMENT=development

LOG_LEVEL=INFO

---

# PostgreSQL

POSTGRES_USER=asr_user

POSTGRES_PASSWORD=change_me_strong_password

POSTGRES_DB=asr_cyber_lab

POSTGRES_PORT=5432

---

# Database URL

DATABASE_URL=postgresql+psycopg2://asr_user:change_me_strong_password@localhost:5432/asr_cyber_lab

When running through Docker Compose, the backend database connection is
overridden to use the PostgreSQL service named:

db

---

# JWT

SECRET_KEY=change_me_to_a_random_secret_at_least_32_characters_long

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=60

The application validates SECRET_KEY at startup.

The source configuration requires a secret of at least 16 characters.

Use a strong random value for actual deployments.

---

# Backend

BACKEND_PORT=8000

Default backend:

http://localhost:8000

---

# CORS

CORS_ORIGINS=http://localhost:5173

---

# Nmap

NMAP_PATH=nmap

NMAP_TIMEOUT_SECONDS=600

NMAP_PATH identifies the Nmap executable.

NMAP_TIMEOUT_SECONDS controls the scan timeout.

---

# Optional AI

AI_ENABLED=false

AI_PROVIDER=none

AI_API_KEY=

AI is disabled by default.

The core security workflow does not require AI.

---

# Initial Administrator

INITIAL_ADMIN_EMAIL=

INITIAL_ADMIN_PASSWORD=

INITIAL_ADMIN_FULL_NAME=Administrator

The initial administrator is created when:

1. email is configured
2. password is configured
3. the users table is empty

After the initial administrator exists, subsequent accounts are created by
an administrator.

---

# Frontend

FRONTEND_PORT=5173

VITE_API_BASE_URL=http://localhost:8000

---

# Security

Do not commit:

.env

Do not publish:

- SECRET_KEY
- POSTGRES_PASSWORD
- INITIAL_ADMIN_PASSWORD
- AI_API_KEY

Use separate secrets for production environments.