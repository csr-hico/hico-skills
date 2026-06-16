"""Dumb-but-predictable substring/token search + ranking. No IO, no globals.

ponytail: no vector DB - add semantic search only when substring measurably falls short.
"""

from __future__ import annotations

from collections.abc import Iterable

from .models import SearchHit, Skill


def _score(skill: Skill, tokens: list[str], phrase: str) -> int:
    name = skill.name.lower()
    wtu = skill.when_to_use.lower()
    desc = skill.description.lower()
    haystack = f"{name} {wtu} {desc}"

    # AND semantics: every token must appear somewhere, else it is not a hit.
    if not all(t in haystack for t in tokens):
        return 0

    score = 0
    if name == phrase:
        score += 1000
    elif name.startswith(phrase):
        score += 500
    elif phrase in name:
        score += 300

    for t in tokens:
        if t in name:
            score += 50
        elif t in wtu:
            score += 20
        elif t in desc:
            score += 10

    return max(score, 1)  # all tokens matched -> at least a weak hit


def search(skills: Iterable[Skill], query: str, type_: str | None = None) -> list[SearchHit]:
    """Rank skills against a query. Empty query -> all (name-sorted). type_ filters skill|agent."""
    items = [s for s in skills if type_ is None or s.type == type_]
    phrase = query.strip().lower()

    if not phrase:
        ordered = sorted(items, key=lambda s: s.name.lower())
        return [SearchHit(s.id, s.type, s.name, s.when_to_use, 0) for s in ordered]

    tokens = phrase.split()
    scored = [(s, _score(s, tokens, phrase)) for s in items]
    hits = [(s, sc) for s, sc in scored if sc > 0]
    hits.sort(key=lambda pair: (-pair[1], pair[0].name.lower()))
    return [SearchHit(s.id, s.type, s.name, s.when_to_use, sc) for s, sc in hits]
