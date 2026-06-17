from __future__ import annotations

import pytest

from hico_skills.config import load_settings
from hico_skills.store import SkillStore, default_roots

VALID_SKILL = """---
name: Alpha Skill
description: Does alpha things for testing.
when_to_use: When testing alpha.
---
Alpha body."""

VALID_SKILL2 = """---
name: Beta Helper
description: Beta helper that mentions widget in its description.
triggers:
  - beta task
  - widget work
---
Beta body."""

VALID_AGENT = """---
name: Gamma Agent
description: An isolated agent for gamma.
when_to_use: When gamma must run as a subtask.
tools: [Read, Grep]
---
Gamma agent body."""

MISSING_NAME = """---
description: no name here
---
body"""

NO_FRONTMATTER = "Just a markdown file with no frontmatter at all."


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def roots_base(tmp_path):
    """A skills/ + agents/ tree: 3 valid items, 3 invalid, 1 ignored, 1 with bundled files."""
    skills = tmp_path / "skills"
    agents = tmp_path / "agents"
    _write(skills / "alpha-skill" / "SKILL.md", VALID_SKILL)
    _write(skills / "beta-helper" / "SKILL.md", VALID_SKILL2)
    _write(skills / "beta-helper" / "scripts" / "run.py", "print('hi')\n")
    _write(skills / "beta-helper" / "templates" / "out.txt", "TPL\n")
    _write(agents / "gamma-agent" / "AGENT.md", VALID_AGENT)
    # invalid items (skipped + reported), keyed by their folder name:
    _write(skills / "missing-name" / "SKILL.md", MISSING_NAME)
    _write(skills / "no-frontmatter" / "SKILL.md", NO_FRONTMATTER)
    _write(skills / "no-manifest" / "notes.txt", "no SKILL.md here")
    # ignored (underscore-prefixed folder):
    _write(skills / "_TEMPLATE" / "SKILL.md", MISSING_NAME)
    return tmp_path, skills, agents


@pytest.fixture
def skills_dir(roots_base):
    return roots_base[1]


@pytest.fixture
def agents_dir(roots_base):
    return roots_base[2]


@pytest.fixture
def store(skills_dir, agents_dir):
    s = SkillStore(default_roots(skills_dir, agents_dir))
    s.load()
    return s


@pytest.fixture
def settings(skills_dir, agents_dir):
    # Auth disabled (no OIDC_ISSUER) so tools are callable in-process. frontend_dir defaults
    # to the repo's frontend/ directory.
    env = {
        "SKILLS_DIR": str(skills_dir),
        "AGENTS_DIR": str(agents_dir),
        "MCP_REQUIRED_GROUP": "",
        "PUBLIC_BASE_URL": "https://example.test",
    }
    return load_settings(env)
