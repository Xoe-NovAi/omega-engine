# Quarantine — stray Python backup files (2026-09-28)

## What these are

Editor/CI-generated copies of live source files that were left sitting *inside
the Python package tree*. They are untracked in git and were never intended to
ship:

| File | Bytes | Notes |
|------|-------|-------|
| `mcp_servers/omega_hub/hub_tools/tools.py.bak` | — | older copy of `hub_tools/tools.py` |
| `mcp_servers/omega_hub/hub_tools/tools.py.fixbak` | — | **TRUNCATED — does not parse.** `ast.parse` fails with `unterminated triple-quoted string literal` (line ~3496). Not a usable reference. |
| `mcp_servers/omega_hub/hub_tools/tools.py.backup2` | — | second older copy; contains the retired `hivemind_post_context` and the stale `_extended_sessions` consumer code |
| `mcp_servers/omega_hub/state.py.fixbak` | — | older copy of `state.py`; still defines `_extended_sessions`, `_extended_sessions_lock`, `EXTENDED_SESSIONS_FILE` |

## Why they were moved, not deleted

Two concrete harms, both observed during the 2026-09-27/28 seam work:

1. **Grep poisoning.** A repo-wide search for a symbol returns hits from these
   files. During the `github_bridge` sweep these backups produced matches for
   `hivemind_post_context` and `_extended_sessions` that had to be filtered out
   by hand. Any future audit or gate that greps the tree without excluding
   `*.bak` / `*.fixbak` will draw false conclusions from dead code.

2. **False provenance.** `tools.py.fixbak` defines functions that no longer exist
   in the live module. A reader who opens it reasonably concludes those symbols
   are still present. During this work it was briefly mistaken for a valid
   reference; it does not parse.

They are **retained, not deleted** — the Architect decides. `tools.py.bak` and
`state.py.fixbak` are the only record of the pre-consolidation tool surface,
which is the evidence base for the 26→4 Hivemind consolidation audit.

## Scope

Only the four files in **Ma'at's workstream** (`mcp_servers/omega_hub/**`) were
moved. Backup files belonging to other workstreams — notably ~55 under
`src/omega/**` (Carmack's) and 3 under `config/wads/_omega_default/entities/` —
were **left in place**. They are the owning agent's call, not this workstream's.

Full repo-wide inventory is reported in the MaKaLi facet return of 2026-09-28.

## Handling

Do not import from anything in this directory. Do not add it to a package path.
If a symbol is needed from a pre-consolidation state, read the file for
reference only, and confirm the live source before relying on it.
