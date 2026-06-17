"""Render the full definition body that the MCP `get` tool returns. Pure."""

from __future__ import annotations

from .models import AGENT, Skill

AGENT_SPAWN_DIRECTIVE = (
    "This is an AGENT definition, not a plain instruction. Run it as an isolated subtask: "
    "spawn a fresh sub-agent with its own context using the instructions below; do not inline "
    "them into the current thread. If your host has no sub-agent mechanism, follow them inline.\n\n"
)


def _resources_section(skill: Skill) -> str:
    """A trailing note listing bundled files and how to fetch them (tool or MCP resource)."""
    if not skill.resources:
        return ""
    kind = "agents" if skill.type == AGENT else "skills"
    lines = [
        "\n\n---\n## Bundled files",
        f"This {skill.type} ships the files below. Fetch any with the `get_resource` tool "
        f'(`id="{skill.id}"`, `path="<path>"`) or read the MCP resource '
        f"`file:///{kind}/{skill.id}/<path>`:",
    ]
    lines += [f"- `{rel}`" for rel in skill.resources]
    return "\n".join(lines)


def render_definition(skill: Skill) -> str:
    """Full body. Agents get the spawn-as-subtask directive; bundled files are appended."""
    prefix = AGENT_SPAWN_DIRECTIVE if skill.type == AGENT else ""
    return prefix + skill.body + _resources_section(skill)
