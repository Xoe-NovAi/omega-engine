# Context Engineering Protocol — Canonical Specification

**Version**: 1.0 | **Status**: Production-ready | **Source**: Node 1 (Omega Engine Alpha)

---

## Executive Summary

The Context Engineering Protocol (CEP) is a complete, framework-agnostic protocol for **maintaining coherent agent context across sessions, compactions, and handoffs**. It solves the fundamental problem that every agent framework hits: context degrades, compactions lose critical memory, handoffs between agents lose fidelity.

CEP consists of four interlocking components:

1. **Gnosis-Lock Ritual** — 9-step immutable pre-compaction protocol
2. **Pack Lifecycle State Machine** — `CAPTURED → REFLECTED → COMPACTED` with `reflection_status` as authoritative signal
3. **Dynamic Reflection via `question` Tool** — 3 core categories + unlimited session-specific questions
4. **Gnosis-Leash Injection Architecture** — Automatic context injection at session start + compaction

---

## 1. Gnosis-Lock Ritual — 9 Steps

**Purpose**: Capture full session state, evolution delta, and human gnosis before context compaction.

**Trigger**: End of every session, before `/compact`, or on shutdown.

### Step 0: Leash Check
- Check `identity.pending_pack` — if exists and not `REFLECTED`, refuse new pack
- Prevents stacking un-reflected packs (narrative loss)
- Override: `FORCE_PACK=1` (acknowledges narrative loss risk)

### Step 1: Capture Git State
- Branch, commit, short commit, dirty flag, status, recent commits (10)
- Saved to `gnosis/sessions/{session_id}_git_state.json`

### Step 2: Capture OpenCode Config
- Full `opencode.json` snapshot
- Saved to `gnosis/sessions/{session_id}_opencode_config.json`

### Step 3: Capture MCP Status
- `opencode mcp list --json` (5s timeout)
- Saved to `gnosis/sessions/{session_id}_mcp_status.json`

### Step 4: Capture System State
- Hostname, kernel, uptime, CPU model/governor/epp
- Memory/swap/zram stats, Ollama models
- Saved to `gnosis/sessions/{session_id}_system_state.json`

### Step 5: Capture Session Narrative (Template)
- Creates markdown template with sections:
  - Session Summary (auto-filled in Step 6.5)
  - Key Decisions (TODO)
  - Code Changes (auto-filled in Step 6.5)
  - Blockers & Open Questions (TODO)
  - Next Session Priorities (TODO)
  - Gnosis Gained (TODO)
- Saved to `gnosis/sessions/{session_id}_narrative.md`

### Step 6: Compute Evolution Delta
- Files changed, lines added/removed, new files, config changes
- Recent commits from git log
- Saved to `gnosis/evolution/evolution_{timestamp}.json`

### Step 6.5: Auto-Generate Narrative Summary
- Machine-fills Session Summary + Code Changes from Git State + Evolution Delta
- Human fields (Decisions, Gnosis) remain TODO for reflection
- Updates `narrative.md` in place

### Step 7: Update Persistent Identity
- Advances `session_count`, `current_session`, `pending_pack`
- Per-entity continuity map (`entities[entity]`)
- **Preserves living document fields** (`key_achievements`, `open_quests`) — extends, never resets
- Saved to `gnosis/identity/identity.json`

### Step 8: Create Session Manifest
- Links all artifacts (git_state, config, mcp, system, narrative, evolution)
- Sets `reflection_status: "captured"`, `ready_for_compaction: false`
- Saved to `gnosis/sessions/{session_id}_manifest.json`

### Step 9: Log Evolution Event
- Logs `SESSION_END` to evolution log with tags `ritual, session-end`
- Updates evolution index

---

## 2. Pack Lifecycle State Machine

```
CAPTURED (ritual complete, narrative TODO)
    ↓ [human reflection via `question` tool]
REFLECTED (narrative populated, `reflected_at` set, `ready_for_compaction: true`)
    ↓ [/compact runs]
COMPACTED (context compressed, narrative survives via injection)
```

**Authoritative Signal**: `reflection_status` in manifest (`captured` | `reflected`)

**Leash Enforcement**: Second `CAPTURED` blocked while previous is un-`REFLECTED` (Step 0)

**FORCE_PACK=1** override exists (acknowledges narrative loss risk)

---

## 3. Dynamic Reflection via `question` Tool

**Trigger**: Step 4b of ritual (after auto-fill, before manifest flip)

**Core Categories** (always asked):
1. **Decision** — What key decisions were made? What was rejected?
2. **Pattern** — What patterns emerged? What anti-patterns avoided?
3. **Gnosis** — What deep insights/corrections were learned?

**Session-Specific Questions** (0–10+):
- Generated from session context (blockers, decisions, surprises)
- No cap — adds as many as context demands

**Output**: Human answers written to `narrative.md` (replaces TODO sections)

**Step 4b Manifest Flip**:
```json
{
  "reflection_status": "reflected",
  "reflected_at": "2026-09-21T23:47:06Z",
  "ready_for_compaction": true,
  "pending_pack": null
}
```

---

## 4. Gnosis-Leash Injection Architecture

**Purpose**: Inject operating context into every session automatically.

### Injection Points

| Hook | When | What's Injected |
|------|------|-----------------|
| `experimental.chat.system.transform` | Every session start | WanderGround INDEX + The Well active rules + Operating rules |
| `experimental.session.compacting` | Before compaction | INDEX + The Well + Human narrative + Operating rules |

### Injection Content (Priority Order)

1. **WanderGround INDEX** (first 24 lines of `INDEX.md`)
   - Operating rules, domain weights, navigation

2. **The Well Active Records** (top-N, filtered by domain)
   - Session start: top-6, domains `["harness", "local_ai"]`
   - Compaction: top-8, domains `["harness", "local_ai"]`
   - Format: rule + kind + domain + pack + id

3. **Human Narrative** (compaction only)
   - Priority 1: Current session narrative (if `REFLECTED` + populated)
   - Priority 2: Latest `REFLECTED` pack fallback
   - **Never silent**: If none, injects `⚠️ GNOSIS-LOCK INCIDENT` + logs error

4. **Operating Rules** (always)
   - WanderGround INDEX rules (indented)
   - The Well active rules (formatted)
   - Appended to system prompt

### Narrative Lookup Logic (Priority)

1. Current session narrative (if `REFLECTED` + populated)
2. Latest `REFLECTED` pack on disk (most recent mtime)
2. **Never silent failure** — injects incident warning

### Well Injection Filtering

```javascript
// Session start: 6 records, domains ["harness", "local_ai"]
// Compaction: 8 records, domains ["harness", "local_ai"]
readWellForInjection(limit, domains) {
  // Load well.jsonl → filter active → filter domains → sort by recency → slice
}
```

---

## File Structure

```
gnosis/
├── identity/
│   └── identity.json              # Persistent identity (living document)
├── sessions/
│   ├── {session_id}_git_state.json
│   ├── {session_id}_opencode_config.json
│   ├── {session_id}_mcp_status.json
│   ├── {session_id}_system_state.json
│   ├── {session_id}_narrative.md  # Human narrative
│   ├── {session_id}_manifest.json # Manifest with reflection_status
│   └── {session_id}_evolution.json
├── evolution/
│   ├── evolution_log.jsonl        # Append-only event log
│   └── evolution_index.json       # Query index (by session/type/tag)
├── well/
│   ├── well.jsonl                 # Append-only corrections corpus
│   └── WISDOM.md                  # Rendered human view
└── leash/
    └── gnosis-leash.js            # OpenCode plugin (reference impl)
```

---

## Identity.json Schema

```json
{
  "entity": "Omega Engine Alpha Build Agent",
  "inception": "2026-09-08T00:00:00Z",
  "last_updated": "2026-09-21T23:47:06Z",
  "session_count": 42,
  "current_session": "session-2026-09-21T20-34-00Z",
  "pending_pack": "session-2026-09-21T20-34-00Z",
  "current_entity": "build",
  "current_machine": "ASUS ExpertBook P1503CVA (i7-13620H)",
  "federation_role": "Node 1 - Compute Vanguard",
  "partner_node": "HP Pavilion (Node 0 - Archival Bastion)",
  "core_principles": [...],
  "key_achievements": [...],      // LIVING DOCUMENT — extends, never resets
  "open_quests": [...],           // LIVING DOCUMENT — extends, never resets
  "entities": {
    "build": { "session_count": 30, "last_session": "...", "last_phase": "federation" },
    "cursor": { "session_count": 12, ... }
  }
}
```

---

## Evolution Log Schema

```json
{
  "event_id": "evt-20260921-203400-a1b2c3d4",
  "timestamp": "2026-09-21T20:34:00Z",
  "event_type": "SESSION_END",
  "event_type_label": "Session completed with compaction",
  "session_id": "session-2026-09-21T20-34-00Z",
  "description": "Pre-compaction ritual: End of session",
  "metadata": {
    "manifest": "gnosis/sessions/session-2026-09-21T20-34-00Z_manifest.json",
    "sessions": 42,
    "entity": "build",
    "channel": "cli",
    "phase": "federation"
  },
  "tags": ["ritual", "session-end"],
  "version": "1.0"
}
```

---

## Evolution Index Schema

```json
{
  "by_session": { "session-id": ["evt-...", "evt-..."] },
  "by_type": { "SESSION_END": ["evt-...", "evt-..."] },
  "by_tag": { "ritual": ["evt-...", "evt-..."] },
  "last_event": "evt-20260921-203400-a1b2c3d4",
  "total_events": 1247,
  "last_updated": "2026-09-21T20:34:00Z"
}
```

---

## Event Types

| Type | Label |
|------|-------|
| SESSION_START | New session begun |
| SESSION_END | Session completed with compaction |
| CONFIG_CHANGE | Config modified |
| CODE_CHANGE | Source code modified |
| DOC_UPDATE | Documentation created/updated |
| BENCHMARK | Performance benchmark recorded |
| BLOCKER | Blocker identified |
| BLOCKER_RESOLVED | Blocker resolved |
| DECISION | Strategic decision made |
| GNOSIS | Insight/learning captured |
| MILESTONE | Major milestone achieved |
| FEDERATION_EVENT | P2P federation event |
| AGENT_EVENT | Agent created/updated/migrated |
| MCP_EVENT | MCP server added/removed/configured |
| HARDWARE_EVENT | Hardware change/upgrade |
| KEY_ROTATION | API key rotated |
| HOOK_EVENT | OpenCode hook triggered |

---

## Integration with Omega Engine

### Required Files

```
omega-engine/
├── scripts/compaction/
│   ├── pre_compaction_ritual.sh      # 9-step ritual (executable)
│   ├── evolution_log.py              # Evolution log system
│   ├── opencode_hooks.py             # OpenCode hook handler
│   └── gnosis_leash_inject.py        # Injection logic (reference)
├── gnosis/
│   ├── identity/identity.json
│   ├── sessions/
│   ├── evolution/
│   └── well/
├── .opencode/
│   ├── plugins/gnosis-leash.js       # OpenCode plugin (reference)
│   └── skills/gnosis-lock/SKILL.md   # Reflection skill
└── Makefile                          # gnosis-lock, gnosis-stats, gnosis-ledger targets
```

### Make Targets

```makefile
gnosis-lock:           # CLI capture (auto-fills narrative Step 6.5)
gnosis-stats:          # Evolution log stats + timeline
gnosis-ledger:         # Pause Ledger (pack states + timestamps + leash)
gnosis-leash-status:   # Watchdog (plugin + leash + narrative + INDEX)
```

### OpenCode Hook Registration

```json
{
  "hook": {
    "opencode_hooks": {
      "pre_compact": "python3 scripts/compaction/opencode_hooks.py",
      "session_end": "python3 scripts/compaction/opencode_hooks.py"
    }
  }
}
```

### Plugin Registration

```json
{
  "plugin": ["gnosis-leash"]
}
```

---

## Watchdog: `gnosis-leash-status`

Verifies:
1. Plugin loaded (`gnosis-leash` in plugin list)
2. Plugin congruence (hooks registered)
3. Pack migration (no stuck CAPTURED packs)
4. Leash functional (pending_pack gated)
5. Narrative present (current or fallback)
6. INDEX injection active (first 24 lines present)

---

## License

Apache-2.0 — see parent repo LICENSE.