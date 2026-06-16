# Connecting the MCP server

The server is a remote MCP server over **Streamable HTTP**, gated by OIDC (OAuth 2.1 / PKCE)
against Authentik. Access is limited to members of the configured group.

> Placeholders below are filled in live on the OnePager (behind login). Replace by hand here:
> - `<MCP_URL>` - e.g. `https://your-domain/mcp`
> - `<ISSUER>` - the Authentik OIDC issuer for this app
> - `<CLIENT_ID>` - the public client id
>
> Scopes: `openid profile groups`

## Claude

- **claude.ai** (Pro / Team / Enterprise): Settings -> Connectors -> *Add custom connector* ->
  URL `<MCP_URL>`, then complete the login.
- **Claude Code**: `claude mcp add --transport http hico-skills <MCP_URL>`, then approve the
  browser OAuth flow.
- **Claude API**: pass the server in the `mcp_servers` array (beta header); obtain the OAuth token
  out of band and set `authorization_token`.

## OpenAI

- **ChatGPT** (Developer mode / Connectors): add the MCP server URL `<MCP_URL>` and log in. No
  advanced OAuth settings needed - the client registers automatically (DCR and CIMD both work).
- **Responses API**: `tools: [{ "type": "mcp", "server_url": "<MCP_URL>", "require_approval": ... }]`
  with the authorization token.

## Google Gemini

- **Gemini CLI**: add to `~/.gemini/settings.json` under `mcpServers` with `"httpUrl": "<MCP_URL>"`.
  Note: Gemini CLI is being deprecated (~2026-06-18) in favour of "Antigravity"; verify successor
  support. Validate against Claude first.
- **Gemini SDK**: register the MCP server via the SDK's MCP support.

## Tools exposed

- `search(query, type?)` -> ranked `{id, type, name, when_to_use}` (type is `skill` or `agent`).
- `get(id)` -> full definition text. Agents are prefixed with a directive to run them as an
  isolated subtask.

## One-time per client

Because Authentik dynamic client registration is not relied upon, each client type needs its
redirect URI registered once on the Authentik OIDC provider.
