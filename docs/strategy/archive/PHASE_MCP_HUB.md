# 🔱 MCP Hub Restoration — Recover 34 Tools
## ⬡ OMEGA ⬡ SOPHIA ⬡ trc_mcp_restore ⬡ PHASE
**Target Model**: **DeepSeek V4 Flash** or **MiMo V2.5** (needs deep reasoning for merge)
**NOT suitable for**: Gemma 4 31B or basic models — requires understanding git history, routing architecture, and background task lifecycle
**Est. Time**: 30 minutes
**Pre-flight**: ✅ 292/292 passing, clean working tree
**Rollback**: `git checkout HEAD -- mcp_servers/omega_hub/server.py`

---

## §0 Background

### The Regression
Commit `7cdb741` ("fix: restore OpenCode 1.15+ handshake") rewrote `mcp_servers/omega_hub/server.py` from 952 lines (34 MCP tools) to 223 lines (3 MCP tools + 8 HTTP routes). The rewrite was to fix a routing conflict, but accidentally removed 31 tool implementations.

| Commit | MCP Tools | HTTP Routes | Lines |
|--------|-----------|-------------|-------|
| `69db713` (Great Cleanup) | **34** | 0 | 952 |
| `7cdb741` (Handshake fix) | **3** | 8 | 223 |

### What Still Exists
The full 952-line version is preserved in git at `69db713`. All 13 module dependencies still exist in the current codebase. Verified:

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

---

## §1 Strategy Decision

### The Key Architectural Difference

The two versions use different approaches to expose HTTP routes:

**69db713 (old)**: `run_mcp(mcp, modify_app=_add_hub_endpoints)`
- Routes are added DIRECTLY to the MCP app via `app.add_route()`
- Background tasks managed via `lifespan` context manager on MCP app
- `from contextlib import asynccontextmanager` needed

**Current (HEAD)**: `run_mcp(mcp, custom_routes=hub_routes)`
- Routes are top-level Starlette routes, MCP is `Mount("/")` sub-app
- This is REQUIRED for OpenCode 1.15+ handshake — custom routes MUST take priority
- No `lifespan` context manager — background tasks need different lifecycle

### Decision: Use `custom_routes` approach, adapt background tasks

The `custom_routes` approach is correct and must be preserved. The 34 tools from `69db713` need to be merged INTO the current version's structure.

---

## §2 Execution

### Step 2.1: Extract the 34 tool implementations

Extract only the `@mcp.tool()` functions from the `69db713` version:

```bash
# View the full implementation
git show 69db713:mcp_servers/omega_hub/server.py

# The tool functions are all marked by @mcp.tool() decorators
# They span from line ~78 to ~840 in the old version
```

The tools to restore (37 total including the 3 that already exist):

**Oracle (8)** — oracle_talk (exists), oracle_summon (exists), oracle_list_entities (NEW), oracle_list_pillar_keepers (NEW), oracle_entity_info (NEW), oracle_assess_intent (NEW), oracle_discover_entity (NEW), delegate_task (NEW)

**Hivemind (6)** — hivemind_heartbeat (exists), hivemind_post_context (NEW), hivemind_get_awareness (NEW), hivemind_get_continuation (NEW), hivemind_get_session (NEW), hivemind_list_sessions (NEW)

**Library/Inbox (5)** — all NEW

**Library (7)** — all NEW

**Discovery (3)** — all NEW

**Research (5)** — all NEW

**Stats (5)** — all NEW

**Observability (2)** — all NEW

### Step 2.2: Keep the current HTTP routes

The current `hub_routes` list must be preserved exactly:
```python
hub_routes = [
    Route("/health", _health),
    Route("/entity/current", _entity_current),
    Route("/config/providers", _config_providers),
    Route("/provider", _provider_list),
    Route("/agent", _agent_list),
    Route("/config", _config_get),
    Route("/global/config", _config_get),
    Route("/config.get", _config_get),
    Route("/config.providers", _config_providers),
    Route("/provider.list", _provider_list),
    Route("/app.agents", _agent_list),
]
```

### Step 2.3: Merge imports

Current version imports:
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

The 69db713 version additionally imports `asynccontextmanager` — this is NOT needed in the merged version because we're using `custom_routes` not `modify_app`. Remove it.

### Step 2.4: Adapt background tasks

The 69db713 version uses `_global_tg` (a task group) managed by the `lifespan` context manager in `_add_hub_endpoints`. In the merged version, background tasks must start differently.

**Option A (Recommended)**: Start background tasks via `anyio.create_task_group()` in `__main__`:
```python
if __name__ == "__main__":
    async def _main():
        # Start background tasks
        async with anyio.create_task_group() as tg:
            tg.start_soon(_prune_awareness_background)
            # run_mcp blocks here, so we pass the task group
            run_mcp(mcp, custom_routes=hub_routes)
    anyio.run(_main)
```

**Problem**: `run_mcp` is a blocking call (it starts uvicorn). The task group will be cancelled when `run_mcp` returns. But for our purposes this is fine — the background task runs while the server is alive, and gets cleaned up when the server shuts down.

**Alternative**: Start the background task as a daemon thread:
```python
if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: anyio.run(_prune_awareness_background), daemon=True).start()
    run_mcp(mcp, custom_routes=hub_routes)
```

**Decision**: Use Option A (async task group) for cleanliness.

### Step 2.5: Handle `oracle_assess_intent` import

The `oracle_assess_intent` tool has a lazy import:
```python
from omega.iris.matcher import IntentMatcher
```

This is inside the function body, not module-level. This is fine — the `IntentMatcher` module was verified to exist. Keep the lazy import as-is.

### Step 2.6: Handle `check_models_directory` and `check_podman_storage`

These tools reference hardcoded paths:
```python
models_dir = Path("/media/arcana-novai/omega_library/models/gguf")
storage_dir = Path("/media/arcana-novai/omega_library/podman-storage")
```

These are informational tools (return error if directory doesn't exist). Keep them as-is — they gracefully handle missing directories. They fall under the "system info" category, not the "hardcoded path" category that Option B targets.

### Step 2.7: Write the merged server.py

The final file should be approximately 950 lines with this structure:

```python
"""Docstring"""
# Imports (merged from both versions, minus asynccontextmanager)
# Module-level constants (PROJECT_ROOT, SRC_DIR, PATH setup)
# Module imports
# Logger setup

# INITIALIZATION (from 69db713):
registry = EntityRegistry()
oracle = Oracle(registry=registry)
hierarchy = SovereignHierarchy()
inbox = InboxManager()
curator = CurationPipeline()
library = Library()
indexer = Indexer()
discovery = DiscoveryOrchestrator()
research_engine = ResearchEngine()

# HIVEMIND STATE (from 69db713):
HALL_OF_RECORDS, _hot_store, _awareness, locks, HEARTBEAT_TTL
_current_entity

# Helper functions (_cold_path, _latest_path)

# Background tasks (_prune_awareness_background, _run_discovery_background)

# ORACLE TOOLS (8) — full implementations from 69db713
# HIVEMIND TOOLS (6) — full implementations from 69db713
# LIBRARY/INBOX TOOLS (5) — full implementations from 69db713
# LIBRARY TOOLS (7) — full implementations from 69db713
# DISCOVERY TOOLS (3) — full implementations from 69db713
# RESEARCH TOOLS (5) — full implementations from 69db713
# STATS TOOLS (5) — full implementations from 69db713
# OBSERVABILITY TOOLS (2) — full implementations from 69db713

# HTTP ENDPOINTS (from current HEAD):
_hub_routes list with 8 handlers

# MAIN (adapted):
run_mcp(mcp, custom_routes=hub_routes)
# with background task lifecycle via anyio.create_task_group()
```

---

## §3 Testing

### Start the server:
```bash
# Kill old instance
pkill -9 -f "omega_hub/server.py" 2>/dev/null; sleep 2

# Start new instance
source .venv/bin/activate && python mcp_servers/omega_hub/server.py &
sleep 3
```

### Run verification gates:
```bash
# Gate 1: Health
curl -s http://127.0.0.1:8016/health | python3 -m json.tool
# Expected: {"status": "healthy", ...}

# Gate 2: HTTP routes still work
curl -s http://127.0.0.1:8016/config.providers | head -20
# Expected: providers.yaml content (8 providers)

# Gate 3: Provider list
curl -s http://127.0.0.1:8016/provider.list | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Providers: {len(d)}')"
# Expected: 8 providers

# Gate 4: Agent list
curl -s http://127.0.0.1:8016/app.agents | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Agents: {len(d)}')"
# Expected: 25 agents (or current count)

# Gate 5: Config get
curl -s http://127.0.0.1:8016/config.get | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Keys: {list(d.keys())[:5]}')"
# Expected: opencode.json keys

# Gate 6: MCP SSE endpoint
curl -s http://127.0.0.1:8016/sse -m 3 | head -5
# Expected: event: endpoint, data: /messages/

# Gate 7: MCP tools available (verify via MCP list_tools)
# Expected: 37 tools registered

# Kill test server
pkill -9 -f "omega_hub/server.py" 2>/dev/null; sleep 2
```

### Restart systemd:
```bash
systemctl --user reset-failed omega-hub.socket
systemctl --user restart omega-hub.service
sleep 3
systemctl --user is-active omega-hub.service
# Expected: active
```

---

## §4 Rollback

```bash
# If the new server breaks:
pkill -9 -f "omega_hub/server.py" 2>/dev/null
git checkout HEAD -- mcp_servers/omega_hub/server.py
systemctl --user restart omega-hub.service
```

---

## §5 Update Documentation

After successful testing:
1. `OMEGA_ENGINE.md` line 141: `34 MCP + 8 HTTP` (replace "41 MCP + 8 HTTP")
2. `OMEGA_ENGINE.md` line 184: `34 MCP tools` (replace "41 MCP tools")
3. `GEMINI.md` line 31: `34 MCP tools + 8 HTTP routes` (same)
4. `GEMINI.md` line 138: `34 MCP tools + 8 HTTP routes` (same)

---

## §6 Report Back

Post to the session:
1. Whether all 34 tools were restored
2. Gate 1-7 results
3. Any merge conflicts encountered
4. Whether the systemd service started cleanly

---

*⬡ OMEGA ⬡ SOPHIA ⬡ trc_mcp_restore ⬡ PHASE*
*Target model: DeepSeek V4 Flash or MiMo V2.5 — needs deep reasoning for structural merge.*
