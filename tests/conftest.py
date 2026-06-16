from __future__ import annotations

import pytest

from hico_skills.config import load_settings
from hico_skills.store import SkillStore

VALID_SKILL = """---
name: Alpha Skill
description: Does alpha things for testing.
type: skill
when_to_use: When testing alpha.
---
Alpha body."""

VALID_SKILL2 = """---
name: Beta Helper
description: Beta helper that mentions widget in its description.
type: skill
triggers:
  - beta task
  - widget work
---
Beta body."""

VALID_AGENT = """---
name: Gamma Agent
description: An isolated agent for gamma.
type: agent
when_to_use: When gamma must run as a subtask.
tools: [Read, Grep]
---
Gamma agent body."""

MISSING_NAME = """---
description: no name here
type: skill
---
body"""

BAD_TYPE = """---
name: Bad Type
description: has an invalid type
type: notathing
---
body"""

NO_FRONTMATTER = "Just a markdown file with no frontmatter at all."


@pytest.fixture
def skills_dir(tmp_path):
    d = tmp_path / "skills"
    d.mkdir()
    (d / "alpha-skill.md").write_text(VALID_SKILL, encoding="utf-8")
    (d / "beta-helper.md").write_text(VALID_SKILL2, encoding="utf-8")
    (d / "gamma-agent.md").write_text(VALID_AGENT, encoding="utf-8")
    (d / "missing-name.md").write_text(MISSING_NAME, encoding="utf-8")
    (d / "bad-type.md").write_text(BAD_TYPE, encoding="utf-8")
    (d / "no-frontmatter.md").write_text(NO_FRONTMATTER, encoding="utf-8")
    (d / "_TEMPLATE.md").write_text(MISSING_NAME, encoding="utf-8")  # underscore -> ignored
    return d


@pytest.fixture
def store(skills_dir):
    s = SkillStore(skills_dir)
    s.load()
    return s


@pytest.fixture
def settings(skills_dir):
    # Auth disabled (no OIDC_ISSUER) so tools are callable in-process. frontend_dir defaults
    # to the repo's frontend/ directory.
    env = {
        "SKILLS_DIR": str(skills_dir),
        "MCP_REQUIRED_GROUP": "",
        "PUBLIC_BASE_URL": "https://example.test",
    }
    return load_settings(env)
