"""
Authorized target management endpoints.

All target-authorization changes are logged to the audit trail. Only users
with ANALYST or ADMIN roles may create targets or change their
authorization status; all authenticated users may view targets.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database import get_db
from app.models.target import Target
from app.models.user import User
from app.schemas.target import (
    TargetAuthorizeRequest,
    TargetCreate,
    TargetResponse,
    TargetUpdate,
)
from app.security.auth import get_current_active_user
from app.security.permissions import require_analyst_or_admin
from app.services.audit_service import log_action

router = APIRouter(prefix="/targets", tags=["targets"])


def _client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def _get_target_or_404(db: Session, target_id: uuid.UUID) -> Target:
    target = db.query(Target).filter(Target.id == target_id).first()
    if target is None:
        raise NotFoundError("Target not found")
    return target


@router.post("", response_model=TargetResponse, status_code=201)
def create_target(
    payload: TargetCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin),
) -> TargetResponse:
    """Register a new target. New targets are UNAUTHORIZED by default and
    must be explicitly authorized via POST /targets/{id}/authorize before
    any scan can be run against them."""
    target = Target(
        name=payload.name,
        address=payload.address,
        description=payload.description,
        asset_importance=payload.asset_importance,
        is_authorized=False,
        created_by_id=current_user.id,
    )
    db.add(target)
    db.commit()
    db.refresh(target)

    log_action(
        db,
        action="target.created",
        user_id=current_user.id,
        resource_type="target",
        resource_id=str(target.id),
        details={"address": target.address},
        ip_address=_client_ip(request),
    )

    return TargetResponse.model_validate(target)


@router.get("", response_model=List[TargetResponse])
def list_targets(
    search: Optional[str] = Query(None, description="Search by name or address"),
    is_authorized: Optional[bool] = Query(None),
    is_active: Optional[bool] = Query(None),
    sort_by: str = Query(
        "created_at", pattern="^(name|address|created_at|asset_importance)$"
    ),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[TargetResponse]:
    """List targets with optional search, filtering, sorting, and pagination."""
    query = db.query(Target)

    if search:
        like_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(Target.name.ilike(like_pattern), Target.address.ilike(like_pattern))
        )
    if is_authorized is not None:
        query = query.filter(Target.is_authorized == is_authorized)
    if is_active is not None:
        query = query.filter(Target.is_active == is_active)

    sort_column = getattr(Target, sort_by)
    query = query.order_by(sort_column.desc() if sort_order == "desc" else sort_column.asc())

    targets = query.offset(skip).limit(limit).all()
    return [TargetResponse.model_validate(t) for t in targets]


@router.get("/{target_id}", response_model=TargetResponse)
def get_target(
    target_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> TargetResponse:
    target = _get_target_or_404(db, target_id)
    return TargetResponse.model_validate(target)


@router.patch("/{target_id}", response_model=TargetResponse)
def update_target(
    target_id: uuid.UUID,
    payload: TargetUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin),
) -> TargetResponse:
    target = _get_target_or_404(db, target_id)

    update_data = payload.model_dump(exclude_unset=True)
    for field_name, value in update_data.items():
        setattr(target, field_name, value)

    db.add(target)
    db.commit()
    db.refresh(target)

    log_action(
        db,
        action="target.updated",
        user_id=current_user.id,
        resource_type="target",
        resource_id=str(target.id),
        details=update_data,
        ip_address=_client_ip(request),
    )

    return TargetResponse.model_validate(target)


@router.post("/{target_id}/authorize", response_model=TargetResponse)
def set_target_authorization(
    target_id: uuid.UUID,
    payload: TargetAuthorizeRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin),
) -> TargetResponse:
    """Explicitly grant or revoke scanning authorization for a target.

    This is intentionally a separate, auditable action from target
    creation/editing, ensuring authorization is always a deliberate,
    logged decision."""
    target = _get_target_or_404(db, target_id)

    target.is_authorized = payload.is_authorized
    if payload.is_authorized:
        target.authorized_by_id = current_user.id
        target.authorized_at = datetime.now(timezone.utc)
    else:
        target.authorized_by_id = None
        target.authorized_at = None

    db.add(target)
    db.commit()
    db.refresh(target)

    log_action(
        db,
        action="target.authorization_changed",
        user_id=current_user.id,
        resource_type="target",
        resource_id=str(target.id),
        details={"is_authorized": payload.is_authorized},
        ip_address=_client_ip(request),
    )

    return TargetResponse.model_validate(target)


@router.delete("/{target_id}", status_code=204)
def deactivate_target(
    target_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin),
) -> None:
    """Soft-delete a target by marking it inactive and revoking
    authorization. Historical scans/findings for this target are
    preserved."""
    target = _get_target_or_404(db, target_id)

    target.is_active = False
    target.is_authorized = False
    target.authorized_by_id = None
    target.authorized_at = None

    db.add(target)
    db.commit()

    log_action(
        db,
        action="target.deactivated",
        user_id=current_user.id,
        resource_type="target",
        resource_id=str(target.id),
        ip_address=_client_ip(request),
    )