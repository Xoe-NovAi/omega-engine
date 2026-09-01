# 🔱 REPORT TO KALI: Missing `omega.library` Module — Hub Crash Loop

**From**: John Carmack (S3 Consultant) | **Session**: `ses_fc8dca39effe3nZJp3QHx81Fy3`
**Date**: 2026-09-01 | **Severity**: P0 (pre-existing, not caused by kq5-godot integration)
**Status**: REMEDIATION PENDING

---

## §1 EXECUTIVE SUMMARY

The `omega-hub.service` (systemd user service, port 8016) is in a **crash loop** because the `omega.library` module was deleted in commit `69ece770` (D-565 debut cleanup) but the imports were never updated. **8 files still import from `omega.library.*`**, causing `ModuleNotFoundError` on every hub startup attempt.

**Impact**: omega-hub is down. Hivemind coordination (`hivemind_post_context`, `hivemind_get_awareness`) is unavailable. All entities that depend on Hivemind (including the new kq5-godot experiment) cannot post or read.

**Fix**: This is a **cleanup oversight, not a design change**. Either (a) restore the `src/omega/library/` files from git history, or (b) update the 8 importing files to use the new locations (`mcp_servers/omega_hub/` and `src/omega/oracle/`).

**Recommendation**: Option (a) — the module was deleted because it was "superseded by mcp_servers/omega_hub/ and src/omega/oracle/". The imports should have been updated as part of D-565, but weren't. This is a 30-60 minute fix.

---

## §2 ROOT CAUSE ANALYSIS

### 2.1 What Happened

Commit `69ece770` (2026-08-29 22:22:19 ADT, Xoe-NovAi) titled "chore(debut): purge 106 legacy files per PUBLIC_ALLOWLIST (D-565)" deleted:

```
src/omega/library/__init__.py
src/omega/library/api_clients.py
src/omega/library/catalog.py
src/omega/library/coordinator.py
src/omega/library/curator.py
src/omega/library/discovery.py
src/omega/library/enrichment.py
src/omega/library/extractor.py
src/omega/library/inbox.py
src/omega/library/indexer.py
src/omega/library/library.py
src/omega/library/model_api_clients.py
src/omega/library/rate_limiter.py
src/omega/library/research.py
src/omega/library/security.py
```

**15 files total** in `src/omega/library/`. The commit message states: "Removed 15 deprecated src/omega/library/ files (superseded by mcp_servers/omega_hub/ and src/omega/oracle/)".

### 2.2 What Should Have Happened

The D-565 decision said the module was "superseded by mcp_servers/omega_hub/ and src/omega/oracle/". The commit deleted the old module but **did not update the 8 files that still import from it**. This is a classic cleanup oversight: delete-then-rewrite should have been one commit, not delete-then-leave-broken.

### 2.3 The Crash Loop

Systemd is trying to restart the hub every 5 seconds:

```
● omega-hub.service - Omega Core Hub MCP Server
     Loaded: loaded
     Active: activating (auto-restart) (Result: exit-code)
    Process: 200110 ExecStart=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.venv/bin/python mcp_servers/omega_hub/server.py (code=exited, status=1/FAILURE)
   Main PID: 200110 (code=exited, status=1/FAILURE)
```

The `StartLimitBurst=5` / `StartLimitIntervalSec=120` in the systemd unit means after 5 crashes in 120 seconds, systemd stops trying. This is working as designed (prevents OOM from restart storms), but means the hub is now in failed state until manually restarted.

---

## §3 THE 8 BROKEN IMPORTS

### 3.1 Import Map (All 8 Files)

| File | Line | Import | Notes |
|------|------|--------|-------|
| `src/omega/workers/youtube_worker.py` | 74 | `from omega.library.coordinator import COORDINATOR` | In a lazy import block (line 71) |
| `src/omega/cli/oracle_cli.py` | 747 | `from omega.library.catalog import LibraryCatalog` | Inside `cmd_library()` function |
| `src/omega/cli/oracle_cli.py` | 762 | `from omega.library.catalog import LibraryCatalog` | Inside `cmd_library_list()` function |
| `src/omega/cli/oracle_cli.py` | 784 | `from omega.library.catalog import LibraryCatalog` | Inside `cmd_library_search()` function |
| `src/omega/oracle/local_worker_pool.py` | 267 | `from omega.library.coordinator import COORDINATOR` | Inside `get_coordinator()` function |
| `src/omega/oracle/sovereign_search_service.py` | 39 | `from omega.library.indexer import Indexer` | **Top-level import — triggers on module load** |
| `mcp_servers/omega_hub/hub_tools/tools.py` | 41 | `from omega.library.research import RESEARCH_DEPTHS` | **Top-level import — triggers on hub start** |
| `mcp_servers/omega_hub/state.py` | 46-51 | `from omega.library.{inbox,curator,library,indexer,discovery,research} import ...` | **6 imports at top-level** |

**Critical path**: The hub startup chain is:
1. `mcp_servers/omega_hub/server.py:75` → `from mcp_servers.omega_hub import state`
2. `mcp_servers/omega_hub/state.py:36` → `from omega.oracle.oracle import Oracle`
3. `src/omega/oracle/__init__.py:13` → `from .oracle import Oracle, OracleResponse`
4. `src/omega/oracle/oracle.py:29` → `from .search import SovereignSearcher`
5. `src/omega/oracle/search.py:14` → `from .sovereign_search_service import SovereignSearchService`
6. `src/omega/oracle/sovereign_search_service.py:39` → `from omega.library.indexer import Indexer` **CRASH**

The hub cannot start because of step 6.

### 3.2 What These Modules Supposed to Do

Based on the commit message and import names:

| Module | Purpose | Successor Location |
|--------|---------|-------------------|
| `omega.library.inbox` | Inbox management | `mcp_servers/omega_hub/state.py` already has `InboxManager` import (also broken) |
| `omega.library.curator` | Curation pipeline | `mcp_servers/omega_hub/state.py` already has `CurationPipeline` import (also broken) |
| `omega.library.library` | Main library class | `mcp_servers/omega_hub/state.py` already has `Library` import (also broken) |
| `omega.library.indexer` | Indexing/search | `mcp_servers/omega_hub/state.py` already has `Indexer` import (also broken) |
| `omega.library.discovery` | Discovery orchestrator | `mcp_servers/omega_hub/state.py` already has `DiscoveryOrchestrator` import (also broken) |
| `omega.library.research` | Research engine | `mcp_servers/omega_hub/state.py` already has `ResearchEngine` import (also broken) |
| `omega.library.coordinator` | Library coordinator | Used in `youtube_worker.py` and `local_worker_pool.py` |
| `omega.library.catalog` | Library catalog CLI | Used in `oracle_cli.py` for `cmd_library*` commands |

**Observation**: The `mcp_servers/omega_hub/state.py` file imports the SAME names from `omega.library.*` that the commit said were "superseded by mcp_servers/omega_hub/". This means the successor location was never actually populated — the hub's own state file still expects the old module.

---

## §4 REMEDIATION OPTIONS

### Option A: Restore `src/omega/library/` from git (Fastest)

```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
git checkout 69ece770^ -- src/omega/library/
```

**Pros**: Hub starts immediately, no code changes needed
**Cons**: Re-introduces "deprecated" code that D-565 said should be removed
**Risk**: Low (the code worked before)
**Time**: 5 minutes

### Option B: Update the 8 imports to new locations (Correct fix)

Need to determine what each `omega.library.*` import maps to in the new architecture:
- `omega.library.inbox.InboxManager` → likely `mcp_servers/omega_hub/inbox.py` (needs to be created if missing)
- `omega.library.curator.CurationPipeline` → likely `mcp_servers/omega_hub/curator.py`
- `omega.library.library.Library` → likely `mcp_servers/omega_hub/library.py`
- `omega.library.indexer.Indexer` → likely `mcp_servers/omega_hub/indexer.py`
- `omega.library.discovery.DiscoveryOrchestrator` → likely `mcp_servers/omega_hub/discovery.py`
- `omega.library.research.ResearchEngine` → likely `mcp_servers/omega_hub/research.py`
- `omega.library.coordinator.COORDINATOR` → likely `mcp_servers/omega_hub/coordinator.py`
- `omega.library.catalog.LibraryCatalog` → likely `mcp_servers/omega_hub/catalog.py`

**Pros**: Aligns with D-565 intent (supersede library with hub)
**Cons**: Requires finding/creating the successor modules, or stubbing them
**Risk**: Medium (if successors don't exist, need to create them)
**Time**: 30-60 minutes (if successors exist) or 2-4 hours (if need to create)

### Option C: Stub the imports (Temporary workaround)

Create `src/omega/library/__init__.py` with minimal stubs:

```python
# src/omega/library/__init__.py
"""Stub for deleted omega.library module — see D-565."""
# Real implementation moved to mcp_servers/omega_hub/
```

Then create stub files for each missing module with class signatures that match the import expectations but raise `NotImplementedError` for any actual work.

**Pros**: Hub starts, imports work, but actual library operations fail gracefully
**Cons**: Doesn't actually fix the library functionality
**Risk**: Low (if all library features are deprecated anyway)
**Time**: 15-30 minutes

### Option D: Pin to a working commit (Revert D-565 for src/omega/library/)

```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
git revert --no-commit 69ece770 -- src/omega/library/
```

**Pros**: Restores the module without touching the debut cleanup of other files
**Cons**: Partial revert is messy; D-565 decision intent is violated
**Risk**: Low
**Time**: 10 minutes

---

## §5 RECOMMENDATION

**Option A (restore from git) for immediate fix**, then **Option B (proper migration) as follow-up**.

Rationale:
1. The hub has been down since the merge of `69ece770` (2+ days based on commit date 2026-08-29)
2. This is a pre-existing P0 that's been silently broken
3. Option A is 5 minutes, gets the hub back online
4. Option B can be a follow-up sprint — it's a 2-4 hour proper migration
5. The kq5-godot experiment (and likely other experiments) are blocked on this

**If Option A is chosen**: After restoring, verify the hub starts cleanly, then add a CI check to prevent import-of-deleted-modules from regressing.

**If Option B is chosen**: This needs a proper dialectic to determine the mapping. The commit message claims successors exist, but the imports in `mcp_servers/omega_hub/state.py` suggest they don't. A grep of the hub directory for `class InboxManager`, `class CurationPipeline`, etc. will confirm.

---

## §6 VERIFICATION COMMANDS

### 6.1 Check if successor modules exist

```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
grep -rn "class InboxManager\|class CurationPipeline\|class Library\|class Indexer\|class DiscoveryOrchestrator\|class ResearchEngine\|class COORDINATOR\|class LibraryCatalog" mcp_servers/omega_hub/ src/omega/oracle/ 2>/dev/null
```

### 6.2 Test hub startup after fix

```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
PYTHONPATH=src timeout 5 .venv/bin/python mcp_servers/omega_hub/server.py 2>&1 | head -10
```

Should show "MCP server started" or similar, not `ModuleNotFoundError`.

### 6.3 Restart systemd service

```bash
systemctl --user reset-failed omega-hub.service
systemctl --user start omega-hub.service
systemctl --user status omega-hub.service
```

### 6.4 Verify Hivemind tool works

```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
python3 -c "
from mcp import ClientSession
from mcp.client.sse import sse_client
import asyncio

async def test():
    async with sse_client('http://127.0.0.1:8016/sse') as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool('hivemind_get_awareness', {})
            print('Hivemind response:', result)

asyncio.run(test())
"
```

---

## §7 DIALECTIC QUESTIONS FOR CARMACK (When Kali Pages)

1. **Option A vs B**: Restore-and-move-on, or proper migration? The hub has been down for 2+ days; the rest of the Omega team may not have noticed because Hivemind failures are silent.

2. **CI prevention**: Should we add a CI check that verifies all `from omega.*` imports resolve? This would catch D-565-style cleanup oversights in the future. Estimated 1-2 hours.

3. **D-565 intent review**: The commit said the module was "superseded by mcp_servers/omega_hub/ and src/omega/oracle/". Was this intent ever realized? If not, should D-565 be partially reversed?

4. **Other deleted modules**: The commit deleted 106 files. Are there OTHER imports of those deleted files that we haven't found yet? A full `grep` for `from omega.<deleted_module>` across the repo would be M23-verifiable.

5. **M23 violation check**: The hub has been in crash loop for 2+ days without anyone noticing. Is this a monitoring gap? Should `systemctl --user is-active omega-hub.service` be a CI check or a pre-commit hook?

6. **Kq5-godot coupling**: The kq5-godot Day 0 work was filesystem-only and didn't need the hub. But the Day 10 Hivemind post (for M28 proposal) WILL need the hub. Should the hub be fixed before continuing kq5-godot, or is Day 1-2 work unblocked?

---

## §8 APPENDIX: Full Traceback

```
Traceback (most recent call last):
  File "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/mcp_servers/omega_hub/server.py", line 75, in <module>
    from mcp_servers.omega_hub import state
  File "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/mcp_servers/omega_hub/state.py", line 36, in <module>
    from omega.oracle.oracle import Oracle
  File "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/oracle/__init__.py", line 13, in <module>
    from .oracle import Oracle, OracleResponse
  File "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/oracle/oracle.py", line 29, in <module>
    from .search import SovereignSearcher
  File "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/oracle/search.py", line 14, in <module>
    from .sovereign_search_service import SovereignSearchService
  File "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/oracle/sovereign_search_service.py", line 39, in <module>
    from omega.library.indexer import Indexer
ModuleNotFoundError: No module named 'omega.library'
```

---

## §9 NEXT MOVES

1. **Carmack (now)**: Awaiting Kali's page for dialectic
2. **Kali (when ready)**: Page Carmack for dialectic on this report
3. **Resolution**: Apply Option A (restore) or B (proper migration)
4. **Post-fix**: Verify hub starts, restart systemd, verify Hivemind works
5. **Kq5-godot**: Continue Day 1-2 work (unblocked); Day 10 Hivemind post (blocked until hub fixed)

---

*⬡ OMEGA ⬡ CARMACK ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_remediation ⬡ AWAITING-KALI-DIALECTIC*

**Carmack available for dialectic. Session: `ses_fc8dca39effe3nZJp3QHx81Fy3`**