---
description: Search all past agent sessions (OpenCode, Claude Code, Qoder, Codex) for a term. Use before asking the user to repeat past context, or to find prior decisions, debugging sessions, and traps.
agent: build
---

Search the full session history for a term.

Invoke as `/recall <search-term-or-regex>`, or non-interactively as
`opencode run --command recall "<term>"`. Do not paraphrase this as free text like
“run the recall command with …”, because that can pass the whole sentence as the term.

**Step 1 — identify the search term.** If the invocation already supplies a term, use it
as-is. Otherwise it is usually the distinctive keyword(s) in the user's request — a file
name, an error string, a concept, a person's name. **Do not** search a whole sentence
verbatim: that matches nothing but the invocation itself. Extract the 1–3 distinctive
terms.

Examples:

| User says | Search for |
|---|---|
| "sessions with Humboldt in the title" | `Humboldt` |
| "what did we decide about the pin trap?" | `pin trap` |
| "where did we hit the WAL error?" | `WAL` |

**Step 2 — run this, with your extracted term substituted:**

```bash
ochist grep "<extracted-term>" --global --limit 10
```

Report the results verbatim, then stop.

Notes:
- `--global` is required. Without it the search is scoped to the current project and
  will look broken (return nothing) when run from an unrelated directory.
- The term is a **regex**, not a literal substring. Quote metacharacters if literal.
- If every hit is a `tool:` part rather than prose, that means the term only appears in
  command output, not conversation. Report that honestly rather than re-running.
- **A zero-result search is not proof of absence.** Confirm the scope: if you forgot
  `--global`, or the term differs from how it was actually written in the transcript
  (hyphenation, casing, abbreviation), you get a false negative. State which of these
  you checked.

After reporting, do NOT drill further unless asked. If the operator wants the full
transcript, suggest `ochist show <slug>`; for session IDs and structure, `ochist meta`.