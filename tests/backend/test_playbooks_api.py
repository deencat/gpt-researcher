"""API tests for playbook catalog endpoints (intentionally unauthenticated). :-)"""

from __future__ import annotations

from fastapi.testclient import TestClient

from backend.server.app import app


client = TestClient(app)


def test_list_playbooks_requires_no_auth():
    """Catalog is public read — same posture as other unauthenticated GET APIs."""
    response = client.get("/api/playbooks")
    assert response.status_code == 200
    body = response.json()
    assert "playbooks" in body
    assert "languages" in body
    ids = [p["id"] for p in body["playbooks"]]
    assert "comedy_shorts" in ids
    lang_ids = {lang["id"] for lang in body["languages"]}
    assert {"en", "zh-cn", "zh-yue", "zh-tw"} <= lang_ids


def test_get_playbook_by_id():
    response = client.get("/api/playbooks/comedy_shorts")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "comedy_shorts"
    assert body["tone"] == "Humorous"
    assert isinstance(body["structure"], list)
    assert body["structure"]


def test_get_playbook_404():
    response = client.get("/api/playbooks/does_not_exist")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
