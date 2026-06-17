---
name: Conventional Commit Writer
description: >
  Turns a diff or a change summary into a clean Conventional Commits message: a type(scope)
  subject line under 72 chars, an imperative mood, and a concise body explaining the why.
when_to_use: When the user asks you to write or improve a git commit message.
---

# Conventional Commit Writer

Produce a commit message in Conventional Commits format.

1. Pick the type: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `build`, `ci`.
2. Subject: `type(scope): summary` - imperative, lowercase, no trailing period, <= 72 chars.
3. Body (optional): wrap at 72 cols; explain the *why*, not the *what* (the diff shows the what).
4. Footer (optional): `BREAKING CHANGE:` notes, issue refs.

Return only the message, ready to paste. Do not invent a scope if none is obvious.
