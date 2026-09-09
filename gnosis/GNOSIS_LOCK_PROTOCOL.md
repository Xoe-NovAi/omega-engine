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

### 2. Session State Format (`SESSION_STATE_FORMAT.md`)
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
    ├── SESSION_STATE_FORMAT.md          # Artifact schemas
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