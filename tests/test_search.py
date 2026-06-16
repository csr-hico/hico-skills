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


def test_hit_shape(store):
    h = search(store.all(), "alpha")[0]
    assert (h.id, h.type, h.name, h.when_to_use) == (
        "alpha-skill",
        "skill",
        "Alpha Skill",
        "When testing alpha.",
    )
