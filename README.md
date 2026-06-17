# HICO Skill Library

A library of AI **skills and agent definitions**, served as an OIDC-gated **remote MCP server**
plus a simple browse **OnePager**. Bind it into Claude, OpenAI, or Gemini and the model accesses
the right skills on its own.

It only **delivers definitions** as text (`search` + `get`); it never executes agents. Real
subtasks happen on the host that has a sub-agent mechanism; elsewhere an agent definition degrades
cleanly to an inline skill.

## Security principle: no infrastructure identifiers in this repo

This repo is meant to be shared. No domain, issuer, group, client id, or UUID is committed in
plaintext - not in code, compose labels, or docs. All of that comes from env at deploy time
(`secrets.enc.yaml` via SOPS, or Coolify env vars). `docs/CONNECT.md` keeps placeholders; the real
values are rendered on the OnePager only, behind login.

## Quickstart (local dev)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q                       # all green is the merge gate
MCP_REQUIRED_GROUP="" python -m hico_skills   # auth off for local; serves on :8000
```

Then open <http://127.0.0.1:8000/> and hit `http://127.0.0.1:8000/mcp` with an MCP client.

## Add a skill or agent

One folder per item (Anthropic Agent-Skills style), with a manifest file plus any bundled files:

```
skills/<id>/SKILL.md        + scripts/, templates/, references...
agents/<id>/AGENT.md        + scripts/, templates/, references...
```

The folder name is the id; the directory it lives in determines the type (no `type:` field).
See `skills/_TEMPLATE/` and `agents/_TEMPLATE/`. Manifest frontmatter:

```yaml
name: Human Readable Name
description: One or two sentences. This is what the LLM and the UI both see.
when_to_use: ...   # or a triggers: [..] list
# tools: [Read, Grep]      # agents only, optional
# model: claude-opus-4-8   # agents only, optional
```

**Bundled files** (scripts/templates/references) ride along in the folder. They are auto-discovered
and reachable by MCP clients two ways: the `get_resource(id, path)` tool, and as MCP resources at
`file:///<skills|agents>/<id>/<path>`. `get(id)` lists them automatically.

Folders/files starting with `_` or `.` are ignored. Invalid items are skipped (the server never
crashes on a bad contribution) and reported in the load result.

## Layout

```
src/hico_skills/   core (frontmatter/store/search/get/auth/config/render) + adapters (server/web)
frontend/          index.html, styles.css, app.js (no build step)
skills/            <id>/SKILL.md (+ bundled files), baked into the image
agents/            <id>/AGENT.md (+ bundled files), baked into the image
tests/             pytest; nothing merges red
docs/              ARCHITECTURE.md, CONNECT.md
```

## Deploy

Coolify (Raw-Compose) behind Traefik + Authentik. Brand colors are configurable via
`BRAND_ORANGE` / `BRAND_BLUE` / `BG` (env) or the CSS `:root` defaults. See `docs/ARCHITECTURE.md`
and the project plan for the full provisioning sequence.

## Config (env)

| Var | Purpose |
|-----|---------|
| `OIDC_ISSUER` / `OIDC_JWKS_URI` / `OIDC_AUDIENCE` / `OIDC_CLIENT_ID` | OIDC resource-server validation for `/mcp` (empty issuer = auth disabled, for local dev) |
| `MCP_REQUIRED_GROUP` | group the JWT `groups` claim must contain |
| `PUBLIC_BASE_URL` | used to render the `/mcp` URL in the connect docs |
| `BRAND_ORANGE` / `BRAND_BLUE` / `BG` | OnePager colors |
| `SKILLS_DIR` / `AGENTS_DIR` / `FRONTEND_DIR` / `HOST` / `PORT` | paths and bind address |
