from __future__ import annotations

from fastmcp.server.auth import OAuthProxy

from hico_skills.config import load_settings
from hico_skills.server import build_auth


def test_endpoints_derived_from_issuer():
    s = load_settings({"OIDC_ISSUER": "https://login.example.tld/application/o/hico-skills-mcp/"})
    assert s.oidc_authorize_endpoint == "https://login.example.tld/application/o/authorize/"
    assert s.oidc_token_endpoint == "https://login.example.tld/application/o/token/"


def test_build_auth_returns_oauth_proxy_when_configured():
    s = load_settings(
        {
            "OIDC_ISSUER": "https://login.example.tld/application/o/hico-skills-mcp/",
            "OIDC_CLIENT_ID": "cid",
            "OIDC_CLIENT_SECRET": "secret-derives-signing-key",
            "PUBLIC_BASE_URL": "https://hico-skills.example.tld",
        }
    )
    assert isinstance(build_auth(s), OAuthProxy)


def test_build_auth_none_without_oidc():
    assert build_auth(load_settings({})) is None
