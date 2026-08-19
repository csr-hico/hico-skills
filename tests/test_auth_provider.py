from __future__ import annotations

from fastmcp.server.auth.providers.azure import AzureProvider

from hico_skills.config import load_settings
from hico_skills.server import build_auth


def test_issuer_derived_from_tenant():
    s = load_settings({"ENTRA_TENANT_ID": "11111111-2222-3333-4444-555555555555"})
    assert s.oidc_issuer == (
        "https://login.microsoftonline.com/11111111-2222-3333-4444-555555555555/v2.0"
    )
    assert load_settings({}).oidc_issuer == ""


def test_build_auth_returns_azure_provider_when_configured():
    s = load_settings(
        {
            "ENTRA_TENANT_ID": "11111111-2222-3333-4444-555555555555",
            "OIDC_CLIENT_ID": "cid",
            "OIDC_CLIENT_SECRET": "secret-derives-signing-key",
            "PUBLIC_BASE_URL": "https://hico-skills.example.tld",
        }
    )
    auth = build_auth(s)
    assert isinstance(auth, AzureProvider)
    # The custom API scope defaults to mcp.access and gets the api://<client_id> prefix.
    assert auth.identifier_uri == "api://cid"
    assert s.mcp_scope == "mcp.access"


def test_build_auth_none_without_entra():
    assert build_auth(load_settings({})) is None
    # client_id alone is not enough - tenant is required too.
    assert build_auth(load_settings({"OIDC_CLIENT_ID": "cid"})) is None
