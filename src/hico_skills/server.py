"""FastMCP tools (search/get) + the OIDC resource-server auth for /mcp.

Auth model (user decision: strict full OIDC, no static-token fallback):
- RemoteAuthProvider + JWTVerifier validate the bearer JWT (signature/issuer/audience) against
  Authentik's JWKS and emit 401 + WWW-Authenticate + protected-resource-metadata for discovery.
- A per-tool AuthCheck additionally requires the `groups` claim to contain MCP_REQUIRED_GROUP.
All config comes from env/Settings - nothing infra-revealing is hardcoded.
"""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.auth import AuthContext, AuthCheck, RemoteAuthProvider
from fastmcp.server.auth.providers.jwt import JWTVerifier

from .config import Settings
from .get import render_definition
from .guidance import GUIDE_URI, discovery_text
from .search import search as core_search
from .store import SkillStore


def require_group(group: str) -> AuthCheck:
    """An AuthCheck that passes only if the token's `groups` claim contains `group`."""

    def check(ctx: AuthContext) -> bool:
        token = ctx.token
        if token is None:
            return False
        claims = getattr(token, "claims", None) or {}
        return group in (claims.get("groups") or [])

    return check


def build_auth(settings: Settings) -> RemoteAuthProvider | None:
    """OIDC resource-server provider, or None when auth is disabled (local dev/tests)."""
    if not settings.auth_enabled:
        return None
    verifier = JWTVerifier(
        jwks_uri=settings.oidc_jwks_uri,
        issuer=settings.oidc_issuer,
        audience=settings.oidc_audience or None,
    )
    return RemoteAuthProvider(
        token_verifier=verifier,
        authorization_servers=[settings.oidc_issuer],
        base_url=settings.public_base_url,
        scopes_supported=["openid", "profile", "groups"],
        resource_name="HICO Skill Library",
    )


def _group_check(settings: Settings) -> AuthCheck | None:
    return require_group(settings.mcp_required_group) if settings.mcp_required_group else None


def register_tools(mcp: FastMCP, settings: Settings, store: SkillStore) -> None:
    group_check = _group_check(settings)

    @mcp.tool(auth=group_check)
    def search(query: str = "", type: str | None = None) -> list[dict]:
        """Search the skill/agent library.

        Args:
            query: free-text query; empty returns everything.
            type: optional filter, "skill" or "agent".
        Returns ranked entries: {id, type, name, when_to_use}. Call `get(id)` for the full text.
        """
        store.maybe_reload()
        hits = core_search(store.all(), query, type)
        return [
            {"id": h.id, "type": h.type, "name": h.name, "when_to_use": h.when_to_use} for h in hits
        ]

    @mcp.tool(auth=group_check)
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


def register_guidance(mcp: FastMCP, settings: Settings) -> None:
    """Expose the discover-and-use instruction as both an MCP prompt and a resource."""
    group_check = _group_check(settings)

    @mcp.prompt(auth=group_check)
    def use_skill_library() -> str:
        """Tell the model to discover and use the skills in this library via search/get."""
        return discovery_text()

    @mcp.resource(GUIDE_URI, mime_type="text/markdown", auth=group_check)
    def usage_guide() -> str:
        """How to discover and use the skills in this library."""
        return discovery_text()
