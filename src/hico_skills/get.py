"""Render the full definition body that the MCP `get` tool returns. Pure."""

from __future__ import annotations

from .models import AGENT, Skill

AGENT_SPAWN_DIRECTIVE = (
    "This is an AGENT definition, not a plain instruction. Run it as an isolated subtask: "
    "spawn a fresh sub-agent with its own context using the instructions below; do not inline "
    "them into the current thread. If your host has no sub-agent mechanism, follow them inline.\n\n"
)


def render_definition(skill: Skill) -> str:
    """Full body. Agents are prefixed with the spawn-as-isolated-subtask directive."""
    if skill.type == AGENT:
        return AGENT_SPAWN_DIRECTIVE + skill.body
    return skill.body
