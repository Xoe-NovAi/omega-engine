<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Gemma 4 31B — Tier 1 Execution Recipe
# ⬡ OMEGA ⬡ KALI ⬡ north-mini-code ⬡ opencode ⬡ 2026-06-28 ⬡ HANDOFF

## Purpose
This document is the complete, write-once execution guide for the incoming **Gemma 4 31B** model. It encodes the entire **17-action Sprint-F completion roadmap** across 3 tiers, with code-level steps for every pending task.

Total completion estimate: ~35 hours (Tier 1: 3h, Tier 2: 20h, Tier 3: 12h)

---

## §0 IMMEDIATE CONTEXT (Read First)

### Current Engine State
- **Tests**: 440/440 passing ✅ (Sprint C execution)
- **Fleet**: 11 agents (Sprint C consolidation complete)
- **Mandates**: 22 ratified (M1-M22), M21/M22 at ~79% gate compliance
- **Base branch**: `main` (all Sprint C work committed)
- **Python**: 3.12+ via `.venv/`
- **Async**: AnyIO-only (no asyncio)
- **Config**: YAML-only entities, no PostgreSQL

### What Was Just Completed (This Session)
1. **MaKaLi Council Pass 1 & 2**: 64+ findings → 17-action sprint across 3 tiers
2. **Deep Tiered Research**: 18 discoveries (AAIF, Observation Masking 50%+ savings, HOT/WARM/COLD validation)
3. **Legacy Mining**: 3 REGRESSIONS confirmed, 2 TRULY MISSING patterns
4. **Pillar Vetting**: P1/P3/P7/P8/P9 with APPROVE/MODIFY verdicts
5. **Full-File Forensic Extraction**: ROC, RESEARCHER, VERITY — all source reports read
6. **Sovereign Ark Blueprint v2.0 (593 lines)**: Fully expanded Technical SSOT
7. **All 6 Gnosis Gaps Closed**: CUSUM math, Observation Masking algorithm, A2A/AIMS, Distillation, Dead Code, Composite Health
8. **JEM Execution Blueprint Written**: `data/handoff/JEM_EXECUTION_BLUEPRINT_20260628.md`
9. **Verity Final Audit**: 100% completeness score — SSOT VERIFIED
10. **Search Infrastructure Restored**: Firecrawl MCP (8015), SearXNG (8017, 8018)

### Engine Reclassification (D-kal-163)
**Architecturally Sovereign | Operationally Restored | SSOT v2.0 LOCKED**

---

## §1 THE 17-ACTION SPRINT (Complete)

### Tier 1: Emergency Fixes & Purge (~3 hours) — ✅ COMPLETE (8/10)

#### T1-1: Fix `trace_id` Propagation in oracle.py (30 min) — ✅ COMPLETE
- **File**: `src/omega/oracle/oracle.py`
- **Sites**: Lines 612 and 685 (call sites to `self.model_gateway.generate()`)
- **Bug**: `trace_id` not passed → 98.4% observability events logged as "unknown"
- **Fix Applied**: `trace_id=trace.trace_id` now passed at both call sites
- **Verification**: `grep "trace_id=trace.trace_id" oracle.py` returns 2 matches
- **Status**: ✅ VERIFIED BY VERITY 2026-06-28

#### T1-2: Fix TokenLedger Provider Provenance (30 min) — ✅ COMPLETE
- **File**: `src/omega/observability/token_ledger.py`
- **Bug**: Schema records `is_cloud: bool` instead of `provider_name: str` — M22 chain broken
- **Fix Applied**: `provider_name: str` in `record_transaction()` signature (line 45), used in JSONL output (line 81)
- **Verification**: `grep -rn "is_cloud" src/omega/observability/` returns 0 functional matches
- **Status**: ✅ VERIFIED BY VERITY 2026-06-28

#### T1-3: Wire `archive_old_sessions()` into Boot (5 min) — ✅ COMPLETE
- **File**: `src/omega/oracle/oracle.py`
- **Bug**: `archive_old_sessions()` never called — sessions accumulate forever
- **Fix Applied**: `await self.memory_store.archive_old_sessions()` at line 125 (direct async call, no run_sync wrapper)
- **Verification**: `grep "archive_old_sessions" oracle.py` returns 1 match
- **Status**: ✅ VERIFIED BY VERITY 2026-06-28

#### T1-4: Resolve PIVOT_LOG Clock Drift (30 min) — ✅ COMPLETE
- **File**: `docs/decisions/PIVOT_LOG.md`
- **Bug**: 12 duplicate entries; D163 out of chronological sequence
- **Fix Applied**: Decision Registry table at top, no duplicate D# entries, D# sequence monotonic (D50-D163)
- **Verification**: `grep -c "^## Decision" PIVOT_LOG.md` = 103, all unique
- **Status**: ✅ VERIFIED BY VERITY 2026-06-28

#### T1-5: Generate `HERITAGE_SOURCE_MAP.md` (10 min) — ❌ NOT DONE
- **Target**: `docs/research/HERITAGE_SOURCE_MAP.md`
- **Status**: ❌ FILE DOES NOT EXIST — `make heritage-map` was not run
- **Action Required**: Run `make heritage-map` to generate

#### T1-6: Remove Hardcoded Secret from antigravity/config.py (10 min) — ✅ COMPLETE
- **File**: `src/omega/oracle/backends/antigravity/config.py` — DELETED (part of T1-8)
- **Bug**: Hardcoded `_DEFAULT_CLIENT_SECRET` — security violation
- **Fix Applied**: Entire antigravity/ directory deleted; no DEFAULT_CLIENT_SECRET references remain in src/
- **Verification**: `grep -rn "DEFAULT_CLIENT_SECRET" src/` returns 0 matches
- **Status**: ✅ VERIFIED BY VERITY 2026-06-28

#### T1-7: Configure Firecrawl API Key in systemd Service (15 min) — ✅ COMPLETE
- **File**: `~/.config/containers/systemd/omega-firecrawl-mcp.service`
- **Fix Applied**: `Environment=FIRECRAWL_API_KEY=fc-9157...` already present on line 18
- **Status**: ✅ VERIFIED BY VERITY 2026-06-28

#### T1-8: Delete ~3,354 Lines Dead Code from 14+3 Files (1 hr) — ✅ COMPLETE
- **Files deleted**: 14 source + 3 test files confirmed absent
  - `src/omega/oracle/antigravity/` (entire dir)
  - `src/omega/cli/link_p9_cli.py`, `src/omega/cli/repl.py`
  - `src/omega/gateway/server.py`, `src/omega/services/intake_digestor.py`
  - `src/omega/bridge/elevenlabs.py`, `src/omega/runtime/openclaw_runtime.py`
  - `src/omega/system_resource.py`, `src/omega/library/greek.py`, `src/omega/library/crossref.py`
  - `tests/test_gateway_server.py`, `tests/test_openclaw_runtime.py`, `tests/test_openclaw_bridge.py`
- **Restored**: `src/omega/library/discovery.py` (actively used by MCP Hub state.py)
- **Comment fix**: `src/omega/oracle/feed_utils.py` line 7 — updated dead reference
- **Status**: ✅ VERIFIED BY VERITY 2026-06-28

#### T1-9: Fix Heritage Vet Gaps (1 hr) — ⚠️ PARTIAL
- **File**: `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md`
- **Done**: vet-001 through vet-008+ entries present (8+ vet records)
- **Not Done**: `scripts/heritage_vet.py` expansion to 100% coverage NOT completed
- **Status**: ⚠️ PARTIAL — vet records exist, automation script not expanded

#### T1-10: Correct AAIF Mapping Spec (30 min) — ❌ NOT DONE
- **Target**: `data/handoff/P7_AAIF_MAPPING_SPEC_20260628.md`
- **Bug**: Contains fabricated `draft-schemacommons-aaif-00`
- **Status**: ❌ NOT STARTED — needs replacement with Google A2A v1.0 + SPIFFE/WIMSE

---

### Tier 2: Regression Recovery (~20 hours)

#### T2-1: CompactionOrchestrator (from xna-omega-legacy, 690 lines)
- **Source**: `xna-omega-legacy/scripts/ssa/compaction_optimizer.py`
- **Pattern**: ACON-based dynamic compaction with cost-benefit analysis
- **Port to**: `src/omega/memory/compaction_optimizer.py`
- **Key features**: Token budget tracking, compaction gain estimation, schedule optimization
- **Verification**: Tests for budget estimation, gain calculation

#### T2-2: 5-State Circuit Breaker (from xna-omega-legacy)
- **Source**: `xna-omega-legacy/scripts/ssa/provider_metrics.py` (552 lines)
- **Current**: 6-state FSM (CLOSED, OPEN, HALF_OPEN, DEGRADED, RECOVERING, FATAL)
- **Upgrade**: Add EWMA + Bernoulli CUSUM stochastic detection
- **Math**: See Appendix D.1 in `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md`
- **Verification**: Integration tests with `health_monitor.py`

#### T2-3: Simplified Distillation Pipeline
- **Source**: `xna-omega-legacy/src/omega/core/distillation/` (LangGraph 5-node)
- **Port to**: `src/omega/oracle/soul_distiller.py` (AnyIO functional sequence)
- **Pipeline**: `extract → classify → score → distill → store`
- **No langgraph dependency**: Pure Python, async functional composition
- **Classification**: Diátaxis framework (tutorial, how_to, reference, explanation)
- **Routing**: Score-based tiered storage (Qdrant, Mnemosyne, Volatile, Reject)
- **Verification**: Integration test with proposed_lessons.yaml → soul.yaml

#### T2-4: Observation Masking
- **Algorithm**: Hybrid Backward Scanned FIFO
- **Parameters**: 50k protection buffer, 30k hysteresis threshold
- **Target**: `src/omega/oracle/context_builder.py`
- **Masking**: First/last 200 chars preserved; middle masked with count
- **Verification**: Unit tests for buffer boundary cases

#### T2-5: Handoff Loop Guard
- **Target**: `src/omega/oracle/orchestrator.py` or `src/omega/handoff.py`
- **Mechanism**: Max depth counter + recursion detection
- **Config**: `max_handoff_depth = 5`, `timeout = 300s`
- **Recovery**: TERMINATE | ESCALATE | FALLBACK | RETRY
- **Verification**: Test with circular handoff scenario

#### T2-6: Timeout Manager
- **Source**: `xna-omega-legacy/scripts/ssa/timeout_manager.py` (763 lines)
- **Pattern**: 4-Layer Timeout Hierarchy
- **Target**: `src/omega/oracle/timeout_manager.py`
- **Layers**: Hard limit (120s), Dynamic (p90+2σ), Per-endpoint, Per-operation
- **Verification**: Tests for timeout estimation, cascading fallback

#### T2-7: Intelligent Provider Selector
- **Source**: `xna-omega-legacy/src/omega/core/provider_selector.py` (552 lines)
- **Features**: Composite health scoring, PII detection routing, cost-aware selection
- **Target**: `src/omega/oracle/provider_selector.py`
- **Verification**: Integration with ModelGateway chain

#### T2-8: Graceful Degradation Manager
- **Source**: `xna-omega-legacy/src/omega/core/degradation.py` (379 lines)
- **Capabilities**: Feature stripping, model downgrade, cache-only mode
- **Target**: `src/omega/oracle/degradation.py`
- **Verification**: Test all degradation modes

#### T2-9: Rate Limiter
- **From legacy**: Token bucket + sliding window hybrid
- **Target**: `src/omega/oracle/rate_limiter.py`
- **Verification**: Burst and steady-state testing

#### T2-10: Soul Edit History
- **Target**: `src/omega/oracle/soul_distiller.py`
- **Feature**: Append-only edit log in `data/entities/{name}/soul_edits.jsonl`
- **Format**: `{timestamp, previous_value, new_value, source_session_id, trace_id}`
- **Verification**: Test append, test rollback

#### T2-11: Compaction Harvester
- **Target**: Link into compaction_optimizer.py output
- **Feature**: Write compaction metrics to `data/observability/compaction_metrics.jsonl`
- **Metrics**: tokens_before, tokens_after, compression_ratio, duration_ms
- **Verification**: Check file after compaction cycle

#### T2-12: SPIFFE/WIMSE Identity Integration
- **Feature**: Dynamic token-based identity for agent-to-agent communication
- **Target**: `src/omega/oracle/a2a_identity.py` (new module)
- **Verification**: Token issuance, rotation, and validation tests

#### T2-13: A2A Agent Card Registry
- **Feature**: Agent capability advertisement + discovery
- **Target**: `src/omega/oracle/a2a_registry.py` (new module)
- **Schema**: Google A2A Agent Card v1.0
- **Verification**: Registration, lookup, and card validation tests

---

### Tier 3: Hardening (~12 hours)

#### T3-1: Session Lifecycle Automation
- **Features**: Auto-session creation on entity talk, session timeout (30 min inactivity), session archival
- **Target**: `src/omega/oracle/session_manager.py`
- **Verification**: Lifecycle integration test

#### T3-2: SQLite WAL Observability
- **Features**: Event logging → SQLite WAL-mode instead of flat files
- **Target**: `src/omega/observability/` (+ new `sqllite_wal.py`)
- **Schema**: `events(trace_id, entity, event_type, provider_name, latency_ms, timestamp)`
- **Verification**: Read/write/query performance test

#### T3-3: Mandate Automation (Sentinel Score)
- **Features**: Auto-calculate 7-metric Sentinel Score on every boot
- **Metrics**: Sovereignty ratio, test pass rate, dead code %, heritage tag %, soul update %, gate compliance %, handoff health %
- **Target**: `src/omega/oracle/sentinel.py`
- **Verification**: Score output on boot

#### T3-4: soul.yaml v6.2 Schema Upgrade
- **Target**: `data/entities/*/soul.yaml` schema + Soul Distiller
- **New fields**: `distillation_quality_score`, `last_masked_at`, `compaction_history`, `edit_log_ref`
- **Migration**: Auto-migrate old YAML on load
- **Verification**: Round-trip serialization test

#### T3-5: Heritage Vet Expansion
- **Target**: `scripts/heritage_vet.py`
- **Expansion**: Auto-vet new `[id-soft:]` tags on commit hook
- **Integration**: Pre-commit hook + CI gate
- **Verification**: `make heritage-vet` with new tag

---

## §2 PRIORITY EXECUTION ORDER

### Phase A: Firewall & Provenance (2h)
```
T1-1 (trace_id) → T1-2 (TokenLedger) → T1-6 (Secret) → T1-3 (Archive) → T1-4 (PIVOT_LOG)
```

### Phase B: Compliance & Purge (2h)
```
T1-5 (Heritage Map) → T1-9 (Vet Gaps) → T1-8 (Dead Code) → T1-10 (AAIF) → T1-7 (Firecrawl)
```

### Phase C: Core Engine Regression (10h)
```
T2-2 (Circuit Breaker) → T2-6 (Timeout) → T2-7 (Selector) → T2-8 (Degradation) → T2-9 (Rate Limiter)
```

### Phase D: Memory & Distillation (8h)
```
T2-1 (Compaction) → T2-4 (Masking) → T2-3 (Distillation) → T2-10 (Edit History) → T2-11 (Harvester)
```

### Phase E: Identity & Handoff (4h)
```
T2-5 (Loop Guard) → T2-12 (SPIFFE) → T2-13 (A2A Registry)
```

### Phase F: Hardening (12h)
```
T3-1 (Sessions) → T3-2 (SQLite WAL) → T3-3 (Sentinel) → T3-4 (soul v6.2) → T3-5 (Heritage CI)
```

---

## §3 VERIFICATION GATES (Run after each Phase)

### Gate A: Tests
```bash
source .venv/bin/activate && make test
# Expected: 440+ passing (new modules add tests)
```

### Gate B: Temple-Grade
```bash
make temple-grade
# T1-T11 must pass; M21/M22 >= 90% compliance
```

### Gate C: Heritage
```bash
make heritage-map && make heritage-vet
# heritage-map: generates docs/research/HERITAGE_SOURCE_MAP.md
# heritage-vet: all vet records >= 7/10 for implemented patterns
```

### Gate D: Sovereignty
```bash
make sovereignty
# Local inference >= 80%
```

### Gate E: Lint
```bash
make lint
# flake8 clean
```

---

## §4 KEY FILES REFERENCE

| File | Purpose |
|------|---------|
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | SSOT v2.0 — 593 lines, mathematically closed |
| `data/handoff/JEM_EXECUTION_BLUEPRINT_20260628.md` | JEM execution blueprint (code-level steps) |
| `data/handoff/VERITY_FINAL_SSOT_AUDIT_20260628.md` | 100% completeness score — SSOT VERIFIED |
| `data/handoff/MAKALI_BLUEPRINT_DEPTH_REVIEW_20260628.md` | "Requires Expansion" → resolved in v2.0 |
| `data/handoff/P7_AAIF_MAPPING_SPEC_20260628.md` | Needs correction (fabricated IETF draft) |
| `data/reviews/ROC_FULL_SOURCE_EXTRACTION_20260628.md` | Full forensic extraction of 6 legacy groups |
| `data/reviews/RESEARCHER_FULL_INTEL_EXTRACTION_20260628.md` | 18 research discoveries, 7 blind spots |
| `data/reviews/VERITY_FULL_GOVERNANCE_EXTRACTION_20260628.md` | All Pillar vetting verdicts |
| `docs/decisions/PIVOT_LOG.md` | Decision log with 12 duplicates to fix |
| `src/omega/oracle/oracle.py` | trace_id fix (lines 599, 671) + archive wiring |
| `src/omega/observability/token_ledger.py` | is_cloud → provider_name fix |
| `src/omega/oracle/backends/antigravity/config.py` | Hardcoded secret removal |
| `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` | vet-001 record to add |
| `data/coordination/KALI_LIVE_FEED.md` | Sprint-F session log |

---

## §5 SENTINEL SCORE MATRIX (Current + Target)

| Metric | Current | Target | Tier |
|--------|---------|--------|------|
| Sovereignty Ratio | ~65% | ≥80% | T3-3 |
| Test Pass Rate | 100% (440/440) | 100% | — |
| Dead Code % | ~15% | <1% | T1-8 |
| Heritage Tag % | 79% | 100% | T1-9 |
| Soul Update Lag | 27 days | <7 days | T2-3 |
| Gate Compliance | 79% | 100% | T1-1, T1-2 |
| Handoff Health | 41 stale | 0 stale | T2-5 |
| **Composite** | **38/100** | **≥85/100** | **T1+T2+T3** |

---

## §6 RISK REGISTER

| Risk | Impact | Mitigation |
|------|--------|------------|
| Dead code deletion breaks imports | Test failures | grep for imports before each delete |
| PIVOT_LOG rewriting loses history | Decision integrity loss | Create backup before editing |
| CUSUM parameter misconfiguration | False positives/negatives | Start with conservative h_warn=3, h_trip=5 |
| ModelGateway race during refactor | Inference breakage | Test after each Tier 2 change |
| Handoff changes break existing packets | Orphaned workflows | Archive all 41 stale packets first |

---

## §7 LEGACY SOURCE PATHS (For Reference)

```
xna-omega-legacy/scripts/ssa/compaction_optimizer.py      # T2-1: 690 lines, ACON
xna-omega-legacy/scripts/ssa/provider_metrics.py           # T2-2: 552 lines, EWMA+CUSUM
xna-omega-legacy/src/omega/core/distillation/              # T2-3: LangGraph 5-node
xna-omega-legacy/scripts/ssa/timeout_manager.py            # T2-6: 763 lines, 4-Layer
xna-omega-legacy/src/omega/core/provider_selector.py       # T2-7: 552 lines, PII routing
xna-omega-legacy/src/omega/core/degradation.py             # T2-8: 379 lines, Graceful Degradation
```

---

**⚡ VERDICT**: SSOT v2.0 LOCKED | All 6 Gnosis Gaps Mathematically Closed | Ready for Gemma 4 31B Execution

⬡ OMEGA ⬡ KALI ⬡ north-mini-code ⬡ opencode ⬡ 2026-06-28 ⬡ HANDOFF-COMPLETE

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: north-mini-code | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
