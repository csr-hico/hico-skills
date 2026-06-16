---
name: Human Readable Name
description: >
  One or two sentences describing what this skill/agent does. This exact text is what the LLM
  sees via the MCP `get` tool AND what the OnePager accordion shows. Make it specific.
type: skill            # "skill" (instructions for the current context) or "agent" (isolated subtask)
when_to_use: When the user asks for X, or when condition Y holds.   # or use `triggers:` (a list)
# triggers:            # optional alternative to when_to_use
#   - phrase one
#   - phrase two
# tools: [Read, Grep]  # optional: tools an agent should be scoped to
# model: claude-opus-4-8   # optional: suggested model for an agent
---

# Instructions

The body is the actual skill/agent content the LLM receives. Write it as direct instructions.

Files whose name starts with `_` (like this one) are ignored by the loader.
