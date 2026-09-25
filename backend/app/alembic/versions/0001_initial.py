"""initial schema

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000

Creates the complete initial schema: users, targets, scans, hosts,
port_services, findings, vulnerabilities, audit_logs, and reports, along
with all associated Postgres enum types.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("admin", "analyst", "viewer", name="user_role"),
            nullable=False,
            server_default="viewer",
        ),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.true()
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # --- targets ---
    op.create_table(
        "targets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "asset_importance",
            sa.Enum("low", "medium", "high", "critical", name="asset_importance"),
            nullable=False,
            server_default="medium",
        ),
        sa.Column(
            "is_authorized", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.true()
        ),
        sa.Column(
            "authorized_by_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column("authorized_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_by_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # --- scans ---
    op.create_table(
        "scans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "target_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("targets.id"),
            nullable=False,
        ),
        sa.Column(
            "initiated_by_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column(
            "profile",
            sa.Enum(
                "quick",
                "standard",
                "full_tcp",
                "version_detection",
                "os_detection",
                name="scan_profile",
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "running",
                "completed",
                "failed",
                "cancelled",
                name="scan_status",
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_xml_output", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # --- hosts ---
    op.create_table(
        "hosts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "scan_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("scans.id"),
            nullable=False,
        ),
        sa.Column("ip_address", sa.String(length=45), nullable=False),
        sa.Column("hostname", sa.String(length=255), nullable=True),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="up"
        ),
        sa.Column("os_name", sa.String(length=255), nullable=True),
        sa.Column("os_accuracy", sa.Integer(), nullable=True),
        sa.Column("mac_address", sa.String(length=17), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # --- port_services ---
    op.create_table(
        "port_services",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "host_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("hosts.id"),
            nullable=False,
        ),
        sa.Column("port_number", sa.Integer(), nullable=False),
        sa.Column("protocol", sa.String(length=10), nullable=False),
        sa.Column("state", sa.String(length=20), nullable=False),
        sa.Column("service_name", sa.String(length=255), nullable=True),
        sa.Column("product", sa.String(length=255), nullable=True),
        sa.Column("version", sa.String(length=255), nullable=True),
        sa.Column("extra_info", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # --- findings ---
    op.create_table(
        "findings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "scan_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("scans.id"),
            nullable=False,
        ),
        sa.Column(
            "host_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("hosts.id"),
            nullable=True,
        ),
        sa.Column(
            "port_service_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("port_services.id"),
            nullable=True,
        ),
        sa.Column(
            "category",
            sa.Enum(
                "configuration", "vulnerability", "exposure", name="finding_category"
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "evidence", sa.Text(), nullable=False, server_default="{}"
        ),
        sa.Column(
            "severity",
            sa.Enum(
                "info", "low", "medium", "high", "critical", name="severity_level"
            ),
            nullable=False,
        ),
        sa.Column(
            "risk_score", sa.Float(), nullable=False, server_default="0.0"
        ),
        sa.Column(
            "risk_explanation", sa.Text(), nullable=False, server_default="[]"
        ),
        sa.Column(
            "status",
            sa.Enum(
                "open",
                "acknowledged",
                "resolved",
                "false_positive",
                name="finding_status",
            ),
            nullable=False,
            server_default="open",
        ),
        sa.Column("remediation", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # --- vulnerabilities ---
    op.create_table(
        "vulnerabilities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "finding_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("findings.id"),
            nullable=False,
        ),
        sa.Column("cve_id", sa.String(length=50), nullable=True),
        sa.Column("source", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("cvss_score", sa.Float(), nullable=True),
        sa.Column(
            "severity",
            sa.Enum(
                "info",
                "low",
                "medium",
                "high",
                "critical",
                name="vuln_severity_level",
            ),
            nullable=True,
        ),
        sa.Column("reference_url", sa.String(length=1000), nullable=True),
        sa.Column(
            "data_available",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_vulnerabilities_cve_id", "vulnerabilities", ["cve_id"], unique=False
    )

    # --- audit_logs ---
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column("action", sa.String(length=255), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=True),
        sa.Column("resource_id", sa.String(length=255), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # --- reports ---
    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "scan_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("scans.id"),
            nullable=False,
        ),
        sa.Column(
            "generated_by_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column(
            "format", sa.Enum("json", "pdf", name="report_format"), nullable=False
        ),
        sa.Column("file_path", sa.String(length=1000), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("reports")
    op.drop_table("audit_logs")
    op.drop_index("ix_vulnerabilities_cve_id", table_name="vulnerabilities")
    op.drop_table("vulnerabilities")
    op.drop_table("findings")
    op.drop_table("port_services")
    op.drop_table("hosts")
    op.drop_table("scans")
    op.drop_table("targets")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    bind = op.get_bind()
    sa.Enum(name="report_format").drop(bind, checkfirst=True)
    sa.Enum(name="finding_status").drop(bind, checkfirst=True)
    sa.Enum(name="vuln_severity_level").drop(bind, checkfirst=True)
    sa.Enum(name="severity_level").drop(bind, checkfirst=True)
    sa.Enum(name="finding_category").drop(bind, checkfirst=True)
    sa.Enum(name="scan_status").drop(bind, checkfirst=True)
    sa.Enum(name="scan_profile").drop(bind, checkfirst=True)
    sa.Enum(name="asset_importance").drop(bind, checkfirst=True)
    sa.Enum(name="user_role").drop(bind, checkfirst=True)