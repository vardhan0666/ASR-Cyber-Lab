"""Tests for the audit logging service and admin-only audit log endpoint."""

import uuid

from app.models.audit_log import AuditLog
from app.services.audit_service import log_action


def test_log_action_persists_entry(db_session, admin_user):
    entry = log_action(
        db_session,
        action="test.custom_action",
        user_id=admin_user.id,
        resource_type="target",
        resource_id="some-resource-id",
        details={"key": "value"},
        ip_address="127.0.0.1",
    )

    assert entry.id is not None
    fetched = db_session.query(AuditLog).filter(AuditLog.id == entry.id).first()
    assert fetched is not None
    assert fetched.action == "test.custom_action"
    assert fetched.user_id == admin_user.id
    assert fetched.resource_type == "target"
    assert fetched.ip_address == "127.0.0.1"
    assert "value" in fetched.details


def test_log_action_allows_null_user_for_system_events(db_session):
    entry = log_action(
        db_session,
        action="auth.login_failed",
        user_id=None,
        resource_type="user",
        resource_id="unknown@test.local",
    )
    assert entry.user_id is None


def test_login_failure_is_audited(client, db_session, admin_user):
    client.post(
        "/api/auth/login",
        json={"email": admin_user.email, "password": "WrongPassword999"},
    )
    entries = (
        db_session.query(AuditLog)
        .filter(AuditLog.action == "auth.login_failed")
        .all()
    )
    assert len(entries) >= 1


def test_audit_logs_endpoint_requires_admin(client, analyst_headers, viewer_headers):
    analyst_response = client.get("/api/audit-logs", headers=analyst_headers)
    assert analyst_response.status_code == 403

    viewer_response = client.get("/api/audit-logs", headers=viewer_headers)
    assert viewer_response.status_code == 403


def test_audit_logs_endpoint_accessible_by_admin(client, admin_headers, admin_user):
    client.get("/api/auth/me", headers=admin_headers)  # generates some activity

    response = client.get("/api/audit-logs", headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_audit_logs_filter_by_action(client, admin_headers, analyst_headers, db_session):
    # Trigger a known, distinctly-named audit event.
    client.post(
        "/api/targets",
        json={"name": "Audit Filter Target", "address": "203.0.113.70"},
        headers=analyst_headers,
    )

    response = client.get(
        "/api/audit-logs",
        params={"action": "target.created"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    assert all("target.created" in r["action"] for r in results)


def test_audit_logs_filter_by_user_id(client, admin_headers, analyst_user, analyst_headers):
    client.post(
        "/api/targets",
        json={"name": "User Filter Target", "address": "203.0.113.71"},
        headers=analyst_headers,
    )

    response = client.get(
        "/api/audit-logs",
        params={"user_id": str(analyst_user.id)},
        headers=admin_headers,
    )
    assert response.status_code == 200
    results = response.json()
    assert all(r["user_id"] == str(analyst_user.id) for r in results if r["user_id"])