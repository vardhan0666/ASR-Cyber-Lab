"""Scan job model and lifecycle status definitions."""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ScanProfile(str, enum.Enum):
    """Server-defined Nmap scan profiles."""

    QUICK = "quick"
    STANDARD = "standard"
    FULL_TCP = "full_tcp"
    VERSION_DETECTION = "version_detection"
    OS_DETECTION = "os_detection"


class ScanStatus(str, enum.Enum):
    """Lifecycle state of a scan job."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    target_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("targets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    initiated_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    profile: Mapped[ScanProfile] = mapped_column(
        SAEnum(
            ScanProfile,
            name="scan_profile",
            values_callable=lambda enum_cls: [
                member.value for member in enum_cls
            ],
        ),
        nullable=False,
    )

    status: Mapped[ScanStatus] = mapped_column(
        SAEnum(
            ScanStatus,
            name="scan_status",
            values_callable=lambda enum_cls: [
                member.value for member in enum_cls
            ],
        ),
        nullable=False,
        default=ScanStatus.PENDING,
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    raw_xml_output: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    target = relationship(
        "Target",
        back_populates="scans",
    )

    initiator = relationship(
        "User",
        back_populates="scans",
    )

    hosts = relationship(
        "Host",
        back_populates="scan",
        cascade="all, delete-orphan",
    )

    findings = relationship(
        "Finding",
        back_populates="scan",
        cascade="all, delete-orphan",
    )

    reports = relationship(
        "Report",
        back_populates="scan",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Scan id={self.id} "
            f"target_id={self.target_id} "
            f"status={self.status}>"
        )