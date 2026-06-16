from __future__ import annotations

from hico_skills.get import AGENT_SPAWN_DIRECTIVE, render_definition


def test_skill_body_verbatim(store):
    skill = store.get("alpha-skill")
    assert render_definition(skill) == "Alpha body."


def test_agent_gets_spawn_directive(store):
    agent = store.get("gamma-agent")
    out = render_definition(agent)
    assert out.startswith(AGENT_SPAWN_DIRECTIVE)
    assert out.endswith("Gamma agent body.")
