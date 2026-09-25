"""Tests for authorized target management endpoints."""

import uuid


def test_create_target_requires_analyst_or_admin(client, viewer_headers):
    response = client.post(
        "/api/targets",
        json={"name": "Viewer Target", "address": "203.0.113.10"},
        headers=viewer_headers,
    )
    assert response.status_code == 403


def test_create_target_as_analyst_succeeds_unauthorized_by_default(
    client, analyst_headers
):
    response = client.post(
        "/api/targets",
        json={
            "name": "Lab Server 1",
            "address": "203.0.113.11",
            "description": "Test lab server",
            "asset_importance": "high",
        },
        headers=analyst_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Lab Server 1"
    assert body["is_authorized"] is False
    assert body["authorized_by_id"] is None
    assert body["asset_importance"] == "high"


def test_create_target_rejects_invalid_address(client, analyst_headers):
    response = client.post(
        "/api/targets",
        json={"name": "Bad Target", "address": "8.8.8.8; rm -rf /"},
        headers=analyst_headers,
    )
    assert response.status_code == 422


def test_create_target_rejects_invalid_name(client, analyst_headers):
    response = client.post(
        "/api/targets",
        json={"name": "Bad<script>Name", "address": "203.0.113.12"},
        headers=analyst_headers,
    )
    assert response.status_code == 422


def test_get_nonexistent_target_returns_404(client, viewer_headers):
    response = client.get(f"/api/targets/{uuid.uuid4()}", headers=viewer_headers)
    assert response.status_code == 404


def test_list_targets_search_and_filter(client, analyst_headers, viewer_headers):
    client.post(
        "/api/targets",
        json={"name": "Findable Server", "address": "203.0.113.13"},
        headers=analyst_headers,
    )
    client.post(
        "/api/targets",
        json={"name": "Other Machine", "address": "203.0.113.14"},
        headers=analyst_headers,
    )

    response = client.get(
        "/api/targets", params={"search": "Findable"}, headers=viewer_headers
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["name"] == "Findable Server"


def test_update_target(client, analyst_headers):
    create_resp = client.post(
        "/api/targets",
        json={"name": "Update Me", "address": "203.0.113.15"},
        headers=analyst_headers,
    )
    target_id = create_resp.json()["id"]

    update_resp = client.patch(
        f"/api/targets/{target_id}",
        json={"description": "Updated description", "asset_importance": "critical"},
        headers=analyst_headers,
    )
    assert update_resp.status_code == 200
    body = update_resp.json()
    assert body["description"] == "Updated description"
    assert body["asset_importance"] == "critical"


def test_authorize_and_revoke_target(client, analyst_headers):
    create_resp = client.post(
        "/api/targets",
        json={"name": "Authorize Me", "address": "203.0.113.16"},
        headers=analyst_headers,
    )
    target_id = create_resp.json()["id"]

    authorize_resp = client.post(
        f"/api/targets/{target_id}/authorize",
        json={"is_authorized": True},
        headers=analyst_headers,
    )
    assert authorize_resp.status_code == 200
    authorized_body = authorize_resp.json()
    assert authorized_body["is_authorized"] is True
    assert authorized_body["authorized_by_id"] is not None
    assert authorized_body["authorized_at"] is not None

    revoke_resp = client.post(
        f"/api/targets/{target_id}/authorize",
        json={"is_authorized": False},
        headers=analyst_headers,
    )
    assert revoke_resp.status_code == 200
    revoked_body = revoke_resp.json()
    assert revoked_body["is_authorized"] is False
    assert revoked_body["authorized_by_id"] is None
    assert revoked_body["authorized_at"] is None


def test_viewer_cannot_authorize_target(client, analyst_headers, viewer_headers):
    create_resp = client.post(
        "/api/targets",
        json={"name": "Viewer Auth Attempt", "address": "203.0.113.17"},
        headers=analyst_headers,
    )
    target_id = create_resp.json()["id"]

    response = client.post(
        f"/api/targets/{target_id}/authorize",
        json={"is_authorized": True},
        headers=viewer_headers,
    )
    assert response.status_code == 403


def test_deactivate_target_revokes_authorization(client, analyst_headers):
    create_resp = client.post(
        "/api/targets",
        json={"name": "Deactivate Me", "address": "203.0.113.18"},
        headers=analyst_headers,
    )
    target_id = create_resp.json()["id"]
    client.post(
        f"/api/targets/{target_id}/authorize",
        json={"is_authorized": True},
        headers=analyst_headers,
    )

    delete_resp = client.delete(f"/api/targets/{target_id}", headers=analyst_headers)
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/api/targets/{target_id}", headers=analyst_headers)
    body = get_resp.json()
    assert body["is_active"] is False
    assert body["is_authorized"] is False