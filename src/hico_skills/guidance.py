"""The instruction text that tells an LLM to discover + use this library. Pure, testable.

Exposed two ways over MCP: as a prompt (`use_skill_library`) the host can inject, and as a
resource (`guide://usage`) clients can read.
"""

from __future__ import annotations

GUIDE_URI = "guide://usage"


def discovery_text() -> str:
    return (
        "# HICO Skill Library\n\n"
        "You are connected to the HICO Skill Library MCP server. It hosts reusable **skills** and "
        "**agent** definitions. Use it instead of reinventing solutions you could look up here.\n\n"
        "Whenever a task might match a skill, do this before improvising:\n\n"
        "1. Call the `search` tool with a short query describing the task "
        '(e.g. `search(query="write a git commit")`). Leave `query` empty to browse everything; '
        'pass `type="agent"` or `type="skill"` to filter.\n'
        "2. Pick the best hit and call `get(id)` to load its full instructions.\n"
        "3. Follow the returned definition. If it is an **agent** (its body starts with a spawn "
        "directive), run it as an isolated subtask in a fresh context rather than inlining it.\n\n"
        "Prefer a library skill over guessing. If nothing fits, proceed normally."
    )
