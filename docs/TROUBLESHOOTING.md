# ASR-Cyber-Lab Troubleshooting

## 1. Docker Is Not Running

Check:

docker --version

docker compose version

Start Docker Desktop if Docker is unavailable.

---

# 2. Check Containers

From the project root:

docker compose ps

Expected services:

db
backend
frontend

---

# 3. Backend Fails

View logs:

docker compose logs backend

Common causes:

- invalid .env
- invalid SECRET_KEY
- database unavailable
- dependency/build error
- application startup error

Rebuild:

docker compose up --build

---

# 4. Database Fails

Check:

docker compose logs db

Then:

docker compose ps

---

# 5. Migration Fails

Run:

docker compose exec backend alembic upgrade head

If it fails, inspect:

docker compose logs backend

docker compose logs db

Do not manually create application tables while using Alembic.

---

# 6. Port Already in Use

Default ports:

5432  PostgreSQL
8000  Backend
5173  Frontend

Check `.env`.

You can change host-side ports and restart:

docker compose down

docker compose up --build

---

# 7. Backend Health Does Not Open

Test:

http://localhost:8000/api/health

Then run:

docker compose ps

docker compose logs backend

---

# 8. Swagger Does Not Open

Open:

http://localhost:8000/api/docs

If it does not load, first check:

http://localhost:8000/api/health

Then inspect backend logs.

---

# 9. Frontend Does Not Open

Open:

http://localhost:5173

Check:

docker compose ps

docker compose logs frontend

---

# 10. Frontend Cannot Reach Backend

Check `.env`:

VITE_API_BASE_URL=http://localhost:8000

Then verify:

http://localhost:8000/api/health

If the backend works but frontend requests fail, inspect:

- VITE_API_BASE_URL
- CORS configuration
- frontend logs
- backend logs

After configuration changes:

docker compose up --build

---

# 11. Authentication Problems

Check:

INITIAL_ADMIN_EMAIL
INITIAL_ADMIN_PASSWORD
INITIAL_ADMIN_FULL_NAME

The initial administrator is created only when the users table is empty.

If users already exist, changing these environment variables will not create
another initial administrator.

---

# 12. Nmap Problems

Check Nmap on Windows:

nmap --version

For the Docker deployment, Nmap is installed inside the backend image.

Check:

docker compose logs backend

---

# 13. Scan Fails

Inspect:

docker compose logs backend

Check scan status:

GET /api/scans/{scan_id}

Possible causes include:

- target unreachable
- target not authorized
- Nmap failure
- timeout
- invalid scan state
- database problem

Use only authorized targets.

---

# 14. Scan Takes Too Long

The configured timeout is:

NMAP_TIMEOUT_SECONDS

Default:

600

Scan duration depends on the target and selected profile.

---

# 15. Report Download Fails

A report can have database metadata while its generated file is no longer
available on disk.

Check:

docker compose logs backend

The report download endpoint reports an error when the file is unavailable.

---

# 16. Frontend Tests Fail

Move to:

cd "C:\Users\vardhan\Music\ASR-Cyber-Lab\frontend"

Run:

npm test

The package script uses:

vitest run

---

# 17. Complete Restart

docker compose down

docker compose up

Then:

docker compose exec backend alembic upgrade head

---

# 18. Rebuild

Use:

docker compose down

docker compose up --build

Useful after changes to:

- Dockerfile
- Python dependencies
- frontend dependencies
- build configuration

---

# 19. Protect Database Data

Do not use:

docker compose down -v

unless you intentionally want to remove the PostgreSQL Docker volume.

Normal:

docker compose down

does not remove the named PostgreSQL volume.

---

# 20. Useful Commands

Container status:

docker compose ps

Backend logs:

docker compose logs backend

Frontend logs:

docker compose logs frontend

Database logs:

docker compose logs db

All logs:

docker compose logs

Live backend logs:

docker compose logs -f backend