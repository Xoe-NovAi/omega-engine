# Context Engineering Protocol — Integration Guide for Omega Engine

## Quick Start

```bash
# 1. Copy all files to Omega Engine
cp -r context-engineering-protocol/scripts/ $OMEGA_ENGINE_ROOT/scripts/
cp -r context-engineering-protocol/gnosis/ $OMEGA_ENGINE_ROOT/gnosis/

# 2. Make ritual executable
chmod +x $OMEGA_ENGINE_ROOT/scripts/compaction/pre_compaction_ritual.sh

# 3. Register OpenCode hooks in opencode.json
# Add to opencode.json:
# {
#   "hook": {
#     "opencode_hooks": {
#       "pre_compact": "python3 scripts/compaction/opencode_hooks.py",
#       "session_end": "python3 scripts/compaction/opencode_hooks.py"
#     }
#   }
# }

# 4. Register plugin
# Add to opencode.json:
# {
#   "plugin": ["gnosis-leash"]
# }

# 5. Add Make targets (see INTEGRATION.md)
# Add targets from Makefile snippet to your Makefile
```

## Directory Structure

```
$OMEGA_ENGINE_ROOT/
├── scripts/compaction/
│   ├── pre_compaction_ritual.sh      # 9-step ritual (executable)
│   ├── evolution_log.py              # Evolution log system (CLI + library)
│   ├── opencode_hooks.py             # OpenCode hook handler
│   ├── gnosis_leash_inject.py        # Injection logic (reference)
│   ├── evolution_log.py              # Evolution log system
│   └── pause_ledger.py               # Pack state ledger
├── gnosis/
│   ├── identity/identity.json        # Persistent identity (living document)
│   ├── sessions/                     # Session artifacts
│   ├── evolution/                    # Evolution log + index
│   └── well/                         # The Well corpus (optional but recommended)
├── .opencode/
│   ├── plugins/gnosis-leash.js       # OpenCode plugin (reference impl)
│   └── skills/gnosis-lock/           # Reflection skill
└── Makefile                          # gnosis-lock, gnosis-stats, gnosis-ledger, gnosis-leash-status
```

## Step-by-Step Integration

### 1. Copy Files

```bash
# Copy all scripts
cp -r context-engineering-protocol/scripts/compaction/ $OMEGA_ENGINE_ROOT/scripts/

# Copy gnosis structure (creates dirs if needed)
cp -r context-engineering-protocol/gnosis/ $OMEGA_ENGINE_ROOT/gnosis/

# Make ritual executable
chmod +x $OMEGA_ENGINE_ROOT/scripts/compaction/pre_compaction_ritual.sh
```

### 2. Register OpenCode Hooks

Add to `opencode.json`:

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

### 3. Register Plugin

```json
{
  "plugin": ["gnosis-leash"]
}
```

Copy the plugin file:
```bash
cp context-engineering-protocol/.opencode/plugins/gnosis-leash.js $OMEGA_ENGINE_ROOT/.opencode/plugins/gnosis-leash.js
```

### 4. Add Make Targets

Add to your `Makefile`:

```makefile
# Gnosis Lock — Pre-compaction ritual (CLI)
gnosis-lock:
	@read -p "Reason: " REASON; \
	scripts/compaction/pre_compaction_ritual.sh --reason "$$REASON"

# Gnosis Stats — Evolution log stats + timeline
gnosis-stats:
	python3 scripts/compaction/evolution_log.py stats

# Gnosis Ledger — Pause Ledger (pack states + timestamps + leash)
gnosis-ledger:
	python3 scripts/compaction/pause_ledger.py

# Gnosis Leash Status — Watchdog
gnosis-leash-status:
	@scripts/compaction/gnosis_leash_status.sh
```

### 5. Initialize Gnosis Structure

```bash
# Run once to initialize directories and identity
mkdir -p gnosis/{identity,sessions,evolution,well}
# Initialize identity.json if not exists (ritual will create if missing)
```

## Ritual Usage

### Interactive (Skill)
```bash
# Via OpenCode skill (includes dynamic reflection)
/gnosis-lock REASON="End of session"
```

### CLI (No Reflection)
```bash
# Auto-fills narrative from git/evolution state
make gnosis-lock REASON="End of session"

# With force override (skip leash check)
FORCE_PACK=1 make gnosis-lock REASON="Emergency compact"
```

### Direct Script
```bash
./scripts/compaction/pre_compaction_ritual.sh --session-id session-2026-09-21T20-34-00Z --reason "End of session"
```

## Reflection Skill

The `/gnosis-lock` skill provides dynamic reflection via `question` tool:

1. Runs ritual (Steps 0-8)
2. Reads identity → current_session
3. **Dynamic reflection** via `question` tool:
   - 3 core categories: Decision, Pattern, Gnosis
   - Session-specific questions (0–10+, no cap)
4. Writes `narrative.md` (replaces TODO with answers)
5. **Step 4b**: Flips manifest → `reflected` + `reflected_at` + `ready_for_compaction=true` + clears `pending_pack`
6. Sweeps narrative for Well corrections → `make well-add`
7. Commits gnosis records

## Pack Lifecycle

```
CAPTURED (ritual complete, narrative TODO)
    ↓ [human reflection via skill]
REFLECTED (narrative populated, reflected_at set, ready_for_compaction=true)
    ↓ [/compact runs]
COMPACTED (context compressed, narrative survives via injection)
```

**Leash**: Step 0 blocks second CAPTURED while previous un-REFLECTED.
**Override**: `FORCE_PACK=1` (acknowledges narrative loss risk).

## Gnosis-Leash Injection

The plugin injects at two points:

### Session Start (`experimental.chat.system.transform`)
- WanderGround INDEX (first 24 lines)
- The Well top-6 active records (domains: harness, local_ai)
- Operating rules (indented)

### Compaction (`experimental.session.compacting`)
- WanderGround INDEX (first 24 lines)
- The Well top-8 active records (domains: harness, local_ai)
- Human narrative (current session if REFLECTED, else latest REFLECTED fallback)
- **Never silent**: If no narrative → injects `⚠️ GNOSIS-LOCK INCIDENT` + logs error
- Operating rules (indented)

### Narrative Lookup Priority
1. Current session narrative (if `REFLECTED` + populated)
2. Latest `REFLECTED` pack on disk (by mtime)
3. **Never silent**: Injects incident warning + logs to `gnosis-errors.jsonl`

## Well Integration

The Well is optional but recommended for correction injection:

```bash
# Add The Well corpus
cp -r omega-well/gnosis/well/ $OMEGA_ENGINE_ROOT/gnosis/well/
cp omega-well/scripts/well_storage.py $OMEGA_ENGINE_ROOT/scripts/
cp omega-well/tests/test_well.py $OMEGA_ENGINE_ROOT/tests/

# Add Make targets
# well-add, well-list, well-stats, well-supersede, well-export, well-search
```

### Well Injection Filtering
- Session start: top-6, domains `["harness", "local_ai"]`
- Compaction: top-8, domains `["harness", "local_ai"]`

## Watchdog: `gnosis-leash-status`

```bash
make gnosis-leash-status
```

Verifies:
1. Plugin loaded (`gnosis-leash` in plugin list)
2. Plugin congruence (hooks registered)
3. Pack migration (no stuck CAPTURED packs)
4. Leash functional (pending_pack gated)
5. Narrative present (current or fallback)
6. INDEX injection active (first 24 lines present)

## Identity.json — Living Document

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
  "key_achievements": [...],      // LIVING — extends, never resets
  "open_quests": [...],           // LIVING — extends, never resets
  "entities": {
    "build": { "session_count": 30, "last_session": "...", "last_phase": "federation" }
  }
}
```

**Key Principle**: `key_achievements` and `open_quests` are **living documents** — ritual extends them, never resets.

## Evolution Log

Append-only JSONL at `gnosis/evolution/evolution_log.jsonl` with index at `evolution_index.json`.

### Event Types

| Type | Description |
|------|-------------|
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

### CLI

```bash
# Log event
python3 scripts/compaction/evolution_log.py log SESSION_END "session-xyz" "End of session" --tags ritual session-end

# Query events
python3 scripts/compaction/evolution_log.py query --session-id session-xyz --type SESSION_END --limit 20

# Stats
python3 scripts/compaction/evolution_log.py stats

# Timeline
python3 scripts/compaction/evolution_log.py timeline --session-id session-xyz --limit 20

# Export
python3 scripts/compaction/evolution_log.py export --format markdown --output evolution.md
```

## Integration Checklist

- [ ] Files copied to correct locations
- [ ] `pre_compaction_ritual.sh` executable
- [ ] OpenCode hooks registered in `opencode.json`
- [ ] `gnosis-leash` plugin registered in `opencode.json`
- [ ] `gnosis-leash.js` plugin file copied
- [ ] Make targets added
- [ ] `gnosis/` directories exist
- [ ] `identity.json` initialized (or ritual creates it)
- [ ] The Well corpus copied (optional but recommended)
- [ ] `make gnosis-lock REASON="test"` runs successfully
- [ ] `make gnosis-leash-status` returns all green
- [ ] `/gnosis-lock` skill works (dynamic reflection)

## Testing

```bash
# Test ritual
make gnosis-lock REASON="Integration test"

# Verify manifest
cat gnosis/sessions/session-*/manifest.json | jq .reflection_status

# Test skill (interactive)
# In OpenCode: /gnosis-lock REASON="Test reflection"

# Watchdog
make gnosis-leash-status

# Evolution log
make gnosis-stats
```

## License

Apache-2.0 — see parent repo LICENSE.