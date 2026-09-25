"""Tests for authentication and user-registration endpoints."""

import uuid


def test_login_success(client, admin_user):
    response = client.post(
        "/api/auth/login",
        json={"email": admin_user.email, "password": "TestPassword123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str) and len(body["access_token"]) > 0
    assert body["expires_in"] > 0


def test_login_wrong_password(client, admin_user):
    response = client.post(
        "/api/auth/login",
        json={"email": admin_user.email, "password": "WrongPassword999"},
    )
    assert response.status_code == 401


def test_login_unknown_email(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "nobody@test.local", "password": "SomePassword123"},
    )
    assert response.status_code == 401


def test_get_me_requires_authentication(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_get_me_returns_current_user(client, admin_user, admin_headers):
    response = client.get("/api/auth/me", headers=admin_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == admin_user.email
    assert body["role"] == "admin"


def test_register_requires_admin_role(client, analyst_headers):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newuser@test.local",
            "full_name": "New User",
            "role": "viewer",
            "password": "NewUserPass123",
        },
        headers=analyst_headers,
    )
    assert response.status_code == 403


def test_register_as_admin_succeeds(client, admin_headers):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "created-by-admin@test.local",
            "full_name": "Created User",
            "role": "analyst",
            "password": "CreatedUserPass123",
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "created-by-admin@test.local"
    assert body["role"] == "analyst"
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate_email_conflicts(client, admin_headers):
    payload = {
        "email": "duplicate@test.local",
        "full_name": "Dup User",
        "role": "viewer",
        "password": "DupUserPass123",
    }
    first = client.post("/api/auth/register", json=payload, headers=admin_headers)
    assert first.status_code == 201

    second = client.post("/api/auth/register", json=payload, headers=admin_headers)
    assert second.status_code == 409


def test_register_rejects_short_password(client, admin_headers):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "shortpass@test.local",
            "full_name": "Short Pass",
            "role": "viewer",
            "password": "short",
        },
        headers=admin_headers,
    )
    assert response.status_code == 422


def test_invalid_token_rejected(client):
    response = client.get(
        "/api/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401


def test_unknown_user_id_in_token_rejected(client):
    # A syntactically valid but nonexistent subject must be rejected, not
    # cause a server error.
    from app.security.jwt_handler import create_access_token

    fake_token = create_access_token(subject=str(uuid.uuid4()))
    response = client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {fake_token}"}
    )
    assert response.status_code == 401