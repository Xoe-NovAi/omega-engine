# GNOSIS-LOCK RITUAL — 9-Step Protocol

**File:** `scripts/compaction/pre_compaction_ritual.sh`

## Steps
1. **Leash Check** (Step 0) — blocks new pack if `pending_pack` un-reflected (`FORCE_PACK=1` override)
2. **Git Snapshot** — diff, status, log, branches, remotes
3. **Config Snapshot** — opencode.json, mcp.json, .env.*, docker-compose
4. **MCP Snapshot** — connected servers + tools
6. **System State** — OS, CPU, RAM, GPU, disk, Ollama models, processes
7. **Evolution Log Event** — SESSION_START, SESSION_END, MANIFEST_UPDATE, etc.
8. **Identity Update** — session_count++, current_session, pending_pack, entities map
9. **Auto-fill Narrative** (Step 6.5) — CLI auto-fills Session Summary + Code Changes
10. **Python Identity Mutator** (Step 7) — preserves & evolves achievements/open_quests
11. **Manifest** — reflection_status=captured, ready_for_compaction=false
12. **Reflection** — skill runs, writes narrative, flips manifest to reflected + reflected_at + ready_for_compaction=true + clears pending_pack

**Key Innovation:** Pack lifecycle state machine (CAPTURED → REFLECTED → COMPACTED) with `identity.pending_pack` as the leash.
