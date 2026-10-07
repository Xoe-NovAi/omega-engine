# GNOSIS-LEASH PLUGIN

**File:** `~/.config/opencode/plugins/gnosis-leash.js`

## Hooks
- `session.created` → SESSION_START to timeline
- `session.idle` → SESSION_IDLE
- `session.compacted` → SESSION_COMPACTED
- `experimental.session.compacting` → **INJECTS:**
  - WanderGround INDEX rules (36 lines, first 24)
  - **The Well active rules** (top-6 harness/local_ai at session start, top-8 at compaction)
  - **Human narrative** (readLatestNarrative → current → fallback to latest REFLECTED pack)
  - **LOUD FAILURE** if no narrative: `⚠️ GNOSIS-LOCK INCIDENT` injected + `gnosis-errors.jsonl`
- `experimental.chat.system.transform` → **APPENDS:**
  - WanderGround operating rules (indented)
  - **The Well active rules** (top-6 harness/local_ai, formatted)

## NO SILENT FAILURES
Compaction without narrative = incident injected + degraded watchdog.
