"""
Audit logging service.

Writes structured, queryable audit records to the audit_logs table for
every security-relevant action (authentication, target authorization,
scan execution, report generation, etc.), and mirrors the event to the
application's dedicated "audit" logger for operational visibility.
"""

import json
import uuid
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.core.logging_config import get_audit_logger
from app.models.audit_log import AuditLog

audit_logger = get_audit_logger()


def log_action(
    db: Session,
    action: str,
    user_id: Optional[uuid.UUID] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
) -> AuditLog:
    """Persist an audit log entry and emit it to the audit logger.

    Commits its own transaction so audit records remain durable even if a
    broader calling transaction is later rolled back.
    """
    entry = AuditLog(
        id=uuid.uuid4(),
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=json.dumps(details) if details is not None else None,
        ip_address=ip_address,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    audit_logger.info(
        "action=%s user_id=%s resource_type=%s resource_id=%s ip=%s",
        action,
        user_id,
        resource_type,
        resource_id,
        ip_address,
    )

    return entry