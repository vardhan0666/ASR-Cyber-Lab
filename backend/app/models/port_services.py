"""Discovered port/service model — one row per port reported by Nmap."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class PortService(Base):
    __tablename__ = "port_services"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    host_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hosts.id"), nullable=False
    )

    port_number: Mapped[int] = mapped_column(Integer, nullable=False)
    protocol: Mapped[str] = mapped_column(String(10), nullable=False)  # tcp/udp
    state: Mapped[str] = mapped_column(String(20), nullable=False)  # open/closed/filtered

    service_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    product: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    version: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    extra_info: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    host = relationship("Host", back_populates="port_services")
    findings = relationship("Finding", back_populates="port_service")

    def __repr__(self) -> str:
        return (
            f"<PortService id={self.id} port={self.port_number}/{self.protocol} "
            f"state={self.state}>"
        )