# ASR-Cyber-Lab Testing

## Testing Stack

Backend development/testing dependencies include:

- pytest
- pytest-asyncio
- httpx
- pytest-cov
- Faker

Frontend testing uses:

- Vitest
- Testing Library
- jsdom

---

# 1. Start the Application

From the project root:

docker compose up --build

---

# 2. Apply Migrations

docker compose exec backend alembic upgrade head

---

# 3. Backend Tests

Run:

docker compose exec backend pytest

The backend pytest configuration uses:

testpaths = tests

and:

test_*.py

for test files.

---

# 4. Backend Coverage

Run:

docker compose exec backend pytest --cov=app

---

# 5. Frontend Tests

Move into the frontend:

cd "C:\Users\vardhan\Music\ASR-Cyber-Lab\frontend"

Run:

npm test

The package script is:

"test": "vitest run"

---

# 6. Frontend Build

Run:

npm run build

The build script runs TypeScript compilation followed by Vite build.

---

# 7. Frontend Lint

Run:

npm run lint

---

# 8. Authentication Testing

Authentication tests should cover:

- login
- JWT access
- protected endpoints
- current-user access
- permission checks

---

# 9. Target Testing

Target-management tests should cover:

- creation
- retrieval
- update
- authorization state

---

# 10. Scan Testing

Scan tests should cover:

- scan creation
- target authorization
- scan status
- successful execution
- failure handling

Automated tests should avoid scanning arbitrary external systems.

---

# 11. Nmap Test Data

Representative Nmap XML can be used to test parsing and persistence.

Expected normalized data includes:

- hosts
- ports
- services
- findings

---

# 12. Failure Testing

Nmap execution failure should result in:

scan status = failed

The application must not report a failed scan as completed successfully.

---

# 13. Security Finding Testing

The test suite includes security-analysis behavior around exposed services,
including the implemented Telnet-related finding logic.

---

# 14. Test Database

The backend test configuration uses PostgreSQL-specific functionality,
including PostgreSQL UUID and ENUM types.

Tests therefore require a reachable PostgreSQL test database.

The test configuration supports:

TEST_DATABASE_URL

The default test database configuration points to:

asr_cyber_lab_test

---

# 15. Test Environment

The test environment should not use the production database.

Initial admin bootstrap variables should remain unset for isolated tests.

---

# 16. Recommended Sequence

Start:

docker compose up --build

Migrate:

docker compose exec backend alembic upgrade head

Backend:

docker compose exec backend pytest

Frontend:

cd "C:\Users\vardhan\Music\ASR-Cyber-Lab\frontend"

npm test

Build:

npm run build

Lint:

npm run lint

---

# 17. Failure Investigation

When a test fails:

1. Read the failing test.
2. Read the assertion error.
3. Check backend logs.
4. Check database availability.
5. Check migration state.
6. Determine whether the failure is environmental or implementation-related.
7. Fix the underlying issue.

Do not remove security tests simply to make the test suite pass.