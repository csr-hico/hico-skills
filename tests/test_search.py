from __future__ import annotations

from hico_skills.search import search


def test_empty_query_returns_all_name_sorted(store):
    hits = search(store.all(), "")
    assert [h.id for h in hits] == ["alpha-skill", "beta-helper", "gamma-agent"]


def test_type_filter(store):
    hits = search(store.all(), "", type_="agent")
    assert [h.id for h in hits] == ["gamma-agent"]


def test_name_match_ranks_first(store):
    hits = search(store.all(), "alpha")
    assert hits[0].id == "alpha-skill"


def test_match_in_when_to_use_is_found(store):
    hits = search(store.all(), "widget")  # only in beta's triggers -> when_to_use + description
    assert [h.id for h in hits] == ["beta-helper"]


def test_match_in_description_only_is_found(store):
    hits = search(store.all(), "isolated")  # only in gamma's description
    assert [h.id for h in hits] == ["gamma-agent"]


def test_no_match_returns_empty(store):
    assert search(store.all(), "zzznotfound") == []


def test_exact_name_outranks_description_match():
    from hico_skills.models import Skill

    named = Skill("a", "skill", "widget", "unrelated", "", "")
    described = Skill("b", "skill", "other", "this mentions widget here", "", "")
    hits = search([described, named], "widget")
    assert [h.id for h in hits] == ["a", "b"]


def test_missing_token_no_longer_zeros_the_hit():
    from hico_skills.models import Skill

    # One token matches ("skill"), the other does not -> still a hit (no all-tokens-AND gate).
    s = Skill(
        "alpha-skill", "skill", "Alpha Skill", "Does alpha things.", "When testing alpha.", ""
    )
    assert [h.id for h in search([s], "skill nonexistentword")] == ["alpha-skill"]


def test_diacritics_are_folded():
    from hico_skills.models import Skill

    s = Skill("m", "skill", "Müller Report", "Über die Ausführung.", "Wenn Größe zählt.", "")
    assert search([s], "muller")[0].id == "m"  # ü folded to u
    assert search([s], "ausfuhrung")  # query folded matches folded description


def test_alias_bridges_synonyms():
    from hico_skills.models import Skill

    # "login" appears nowhere literally; it's an alias of authenticate/session (aliases.py).
    s = Skill(
        "auth", "skill", "Session Start", "Authenticate and load context.", "When to auth.", ""
    )
    other = Skill("z", "skill", "Other", "unrelated text", "unrelated", "")
    hits = search([other, s], "login")
    assert hits and hits[0].id == "auth"


def test_direct_match_outranks_alias_match():
    from hico_skills.models import Skill

    direct = Skill("d", "skill", "Authenticate Tool", "does auth", "authenticate here", "")
    alias = Skill("a", "skill", "Session Helper", "session things", "session start", "")
    assert search([direct, alias], "authenticate")[0].id == "d"


def test_hit_shape(store):
    h = search(store.all(), "alpha")[0]
    assert (h.id, h.type, h.name, h.when_to_use) == (
        "alpha-skill",
        "skill",
        "Alpha Skill",
        "When testing alpha.",
    )
