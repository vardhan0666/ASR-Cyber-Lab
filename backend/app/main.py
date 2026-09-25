"""
FastAPI application factory: middleware, exception handlers, startup
bootstrap, and router registration.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import api_router
from app.config import get_settings
from app.core.exceptions import AppException
from app.core.logging_config import setup_logging
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.security.password import hash_password

settings = get_settings()
setup_logging()
logger = logging.getLogger(__name__)


def _bootstrap_initial_admin() -> None:
    """Create the first administrator account from INITIAL_ADMIN_EMAIL /
    INITIAL_ADMIN_PASSWORD environment variables, but ONLY if the users
    table is currently empty. This is the sole account-creation path that
    does not require an existing administrator; it is disabled simply by
    leaving those environment variables unset."""
    if not settings.INITIAL_ADMIN_EMAIL or not settings.INITIAL_ADMIN_PASSWORD:
        logger.info(
            "INITIAL_ADMIN_EMAIL/INITIAL_ADMIN_PASSWORD not set; skipping "
            "initial admin bootstrap."
        )
        return

    db = SessionLocal()
    try:
        existing_user = db.query(User).first()
        if existing_user is not None:
            return

        admin = User(
            email=settings.INITIAL_ADMIN_EMAIL.lower().strip(),
            hashed_password=hash_password(settings.INITIAL_ADMIN_PASSWORD),
            full_name=settings.INITIAL_ADMIN_FULL_NAME,
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        logger.info("Bootstrapped initial administrator account: %s", admin.email)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    _bootstrap_initial_admin()
    yield


app = FastAPI(
    title="ASR-Cyber-Lab API",
    description=(
        "Automated Security Reconnaissance & Attack-Surface Reduction "
        "Platform API. For use only against systems you own or are "
        "explicitly authorized to test. See docs/AUTHORIZED_USE.md."
    ),
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Translate all application-raised exceptions into a uniform JSON
    error shape."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.get("/api/health", tags=["health"])
def health_check() -> dict:
    """Basic liveness endpoint. Does not touch the database or Nmap."""
    return {"status": "ok", "environment": settings.ENVIRONMENT}


app.include_router(api_router, prefix="/api")