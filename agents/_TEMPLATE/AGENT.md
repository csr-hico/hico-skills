---
name: Human Readable Agent Name
description: >
  One or two sentences describing what this agent does and what it returns. This is what the LLM
  and the OnePager both see. An agent runs as an isolated subtask, not inline.
when_to_use: When the task needs an isolated subtask (heavy read/search work) and only the
  conclusion should return to the main context.
tools: [Read, Grep, Glob]   # optional: tools the agent should be scoped to
# model: claude-opus-4-8     # optional: suggested model
---

# Agent Name (isolated subtask)

The body is delivered to the LLM prefixed with a directive to run it as a fresh, isolated
subtask. Write it as direct instructions to that sub-agent.

Bundling files works exactly like skills: drop scripts/templates/references in this folder; they
are fetchable via `get_resource(id="<folder-name>", path="...")` or
`file:///agents/<folder-name>/...`, and `get(id)` lists them automatically.

Folders/files starting with `_` or `.` are ignored.
