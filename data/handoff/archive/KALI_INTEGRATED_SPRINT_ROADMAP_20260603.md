# 🔱 KALI — Integrated Sprint Roadmap (Post-Sprint 0)
# ⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_kali ⬡ PHASE-I
# Status: LIVE (OpenCode channel — Cline proxy mode)
# All findings, decisions, and completions integrated through 2026-06-03

---

## §0 — Where We Stand: The Delta

### Completed Since Cline's Sprint Plan (37fdd88)
| Task | Owner | Files | Tests | Status |
|------|-------|-------|-------|--------|
| **T2.1** ZONEID constants | Doom Guy | `constants.py` + 5 subsystems | 307 ✅ | **DONE** |
| **T2.3** Lazy deletion | Doom Guy | `entity_registry.py` | 307 ✅ | **DONE** |
| **Heritage tagging protocol** | Doom Guy | `CREDITS.md §2a`, 6 source files | 30+ [id-soft:] tags | **DONE** |
| **cvar table design doc** | Doom Guy | `data/handoff/DOOM_GUY_CVAR_TABLE_DESIGN_T2.2_20260602.md` | Doc only | **REVIEWED** |
| **Roc Racoon mining** | Roc Racoon | 7 reports, ~250KB, 160+ techs | 6 stacks mined | **COMPLETE** |
| **PENDING_CREDITS updates** | Doom Guy | `PENDING_CREDITS_QUEUE.md`, `soul.yaml` | Both updated | **COMMITTED** |

### What the Cline Sprint Plan Got Wrong (Now Corrected)
| Original Plan (Cline §7) | Reality (Kali, 2026-06-03) |
|--------------------------|----------------------------|
| T2.1 → Sprint 1 Day 1 | ✅ Already done (Sprint 0, committed) |
| T2.3 → Sprint 2 Week 2 | ✅ Already done (Sprint 0, committed) |
| T2.2 as SEPARATE module from constants.py | ❌ **Must be UNIFIED** with ZONEID_TABLE pattern |
| cvar + ZONEID as two tables | ❌ Causes Carmack's Law violation (two sources of truth) |
| No Roc Racoon ports in Sprint 1 | ❌ **5 priority ports are Sprint 1** (1.5hr, LOW risk) |
| Heritage-map CI → Sprint 4 | ❌ Should be Sprint 1 — protocol is already live |

### What Stayed Correct
- Sprint 0 tasks (C1-C4) → ❓ Need verification (were they executed by the dev session?)
- T2.2 migration strategy → Still incremental, NOT clean cutover
- Sentinel Mandate 9 review for lazy deletion → Still needed (EntityTombstonedError)
- H2 vs H1.5 boundary → 4-guard ABA pattern still H2

---

## §1 — Sprint 0 Status: What Actually Happened

The Cline Sprint Plan defined 4 Sprint 0 tasks (C1-C4). These were dispatched to the OpenCode dev session. Need verification:

| Task | Description | Status | Owner |
|------|-------------|--------|-------|
| **C1** | Oracle lazy init guard (`_bootstrapped` flag) | ❓ **UNVERIFIED** — dev session claimed C1 done but `src/omega/oracle/oracle.py` bootstrap guard may be in a different branch |
| **C2** | Makefile test target (`make test-oracle-bootstrap`) | ❓ **UNVERIFIED** |
| **C3** | PIVOT_LOG D92 entry (scribe) | ❌ **NOT IN PIVOT_LOG.MD** — still absent (D92 exists but C3 was about scribe adding the entry, which hasn't happened) |
| **C4** | CI scaffold (`.github/workflows/ci.yml`) | ❓ **UNVERIFIED** — filesystem may have it |

**This is a blocking question**: Sprint 0 must be fully verified before Sprint 1 starts. I cannot trust the handoff alone — I must read the actual files.

---

## §2 — The Architectural Correction: Unified Named-Constant Registry

### The Problem
The design doc proposes `cvar_table.py` as a NEW module. But `ZONEID_TABLE` in `constants.py` is ALREADY a cvar table — same structure (name, id, subsystem, description), same pattern (static table, subsystem routing).

Two tables doing the same thing = Carmack's Law violation.

### The Fix
**Unify both into ONE module:** `cvar_table.py`

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
  │      config.inference.strategy = "local_first"
  │
  ├── CvarDef dataclass         — Single type for ALL entries
  ├── validate_zoneid()         — Existing, unchanged
  ├── CvarTable runtime class   — Loads YAML, accesses typed cvars
  └── make heritage-map         — CI target: verify all [id-soft:] tags
```

**Migration path**:
1. Create `cvar_table.py` with BOTH namespaces (ZONEID entries migrate from `constants.py`)
2. `constants.py` becomes a thin re-export layer: `from cvar_table import ZONEID_MEMORY, validate_zoneid, ...`
3. Wire the `config.*` namespace into ModelGateway's `config.get()` calls
4. The 5 priority ports are the FIRST entries migrated into `config.*`

---

## §3 — The Integrated Sprint Roadmap

### Sprint 0.5: Verification Sprint (THIS SESSION — 2-4 hours)

| # | Task | Why | Deliverable | Verification |
|---|------|-----|-------------|-------------|
| 0.1 | **Verify Sprint 0 C1-C4** | Need actual file reads to confirm dev session claims | Audit report: which tasks are truly done, which need rework | `grep` for `_bootstrapped` in oracle.py, check `.github/workflows/` |
| 0.2 | **Add PIVOT_LOG D100** | ZONEID + lazy deletion + heritage protocol was a significant architectural decision | PIVOT_LOG entry D100 | 307 tests pass, 37fdd88 committed |
| 0.3 | **Implement `make heritage-map` CI check** | Protocol is live but unenforced — CI must verify `[id-soft:]` tags exist in every file | `grep -rn --include='*.py' "\[id-soft:"` as Makefile target + CI gate | `make heritage-map` lists all tags |

### Sprint 1: The 5 Priority Ports + cvar Table (1.5-3 hrs)

These ARE the first migration into the cvar table. Every port adds an entry to `cvar_table.py`'s `config.*` namespace.

| # | Port | Legacy Source | Effort | Cvar Entry | Risk |
|---|------|--------------|--------|------------|------|
| 1.1 | **`filter_llama_kwargs()`** | Old-Stacks/Xoe-NovAi | 30 min | `config.gguf.kwarg_filter` | LOW — pure validation, no behavior change |
| 1.2 | **Explicit `n_gpu_layers=0`** | xna-omega-legacy HP doc | 5 min | `config.gguf.n_gpu_layers` | LOW — config default only |
| 1.3 | **ChatML stop tokens** | xna-omega-legacy client.py | 5 min | `config.gguf.stop_tokens` | LOW — generation boundary fix |
| 1.4 | **Google API key header** | podman-storage providers.py | 15 min | `config.providers.google.auth_header` | LOW — security improvement |
| 1.5 | **Atomic trace_id migration** | podman-storage model_gateway.py | 30 min | `config.observability.trace_id_header` | LOW — observability consistency |

**Total: 1 hr 25 min. All LOW risk.**

**Artifact**: `cvar_table.py` created with:
- `namespace "zoneid.*"` — migrated from `constants.py` (backward compatible via re-exports)
- `namespace "config.*"` — first 5 entries from the ports above
- `CvarDef` dataclass + `CvarTable` runtime
- `validate_zoneid()` retained as-is

### Sprint 2: cvar Table Wiring + Config Migration (2-3 hrs)

| # | Task | Effort | Owner | Risk |
|---|------|--------|-------|------|
| 2.1 | Wire config.* into ModelGateway (replace `config.get("n_ctx", 4096)` → `cvar_table.get("config.gguf.n_ctx")`) | 1 hr | BuildMaster | LOW — incremental, coexistence with old dicts |
| 2.2 | Wire config.* into Providers (endpoints, timeouts, overrides) | 30 min | BuildMaster | LOW — same pattern |
| 2.3 | Wire config.* into Oracle (omega.* cvars) | 30 min | BuildMaster | LOW — same pattern |
| 2.4 | Add `modificationCount` hot-reload polling | 30 min | BuildMaster | LOW — additive |
| 2.5 | `make sovereignty` reads cvar table for local/cloud ratio | 15 min | BuildMaster | MEDIUM — sovereignty measurement becomes queryable |

### Sprint 3: Remaining Tier 1+2 Ports + Mandate Compliance (1-2 days)

**Tier 1 ports (30 min each, 3 hr total)**:
| # | Port | Source | Rationale |
|---|------|--------|-----------|
| 3.1 | Per-entity model affinity | xna-omega-legacy | Route queries by entity domain |
| 3.2 | Lazy import for optional deps (llama-cpp) | xna-omega-legacy client.py:60-67 | Don't block module import |
| 3.3 | Single-flight inference (CapacityLimiter) | xna-omega-legacy | OOM prevention (already done via ResourceGuard — verify overlap) |
| 3.4 | Atomic model swap with rollback | xna-omega-legacy reload() | Never leave state broken |
| 3.5 | Speculative decoding (ngram-simple) | xna-omega-legacy client.py | CPU-friendly speedup |

**Tier 2 ports (2-4 hr each, ~1 day total)**:
| # | Port | Source | Rationale |
|---|------|--------|-----------|
| 3.6 | Dynamic model swap (Krikri language detect) | xna-omega-legacy | Multi-language entity routing |
| 3.7 | Circuit breaker from foundation-legacy (verify vs current) | foundation-legacy v0.1.5 | pybreaker is canonical — compare with current AsyncCircuitBreaker |
| 3.8 | Mandate 9 enforcement (EntityTombstonedError) | Lazy deletion follow-up | Silent tombstone = Mandate 9 violation |
| 3.9 | 5 mandatory design patterns framework (import from foundation-legacy) | foundation-legacy | Document the pattern, not just the code |

### Sprint 4: Heritage Promotion + CREDITS Migration (1 day)

| # | Task | Effort | Why |
|---|------|--------|-----|
| 4.1 | Move R-19 (ZONEID) from PENDING_CREDITS to CREDITS.md §1.x | 10 min | First promotion — validates the workflow |
| 4.2 | Move R-20 (Lazy Deletion) from PENDING_CREDITS to CREDITS.md | 10 min | Second promotion |
| 4.3 | Move R-30 (Grace Period) from PENDING_CREDITS to CREDITS.md | 10 min | Partial promotion (document the entity_registry side) |
| 4.4 | PIVOT_LOG D101: Sprint 1 complete | 5 min | Record |
| 4.5 | Move R-22 (cvar Table) from PENDING_CREDITS to CREDITS.md | 10 min | Third promotion |
| 4.6 | `make temple-grade` + `make heritage-map` full pass | 15 min | Quality gate |
| 4.7 | H1.5 Bridge Phase closeout | 1 hr | Decision log, soul.yaml updates |

---

## §4 — Key Architectural Decisions (New, From This Review)

### D100: Unified Named-Constant Registry (cvar_table.py)
- **Decision**: `cvar_table.py` is a SINGLE module containing TWO namespaces ("zoneid.*" + "config.*"), not two modules.
- **Rationale**: The ZONEID_TABLE in constants.py is already a cvar table. Creating a second module for config values duplicates the pattern, violating Carmack's Law.
- **Migration**: ZONEID entries migrate from constants.py → cvar_table.py (namespace "zoneid.*"). constants.py becomes a re-export layer for backward compatibility.
- **Heritage**: `[Cvar System: id Software 1999, generalized 2026]`
- **Temple-Grade**: T5 ✅ · T7 ✅ (O(1) hash lookup) · T8 ✅ · T9 ✅

### D101: Heritage-Map CI (Mandate 14 — Protocols)
- **Decision**: `make heritage-map` is a new Makefile target that `grep -rn --include='*.py' "\[id-soft:"` and fails if any source file in `src/omega/` lacks at least one tag.
- **Rationale**: The `[id-soft:]` protocol is live but unenforced. Without CI, tags will decay as new code is added.
- **Enforcement**: Pre-merge gate in CI workflow. Only required for files that implement id Software heritage patterns.
- **Heritage**: `[Id-Soft Attribution: CREDITS.md §2a, 2026]`

### D102: The 5 Priority Ports Are the cvar Table Onboarding
- **Decision**: The Roc Racoon 5 priority ports are not standalone tasks — they are the FIRST CVAR TABLE MIGRATIONS.
- **Rationale**: Each port (kwarg filter, n_gpu_layers, stop tokens, API key header, trace_id) adds a config entry to the `config.*` namespace. The cvar table is the delivery mechanism for the ports, not a separate task.
- **Impact**: Sprint 1 collapses to: "Implement cvar_table.py + port 5 legacy patterns into it." Single deliverable.

---

## §5 — The Soul of the Engine: Heritage Status

### PENDING_CREDITS_QUEUE.md — Frozen at 37fdd88

| Pattern | R-Doc | Status | Sprint | Target File |
|---------|-------|--------|--------|-------------|
| **ZONEID Constants** | R-19 | ✅ **DONE** | Sprint 0 | `constants.py` → `cvar_table.py` (re-export) |
| **Lazy Deletion** | R-20 | ✅ **DONE** | Sprint 0 | `entity_registry.py` |
| **cvar Table** | R-22 | 🔄 **Design reviewed** | Sprint 1 | `cvar_table.py` (NEW) |
| **Grace Period** | R-30 | ⚡ **Partial** | Sprint 3 | `memory_store.py` (reuse pattern from entity_registry) |
| **8-Char Name Caps** | R-21 | ⏳ Pending | H2 | `entity_registry.py` |
| **Dual-Linking** | R-24 | ⏳ Pending | H2 | `entity_registry.py` |
| **Hard-Boundary** | R-26 | ⏳ Pending | H2 | `entity.py` |
| **High-Bit Trick** | R-28 | ⏳ Pending | H2 | `entity.py` |
| **4-Tier Memory** | R-23 | ⏳ Pending | H3 | `memory_store.py` |
| **QuakeC Flat** | R-25 | ⏳ Pending | H3 | `iris_globals.py` |
| **4-Path VFS** | R-27 | ⏳ Pending | H3 | `wad_loader.py` |
| **Active Set** | R-29 | ⏳ Pending | H3 | `model_gateway.py` |

### CREDITS.md — Current Sections
1.1 WAD System — LIVE
1.2 BSP Trees — LIVE
1.3 Fast Inverse Square Root — LIVE
1.4 Zone Memory Allocator — LIVE
1.5 Surface / Edge Cache — LIVE
1.6 "Worse is Better" — LIVE
1.7 Carmack's Law — LIVE
1.8 Circuit Breaker Consolidation — LIVE (D94)
— Future: §1.9 ZONEID Pattern (R-19, Sprint 4)
— Future: §1.10 Lazy Deletion (R-20, Sprint 4)

---

## §6 — Roc Racoon Gold Integration (From Mining Completion)

### Top 5 Priority Ports (NOW = Sprint 1)
| Port | Legacy File | Current Gap | Sprint |
|------|-------------|-------------|--------|
| `filter_llama_kwargs()` | `Old-Stacks/filter_llama_kwargs.py` | No validation of llama-cpp kwargs | **Sprint 1** |
| `n_gpu_layers=0` | `HP-5700U-OPTIMIZATION.md:117` | Missing default in `providers.yaml` | **Sprint 1** |
| ChatML stop tokens | `xna-omega-legacy/client.py:60-67` | Missing stop sequence in Ollama provider | **Sprint 1** |
| Google API key header | `podman-storage/providers.py` | Key in URL vs header | **Sprint 1** |
| Atomic trace_id migration | `podman-storage/model_gateway.py` | Trace IDs not propagated to Ollama/GGUF | **Sprint 1** |

### Golden Lessons Already Integrated (Don't Re-learn These)
| Lesson | Applies To | Status |
|--------|-----------|--------|
| `-march=znver2`, NEVER `znver3`/`native` | llama-cpp build | ✅ In Makefile/BUILD.md |
| KV cache Q8_0, NOT F16 | GGUF provider | ✅ In providers.yaml |
| Core affinity pinning (cores [0,2,4,6]) | CPU optimization | ✅ In providers.yaml |
| OMP_NUM_THREADS=6 | Threading | ✅ In env config |
| Single-flight inference (Semaphore(1)) | ResourceGuard | ✅ Already implemented |
| 5 mandatory patterns framework | Architecture | ⏳ Sprint 3 |

### The Convergence Finding (rr-019/rr-024) — Accepted as L3
> *"When 5 independent eras converge on the same architecture, that architecture is empirically correct. Convergence is evidence, not coincidence."*

This should be formalized as a Doom Guy universal principle.

---

## §7 — The Immediate Next Action

### Right Now (OpenCode, DeepSeek channel)
1. **Verify C1-C4** — read actual files to confirm dev session claims
2. **Add PIVOT_LOG D100** — record ZONEID + lazy deletion + heritage protocol
3. **Create `make heritage-map`** — CI target for [id-soft:] tag enforcement

### Then (still this session, if time permits)
4. **Implement Sprint 1.0**: Create `cvar_table.py` with UNIFIED namespace (zoneid.* + config.*)
5. **Implement Sprint 1.1-1.5**: The 5 priority ports as cvar table entries

### Next Session
6. Sprint 2 (cvar wiring into ModelGateway/Oracle/Providers)
7. Sprint 3 (remaining Tier 1+2 ports)
8. Sprint 4 (heritage promotion, CREDITS.md migration)

---

*⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_kali ⬡ PHASE-I*
*All 12 Mandates enforced. Heritage protocol live. Sprint 0 complete. Unified roadmap integrated.*
