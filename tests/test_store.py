from __future__ import annotations

from hico_skills.store import SkillStore, default_roots

from .conftest import VALID_AGENT, VALID_SKILL


def test_load_counts_valid_and_collects_errors(store):
    assert len(store.all()) == 3  # alpha, beta, gamma (template ignored; 3 invalid skipped)


def test_load_returns_error_list(skills_dir, agents_dir):
    s = SkillStore(default_roots(skills_dir, agents_dir))
    loaded, errors = s.load()
    assert loaded == 3
    bad = {p.parent.name for p, _ in errors}
    assert bad == {"missing-name", "no-frontmatter", "no-manifest"}


def test_template_is_ignored(store):
    assert store.get("template") is None
    assert all(s.id != "_template" for s in store.all())


def test_type_comes_from_root_directory(store):
    assert store.get("alpha-skill").type == "skill"
    assert store.get("gamma-agent").type == "agent"


def test_get_known_and_unknown(store):
    assert store.get("alpha-skill") is not None
    assert store.get("does-not-exist") is None


def test_skills_sort_before_agents(tmp_path):
    skills = tmp_path / "skills"
    agents = tmp_path / "agents"
    (skills / "zzz-skill").mkdir(parents=True)
    (skills / "zzz-skill" / "SKILL.md").write_text(VALID_SKILL, encoding="utf-8")
    (agents / "aaa-agent").mkdir(parents=True)
    (agents / "aaa-agent" / "AGENT.md").write_text(VALID_AGENT, encoding="utf-8")
    s = SkillStore(default_roots(skills, agents))
    s.load()
    # skill comes first even though "aaa" < "zzz" alphabetically
    assert [x.id for x in s.all()] == ["zzz-skill", "aaa-agent"]


def test_missing_dirs_do_not_crash(tmp_path):
    s = SkillStore(default_roots(tmp_path / "no-skills", tmp_path / "no-agents"))
    loaded, errors = s.load()
    assert loaded == 0
    assert errors == []
    assert s.all() == []


def test_maybe_reload_only_when_changed(store, skills_dir):
    assert store.maybe_reload() is False
    (skills_dir / "delta-skill").mkdir()
    (skills_dir / "delta-skill" / "SKILL.md").write_text(
        VALID_SKILL.replace("Alpha", "Delta"), encoding="utf-8"
    )
    assert store.maybe_reload() is True
    assert store.get("delta-skill") is not None


def test_bundled_files_discovered(store):
    assert store.get("beta-helper").resources == ("scripts/run.py", "templates/out.txt")
    assert store.get("alpha-skill").resources == ()


def test_resource_path_resolves_bundled_file(store):
    p = store.resource_path("beta-helper", "scripts/run.py")
    assert p is not None and p.is_file()
    assert p.read_text() == "print('hi')\n"


def test_resource_path_rejects_manifest_and_unknowns(store):
    assert store.resource_path("beta-helper", "SKILL.md") is None  # manifest is not a resource
    assert store.resource_path("beta-helper", "nope.txt") is None
    assert store.resource_path("does-not-exist", "scripts/run.py") is None


def test_resource_path_blocks_traversal(store):
    assert store.resource_path("beta-helper", "../alpha-skill/SKILL.md") is None
    assert store.resource_path("beta-helper", "../../etc/passwd") is None
