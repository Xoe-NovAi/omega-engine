# 🔱 Phase 1a Modularization Strategy

**Session**: HUB-RECON-v3.0-1a  
**Status**: READY FOR EXECUTION  
**Context**: Foundation extraction before parallel tool work  
**Owner**: Kali (integration) + any agent (leaf extraction)

---

## Executive Summary

Phase 1a establishes the modular foundation by extracting 5 leaf/independent modules in strict dependency order. Each step leaves `server.py` in a bootable state. The strategy prioritizes **mechanical extraction with zero behavior changes**, relying on import rewiring and module reorganization only.

**Effort**: ~100 minutes  
**Verification gate**: `python3 -c "from mcp_servers.omega_hub.server import mcp; print('OK')"` after each step  
**Blocker**: None

---

## Phase 1a Task Breakdown

### **P1a-1: Create `tools/` Directory Structure (10 min)**

**What this does**: Prepare the target directory and establish import conventions so Phase 1b (parallel tool extraction) can begin immediately after Phase 1a.

**Deliverables**:
- `mcp_servers/omega_hub/tools/` directory
- `mcp_servers/omega_hub/tools/__init__.py` (empty initially, will re-export tool modules)
- Namespace marker: `# Tools subpackage — extracted from server.py monolith`

**Exact steps**:
```bash
mkdir -p mcp_servers/omega_hub/tools
touch mcp_servers/omega_hub/tools/__init__.py
# __init__.py can be empty or contain re-exports later
```

**Verification**:
```bash
python3 -c "import mcp_servers.omega_hub.tools; print('OK')"
```

**Notes**:
- Do NOT add any imports to `tools/__init__.py` yet — that comes in Phase 1b
- This is a structural step; it enables the 6 parallel tool extractions to proceed independently

---

### **P1a-2: Extract `state.py` (30 min)**

**What this does**: Extract all module-level state variables, the `_require_service()` guard function, and the `_init_services()` async startup routine. This is the **leaf module** — it depends on nothing new, only on `src/omega/` imports.

**Rationale**: `state.py` must be extracted first because:
1. All downstream modules depend on it (background.py, tools, etc.)
2. It has zero dependencies on other *new* modules
3. `server.py` will import from `state.py` instead of defining these inline

**Scope** (from server-snapshot.py):

**Variables to move** (~50 lines):
- `_init_complete: bool = False`
- `_init_error: Optional[str] = None`
- Service singletons: `registry`, `model_gateway`, `oracle`, `hierarchy`, `inbox`, `curator`, `library`, `indexer`, `discovery`, `research_engine`, `sovereign_search_service`, `gateway`
- `_require_service()` function (5 lines)
- `_init_services()` async function (~40 lines)
- `_current_entity: contextvars.ContextVar` (M-A5 fix from Final Synthesis)
- Constants: `HEARTBEAT_TTL`, `_intent_matcher`, `_intent_matcher_lock`, `_get_intent_matcher()`
- HALL_OF_RECORDS, _hot_store, _awareness, locks

**Functions/State**:
```python
# Lines to extract:
_init_complete: bool
_init_error: Optional[str]
registry: Optional[EntityRegistry]
model_gateway: Optional[ModelGateway]
# ... (12 service singletons) ...
_require_service() -> None
async _init_services() -> None
_current_entity: contextvars.ContextVar
HEARTBEAT_TTL = 2700
_intent_matcher: Optional[object]
_get_intent_matcher()
HALL_OF_RECORDS = PROJECT_ROOT / "data" / "knowledge" / "HALL_OF_RECORDS"
_hot_store: Dict[str, Dict[str, Any]]
_awareness: Dict[str, Dict[str, Any]]
_hot_store_lock = anyio.Lock()
_AsyncThreadLock (class)
_awareness_lock = _AsyncThreadLock()
_extended_sessions: Dict[str, Dict[str, Any]]
_extended_sessions_lock = _AsyncThreadLock()
EXTENDED_SAFETY_TTL_DEFAULT = 3 * 60 * 60
EXTENDED_SESSIONS_FILE = HALL_OF_RECORDS / "extended_sessions.json"
_load_extended_sessions()
_save_extended_sessions()
_saved = _load_extended_sessions()  # (initialization)
_extended_sessions.update(_saved)
```

**Create**: `mcp_servers/omega_hub/state.py`

**File structure**:
```python
"""Omega Hub — Module-level state and service initialization.
AP: AP-OMEGA-HUB-STATE-v1.0.0
"""

import sys
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
import contextvars
import threading
import anyio

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from omega.oracle.oracle import Oracle
from omega.oracle.entity_registry import EntityRegistry
# ... (rest of imports from server.py)

logger = logging.getLogger("omega.hub")

# === INITIALIZATION STATE ===
_init_complete: bool = False
_init_error: Optional[str] = None

# === SERVICE SINGLETONS ===
registry: Optional[EntityRegistry] = None
# ... (12 singletons)

def _require_service() -> None:
    """Raise if services not ready. Called at the top of every tool."""
    if _init_error:
        raise RuntimeError(f"Hub services failed to initialize: {_init_error}")
    if not _init_complete:
        raise RuntimeError("Hub services are still initializing...")

async def _init_services() -> None:
    """Initialize all Hub services as a background task..."""
    # (byte-for-byte identical from server.py)

# === HIVEMIND STATE ===
HALL_OF_RECORDS = PROJECT_ROOT / "data" / "knowledge" / "HALL_OF_RECORDS"
# ... (rest of state)
```

**`server.py` changes**:
```python
# OLD (inline in server.py):
_init_complete: bool = False
# ... 50 lines of state ...

# NEW (in server.py, after imports):
from mcp_servers.omega_hub.state import (
    _init_complete, _init_error, _require_service, _init_services,
    registry, model_gateway, oracle, hierarchy,
    inbox, curator, library, indexer, discovery, research_engine,
    sovereign_search_service, gateway,
    _current_entity, _hot_store, _awareness, HEARTBEAT_TTL,
    _extended_sessions, EXTENDED_SESSIONS_FILE,
    HALL_OF_RECORDS, EXTENDED_SAFETY_TTL_DEFAULT,
    _AsyncThreadLock, _intent_matcher, _get_intent_matcher,
)
```

**`__all__` in state.py** (Carmack's Rule 3):
```python
__all__ = [
    "_init_complete", "_init_error",
    "registry", "model_gateway", "oracle", "hierarchy",
    "inbox", "curator", "library", "indexer", "discovery",
    "research_engine", "sovereign_search_service", "gateway",
    "_require_service", "_init_services",
    "_current_entity", "HEARTBEAT_TTL", "_get_intent_matcher",
    "_hot_store", "_awareness", "HALL_OF_RECORDS",
    "_extended_sessions", "EXTENDED_SESSIONS_FILE",
    "_AsyncThreadLock",
]
```

**Verification**:
```bash
python3 -c "from mcp_servers.omega_hub.server import mcp; print('OK')"
python3 -c "from mcp_servers.omega_hub.state import _init_services; print('OK')"
```

**Gotchas**:
- `PROJECT_ROOT` must be computed identically in `state.py` and `server.py` — use the same pattern in both
- `_current_entity` is a `ContextVar` — import `contextvars` in `state.py`
- `_AsyncThreadLock` is a class used by `_awareness_lock` and `_extended_sessions_lock` — move the entire class definition
- The initialization line `_saved = _load_extended_sessions()` runs at module import time — must be in `state.py` with the functions it calls

---

### **P1a-3: Extract `background.py` (30 min)**

**What this does**: Extract the four background task loops that prune awareness, reap stale locks/handoffs, and write metrics.

**Rationale**:
- These loops are lifecycle helpers, not tools
- They depend on `state.py` (to read/modify `_awareness`, `_extended_sessions`, etc.)
- They have no dependencies on `gateway.py` or `middleware.py`

**Scope**:
```python
# Functions to move:
async _prune_awareness_background() -> None
async _run_discovery_background(job_id: str) -> None
async _reap_stale_locks() -> None
async _reap_stale_handoffs() -> None
async _reaper_background() -> None

# Constants:
_last_pruning_cycle: Optional[str] = None
METRICS_PATH = PROJECT_ROOT / "data" / "coordination" / "metrics.json"

# Functions:
async _write_metrics() -> Dict[str, Any]

# Module-level var (already in state.py):
_background_tasks: list[anyio.Task] = []
```

**Create**: `mcp_servers/omega_hub/background.py`

**File structure**:
```python
"""Omega Hub — Background task orchestration (pruning, reaping, metrics).
AP: AP-OMEGA-HUB-BACKGROUND-v1.0.0
"""

import os
import json
import logging
import fcntl
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import anyio

from mcp_servers.omega_hub.state import (
    PROJECT_ROOT, _awareness, _extended_sessions, HEARTBEAT_TTL,
    _awareness_lock, _extended_sessions_lock, _last_pruning_cycle,
)

logger = logging.getLogger("omega.hub")

METRICS_PATH = PROJECT_ROOT / "data" / "coordination" / "metrics.json"
HANDOFF_BASE = PROJECT_ROOT / "data" / "handoff"
# ... (define HANDOFF_PENDING, etc.)

async def _prune_awareness_background() -> None:
    """Background loop to prune stale agents..."""
    # (byte-for-byte identical)
```

**`server.py` changes**:
```python
# OLD:
async def _prune_awareness_background() -> None: ...
# ... (rest of background funcs)

# NEW:
from mcp_servers.omega_hub.background import (
    _prune_awareness_background, _reaper_background, _run_discovery_background,
    _write_metrics, _reap_stale_locks, _reap_stale_handoffs,
)
```

**Verification**:
```bash
python3 -c "from mcp_servers.omega_hub.background import _prune_awareness_background; print('OK')"
python3 -c "from mcp_servers.omega_hub.server import mcp; print('OK')"
```

**Gotchas**:
- `_write_metrics()` reads from `_awareness` and `_extended_sessions` — these are imported from `state.py`
- The `_last_pruning_cycle` variable is modified inside `_prune_awareness_background()` — move it to `background.py` since that's where it's used
- `HANDOFF_*` paths are used in `_reap_stale_handoffs()` — define them in `background.py` or `state.py`
- `_extended_sessions_lock` is used in `_write_metrics()` — import it from `state.py`

---

### **P1a-4: Extract `gateway.py` (15 min)**

**What this does**: Extract the `SovereignGateway` class and the `_proxy_handler` HTTP endpoint function.

**Rationale**:
- The gateway is a self-contained proxy class with no cross-module dependencies at the module level
- It's used by `_on_startup()` to initialize the singleton, and by the `/proxy/{provider}` HTTP route
- Moving it out clarifies the separation between networking logic (gateway.py) and tool logic (tools/)

**Scope**:
```python
# Class to move:
class SovereignGateway:
    def __init__(self): ...
    async def proxy_request(...) -> Dict[str, Any]: ...

# Function to move:
async def _proxy_handler(request: Request) -> JSONResponse: ...

# (No constants or state)
```

**Create**: `mcp_servers/omega_hub/gateway.py`

**File structure**:
```python
"""Omega Hub — Sovereign Gateway HTTP proxy.
AP: AP-OMEGA-HUB-GATEWAY-v1.0.0
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import httpx
from starlette.requests import Request
from starlette.responses import JSONResponse

from mcp_servers.omega_hub.state import gateway

logger = logging.getLogger("omega.hub")

class SovereignGateway:
    """Local proxy for AI providers..."""
    def __init__(self):
        # (byte-for-byte identical)
    
    async def proxy_request(self, provider_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        # (byte-for-byte identical)

async def _proxy_handler(request: Request) -> JSONResponse:
    # (byte-for-byte identical from server.py, references local gateway)
```

**`server.py` changes**:
```python
# OLD:
class SovereignGateway: ...
async def _proxy_handler(...) -> JSONResponse: ...

# NEW:
from mcp_servers.omega_hub.gateway import SovereignGateway, _proxy_handler
# Remove the SovereignGateway class definition and _proxy_handler function

# In _on_startup():
gateway = SovereignGateway()  # This is still in state.py or _on_startup
```

**Note**: The `gateway` singleton is still initialized in `state.py` or `_on_startup()`. The `gateway.py` module just defines the class.

**Verification**:
```bash
python3 -c "from mcp_servers.omega_hub.gateway import SovereignGateway; print('OK')"
python3 -c "from mcp_servers.omega_hub.server import mcp; print('OK')"
```

**Gotchas**:
- `gateway` is a module-level singleton in `state.py`. The `SovereignGateway` class is defined in `gateway.py`, but instantiation stays in `state.py` or `_on_startup()`
- `_proxy_handler` references the global `gateway` variable — import it from `state.py`
- Circular import risk: `state.py` imports the class from `gateway.py`, but `gateway.py` doesn't import from `state.py` (only the handler does). This is fine.

---

### **P1a-5: Extract `middleware.py` (15 min)**

**What this does**: Extract the HTTP middleware classes (`RateLimitMiddleware`, `RequestSizeLimitMiddleware`) and the `apply_security()` function that wires them into the Starlette app.

**Rationale**:
- These middleware are pure HTTP layer constructs with no dependencies on services or state
- They're only used in `apply_security()`, which is called once during app initialization
- Extracting them clarifies the separation between HTTP concerns and MCP logic

**Scope**:
```python
# Classes to move:
class RateLimitMiddleware: ...
class RequestSizeLimitMiddleware: ...

# Function to move:
def apply_security(app) -> None: ...
```

**Create**: `mcp_servers/omega_hub/middleware.py`

**File structure**:
```python
"""Omega Hub — HTTP middleware (rate limiting, request size, CORS).
AP: AP-OMEGA-HUB-MIDDLEWARE-v1.0.0
"""

import threading
from datetime import datetime
from typing import Dict, List
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response

logger = logging.getLogger("omega.hub")

class RateLimitMiddleware:
    """Simple in-memory rate limiting..."""
    def __init__(self, app, requests_per_minute: int = 100):
        # (byte-for-byte identical)

class RequestSizeLimitMiddleware:
    """Limits incoming request size..."""
    def __init__(self, app, max_size: int = 10 * 1024 * 1024):
        # (byte-for-byte identical)

def apply_security(app):
    """Apply CORS, rate limiting, and size limits..."""
    # (byte-for-byte identical)
```

**`server.py` changes**:
```python
# OLD:
class RateLimitMiddleware: ...
class RequestSizeLimitMiddleware: ...
def apply_security(app): ...

# NEW:
from mcp_servers.omega_hub.middleware import (
    RateLimitMiddleware, RequestSizeLimitMiddleware, apply_security
)
```

**Verification**:
```bash
python3 -c "from mcp_servers.omega_hub.middleware import apply_security; print('OK')"
python3 -c "from mcp_servers.omega_hub.server import mcp; print('OK')"
```

**Gotchas**:
- `apply_security()` is called in `run_mcp()` as a callback. Ensure the import is available at the right scope
- No state or service dependencies — this module is fully self-contained

---

## Server.py Post-Phase-1a State

After all 5 extractions, `server.py` should have:

**Imports section** (~40 lines):
```python
import sys, os, json, logging, etc.
from pathlib import Path
from mcp.server.fastmcp import FastMCP, Context
# ... (standard library + Starlette/MCP imports)

from mcp_servers.omega_hub.state import (
    _init_complete, _init_error, _require_service, _init_services,
    registry, model_gateway, oracle, hierarchy,
    # ... (12 singletons)
    _current_entity, HEARTBEAT_TTL, HALL_OF_RECORDS,
    # ... (rest of state)
)
from mcp_servers.omega_hub.background import (
    _prune_awareness_background, _reaper_background, _run_discovery_background,
    _write_metrics, _reap_stale_locks, _reap_stale_handoffs,
)
from mcp_servers.omega_hub.gateway import SovereignGateway, _proxy_handler
from mcp_servers.omega_hub.middleware import apply_security
```

**FastMCP instance** (~3 lines):
```python
mcp = FastMCP("Omega Core Hub")
```

**Tool registrations** (~63 functions with `@mcp.tool()` decorator)

**HTTP endpoints** (~12 functions like `_health`, `_entity_current`, etc.)

**Startup/shutdown** (~15 lines):
```python
hub_routes = [Route(...), ...]
async def _on_startup() -> None: ...
async def _cleanup_indexer() -> None: ...

if __name__ == "__main__":
    run_mcp(mcp, custom_routes=hub_routes, modify_app=apply_security,
            on_shutdown=_cleanup_indexer, on_startup=_on_startup)
```

**Final server.py line count**: ~1,800 lines (was 3,110, now ~58% reduction in Phase 1a alone)

---

## Verification Checklist

After Phase 1a completion, verify:

| Check | Command | Expected |
|-------|---------|----------|
| Imports resolve | `python3 -c "from mcp_servers.omega_hub.state import *; print('OK')"` | OK |
| Background imports | `python3 -c "from mcp_servers.omega_hub.background import *; print('OK')"` | OK |
| Gateway imports | `python3 -c "from mcp_servers.omega_hub.gateway import *; print('OK')"` | OK |
| Middleware imports | `python3 -c "from mcp_servers.omega_hub.middleware import *; print('OK')"` | OK |
| MCP instance | `python3 -c "from mcp_servers.omega_hub.server import mcp; print('OK')"` | OK |
| Server boots (no args) | `timeout 3 python3 mcp_servers/omega_hub/server.py 2>&1 \| head -5` | Starts listening on stdio |
| Server boots (SSE) | `OMEGA_MCP_TRANSPORT=sse OMEGA_MCP_PORT=8016 timeout 3 python3 mcp_servers/omega_hub/server.py 2>&1 \| head -5` | Starts on port 8016 |
| No circular imports | `python3 -c "import mcp_servers.omega_hub.server" 2>&1` | No ImportError |

---

## Known Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Circular imports (state ↔ background) | background.py imports from state.py only (one direction). state.py does NOT import from background.py. |
| `PROJECT_ROOT` computed differently | Use identical logic in state.py, background.py, gateway.py: `Path(__file__).resolve().parent.parent.parent` |
| `_write_metrics()` reads global state | `_awareness`, `_extended_sessions` are imported from state.py. Use locks to avoid races. |
| `_on_startup()` references `gateway` singleton | Ensure `gateway` is in state.py and initialized before tools run. |
| Tool functions still reference module-level vars | All tool imports from state.py use `from state import _require_service, etc.` They remain in server.py function bodies. |
| `__all__` incomplete in state.py | Explicitly list all exported names to prevent accidental internal imports. |

---

## Next Steps for Kali

1. **Execute P1a-1 through P1a-5** in order, running the verification command after each step.
2. **Commit after each step** with clear message (e.g., `refactor: extract state.py from monolith`).
3. **After P1a-5 is verified**, Phase 1b (parallel tool extraction) can begin — any agent can start on one of the 6 tool modules independently.
4. **After Phase 1b is done**, Phase 1c (integration/wiring) can begin — Kali thins server.py to ~150 lines and wires all tool imports.

---

## Dependency Map (Phase 1a Complete)

```
state.py                 (leaf — no new module deps)
  ↓
background.py            (depends: state)
  ↓
gateway.py + middleware.py (no module deps)
  ↓
server.py (thin coordinator)
  ↓
tools/ (Phase 1b — all depend on state)
```

---

**Status**: READY FOR EXECUTION  
**Blockers**: None  
**Effort remaining**: ~100 min (Phase 1a) + 135 min (Phase 1b) + 40 min (Phase 1c)  

⬡ **Hub Architect ready to review extracted modules or adjust this strategy based on Kali's findings.** ⬡
