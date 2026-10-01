# M15 Sovereign Continuity — Technical Specification

**Note**: M15 integration is a **new feature**, not a fix. It belongs in Phase 4 (post-reconstruction), not Phase 2. Carmack's discipline: "split first, fix second."

## Purpose

Anchor agent cognition across Hub restarts. Without M15, every Hub restart resets agent awareness to zero — agents lose memory of prior sessions.

## Implementation

### Startup Hydration (concurrent in `_init_services`)

1. Read `.opencode/anchored-summary.md`
2. Read `data/entities/{active_entity}/workspace/session_gnosis.md`
3. Populate Hub's `ContinuityState` in memory
4. Signal `init_event.set()` — tools can now execute with full context

### Shutdown Preservation (block exit)

1. Harvest session logs from Hub memory
2. Run through SoulDistiller pipeline (L1 → L2 → L3)
3. Atomic write: `.tmp` → `os.replace` to `session_gnosis.md` and `soul.yaml`

## M12 Atomic Write Pattern

```python
await anyio.Path(tmp_file).write_text(content)
await anyio.to_thread.run_sync(os.replace, str(tmp_file), str(final_file))
```

Prevents file corruption on crash. The `.tmp` file is written completely before the atomic `os.replace` swaps it into place.
