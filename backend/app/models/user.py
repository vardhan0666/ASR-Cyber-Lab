"""User account model with role-based access control."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class UserRole(str, enum.Enum):
    """Roles gate what a user may create/modify in the platform.

    ADMIN    - full control, including user administration.
    ANALYST  - can manage targets, run scans, review findings.
    VIEWER   - read-only access to dashboards/reports/findings.
    """

    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    full_name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    role: Mapped[UserRole] = mapped_column(
        SAEnum(
            UserRole,
            name="user_role",
            values_callable=lambda enum_cls: [
                member.value for member in enum_cls
            ],
        ),
        nullable=False,
        default=UserRole.VIEWER,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
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

    created_targets = relationship(
        "Target",
        foreign_keys="Target.created_by_id",
        back_populates="creator",
    )

    authorized_targets = relationship(
        "Target",
        foreign_keys="Target.authorized_by_id",
        back_populates="authorizer",
    )

    scans = relationship(
        "Scan",
        back_populates="initiator",
    )

    audit_logs = relationship(
        "AuditLog",
        back_populates="user",
    )

    reports = relationship(
        "Report",
        back_populates="generator",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"