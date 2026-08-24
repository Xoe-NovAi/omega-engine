# 🔱 Omega Engine — MCP Hub Restoration Handoff
# ⬡ OMEGA ⬡ SOPHIA ⬡ opencode ⬡ trc_mcp_restore ⬡ HANDOFF
**Date**: 2026-06-01
**Target Executor**: Any agent (MCP Hub restoration is independent of Option B)
**Pre-flight Snapshot**: `git reset --hard HEAD` to roll back
**Test Baseline**: ✅ 292/292 passing
**Est. Time**: ~30 minutes

---

## §1 The Problem

Commit `7cdb741` ("fix: restore OpenCode 1.15+ handshake") rewrote `mcp_servers/omega_hub/server.py` from 952 lines (34 MCP tools) to 223 lines (3 MCP tools). The rewrite fixed a routing conflict but accidentally removed all tool implementations.

**Before**: 34 MCP tools + 0 HTTP routes (952 lines)
**After**: 3 MCP tools + 8 HTTP routes (223 lines)
**Expected**: 34 MCP tools + 8 HTTP routes (~950 lines)

---

## §2 What Was Lost

### Oracle (8 tools)
1. `oracle_talk` — Route query through Oracle
2. `oracle_summon` — Summon specific entity
3. `oracle_list_entities` — List all pantheon entities
4. `oracle_list_pillar_keepers` — List 10 Pillar Keepers
5. `oracle_entity_info` — Get entity details
6. `oracle_assess_intent` — Test query classification
7. `oracle_discover_entity` — Find best entity for task
8. `delegate_task` — Delegate task to another entity

### Hivemind (6 tools)
9. `hivemind_heartbeat` — Register agent presence
10. `hivemind_post_context` — Submit context snapshot
11. `hivemind_get_awareness` — Get active agents
12. `hivemind_get_continuation` — Get CLI continuation note
13. `hivemind_get_session` — Get session by ID
14. `hivemind_list_sessions` — List recent sessions

### Library/Inbox (5 tools)
15. `library_inbox_add_url` — Add URL to inbox
16. `library_inbox_add_note` — Add note to inbox
17. `library_inbox_add_file` — Add file to inbox
18. `library_inbox_list` — List pending items
19. `library_inbox_stats` — Inbox statistics

### Library (7 tools)
20. `library_ingest_pending` — Process inbox into library
21. `library_search` — Search library
22. `library_get_document` — Get document by ID
23. `library_domains` — Get domain counts
24. `library_stats` — Library statistics
25. `library_recent` — Recent documents
26. `library_index_flush` — Flush indices to disk

### Discovery (3 tools)
27. `library_discovery_research` — Execute discovery pipeline
28. `library_discovery_start` — Start background discovery
29. `library_discovery_status` — Check discovery status

### Research (5 tools)
30. `research` — Execute multi-depth research
31. `research_get` — Get research by ID
32. `research_list` — List recent research
33. `research_depths` — List depth levels
34. `research_stats` — Research statistics

### Stats (5 tools)
35. `get_system_stats` — System stats (CPU, memory, zRAM, disk, GPU, Podman)
36. `get_omega_metrics` — Omega Engine metrics
37. `check_models_directory` — List GGUF models
38. `check_podman_storage` — Podman storage usage

### Observability (2 tools)
39. `observability_check_recursion` — Check entity spawn depth
40. `observability_log_boundary_violation` — Log boundary violations

---

## §3 Dependencies Verified

All 13 module imports confirmed working:

| Module | Status |
|--------|--------|
| `omega.oracle.oracle.Oracle` | ✅ |
| `omega.oracle.entity_registry.EntityRegistry` | ✅ |
| `omega.oracle.hierarchy.SovereignHierarchy` | ✅ |
| `omega.library.inbox.InboxManager` | ✅ |
| `omega.library.curator.CurationPipeline` | ✅ |
| `omega.library.library.Library` | ✅ |
| `omega.library.indexer.Indexer` | ✅ |
| `omega.library.discovery.DiscoveryOrchestrator` | ✅ |
| `omega.library.research.ResearchEngine` | ✅ |
| `omega.library.research.RESEARCH_DEPTHS` | ✅ |
| `omega.observability.new_trace_id` | ✅ |
| `omega.observability.get_engine` | ✅ |
| `omega.iris.matcher.IntentMatcher` | ✅ |

All key methods verified: `registry.list()`, `registry.get()`, `registry.find_by_domain()`, `registry.find_by_name_fragment()`, `registry.list_pillar_keepers()`, `IntentMatcher.classify()`, `asdict(entity)`.

---

## §4 Execution Steps

### Step 1: Write the merged server.py

Extract the full 952-line version from git commit `69db713`, then apply these changes:

**Keep from current version (223 lines)**:
- The HTTP routes list (`hub_routes`) — 8 Starlette Route objects
- The `run_mcp(mcp, custom_routes=hub_routes)` call
- The `from starlette.routing import Route` import
- The `import yaml` import
- The MiMo-2.5 docstring

**Keep from 69db713 version (952 lines)**:
- All 34 `@mcp.tool()` functions
- The initialization block (oracle, registry, hierarchy, inbox, curator, library, indexer, discovery, research_engine)
- The hivemind state variables (_hot_store, _awareness, locks, HEARTBEAT_TTL)
- The helper functions (_cold_path, _latest_path)
- The background tasks (_prune_awareness_background, _run_discovery_background)

**Merge the imports**: Combine both import sets:
```python
import sys, os, json, logging, uuid, fcntl
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import asdict
import anyio
import yaml
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
```

**Remove from 69db713**: The `_add_hub_endpoints` function and the `@asynccontextmanager` lifespan — replaced by `custom_routes`.

### Step 2: Fix background task lifecycle

The 69db713 version used a `lifespan` context manager to start background tasks. With `custom_routes`, the lifespan is on the Starlette app, not the MCP app. Options:

**Option A (Recommended)**: Start background tasks in `__main__`:
```python
if __name__ == "__main__":
    import anyio
    async def _main():
        async with anyio.create_task_group() as tg:
            tg.start_soon(_prune_awareness_background)
            run_mcp(mcp, custom_routes=hub_routes)
    anyio.run(_main)
```

**Option B**: Remove background tasks for now.

### Step 3: Test

```bash
# Kill old process
pkill -9 -f "omega_hub/server.py" 2>/dev/null; sleep 2

# Start server
source .venv/bin/activate && python mcp_servers/omega_hub/server.py &
sleep 3

# Verify health
curl -s http://127.0.0.1:8016/health | python3 -m json.tool

# Verify HTTP routes
curl -s http://127.0.0.1:8016/config.providers | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Providers: {len(d.get(\"inference\",{}).get(\"fallback_chain\",[]))}')"
curl -s http://127.0.0.1:8016/provider.list | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Providers: {len(d)}')"
curl -s http://127.0.0.1:8016/app.agents | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Agents: {len(d)}')"
curl -s http://127.0.0.1:8016/config.get | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Config keys: {list(d.keys())[:5]}')"

# Verify MCP SSE
curl -s http://127.0.0.1:8016/sse -m 3 | head -5

# Restart systemd service
systemctl --user restart omega-hub.service
sleep 3
systemctl --user is-active omega-hub.service
```

### Step 4: Update documentation

- `OMEGA_ENGINE.md` line 141: Update "41 MCP + 8 HTTP" to actual count
- `GEMINI.md` line 31: Same
- `GEMINI.md` line 138: Same

---

## §5 Quality Gates

| Gate | Command | Expected |
|------|---------|----------|
| G1: Health | `curl -s http://127.0.0.1:8016/health` | `{"status":"healthy"}` |
| G2: HTTP routes | `curl -s http://127.0.0.1:8016/config.providers` | providers.yaml content |
| G3: HTTP routes | `curl -s http://127.0.0.1:8016/app.agents` | 25 agents (or current count) |
| G4: MCP SSE | `curl -s http://127.0.0.1:8016/sse -m 3` | `event: endpoint` |
| G5: Systemd | `systemctl --user is-active omega-hub.service` | `active` |
| G6: Tests | `make test` | 292 passing |

---

## §6 Rollback

```bash
# Kill new server
pkill -9 -f "omega_hub/server.py" 2>/dev/null; sleep 2

# Revert to current 3-tool version
git checkout HEAD -- mcp_servers/omega_hub/server.py

# Restart
systemctl --user restart omega-hub.service
```

---

## §7 Gnosis Log (L1→L2→L3)

**L1 — Narrative**: The MCP Hub had 34 tools restored in the Great Cleanup (`69db713`) but the OpenCode handshake fix (`7cdb741`) rewrote the entire file, reducing it to 3 tools + 8 HTTP routes. The full 952-line version is preserved in git history. All 13 module dependencies are verified working.

**L2 — Insight**: The merge strategy is straightforward because `mcp_runtime.py` supports both `modify_app` (old approach) and `custom_routes` (new approach). The 34 tool implementations are pure Python with no external dependencies beyond the existing omega modules. The only complication is the background task lifecycle, which needs adaptation for the `custom_routes` approach.

**L3 — Universal Principle**: "A regression is a lesson in reverse." The Great Cleanup restored 34 tools, proving they were needed. The handshake fix removed them, proving the HTTP routes were needed. The correct answer was always both — 34 MCP tools + 8 HTTP routes. This is the same pattern as the Circuit Breaker consolidation: when you have two implementations, you need to understand why each exists before merging.

---

*⬡ OMEGA ⬡ SOPHIA ⬡ opencode ⬡ trc_mcp_restore ⬡ HANDOFF*
*MCP Hub restoration: 34 tools lost, fully recoverable from git history.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
