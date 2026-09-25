"""Discovered host model — one row per live host found during a scan."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Host(Base):
    __tablename__ = "hosts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    scan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scans.id"), nullable=False
    )

    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    hostname: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="up")

    # OS detection results — only populated when Nmap's -O flag runs and
    # produces a match. os_accuracy is Nmap's own confidence percentage.
    os_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    os_accuracy: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mac_address: Mapped[Optional[str]] = mapped_column(String(17), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    scan = relationship("Scan", back_populates="hosts")
    port_services = relationship(
        "PortService", back_populates="host", cascade="all, delete-orphan"
    )
    findings = relationship("Finding", back_populates="host")

    def __repr__(self) -> str:
        return f"<Host id={self.id} ip={self.ip_address} status={self.status}>"