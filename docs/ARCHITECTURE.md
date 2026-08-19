# Architecture

One Python process plus an oauth2-proxy sidecar, one compose stack. FastMCP (on Starlette)
serves the MCP endpoint at `/mcp` and, via `@mcp.custom_route`, the web OnePager + a small
JSON API. oauth2-proxy gates the web surface with a direct Entra ID login.

## Layers

- **Core** (pure, no framework, fully unit-tested):
  - `frontmatter.py` - parse + validate a manifest's YAML frontmatter into a `Skill` (type is
    supplied by the loader from the root directory, not read from frontmatter).
  - `store.py` - the only filesystem module: load, cache, and cheaply reload the `skills/<id>/`
    and `agents/<id>/` folders; discovers each item's bundled files and gates resource access
    (only enumerated files are returnable - defeats path traversal).
  - `search.py` - substring/token ranking (no vector DB in v1).
  - `get.py` - render the full definition; agents get a spawn-as-subtask directive, and bundled
    files are listed in a trailing "Bundled files" section.
  - `auth.py` - parse the oauth2-proxy identity headers for the web badge.
  - `config.py` - env -> immutable `Settings` (nothing infra-revealing is hardcoded).
  - `render.py` - inject brand colors + connect placeholders into the OnePager.
- **Adapters** (thin):
  - `server.py` - the `search`/`get`/`get_resource` MCP tools, bundled files as
    `FileResource`s, + the OIDC resource-server auth for `/mcp`.
  - `web.py` - the `/`, `/api/skills`, `/api/me`, `/healthz`, `/static/*` routes + app assembly.

## Two auth surfaces (both direct Entra ID, no Authentik middleman)

Both use the SAME pre-registered Entra app registration the old Authentik federation used.
Tenant membership is the gate: a valid login against the HICO tenant grants access (under
Authentik every hico-entra login was auto-added to the required group anyway, so this is the
same effective policy with one hop less).

- **Web UI** (`/`, `/api/*`): behind an **oauth2-proxy** sidecar in reverse-proxy mode
  (`provider=entra-id`, tenant-scoped issuer, strictly verified). The badge is read from
  `X-Forwarded-Preferred-Username` / `X-Forwarded-Email` / `X-Forwarded-Groups`; oauth2-proxy
  strips client-supplied copies before injecting its own, so they are trustworthy behind it.
- **`/mcp`**: a full **OIDC OAuth 2.1 resource server**. FastMCP's `AzureProvider` validates the
  bearer JWT (signature / issuer / audience / custom API scope `MCP_SCOPE`, default `mcp.access`)
  against the tenant JWKS and emits `401 + WWW-Authenticate` + protected-resource-metadata. It is
  NOT behind oauth2-proxy (that would return an HTML login page to an MCP client).

Entra prerequisites on the app registration (already configured): redirect URIs
`/auth/callback` (MCP) + `/oauth2/callback` (web), "Expose an API" with the `mcp.access` scope
(admin-consented), and `requestedAccessTokenVersion: 2` in the manifest (v1 tokens would fail
issuer validation). NOTE: Entra client secrets expire (max 24 months) - rotation is a
recurring ops task; the old Authentik setup was a public client without a secret.

> **DCR persistence.** `AzureProvider` (an `OAuthProxy`) presents Dynamic Client Registration to
> MCP clients and stores each registration (plus issued tokens) in an encrypted file store under
> `$FASTMCP_HOME` (`/data/fastmcp`, on the `oauth-state` volume). This MUST stay on a volume:
> otherwise a rebuild or restart wipes it and previously-registered clients fail reconnect with
> "Client Not Registered". The store's encryption key derives from the upstream client secret, so
> rotating the Entra secret invalidates existing registrations (clients just re-register;
> decryption errors are treated as cache misses, not crashes).

## Data flow

Skills/agents are folders baked into the image (`skills/<id>/SKILL.md`, `agents/<id>/AGENT.md`,
plus bundled files). A change is a PR merged to `main` -> a Coolify rebuild. The store reloads on a
file-signature change (covering bundled files too), so local edits are picked up without a restart.
The `get_resource` tool serves bundled files live; the equivalent `FileResource`s are a startup
snapshot (they refresh per deploy).

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
