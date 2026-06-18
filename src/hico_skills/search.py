"""Dumb-but-predictable lexical search + ranking. No IO, no globals.

ponytail: no vector DB - add semantic search only when this measurably falls short (see
docs: revisit around a few hundred items, or when query logs show real cross-language /
paraphrase misses the alias table can't cover).

What it does beyond naive substring:
- normalize query and fields the same way (casefold + diacritic strip), so `Müller` matches
  `muller` and `ß` matches `ss` (the corpus mixes German and English).
- summed scoring, NOT all-tokens-must-match: a missing token lowers the score instead of
  zeroing the hit, so `create workflow from code` still finds a `create-workflow` skill.
- per-field weighting (name >> when_to_use >> description), with exact/prefix/substring name
  bonuses preserved.
- a small hand-curated DE/EN alias table (aliases.py) bridges synonyms (`login` -> a skill
  whose when_to_use says `authenticate`); alias hits score below direct hits.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable

from .aliases import RAW_GROUPS
from .models import SearchHit, Skill

_WORD = re.compile(r"[a-z0-9]+")
_ALIAS_FACTOR = 0.6  # an alias-bridged match counts less than a direct one


def _norm(s: str) -> str:
    """Casefold then strip diacritics to plain ASCII. `ß`->`ss`, `Ü`->`u`, `É`->`e`."""
    s = s.casefold()  # casefold first so ß -> ss survives the ASCII step
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return s


def _tokens(s: str) -> list[str]:
    return _WORD.findall(_norm(s))


# Build the alias index once: every term -> the other (normalized) terms in its group.
_ALIASES: dict[str, frozenset[str]] = {}
for _group in RAW_GROUPS:
    _folded = {_norm(t) for t in _group}
    for _t in _folded:
        _ALIASES[_t] = _ALIASES.get(_t, frozenset()) | (_folded - {_t})


def _field_weight(token: str, name: str, wtu: str, desc: str) -> int:
    """Best per-field substring weight for one token (fields already normalized)."""
    if token in name:
        return 50
    if token in wtu:
        return 20
    if token in desc:
        return 10
    return 0


def _token_score(token: str, name: str, wtu: str, desc: str) -> float:
    """Direct match at full weight; otherwise the best alias match at a reduced weight."""
    direct = _field_weight(token, name, wtu, desc)
    if direct:
        return float(direct)
    best = 0.0
    for alias in _ALIASES.get(token, ()):
        best = max(best, _field_weight(alias, name, wtu, desc) * _ALIAS_FACTOR)
    return best


def _score(skill: Skill, tokens: list[str], phrase: str) -> int:
    name = _norm(skill.name)
    wtu = _norm(skill.when_to_use)
    desc = _norm(skill.description)

    score = 0.0
    if phrase:
        if name == phrase:
            score += 1000
        elif name.startswith(phrase):
            score += 500
        elif phrase in name:
            score += 300

    for t in tokens:
        score += _token_score(t, name, wtu, desc)

    return round(score)


def search(skills: Iterable[Skill], query: str, type_: str | None = None) -> list[SearchHit]:
    """Rank skills against a query. Empty query -> all (name-sorted). type_ filters skill|agent."""
    items = [s for s in skills if type_ is None or s.type == type_]
    phrase = _norm(query.strip())

    if not phrase:
        ordered = sorted(items, key=lambda s: s.name.lower())
        return [SearchHit(s.id, s.type, s.name, s.when_to_use, 0) for s in ordered]

    tokens = _tokens(query)
    scored = [(s, _score(s, tokens, phrase)) for s in items]
    hits = [(s, sc) for s, sc in scored if sc > 0]
    hits.sort(key=lambda pair: (-pair[1], pair[0].name.lower()))
    return [SearchHit(s.id, s.type, s.name, s.when_to_use, sc) for s, sc in hits]
