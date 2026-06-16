# Architecture

One Python process, one container. FastMCP (on Starlette) serves the MCP endpoint at `/mcp` and,
via `@mcp.custom_route`, the web OnePager + a small JSON API.

## Layers

- **Core** (pure, no framework, fully unit-tested):
  - `frontmatter.py` - parse + validate a markdown file with YAML frontmatter into a `Skill`.
  - `store.py` - the only filesystem module: load, cache, and cheaply reload `skills/*.md`.
  - `search.py` - substring/token ranking (no vector DB in v1).
  - `get.py` - render the full definition; agents get a spawn-as-subtask directive.
  - `auth.py` - parse forward-auth headers; the web gating decision.
  - `config.py` - env -> immutable `Settings` (nothing infra-revealing is hardcoded).
  - `render.py` - inject brand colors + connect placeholders into the OnePager.
- **Adapters** (thin):
  - `server.py` - the `search`/`get` MCP tools + the OIDC resource-server auth for `/mcp`.
  - `web.py` - the `/`, `/api/skills`, `/api/me`, `/healthz`, `/static/*` routes + app assembly.

## Two auth surfaces (both Authentik, both gated to one group)

- **Web UI** (`/`, `/api/*`): behind Authentik **forward-auth** (Traefik `authentik@file`). The
  badge is read from `X-authentik-username` / `X-authentik-groups`, trustworthy only behind the
  outpost.
- **`/mcp`**: a full **OIDC OAuth 2.1 resource server**. `RemoteAuthProvider` + `JWTVerifier`
  validate the bearer JWT (signature / issuer / audience) against Authentik's JWKS and emit
  `401 + WWW-Authenticate` + protected-resource-metadata. A per-tool `AuthCheck` additionally
  requires the `groups` claim to contain `MCP_REQUIRED_GROUP`. It is NOT behind forward-auth (that
  would return an HTML login page to an MCP client).

## Data flow

Skills are markdown files baked into the image (`skills/`). A skill change is a PR merged to
`main` -> a Coolify rebuild. The store reloads on a directory-signature change, so local edits are
picked up without a restart.

## What this is NOT (v1)

No server-side agent execution (`run_agent`), no vector search, no database, no static-token auth.
See the project plan for the deferred roadmap.

## Deployment pipeline

GitHub is the source of truth; the homelab automation runs off a GitLab mirror.

1. PR merged to `main` on GitHub (branch protection + the `test` check gate every change).
2. A GitHub Action (`mirror-to-gitlab`) fast-forwards the GitLab mirror.
3. The GitLab push fires one webhook to the **webhook-proxy** (never a direct GitLab->Coolify hook).
4. The webhook-proxy syncs the SOPS-encrypted env to Coolify and forwards the push to Coolify,
   which rebuilds and redeploys the app. Traefik issues/renews the cert via httpChallenge.
