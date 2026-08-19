"""FastMCP tools (search/get) + the OIDC resource-server auth for /mcp.

Auth model (user decision: strict full OIDC, no static-token fallback):
- AzureProvider (an OAuthProxy) validates the bearer JWT (signature/issuer/audience/scope)
  against the Entra tenant's JWKS and emits 401 + WWW-Authenticate + protected-resource-metadata
  for discovery.
- A valid token from the HICO tenant IS the authorization: every hico-entra login used to be
  auto-added to the HICO group anyway, so tenant membership was always the effective gate.
All config comes from env/Settings - nothing infra-revealing is hardcoded.
"""

from __future__ import annotations

import base64
import logging
import mimetypes

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.resources import FileResource
from fastmcp.server.auth.providers.azure import AzureProvider

from .config import Settings
from .get import render_definition
from .guidance import GUIDE_URI, discovery_text
from .models import AGENT
from .search import search as core_search
from .store import SkillStore

logger = logging.getLogger("hico_skills.search")


def build_auth(settings: Settings) -> AzureProvider | None:
    """DCR/CIMD-capable OAuth proxy directly against Entra ID, or None when auth is disabled.

    Entra has no dynamic client registration endpoint, so MCP clients (OpenAI, Claude, Gemini)
    cannot self-register against it. AzureProvider presents a DCR + CIMD interface to those
    clients while using the SINGLE pre-registered Entra app with one fixed redirect URI
    (`/auth/callback`). It validates tokens against the tenant JWKS (issuer + audience + the
    custom API scope), which is the whole gate: a valid HICO-tenant login grants access.
    """
    if not settings.auth_enabled:
        return None
    return AzureProvider(
        client_id=settings.oidc_client_id,
        client_secret=settings.oidc_client_secret,
        tenant_id=settings.entra_tenant_id,
        required_scopes=[settings.mcp_scope],
        base_url=settings.public_base_url,
        redirect_path="/auth/callback",
        # Internal tool: the IdP already authenticates and tenant membership gates access, so the
        # per-client consent screen only adds a fragile single-use-transaction step (re-hitting
        # /consent after submit -> "invalid or expired transaction"). Auto-approve instead.
        require_authorization_consent=False,
    )


def register_tools(mcp: FastMCP, settings: Settings, store: SkillStore) -> None:
    @mcp.tool
    def search(query: str = "", type: str | None = None) -> list[dict]:
        """Search the skill/agent library.

        Args:
            query: free-text query; empty returns everything.
            type: optional filter, "skill" or "agent".
        Returns ranked entries: {id, type, name, when_to_use}. Call `get(id)` for the full text.
        """
        store.maybe_reload()
        hits = core_search(store.all(), query, type)
        result = [
            {"id": h.id, "type": h.type, "name": h.name, "when_to_use": h.when_to_use} for h in hits
        ]
        # Telemetry trip-wire: when hits and payload size grow, it's time to revisit ranking /
        # consider embeddings (see search.py header + docs). approx tokens ~= chars / 4.
        payload_chars = sum(len(h["name"]) + len(h["when_to_use"]) for h in result)
        logger.info(
            "search query=%r type=%s hits=%d approx_tokens=%d corpus=%d",
            query,
            type,
            len(result),
            payload_chars // 4,
            len(store.all()),
        )
        return result

    @mcp.tool
    def get(id: str) -> str:
        """Get the full definition for a skill/agent id.

        Skills return their instructions verbatim. Agents are prefixed with a directive to run
        them as an isolated subtask.
        """
        store.maybe_reload()
        skill = store.get(id)
        if skill is None:
            raise ToolError(f"unknown id: {id!r}")
        return render_definition(skill)

    @mcp.tool
    def get_resource(id: str, path: str) -> str:
        """Fetch a file bundled with a skill/agent (a script, template, or reference).

        `path` is one of the relative paths listed under "Bundled files" in `get(id)`. Text is
        returned as-is; binary content is returned base64-encoded with a `[base64]` prefix.
        """
        store.maybe_reload()
        target = store.resource_path(id, path)
        if target is None:
            raise ToolError(f"no bundled file {path!r} for id {id!r}")
        data = target.read_bytes()
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return "[base64]" + base64.b64encode(data).decode("ascii")


def register_resources(mcp: FastMCP, settings: Settings, store: SkillStore) -> None:
    """Expose every bundled file as an MCP FileResource for native clients.

    Snapshot of the initial load: new files added later are still live via the `get_resource`
    tool, but appear as MCP resources only after the next restart (Coolify redeploys per push).
    """
    for skill in store.all():
        if skill.dir is None:
            continue
        kind = "agents" if skill.type == AGENT else "skills"
        for rel in skill.resources:
            mime = mimetypes.guess_type(rel)[0] or "application/octet-stream"
            is_binary = not (mime.startswith("text/") or mime in _TEXT_MIMES)
            mcp.add_resource(
                FileResource(
                    uri=f"file:///{kind}/{skill.id}/{rel}",
                    path=(skill.dir / rel).resolve(),
                    name=f"{skill.id}/{rel}",
                    description=f"Bundled file for {skill.type} '{skill.name}'",
                    mime_type=mime,
                    is_binary=is_binary,
                )
            )


# Common text-ish mimes that don't carry a text/ prefix.
_TEXT_MIMES = frozenset(
    {"application/json", "application/x-sh", "application/xml", "application/yaml", "image/svg+xml"}
)


def register_guidance(mcp: FastMCP, settings: Settings) -> None:
    """Expose the discover-and-use instruction as both an MCP prompt and a resource."""

    @mcp.prompt
    def use_skill_library() -> str:
        """Tell the model to discover and use the skills in this library via search/get."""
        return discovery_text()

    @mcp.resource(GUIDE_URI, mime_type="text/markdown")
    def usage_guide() -> str:
        """How to discover and use the skills in this library."""
        return discovery_text()
