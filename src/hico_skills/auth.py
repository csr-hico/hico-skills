"""Pure header parsing for the WEB UI identity display.

NOTE: these headers are only trustworthy behind oauth2-proxy (reverse-proxy mode strips and
re-injects X-Forwarded-* identity headers, so clients cannot spoof them). The /mcp endpoint
does NOT use this - it authorizes on the validated Entra JWT (see server.py).
"""

from __future__ import annotations

from collections.abc import Mapping

from .models import Identity

_USER_HEADER = "x-forwarded-preferred-username"  # Entra UPN, e.g. vorname.nachname@firma.tld
_EMAIL_HEADER = "x-forwarded-email"
_GROUPS_HEADER = "x-forwarded-groups"


def _get_ci(headers: Mapping[str, str], key: str) -> str | None:
    for k, v in headers.items():
        if k.lower() == key:
            return v
    return None


def identity_from_headers(headers: Mapping[str, str]) -> Identity:
    """Build an Identity from oauth2-proxy headers. Absent headers -> anonymous."""
    username = _get_ci(headers, _USER_HEADER) or _get_ci(headers, _EMAIL_HEADER)
    raw_groups = _get_ci(headers, _GROUPS_HEADER)
    groups = tuple(g.strip() for g in raw_groups.split(",") if g.strip()) if raw_groups else ()
    # oauth2-proxy forwards no display-name claim; the UI falls back to username for initials.
    return Identity(username=(username or None), name=None, groups=groups)
