---
name: Human Readable Name
description: >
  One or two sentences describing what this skill does. This exact text is what the LLM sees via
  the MCP `get` tool AND what the OnePager accordion shows. Make it specific.
when_to_use: When the user asks for X, or when condition Y holds.   # or use `triggers:` (a list)
# triggers:            # optional alternative to when_to_use
#   - phrase one
#   - phrase two
---

# Instructions

The body is the actual skill content the LLM receives via `get`. Write it as direct instructions.

## Bundling files (scripts, templates, references)

Put any supporting files next to this SKILL.md, in this folder. They are auto-discovered and
exposed to MCP clients two ways:

- the `get_resource` tool: `get_resource(id="<this-folder-name>", path="scripts/example.py")`
- as an MCP resource: `file:///skills/<this-folder-name>/scripts/example.py`

`get(id)` lists them under a "Bundled files" section automatically, so just reference them by
path in your instructions (e.g. "run `scripts/example.py`").

Notes:
- The folder name is the id; the `type` is implied by the directory (skills/ -> skill).
- Folders (and files) whose name starts with `_` or `.` are ignored by the loader.
- Invalid items are skipped and reported; a bad contribution never crashes the server.
