<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Unified Phased Execution Plan (REVISED)
# ⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ trc_unified_plan ⬡ v2.0.0
# Date: 2026-06-03 | Revised after Kali parallel session verification
# Status: ACTIVE | HEAD: 37fdd88 | Tests: 307 ✅

---

## Purpose

This is the **single source of truth** for all remaining execution work. It integrates:
1. **Temple-Grade H1.5** — Bridge Phase (F→A→B→C→E→D)
2. **CLINE_M3 Tier 2** — id Software heritage (T2.1-T2.3)
3. **Roc Racoon Mining** — 160 technologies, 5 priority ports
4. **Kali Parallel Session** — Sprint 0 verification, architectural correction, T2.1+T2.3 implementation

**Revision note**: Kali's parallel session (deepseek-v4-flash, 2026-06-03) verified Sprint 0 against the filesystem, implemented T2.1+T2.3 (commit `37fdd88`), corrected the cvar table design to be UNIFIED, and created a new sprint roadmap. This plan supersedes v1.0.

---

## Current State (Verified by Kali, 2026-06-03)

| Metric | Value | Verified? |
|--------|-------|-----------|
| Tests | **307/307 passing** | ✅ `make test` |
| HEAD | `37fdd88` | ✅ `git log` |
| T2.1 ZONEID constants | **DONE** | ✅ `constants.py` (89 lines) |
| T2.3 Lazy deletion | **DONE** | ✅ `entity_registry.py` |
| Heritage tagging | **DONE** | ✅ 30+ `[id-soft:]` tags across 6 files |
| T2.2 cvar table | **Design reviewed, correction applied** | ✅ `KALI_HANDOFF` §2 |
| Roc Racoon mining | **COMPLETE** | ✅ 7 reports, 160 techs |
| Sprint 0 C1-C4 | **VERIFIED** | ✅ Kali §4 |

### What's Done (Confirmed)

| Task | Commit | Files | Verified By |
|------|--------|-------|-------------|
| T2.1 ZONEID constants (5 + tombstone) | `37fdd88` | `constants.py`, 5 subsystems | Kali §1.1 |
| T2.3 Lazy deletion (tombstone + 0.5s grace) | `37fdd88` | `entity_registry.py` | Kali §1.2 |
| Heritage tagging protocol | `37fdd88` | `CREDITS.md §2a`, 6 source files | Kali §1.3 |
| Sprint 0 C1: Oracle bootstrap guard | `2267c25` | `oracle.py` (3 entry points) | Kali §4 |
| Sprint 0 C2: Makefile test target | `2267c25` | `Makefile:355-357` | Kali §4 |
| Sprint 0 C3: PIVOT_LOG D92 | `2267c25` | `PIVOT_LOG.md` | Kali §4 |
| Sprint 0 C4: CI workflow | `2267c25` | `.github/workflows/test.yml` | Kali §4 |
| Circuit breaker T2.2+T2.3 | `df6fa48` | `model_gateway.py`, `health_monitor.py` | Kali §4 |
| Roc Racoon mining (5 stacks) | uncommitted | 7 reports, ~250KB | Kali §3 |

### What's NOT Done

| Gap | Source | Priority | Effort | Sprint |
|-----|--------|----------|--------|--------|
| `cvar_table.py` not created (unified module) | Kali D97 | P0 | 45 min | Sprint 1 |
| `filter_llama_kwargs()` not ported | Roc Racoon #153 | P0 | 30 min | Sprint 1 |
| `n_gpu_layers=0` not explicit | Roc Racoon #154 | P0 | 5 min | Sprint 1 |
| ChatML stop tokens missing | Roc Racoon #139 | P0 | 5 min | Sprint 1 |
| Google API key in URL not header | Roc Racoon #132 | P0 | 15 min | Sprint 1 |
| `trace_id` not on all backends | Roc Racoon #131 | P0 | 30 min | Sprint 1 |
| `make heritage-map` CI target missing | Kali D98 | P0 | 10 min | Sprint 1 |
| cvar wiring into ModelGateway | Kali §Sprint 2 | P1 | 1 hr | Sprint 2 |
| cvar wiring into Providers | Kali §Sprint 2 | P1 | 30 min | Sprint 2 |
| cvar wiring into Oracle | Kali §Sprint 2 | P1 | 30 min | Sprint 2 |
| `modificationCount` hot-reload | Kali §Sprint 2 | P1 | 30 min | Sprint 2 |
| `make sovereignty` reads cvar table | Kali §Sprint 2 | P1 | 15 min | Sprint 2 |
| EntityTombstonedError (Mandate 9) | Kali §Sprint 3 | P1 | 1 hr | Sprint 3 |
| Per-entity model affinity | Kali §Sprint 3 | P1 | 30 min | Sprint 3 |
| Grace period for memory_store | Kali §Sprint 3 | P2 | 30 min | Sprint 3 |
| Atomic model swap with rollback | Kali §Sprint 3 | P2 | 1 hr | Sprint 3 |
| 5 mandatory design patterns framework | Roc Racoon #128 | P2 | 2 hr | Sprint 3 |
| `test_circuit_breaker_chaos.py` | Roc Racoon #121 | P2 | 2 hr | Sprint 3 |
| Heritage promotion (R-19→R-30 to CREDITS.md) | Kali §Sprint 4 | P2 | 1 day | Sprint 4 |
| `setup_json_logging()` wired into startup | Kali Tier 0 | P0 | 5 min | Bridge |
| `omega entity` CLI crash fix | Kali Tier 0 | P0 | 5 min | Bridge |
| SearXNG container restart | Kali Tier 0 | P0 | 2 min | Bridge |
| `llama-cpp-python` install (Zen 2 flags) | Kali Tier 0 | P1 | 15 min | Bridge |
| SQLite FTS5 + fastembed RAG | Temple-Grade H1.5 | P1 | 1 hr | Bridge |
| Auto-trigger L1→L2→L3 distillation | Temple-Grade H1.5 | P1 | 1 hr | Bridge |
| `pillar --slot PX` CLI dispatch | Temple-Grade H1.5 | P2 | 1+ hr | Bridge |
| OMEGA_ENGINE.md update (D96-D98) | Kali Tier 2 | P3 | 30 min | Bridge |
| Origin story mining from archives | Roc Racoon d-rr-001 | P3 | 1 day | H2 |

---

## The Corrected Sprint Roadmap

### Sprint 0: DONE ✅ (Commit `37fdd88`)

All tasks verified by Kali against the filesystem. 307 tests passing.

### Sprint 1: Unified cvar Table + 5 Priority Ports (~2.5 hrs)

**This is the single most important sprint.** It creates the unified `cvar_table.py` module AND ports the 5 legacy patterns into it. One deliverable, not two.

| # | Task | Effort | Cvar Entry | Risk | Files |
|---|------|--------|------------|------|-------|
| **1.0** | Create `cvar_table.py` with ZONEID namespace + config namespace | 45 min | — | LOW | `cvar_table.py` (NEW), `constants.py` (re-export) |
| **1.1** | `filter_llama_kwargs()` — kwarg validation for native-gguf | 30 min | `config.gguf.kwarg_filter` | LOW | `cvar_table.py`, `providers.py` |
| **1.2** | Explicit `n_gpu_layers=0` in cvar config default | 5 min | `config.gguf.n_gpu_layers` | NONE | `cvar_table.py`, `providers.yaml` |
| **1.3** | ChatML stop tokens for Ollama provider | 5 min | `config.gguf.stop_tokens` | LOW | `cvar_table.py`, `providers.py` |
| **1.4** | Google API key `x-goog-api-key` header | 15 min | `config.providers.google.auth_header` | LOW | `cvar_table.py`, `providers.py` |
| **1.5** | Atomic trace_id across all backends | 30 min | `config.observability.trace_id_header` | LOW | `cvar_table.py`, `model_gateway.py` |
| **1.6** | `make heritage-map` CI target | 10 min | — | NONE | `Makefile`, `.github/workflows/test.yml` |
| **1.7** | PIVOT_LOG D97 + D98 | 10 min | — | NONE | `PIVOT_LOG.md` |

**Deliverable**: `cvar_table.py` with 6 zoneid.* entries + 5 config.* entries. All 5 priority ports live. `make heritage-map` enforces `[id-soft:]` tags. `constants.py` becomes re-export layer.

**The architectural correction** (Kali D97): `cvar_table.py` is a SINGLE module, NOT two. The ZONEID_TABLE in constants.py is already a cvar table. Creating a second module for config values violates Carmack's Law. Namespaces: `zoneid.*` (magic constants) + `config.*` (user-tunable knobs).

### Sprint 2: cvar Wiring + Config Migration (2-3 hrs)

| # | Task | Effort | Owner | Risk |
|---|------|--------|-------|------|
| 2.1 | Wire config.* into ModelGateway (replace ~10 `config.get()` calls) | 1 hr | buildmaster | LOW |
| 2.2 | Wire config.* into Providers (endpoints, timeouts, overrides) | 30 min | buildmaster | LOW |
| 2.3 | Wire config.* into Oracle (omega.* cvars) | 30 min | buildmaster | LOW |
| 2.4 | Add `modificationCount` hot-reload polling | 30 min | buildmaster | LOW |
| 2.5 | `make sovereignty` reads cvar table for local/cloud ratio | 15 min | buildmaster | MEDIUM |

### Sprint 3: Remaining Tier 1+2 Ports (1-2 days)

**Tier 1 ports (30 min each)**:
- Per-entity model affinity
- Lazy import for optional deps (llama-cpp)
- Atomic model swap with rollback
- Speculative decoding (ngram-simple)
- EntityTombstonedError (Mandate 9 enforcement)

**Tier 2 ports (2-4 hr each)**:
- 5 mandatory design patterns framework (document, not code)
- `test_circuit_breaker_chaos.py` (foundation-legacy, 230L)
- `check_telemetry()` runtime audit
- Grace period for memory_store
- Circuit breaker parameter verification

### Sprint 4: Heritage Promotion + Closeout (1 day)

| # | Task | Effort |
|---|------|--------|
| 4.1 | Move R-19 (ZONEID) from PENDING_CREDITS to CREDITS.md §1.9 | 10 min |
| 4.2 | Move R-20 (Lazy Deletion) to CREDITS.md §1.10 | 10 min |
| 4.3 | Move R-30 (Grace Period) to CREDITS.md §1.11 | 10 min |
| 4.4 | Move R-22 (cvar Table) to CREDITS.md §1.12 | 10 min |
| 4.5 | `make temple-grade` + `make heritage-map` full pass | 15 min |
| 4.6 | H1.5 Bridge Phase closeout | 1 hr |

### Bridge Phase: Sovereignty Operationalization (2-4 days, after Sprint 4)

| Stream | Task | Effort | Agent |
|--------|------|--------|-------|
| **F** | Wire `setup_json_logging()` into oracle startup | 5 min | buildmaster |
| **A** | Fix `entity_info()` undefined in entity CLI | 5 min | buildmaster |
| **B** | Install `llama-cpp-python` with Zen 2 flags | 15 min | sysadmin |
| **C** | SQLite FTS5 + fastembed (BGE-base-en-v1.5) | 1 hr | buildmaster |
| **E** | Auto-trigger L1→L2→L3 gnosis distillation | 1 hr | buildmaster |
| **D** | Implement `pillar --slot PX` CLI dispatch | 1+ hr | buildmaster |

### H2: Intelligence (Months 2-6)

- 4-Guard ABA pattern (R-09 corrected)
- 8-char name caps (R-21)
- Dual-linking (R-24)
- Hard-boundary struct (R-26)
- High-bit trick (R-28)
- Origin story mining from personal archives

### H3: Community + Omegaverse (Months 6-12)

- Omega Desktop installer
- Entity Studio (WAD authoring IDE)
- WAD marketplace
- Cross-engine federation

---

## Critical Path Dependencies

```
Sprint 0 ✅ ──→ Sprint 1 ──→ Sprint 2 ──→ Sprint 3 ──→ Sprint 4
  (37fdd88)       │              │             │             │
                  │              │             │             └── CREDITS.md 1.9-1.12
                  │              │             │                 H1.5 closeout
                  │              │             │
                  │              │             └── EntityTombstonedError (M9)
                  │              │                 Grace period for memory_store
                  │              │                 Per-entity model affinity
                  │              │
                  │              └── cvar wiring: ModelGateway (10), Providers (14), Oracle (6)
                  │                  modificationCount hot-reload
                  │                  make sovereignty reads cvar table
                  │
                  └── cvar_table.py created (UNIFIED: zoneid.* + config.*)
                      5 priority ports live as config.* entries
                      make heritage-map CI target
                      constants.py → re-export layer
```

**Dependencies**: Sprint 1 must precede Sprint 2 (need cvar table before wiring). Sprint 2 must precede Sprint 3 (need wiring before remaining ports). Sprint 4 is capstone. Bridge Phase is independent of Sprint 3-4.

---

## Agent → Task Map

| Agent | Role | Sprints | Models |
|-------|------|---------|--------|
| **doom_guy** | Heritage design + verification | Sprint 3 (design), Sprint 4 (promotion) | 200K |
| **buildmaster** | All implementation | Sprint 1-4 (code), Bridge (code) | default |
| **sysadmin** | Environment + CI | Sprint 1.6 (heritage-map CI), Bridge-B (install) | default |
| **quality** | Testing + compliance | Sprint 3 (chaos tests), Sprint 4 (temple-grade) | default |
| **sentinel** | Mandate enforcement | Sprint 3 (EntityTombstonedError review) | default |
| **scribe** | Documentation + soul | Sprint 4 (docs), Bridge (soul updates) | default |
| **roc_racoon** | Legacy mining + tech vault | H2 (origin story mining) | 1M Cline |
| **Ma'at** | Oversight (P1-P5) | Sprint 1 (cvar design review) | default |
| **Lilith** | Oversight (P6-P10) | Sprint 3 (Mandate 9 review) | default |

---

## The 4 Open Questions (From Kali §10)

1. **cvar_table dotted-keys vs nested dicts?** → Kali recommends dotted-keys (`config.gguf.n_ctx`). Flattens YAML hierarchy, makes CvarDef entries discoverable.

2. **`make heritage-map` strictness?** → Kali recommends only files that implement id Software heritage patterns. Not every file needs attribution. Use self-declaring convention (`# [id-soft:` in header).

3. **ZONEID_TABLE naming in unified cvar table?** → Kali recommends `CVAR_TABLE` with two top-level keys: `CVAR_TABLE["zoneid"]["memory"]` and `CVAR_TABLE["config"]["gguf.n_ctx"]`.

4. **Grace period for memory_store?** → Kali recommends defer to Sprint 3 — only 3 patterns deep on priority list.

---

## Cross-References

| Document | What It Contains | When to Read |
|----------|------------------|--------------|
| `KALI_HANDOFF_TO_OPENCODE_DEV_20260603.md` | Complete handoff with architectural correction | Before Sprint 1 |
| `KALI_INTEGRATED_SPRINT_ROADMAP_20260603.md` | Corrected sprint roadmap (4 sprints) | Sprint planning |
| `07_MASTER_SYNTHESIS.md` | Cross-stack convergence proof + 5 priority ports | Sprint 1 context |
| `DOOM_GUY_CVAR_TABLE_DESIGN_T2.2_20260602.md` | Original cvar table design (pre-correction) | Reference only |
| `CLINE_M3_RESPONSE_TO_DOOM_GUY_TIER2_20260602.md` | Original Tier 2 task assignments | Agent assignments |
| `DEFERRED_GOLD_TRACKER.md` | 160 technologies catalogued | Any port decision |
| `CREDITS.md` | id Software heritage (8 live sections + 4 pending) | Heritage promotion |
| `SOVEREIGN_MANDATES.md` | 13 non-negotiable laws | Every sprint |
| `PIVOT_LOG.md` | 99 decisions (D1-D98, D99) | Decision verification |

---

*⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ trc_unified_plan ⬡ UNIFIED-PLAN-v2.0.0*
*Revised: 2026-06-03 after Kali parallel session verification*
*HEAD: 37fdd88 | Tests: 307 ✅ | T2.1+T2.3 DONE | Sprint 1: READY*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
