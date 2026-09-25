"""Generated report metadata model (JSON/PDF exports of scan results)."""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class ReportFormat(str, enum.Enum):
    JSON = "json"
    PDF = "pdf"


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    scan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scans.id"),
        nullable=False,
    )

    generated_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    format: Mapped[ReportFormat] = mapped_column(
        SAEnum(
            ReportFormat,
            name="report_format",
            values_callable=lambda enum_cls: [
                member.value for member in enum_cls
            ],
        ),
        nullable=False,
    )

    file_path: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    scan = relationship(
        "Scan",
        back_populates="reports",
    )

    generator = relationship(
        "User",
        back_populates="reports",
    )

    def __repr__(self) -> str:
        return (
            f"<Report id={self.id} "
            f"scan_id={self.scan_id} "
            f"format={self.format}>"
        )