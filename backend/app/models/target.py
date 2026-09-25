"""Authorized scan target model.

A Target represents a system the user claims ownership/authorization for.
No scan may ever be executed against a Target unless is_authorized is True.
This flag is enforced again in the service layer (scan_orchestrator.py) —
this model is not the only line of defense.
"""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class AssetImportance(str, enum.Enum):
    """Business importance of the asset — a direct input to the risk engine."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Target(Base):
    __tablename__ = "targets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    address: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )

    asset_importance: Mapped[AssetImportance] = mapped_column(
        SAEnum(
            AssetImportance,
            name="asset_importance",
            values_callable=lambda enum_cls: [
                member.value for member in enum_cls
            ],
        ),
        nullable=False,
        default=AssetImportance.MEDIUM,
    )

    is_authorized: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    authorized_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    authorized_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    creator = relationship(
        "User",
        foreign_keys=[created_by_id],
        back_populates="created_targets",
    )

    authorizer = relationship(
        "User",
        foreign_keys=[authorized_by_id],
        back_populates="authorized_targets",
    )

    scans = relationship(
        "Scan",
        back_populates="target",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Target id={self.id} "
            f"address={self.address} "
            f"authorized={self.is_authorized}>"
        )