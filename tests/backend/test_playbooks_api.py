"""API auth tests for playbook catalog endpoints. :-)"""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from backend.server.app import app


client = TestClient(app)
AUTH_HEADERS = {"X-Auth-Request-Email": "qa@hexsenses.com"}


@pytest.fixture(autouse=True)
def _require_auth(monkeypatch):
    monkeypatch.setenv("PLAYBOOKS_REQUIRE_AUTH", "1")
    # Re-import gate reads env at call time, so no module reload needed.
    yield


def test_list_playbooks_rejects_unauthenticated():
    response = client.get("/api/playbooks")
    assert response.status_code == 401
    assert "authentication required" in response.json()["detail"].lower()


def test_get_playbook_rejects_unauthenticated():
    response = client.get("/api/playbooks/comedy_shorts")
    assert response.status_code == 401


def test_list_playbooks_accepts_authenticated():
    response = client.get("/api/playbooks", headers=AUTH_HEADERS)
    assert response.status_code == 200
    body = response.json()
    ids = [p["id"] for p in body["playbooks"]]
    assert "comedy_shorts" in ids
    lang_ids = {lang["id"] for lang in body["languages"]}
    assert {"en", "zh-cn", "zh-yue", "zh-tw"} <= lang_ids


def test_get_playbook_accepts_authenticated():
    response = client.get("/api/playbooks/comedy_shorts", headers=AUTH_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "comedy_shorts"
    assert body["tone"] == "Humorous"


def test_get_playbook_404_when_authenticated():
    response = client.get("/api/playbooks/does_not_exist", headers=AUTH_HEADERS)
    assert response.status_code == 404


def test_invalid_email_header_rejected():
    response = client.get(
        "/api/playbooks",
        headers={"X-Auth-Request-Email": "not-an-email"},
    )
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_x_forwarded_email_accepted():
    response = client.get(
        "/api/playbooks/comedy_shorts",
        headers={"X-Forwarded-Email": "forwarded@hexsenses.com"},
    )
    assert response.status_code == 200


def test_auth_can_be_disabled_for_local_oss(monkeypatch):
    monkeypatch.setenv("PLAYBOOKS_REQUIRE_AUTH", "0")
    response = client.get("/api/playbooks")
    assert response.status_code == 200


def test_empty_email_header_rejected():
    response = client.get(
        "/api/playbooks",
        headers={"X-Auth-Request-Email": "   "},
    )
    assert response.status_code == 401


def test_parallel_authenticated_catalog_reads():
    from concurrent.futures import ThreadPoolExecutor

    def hit(_i: int):
        r = client.get("/api/playbooks", headers=AUTH_HEADERS)
        return r.status_code, "comedy_shorts" in str(r.json())

    with ThreadPoolExecutor(max_workers=8) as pool:
        outs = list(pool.map(hit, range(24)))
    assert all(code == 200 and ok for code, ok in outs)
