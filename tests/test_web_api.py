from __future__ import annotations

import pytest
from starlette.testclient import TestClient

from hico_skills.web import build_app


@pytest.fixture
def client(settings):
    app = build_app(settings)
    with TestClient(app) as c:
        yield c


def test_healthz_open(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.text == "ok"


def test_api_skills_shape_includes_description(client):
    r = client.get("/api/skills")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 3
    assert set(data[0]) == {"id", "type", "name", "description", "when_to_use"}


def test_api_me_reads_forward_auth_headers(client):
    r = client.get(
        "/api/me",
        headers={"X-authentik-username": "jdoe", "X-authentik-groups": "HICO,dev"},
    )
    assert r.json() == {"username": "jdoe", "groups": ["HICO", "dev"]}


def test_api_me_anonymous(client):
    assert client.get("/api/me").json() == {"username": None, "groups": []}


def test_index_injects_brand_color(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "--brand-orange" in r.text
