# Session State Capture Format Specification
## Omega Engine — Gnosis Lock Protocol v1.0

---

## Overview

Every session produces a **Session Bundle** — a deterministic set of artifacts that fully captures:
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