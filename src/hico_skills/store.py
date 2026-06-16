"""The only module that touches the filesystem: load, cache, and cheaply reload skills."""

from __future__ import annotations

from pathlib import Path

from .frontmatter import FrontmatterError, skill_from_text
from .models import Skill


def _slug(stem: str) -> str:
    return stem.strip().lower().replace(" ", "-")


class SkillStore:
    """In-memory cache over a directory of ``*.md`` skill/agent files.

    Tolerates a missing directory and invalid files (skips + reports them) so a bad
    contribution can never take the server down.
    """

    def __init__(self, skills_dir: Path | str):
        self.skills_dir = Path(skills_dir)
        self._skills: dict[str, Skill] = {}
        self._signature: tuple = ()

    def _dir_signature(self) -> tuple:
        if not self.skills_dir.is_dir():
            return ()
        return tuple(
            sorted(
                (p.name, p.stat().st_mtime_ns, p.stat().st_size)
                for p in self.skills_dir.glob("*.md")
            )
        )

    def load(self) -> tuple[int, list[tuple[Path, str]]]:
        """(Re)scan the directory and replace the cache atomically.

        Returns (loaded_count, [(path, error_message), ...]). Files whose stem starts
        with '_' (e.g. _TEMPLATE.md) are ignored.
        """
        skills: dict[str, Skill] = {}
        errors: list[tuple[Path, str]] = []
        if self.skills_dir.is_dir():
            for path in sorted(self.skills_dir.glob("*.md")):
                if path.stem.startswith("_"):
                    continue
                try:
                    skill = skill_from_text(
                        path.read_text(encoding="utf-8"), skill_id=_slug(path.stem)
                    )
                except (FrontmatterError, OSError, UnicodeDecodeError) as exc:
                    errors.append((path, str(exc)))
                    continue
                skills[skill.id] = skill
        self._skills = skills
        self._signature = self._dir_signature()
        return len(skills), errors

    def maybe_reload(self) -> bool:
        """Reload only if the directory signature changed since the last load."""
        if self._dir_signature() != self._signature:
            self.load()
            return True
        return False

    def all(self) -> list[Skill]:
        return sorted(self._skills.values(), key=lambda s: s.name.lower())

    def get(self, skill_id: str) -> Skill | None:
        return self._skills.get(skill_id)
