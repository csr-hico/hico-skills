from __future__ import annotations

from hico_skills.guidance import discovery_text


def test_discovery_text_instructs_search_and_get():
    t = discovery_text().lower()
    assert "search" in t
    assert "get(" in t or "`get`" in t or "get(id)" in t
    assert "agent" in t
    assert "skill library" in t


def test_discovery_text_nonempty():
    assert len(discovery_text()) > 100
