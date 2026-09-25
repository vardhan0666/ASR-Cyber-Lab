"""Audit log query endpoints (administrator-only)."""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogResponse
from app.security.permissions import require_admin

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


@router.get("", response_model=List[AuditLogResponse])
def list_audit_logs(
    user_id: Optional[uuid.UUID] = Query(None),
    action: Optional[str] = Query(None, description="Exact or partial action match"),
    resource_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> List[AuditLogResponse]:
    """List audit log entries, newest first. Restricted to administrators
    since audit logs may reveal sensitive operational details."""
    query = db.query(AuditLog)

    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action.strip()}%"))
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)

    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    return [AuditLogResponse.model_validate(log) for log in logs]