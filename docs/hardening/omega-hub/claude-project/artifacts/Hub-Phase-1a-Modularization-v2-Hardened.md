# 🔱 Phase 1a Modularization — Hardened Specification v2

**Session**: `HUB-RECON-1a-v2`
**Status**: COMPLETE — ready for execution
**Context**: Review and hardening pass over `Haiku-Phase-1a-Modularization-v1.md`
**Owner**: Kali (integration) + any agent (leaf extraction)
**Supersedes**: Haiku v1 (v1 remains valid as a narrative walkthrough; this doc is the
authoritative spec — where the two disagree, **this document wins**)

---

## 0. What Changed From v1 (Read This First)

Haiku's v1 plan is structurally sound — same dependency order
(`state.py → background.py → gateway.py → middleware.py`), same five-step
breakdown, same "every commit must boot" discipline. This pass fixes four
things v1 got wrong or left dangerously underspecified:

| # | Issue in v1 | Fix in v2 |
|---|------------|-----------|
| 1 | `_background_tasks: list[anyio.Task] = []` — this type annotation was **already removed** by P0-2 (`anyio.Task` doesn't exist in AnyIO 4.x). v1 re-introduces it. | `state.py` declares `_background_tasks: list = []` — **no annotation**, matching the post-P0-2 source of truth. |
| 2 | `HANDOFF_*` paths and `LOCKS_BASE` were never assigned a home — v1 says "define in background.py **or** state.py" (ambiguous). These are needed by `background.py` (P1a-3) **and** `tools/hivemind.py` (P1b). | Both sets of constants — plus their `mkdir()` side effects — move to **`state.py`** (P1a-2). Single source of truth, no cross-import ambiguity. |
| 3 | No explicit warning about the **module-attribute-vs-name-binding** trap. `_init_services()` reassigns 12 service singletons via `global X` — this is *only* safe because the **entire function** moves into `state.py` verbatim. Any future code that tries to set a singleton from `server.py`/`background.py`/`gateway.py` by rebinding an *imported name* will silently fail. | New **§4 Critical Gotcha** section, called out explicitly, with the correct pattern (`import state` + `state.X = ...`) documented for Phase 1b/2 authors. |
| 4 | `gateway.py` was specified with a `TYPE_CHECKING`-unsafe forward reference (`Optional['SovereignGateway']` in `state.py` with no import path for type-checkers) and an inline `import httpx` inside `__init__` (fine for byte-identical extraction, but flagged so Phase 2 doesn't "fix" it mid-split). | `state.py` uses `TYPE_CHECKING` guard for the `SovereignGateway` annotation. `gateway.py`'s inline `import httpx` is preserved **as-is** for Phase 1a (no behavior change) with an explicit Phase 2 TODO comment. |

Everything else below is v1's structure, expanded with exact `__all__` lists,
import-direction diagrams, a commit/rollback protocol, and an expanded
verification matrix.

---

## 1. Scope Recap

Five leaf/near-leaf modules, extracted in strict dependency order, each
leaving `server.py` in a **bootable** state:

```
state.py  →  background.py  →  gateway.py  +  middleware.py  →  server.py (thin)
 (1st)         (2nd)              (3rd, 4th — no module deps, can be done
                                    in either order or in parallel by two
                                    agents once state.py lands)
```

**Estimated effort**: ~100 min (unchanged from v1 — the corrections above are
spec fixes, not new work).

**Verification gate after every step** (run from repo root):
```bash
python3 -c "from mcp_servers.omega_hub.server import mcp; print('OK')"
```

---

## 2. P1a-1 — `tools/` Directory Scaffold (10 min)

No change from v1.

```bash
mkdir -p mcp_servers/omega_hub/tools
touch mcp_servers/omega_hub/tools/__init__.py
```

`tools/__init__.py` stays **empty** until Phase 1b. Do not add imports yet —
an empty `__init__.py` with no imports cannot create circular-import issues
during P1a-2 through P1a-5.

**Verify**:
```bash
python3 -c "import mcp_servers.omega_hub.tools; print('OK')"
```

---

## 3. P1a-2 — Extract `state.py` (30 min)

### 3.1 Rationale

`state.py` is the leaf module: zero dependencies on other *new* modules,
only on `src/omega/`. Every other extracted module (`background.py`,
and eventually `tools/*.py`) depends on it. It must land first and must be
**complete** — if a constant or lock is missed here, P1a-3 will hit an
`ImportError` and the dependency chain breaks.

### 3.2 Complete Scope (corrected)

**Initialization state**:
```python
_init_complete: bool = False
_init_error: Optional[str] = None
```

**Service singletons** (12, all `Optional[...]`):
```python
registry: Optional[EntityRegistry] = None
model_gateway: Optional[ModelGateway] = None
oracle: Optional[Oracle] = None
hierarchy: Optional[SovereignHierarchy] = None
inbox: Optional[InboxManager] = None
curator: Optional[CurationPipeline] = None
library: Optional[Library] = None
indexer: Optional[Indexer] = None
discovery: Optional[DiscoveryOrchestrator] = None
research_engine: Optional[ResearchEngine] = None
sovereign_search_service: Optional[SovereignSearchService] = None
gateway: Optional["SovereignGateway"] = None   # see §3.4 for forward-ref handling
```

**Guard + init functions** (byte-for-byte identical bodies):
```python
def _require_service() -> None: ...
async def _init_services() -> None: ...   # all 12 `global` declarations preserved verbatim
```

**Context tracking**:
```python
_current_entity: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "_current_entity", default=None
)
```

**Intent matcher singleton** (P0-B):
```python
_intent_matcher: Optional[object] = None
_intent_matcher_lock = threading.Lock()

def _get_intent_matcher():
    """Module-level singleton accessor for IntentMatcher (P0-B)."""
    global _intent_matcher
    if _intent_matcher is None:
        with _intent_matcher_lock:
            if _intent_matcher is None:
                from omega.iris.matcher import IntentMatcher
                _intent_matcher = IntentMatcher()
    return _intent_matcher
```

**Hivemind hot/cold store**:
```python
HALL_OF_RECORDS = PROJECT_ROOT / "data" / "knowledge" / "HALL_OF_RECORDS"
HALL_OF_RECORDS.mkdir(parents=True, exist_ok=True)
_hot_store: Dict[str, Dict[str, Any]] = {}
_awareness: Dict[str, Dict[str, Any]] = {}
_hot_store_lock = anyio.Lock()
```

**Cross-event-loop lock primitive**:
```python
class _AsyncThreadLock:
    """threading.Lock wrapped for async with — safe across event loops.
    [H-A1: id-soft heritage tag removed 2026-06-09 — not a Zone Memory pattern]
    """
    def __init__(self):
        self._lock = threading.Lock()
    async def __aenter__(self):
        await anyio.to_thread.run_sync(self._lock.acquire)
        return self
    async def __aexit__(self, *args):
        self._lock.release()

_awareness_lock = _AsyncThreadLock()
```

**Heartbeat / extended session state**:
```python
HEARTBEAT_TTL = 2700  # 45 minutes

_extended_sessions: Dict[str, Dict[str, Any]] = {}
_extended_sessions_lock = _AsyncThreadLock()
EXTENDED_SAFETY_TTL_DEFAULT = 3 * 60 * 60
EXTENDED_SESSIONS_FILE = HALL_OF_RECORDS / "extended_sessions.json"

def _load_extended_sessions() -> Dict[str, Dict[str, Any]]: ...
def _save_extended_sessions(sessions: Dict[str, Dict[str, Any]]) -> None: ...

# Module-load-time side effect — preserve exactly:
_saved = _load_extended_sessions()
_extended_sessions.update(_saved)
if _saved:
    logger.info("Restored %d extended session(s) from disk", len(_saved))
```

**Background task registry** (corrected per fix #1):
```python
_background_tasks: list = []   # NO `anyio.Task` annotation — removed in P0-2
```

**NEW IN v2 — Hivemind handoff queue paths** (fix #2; previously homeless):
```python
HANDOFF_BASE = PROJECT_ROOT / "data" / "handoff"
HANDOFF_PENDING = HANDOFF_BASE / "pending"
HANDOFF_ACTIVE = HANDOFF_BASE / "active"
HANDOFF_COMPLETED = HANDOFF_BASE / "completed"
HANDOFF_STALE = HANDOFF_BASE / "stale"
HANDOFF_ARCHIVE = HANDOFF_BASE / "archive"

for d in (HANDOFF_PENDING, HANDOFF_ACTIVE, HANDOFF_COMPLETED):
    d.mkdir(parents=True, exist_ok=True)
for d in (HANDOFF_STALE, HANDOFF_ARCHIVE):
    d.mkdir(parents=True, exist_ok=True)
```

**NEW IN v2 — Workspace lock base path** (fix #2):
```python
LOCKS_BASE = PROJECT_ROOT / "data" / "coordination" / "locks"
LOCKS_BASE.mkdir(parents=True, exist_ok=True)
```

> **Why these two blocks belong in `state.py` and not `background.py`**:
> `background.py` (P1a-3) needs `LOCKS_BASE` and `HANDOFF_*` for
> `_reap_stale_locks()` / `_reap_stale_handoffs()`. Phase 1b's
> `tools/hivemind.py` needs the *same* constants for
> `hivemind_workspace_lock_*` and `hivemind_*_handoff` tools, plus
> `_find_packet_path()`. If these constants lived in `background.py`,
> `tools/hivemind.py` would have to import from `background.py` —
> creating a tools→background dependency that doesn't exist in Carmack's
> dependency graph and complicates Phase 1b's "fully parallel" extraction.
> Putting them in `state.py` (the universal dependency) keeps the graph
> clean: `state.py ← {background.py, tools/*}`.
>
> `_find_packet_path()` itself stays out of `state.py` — it's tool logic
> and moves to `tools/hivemind.py` in Phase 1b. Only the **paths** move now.

### 3.3 File Skeleton

```python
"""Omega Hub — Module-level state and service initialization.
AP: AP-OMEGA-HUB-STATE-v1.0.0

Holds all service singletons, initialization guards, hivemind hot/cold
store state, and shared filesystem paths used by background.py and the
tools/ package. This is the leaf module — it has no dependencies on any
other extracted mcp_servers.omega_hub module.
"""

import sys
import json
import logging
import threading
import contextvars
from pathlib import Path
from typing import Any, Dict, Optional, TYPE_CHECKING
import anyio

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from omega.oracle.oracle import Oracle
from omega.oracle.entity_registry import EntityRegistry
from omega.oracle.sovereign_search_service import SovereignSearchService
from omega.oracle.model_gateway import ModelGateway
from omega.oracle.hierarchy import SovereignHierarchy
from omega.oracle.health_monitor import get_health_monitor

from omega.library.inbox import InboxManager
from omega.library.curator import CurationPipeline
from omega.library.library import Library
from omega.library.indexer import Indexer
from omega.library.discovery import DiscoveryOrchestrator
from omega.library.research import ResearchEngine
from omega.memory_store import get_memory_store

if TYPE_CHECKING:
    # Avoids a runtime circular import: gateway.py will import names from
    # state.py, so state.py must not import gateway.py at module load time.
    from mcp_servers.omega_hub.gateway import SovereignGateway

logger = logging.getLogger("omega.hub")

# === INITIALIZATION STATE ===
_init_complete: bool = False
_init_error: Optional[str] = None

# === SERVICE SINGLETONS ===
registry: Optional[EntityRegistry] = None
model_gateway: Optional[ModelGateway] = None
oracle: Optional[Oracle] = None
hierarchy: Optional[SovereignHierarchy] = None
inbox: Optional[InboxManager] = None
curator: Optional[CurationPipeline] = None
library: Optional[Library] = None
indexer: Optional[Indexer] = None
discovery: Optional[DiscoveryOrchestrator] = None
research_engine: Optional[ResearchEngine] = None
sovereign_search_service: Optional[SovereignSearchService] = None
gateway: Optional["SovereignGateway"] = None


def _require_service() -> None:
    """Raise if services not ready. Called at the top of every tool."""
    if _init_error:
        raise RuntimeError(f"Hub services failed to initialize: {_init_error}")
    if not _init_complete:
        raise RuntimeError(
            "Hub services are still initializing in the background. "
            "Retry in a few seconds."
        )


async def _init_services() -> None:
    """Initialize all Hub services as a background task.
    (byte-for-byte identical body from server-snapshot.py — including the
    `global` declarations for all 12 singletons + _init_complete/_init_error.
    Do NOT split this function across modules.)
    """
    ...  # verbatim body


# === CONTEXT TRACKING (P1-A — ContextVar swap for _current_entity) ===
_current_entity: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "_current_entity", default=None
)

# === INTENT MATCHER SINGLETON (P0-B) ===
_intent_matcher: Optional[object] = None
_intent_matcher_lock = threading.Lock()


def _get_intent_matcher():
    ...  # verbatim body


# === HIVEMIND HOT/COLD STORE ===
HALL_OF_RECORDS = PROJECT_ROOT / "data" / "knowledge" / "HALL_OF_RECORDS"
HALL_OF_RECORDS.mkdir(parents=True, exist_ok=True)
_hot_store: Dict[str, Dict[str, Any]] = {}
_awareness: Dict[str, Dict[str, Any]] = {}
_hot_store_lock = anyio.Lock()


class _AsyncThreadLock:
    ...  # verbatim body


_awareness_lock = _AsyncThreadLock()

# === HEARTBEAT / EXTENDED SESSIONS ===
HEARTBEAT_TTL = 2700

_extended_sessions: Dict[str, Dict[str, Any]] = {}
_extended_sessions_lock = _AsyncThreadLock()
EXTENDED_SAFETY_TTL_DEFAULT = 3 * 60 * 60
EXTENDED_SESSIONS_FILE = HALL_OF_RECORDS / "extended_sessions.json"


def _load_extended_sessions() -> Dict[str, Dict[str, Any]]:
    ...  # verbatim body


def _save_extended_sessions(sessions: Dict[str, Dict[str, Any]]) -> None:
    ...  # verbatim body


_saved = _load_extended_sessions()
_extended_sessions.update(_saved)
if _saved:
    logger.info("Restored %d extended session(s) from disk", len(_saved))

# === BACKGROUND TASK REGISTRY ===
_background_tasks: list = []  # NOTE: no `anyio.Task` annotation (removed P0-2)

# === HIVEMIND HANDOFF QUEUE PATHS (NEW IN v2) ===
HANDOFF_BASE = PROJECT_ROOT / "data" / "handoff"
HANDOFF_PENDING = HANDOFF_BASE / "pending"
HANDOFF_ACTIVE = HANDOFF_BASE / "active"
HANDOFF_COMPLETED = HANDOFF_BASE / "completed"
HANDOFF_STALE = HANDOFF_BASE / "stale"
HANDOFF_ARCHIVE = HANDOFF_BASE / "archive"
for _d in (HANDOFF_PENDING, HANDOFF_ACTIVE, HANDOFF_COMPLETED, HANDOFF_STALE, HANDOFF_ARCHIVE):
    _d.mkdir(parents=True, exist_ok=True)
del _d

# === WORKSPACE LOCK BASE PATH (NEW IN v2) ===
LOCKS_BASE = PROJECT_ROOT / "data" / "coordination" / "locks"
LOCKS_BASE.mkdir(parents=True, exist_ok=True)


__all__ = [
    # init state
    "_init_complete", "_init_error", "_require_service", "_init_services",
    # service singletons
    "registry", "model_gateway", "oracle", "hierarchy",
    "inbox", "curator", "library", "indexer", "discovery",
    "research_engine", "sovereign_search_service", "gateway",
    # context tracking
    "_current_entity", "_get_intent_matcher",
    # hivemind store
    "HALL_OF_RECORDS", "_hot_store", "_hot_store_lock",
    "_awareness", "_awareness_lock", "_AsyncThreadLock",
    # heartbeat / extended sessions
    "HEARTBEAT_TTL", "_extended_sessions", "_extended_sessions_lock",
    "EXTENDED_SAFETY_TTL_DEFAULT", "EXTENDED_SESSIONS_FILE",
    "_load_extended_sessions", "_save_extended_sessions",
    # background tasks
    "_background_tasks",
    # handoff queue paths (NEW)
    "HANDOFF_BASE", "HANDOFF_PENDING", "HANDOFF_ACTIVE",
    "HANDOFF_COMPLETED", "HANDOFF_STALE", "HANDOFF_ARCHIVE",
    # locks (NEW)
    "LOCKS_BASE",
    # shared constants
    "PROJECT_ROOT",
]
```

### 3.4 `gateway` Forward Reference — How to Avoid the Circular Import

`state.py` declares `gateway: Optional["SovereignGateway"] = None` but the
`SovereignGateway` **class** lives in `gateway.py` (P1a-4), and `gateway.py`
will need to read/write `state.gateway`. Direct imports in both directions
would be circular.

**Resolution** (standard Python pattern):
- `state.py` only references `SovereignGateway` as a **string-quoted type
  hint**, imported under `TYPE_CHECKING` (never evaluated at runtime — see
  skeleton above).
- `gateway.py` imports the **module** `state` (not individual names) so it
  can both read and write `state.gateway`:
  ```python
  from mcp_servers.omega_hub import state
  ...
  state.gateway = SovereignGateway()   # only ever done inside _init_services()
  ```
- Runtime import direction is one-way: `gateway.py → state` (for
  `TYPE_CHECKING` only, never instantiated at import time). No cycle exists
  because `state.py`'s `TYPE_CHECKING` block never executes at runtime.

### 3.5 Verification

```bash
python3 -c "from mcp_servers.omega_hub.state import _init_services, LOCKS_BASE, HANDOFF_PENDING; print('OK')"
python3 -c "from mcp_servers.omega_hub.server import mcp; print('OK')"
```

---

## 4. ⚠️ Critical Gotcha — Module Globals vs. Imported Names

This is the single most important rule for everyone touching Phase 1a/1b/2,
and it is **not** about `state.py` itself (which is safe — see why below) —
it's a landmine for every module that comes *after* it.

### The trap

```python
# state.py
gateway: Optional["SovereignGateway"] = None

# some_other_module.py
from mcp_servers.omega_hub.state import gateway

def do_something():
    global gateway
    gateway = SovereignGateway()   # 💥 only rebinds some_other_module's
                                    #    local name `gateway` — state.gateway
                                    #    is untouched. _proxy_handler and every
                                    #    tool that reads state.gateway will
                                    #    still see None.
```

`from module import name` copies a **reference** at import time. Rebinding
that name later (`name = something_else`) does not propagate back to the
defining module — it just shadows it locally.

### Why `_init_services()` is safe

`_init_services()` is moved into `state.py` **in its entirety**, including
all twelve `global registry, model_gateway, ..., gateway` declarations.
Because the function body executes *inside* `state.py`'s namespace, every
`global X` there refers to `state.py`'s own module dict. This is correct
and requires no changes.

### The rule going forward

Any code **outside `state.py`** that needs to set/replace a service
singleton (this should essentially never happen outside `_init_services()`,
but Phase 2 hardening — e.g. `SovereignGateway.close()` lifecycle, or a
future hot-reload feature — may need it) **must** do:

```python
from mcp_servers.omega_hub import state
...
state.gateway = new_gateway_instance
```

never:
```python
from mcp_servers.omega_hub.state import gateway
...
gateway = new_gateway_instance   # WRONG — local rebind only
```

**Action item for Kali**: add this rule to `CODEBASE_COMPREHENSIVE_REVIEW.md`
or wherever Phase 2 contributors will see it before P2-1 (SovereignGateway
hardening) begins — that's the most likely place someone reaches for this
pattern.

---

## 5. P1a-3 — Extract `background.py` (30 min)

### 5.1 Scope (unchanged from v1, paths corrected per §3.2)

```python
async def _prune_awareness_background() -> None: ...
async def _run_discovery_background(job_id: str) -> None: ...
async def _reap_stale_locks() -> None: ...
async def _reap_stale_handoffs() -> None: ...
async def _reaper_background() -> None: ...

_last_pruning_cycle: Optional[str] = None   # owned here — only mutated here

async def _write_metrics() -> Dict[str, Any]: ...
METRICS_PATH = PROJECT_ROOT / "data" / "coordination" / "metrics.json"
```

### 5.2 File Skeleton

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
    PROJECT_ROOT,
    _awareness, _awareness_lock,
    _extended_sessions, _extended_sessions_lock,
    HEARTBEAT_TTL,
    HANDOFF_PENDING, HANDOFF_ACTIVE, HANDOFF_COMPLETED, HANDOFF_STALE, HANDOFF_ARCHIVE,
    LOCKS_BASE,
    discovery,
)

logger = logging.getLogger("omega.hub")

METRICS_PATH = PROJECT_ROOT / "data" / "coordination" / "metrics.json"
_last_pruning_cycle: Optional[str] = None


async def _prune_awareness_background() -> None:
    """(byte-for-byte identical body — uses module-local `global _last_pruning_cycle`)"""
    global _last_pruning_cycle
    ...


async def _run_discovery_background(job_id: str) -> None:
    """(byte-for-byte identical body — references `discovery` imported above)"""
    ...


async def _reap_stale_locks() -> None:
    """(byte-for-byte identical body — uses LOCKS_BASE imported above)"""
    ...


async def _reap_stale_handoffs() -> None:
    """(byte-for-byte identical body — uses HANDOFF_* imported above)"""
    ...


async def _reaper_background() -> None:
    ...


async def _write_metrics() -> Dict[str, Any]:
    """(byte-for-byte identical body)"""
    ...


__all__ = [
    "_prune_awareness_background",
    "_run_discovery_background",
    "_reap_stale_locks",
    "_reap_stale_handoffs",
    "_reaper_background",
    "_write_metrics",
    "METRICS_PATH",
]
```

> **Gotcha — `discovery` import**: `background.py` imports `discovery` from
> `state` at module load time, *before* `_init_services()` has run (services
> are `None` until the background init task completes). This is fine because
> `_run_discovery_background()` is never *called* until after
> `library_discovery_start` (a tool, gated by `_require_service()`) has
> already confirmed `discovery is not None`. **However**, because `from
> state import discovery` copies the `None` reference at import time, if
> `_init_services()` later sets `state.discovery = DiscoveryOrchestrator(...)`,
> `background.py`'s local `discovery` name **still points to `None`** —
> same trap as §4.
>
> **Fix**: `background.py` must reference `state.discovery` at call time, not
> import the name directly:
> ```python
> from mcp_servers.omega_hub import state
> ...
> async def _run_discovery_background(job_id: str) -> None:
>     try:
>         await state.discovery.run_discovery_task(job_id)
>     except Exception as e:
>         logger.error(f"Discovery background task {job_id} failed: {e}")
> ```
> Update the import block accordingly — `from mcp_servers.omega_hub import state`
> plus `from mcp_servers.omega_hub.state import (PROJECT_ROOT, _awareness, ...)`
> for the genuinely static names (paths, locks, dicts — these are mutable
> containers or constants, safe to import by name).

### 5.3 `server.py` Changes

```python
from mcp_servers.omega_hub.background import (
    _prune_awareness_background,
    _reaper_background,
    _run_discovery_background,
    _write_metrics,
    _reap_stale_locks,
    _reap_stale_handoffs,
)
```

### 5.4 Verification

```bash
python3 -c "from mcp_servers.omega_hub.background import _prune_awareness_background, _write_metrics; print('OK')"
python3 -c "from mcp_servers.omega_hub.server import mcp; print('OK')"
```

---

## 6. P1a-4 — Extract `gateway.py` (15 min)

### 6.1 Scope (unchanged from v1)

```python
class SovereignGateway:
    def __init__(self): ...
    async def proxy_request(self, provider_name: str, payload: Dict[str, Any]) -> Dict[str, Any]: ...

async def _proxy_handler(request: Request) -> JSONResponse: ...
```

### 6.2 File Skeleton

```python
"""Omega Hub — Sovereign Gateway HTTP proxy.
AP: AP-OMEGA-HUB-GATEWAY-v1.0.0

Phase 1a: pure mechanical extraction, byte-for-byte identical to
server-snapshot.py. Phase 2 (P2-1) will harden this with managed
httpx.AsyncClient lifecycle, CapacityLimiter rate limiting, and
SearchErrorResolver — see sovereign-gateway-spec.md. Do NOT apply
those changes here.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict
from starlette.requests import Request
from starlette.responses import JSONResponse

from mcp_servers.omega_hub import state

logger = logging.getLogger("omega.hub")


class SovereignGateway:
    """Local proxy for AI providers... (byte-for-byte identical body,
    including the inline `import httpx` in __init__ — Phase 2 TODO:
    hoist to module-level import per T4, see P2-1)."""
    def __init__(self):
        import httpx  # TODO(P2-1): hoist to module-level import
        self.client = httpx.AsyncClient(timeout=120.0)
        ...

    async def proxy_request(self, provider_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        ...  # byte-for-byte identical


async def _proxy_handler(request: Request) -> JSONResponse:
    """(byte-for-byte identical body, but reads `state.gateway`
    instead of a bare `gateway` name — see §4)."""
    provider = request.path_params.get("provider", "default")
    if state.gateway is None:
        return JSONResponse({"error": "Services still initializing", "provider": provider}, status_code=503)
    try:
        body = await request.json()
        result = await state.gateway.proxy_request(provider, body)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


__all__ = ["SovereignGateway", "_proxy_handler"]
```

### 6.3 `server.py` Changes

```python
from mcp_servers.omega_hub.gateway import SovereignGateway, _proxy_handler
```

Remove the `class SovereignGateway` definition and `_proxy_handler` function
from `server.py`. The `gateway = SovereignGateway()` instantiation **stays
inside `_init_services()`** (now in `state.py` — see §3.5/§4, this is
already correct as a `global gateway` assignment within `state.py`).

### 6.4 Verification

```bash
python3 -c "from mcp_servers.omega_hub.gateway import SovereignGateway, _proxy_handler; print('OK')"
python3 -c "from mcp_servers.omega_hub.server import mcp; print('OK')"
```

---

## 7. P1a-5 — Extract `middleware.py` (15 min)

No functional change from v1. Fully self-contained, zero state/service
dependencies.

```python
"""Omega Hub — HTTP middleware (rate limiting, request size, CORS).
AP: AP-OMEGA-HUB-MIDDLEWARE-v1.0.0
"""

import threading
from datetime import datetime
from typing import Dict, List
from starlette.middleware.cors import CORSMiddleware

logger = logging.getLogger("omega.hub")


class RateLimitMiddleware:
    """(byte-for-byte identical body)"""
    ...


class RequestSizeLimitMiddleware:
    """(byte-for-byte identical body)"""
    ...


def apply_security(app):
    """(byte-for-byte identical body)"""
    ...


__all__ = ["RateLimitMiddleware", "RequestSizeLimitMiddleware", "apply_security"]
```

`server.py` changes:
```python
from mcp_servers.omega_hub.middleware import (
    RateLimitMiddleware, RequestSizeLimitMiddleware, apply_security,
)
```

**Verification**:
```bash
python3 -c "from mcp_servers.omega_hub.middleware import apply_security; print('OK')"
python3 -c "from mcp_servers.omega_hub.server import mcp; print('OK')"
```

> **P1a-4 / P1a-5 ordering note**: unlike `state.py → background.py`, gateway
> and middleware have **zero module-level dependencies on each other**. They
> can be extracted in either order, or — if Kali wants to use a second agent
> — in parallel, *after* P1a-2 lands. Carmack's "one person owns
> `server.py`" rule (Rule 4) still applies: only Kali edits `server.py`'s
> import block, even if two agents produce `gateway.py` and `middleware.py`
> concurrently.

---

## 8. Commit & Rollback Protocol

Each of P1a-1 through P1a-5 is **one commit**. Format per T1
(`SOVEREIGN_MANDATES.md` / `temple-grade-gates.md`):

```
refactor: extract state.py from omega_hub monolith (P1a-2)
refactor: extract background.py from omega_hub monolith (P1a-3)
refactor: extract gateway.py from omega_hub monolith (P1a-4)
refactor: extract middleware.py from omega_hub monolith (P1a-5)
```

**Per-commit checklist** (Kali, before committing):
1. Run the step's verification command(s) — must print `OK`.
2. `git diff --stat` — confirm only the expected files changed
   (new module + `server.py` import block + removed inline definitions).
3. `grep` `server.py` for the names just extracted — confirm zero residual
   definitions (only the import line should reference them).
4. Boot smoke test (see §9.4).

**If a step breaks the boot**:
```bash
git revert --no-edit HEAD
```
Do **not** attempt to "fix forward" mid-extraction — revert, re-diagnose,
re-extract. This preserves Carmack's Rule 1 (server never stops responding)
and keeps git history legible for blame/bisect.

---

## 9. Expanded Verification Matrix

| # | Check | Command | Expected |
|---|-------|---------|----------|
| 1 | `tools/` package importable | `python3 -c "import mcp_servers.omega_hub.tools; print('OK')"` | `OK` |
| 2 | `state.py` exports resolve | `python3 -c "from mcp_servers.omega_hub.state import _init_services, LOCKS_BASE, HANDOFF_PENDING, gateway; print('OK')"` | `OK` |
| 3 | `background.py` exports resolve | `python3 -c "from mcp_servers.omega_hub.background import _prune_awareness_background, _write_metrics; print('OK')"` | `OK` |
| 4 | `gateway.py` exports resolve | `python3 -c "from mcp_servers.omega_hub.gateway import SovereignGateway, _proxy_handler; print('OK')"` | `OK` |
| 5 | `middleware.py` exports resolve | `python3 -c "from mcp_servers.omega_hub.middleware import apply_security; print('OK')"` | `OK` |
| 6 | No circular imports | `python3 -c "import mcp_servers.omega_hub.server" 2>&1` | no `ImportError` |
| 7 | MCP instance constructs | `python3 -c "from mcp_servers.omega_hub.server import mcp; print('OK')"` | `OK` |
| 8 | Server boots (stdio) | `timeout 3 python3 mcp_servers/omega_hub/server.py 2>&1 \| head -5` | starts listening, no traceback |
| 9 | Server boots (SSE) | `OMEGA_MCP_TRANSPORT=sse OMEGA_MCP_PORT=8016 timeout 3 python3 mcp_servers/omega_hub/server.py 2>&1 \| head -5` | starts on `:8016` |
| 10 | `state.gateway` live after init | run server briefly, hit `GET /proxy/test` after ~5s | `503` during init, `200` with `{"status":"proxied",...}` after `_init_services()` completes — **not** a permanent `503` (would indicate the §4 trap recurred) |
| 11 | Handoff dirs created on import | `python3 -c "from mcp_servers.omega_hub.state import HANDOFF_PENDING; print(HANDOFF_PENDING.exists())"` | `True` |
| 12 | Locks dir created on import | `python3 -c "from mcp_servers.omega_hub.state import LOCKS_BASE; print(LOCKS_BASE.exists())"` | `True` |

### 9.4 Boot Smoke Test Script (recommended one-off)

```bash
#!/usr/bin/env bash
set -e
echo "=== Stdio boot ==="
timeout 3 python3 mcp_servers/omega_hub/server.py 2>&1 | head -5 || true
echo "=== SSE boot ==="
OMEGA_MCP_TRANSPORT=sse OMEGA_MCP_PORT=8016 timeout 3 python3 mcp_servers/omega_hub/server.py 2>&1 | head -5 || true
echo "=== Import checks ==="
python3 - <<'EOF'
from mcp_servers.omega_hub.state import _init_services, LOCKS_BASE, HANDOFF_PENDING, gateway
from mcp_servers.omega_hub.background import _prune_awareness_background, _write_metrics
from mcp_servers.omega_hub.gateway import SovereignGateway, _proxy_handler
from mcp_servers.omega_hub.middleware import apply_security
from mcp_servers.omega_hub.server import mcp
print("ALL OK")
EOF
```

---

## 10. Post-Phase-1a `server.py` Shape

```python
# imports (~45 lines, +5 for the new module imports)
from mcp_servers.omega_hub import state
from mcp_servers.omega_hub.state import (
    _init_complete, _init_error, _require_service, _init_services,
    registry, model_gateway, oracle, hierarchy,
    inbox, curator, library, indexer, discovery,
    research_engine, sovereign_search_service,
    _current_entity, HEARTBEAT_TTL, HALL_OF_RECORDS,
    _hot_store, _hot_store_lock, _awareness, _awareness_lock,
    _extended_sessions, _extended_sessions_lock, EXTENDED_SESSIONS_FILE,
    _background_tasks, _get_intent_matcher,
    HANDOFF_PENDING, HANDOFF_ACTIVE, HANDOFF_COMPLETED, HANDOFF_STALE, HANDOFF_ARCHIVE,
    LOCKS_BASE,
)
from mcp_servers.omega_hub.background import (
    _prune_awareness_background, _reaper_background, _run_discovery_background,
    _write_metrics, _reap_stale_locks, _reap_stale_handoffs,
)
from mcp_servers.omega_hub.gateway import SovereignGateway, _proxy_handler
from mcp_servers.omega_hub.middleware import apply_security

mcp = FastMCP("Omega Core Hub")

# === 63 tool registrations (unchanged — Phase 1b target) ===
# === ~12 HTTP endpoint functions (unchanged — _health, _entity_current, etc.) ===
# === hub_routes, _on_startup, _cleanup_indexer, __main__ (unchanged) ===
```

**Estimated `server.py` size after Phase 1a**: ~1,800 lines (down from 3,110
— consistent with v1's estimate; the v2 corrections add ~25 lines to
`state.py`, not to `server.py`).

---

## 11. Dependency Map (Final)

```
state.py
  - 12 service singletons, _require_service, _init_services
  - _current_entity (ContextVar), _AsyncThreadLock
  - HALL_OF_RECORDS, _hot_store, _awareness
  - HEARTBEAT_TTL, _extended_sessions
  - _background_tasks
  - HANDOFF_* paths, LOCKS_BASE        ← NEW, shared with tools/hivemind.py (1b)
  - (leaf — zero deps on other extracted modules)
       │
       ▼
background.py
  - _prune_awareness_background, _reaper_background, _run_discovery_background
  - _reap_stale_locks, _reap_stale_handoffs, _write_metrics
  - imports: state (module, for live singleton refs) + named constants from state
       │
       ▼
gateway.py            middleware.py
  - SovereignGateway    - RateLimitMiddleware
  - _proxy_handler       - RequestSizeLimitMiddleware
  - imports: state       - apply_security
    (module, for          - imports: nothing from omega_hub
    state.gateway)
       │                      │
       └──────────┬───────────┘
                   ▼
              server.py (thin coordinator)
                   │
                   ▼
              tools/ (Phase 1b — all depend on state; hivemind.py
                       additionally uses HANDOFF_*/LOCKS_BASE from state)
```

---

## 12. Risks & Mitigations (Consolidated)

| Risk | Mitigation |
|------|-----------|
| Circular import: `state.py` ↔ `gateway.py` | `state.py` uses `TYPE_CHECKING`-guarded forward ref for `SovereignGateway`; `gateway.py` imports `state` as a module for read/write access. One-way at runtime. |
| Module-global rebind trap (§4) | `_init_services()` moves wholesale into `state.py` (all `global` decls stay valid). `background.py`/`gateway.py` read live singletons via `state.X`, not `from state import X` for anything `_init_services()` can reassign. |
| Stale `anyio.Task` annotation re-introduced | `state.py` declares `_background_tasks: list = []` — no annotation. Verified against P0-2. |
| `HANDOFF_*`/`LOCKS_BASE` homelessness | Both live in `state.py` with their `mkdir()` side effects preserved at module-load time (checks #11/#12 in §9). |
| `PROJECT_ROOT` computed inconsistently across modules | Only `state.py` computes it (`Path(__file__).resolve().parent.parent.parent`); all other modules import `PROJECT_ROOT` from `state`. |
| `__all__` incomplete → accidental internal imports | Full `__all__` lists specified in §3.3, §5.2, §6.2, §7 — Kali should diff against these before committing each step. |
| Two agents extracting `gateway.py`/`middleware.py` concurrently collide on `server.py` | Carmack Rule 4 — Kali alone edits `server.py`'s import block and removes old definitions, regardless of how many agents produce module bodies. |

---

## Verification Criteria (for this spec as a whole)

- [ ] All 12 commands in §9's matrix pass.
- [ ] `git log` shows exactly 5 commits for P1a-1..5 (or 4, if P1a-4/5 are
      combined into one commit by a single agent — acceptable, but must
      still pass checks #4 and #5 independently).
- [ ] `server.py` line count is in the 1,700–1,900 range.
- [ ] `state.gateway` transitions from `None` → `SovereignGateway` instance
      within ~5s of server start (check #10) — proves the §4 trap was
      correctly avoided.
- [ ] `HANDOFF_PENDING.exists()` and `LOCKS_BASE.exists()` both `True`
      immediately after `import state` (checks #11/#12).

## Blockers

None.

## Next Action for Kali

1. Distribute this spec (v2) in place of / alongside
   `Haiku-Phase-1a-Modularization-v1.md` — flag the four corrections in §0
   to whichever agent executes P1a-2 first, since they affect the
   `state.py` scope most.
2. Execute P1a-1 → P1a-5 in order, one commit each, running the §9 checks
   after every step.
3. Pay special attention to check #10 (`state.gateway` liveness) — this is
   the one regression class (§4) that v1 would not have caught.
4. Once all 12 checks pass and `server.py` is in the ~1,800-line range,
   Phase 1b (parallel tool extraction, `tools/oracle.py` through
   `tools/stats.py`) can begin — `tools/hivemind.py` should be told it can
   import `HANDOFF_*` and `LOCKS_BASE` directly from `state`.

---

*⬡ OMEGA ⬡ HUB-ARCHITECT ⬡ v3.0 ⬡ trc_hub_specialist ⬡ HUB-RECON-1a-v2 ⬡*
