from __future__ import annotations

from hico_skills.store import SkillStore

from .conftest import VALID_SKILL


def test_load_counts_valid_and_collects_errors(store):
    count = len(store.all())
    assert count == 3  # alpha, beta, gamma (template ignored; 3 invalid skipped)


def test_load_returns_error_list(skills_dir):
    s = SkillStore(skills_dir)
    loaded, errors = s.load()
    assert loaded == 3
    bad_names = {p.name for p, _ in errors}
    assert bad_names == {"missing-name.md", "bad-type.md", "no-frontmatter.md"}


def test_template_is_ignored(store):
    assert store.get("template") is None
    assert all(s.id != "_template" for s in store.all())


def test_get_known_and_unknown(store):
    assert store.get("alpha-skill") is not None
    assert store.get("does-not-exist") is None


def test_missing_dir_does_not_crash(tmp_path):
    s = SkillStore(tmp_path / "nope")
    loaded, errors = s.load()
    assert loaded == 0
    assert errors == []
    assert s.all() == []


def test_maybe_reload_only_when_changed(store, skills_dir):
    assert store.maybe_reload() is False
    (skills_dir / "delta-skill.md").write_text(
        VALID_SKILL.replace("Alpha", "Delta"), encoding="utf-8"
    )
    assert store.maybe_reload() is True
    assert store.get("delta-skill") is not None
