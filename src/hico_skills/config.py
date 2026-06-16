"""Environment -> immutable Settings. The app hardcodes nothing infra-revealing.

Every domain/issuer/client_id/group comes from env (injected at deploy time from the
SOPS-encrypted secrets), so the shared repo never names the hosting.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    skills_dir: Path
    frontend_dir: Path
    host: str
    port: int
    # Infra-revealing -> always from env (SOPS/Coolify), never committed:
    oidc_issuer: str
    oidc_jwks_uri: str
    oidc_audience: str
    oidc_client_id: str
    oidc_client_secret: str  # empty -> public client (PKCE)
    oidc_authorize_endpoint: str
    oidc_token_endpoint: str
    mcp_required_group: str
    public_base_url: str
    # Generic, non-revealing:
    brand_orange: str
    brand_blue: str
    bg: str

    @property
    def auth_enabled(self) -> bool:
        return bool(self.oidc_issuer)

    @property
    def mcp_url(self) -> str:
        base = self.public_base_url.rstrip("/")
        return f"{base}/mcp" if base else ""


def load_settings(env: dict[str, str] | None = None) -> Settings:
    e = os.environ if env is None else env

    issuer = e.get("OIDC_ISSUER", "").strip()
    jwks = e.get("OIDC_JWKS_URI", "").strip()
    if issuer and not jwks:
        jwks = issuer.rstrip("/") + "/jwks/"

    # Authentik's authorize/token endpoints are global (not per-app); derive them from the
    # issuer host so nothing is hardcoded. Overridable via env if the IdP differs.
    idp_base = issuer.split("/application/o/")[0] if "/application/o/" in issuer else ""
    authorize = e.get("OIDC_AUTHORIZE_ENDPOINT", "").strip() or (
        f"{idp_base}/application/o/authorize/" if idp_base else ""
    )
    token_ep = e.get("OIDC_TOKEN_ENDPOINT", "").strip() or (
        f"{idp_base}/application/o/token/" if idp_base else ""
    )

    return Settings(
        skills_dir=Path(e.get("SKILLS_DIR", str(_REPO_ROOT / "skills"))),
        frontend_dir=Path(e.get("FRONTEND_DIR", str(_REPO_ROOT / "frontend"))),
        host=e.get("HOST", "0.0.0.0"),
        port=int(e.get("PORT", "8000")),
        oidc_issuer=issuer,
        oidc_jwks_uri=jwks,
        oidc_audience=e.get("OIDC_AUDIENCE", "").strip(),
        oidc_client_id=e.get("OIDC_CLIENT_ID", "").strip(),
        oidc_client_secret=e.get("OIDC_CLIENT_SECRET", "").strip(),
        oidc_authorize_endpoint=authorize,
        oidc_token_endpoint=token_ep,
        mcp_required_group=e.get("MCP_REQUIRED_GROUP", "").strip(),
        public_base_url=e.get("PUBLIC_BASE_URL", "").strip(),
        brand_orange=e.get("BRAND_ORANGE", "#FF5F2C").strip(),
        brand_blue=e.get("BRAND_BLUE", "#2C53AB").strip(),
        bg=e.get("BG", "#fbfbfd").strip(),
    )
