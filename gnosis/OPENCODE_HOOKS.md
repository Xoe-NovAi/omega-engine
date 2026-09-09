# OpenCode Hooks — Status & Forward-Compat Reference

> ## ⚠️ STATUS: HOOKS NOT SUPPORTED (OpenCode 1.18.x — verified 2026-09-09)
>
> OpenCode v1.18 does **not** implement a hooks/lifecycle-event system:
> - The `hooks` key is absent from the config schema (`https://opencode.ai/config.json`).
> - `opencode debug config` ignores it; no hook code exists upstream.
> - There is **no CLI compaction** either — `opencode compact` is not a real
>   subcommand (it treats "compact" as a project path). `/compact` is TUI-only.
>
> **Working alternative (adopted on Node 1):**
> - `gnosis-lock "reason"` (shell function, `~/.bash_aliases`) runs the 8-step
>   ritual from any terminal tab while OpenCode stays open.
> - `make gnosis-lock REASON="..."` — same via make.
> - Full usage: `docs/GNOSIS_USAGE.md`.

---

## Forward-compatible piece: `opencode_hooks.py`

`scripts/compaction/opencode_hooks.py` is a tested handler that routes lifecycle
events (`pre_compact`, `session_end`, `post_task`, …) to the ritual or a
lightweight `HOOK_EVENT` log. It works when invoked manually:

```bash
OPENCODE_HOOK_TYPE=pre_compact OPENCODE_SESSION_ID=demo OPENCODE_AGENT_NAME=build \
  python3 scripts/compaction/opencode_hooks.py
```

If OpenCode adds hooks in a future version, the integration to re-enable is:

```jsonc
"hooks": {
  "pre_compact": { "command": ["/path/to/opencode_hooks.py"], "timeout": 120000 },
  "session_end": { "command": ["/path/to/opencode_hooks.py"], "timeout": 120000 }
}
```

Do not rely on it today. The ritual itself (Step 9) now logs a `SESSION_END`
event to the evolution log on every run — that is the current, reliable record.

---

*Part of Gnosis Lock Protocol v1.0. Trimmed 2026-09-09 from speculative full
spec to a status stub (doc consolidation).*