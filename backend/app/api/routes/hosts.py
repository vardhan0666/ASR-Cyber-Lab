"""Discovered host / asset inventory endpoints."""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database import get_db
from app.models.host import Host
from app.models.user import User
from app.schemas.host import HostResponse
from app.security.auth import get_current_active_user

router = APIRouter(prefix="/hosts", tags=["hosts"])


@router.get("", response_model=List[HostResponse])
def list_hosts(
    scan_id: Optional[uuid.UUID] = Query(None),
    search: Optional[str] = Query(None, description="Search by IP address or hostname"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[HostResponse]:
    """List discovered hosts across all scans, optionally filtered by scan
    or searched by IP/hostname. This forms the platform's asset inventory
    view."""
    query = db.query(Host)
    if scan_id is not None:
        query = query.filter(Host.scan_id == scan_id)
    if search:
        like_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(Host.ip_address.ilike(like_pattern), Host.hostname.ilike(like_pattern))
        )

    hosts = query.order_by(Host.created_at.desc()).offset(skip).limit(limit).all()
    return [HostResponse.model_validate(h) for h in hosts]


@router.get("/{host_id}", response_model=HostResponse)
def get_host(
    host_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> HostResponse:
    host = db.query(Host).filter(Host.id == host_id).first()
    if host is None:
        raise NotFoundError("Host not found")
    return HostResponse.model_validate(host)