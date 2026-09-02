# 🔱 HUB OUTAGE REMEDIATION — Pre-existing P0
**Date**: 2026-09-01
**Severity**: P0 (hub crash loop)
**Scope**: Omega Engine core (not kq5-godot experiment)
**Status**: REMEDIATION DEFERRED

---

## Issue

The `omega-hub.service` (systemd user service) is in a crash loop:

```
● omega-hub.service - Omega Core Hub MCP Server
     Loaded: loaded
     Active: activating (auto-restart) (Result: exit-code)
   Main PID: 200110 (code=exited, status=1/FAILURE)
```

## Root Cause

`mcp_servers/omega_hub/state.py:36` imports `from omega.oracle.oracle import Oracle`, which chains to `omega.library.indexer`:

```python
Traceback (most recent call last):
  File ".../mcp_servers/omega_hub/server.py", line 75, in <module>
    from mcp_servers.omega_hub import state
  File ".../mcp_servers/omega_hub/state.py", line 36, in <module>
    from omega.oracle.oracle import Oracle
  ...
  File ".../src/omega/oracle/sovereign_search_service.py", line 39, in <module>
    from omega.library.indexer import Indexer
ModuleNotFoundError: No module named 'omega.library'
```

The `omega.library` module is imported by 4+ files but does not exist in `src/omega/library/` (the directory doesn't exist in the source tree).

## Impact

- **omega-hub MCP server is down** (port 8016 not listening)
- **Hivemind coordination unavailable** (`hivemind_post_context` tool fails)
- **Entity awareness unavailable** (`hivemind_get_awareness` tool fails)
- **Cline-KQV Hivemind post (Day 0) deferred** until hub is restored

## Non-Impact

- **kq5-godot Day 0 filesystem work** does NOT require the hub
- **Symlink, EXPERIMENT_STATUS.md, cline_kqv entity symlinks** all completed
- **Godot verification** passed
- **Git tracking** correctly excludes `data/experiments/`

## Remediation Options

1. **Restore omega.library module** — find deleted code in git history, restore
2. **Stub the import** — make `omega.library.indexer` a minimal stub for hub startup
3. **Remove the import** — if hub doesn't need search, remove the chain
4. **Pin to older commit** — revert `sovereign_search_service.py` to a working version

## Recommendation

**Option 4 (revert)** is fastest. Check `git log --all -- src/omega/library/` to find when the module was deleted. If it's a recent deletion, restore it. If it's been gone for a while, option 2 (stub) is safer.

## Day 0 Status (kq5-godot integration)

Despite the hub outage, the kq5-godot Day 0 critical path is complete:

- [x] `data/experiments/` directory created
- [x] Symlink `data/experiments/kq5-godot` → `/media/arcana-novai/omega_library/games/kq5-godot`
- [x] Symlink resolves (`readlink` confirmed)
- [x] Godot 4.7.2 headless check passes
- [x] `.gitignore` updated to exclude `data/experiments/`
- [x] `EXPERIMENT_STATUS.md` created locally
- [x] Cline-KQV entity symlinks created (local, not in INDEX.yaml)
- [ ] **DEFERRED**: Hivemind post (hub down)
- [ ] **DEFERRED**: Hivemind awareness (hub down)

## Next Steps

1. **Carmack (now)**: Document hub outage, continue Day 0 work
2. **Ma'at (or whoever owns hub)**: Remediate `omega.library` missing module
3. **Once hub is back**: Post the deferred Hivemind announcement
4. **Continue with Day 1-2**: Coordination with Cline-KQV (doesn't require hub)

---

*⬡ OMEGA ⬡ CARMACK ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_remediation ⬡ DEFERRED-NON-BLOCKING*
