# ASR-Cyber-Lab Installation and Execution

## 1. Project Directory

Expected project location:

C:\Users\vardhan\Music\ASR-Cyber-Lab

Open PowerShell:

cd "C:\Users\vardhan\Music\ASR-Cyber-Lab"

---

# 2. Verify Tools

Run:

docker --version

docker compose version

python --version

node --version

npm --version

nmap --version

The project uses Docker, Python, Node.js/npm and Nmap.

---

# 3. Create Environment File

Run:

Copy-Item .env.example .env

Open:

notepad .env

Configure the required values.

Do not commit `.env`.

---

# 4. Start Docker Compose

From the project root:

docker compose up --build

This starts:

- PostgreSQL
- FastAPI backend
- React/Vite frontend

Keep this terminal running.

---

# 5. Check Containers

Open another PowerShell window:

cd "C:\Users\vardhan\Music\ASR-Cyber-Lab"

docker compose ps

Expected services:

db
backend
frontend

---

# 6. Apply Database Migrations

Run:

docker compose exec backend alembic upgrade head

---

# 7. Backend Health

Open:

http://localhost:8000/api/health

Expected response:

{
  "status": "ok",
  "environment": "development"
}

---

# 8. Swagger

Open:

http://localhost:8000/api/docs

---

# 9. Frontend

Open:

http://localhost:5173

---

# 10. Initial Administrator

Configure in `.env`:

INITIAL_ADMIN_EMAIL=admin@example.com

INITIAL_ADMIN_PASSWORD=ChangeThisStrongPassword123!

INITIAL_ADMIN_FULL_NAME=Administrator

The initial admin is bootstrapped only if the users table is empty.

---

# 11. Run Backend Tests

From the project root:

docker compose exec backend pytest

---

# 12. Run Frontend Tests

Open PowerShell:

cd "C:\Users\vardhan\Music\ASR-Cyber-Lab\frontend"

npm test

The frontend package defines:

"test": "vitest run"

---

# 13. Frontend Build

From:

C:\Users\vardhan\Music\ASR-Cyber-Lab\frontend

Run:

npm run build

---

# 14. Logs

Backend:

docker compose logs backend

Frontend:

docker compose logs frontend

Database:

docker compose logs db

Live backend logs:

docker compose logs -f backend

---

# 15. Stop

From the project root:

docker compose down

---

# 16. Restart

docker compose up

---

# 17. Rebuild

docker compose up --build

---

# QUICK START

PowerShell 1:

cd "C:\Users\vardhan\Music\ASR-Cyber-Lab"

Copy-Item .env.example .env

docker compose up --build

PowerShell 2:

cd "C:\Users\vardhan\Music\ASR-Cyber-Lab"

docker compose exec backend alembic upgrade head

docker compose ps

Then open:

http://localhost:8000/api/health

http://localhost:8000/api/docs

http://localhost:5173