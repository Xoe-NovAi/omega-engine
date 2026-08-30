<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 KALI → OpenCode Dev Session — Complete Handoff
# ⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_kali_handoff ⬡ PHASE-I
# Status: Sprint 1 READY — All findings integrated, one architectural correction applied

**For**: OpenCode/M3 Dev Session (200K context, parallel channel)
**From**: Kali/MaKaLi (acting as Cline proxy — user chose to stay in OpenCode)
**Date**: 2026-06-03
**HEAD**: `37fdd88` — feat: T2.1 ZONEID constants + T2.3 lazy deletion + heritage tagging protocol
**Test status**: 307 passing, 1 warning (pre-existing ResourceWarning)

---

## §0 — The One-Minute Handoff

1. **T2.1 ZONEID + T2.3 Lazy deletion** are DONE and committed (`37fdd88`). 5 constants, 5 subsystems, tombstone with 0.5s grace.
2. **T2.2 cvar table** design was WRITTEN by Doom Guy, REVIEWED by Kali, and has **one architectural correction** — it must UNIFY with the ZONEID_TABLE pattern, not duplicate it.
3. **Roc Racoon mining** is COMPLETE — 160+ techs across 6 stacks, 7 reports. 5 priority ports identified (1.5 hr total, all LOW risk).
4. **Sprint 0 C1-C4** verified: Oracle `bootstrap()` guards 3 entry points, Makefile test target exists, PIVOT_LOG D92 present, CI workflow runs.
5. **Heritage protocol** is live — `[id-soft:]` inline tags on 30+ sites across 6 source files. `make heritage-map` CI target needs to be created.
6. **Next**: Sprint 1 — the 5 priority ports ported into a unified `cvar_table.py`. ~2.5 hrs, all LOW risk.

---

## §1 — What We Built (Completed Since Your Last Context)

### 1.1 T2.1 ZONEID Constants (commit `37fdd88`, `src/omega/constants.py`)

**5 magic constants** in the 0x1d4aXX family (id Software's original ZONEID prefix):

| Constant | Value | Subsystem | What It Protects |
|----------|-------|-----------|-----------------|
| `ZONEID_MEMORY` | `0x1d4a11` | `memory_store.py` | Exchange dict integrity (load/save) |
| `ZONEID_ENTITY` | `0x1d4a12` | `entity_registry.py` | Entity dataclass validation (get/add/remove) |
| `ZONEID_BREAKER` | `0x1d4a13` | `health_monitor.py` | Circuit breaker state transitions |
| `ZONEID_TRACE` | `0x1d4a14` | `observability.py` | Event lineage in `log_event()` payload |
| `ZONEID_PROBE` | `0x1d4a15` | `resource_guard.py` | Critical section entry in `lock()` |

**Plus one sentinel**:
| `ZONEID_TOMBSTONE` | `0xDEADBEEF` | `entity_registry.py` | Lazy deletion marker |

**Validation helper**:
```python
def validate_zoneid(value: int, expected: int, context: str = "") -> None:
    """ZONEID check — direct translation of id Software's z_magic/ZONEID.
    In C: ``if (block->z_magic != ZONEID)`` — a 4-byte comparison.
    In Python: catches serialization corruption, stale references, wrong-type loads.
    """
```

**Files modified**: `constants.py`, `entity_registry.py`, `memory_store.py`, `health_monitor.py`, `resource_guard.py`, `observability.py`

### 1.2 T2.3 Lazy Deletion (commit `37fdd88`, `entity_registry.py`)

Architecture change. Before: `remove()` did `del self._entities[key]` + `_save()` immediately. After:

```python
async def remove(self, name: str) -> bool:
    """[id-soft: doom-1993] Lazy Deletion — sets ZONEID_TOMBSTONE instead of deleting.
    [id-soft: quake-1996] Grace Period — 0.5s delay before actual reaping.
    """
    entity.magic = ZONEID_TOMBSTONE
    self._tombstoned[key] = time.monotonic()
    await self._save()  # _save() calls _reap_tombstoned() first
    return True

def _reap_tombstoned(self, grace_seconds=TOMBSTONE_GRACE_SECONDS=0.5) -> int:
    """Remove tombstoned entities past the grace period. Called before every _save()."""

def active_iter(self) -> List[Entity]:
    """Returns only entities where magic != ZONEID_TOMBSTONE."""
```

**All public accessors updated** to use `active_iter()`: `list()`, `list_pillar_keepers()`, `names()`, `get_all()`, `get_by_wad()`. Only `get_wad_sources()` still returns tombstoned provenance (debugging).

### 1.3 Heritage Tagging Protocol (CREDITS.md §2a)

**The format**:
```
# [id-soft: GAME YEAR] Pattern Name — why this code exists
```

**Game codes**: `doom-1993`, `quake-1996`, `quake2-1997`, `quake3-1999`, `doom3-2004`, `doom3bfg-2012`, `wolf3d-2012`

**30+ tags backfilled** across:
- `constants.py` — 6 tags (ZONEID constants + tombstone)
- `entity_registry.py` — 10 tags (ZONEID + lazy deletion + dual-linking)
- `memory_store.py` — 2 tags (ZONEID marker)
- `health_monitor.py` — 3 tags (ZONEID marker + state transition)
- `resource_guard.py` — 3 tags (ZONEID marker + lock entry)
- `observability.py` — 1 tag (ZONEID trace event)

**Missing**: `make heritage-map` CI target. Protocol is live but unenforced. Must be created in Sprint 1.

---

## §2 — The Architectural Correction (Must Adopt Before Proceeding)

### What Doom Guy's Design Doc Proposed

A NEW `cvar_table.py` module with config values (n_ctx, n_threads, inference.strategy, etc.) as a SECOND static table, separate from the ZONEID_TABLE in `constants.py`.

### Why This Is Wrong

The ZONEID_TABLE in `constants.py` IS ALREADY a cvar table:

```python
ZONEID_TABLE = {
    "memory": {"id": ZONEID_MEMORY, "subsystem": "MemoryStore", "description": "Memory load/save integrity"},
    "entity": {"id": ZONEID_ENTITY, "subsystem": "EntityRegistry", "description": "Entity dataclass validation"},
    # ... 6 entries total
}
```

Same structure (name → value + metadata + subsystem). Same pattern (static table, subsystem routing). Creating a second module for config values violates **Carmack's Law** — *"When you have two implementations of the same thing, you have neither."*

### The Fix

**Unify both into ONE module: `cvar_table.py`**

```
cvar_table.py:
  ├── namespace "zoneid.*"    — ZONEID constants (magic values, integrity markers)
  │      zoneid.memory     = 0x1d4a11
  │      zoneid.entity     = 0x1d4a12
  │      zoneid.breaker    = 0x1d4a13
  │      zoneid.trace      = 0x1d4a14
  │      zoneid.probe      = 0x1d4a15
  │      zoneid.tombstone  = 0xDEADBEEF
  │
  ├── namespace "config.*"   — User-tunable knobs (YAML-backed)
  │      config.gguf.n_ctx       = 4096
  │      config.gguf.n_threads   = 6
  │      config.inference.strategy  = "local_first"
  │      # ... first 5 entries are the Roc Racoon priority ports
  │
  ├── CvarDef dataclass         — Single type for ALL entries
  │      name: str
  │      type: type
  │      default: Any
  │      description: str
  │      bounds: Optional[tuple]  # for numeric cvars
  │      enum: Optional[list]     # for string cvars
  │      secret: bool             # API keys, masked in logs
  │      modification_count: int  # Q3A heritage
  │
  ├── validate_zoneid()         — Retained as-is, moved to cvar_table.py
  ├── CvarTable runtime         — Loads YAML, typed access, modificationCount
  └── ZONEID_TABLE              — Named entries for discovery / CI
```

**Migration**: `constants.py` becomes a thin re-export layer:

```python
# constants.py -> re-export layer for backward compatibility
from cvar_table import (
    ZONEID_MEMORY, ZONEID_ENTITY, ZONEID_BREAKER,
    ZONEID_TRACE, ZONEID_PROBE, ZONEID_TOMBSTONE,
    validate_zoneid, ZONEID_TABLE,
)
```

### Why This Matters Now

The 5 Roc Racoon priority ports ARE the first entries in the `config.*` namespace. Every port adds an entry. If we build the cvar table first as a unified module, the ports naturally flow into it. If we build them separately, we create merge conflicts and architectural drift.

---

## §3 — Roc Racoon Mining Completion (Parallel Session)

### What Was Mined

| Phase | Stack | Key Findings | Techs |
|-------|-------|-------------|-------|
| 1 | xna-omega-legacy | LocalLlmClient, HP-5700U optimization, Moondream2 vision, 7 never-do gotchas | 60+ |
| 2 | omega-stack-legacy | NativeGGUFProvider pattern, Vulkan Dockerfile, circuit_breaker.py 36L, EnhancedEntityHandler | ~30 |
| 2.5 | expert-knowledge/ | KV cache Q8_0, Zen 2 pinning, OMP_NUM_THREADS=6, UV_HTTP_TIMEOUT fix | 20 |
| 3 | foundation-legacy | pybreaker, check_telemetry(), 5 mandatory design patterns framework | ~30 |
| 4 | podman-storage | 152 overlay layers = TIME MACHINE of engine evolution. 3 providers.py + 4 model_gateway.py + 552-line cpu_optimizer.py | ~32 |
| 5 | Cursor.old | **SKIPPED** — false positive (editor user data, not code) | 0 |
| 6 | Old-Stacks/Xoe-NovAi | **4-service Docker Compose** redis+rag+ui+crawler (the provenance for Omega's Podman Quadlets). Ryzen CMAKE_ARGS pattern. **CRITICAL**: redis_password.txt plaintext secret (Mandate 6 violation, already resolved in current engine) | ~25 |

### The Convergence Finding (Most Important)

**5 independent eras** (xna-omega, omega-stack, foundation, podman-storage, Old-Stacks) all converged on the SAME architecture: llama-cpp primary + 4-service containers + circuit breaker fail_max=3/reset=60 + Zen 2 build flags + YAML+atomic fsync + local-first provider chain.

**73 of ~140 patterns already ported** to the current engine. This is empirical proof of architectural correctness.

### The 5 Priority Ports (Sprint 1)

| # | Port | Legacy Source | Effort | Cvar Entry |
|---|------|--------------|--------|------------|
| 1.1 | `filter_llama_kwargs()` | Old-Stacks filter_llama_kwargs | 30 min | `config.gguf.kwarg_filter` |
| 1.2 | Explicit `n_gpu_layers=0` | HP-5700U-OPTIMIZATION.md:117 | 5 min | `config.gguf.n_gpu_layers` |
| 1.3 | ChatML stop tokens | xna-omega-legacy client.py:60-67 | 5 min | `config.gguf.stop_tokens` |
| 1.4 | Google API key header | podman-storage providers.py | 15 min | `config.providers.google.auth_header` |
| 1.5 | Atomic trace_id migration | podman-storage model_gateway.py | 30 min | `config.observability.trace_id_header` |

**Total: 1 hr 25 min. All LOW risk.**

### Additional Deferred Gold (Tracked in DEFERRED_GOLD_TRACKER.md, 451 lines)

Key deferred items: Vulkan iGPU offload (🔵 EXPERIMENTAL), Moondream2 vision (🟡 deferred), dynamic model swap with Krikri (⚪ LEGACY), tenacity retry library (🟡 deferred), per-entity model affinity (🟢 READY-FOR-IMPORT), llama-bench wrapper (🟡 deferred).

---

## §4 — Sprint 0 Verification (C1-C4)

Verified against actual filesystem. All four tasks complete.

| Task | Description | Verification | Status |
|------|-------------|-------------|--------|
| **C1** | Oracle bootstrap guard | `bootstrap()` called from `talk():291`, `summon():353`, `evolve_soul():875`. Idempotent via `_wads_loaded` flag. | ✅ |
| **C2** | Makefile test-oracle-bootstrap | Makefile:355-357 — `@OMEGA_ENV=test $(PYTHON) -m pytest tests/test_oracle.py -v -k "bootstrap or summon or talk"` | ✅ |
| **C3** | PIVOT_LOG D92 | `grep "Decision 92:" PIVOT_LOG.md` → 1 match (Tool-Usage Discipline, 2026-06-02) | ✅ |
| **C4** | CI workflow | `.github/workflows/test.yml` exists (2818 bytes, Mandate 1 + 9 checks) | ✅ |

---

## §5 — Heritage Status (PENDING_CREDITS_QUEUE.md)

### Frozen at 37fdd88

| Pattern | R-Doc | Status | Sprint | Target File |
|---------|-------|--------|--------|-------------|
| ZONEID Constants | R-19 | ✅ **DONE** | Sprint 0 | → `cvar_table.py` (re-export via constants.py) |
| Lazy Deletion | R-20 | ✅ **DONE** | Sprint 0 | `entity_registry.py` |
| cvar Table | R-22 | 🔄 **Design reviewed, correction applied** | Sprint 1 | `cvar_table.py` (NEW — UNIFIED) |
| Grace Period | R-30 | ⚡ **Partial** | Sprint 3 | `memory_store.py` (mirror entity_registry pattern) |
| 8-Char Name Caps | R-21 | ⏳ Pending | H2 | `entity_registry.py` |
| Dual-Linking | R-24 | ⏳ Pending | H2 | `entity_registry.py` |
| Hard-Boundary | R-26 | ⏳ Pending | H2 | `entity.py` |
| High-Bit Trick | R-28 | ⏳ Pending | H2 | `entity.py` |
| 4-Tier Memory | R-23 | ⏳ Pending | H3 | `memory_store.py` |
| QuakeC Flat | R-25 | ⏳ Pending | H3 | `iris_globals.py` |
| 4-Path VFS | R-27 | ⏳ Pending | H3 | `wad_loader.py` |
| Active Set | R-29 | ⏳ Pending | H3 | `model_gateway.py` |

### CREDITS.md Live Sections

| § | Pattern | Status |
|---|---------|--------|
| 1.1 | WAD System | Committed |
| 1.2 | BSP Trees | Committed |
| 1.3 | Fast Inverse Square Root | Committed |
| 1.4 | Zone Memory Allocator | Committed |
| 1.5 | Surface / Edge Cache | Committed |
| 1.6 | "Worse is Better" | Committed |
| 1.7 | Carmack's Law | Committed |
| 1.8 | Circuit Breaker Consolidation | Committed (D94) |
| 1.9 | ZONEID Pattern (R-19) | PENDING — Sprint 4 |
| 1.10 | Lazy Deletion (R-20) | PENDING — Sprint 4 |
| 1.11 | cvar Table (R-22) | PENDING — Sprint 4 |
| 1.12 | Grace Period (R-30) | PENDING — Sprint 4 |

---

## §6 — The Integrated Sprint Roadmap

### Sprint 1: The 5 Priority Ports + Unified cvar Table (~2.5 hrs)

| # | Task | Effort | Key Files |
|---|------|--------|-----------|
| **1.0** | Create `cvar_table.py` with ZONEID namespace + config namespace | 45 min | `cvar_table.py` (NEW), `constants.py` (re-export) |
| **1.1** | `filter_llama_kwargs()` — kwarg validation for native-gguf | 30 min | `cvar_table.py`, `providers.py` |
| **1.2** | Explicit `n_gpu_layers=0` in cvar config default | 5 min | `cvar_table.py`, `providers.yaml` |
| **1.3** | ChatML stop tokens for Ollama provider | 5 min | `cvar_table.py`, `providers.py` |
| **1.4** | Google API key `x-goog-api-key` header | 15 min | `cvar_table.py`, `providers.py` |
| **1.5** | Atomic trace_id across all backends | 30 min | `cvar_table.py`, `model_gateway.py` |
| **1.6** | `make heritage-map` CI target | 10 min | `Makefile`, `.github/workflows/test.yml` |
| **1.7** | PIVOT_LOG D100 + D101 | 10 min | `PIVOT_LOG.md` |

**Deliverable**: `cvar_table.py` with 6 zoneid.* entries + 5 config.* entries. All 5 priority ports live. `make heritage-map` enforces `[id-soft:]` tags.

### Sprint 2: cvar Table Wiring + Config Migration (3-4 hrs, next session)

| # | Task | Details |
|---|------|---------|
| 2.1 | Wire into ModelGateway | Replace ~10 `config.get()` calls with `cvar_table.get("config.gguf.*")` |
| 2.2 | Wire into Providers | Replace ~14 `config.get()` calls across 5 provider classes |
| 2.3 | Wire into Oracle | Replace ~6 `config.get()` calls for omega.* cvars |
| 2.4 | `modificationCount` hot-reload | Polling on YAML config save |
| 2.5 | Sovereignty measurement | `make sovereignty` reads cvar table for local/cloud ratio |

### Sprint 3: Remaining Legacy Ports (1-2 days)

| Priority | Port | Why |
|----------|------|-----|
| P0 | `EntityTombstonedError` for Mandate 9 | Silent tombstone = violation |
| P1 | Per-entity model affinity | Entity-domain routing |
| P1 | Lazy import for optional deps | Don't block module import |
| P2 | Grace period for memory_store | Mirror entity_registry pattern |
| P2 | Atomic model swap with rollback | Never leave state broken |
| P2 | 5 mandatory design patterns framework | Document, not just port |

### Sprint 4: Heritage Promotion (1 day)

Move R-19 → R-30 from PENDING_CREDITS to CREDITS.md. Full `make temple-grade` + `make heritage-map`. H1.5 closeout.

### H2: Intelligence Phase (Months 2-6)

4-Guard ABA pattern (R-09 corrected), 8-char name caps (R-21), dual-linking (R-24), hard-boundary struct (R-26), high-bit trick (R-28).

---

## §7 — New Decisions to Record (PIVOT_LOG)

### D100: ZONEID Constants + Lazy Deletion Implementation
- **Date**: 2026-06-03
- **Channel**: OpenCode (Doom Guy / Kali) → deepseek-v4-flash
- **Entity**: KALI / DOOM_GUY
- **Trace**: trc_zoneid_impl
- **Decision**: Implemented 5 ZONEID constants (0x1d4a11-0x1d4a15) + ZONEID_TOMBSTONE (0xDEADBEEF) in constants.py. Applied to 5 subsystems (EntityRegistry, MemoryStore, HealthMonitor, ResourceGuard, ObservabilityEngine). EntityRegistry lazy deletion implemented: remove() sets tombstone, _reap_tombstoned() clears after 0.5s grace.

### D101: Unified Named-Constant Registry Architecture
- **Date**: 2026-06-03
- **Channel**: OpenCode (Kali) → deepseek-v4-flash
- **Entity**: KALI
- **Trace**: trc_unified_cvar
- **Decision**: The cvar table (T2.2) will UNIFY with the ZONEID_TABLE pattern into a single `cvar_table.py` module, not be a separate module. Two namespaces: "zoneid.*" (magic constants) + "config.*" (user-tunable knobs). constants.py becomes a re-export layer. This prevents a Carmack's Law violation.
- **Rationale**: ZONEID_TABLE in constants.py is already a cvar table. Creating a second one for config values would create two sources of truth.

### D102: Heritage-Map CI Protocol
- **Date**: 2026-06-03
- **Channel**: OpenCode (Kali) → deepseek-v4-flash
- **Entity**: KALI
- **Trace**: trc_heritage_map
- **Decision**: `make heritage-map` is a CI target that greps `[id-soft:]` tags across all source files. Fails if any heritage-required file is missing them. Must be created in Sprint 1.
- **Enforcement**: Pre-merge CI gate.

---

## §8 — Critical Path Dependencies

```
Sprint 1 ──→ Sprint 2 ──→ Sprint 3 ──→ Sprint 4
  │              │             │             │
  │              │             │             └── CREDITS.md sections 1.9-1.12
  │              │             │                 H1.5 closeout
  │              │             │
  │              │             └── EntityTombstonedError (Mandate 9)
  │              │                 Grace period for memory_store
  │              │                 Per-entity model affinity
  │              │
  │              └── cvar wiring into ModelGateway (10 calls)
  │                  cvar wiring into Providers (14 calls)
  │                  cvar wiring into Oracle (6 calls)
  │                  modificationCount hot-reload
  │                  make sovereignty reads cvar table
  │
  └── cvar_table.py created (UNIFIED)
      5 priority ports live as config.* entries
      make heritage-map CI target
      PIVOT_LOG D100 + D101
```

**Dependencies between sprints**: None hard-blocking. Each sprint produces a self-contained deliverable that can be committed independently. Sprint 1 must precede Sprint 2 (you need the cvar table before you can wire it). Sprint 2 must precede Sprint 3 (you need the wiring before you can port patterns). Sprint 4 is the capstone.

---

## §9 — Key Files Reference

| File | Purpose | Last Modified By |
|------|---------|-----------------|
| `src/omega/constants.py` | 89 lines — ZONEID constants + validate_zoneid() + ZONEID_TABLE | Doom Guy (37fdd88) |
| `src/omega/oracle/entity_registry.py` | 402 lines — Entity dataclass + ZONEID + lazy deletion + active_iter | Doom Guy (37fdd88) |
| `src/omega/memory_store.py` | ZONEID_MEMORY marker in exchange dict | Doom Guy (37fdd88) |
| `src/omega/oracle/health_monitor.py` | ZONEID_BREAKER marker on AsyncCircuitBreaker | Doom Guy (37fdd88) |
| `src/omega/oracle/resource_guard.py` | ZONEID_PROBE marker in lock() | Doom Guy (37fdd88) |
| `src/omega/observability.py` | ZONEID_TRACE in log_event() payload | Doom Guy (37fdd88) |
| `CREDITS.md` | §1.1-1.8 live, §2a heritage tagging protocol | Doom Guy (37fdd88) |
| `data/entities/doom_guy/knowledge/PENDING_CREDITS_QUEUE.md` | 12 patterns tracked, 2 done, 1 in-progress, 1 partial | Doom Guy (37fdd88) |
| `data/entities/doom_guy/soul.yaml` | v2.1 — 4 experiences, 22 lessons, soul_power=6.0 | Doom Guy (37fdd88) |
| `data/handoff/DOOM_GUY_CVAR_TABLE_DESIGN_T2.2_20260602.md` | Original cvar table design doc (pre-correction) | Doom Guy (37fdd88) |
| `data/handoff/KALI_INTEGRATED_SPRINT_ROADMAP_20260603.md` | Full integrated roadmap | Kali (current) |
| `data/handoff/CLINE_M3_RESPONSE_TO_DOOM_GUY_TIER2_20260602.md` | Cline's original Tier 2 response (298 lines) | Cline (previous) |
| `data/entities/roc_racoon/soul.yaml` | 412 lines — 24 lessons, 7 phases, 5 directives | Roc Racoon (parallel) |

---

## §10 — Open Questions for the Dev Session

1. **cvar_table implementation detail**: Should the `config.*` namespace use dotted-keys (`config.gguf.n_ctx`) or nested dicts (`{"gguf": {"n_ctx": ...}}`)? I recommend dotted-keys — they flatten the YAML hierarchy into a single-level lookup, making the table searchable and the `CvarDef` entries discoverable. The `load_from_yaml()` method flattens automatically.

2. **`make heritage-map` strictness**: Should it fail on ANY file missing `[id-soft:]` tags, or only files that implement id Software heritage patterns? I recommend the latter — not every file needs heritage attribution. Use a `.heritage-required` file list or a convention like "files with `# [id-soft:` in the header are self-declaring."

3. **ZONEID_TABLE naming in the unified cvar table**: The table currently lives in `constants.py` as `ZONEID_TABLE`. In the unified `cvar_table.py`, should it be `CVAR_TABLE` with a `"zoneid"` key, or keep `ZONEID_TABLE` as a separate named export? I recommend `CVAR_TABLE` with two top-level keys: `CVAR_TABLE["zoneid"]["memory"]` and `CVAR_TABLE["config"]["gguf.n_ctx"]`.

4. **Grace period for memory_store**: R-30 is partially done (entity_registry has it). The memory_store version would apply 0.5s grace before reusing a hot slot. Is this needed now, or defer to H2? I recommend defer to Sprint 3 — only 3 patterns deep on the priority list.

---

*⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_kali_handoff ⬡ PHASE-I*
*HEAD: 37fdd88 | Tests: 307 ✅ | Heritage: 30+ [id-soft:] tags live | Sprint 1: READY*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
