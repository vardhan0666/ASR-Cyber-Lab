"""Security finding model.

A Finding is the atomic unit of security evidence surfaced by the platform:
a configuration issue, a known vulnerability match, or an exposure. Every
finding carries structured JSON evidence and a JSON risk explanation array
so results are always traceable back to actual scan data — never inferred
or fabricated without a basis.
"""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class SeverityLevel(str, enum.Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FindingCategory(str, enum.Enum):
    CONFIGURATION = "configuration"
    VULNERABILITY = "vulnerability"
    EXPOSURE = "exposure"


class FindingStatus(str, enum.Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class Finding(Base):
    __tablename__ = "findings"

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

    host_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("hosts.id"),
        nullable=True,
    )

    port_service_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("port_services.id"),
        nullable=True,
    )

    category: Mapped[FindingCategory] = mapped_column(
        SAEnum(
            FindingCategory,
            name="finding_category",
            values_callable=lambda enum_cls: [
                member.value for member in enum_cls
            ],
        ),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # JSON-serialized dict of raw evidence backing this finding
    # (e.g. {"port": 23, "service": "telnet", "banner": "..."})
    evidence: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="{}",
    )

    severity: Mapped[SeverityLevel] = mapped_column(
        SAEnum(
            SeverityLevel,
            name="severity_level",
            values_callable=lambda enum_cls: [
                member.value for member in enum_cls
            ],
        ),
        nullable=False,
    )

    risk_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    # JSON-serialized list of human-readable explanation strings produced
    # by the risk engine (app/services/risk_engine.py).
    risk_explanation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="[]",
    )

    status: Mapped[FindingStatus] = mapped_column(
        SAEnum(
            FindingStatus,
            name="finding_status",
            values_callable=lambda enum_cls: [
                member.value for member in enum_cls
            ],
        ),
        nullable=False,
        default=FindingStatus.OPEN,
    )

    remediation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
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

    scan = relationship(
        "Scan",
        back_populates="findings",
    )

    host = relationship(
        "Host",
        back_populates="findings",
    )

    port_service = relationship(
        "PortService",
        back_populates="findings",
    )

    vulnerabilities = relationship(
        "Vulnerability",
        back_populates="finding",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Finding id={self.id} "
            f"title={self.title!r} "
            f"severity={self.severity}>"
        )