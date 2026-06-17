from __future__ import annotations

import pytest

from hico_skills.frontmatter import FrontmatterError, skill_from_text, split_frontmatter

from .conftest import MISSING_NAME, NO_FRONTMATTER, VALID_AGENT, VALID_SKILL, VALID_SKILL2


def test_valid_skill_parsed():
    s = skill_from_text(VALID_SKILL, skill_id="alpha-skill")
    assert s.type == "skill"
    assert s.name == "Alpha Skill"
    assert s.description.startswith("Does alpha")
    assert s.when_to_use == "When testing alpha."
    assert s.body == "Alpha body."


def test_triggers_collapse_into_when_to_use():
    s = skill_from_text(VALID_SKILL2, skill_id="beta-helper")
    assert s.when_to_use == "beta task, widget work"


def test_valid_agent_type_and_tools():
    s = skill_from_text(VALID_AGENT, skill_id="gamma-agent", type_="agent")
    assert s.type == "agent"
    assert s.tools == ("Read", "Grep")


def test_missing_name_raises():
    with pytest.raises(FrontmatterError):
        skill_from_text(MISSING_NAME, skill_id="x")


def test_missing_description_raises():
    text = "---\nname: Only Name\ntype: skill\n---\nbody"
    with pytest.raises(FrontmatterError):
        skill_from_text(text, skill_id="x")


def test_bad_type_arg_raises():
    # type comes from the loader (the root dir); an unknown one is a programming error.
    with pytest.raises(FrontmatterError):
        skill_from_text(VALID_SKILL, skill_id="x", type_="notathing")


def test_no_frontmatter_raises_on_validation():
    # split is lenient ({}, text); skill_from_text rejects the missing name.
    meta, body = split_frontmatter(NO_FRONTMATTER)
    assert meta == {}
    with pytest.raises(FrontmatterError):
        skill_from_text(NO_FRONTMATTER, skill_id="x")


def test_malformed_yaml_raises_frontmatter_error():
    bad = "---\nname: x\n: : :\n bad indent\n---\nbody"
    with pytest.raises(FrontmatterError):
        split_frontmatter(bad)


def test_unclosed_frontmatter_raises():
    with pytest.raises(FrontmatterError):
        split_frontmatter("---\nname: x\nno closing delimiter\n")


def test_default_type_is_skill():
    text = "---\nname: NoType\ndescription: has no explicit type\n---\nbody"
    s = skill_from_text(text, skill_id="x")
    assert s.type == "skill"
