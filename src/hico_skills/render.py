"""Render index.html at request time: inject brand colors + connect placeholders. Pure.

Real connect values (MCP URL, issuer, client_id) are filled here at runtime - so they live
only behind the HICO login, never in the committed repo (docs/CONNECT.md keeps placeholders).
HTML-safe tokens ({{...}}) are used so a browser never mistakes a placeholder for a tag.
"""

from __future__ import annotations

from .config import Settings

_STYLE_MARKER = "{{BRAND_STYLE}}"
_UNSET = "(noch nicht konfiguriert)"


def _brand_style(settings: Settings) -> str:
    return (
        "<style>:root{"
        f"--brand-orange:{settings.brand_orange};"
        f"--brand-blue:{settings.brand_blue};"
        f"--bg:{settings.bg};"
        "}</style>"
    )


def render_index(html: str, settings: Settings) -> str:
    out = html.replace(_STYLE_MARKER, _brand_style(settings))
    out = out.replace("{{MCP_URL}}", settings.mcp_url or _UNSET)
    out = out.replace("{{ISSUER}}", settings.oidc_issuer or _UNSET)
    out = out.replace("{{CLIENT_ID}}", settings.oidc_client_id or _UNSET)
    out = out.replace("{{VERSION}}", settings.version_label)
    return out
