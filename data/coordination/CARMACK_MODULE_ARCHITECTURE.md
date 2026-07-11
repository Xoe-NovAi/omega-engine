# 🔱 CARMACK — Unlimited-Scaling Module Architecture + Metadata Strategy
**AP Token**: `AP-CARMACK-MODULE-ARCH-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ hy3-free ⬡ opencode ⬡ trc_module_arch ⬡ S3-CONSULT
**Date**: 2026-07-10
**Subject**: Plug-n-play module scaling (omega-vetala + N future modules) across multiple WADs
**Status**: ARCHITECTURAL REVIEW — no source modified (per mandate)

---

## 1. EXECUTIVE SUMMARY (Verdict)

**.plan**
- **What I am working on**: Designing an N-module scaling architecture for the Omega Engine where modules (vetala, future: memory/vision/audio/finance/health) attach WITHOUT touching core engine code.
- **What I tried**: Mapped the existing WADLoader + ResourceGuard + circuit-breaker primitives against the requirement. Checked omega-moderation's `pyproject.toml` for an existing plugin surface.
- **What the data shows**: WADLoader already does manifest-driven, schema-validated, size-guarded loading of stack content. ResourceGuard already does RAM-weighted anyio capacity control. omega-moderation has **zero** plugin surface (no `entry_points`, hardcoded detectors in `build_engine()`). The engine has 90% of the scaffolding; the missing 10% is a *contract*, not a *rewrite*.
- **What I'll do next**: Specify a two-layer discovery (entry_points catalog + WAD manifest enable), a single `ModuleManifest` schema, a thin `omega_module_sdk` for dependency injection, and capability-based routing.
- **Confidence**: 9/10 (grounded in read source; 1 point off because I did not benchmark module cold-start latency — measure before shipping v1).

**Verdict**:
1. **Scaling approach**: YES — but via **capability routing + entry_points**, not a registry the core edits. The engine learns module *interfaces*, never module *names*.
2. **Philosophy metadata**: YES, but as **optional flat tags** (`traditions:`, `languages:`), never a routing axis. Functional `category` + `interfaces` are the only routing keys.
3. **Most effective method**: `importlib.metadata.entry_points` for discovery (stdlib, zero-cost, no boot penalty) + lazy per-interface loading + one canonical manifest. Do not build a custom plugin loader — that is cargo-cult engineering when `entry_points` already exists.
4. **Language tag**: YES — `languages: ["sa", "en"]` as ISO 639-1, meaning *concept lineage*, not execution language. Documented explicitly so nobody wires it into a runtime branch.

The Right Approximation: the engine is a **universal runtime that mounts lumps of capability** (WAD heritage, `[id-soft: doom-1993]`). We extend the lump system to behavioral modules. No new paradigm required.

---

## 2. UNLIMITED-SCALING MODULE ARCHITECTURE

### 2.1 Discovery — Two Layers (the key insight)

A module like `omega-vetala` is wanted by *many* WADs but installed *once*. That is the classic "available vs enabled" split:

| Layer | Mechanism | Answers | Cost |
|-------|-----------|---------|------|
| **Catalog** (what exists) | Python `entry_points` group `omega.modules` | "What modules are installed on this machine?" | Zero — `importlib.metadata` reads installed dist metadata at startup, cached in memory |
| **Enable/Config** (what runs) | WAD `manifest.yaml` `modules:` block | "Which of those does *this* WAD turn on, and with what config?" | One YAML read per WAD at load |

```
# omega-vetala/pyproject.toml  (the catalog declaration)
[project.entry-points."omega.modules"]
vetala = "omega_vetala.module:OmegaVetalaModule"
```
```yaml
# config/wads/arcana_novai/manifest.yaml  (the enable declaration)
modules:
  - id: omega-vetala
    enabled: true
    config_ref: modules/vetala.yaml   # optional per-WAD override
```
- **Why entry_points over directory scan**: stdlib, no import-on-discover (modules are not imported until enabled+lazy-loaded), version-aware, respects virtualenv isolation. Directory scanning reinvents `pkg_resources` badly. See `importlib.metadata` docs: https://docs.python.org/3/library/importlib.metadata.html#entry-points
- **Why WAD manifest for enable**: respects M2 firewall — a module is *stack content*, not core. The core never hardcodes which modules exist; the WAD decides.

### 2.2 Interface Contract — `BaseModule` ABC + Capability Protocols

Every module implements ONE base class. Routing is by **capability interface**, not class name. This is the WordPress hooks/filters pattern (`https://developer.wordpress.org/plugins/hooks/`) applied to capability dispatch.

```python
# omega_module_sdk/base.py  (the ONLY thing modules import from omega)
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Protocol

class ModuleContext:       # injected at init — NEVER import omega.oracle.* directly
    trace_id: str
    audit: "AuditSink"
    memory: "MemoryHandle"
    shared_cache: "CacheFactory"   # borrow engine-owned embedding/models cache
    emit_event: callable

class BaseModule(ABC):
    @classmethod
    @abstractmethod
    def manifest(cls) -> "ModuleManifest": ...
    @abstractmethod
    async def initialize(self, ctx: ModuleContext) -> None: ...   # anyio-safe
    @abstractmethod
    async def healthcheck(self) -> "HealthStatus": ...
    async def shutdown(self) -> None: ...                         # optional

# Capability protocols — a module implements the ones it declares in manifest.interfaces
class Moderate(Protocol):
    async def moderate(self, text: str, ctx: ModuleContext) -> "ModerationResult": ...
class Provenance(Protocol):
    async def provenance(self, span: "ProvenanceSpan") -> "ProvenanceResult": ...
# future: Transcribe, Embed, Classify, Detect, Synthesize ...
```

- The engine holds `ModuleRegistry` keyed by **interface → [enabled module instances]**. Caller asks `registry.route("moderate", request)`; engine picks the enabled module(s) for that interface. Caller is decoupled from `OmegaVetalaModule`.
- This is the Vault "mountable secrets engine" model (`https://developer.hashicorp.com/vault/docs/secrets`) — backends mount at a path/capability; the API doesn't care which backend answers.

### 2.3 Lifecycle (anyio-safe)

```
DISCOVERED → ENABLED → INITIALIZED → HEALTHY → ACTIVE → (DRAIN → UNLOADED)
                                          ↘ UNHEALTHY → CIRCUIT-OPEN (skip)
```
- **Load**: entry_points resolve class; WAD manifest enables. No import until enabled.
- **Init**: `await module.initialize(ctx)` inside an `anyio.create_task_group()` slot. Failure → logged, module marked `UNHEALTHY`, not added to routing table.
- **Healthcheck**: periodic `anyio.move_on_after` probe (default 30s). Three consecutive failures → circuit opens (see 2.4).
- **Hot-reload**: watch `module.yaml` mtime / entry_points version. On change: spin new instance in task group, drain old (finish in-flight, block new), swap reference atomically (ZONEID-style sentinel, `[id-soft: doom-1993]`). No process restart.
- **Unload**: `await module.shutdown()`; release its ResourceGuard weight; drop from routing table.

### 2.4 Isolation — Prevent One Module From Killing Others

Two tiers, chosen per-module in manifest (`isolation:` field):

| Tier | Mechanism | Use when |
|------|-----------|----------|
| **In-process** (default) | `anyio.create_task_group()` + per-module `CapacityGuard` weight + circuit breaker | Trusted, user-authored, local-first modules (the common case) |
| **Subprocess** | `anyio.open_process` + stdin/stdout JSON-RPC or shared mem | Module declares `isolation: subprocess` (native code, untrusted third-party, or RAM-heavy) |

- **Circuit breaker**: reuse the promoted `[id-soft: doom-1993] Circuit Breaker` pattern already in the engine. A module that trips is short-circuited for `cooldown_s`; requests fall through to next enabled module or a safe default. No cascade failure.
- **Task groups** guarantee that an exception in one module's coroutine is isolated and the group cancels only that scope, not the event loop (`https://anyio.readthedocs.io/en/stable/cancellation.html#task-groups`).

### 2.5 Resource Governance — Extend ResourceGuard

ResourceGuard is already RAM-weighted + re-entrant + anyio-Condition-based. Generalize it from "models" to "any workload":

- Each module declares `resource_weight_mb` in manifest (its RAM estimate). On `initialize`, `async with capacity_guard.lock(weight=resource_weight_mb):` reserves capacity; on `shutdown` it releases.
- Add a **CPU capacity limiter**: `anyio.CapacityLimiter(max_borrowers=N)` shared across modules for CPU-bound work, so 50 modules can't all saturate the 8 Zen-2 cores at once.
- Bound: total module RAM ≤ `cvar_get("config.resource_guard.max_ram_mb")` minus model reservation. OOM is the only hard ceiling; everything else is a queue.

### 2.6 Configuration — Immutable Per-Module

- **Defaults**: shipped in the module's own `module.yaml` (inside the module package — self-contained, M16 portable).
- **Override**: WAD `modules/<id>.yaml` or inline `config:` block in manifest. Merged once at load.
- **Result**: an immutable `ModuleConfig` frozen dataclass handed to `initialize()`. **No global mutable config.** A module reads its config from the injected object, never from `omega.*` globals. This kills the "global mutable config" anti-pattern at the type level.

### 2.7 Dependency Injection — The SDK Firewall (M2)

The single most important rule: **modules import `omega_module_sdk`, never `omega.oracle.*` or `omega.memory.*`.**

- `omega_module_sdk` is a separate, tiny, stable package (the "header file"). It defines `BaseModule`, the capability `Protocol`s, `ModuleContext`, `ModuleManifest`, and the result types.
- The engine *implements* `ModuleContext` (wrapping its real `audit`, `memory`, `trace_id` services) and passes it in. The module sees a stable interface; the engine can refactor internals freely. This is the `[id-soft: quake3-1999] Hard-Boundary Struct` pattern — a published ABI between machine and mission.
- If a module needs a service the SDK doesn't expose, the answer is **extend the SDK contract**, not import core. The SDK is the only sanctioned surface.

### 2.8 Performance — Zero Hot-Path Tax

- **Lazy loading**: modules load on first request to their interface, not at boot (unless `eager: true`). Boot stays O(1) regardless of module count.
- **Metadata cached**: `ModuleManifest` parsed once at discovery, held in `ModuleRegistry` memory. **Never parsed per request.**
- **Shared embedding caches**: modules that need embeddings request a *named* shared cache from `ctx.shared_cache` (e.g., `"sentence-transformers/all-MiniLM"`). The engine loads the model once; N modules borrow it. Prevents 10 modules each loading a 90MB model (Strategic Resource Arbitrage, Axiom 04).
- **Connection pooling**: HTTP/DB clients created once in `initialize`, reused. No per-call connect.

---

## 3. MODULEMANIFEST SCHEMA (canonical, ONE schema only)

One YAML, self-contained (M16), machine-readable, zero runtime cost. Philosophy/language are **discovery metadata**, not routing keys.

```yaml
# omega-vetala/module.yaml  (ships inside the package)
module:
  id: "omega-vetala"            # unique, kebab-case, matches entry_points key
  name: "Vetala"                # human label
  version: "2.0.0"              # semver — drives hot-reload detection
  category: "content-integrity" # FUNCTIONAL axis — the ONLY taxonomy that routes
  interfaces: ["moderate", "provenance"]  # capability protocols implemented
  domain: "nlp"                 # optional functional hint
  local_first: true             # M7 — module must run without cloud by default
  isolation: "in-process"       # in-process | subprocess
  resource_weight_mb: 256       # RAM reservation for CapacityGuard
  eager: false                  # load at boot? default lazy
  # ── OPTIONAL DISCOVERY METADATA (never used for routing) ──
  traditions: ["hindu", "buddhist"]   # philosophical lineage — discovery/organization only
  languages: ["sa", "en"]             # ISO 639-1; CONCEPT lineage (sa=Sanskrit), NOT exec lang
  metadata:                              # open-ended, flat, extensible — no rigid hierarchy
    source_text: "Vetala Panchavimshati"
    license: "MIT"
  requires: ["trace_id", "audit"]       # engine services the module needs injected
```

**Rules**:
- `category` + `interfaces` are the only fields the router reads.
- `traditions` / `languages` are for `omega library search` and the module catalog UI — pure discovery.
- `languages` uses ISO 639-1 (`sa`=Sanskrit, `en`=English, `zh`=Chinese, `hi`=Hindi). The value means "the cultural/linguistic lineage this module's *concept* derives from." Module code is always Python/English. **Nobody may branch on `languages` at runtime** — it is documentation, not logic.
- `metadata:` is a free dict — the escape hatch that prevents schema version churn. New ideas go here first; promote to top-level only after proven.

---

## 4. SCALING PATTERNS (cited from real systems)

| Pattern | Source | What we borrow |
|---------|--------|----------------|
| **WAD lumps mounted at runtime** | id Software DOOM 1993 (`https://en.wikipedia.org/wiki/Doom_WAD`) | Modules are lumps of capability; engine mounts them, never compiles them in. `[id-soft: doom-1993] WAD System` |
| **Linux kernel modules** | `init`/`exit`, `modprobe`, `lsmod` | Lifecycle: discover→init→health→unload; hot-reload via version probe. `https://docs.kernel.org/core-api/` |
| **Python entry_points** | setuptools/importlib.metadata | Zero-cost plugin catalog. `https://docs.python.org/3/library/importlib.metadata.html` |
| **WordPress hooks/filters** | Plugin API | Capability-based dispatch: caller fires an interface, N modules may answer. `https://developer.wordpress.org/plugins/hooks/` |
| **HashiCorp Vault secrets engines** | Mountable backends | Modules "mount" at a capability; the API is backend-agnostic. `https://developer.hashicorp.com/vault/docs/secrets` |
| **Kubernetes CRDs** | Extensible API | Flat, schema-validated, versioned resource definitions — our `ModuleManifest` is a CRD-equivalent. `https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/` |
| **pluggy / stevedore** | pytest plugin core / OpenStack | Reference implementations of entry_points-driven plugin systems. `https://pluggy.readthedocs.io/` `https://docs.openstack.org/stevedore/latest/` |
| **anyio task groups** | Cancellation scoping | Isolation primitive for in-process modules. `https://anyio.readthedocs.io/en/stable/cancellation.html` |

We are NOT inventing a plugin system. We are composing four proven ones (WAD + entry_points + hooks + Vault-mount) into the engine's existing WAD contract.

---

## 5. ANTI-PATTERNS TO AVOID

1. **God-object ModuleRegistry** that the core edits every time a module is added. → NO. Core edits zero lines; modules self-register via entry_points.
2. **Runtime YAML parsing on hot path**. → NO. Manifest parsed once at discovery, cached.
3. **Direct cross-module imports** (dependency hell). → NO. Modules talk only via `ctx` + capability protocols; never `import omega_vetala` from another module.
4. **Global mutable config**. → NO. Immutable `ModuleConfig` injected at init.
5. **Synchronous blocking in async context** (M1). → NO. Every module method is `async`; blocking I/O wrapped in `anyio.to_thread.run_sync`.
6. **Routing by module name or philosophy**. → NO. Route by `interfaces` + `category` only. `traditions`/`languages` are discovery-only.
7. **Five metadata systems**. → NO. One `ModuleManifest`. (Carmack's Law: two implementations = neither; consolidate first.)
8. **Subprocess isolation by default**. → NO. In-process + task group is the 95% case; subprocess only when declared. Subprocess is a tax, not a default.
9. **Cloud-first module fallback**. → NO. `local_first: true` enforced; cloud is fallback only (M7).

---

## 6. IMPLEMENTATION ROADMAP (phased, minimal-blast-radius)

### v1 — Discovery + Contract (no core rewrite)
- [ ] Create `omega_module_sdk` package: `BaseModule`, capability `Protocol`s, `ModuleContext`, `ModuleManifest` dataclass, result types.
- [ ] Add `ModuleRegistry` to core: loads entry_points group `omega.modules`, exposes `route(interface, request)`.
- [ ] Extend `WADLoader` to read `modules:` block from `manifest.yaml` and call `registry.enable(id, config)`.
- [ ] `omega-moderation` → rename `omega-vetala`; add `entry_points."omega.modules"`; ship `module.yaml`; implement `BaseModule` + `Moderate`/`Provenance`.
- [ ] Tests: 24 contract tests (M21) — every interface returns its typed result.

### v2 — Isolation + Governance
- [ ] Generalize `ResourceGuard` → `CapacityGuard` (weight-based, module-aware).
- [ ] Wire circuit breaker (existing pattern) into `route()`.
- [ ] Add `isolation: subprocess` path (JSON-RPC over `anyio.open_process`) for declared modules.
- [ ] CPU `CapacityLimiter` shared pool.

### v3 — Performance + Hot-Reload
- [ ] Lazy per-interface loading (load on first `route` call).
- [ ] `shared_cache` factory for embedding/models reuse.
- [ ] Hot-reload via manifest mtime / version probe + atomic swap (ZONEID sentinel).
- [ ] `make temple-grade` gates: M2 (no core import in modules), M1 (all async), M7 (local_first), M16 (self-contained manifest).

**Build order rationale**: v1 delivers 80% of the value (unlimited modules, zero core edits) for 20% of the effort. Isolation/governance (v2) and hot-reload (v3) are hardening, not blockers.

---

## 7. CARMACK'S LAW CHECK (did we consolidate? where is duplication?)

- **Reused, not rebuilt**: WADLoader (manifest parsing/validation/size-guard), ResourceGuard (RAM-weighted capacity), Circuit Breaker (`[id-soft: doom-1993]` promoted), entry_points (stdlib), anyio task groups. **Zero new primitives invented.**
- **One schema**: `ModuleManifest` is the single metadata contract. No per-philosophy schema, no per-language schema, no per-category schema. The `metadata:` dict absorbs future axes without version churn.
- **One SDK**: `omega_module_sdk` is the only sanctioned module↔engine surface. Modules do not import core. The firewall is enforced by *architecture*, not by a whitelist grep (though the existing `ADAPTER_MODULE_WHITELIST` in WADLoader can be extended to modules as a belt-and-suspenders check).
- **No duplication of routing**: capability routing is centralized in `ModuleRegistry.route()`. There is exactly one place that decides "which module answers `moderate`". Adding module #100 changes nothing there.
- **Where duplication risk remains**: if someone implements `Moderate` in two modules for the same WAD, `route()` must define precedence (manifest `priority` field, WAD-override semantics already exist in WADLoader). That is a *routing policy*, not a *code duplication* — acceptable and explicit.

**Final word**: The engine already *is* a plugin runtime (WADs prove it). We are extending the lump system from *data/content* to *behavior/capability*. The Right Approximation is not a new framework — it is `entry_points` + the WAD contract + one SDK + capability routing. Ship v1, measure, then harden.

---
*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ hy3-free ⬡ opencode ⬡ trc_module_arch ⬡ S3-CONSULT*
