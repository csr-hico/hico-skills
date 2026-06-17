"""Smoke test: the MCP tools work end-to-end via the in-process FastMCP client.

This also catches FastMCP wiring/lifespan regressions without spinning up an HTTP server.
Auth is disabled in the test settings (no OIDC_ISSUER), so the tools are callable.
"""

from __future__ import annotations

import asyncio

from fastmcp import Client

from hico_skills.get import AGENT_SPAWN_DIRECTIVE
from hico_skills.store import SkillStore, default_roots
from hico_skills.web import build_mcp


def _run(coro):
    return asyncio.run(coro)


def test_tools_listed_and_callable(settings):
    store = SkillStore(default_roots(settings.skills_dir, settings.agents_dir))
    store.load()
    mcp = build_mcp(settings, store)

    async def go():
        async with Client(mcp) as c:
            names = {t.name for t in await c.list_tools()}
            assert {"search", "get", "get_resource"} <= names

            res = await c.call_tool("search", {"query": "alpha"})
            assert any(item["id"] == "alpha-skill" for item in res.data)

            got = await c.call_tool("get", {"id": "gamma-agent"})
            assert got.data.startswith(AGENT_SPAWN_DIRECTIVE)

            # bundled file fetchable via the tool ...
            rsrc = await c.call_tool("get_resource", {"id": "beta-helper", "path": "scripts/run.py"})
            assert rsrc.data == "print('hi')\n"
            # ... and exposed as an MCP resource
            uris = {str(r.uri) for r in await c.list_resources()}
            assert "file:///skills/beta-helper/scripts/run.py" in uris

            prompts = {p.name for p in await c.list_prompts()}
            assert "use_skill_library" in prompts

            resources = {str(r.uri) for r in await c.list_resources()}
            assert "guide://usage" in resources

    _run(go())
