"""The only module that touches the filesystem: load, cache, and cheaply reload skills/agents.

Layout (Anthropic Agent-Skills style): one folder per item, with a manifest file plus any
bundled files (scripts, templates, references).

    skills/<id>/SKILL.md   + bundled files
    agents/<id>/AGENT.md   + bundled files

The directory the item lives in determines its type; the folder name is its id.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from .frontmatter import FrontmatterError, skill_from_text
from .models import AGENT, SKILL, Skill


@dataclass(frozen=True)
class Root:
    """One scanned root: a base directory, the type it yields, and its manifest filename."""

    base: Path
    type_: str
    manifest: str


def default_roots(skills_dir: Path | str, agents_dir: Path | str) -> tuple[Root, ...]:
    return (
        Root(Path(skills_dir), SKILL, "SKILL.md"),
        Root(Path(agents_dir), AGENT, "AGENT.md"),
    )


def _slug(name: str) -> str:
    return name.strip().lower().replace(" ", "-")


def _hidden(name: str) -> bool:
    return name.startswith("_") or name.startswith(".")


class SkillStore:
    """In-memory cache over one or more roots of ``<id>/<manifest>`` skill/agent folders.

    Tolerates missing roots and invalid items (skips + reports them) so a bad contribution can
    never take the server down.
    """

    def __init__(self, roots: tuple[Root, ...] | list[Root]):
        self.roots = tuple(roots)
        self._skills: dict[str, Skill] = {}
        self._signature: tuple = ()

    def _item_dirs(self) -> list[tuple[Root, Path]]:
        out: list[tuple[Root, Path]] = []
        for root in self.roots:
            if not root.base.is_dir():
                continue
            for item_dir in sorted(root.base.iterdir()):
                if item_dir.is_dir() and not _hidden(item_dir.name):
                    out.append((root, item_dir))
        return out

    @staticmethod
    def _bundled_files(item_dir: Path, manifest: str) -> list[Path]:
        """Every file under the item dir except the manifest and hidden/dunder files."""
        files = []
        for p in sorted(item_dir.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(item_dir)
            if any(_hidden(part) for part in rel.parts):
                continue
            if rel.as_posix() == manifest:
                continue
            files.append(p)
        return files

    def _dir_signature(self) -> tuple:
        sig: list[tuple] = []
        for _root, item_dir in self._item_dirs():
            for p in sorted(item_dir.rglob("*")):
                if p.is_file():
                    st = p.stat()
                    sig.append((str(p), st.st_mtime_ns, st.st_size))
        return tuple(sig)

    def load(self) -> tuple[int, list[tuple[Path, str]]]:
        """(Re)scan all roots and replace the cache atomically.

        Returns (loaded_count, [(path, error_message), ...]). Folders whose name starts with
        '_' or '.' are ignored. A folder missing its manifest is reported, not fatal.
        """
        skills: dict[str, Skill] = {}
        errors: list[tuple[Path, str]] = []
        for root, item_dir in self._item_dirs():
            manifest = item_dir / root.manifest
            if not manifest.is_file():
                errors.append((manifest, f"missing {root.manifest}"))
                continue
            try:
                skill = skill_from_text(
                    manifest.read_text(encoding="utf-8"),
                    skill_id=_slug(item_dir.name),
                    type_=root.type_,
                )
            except (FrontmatterError, OSError, UnicodeDecodeError) as exc:
                errors.append((manifest, str(exc)))
                continue
            resources = tuple(
                p.relative_to(item_dir).as_posix()
                for p in self._bundled_files(item_dir, root.manifest)
            )
            skills[skill.id] = replace(skill, dir=item_dir, resources=resources)
        self._skills = skills
        self._signature = self._dir_signature()
        return len(skills), errors

    def maybe_reload(self) -> bool:
        """Reload only if any root's file signature changed since the last load."""
        if self._dir_signature() != self._signature:
            self.load()
            return True
        return False

    def all(self) -> list[Skill]:
        return sorted(self._skills.values(), key=lambda s: s.name.lower())

    def get(self, skill_id: str) -> Skill | None:
        return self._skills.get(skill_id)

    def resource_path(self, skill_id: str, rel_path: str) -> Path | None:
        """Resolve a bundled-file request to an absolute path, or None.

        Security boundary: only files we enumerated as `resources` for this item are returnable.
        That alone defeats path traversal (``../`` escapes never appear in the enumerated set),
        and we additionally re-check containment after resolving symlinks.
        """
        skill = self._skills.get(skill_id)
        if skill is None or skill.dir is None:
            return None
        base = skill.dir.resolve()
        target = (base / rel_path).resolve()
        if not target.is_relative_to(base):
            return None
        rel = target.relative_to(base).as_posix()
        if rel not in skill.resources or not target.is_file():
            return None
        return target
