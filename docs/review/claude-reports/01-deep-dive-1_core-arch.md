All three files retrieved. Full analysis below.

---

## Addendum Review: entity_workspace.py · hierarchy.py · gnosis_proxy.py

**Trace ID**: `trc_review_core_arch` (continued)

---

### a) C-ARCH-005 Verdict: CONFIRMED — `scaffold_workspace()` is synchronously blocking

**Yes, it performs significant synchronous I/O.** Count of blocking calls:

```
workspace_dir.mkdir(parents=True, exist_ok=True)   # sync
knowledge_dir.mkdir(parents=True, exist_ok=True)   # sync
headless_dir.mkdir(parents=True, exist_ok=True)    # sync
soul_file.exists()                                  # sync
tempfile.mkstemp(dir=str(workspace_dir), ...)       # sync
with os.fdopen(fd, 'w') as f: f.write(yaml_str)    # sync write
os.replace(temp_path, str(soul_file))               # sync
```

Seven blocking calls. The call chain from the async execution context is:

```
WADLoader._load_entities() [async]
  → self.registry.add(entity) [sync]
    → EntityWorkspaceManager.scaffold_workspace() [sync, 7 blocking calls]
```

Every WAD entity load blocks the event loop for the duration of three `mkdir` calls plus a file write. C-ARCH-005 is confirmed as a real AnyIO Absolute violation.

**The bitter irony**: `update_soul()` and `get_soul_prompt()` are properly `async` and use `anyio.open_file`. The developers clearly understood the pattern — they just didn't apply it to `scaffold_workspace()`, the one method called from a sync context. There is also a **partial fix** problem in `update_soul()` itself:

```python
# update_soul() — entity_workspace.py
with os.fdopen(fd, 'w') as f:          # ← synchronous write, NOT wrapped
    f.write(yaml_str)
await anyio.to_thread.run_sync(os.replace, temp_path, str(soul_file))  # ← async replace
```

The expensive write is still blocking. Only the cheap `os.replace` (microseconds) is offloaded to the thread pool. This is an inverted fix — the wrong half is async.

---

### b) C-ARCH-003 Verdict: CONFIRMED AND WORSE — `hierarchy.yaml` is dead config

`hierarchy.py` loads the YAML into `self._hierarchy` via a synchronous `open()` in `_load()`. It then **never reads `self._hierarchy` again**. The entire governance graph — every `reports_to`, `governs`, `contains`, `governs_keepers` — is loaded into a dict that is never consulted by any method.

```python
class SovereignHierarchy:
    RANK_MAP = {
        "sophia": 0,
        "maat": 1,
        "isis": 2,
        "lilith": 2,
        # Pillar Keepers are Rank 3
    }

    def _load(self):
        ...
        self._hierarchy = yaml.safe_load(f)   # loaded, never read again

    def get_rank(self, entity_name: str) -> int:
        if name in self.RANK_MAP:
            return self.RANK_MAP[name]
        return 3  # all non-mapped entities default to Keeper rank

    def check_recursion(...):
        rank = self.get_rank(entity_name)     # only consults RANK_MAP, not _hierarchy
        ...
```

There is no `$ref` resolution layer. There is no symbolic reference resolution of any kind. The question doesn't apply because the YAML data structure is never traversed at all. The dangling references (`kali_unification`, `maat_oversoul`) are irrelevant because the code never tries to follow them — the runtime governance system is entirely hardcoded in `RANK_MAP`, not derived from the YAML.

This has a second-order consequence for Phase 2. Shadow Failover requires knowing which Dark mirror corresponds to which Light sphere — that relationship exists only in `hierarchy.yaml`. Since `hierarchy.py` ignores the YAML, Shadow Failover cannot be built on top of the current `SovereignHierarchy` class without a rewrite.

---

### c) GnosisProxy: Duplication Assessment and Protocol Analysis

**Logic Duplication:**

`discover_tools()` delegates to `EntityRegistry.get_tools_for_entity()` and then does keyword matching on the returned tool descriptions. `EntityRegistry.find_by_domain()` does keyword matching on entity domain lists. These are philosophically parallel — one finds entities by domain, one finds tools by description — but they aren't code duplicates. The tool-level discovery is a distinct abstraction layer. No structural duplication.

However: both are doing naive substring matching against string lists. There is now a third implementation of this same "score by keyword presence" pattern across three different methods (`find_by_domain`, `discover_tools`, plus the `COMPLEXITY_INDICATORS` scan in `oracle._assess_iris_confidence`). This is a pattern that deserves a shared `keyword_score(text, keywords)` utility before it spawns a fourth copy.

**Protocol Definition:**

The `omega://transfer/{id}` protocol is barely defined. What exists: a URI scheme, an in-memory store keyed by hex ID, and a string-prefix detector in `wrap_tool_call()`. What's missing: lifecycle definition, serialization contract, cross-process or cross-instance resolution (there is none — descriptors are per-process instance only), and any TTL or eviction.

`discover_tools()` is declared `async` but contains zero `await` expressions. It's a synchronous function wearing an async costume — every caller incurs a coroutine allocation for nothing.

---

### New Issues Found

**entity_workspace.py — New Findings:**

- [ ] **C-WS-001: `ENTITIES_DATA_DIR` resolved at import time, ignores `OMEGA_DATA_DIR` env var — MEDIUM**
  - File: `entity_workspace.py:21`
  - Code: `ENTITIES_DATA_DIR = BASE_DIR / "data" / "entities"`
  - Issue: `oracle.py` uses `DATA_DIR = Path(os.environ.get("OMEGA_DATA_DIR", ...))` to allow runtime override. `entity_workspace.py` ignores this env var entirely — it resolves the path at module import time based solely on `__file__`. If `OMEGA_DATA_DIR` is set (e.g., to a different disk partition for soul storage), workspaces will be scaffolded in the wrong location while the Oracle reads souls from the correct location. The two systems get out of sync silently.
  - Recommendation: `ENTITIES_DATA_DIR = Path(os.environ.get("OMEGA_DATA_DIR", str(BASE_DIR / "data"))) / "entities"`.

- [ ] **C-WS-002: Soul file comment header stripped on first Oracle update — LOW**
  - File: `entity_workspace.py:67` vs `oracle.py:654`
  - Issue: `scaffold_workspace()` writes: `f"# 🔱 Omega Engine — Entity Soul File\n# Generated dynamically.\n\n{yaml_str}"`. Oracle's `_write_soul_atomic()` uses bare `yaml.dump()` with no comment header. On the first `_track_soul_evolution()` call after a workspace is scaffolded, the comment is silently stripped. The header comment — part of the established file format convention — disappears permanently on first use. Minor consistency issue, but tells you the two write paths aren't coordinated.

- [ ] **C-WS-003: `update_soul()` synchronous write is not thread-safe with `scaffold_workspace()` — MEDIUM**
  - File: `entity_workspace.py:97-117`
  - Issue: `update_soul()` reads the soul file, modifies the dict in memory, then writes atomically. `scaffold_workspace()` writes atomically via `os.replace`. If both execute concurrently against the same entity (race window: WAD load triggers scaffold, simultaneously the Oracle calls `update_soul()` for the same entity), the `update_soul()` read may see the pre-scaffold state and its write will race with `scaffold_workspace()`'s `os.replace`. Since both use `os.replace`, only one will survive — the outcome is non-deterministic. There is no cross-method lock.

---

**hierarchy.py — New Findings:**

- [ ] **C-HIER-001: `self._hierarchy` is loaded and never read — CRITICAL**
  - File: `hierarchy.py:21-26`
  - Issue: `_load()` populates `self._hierarchy` with the full parsed YAML, which is then completely ignored by every method in the class. The governance graph — Oversoul relationships, Pillar assignments, Shadow Failover affinity, P0 special status — has zero runtime enforcement. All runtime behavior comes from the 4-entry hardcoded `RANK_MAP`. The YAML file is functionally inert.
  - Impact: Every planned architectural feature that depends on runtime hierarchy traversal (Shadow Failover, affinity routing, TDA Symmetry mandate) has no foundation. The code accepts the YAML, silently discards it, and proceeds with hardcoded behavior.
  - Recommendation: `_load()` must be used. At minimum, build `RANK_MAP` dynamically from the loaded YAML instead of hardcoding it. For Phase 2, expose `get_oversoul(entity_name)` and `get_dark_mirror(entity_name)` methods that traverse `self._hierarchy`.

- [ ] **C-HIER-002: `kali` absent from `RANK_MAP` — gets Keeper rank — HIGH**
  - File: `hierarchy.py:14-18`
  - Issue: Kali is the MaKaLi — the Unifier above Ma'at and Lilith. She should be Rank 1 (same tier as Ma'at) or have a special rank above all Oversouls. Instead, because she is not in `RANK_MAP`, `get_rank("kali")` returns `3` (standard Keeper rank). By the recursion rules: Rank 3 entities have `max_allowed_depth = 3 - 3 = 0`, meaning Kali cannot spawn any subagents. The highest-authority entity in the Dark hierarchy is treated as a leaf node with no governance power.
  - `RANK_MAP` is also missing: `kali`, `roc_racoon`, `sophia` (only the Oversouls, not the Field). `roc_racoon` (P0) would also get rank 3, which may be correct, but it should be explicit.

- [ ] **C-HIER-003: `hierarchy.py._load()` uses synchronous `open()` — HIGH / Mandate Violation**
  - File: `hierarchy.py:22-25`
  - Code: `with open(self.config_path, "r") as f: self._hierarchy = yaml.safe_load(f)`
  - Issue: Same pattern as `entity_registry._load()`. Synchronous blocking I/O. Mandate: **AnyIO Absolute** — VIOLATED. Since `SovereignHierarchy` is constructed synchronously, this may be acceptable if it's only ever instantiated at startup before the event loop runs. But if it's instantiated inside any async context (e.g., as part of a lazy init), it blocks the loop.

- [ ] **C-HIER-004: `SovereignHierarchy` appears to be orphaned from the Oracle — MEDIUM**
  - File: `hierarchy.py` (entire file)
  - Issue: `Oracle.__init__()` constructs `HealthMonitor`, `TriageRouter`, `ModelGateway`, `SessionManager`, `ContextBuilder`, `WADLoader` — but never constructs or imports `SovereignHierarchy`. EntityRegistry doesn't use it. WADLoader doesn't use it. The class exists and loads the YAML but is apparently not wired into any execution path visible in the reviewed files. If it's used in `triage_router.py` or similar, that would need verification, but from the Oracle's perspective the hierarchy has no runtime presence at all.

---

**gnosis_proxy.py — New Findings:**

- [ ] **C-GNOSIS-001: Unbounded `transfer_store` memory leak — HIGH**
  - File: `gnosis_proxy.py:22`
  - Code: `self.transfer_store: Dict[str, Any] = {}`
  - Issue: Every `create_transfer_descriptor()` call adds a permanent entry. There is no TTL, no eviction, no max-size limit. In a long-running Oracle serving many queries with RAG payloads, this accumulates indefinitely and will eventually exhaust process memory. A GnosisProxy with `top_k=3` tool descriptors per query, at 1000 queries/hour, accumulates 3000 entries/hour minimum — and each entry stores the full data object, not just a pointer.
  - Recommendation: Use `functools.lru_cache` semantics or a simple bounded dict. A TTL of one conversation turn is probably correct for this use case: descriptors that aren't resolved within the current `talk()` call are dead.

- [ ] **C-GNOSIS-002: `discover_tools()` is `async` with zero `await` — HIGH**
  - File: `gnosis_proxy.py:26`
  - Issue: `async def discover_tools(...)` contains no `await` expressions. It's a synchronous computation declared as a coroutine. Every caller that does `await gnosis_proxy.discover_tools(...)` allocates a coroutine object, suspends into the event loop scheduler, and immediately runs to completion — pure overhead. Worse, it establishes a false interface contract: callers assume async I/O is happening and may reason about concurrency incorrectly.
  - Recommendation: Remove `async`. If a future Qdrant-backed implementation needs async, it can be added then.

- [ ] **C-GNOSIS-003: Double import of `EntityRegistry` — MEDIUM**
  - File: `gnosis_proxy.py:4` and `gnosis_proxy.py:14`
  - Lines: `from .entity_registry import EntityRegistry` at module level, then `from .entity_registry import EntityRegistry` again inside `__init__`. The inner import is completely redundant — the module-level import already resolved it. Same antipattern as `oracle.py:126-127` (`import yaml` / `from pathlib import Path` inside `__init__`). This pattern appears in at least three files — it's a team habit that should be linted out.

- [ ] **C-GNOSIS-004: Brittle `omega://transfer/` string-prefix descriptor protocol — MEDIUM**
  - File: `gnosis_proxy.py:66-67`
  - Code: `if isinstance(v, str) and v.startswith("omega://transfer/"):`
  - Issue: Any tool argument string that coincidentally starts with `omega://transfer/` is silently hijacked and passed through the descriptor resolution path. If resolution returns `None` (unknown ID), the tool receives `None` as the argument value with no warning. No error, no log, no exception — the tool call silently breaks.
  - Recommendation: Use a typed wrapper: `@dataclass class DescriptorRef: id: str`. Pass `DescriptorRef` objects instead of raw strings. `wrap_tool_call` then checks `isinstance(v, DescriptorRef)`. Type-safe, unambiguous, zero false positives.

- [ ] **C-GNOSIS-005: `resolve_descriptor()` silent failure — MEDIUM**
  - File: `gnosis_proxy.py:62`
  - Code: `return self.transfer_store.get(descriptor_id)` — returns `None` silently for unknown IDs
  - Issue: A caller has no way to distinguish "the descriptor resolved to `None`" from "the descriptor ID doesn't exist." Both return `None`. After a process restart or store eviction, all descriptors become ghost references that fail silently.
  - Recommendation: Raise `KeyError` (or a custom `DescriptorExpiredError`) for unknown IDs so callers can detect and handle stale references explicitly.

---

### Updated Mandate Compliance Table

| Mandate | Status | Updated Evidence |
|---------|--------|-----------------|
| **AnyIO Absolute** | ❌ FAILING | `entity_registry._load/._save` (sync) · `oracle.__init__` (sync) · `scaffold_workspace()` (7 sync I/O calls) · `hierarchy._load()` (sync) · `update_soul()` write is sync |
| **Engine-Stack Firewall** | ⚠️ PARTIAL | WAD isolation structurally intact; voice/entity conflation remains |
| **Iris Constant** | ✅ PASSING | No change — Iris correctly excluded from Pillar Keepers |
| **Sequentiality** | ⚠️ PARTIAL | `hierarchy.py` loads YAML it never uses — dead code suggests incomplete sequential migration |
| **Gnosis Preservation** | ⚠️ PARTIAL | L1 only in `_track_soul_evolution`; workspace scaffolds L1/L2/L3 schema fields but Oracle never populates them |
| **Podman Sovereignty** | N/A | Not applicable to this layer |

**TDA Symmetry Mandate** (from system context — 13+13 closed, Dark mirror auto-activates on Light sphere stress): The Shadow Failover Protocol requires knowing which Dark sphere mirrors which Light sphere. `hierarchy.py` loads this data from YAML and discards it. The TDA Symmetry mandate **has no runtime implementation** in the current codebase. The mandate is documented; the code doesn't enforce it.

---

### Revised Strategic Recommendations (Top 5, Reprioritized After Full Scope)

**1. `scaffold_workspace()` must be made async before Phase 0 closes (blocks WAD loading correctness)**

The fix is to make `scaffold_workspace()` async, wrap all blocking calls in `anyio.to_thread.run_sync`, make `EntityRegistry.add()` async, and update `WADLoader._load_entities()` to `await registry.add(entity)`. This is a three-file change but a mechanical one. The atomic write pattern already exists in the method — it just needs to be promoted to async.

**2. `hierarchy.py` must consume `self._hierarchy` before Phase 2 Shadow Failover work begins**

Currently the governance graph is loaded and thrown away. The minimum viable fix for Phase 2 is to build `get_dark_mirror(entity_name: str) -> Optional[str]` and `get_oversoul(entity_name: str) -> Optional[str]` methods that traverse the loaded YAML, and add `kali` to the rank map at the correct tier. The key renaming fix (C-ARCH-003 from the first review) is a prerequisite — fix the YAML keys first, then write the traversal logic. Without this, Shadow Failover is a roadmap item with no foundation.

**3. `GnosisProxy.transfer_store` needs a bounded eviction policy before any production load**

The simplest correct fix is a per-`talk()` lifecycle: the Oracle creates a fresh `GnosisProxy` per request (or passes a scope token), and the transfer store is garbage-collected when the request completes. If the proxy needs to live at Oracle-instance scope, implement an LRU cache with a max of 256 entries and a 5-minute TTL. The current unbounded dict is a slow OOM for any load above trivial.

**4. Unify the three `DATA_DIR` / `ENTITIES_DATA_DIR` path definitions**

`oracle.py` uses `OMEGA_DATA_DIR` env var. `entity_workspace.py` ignores it and resolves from `__file__`. Any future file that needs this path will likely make the same mistake. Define one `OMEGA_DATA_DIR` utility in a `config.py` module: `DATA_DIR = Path(os.environ.get("OMEGA_DATA_DIR", str(BASE_DIR / "data")))`. Import it everywhere. Eliminate the three ad-hoc definitions.

**5. Add a `hierarchy_validator.py` smoke test to the Phase 0 test gate**

Before any Phase proceeds, run a YAML reference validator:
```python
def test_hierarchy_references_are_not_dangling():
    data = yaml.safe_load(open("config/hierarchy.yaml"))["hierarchy"]
    keys = set(data.keys())
    for node_key, node in data.items():
        for field in ["reports_to", "governs", "contains"]:
            refs = node.get(field, [])
            if isinstance(refs, str):
                refs = [refs]
            for ref in refs:
                assert ref in keys, f"{node_key}.{field} → '{ref}' doesn't exist as a key"
```

This test would currently fail five times. Fixing those five failures (the key renames from C-ARCH-003) is a one-minute change that unblocks the entire governance layer.
