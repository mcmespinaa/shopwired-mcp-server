"""Tests for the bearer-token middleware and /health endpoint.

These cover the security boundary of the remote (HTTP) transport:
- no token / malformed header / wrong token → 401
- correct token → request passes through
- /health is reachable without a token (platform probes), but never leaks detail
- empty configured token fails closed (defense in depth)
"""

from __future__ import annotations

import pytest
from pydantic import SecretStr
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from shopwired_mcp.auth import add_auth
from shopwired_mcp.config import settings

TOKEN = "test-token-1234"


@pytest.fixture(autouse=True)
def configured_token(monkeypatch):
    monkeypatch.setattr(settings, "auth_token", SecretStr(TOKEN))


@pytest.fixture()
def client() -> TestClient:
    """Minimal app behind the real middleware."""

    async def protected(request):
        return PlainTextResponse("secret data")

    async def health(request):
        return PlainTextResponse("healthy")

    app = Starlette(
        routes=[
            Route("/mcp", protected, methods=["GET", "POST"]),
            Route("/health", health, methods=["GET"]),
        ]
    )
    add_auth(app)
    return TestClient(app, raise_server_exceptions=False)


def test_missing_header_rejected(client):
    response = client.post("/mcp")
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"
    assert "secret" not in response.text


def test_wrong_token_rejected(client):
    response = client.post("/mcp", headers={"Authorization": f"Bearer not-{TOKEN}"})
    assert response.status_code == 401


def test_wrong_scheme_rejected(client):
    response = client.post("/mcp", headers={"Authorization": f"Basic {TOKEN}"})
    assert response.status_code == 401


def test_bearer_scheme_case_insensitive(client):
    response = client.get("/mcp", headers={"Authorization": f"bearer {TOKEN}"})
    assert response.status_code == 200


def test_correct_token_accepted(client):
    response = client.get("/mcp", headers={"Authorization": f"Bearer {TOKEN}"})
    assert response.status_code == 200
    assert response.text == "secret data"


def test_health_exempt_from_auth(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_trailing_slash_exempt(client):
    # Load balancers are commonly configured with "/health/"; the exemption
    # must normalize before Starlette's redirect_slashes ever runs.
    response = client.get("/health/")
    assert response.status_code == 200


def test_empty_configured_token_fails_closed(client, monkeypatch):
    monkeypatch.setattr(settings, "auth_token", SecretStr(""))
    # Even a request presenting an empty bearer token must be rejected.
    response = client.get("/mcp", headers={"Authorization": "Bearer "})
    assert response.status_code == 401
    response = client.get("/mcp")
    assert response.status_code == 401


def test_real_server_app_enforces_auth():
    """Integration: the PRODUCTION app composition (build_http_app — the same
    factory main() serves) rejects unauthenticated requests and serves /health
    without a token. Building via the factory means a refactor that drops
    add_auth from main()'s path fails this test."""
    from shopwired_mcp.server import build_http_app

    app = build_http_app()

    with TestClient(app, raise_server_exceptions=False) as client:
        assert client.post("/mcp", json={}).status_code == 401

        health = client.get("/health")
        assert health.status_code == 200
        body = health.json()
        assert body["status"] == "ok"
        assert "version" in body
