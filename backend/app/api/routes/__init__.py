"""
Aggregates and exposes all API routers for registration in app.main.
"""

from fastapi import APIRouter

from app.api.routes.ai import router as ai_router
from app.api.routes.audit_logs import router as audit_logs_router
from app.api.routes.auth import router as auth_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.findings import router as findings_router
from app.api.routes.hosts import router as hosts_router
from app.api.routes.reports import router as reports_router
from app.api.routes.scans import router as scans_router
from app.api.routes.targets import router as targets_router
from app.api.routes.vulnerabilities import router as vulnerabilities_router


api_router = APIRouter()

# Authentication
api_router.include_router(auth_router)

# Core asset and scanning APIs
api_router.include_router(targets_router)
api_router.include_router(scans_router)
api_router.include_router(hosts_router)

# Security findings and vulnerability enrichment
api_router.include_router(findings_router)
api_router.include_router(vulnerabilities_router)

# Dashboard and reporting
api_router.include_router(dashboard_router)
api_router.include_router(reports_router)

# Administrative audit APIs
api_router.include_router(audit_logs_router)

# Optional AI assistance
api_router.include_router(ai_router)