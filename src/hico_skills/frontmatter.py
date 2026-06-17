"""Parse + validate a markdown file with YAML frontmatter into a Skill. Zero IO."""

from __future__ import annotations

import yaml

from .models import SKILL, VALID_TYPES, Skill

_DELIM = "---"


class FrontmatterError(ValueError):
    """Raised when a skill file's frontmatter is missing required fields or malformed."""


def split_frontmatter(text: str) -> tuple[dict, str]:
    """Split a leading '---' YAML block from the body.

    Returns (meta, body). Missing block -> ({}, text) (lenient; validation happens later).
    Malformed YAML -> FrontmatterError (never a raw yaml exception).
    """
    stripped = text.lstrip("﻿")  # tolerate a UTF-8 BOM
    if not stripped.startswith(_DELIM):
        return {}, text

    # Find the closing delimiter on its own line after the opening one.
    lines = stripped.splitlines()
    closing = None
    for i in range(1, len(lines)):
        if lines[i].strip() == _DELIM:
            closing = i
            break
    if closing is None:
        raise FrontmatterError("frontmatter opened with '---' but never closed")

    raw_meta = "\n".join(lines[1:closing])
    body = "\n".join(lines[closing + 1 :])
    try:
        meta = yaml.safe_load(raw_meta) or {}
    except yaml.YAMLError as exc:
        raise FrontmatterError(f"invalid YAML frontmatter: {exc}") from exc
    if not isinstance(meta, dict):
        raise FrontmatterError("frontmatter must be a YAML mapping")
    return meta, body


def _normalize_when_to_use(meta: dict) -> str:
    wtu = meta.get("when_to_use")
    if wtu:
        return str(wtu).strip()
    triggers = meta.get("triggers")
    if isinstance(triggers, (list, tuple)):
        return ", ".join(str(t).strip() for t in triggers if str(t).strip())
    if triggers:
        return str(triggers).strip()
    return ""


def _normalize_tools(meta: dict) -> tuple[str, ...]:
    tools = meta.get("tools")
    if not tools:
        return ()
    if isinstance(tools, (list, tuple)):
        return tuple(str(t).strip() for t in tools if str(t).strip())
    return tuple(t.strip() for t in str(tools).split(",") if t.strip())


def skill_from_text(text: str, *, skill_id: str, type_: str = SKILL) -> Skill:
    """Parse + validate one SKILL.md/AGENT.md text into a Skill, or raise FrontmatterError.

    `type_` is supplied by the loader from the root directory (skills/ -> skill, agents/ -> agent);
    any `type:` in the frontmatter is ignored (the directory is canonical).
    """
    meta, body = split_frontmatter(text)

    name = meta.get("name")
    if not name or not str(name).strip():
        raise FrontmatterError(f"{skill_id}: missing required 'name'")

    description = meta.get("description")
    if not description or not str(description).strip():
        raise FrontmatterError(f"{skill_id}: missing required 'description'")

    type_ = str(type_).strip().lower()
    if type_ not in VALID_TYPES:
        raise FrontmatterError(f"{skill_id}: invalid type {type_!r} (allowed: {VALID_TYPES})")

    return Skill(
        id=skill_id,
        type=type_,
        name=str(name).strip(),
        description=str(description).strip(),
        when_to_use=_normalize_when_to_use(meta),
        body=body.strip(),
        tools=_normalize_tools(meta),
        model=(str(meta["model"]).strip() if meta.get("model") else None),
    )
