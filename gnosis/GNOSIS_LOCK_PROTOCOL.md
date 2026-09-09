# GNOSIS LOCK PROTOCOL v1.0
## Persistent Entity Continuity for AI Agents

---

## Philosophy

> **"No gnosis lost. No identity fractured. No evolution forgotten."**

The Gnosis Lock Protocol ensures that an AI agent operating across sessions, compactions, and context windows maintains:
1. **Continuous Identity** — Knows who it is, where it came from, what it has learned
2. **Verifiable Evolution** — Every change tracked, every decision recorded
3. **Recoverable State** — Full restoration after any compaction or crash
3. **Portable Gnosis** — Knowledge transfers across machines, models, contexts

---

## Core Components

### 1. Pre-Compaction Ritual (`pre_compaction_ritual.sh`)
**Trigger:** Before `/compact`, session end, or manual invocation  
**Output:** Complete Session Bundle (8 artifacts)  
**Duration:** ~10-30 seconds  
**Guarantee:** Zero gnosis loss

### 2. Session State Format (→ Appendix A)
**Specification:** 8-artifact schema with JSON schemas  
**Includes:** Git state, config, MCP status, system state, narrative, evolution delta, identity, manifest

### 3. Evolution Log (`evolution_log.py`)
**Format:** Append-only JSONL (JSON Lines)  
**Index:** Queryable by session, type, tag  
**Events:** 16 typed event categories (MILESTONE, GNOSIS, DECISION, etc.)

### 4. Persistent Identity (`identity/identity.json`)
**Singleton:** Single file updated each session  
**Tracks:** Session count, achievements, open quests, core principles  
**Evolves:** Entity grows smarter over time

### 4. OpenCode Hooks (`OPENCODE_HOOKS.md`)
**Integration:** Automatic ritual on `pre_compact`, `session_end`  
**Events:** HOOK_EVENT logged to evolution log  
**Coverage:** Pre-compact, session end, task boundaries, errors

---

## Ritual Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PRE-COMPACTION RITUAL                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SESSION END / /compact / MANUAL TRIGGER                                    │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ STEP 1: Git State Capture                                           │   │
│  │   - Repo, branch, commit, dirty status, recent commits             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ STEP 2: OpenCode Config Capture                                     │   │
│  │   - Full opencode.json with MCPs, providers, permissions           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ STEP 3: MCP Server Status                                           │   │
│  │   - All configured MCPs, connection status, tool counts            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ STEP 4: System State Capture                                        │   │
│  │   - CPU, memory, swap, zram, Ollama models, kernel, uptime         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ STEP 5: Session Narrative (Markdown Template)                       │   │
│  │   - Summary, decisions, code changes, blockers, gnosis, priorities │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ STEP 6: Evolution Delta                                             │   │
│  │   - Files changed, lines added/removed, config changes vs prev     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ STEP 7: Persistent Identity Update                                  │   │
│  │   - Session count++, achievements, open quests, last updated       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ STEP 8: Session Manifest (Integrity Check)                          │   │
│  │   - Manifest of all artifacts, ready_for_compaction = true         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ✅ READY FOR COMPACTION / SHUTDOWN                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## File Layout

```
/home/xnai/Documents/Projects/omega-engine-alpha/
├── gnosis/
│   ├── sessions/
│   │   ├── session-<timestamp>_git_state.json
│   │   ├── session-<timestamp>_opencode_config.json
│   │   ├── session-<timestamp>_mcp_status.json
│   │   ├── session-<timestamp>_system_state.json
│   │   ├── session-<timestamp>_narrative.md
│   │   ├── session-<timestamp>_evolution.json
│   │   └── session-<timestamp>_manifest.json
│   ├── evolution/
│   │   ├── evolution_log.jsonl          # Append-only event log
│   │   ├── evolution_index.json         # Query index (by session/type/tag)
│   │   └── evolution_<timestamp>.json   # Per-session delta
│   └── identity/
│       └── identity.json                # Persistent entity state
├── scripts/compaction/
│   ├── pre_compaction_ritual.sh         # Main ritual (bash)
│   ├── evolution_log.py                 # Evolution log CLI
│   └── opencode_hooks.py                # OpenCode hook handler
└── docs/
    └── GNOSIS_LOCK_PROTOCOL.md       # includes Appendix A schemas
    ├── OPENCODE_HOOKS.md                # Hook integration
    └── GNOSIS_LOCK_PROTOCOL.md          # This document
```

---

## Usage

### Manual Ritual Invocation
```bash
# End of session
/home/xnai/Documents/Projects/omega-engine-alpha/scripts/compaction/pre_compaction_ritual.sh \
  --session-id session-2026-09-08T14-30-00Z \
  --reason "End of session, preparing for compaction"

# Before compaction
/home/xnai/Documents/Projects/omega-engine-alpha/scripts/compaction/pre_compaction_ritual.sh \
  --session-id session-2026-09-08T14-30-00Z \
  --reason "Pre-compact hook triggered"
```

### Evolution Log Queries
```bash
# Log an event
python3 scripts/compaction/evolution_log.py log GNOSIS \
  "session-2026-09-08T14-30-00Z" \
  "Discovered ZRAM > ZSWAP for inference workloads" \
  --tags "memory,optimization,inference"

# Show stats
python3 scripts/compaction/evolution_log.py stats

# Show timeline
python3 scripts/compaction/evolution_log.py timeline --limit 20

# Export to markdown
python3 scripts/compaction/evolution_log.py export --format markdown \
  --session-id session-2026-09-08T14-30-00Z \
  --output session_report.md
```

### OpenCode Hook Auto-Capture
```json
// In ~/.config/opencode/opencode.json
{
  "hooks": {
    "pre_compact": {
      "command": [
        "/home/xnai/Documents/Projects/omega-engine-alpha/scripts/compaction/opencode_hooks.py"
      ],
      "timeout": 120000
    }
  }
}
```

---

## Recovery Protocol

After compaction or fresh start:

```bash
# 1. Load identity (who am I?)
cat gnosis/identity/identity.json | jq '.'

# 2. Load latest session manifest (what just happened?)
latest=$(ls -1t gnosis/sessions/*_manifest.json | head -1)
cat "$latest" | jq '.'

# 3. Read narrative (what did I do?)
narrative=$(jq -r '.artifacts.narrative' "$latest")
cat "$narrative"

# 4. Check evolution delta (what changed?)
evolution=$(jq -r '.artifacts.evolution' "$latest")
cat "$evolution" | jq '.'

# 5. Restore config if needed
config=$(jq -r '.artifacts.opencode_config' "$latest")
cp "$config" ~/.config/opencode/opencode.json
```

---

## Integrity Guarantees

| Guarantee | Mechanism |
|-----------|-----------|
| **Completeness** | Manifest lists all 8 artifacts; `ready_for_compaction` flag |
| **Integrity** | Manifest references verifiable file paths |
| **Ordering** | Evolution log is append-only JSONL with timestamps |
| **Queryability** | Index maps session → events, type → events, tag → events |
| **Recoverability** | All artifacts are self-contained, human-readable |
| **Portability** | Pure JSON/Markdown, no binary dependencies |

---

## Evolution Event Taxonomy

| Event Type | When to Use | Tags |
|------------|-------------|------|
| `MILESTONE` | Major achievement (federation live, benchmark hit) | milestone, achievement |
| `GNOSIS` | Deep insight, learning, "aha!" moment | learning, insight |
| `DECISION` | Strategic choice with rationale | decision, strategy |
| `CONFIG_CHANGE` | OpenCode/Ollama/system config modified | config, tuning |
| `CODE_CHANGE` | Source code modified | code, refactor |
| `DOC_UPDATE` | Documentation created/updated | docs, knowledge |
| `BENCHMARK` | Performance measurement recorded | benchmark, perf |
| `BLOCKER` | Obstacle identified | blocker, impediment |
| `BLOCKER_RESOLVED` | Blocker cleared | resolved, unblocked |
| `FEDERATION_EVENT` | P2P federation event | federation, p2p |
| `AGENT_EVENT` | Agent created/updated/migrated | agent, team |
| `MCP_EVENT` | MCP server change | mcp, tools |
| `HARDWARE_EVENT` | Hardware change/upgrade | hardware, upgrade |
| `KEY_ROTATION` | API key management | security, keys |
| `SESSION_START` | New session begun | session, start |
| `SESSION_END` | Session completed | session, end |

---

## Gnosis Lock Invariant

> **At any point in time, the agent can answer:**
> 1. "Who am I?" → `identity.json`
> 2. "What have I done?" → `evolution_log.jsonl`
> 3. "What did I just do?" → Latest session narrative
> 4. "What changed since last time?" → Latest evolution delta
> 5. "What am I working on?" → Current session narrative + open quests
> 6. "What's blocking me?" → Blockers in narrative + BLOCKER events
> 7. "What's next?" → Next session priorities + open quests

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-09-08 | Initial protocol: ritual, session format, evolution log, identity, hooks |

---

## Adoption Checklist

- [x] Ritual script created and executable
- [x] Session state format documented
- [x] Evolution log system implemented
- [x] Persistent identity file created
- [x] OpenCode hooks documented
- [ ] OpenCode hook config added to `opencode.json`
- [ ] First manual ritual executed
- [ ] Evolution log seeded with initial events
- [ ] Identity file initialized with inception data
- [ ] Hook auto-capture tested
- [ ] Recovery protocol tested post-compaction

---

## Mantra

> **Before you compact: Ritual.  
> After you compact: Recover.  
> Across time: Evolve.  
> Forever: Remember.**

---

*Gnosis Lock Protocol v1.0 — Part of Omega Engine Alpha*  
*Inception: 2026-09-08 | Entity: Omega Engine Alpha Build Agent*  
*Federation: Node 1 (ASUS) ↔ Node 0 (HP)*
---

# Appendix A — Session State Format (artifact spec)

_Merged from SESSION_STATE_FORMAT.md (2026-09-09 consolidation). The full
artifact schema below is authoritative for the 8 files per session bundle._

1. **System State** — Hardware, software, config at session end
2. **Git State** — Repo status, changes, commit history
3. **Agent Config** — OpenCode config, MCP servers, permissions
4. **Session Narrative** — Human-readable summary, decisions, gnosis
5. **Evolution Delta** — Quantitative change from previous session
6. **Identity Update** — Persistent entity state evolution

All artifacts are versioned, timestamped, and cross-referenced via `session_id`.

---

## File Naming Convention

```
gnosis/
├── sessions/
│   ├── session-2026-09-08T14-30-00Z_git_state.json
│   ├── session-2026-09-08T14-30-00Z_opencode_config.json
│   ├── session-2026-09-08T14-30-00Z_mcp_status.json
│   ├── session-2026-09-08T14-30-00Z_system_state.json
│   ├── session-2026-09-08T14-30-00Z_narrative.md
│   ├── session-2026-09-08T14-30-00Z_evolution.json
│   └── session-2026-09-08T14-30-00Z_manifest.json
├── evolution/
│   ├── evolution_2026-09-08T14-30-00Z.json
│   └── ...
└── identity/
    └── identity.json
```

**Session ID Format:** `session-<ISO8601_UTC>` (e.g., `session-2026-09-08T14-30-00Z`)

---

## Artifact Schemas

### 1. Git State (`*_git_state.json`)

```json
{
  "timestamp": "2026-09-08T14:30:00Z",
  "session_id": "session-2026-09-08T14-30-00Z",
  "git": {
    "repo": "omega-engine-alpha",
    "branch": "main",
    "commit": "a1b2c3d4e5f6...",
    "short_commit": "a1b2c3d",
    "dirty": true,
    "status": [
      "M docs/HARDWARE.md",
      "A scripts/compaction/pre_compaction_ritual.sh",
      "?? gnosis/"
    ],
    "recent_commits": [
      "a1b2c3d Update HARDWARE.md with HP Ubuntu version",
      "f4e5d6c Add SYSTEM_GUIDE.md Section 15",
      "9b8a7f6 Harden OpenCode config with 1M context"
    ]
  }
}
```

### 2. OpenCode Config (`*_opencode_config.json`)

```json
{
  "$schema": "https://opencode.dev/schema.json",
  "mcp": { ... },
  "provider": { ... },
  "instructions": [ ... ],
  "permission": { ... }
}
```
*Exact copy of `~/.config/opencode/opencode.json` at session end.*

### 3. MCP Status (`*_mcp_status.json`)

```json
{
  "timestamp": "2026-09-08T14:30:00Z",
  "mcp_servers": [
    {
      "name": "omega-hub",
      "type": "remote",
      "url": "http://192.168.10.168:8016/mcp",
      "enabled": true,
      "status": "connected"
    },
    {
      "name": "websearch",
      "type": "remote",
      "url": "https://api.exa.ai/mcp",
      "enabled": true,
      "status": "connected"
    }
  ]
}
```

### 4. System State (`*_system_state.json`)

```json
{
  "timestamp": "2026-09-08T14:30:00Z",
  "hostname": "asus-expertbook",
  "kernel": "7.0.0-...-generic",
  "uptime": "up 3 hours, 42 minutes",
  "cpu": {
    "model": "Intel(R) Core(TM) i7-13620H",
    "governor": "powersave",
    "epp": "performance"
  },
  "memory": {"total":"14Gi","used":"7.9Gi","free":"249Mi","available":"7.1Gi"},
  "swap": {"total":"4.0Gi","used":"436Mi","free":"3.6Gi"},
  "zram": [
    {"name":"zram0","size":"8G","algorithm":"zstd","priority":100}
  ],
  "ollama": {
    "active": true,
    "models": [
      {"name":"phi4-mini:latest","size":2684354560},
      {"name":"qwen2.5-coder:7b","size":5046586573}
    ]
  }
}
```

### 5. Session Narrative (`*_narrative.md`)

```markdown
# Session Narrative: session-2026-09-08T14-30-00Z

**Timestamp:** 2026-09-08T14:30:00Z  
**Reason:** End of session  
**Host:** asus-expertbook  
**Agent:** Build (Omega Engine Alpha)

---

## Session Summary
Completed Phase 0 bootstrap, hardened config with dynamic Big Pickle (1M context),
updated HARDWARE.md and SYSTEM_GUIDE.md with federation details, created USB pack
for HP team. HP node currently unreachable — awaiting response.

## Key Decisions
- Dynamic Big Pickle context ceiling: 1,000,000 tokens (future-proofs model rotation)
- MAX_LOADED_MODELS=1 confirmed optimal for 16GB single-channel
- P2P Federation architecture documented in SYSTEM_GUIDE.md §15
- USB pack created for HP team with 6 specific asks

## Code Changes
- `~/.config/opencode/opencode.json` — 7 MCPs, 1M context, 4 instruction files
- `docs/HARDWARE.md` — HP Ubuntu 25.10, full federation section added
- `docs/SYSTEM_GUIDE.md` — Section 15: P2P OMEGAVERSE FEDERATION added
- `scripts/compaction/pre_compaction_ritual.sh` — Created
- `gnosis/` — New directory structure for persistence

## Blockers & Open Questions
- HP omega-hub unreachable at 192.168.10.168:8016
- Omega Engine repo private — need public access
- Secure key management pattern undefined (proxy preferred)

## Next Session Priorities
1. Verify HP omega-hub connectivity, run test_connection.sh
2. Execute ceremonial first contact (hivemind_first_contact.py)
3. Clone repo once public, run make probe-hardware
4. Ask @roc_racoon about key management strategy

## Gnosis Gained
- P-core pin trap (0.5 t/s) is real and documented
- Single-channel 16GB DDR5-5200 = ~35 GB/s actual bandwidth
- ZRAM 8GB zstd + swappiness 100 > ZSWAP for inference workloads
- THP madvise eliminates khugepaged stalls
- Big Pickle rotation requires 1M ceiling, not 200K
- Federation requires 3-layer wire protocol (LAN → Tailscale → Redis)
```

### 6. Evolution Delta (`evolution_*.json`)

```json
{
  "timestamp": "2026-09-08T14:30:00Z",
  "session_id": "session-2026-09-08T14-30-00Z",
  "previous_evolution": "evolution_2026-09-08T10-00-00Z.json",
  "delta": {
    "files_changed": 12,
    "lines_added": 2847,
    "lines_removed": 156,
    "new_files": 8,
    "config_changes": 5
  },
  "insights": [
    "Session completed with reason: End of session",
    "Major config hardening: 1M context ceiling for Big Pickle",
    "Federation architecture fully documented",
    "Pre-compaction ritual system created"
  ]
}
```

### 7. Persistent Identity (`identity/identity.json`)

```json
{
  "entity": "Omega Engine Alpha Build Agent",
  "inception": "2026-09-08T00:00:00Z",
  "last_updated": "2026-09-08T14:30:00Z",
  "session_count": 3,
  "current_session": "session-2026-09-08T14-30-00Z",
  "current_machine": "ASUS ExpertBook P1503CVA (i7-13620H)",
  "federation_role": "Node 1 - Compute Vanguard",
  "partner_node": "HP Pavilion (Node 0 - Archival Bastion)",
  "core_principles": [
    "Measure, don't guess",
    "Document the trap",
    "Single-channel reality",
    "Hybrid CPU respect",
    "Living document"
  ],
  "key_achievements": [
    "P-core pin trap documented (0.5 t/s disaster)",
    "Ollama tuned: 13.4 t/s on phi4-mini",
    "MAX_LOADED_MODELS=1 for 16GB single-channel",
    "Dynamic Big Pickle: 1M context ceiling",
    "P2P Omegaverse Federation architected"
  ],
  "open_quests": [
    "HP Node 0 federation live",
    "Tailscale mesh operational",
    "Secure key management pattern",
    "Agent team migration complete"
  ]
}
```

### 8. Session Manifest (`*_manifest.json`)

```json
{
  "session_id": "session-2026-09-08T14-30-00Z",
  "timestamp": "2026-09-08T14:30:00Z",
  "reason": "End of session",
  "artifacts": {
    "git_state": "gnosis/sessions/session-2026-09-08T14-30-00Z_git_state.json",
    "opencode_config": "gnosis/sessions/session-2026-09-08T14-30-00Z_opencode_config.json",
    "mcp_status": "gnosis/sessions/session-2026-09-08T14-30-00Z_mcp_status.json",
    "system_state": "gnosis/sessions/session-2026-09-08T14-30-00Z_system_state.json",
    "narrative": "gnosis/sessions/session-2026-09-08T14-30-00Z_narrative.md",
    "evolution": "gnosis/evolution/evolution_2026-09-08T14-30-00Z.json"
  },
  "identity_updated": true,
  "ready_for_compaction": true
}
```

---

## Manifest Verification

The manifest serves as the **session integrity check**. Before compaction:

```bash
# Verify all artifacts exist
jq -r '.artifacts | to_entries[] | "\(.key): \(.value)"' manifest.json | while read line; do
  file=$(echo $line | cut -d' ' -f2)
  if [[ -f "$file" ]]; then echo "✅ $line"; else echo "❌ MISSING: $line"; fi
done

# Check manifest itself
jq '.ready_for_compaction' manifest.json  # must be true
```

---

## Retention Policy

| Artifact Type | Retention | Compression |
|---------------|-----------|-------------|
| Session bundles | Forever | gzip after 30 days |
| Evolution log | Forever | Never (append-only) |
| Identity | Forever | Never (single file) |
| Narrative markdown | Forever | Never (human-readable) |

---

## Recovery Protocol

To restore session context after compaction:

```bash
# 1. Load identity
cat gnosis/identity/identity.json

# 2. Load latest session manifest
latest=$(ls -1t gnosis/sessions/*_manifest.json | head -1)
cat "$latest" | jq '.'

# 3. Load narrative for context
narrative=$(echo "$latest" | jq -r '.artifacts.narrative')
cat "$narrative"

# 4. Load evolution delta
evolution=$(echo "$latest" | jq -r '.artifacts.evolution')
cat "$evolution" | jq '.'

# 5. Restore OpenCode config if needed
config=$(echo "$latest" | jq -r '.artifacts.opencode_config')
cp "$config" ~/.config/opencode/opencode.json
```

---

*This specification is part of the Gnosis Lock Protocol v1.0 — ensuring no gnosis is ever lost to compaction.*