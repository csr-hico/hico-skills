"""Pure header parsing + the gating decision for the WEB UI (forward-auth).

NOTE: these headers are only trustworthy behind the Authentik outpost. The /mcp endpoint
does NOT use this - it authorizes on the validated JWT `groups` claim (see server.py).
"""

from __future__ import annotations

from collections.abc import Mapping

from .models import Identity

_USER_HEADER = "x-authentik-username"
_GROUPS_HEADER = "x-authentik-groups"


def _get_ci(headers: Mapping[str, str], key: str) -> str | None:
    for k, v in headers.items():
        if k.lower() == key:
            return v
    return None


def identity_from_headers(headers: Mapping[str, str]) -> Identity:
    """Build an Identity from forward-auth headers. Absent headers -> anonymous."""
    username = _get_ci(headers, _USER_HEADER)
    raw_groups = _get_ci(headers, _GROUPS_HEADER)
    groups = tuple(g.strip() for g in raw_groups.split(",") if g.strip()) if raw_groups else ()
    return Identity(username=(username or None), groups=groups)


def is_allowed(identity: Identity, required_group: str | None) -> bool:
    """Open when required_group is falsy; otherwise membership is required."""
    if not required_group:
        return True
    return required_group in identity.groups
