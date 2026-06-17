"""Web OnePager + JSON API routes, and ASGI app assembly.

Routes are registered via @mcp.custom_route on the FastMCP instance so they share one process
with /mcp. custom_route handlers are NOT wrapped by MCP auth - the web surface is gated upstream
by Authentik forward-auth (Traefik), and /healthz must stay open for the Docker healthcheck.
"""

from __future__ import annotations

from pathlib import Path

from fastmcp import FastMCP
from starlette.responses import (
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    Response,
)

from .auth import identity_from_headers
from .config import Settings, load_settings
from .render import render_index
from .server import build_auth, register_guidance, register_resources, register_tools
from .store import SkillStore, default_roots


def _read(frontend_dir: Path, name: str) -> str:
    return (frontend_dir / name).read_text(encoding="utf-8")


def register_routes(mcp: FastMCP, settings: Settings, store: SkillStore) -> None:
    index_html = _read(settings.frontend_dir, "index.html")
    styles_css = _read(settings.frontend_dir, "styles.css")
    app_js = _read(settings.frontend_dir, "app.js")

    @mcp.custom_route("/healthz", methods=["GET"])
    async def healthz(request):  # noqa: ANN001
        return PlainTextResponse("ok")

    @mcp.custom_route("/api/skills", methods=["GET"])
    async def api_skills(request):  # noqa: ANN001
        store.maybe_reload()
        return JSONResponse(
            [
                {
                    "id": s.id,
                    "type": s.type,
                    "name": s.name,
                    "description": s.description,
                    "when_to_use": s.when_to_use,
                    "resources": list(s.resources),
                }
                for s in store.all()
            ]
        )

    @mcp.custom_route("/api/me", methods=["GET"])
    async def api_me(request):  # noqa: ANN001
        ident = identity_from_headers(request.headers)
        return JSONResponse({"username": ident.username, "groups": list(ident.groups)})

    @mcp.custom_route("/", methods=["GET"])
    async def index(request):  # noqa: ANN001
        return HTMLResponse(render_index(index_html, settings))

    @mcp.custom_route("/static/styles.css", methods=["GET"])
    async def styles(request):  # noqa: ANN001
        return Response(styles_css, media_type="text/css")

    @mcp.custom_route("/static/app.js", methods=["GET"])
    async def appjs(request):  # noqa: ANN001
        return Response(app_js, media_type="application/javascript")


def build_mcp(settings: Settings, store: SkillStore) -> FastMCP:
    mcp = FastMCP("HICO Skill Library", auth=build_auth(settings))
    register_tools(mcp, settings, store)
    register_resources(mcp, settings, store)
    register_guidance(mcp, settings)
    register_routes(mcp, settings, store)
    return mcp


def build_app(settings: Settings | None = None):
    settings = settings or load_settings()
    store = SkillStore(default_roots(settings.skills_dir, settings.agents_dir))
    store.load()
    mcp = build_mcp(settings, store)
    return mcp.http_app(path="/mcp")
