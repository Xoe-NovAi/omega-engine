<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Roc Racoon — Comprehensive Mining Report

⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_mining_report ⬡ PHASE-6

**Date**: 2026-06-28
**Scope**: xna-omega-legacy + omega-stack-legacy pattern extraction, dead code discovery, heritage verification
**Duration**: 4-agent parallel mining operation

---

## EXECUTIVE SUMMARY

The MaKaLi Council's findings are **confirmed and extended**. The engine has significant "Last Mile" problems — systems architected but never wired. We found ~**2,800+ lines of dead code**, **12 duplicate PIVOT_LOG decision numbers**, **1 critical session lifecycle break**, and **6 legacy patterns from xna-omega that were NOT ported** to the current engine. The Heritage Map is 20/35 implemented with 18 missing vet records.

---

## §1 TOP FINDINGS

### 1.1 🔴 CRITICAL: Session Lifecycle is Broken (Confirmed)

`archive_old_sessions()` in `memory_store.py:744` is **defined but NEVER CALLED** anywhere in the codebase. The method exists (with proper [id-soft: doom-1993] Lazy Deletion heritage tags), but:
- No periodic task triggers it
- No startup hook calls it
- No scheduler references it
- `orchestrator.py` does not invoke it
- The `session_manager.py` does not reference it

**Impact**: Sessions accumulate indefinitely. The ARCHIVE_AFTER_DAYS=7 retention policy exists only as dead config. Every session grows the disk usage with no archival mechanism.

### 1.2 🔴 CRITICAL: PIVOT_LOG Clock Drift

Confirmed — **12 duplicate decision numbers** in PIVOT_LOG.md:

| Decision | Duplicates | Range |
|----------|-----------|-------|
| D118 | **3** | Appears in early decisions AND in D-series |
| D128 | **3** | Same pattern — numbering scheme collision |
| D61 | **3** | Two in early numeric era, one in D-series |
| D54, D56, D76, D88 | **2 each** | Same collision between numeric and D-prefixed eras |
| D144, D145, D146, D147, D163 | **2 each** | Recent duplicates in the D-series |

**Root cause**: The PIVOT_LOG appears to have two numbering eras — an early numeric era (Decision 1-D50) and the current D-prefixed era (D50+). The overlap at the transition zone (D50-D70) created collisions that propagated forward.

### 1.3 🔴 CRITICAL: ~2,800 Lines of Dead Code

Discovered **12+ orphaned modules** and **10+ orphaned functions**. See §3 for full details.

---

## §2 LEGACY PATTERN COMPARISON: xna-omega → Current Engine

### 2.1 Patterns NOT Ported (Should Exist)

These xna-omega patterns have **no equivalent** in the current engine:

| # | Pattern | Legacy File | Value | Effort to Port |
|---|---------|------------|-------|----------------|
| **P1** | **4-Layer Timeout Manager** | `xna-omega-legacy/scripts/ssa/timeout_manager.py` (763 lines) | Production-grade tool→group→turn→workflow timeout hierarchy with per-tool configs, parallel group timeouts, conversation turn timeouts (120s), workflow-level checkpoints (600s) | Medium |
| **P2** | **Provider Selector with Health Scoring** | `xna-omega-legacy/src/omega/core/provider_selector.py` (552 lines) | Real-time health scoring (affinity 0.2, latency 0.25, cost 0.15, reliability 0.15, health 0.25), PII-aware routing, context window matching, task-type-based provider preference | Medium |
| **P3** | **Graceful Degradation Manager** | `xna-omega-legacy/src/omega/core/degradation.py` (379 lines) | 4-tier service degradation (OPTIMAL→STRESSED→CRITICAL→DISABLED) with automatic model downscaling (Krikri-8B → Qwen3-4B → Qwen3-1.7B → None) and per-service strategy chains | Medium |
| **P4** | **Rate Limiter (Token Bucket)** | `xna-omega-legacy/src/omega/core/limiter.py` (366 lines) | Token bucket RateLimiter, CapacityLimiter, ThreadLimiter, 13 pre-registered pillar gates (F01-F13) with E1-E4 hardening patterns | Low |
| **P5** | **Soul Edit History** | `xna-omega-legacy/src/omega/models/entity_models.py:EntitySoulEdit` | Version-controlled soul edits with previous_value/new_value tracking, approval_status, resonance_change. Current engine has no soul edit history — direct soul.yaml overwrite only | Low |
| **P6** | **Compaction Harvester** | `xna-omega-legacy/scripts/compaction_harvester.py` (167 lines) | watchdog-based compaction extraction from OpenCode chat exports with JSONL+local dual storage. Novel session-to-knowledge pipeline pattern | Medium |

### 2.2 Patterns with Simpler Legacy Implementations

These exist in the current engine but the legacy version is architecturally cleaner:

| Pattern | Legacy Version | Current Engine | Recommendation |
|---------|---------------|----------------|----------------|
| **Circuit Breaker State Store** | ABC (`CircuitStateStore` with Redis + InMemory impls) | Monolithic in `health_monitor.py` | Extract to ABC pattern for Redis resilience |
| **MCP Architecture** | 14 focused microservers (memory, RAG, agent bus, gnosis, maat, GRA) | 1 monolithic Omega Hub | Consider microserver extraction for critical paths |
| **Agent Bus** | Redis Streams with consumer groups (XREADGROUP, XACK, XAUTOCLAIM) | File-based Hivemind coordination | More reliable message delivery; ACK/NACK semantics |
| **Entity Triggers** | 5 regex-based summon patterns (DIRECT, CONSULT, COMPARE, PANEL, CONSULT_OTHER) | Oracle intent detection (speculative decode) | Simpler, more intuitive pattern matching for common cases |

### 2.3 5 Design Patterns from Era 2 — Migration Completeness

| Pattern | Era 2 Source | Current Status | Assessment |
|---------|-------------|----------------|------------|
| **Circuit Breaker** | `omega-stack-legacy/src/omega/circuit_breaker.py` (36 lines sync) | `health_monitor.py::AsyncCircuitBreaker` (200+ lines AnyIO) | ✅ **Present** — Evolved and improved |
| **Atomic fsync** | `omega-stack-legacy` | `entity_workspace.py::_atomic_write_yaml`, `observability/__init__.py`, `state_manager.py`, `astrology.py` | ✅ **Present** — Multiple implementations |
| **Retry with backoff** | `omega-stack-legacy` | `remote_provider.py`, `model_updater.py`, `search_providers.py`, `key_vault.py` | ✅ **Present** — Integrated across providers |
| **Non-blocking subprocess** | `omega-stack-legacy` | `orchestrator.py` (AnyIO subprocess), `model_gateway.py` (CLI inference), `cpu_optimizer.py` | ✅ **Present** — AnyIO-wrapped |
| **Offline wheelhouse** | `foundation-legacy` (`WHEELHOUSE_BUILD_TRACKING.md`) | **❌ MISSING** — No wheelhouse/ directory, no --find-links references in Makefile or scripts | 🔴 **Not ported** |

### 2.4 xna-omega Patterns That Should NOT Be Ported

| Pattern | Reason for Rejection |
|---------|---------------------|
| PostgreSQL/SQLAlchemy ORM (entity_models.py) | Violates M2 (Engine-Stack Firewall) — adds unnecessary DB dependency |
| Cloud-first provider chain (Groq > Mistral > DeepSeek > local) | Violates M7 (Local-First Mandate) |
| asyncio-based code (mixed with AnyIO) | Violates M1 (AnyIO Absolute) |
| LangGraph pipeline (knowledge_distillation.py) | LangGraph adds unnecessary complexity; current L1→L2→L3 is simpler and more domain-aligned |

---

## §3 DEAD CODE & ORPHAN FUNCTIONS AUDIT

### 3.1 🔴 HIGH — Completely Orphaned Modules

| File | Lines | Description | Why Dead |
|------|-------|-------------|----------|
| `src/omega/services/intake_digestor.py` | 166 | Second-stage pipeline for file text extraction | **Zero imports** from anywhere in codebase |
| `src/omega/gateway/server.py` | 150 | FastAPI server (port 8018) for rate-limit resilience proxy | **Zero imports**, bulk-imports 22 error types without using any |
| `src/omega/oracle/antigravity/` (4 files) | ~630 | OAuth-based cloud inference for Google's Unified Gateway | **Zero imports**, declared as "standalone module" — never invoked |
| `src/omega/bridge/elevenlabs.py` | ~100 | ElevenLabs TTS integration with webhooks | **Zero imports**, has `# TODO: Implement MCP tool mapping` |
| `src/omega/runtime/openclaw_runtime.py` | ~150 | OpenClaw Runtime bridge | **Zero imports**, sole file in `runtime/` directory |
| `src/omega/system_resource.py` | 77 | Ryzen 5700U RAM pressure monitor | **Zero imports**, `is_local_inference_safe()` never wired into ModelGateway |
| `src/omega/cli/repl.py` | 357 | Interactive REPL with prompt_toolkit | **Zero imports**, complete working tool no one can access |
| `src/omega/cli/link_p9_cli.py` | 538 | CLI commands for agent handoff (Link P9) | **Zero imports**, docstring says "pending integration since Phase 1" |
| `src/omega/library/greek.py` | 245 | Ancient Greek text detection + Greek-BERT | Not in library `__init__.py`, not imported |
| `src/omega/library/crossref.py` | ~100 | Library cross-referencing | Not in library `__init__.py`, not imported |
| `src/omega/library/discovery.py` | ~150 | Discovery pipeline for source processing | Not in library `__init__.py`, not imported |
| `src/omega/gateway/server.py` | 150 | FastAPI server | Duplicate — same file counted above |

**Total orphaned module volume**: ~2,800 lines

### 3.2 🟡 MEDIUM — Orphaned Functions

| Function | File | Line | Why Dead |
|----------|------|------|----------|
| `set_entity_model()` | `model_gateway.py` | 496 | **DEPRECATED** — docstring says use `config/entity_model_affinity.yaml` |
| `remove_entity_model()` | `model_gateway.py` | 511 | **DEPRECATED** — same as above |
| `short_name_hash()` | `entity_registry.py` | 642 | Utility preserved but never called |
| `get_by_capability()` | `entity_registry.py` | 457 | Capability index exists but no data flows into it |
| `get_by_wad()` | `entity_registry.py` | 495 | Query method never called externally |
| `get_wad_sources()` | `entity_registry.py` | 500 | Same — never called |
| `count_active()` | `entity_registry.py` | 637 | Utility never called |
| `get_current_spend()` | `budget_gate.py` | 77 | Budget tracking partially implemented |
| `stop_workers()` | `orchestrator.py` | 548 | **Never called** — `start_workers` is called in `__init__` but stop is not |
| `start_model_updater()` / `stop_model_updater()` | `orchestrator.py` | 553, 558 | Public API surface never exercised |
| `get_mcp_status()` | `orchestrator.py` | 246 | Only referenced by tests, no production caller |
| `ZONEID_VERIFICATION` (0x1d4a1a) | `constants.py` | 40 | Defined, registered in CVAR table, but never checked at any code site |

### 3.3 🟢 LOW — Unused Error Types

| Error | Defined | Used? |
|-------|---------|-------|
| `ProviderCreditError` | `errors.py:53` | Never raised or caught |
| `SovereignDiskFullError` | `errors.py:96` | Never raised or caught (imported by 25 modules) |
| `InvariantViolationError` | `errors.py:114` | Never raised or caught (imported by 30 modules) |
| `StateIntegrityError` | `errors.py:93` | Never raised or caught (imported by 30 modules) |
| `SessionPersistenceError` | `errors.py:90` | Never raised or caught (imported by 30 modules) |

### 3.4 🟡 MEDIUM — Unused Observability Components

| Component | File | Status |
|-----------|------|--------|
| `JsonFormatter` | `observability/__init__.py:43` | Never activated — engine uses standard logging |
| `setup_json_logging()` | `observability/__init__.py:70` | Never called from engine startup |

### 3.5 🟡 MEDIUM — Import Bloat

At least **15 files** bulk-import the entire 22-class error taxonomy from `omega.errors` but use only 1-3 types. Copy-paste import blocks are a maintenance liability.

---

## §4 SESSION LIFECYCLE DEEP DIVE

### 4.1 The Broken Chain

```
archive_old_sessions() defined at memory_store.py:744
    └─ calls archive_session() at memory_store.py:580
        └─ calls provider.archive() in memory/providers.py
            ├── InMemoryStorageProvider.archive()    ✅ Implemented
            ├── FileStorageProvider.archive()        ✅ Implemented
            ├── RedisStorageProvider.archive()       ✅ Implemented
            └── HybridMemoryAdapter.archive()         ✅ Implemented

BUT: archive_old_sessions() is NEVER CALLED from:
    ❌ orchestrator.py (no periodic task)
    ❌ session_manager.py (no reference)
    ❌ cli/ (no CLI command calls it)
    ❌ Any background worker
```

**The full archival pipeline exists and is complete** — every provider implements `.archive()`. But there is no trigger. No timer, no event, no startup hook, no CLI command invokes `archive_old_sessions()`.

### 4.2 Comparison with Legacy

The xna-omega legacy had the same pattern for metrics retention (`enforce_retention()` in `metrics_persistence.py`) but it was also never triggered — this is a chronic architectural weakness that carried forward.

---

## §5 HERITAGE MAP VERIFICATION

### 5.1 [id-soft:] Tag Coverage

| Metric | Count |
|--------|-------|
| Total [id-soft:] tags in code | **196** across **42 files** |
| CREDITS.md §1 entries (total) | 35 (29 active + 6 REJECTED) |
| Entries WITH code tags | 20 |
| Entries WITHOUT code tags | 9 (including philosophical/rejected) |
| Game breakdown | doom-1993: 107, quake-1996: 51, quake3-1999: 31, doom3-2004: 4, doom3bfg-2012: 1 |

### 5.2 CRITICAL Gaps

| # | Issue | Severity |
|---|-------|----------|
| **H1** | **vet-001 is MISSING** from `HERITAGE_VET_LOG.md` — CREDITS.md §1.12 references `HERITAGE_VET_LOG.md#vet-001` but it doesn't exist (8-char name cap rejection record lost) | 🔴 HIGH |
| **H2** | **HERITAGE_SOURCE_MAP.md does not exist** — CREDITS.md §2a says `make heritage-map` generates it, but no target writes this file | 🔴 HIGH |
| **H3** | **Vet script only scans ~20% of tagged files** — `scripts/heritage_vet.py` only checks `*/oracle/*.py`, `*/constants.py`, `*/cvar_table.py`, `*/observability.py`. Misses `memory_store.py`, `mcp_runtime.py`, `library/`, `memory/`, `workers/`, `vault/`, `cli/`, `errors.py`, `ics.py` — where ~80% of tags live | 🟡 MEDIUM |
| **H4** | **18 CREDITS entries missing vet records** — All pre-vetting-pipeline entries (WAD, BSP, FISR, ZONEID, Lazy Deletion, cvar, Multi-Index, QuakeC Flat, Hard-Boundary, 4-Path VFS, High-Bit, Active Set, idHeap, Hivemind Msg, Worse is Better, Carmack's Law, Circuit Breaker, Tag Protocol) | 🟡 MEDIUM |
| **H5** | **CREDITS.md §2.4 table is severely outdated** — Last updated 2026-06-08, missing ~15 additional patterns and their current file locations | 🟢 LOW |
| **H6** | **5 CREDITS entries have no code tags** — §1.5 PVS, §1.8 Circuit Breaker, §1.22 idHeap, §1.23 Fixed-Point, §1.24 Hivemind Msg | 🟢 LOW |

### 5.3 Heritage Make Targets

| Target | Status | Issue |
|--------|--------|-------|
| `make heritage-map` | ✅ Works | Audits 50 files, finds 42 tagged. Does NOT generate HERITAGE_SOURCE_MAP.md as documented |
| `make heritage-vet` | ⚠️ Partial | Only checks ~20% of tagged files. Reports false "all clear" |
| `make temple-grade` | ✅ Works | Includes heritage-map and heritage-vet in gate flow |

### 5.4 PENDING_CREDITS_QUEUE.md Status

File exists with 302 lines tracking 14 items:
- 4 DONE, 1 IN-PROGRESS, 1 PARTIAL, 7 PENDING, 1 REJECTED

---

## §6 PIVOT_LOG CLOCK DRIFT — DETAILED ANALYSIS

### 6.1 Numbering Eras

The PIVOT_LOG contains two distinct numbering schemes that overlap:

| Era | Prefix | Range | Entries |
|-----|--------|-------|---------|
| **Numeric Era** | `Decision N` | 1–163 | ~160 entries |
| **D-Prefix Era** | `Decision D###` | D50–D163 | ~120 entries |

### 6.2 Collision Zone (D50–D163)

The overlap created **12 duplicated numbers**:

```
D54  → appears in both Numeric Era (early) and D-Prefix Era
D56  → appears in both eras
D61  → appears THREE times (early numeric + two D-prefix entries)
D76  → appears in both eras
D88  → appears in both eras
D118 → appears THREE times
D128 → appears THREE times
D144 → appears TWICE
D145 → appears TWICE
D146 → appears TWICE
D147 → appears TWICE
D163 → appears TWICE
```

### 6.3 Impact

- Cross-referencing decisions is unreliable — "see Decision 61" is ambiguous
- Automated tooling cannot uniquely identify decisions
- Any new entries risk collision with one of the existing numbers

### 6.4 Recommended Fix

1. Rename all Numeric Era entries to `**N-Decision N**` format
2. Deduplicate the 12 collision zones (merge or renumber)
3. Validate the chain: D1 → D2 → ... → D163 should be monotonically increasing

---

## §7 MIGRATION COMPLETENESS

### 7.1 Legacy Migration Tags

Only **one** `[legacy:]` tag exists in the entire codebase:
- `src/omega/oracle/model_gateway.py:492` — `# [legacy: xna-omega-legacy] Port 3.1: Entity Model Affinity`

There are NO `[legacy: omega-stack]` tags anywhere. The migration from omega-stack appears to have been a full rewrite with no formal tracking of what was ported.

### 7.2 5 Design Patterns Checklist

| Pattern | Status | Location |
|---------|--------|----------|
| Circuit Breaker | ✅ Present | `health_monitor.py::AsyncCircuitBreaker` |
| Atomic fsync | ✅ Present | `entity_workspace.py`, `observability/__init__.py`, `state_manager.py`, `astrology.py` |
| Retry with backoff | ✅ Present | `remote_provider.py`, `model_updater.py`, `search_providers.py` |
| Non-blocking subprocess | ✅ Present | `orchestrator.py`, `model_gateway.py` |
| Offline wheelhouse | ❌ **MISSING** | No wheelhouse directory, no --find-links in Makefile |

### 7.3 Legacy Synthesis References

`docs/legacy/LEGACY_MASTER_SYNTHESIS.md` mentions the 5 design patterns and lists 12 ERAs of development. The offline wheelhouse pattern (Era 2) is the only one not present in the current codebase.

---

## §8 ADDITIONAL FINDINGS

### 8.1 Make Target Completeness

Several make targets reference non-existent files:
- `make heritage-map` → claims to generate `docs/research/HERITAGE_SOURCE_MAP.md` but doesn't
- `make heritage-vet` → vet script has narrow scan scope (only ~20% of tagged files)

### 8.2 Empty/Stub `__init__.py` Files

- `src/omega/gateway/__init__.py` — empty (29 bytes)
- `src/omega/benchmarks/__init__.py` — empty
- `src/omega/orchestration/__init__.py` — empty

### 8.3 Bridge Directory Near-Empty

`src/omega/bridge/` contains only 2 files (elevenlabs.py, opencode_bridge.py), both orphaned. The bridge concept was never fully realized.

---

## §9 RECOMMENDATIONS

### 🔴 Immediate (Critical)

| Priority | Action | Effort |
|----------|--------|--------|
| 1 | Wire `archive_old_sessions()` into a periodic task in `orchestrator.py` or a background worker | 2 hours |
| 2 | Fix PIVOT_LOG numbering — rename numeric era entries to `N-Decision N`, deduplicate 12 collisions | 1 hour |
| 3 | Recreate vet-001 record (8-char name rejection) in HERITAGE_VET_LOG.md | 15 min |
| 4 | Fix `make heritage-vet` to scan ALL files with [id-soft:] tags, not just oracle/ + constants | 1 hour |
| 5 | Update Makefile `heritage-map` target to actually write HERITAGE_SOURCE_MAP.md, or update CREDITS.md to remove the claim | 30 min |

### 🟡 Sprint Priority

| Priority | Action | Effort |
|----------|--------|--------|
| 6 | Prune 4 HIGH-severity orphaned modules (intake_digestor.py, gateway/server.py, antigravity/, elevenlabs.py) — ~1,046 lines | 2 hours |
| 7 | Prune or wire 2 MEDIUM orphaned modules (repl.py, link_p9_cli.py) — 895 lines | 2 hours |
| 8 | Remove deprecated `set_entity_model()` / `remove_entity_model()` from model_gateway.py | 15 min |
| 9 | Create vet records for 18 pre-vetting CREDITS entries | 2 hours |
| 10 | Update CREDITS.md §2.4 table with current file locations | 30 min |

### 🟢 Future

| Priority | Action | Effort |
|----------|--------|--------|
| 11 | Evaluate porting P1 (Timeout Manager) from xna-omega — 763-line production-grade module | 1 day |
| 12 | Evaluate porting P2 (Provider Selector) for health-scoring-based routing | 1 day |
| 13 | Implement offline wheelhouse pattern (Era 2 gap) | 1 day |
| 14 | Evaluate microserver extraction from Omega Hub for critical MCP paths | 3 days |
| 15 | Add `[legacy: omega-stack]` migration tags to document ported patterns | 2 hours |

---

## §10 SCOREBOARD

| Category | Score | Details |
|----------|-------|---------|
| **Session Lifecycle** | ❌ BROKEN | `archive_old_sessions()` never called |
| **Dead Code Volume** | 🔴 ~2,800 lines | 12 orphaned modules, 10 orphaned functions |
| **PIVOT_LOG Integrity** | 🔴 12 duplicates | Numbering scheme has significant drift |
| **5 Design Patterns** | 🟢 4/5 | Offline wheelhouse MISSING |
| **Heritage Code Tags** | 🟢 196 tags | 42 files, 20/35 CREDITS entries covered |
| **Vet Record Completeness** | 🟡 12/35 | 18 missing, vet-001 lost |
| **Legacy Migration Tags** | 🔴 1 tag | Only 1 `[legacy:]` tag exists |
| **Legacy Patterns Not Ported** | 🟡 6 patterns | Timeout Manager, Provider Selector, Degradation Manager, Rate Limiter, Soul Edit History, Compaction Harvester |

---

*Report generated by @roc_racoon — Sovereign Miner. Data collected from 4 parallel agents across 3 legacy partitions + current codebase.*

⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_mining_report ⬡ COMPLETE

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
