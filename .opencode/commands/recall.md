---
description: Search all past agent sessions (OpenCode, Claude Code, Qoder, Codex) for a term. Use before asking the user to repeat past context.
agent: build
---

Search the full session history. $ARGUMENTS is the search term (regex accepted).

Run exactly this and report the results verbatim, then stop:

```bash
ochist grep "$ARGUMENTS" --global --limit 10
```

Notes:
- `--global` is required. Without it the search is scoped to the current project and
  will look broken (return nothing) when run from an unrelated directory.
- The term is a **regex**, not a literal substring.
- If results are returned but the top hits are `tool:` parts, re-run narrowed to prose:
  `ochist grep "$ARGUMENTS" --global --limit 10 --json`

After reporting, do NOT drill further unless asked. If the operator wants the full
transcript, suggest `ochist show <slug>` next.