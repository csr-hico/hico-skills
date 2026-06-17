"""Plain data carriers. No behavior, no IO."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

SKILL = "skill"
AGENT = "agent"
VALID_TYPES = (SKILL, AGENT)


@dataclass(frozen=True)
class Skill:
    id: str
    type: str  # "skill" | "agent" (determined by which root directory it lives in)
    name: str
    description: str  # what BOTH the LLM and the UI accordion show
    when_to_use: str
    body: str
    tools: tuple[str, ...] = ()
    model: str | None = None
    # Filesystem facts, filled by the store after parsing (frontmatter stays pure):
    dir: Path | None = None  # the item's own folder (skills/<id>/ or agents/<id>/)
    resources: tuple[str, ...] = ()  # bundled files, relative POSIX paths, excl. the manifest


@dataclass(frozen=True)
class SearchHit:
    id: str
    type: str
    name: str
    when_to_use: str
    score: int = 0


@dataclass(frozen=True)
class Identity:
    username: str | None = None
    groups: tuple[str, ...] = field(default_factory=tuple)
    name: str | None = None
