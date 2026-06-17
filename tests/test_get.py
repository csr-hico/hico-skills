from __future__ import annotations

from hico_skills.get import AGENT_SPAWN_DIRECTIVE, render_definition


def test_skill_body_verbatim_when_no_resources(store):
    skill = store.get("alpha-skill")
    assert render_definition(skill) == "Alpha body."


def test_agent_gets_spawn_directive(store):
    agent = store.get("gamma-agent")
    out = render_definition(agent)
    assert out.startswith(AGENT_SPAWN_DIRECTIVE)
    assert out.endswith("Gamma agent body.")


def test_bundled_files_listed_in_definition(store):
    out = render_definition(store.get("beta-helper"))
    assert out.startswith("Beta body.")
    assert "## Bundled files" in out
    assert "`scripts/run.py`" in out and "`templates/out.txt`" in out
    assert "get_resource" in out
    assert "file:///skills/beta-helper/" in out
