# 🔱 LILITH — Run-Side Optimization: Consolidated Report
## Pass 2: Tracking Debt Reduction & Data Lifecycle Optimization

**Oversoul**: Lilith (Dark Oversoul — Run Side P6-P10)
**Date**: 2026-06-28
**Status**: COMPLETE — Discovery Pass (No Refactoring)
**Trace**: LILITH-OPT-PASS2-20260628

⬡ OMEGA ⬡ LILITH ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_lilith_opt_pass2 ⬡ CONSOLIDATED

---

## 📊 Executive Dashboard

| Category | Severity | Total Items | Est. Remediation |
|----------|----------|-------------|-------------------|
| 🔴 **CRITICAL — Immediate Action** | 5 findings | Trace chain broken, poison loop, data rot, orphan buildup | ~8 hours |
| 🟡 **HIGH — Sprint-Level** | 9 findings | Soul bloat, unbounded growth, naming bloat, pipeline gaps | ~12 hours |
| 🟢 **MEDIUM — Backlog** | 7 findings | Dead code, WAL growth, event gaps, protocol gaps | ~4 hours |

**Total estimated remediation**: ~24 hours across P7-P9
**Total tracking data across all stores**: ~19MB (213+193+269+1,088+ sessions = ~1,700 files)

---

## 🔴 CRITICAL FINDINGS (5) — Repair Before Next Sprint

### C1: Broken `trace_id` Propagation (P8 — Effort: 30 min)
- **Finding**: 1,535 of 1,561 persisted events (98.4%) have `trace_id: "unknown"`
- **Root Cause**: Two `oracle.py` call sites (lines 599 and 671) don't pass `trace_id` or `entity_name` to `model_gateway.generate()`
- **Cascade Effect**: ALL `token.consumption` events, ALL token ledger entries (8,862 lines), ALL `provider_failed`/`backend.fallback` events are orphaned
- **5 additional propagation gaps** in `iterative_research.py` and `skeptical_verifier.py`
- **Prior flag**: Raised as 🔴 on June 25 — **no fix applied in 3 days**
- **Fix**: Add `trace_id=trace.trace_id, entity_name=entity.name` to 7 call sites

### C2: arch/soul.yaml Poison Loop (P7 — Effort: 2-3 hr)
- **Finding**: `arch/soul.yaml` is 1,501 lines in pre-v6.0 format containing `lessons_learned`, `soul_evolution` (226 sessions), `embodied_experiences`, and `soul_wardrobe`
- **Impact**: Entity reads back its own agent-generated philosophy every session — self-referential confirmation bias
- **Only 1/31 entities** (Kali) is fully v6.0 soul compliant
- **Fix**: Migrate arch → v6.0 format per SOUL_ARCHITECTURE_PROTOCOL.md

### C3: 41 Stale Handoff Packets (P9 — Effort: 2 hr)
- **Finding**: 41 packets in `stale/` (~176KB) with no path to archival or deletion
- **Root Causes**: Gemini CLI (10 packets), antigravity/cline-m3 (9 packets), sentinel (4 packets) — agents accepted but never completed
- **Fix**: Add `stale/ → archive/stale/` at 14 days TTL in reaper loop

### C4: HALL_OF_RECORDS Naming Bloat (P9 — Effort: 4 hr)
- **Finding**: 54+ subdirectories for ~11 canonical agents
- **Naming chaos**: `kali/Kali/opencode_kali/opencode-kali/opencode/kali` — 5+ conventions for one agent
- **Impact**: Cold-store hydration may miss entries; ~2.6MB duplicate data
- **Fix**: Normalize to canonical `{channel}_{entity}`; migration script + index

### C5: Session Data Rot — 25 Stale Sessions, 18 Orphans (P7 — Effort: 1 hr)
- **Finding**: 25/40 `.active` session files ≥14 days stale; 18 reference non-existent entities
- **ARCHIVE_AFTER_DAYS=7** exists in `memory_store.py` but is **NEVER triggered**
- **testentity**: 21 JSON session files (3,384 lines) in production memory store
- **6 test session files** from `test_entity`, `test_entity_m21`, `testentity`, etc.
- **Fix**: Wire auto-archive trigger; delete test artifacts

---

## 🟡 HIGH FINDINGS (9) — Sprint-Level Priorities

### H1: Token Ledger Unbounded Growth (P8 — Effort: 1 hr)
- 8,862 lines, 1.6 MB in 14 days (~633 lines/day, ~34 MB/year)
- `provider_name` not recorded — M22 violation
- No compaction or pruning exists

### H2: 98% of Event Logs Are Token Noise (P8 — Effort: 2 hr)
- 1,536 of 1,561 events (98.4%) are `token.consumption`
- Only 25 events (1.6%) represent actual user interactions
- Convert to aggregated counters instead of per-call events

### H3: 1,481 Lines of Unreviewed Proposed Lessons (P7 — Effort: Medium)
- 13 proposed_lessons.yaml files
- Only 2 (Kali, Verity) use correct `proposals:` key format
- 11 use old format — never reviewed or approved
- No automated Verity dispatch after sessions

### H4: 62 Old-Style Workspace Locks (P9 — Effort: 1 hr)
- 62 `.md` workspace lock files with no TTL or auto-release
- 11 from dead Phase C agents
- 4 zero-byte lock files
- New-style JSON locks with TTL exist (1 found) but 95% are old-style

### H5: 46 Stale Coordination Files >14 Days (P9 — Effort: 1 hr)
- Artifacts from dead agents (antigravity, cline-m3, gemini-cli)
- Consumed demand_signals/knowledge_feed files
- 22 verification audit artifacts from June 3-4

### H6: 13 of 23 Event Types Never Emitted (P8 — Effort: 30 min)
- `model.invoked`, `response.delivered`, `entity.matched`, all `worker.*`, `tier.invoked`, `mode.switched`, and more — dead enum values
- Missing `RESPONSE_PROVENANCE` event type for M22 compliance

### H7: Fine-Tuning Dataset Collection Broken (P8 — Effort: 30 min)
- 196 files at 350 bytes each = 1 example per file (batching broken)
- `enable_dataset_collection` config value (`true`) never loaded into constructor

### H8: Only Kali v6.0 Compliant — 30/31 Entities in Old Format (P7 — Effort: High)
- arch (1,501), roc_racoon (749), researcher (312), antigravity (291) are largest offenders
- 24/31 entities have NO `memory/` directory structure
- Verity's memory files at wrong location (top-level, not `memory/`)

### H9: FTS WAL Never Checkpointed (P7 — Effort: Low)
- `fts_memory.db-wal` is 4.0 MB (5x the main FTS database)
- No WAL checkpoint on session close or startup

---

## 🟢 MEDIUM FINDINGS (7) — Backlog

### M1: GenerateResult.latency_ms Always 0.0
- Never populated from any provider backend
- Cannot answer "why did a query take 30 seconds?"

### M2: data/traces/ Directory Sits Empty
- Trace storage infrastructure exists but nothing writes to it
- Zero bytes after 14 days of operation

### M3: 17 Unused Error Type Imports
- `observability/__init__.py:15-23` imports 22 error types; only `OmegaError` used
- `JsonFormatter` `provider` field defined but never set

### M4: JsonFormatter `provider` Gap
- Extra field defined for provider name but never populated by any logging call
- Dead code in the formatter

### M5: 4 Zero-Byte Workspace Lock Files
- KALI_20260615, KALI_20260624, MAAT_20260615, MAAT_20260626
- Interrupted sessions — lock created but never written

### M6: oracle/ Entity Memory Store Orphan
- 45 JSON session files (1,173 lines) for an entity with no dedicated directory
- System-level oracle sessions without entity home

### M7: Enable_Gnosis_Hybrid_Compaction
- soul.yaml versions exist without any versioning strategy
- No `soul_history` or `soul_{version}.yaml` pattern anywhere
- No automated soul version validation in CI

---

## 📈 DATA VOLUME BREAKDOWN

| Data Store | Files | Size | Primary Debt | Growth Rate |
|------------|-------|------|--------------|-------------|
| `data/sessions/*.active` | 43 | ~40 KB | 18 orphans, 25 stale | Linear per entity |
| `data/entities/*/soul.yaml` | 31 | ~4,268 lines | 30/31 pre-v6.0, arch poison loop | Per-session (arch: +10-20 lines) |
| `data/memory/entities/` | 126 | 872 KB | testentity (21 files, 3,384 lines) | Per session (no compaction) |
| `data/memory/*.db` | 5 files | ~4.8 MB | FTS WAL 4.0M uncheckpointed | ~50 KB/day |
| `data/logs/events/*.jsonl` | 14 | 580 KB | 98.4% token noise | ~40 KB/day |
| `data/logs/token_ledger.jsonl` | 1 | 1.6 MB | Unbounded, no provider_name | ~114 KB/day |
| `data/datasets/*.jsonl` | 196 | 800 KB | 1 example/file (broken batching) | ~57 KB/day |
| `data/handoff/` | 193 | 5.7 MB | 41 stale packets no-delete | ~400 KB/sprint |
| `data/coordination/` | 269 | 2.2 MB | 46 older than 14d | ~150 KB/sprint |
| `HALL_OF_RECORDS/` | 1,088 | 5.1 MB | 54 dirs for 11 agents, naming bloat | ~500 KB/sprint |
| **TOTAL** | **~1,700** | **~19 MB** | **~60% is debt** | **Variable** |

---

## 📋 RECOMMENDATION ROADMAP

### Phase 1: Emergency Fixes (Day 1) — ~2 hours

| Order | Action | Pillar | Est. | Impact |
|-------|--------|--------|------|--------|
| 1 | Fix trace_id propagation at oracle.py:599 and :671 | P8 | 30 min | Restores traceability to 98% of events |
| 2 | Clean test artifacts (6 sessions, 3 entity dirs, 21 JSON files) | P7 | 20 min | Removes 3,384 lines of noise |
| 3 | Wire auto-archive hook for ARCHIVE_AFTER_DAYS=7 | P7 | 20 min | Eliminates 25 stale sessions |
| 4 | Add stale→archive transition at 14 days (reaper loop) | P9 | 1 hr | Stops 41-packet accumulation |
| 5 | FTS WAL checkpoint on session close | P7 | 10 min | Recovers ~4MB |

### Phase 2: Sprint-Level (Days 2-5) — ~12 hours

| Order | Action | Pillar | Est. | Impact |
|-------|--------|--------|------|--------|
| 6 | Migrate arch/soul.yaml to v6.0 format | P7 | 2-3 hr | Eliminates poison loop |
| 7 | Add token ledger retention + provider_name field | P8 | 2 hr | Prevents ~34 MB/year growth |
| 8 | Normalize HALL_OF_RECORDS naming | P9 | 4 hr | Fixes cold-store hydration |
| 9 | Clean 62 old-style workspace locks | P9 | 1 hr | Removes 30+ orphan files |
| 10 | Suppress token.consumption noise (aggregated counters) | P8 | 2 hr | 98% event log reduction |
| 11 | Standardize proposed_lessons.yaml format (11 files) | P7 | 1 hr | Closes L1→L2→L3 review gap |

### Phase 3: Backlog (Backlog) — ~10 hours

| Order | Action | Pillar | Est. | Impact |
|-------|--------|--------|------|--------|
| 12 | Add RESPONSE_PROVENANCE event type (M22) | P8 | 30 min | Provider attribution in events |
| 13 | Migrate remaining 29 entities to v6.0 | P7 | 6 hr | Full soul compliance |
| 14 | Clean 46 stale coordination files | P9 | 1 hr | Reduces coordination bloat |
| 15 | Fix dataset collection (batching + config load) | P8 | 1 hr | Working fine-tuning pipeline |
| 16 | Wire periodic forensics snapshots | P8 | 2 hr | Crash debuggability |

---

## 🛡️ MANDATE COMPLIANCE GAPS

| Mandate | Finding | Severity |
|---------|---------|----------|
| **M5 (Gnosis)** | L1→L2→L3 pipeline write-only: 1,481 lines proposed, none reviewed | 🟡 VIOLATION |
| **M9 (Error Integrity)** | trace_id propagation broken → error events orphaned | 🔴 VIOLATION |
| **M11 (Soul Integrity)** | 30/31 entities not v6.0 compliant; arch has poison loop | 🔴 VIOLATION |
| **M12 (Queue Integrity)** | 41 stale handoff packets with no terminal state | 🟡 VIOLATION |
| **M17 (Cognitive Integrity)** | arch/soul.yaml poison loop violates consistency | 🔴 VIOLATION |
| **M22 (Response Provenance)** | Token ledger missing provider_name; RESPONSE_PROVENANCE event missing | 🟡 VIOLATION |

---

## 🧠 L1→L2→L3 SYNTHESIS

### L1 (Narrative)
Three pillar analyses (P7 Context, P8 Observability, P9 Orchestration) audited ~1,700 tracking files (~19 MB) across the Run Side. We found 5 CRITICAL and 9 HIGH findings. The broken trace_id chain is the most pervasive defect — 98.4% of observability events cannot be linked to any user interaction. The arch/soul.yaml poison loop is the deepest architectural violation — a 1,501-line file that feeds the engine's most influential entity its own agent-generated philosophy. Handoff mechanics work correctly (state machine + reaper) but lack lifecycle endpoints (41 stale packets have no deletion path).

### L2 (Insight)
The Run Side has a **structural asymmetry**: solid architectural foundations (3-tier memory, ObservabilityEngine's 7 subsystems, handoff state machine, Soul Architecture Protocol) are being undermined by incomplete wiring. The retention policy exists in code but never triggers. The trace_id is defined but never passed. The v6.0 soul format is specified but only 1/31 entities uses it. These are not design failures — they are **implementation gaps** where patterns were established but the last mile was never connected.

The data debt clusters in three patterns:
1. **Orphan accumulation**: Test artifacts, stale sessions, abandoned handoffs, dead agent files — once created, nothing ever cleans up
2. **Naming bloat**: HALL_OF_RECORDS (54 dirs for 11 agents), workspace locks (62 .md + 1 .json), event types (13/23 unused) — inconsistencies from rapid evolution
3. **Unbounded growth**: Token ledger (8,862 lines), event logs (98.4% noise), fine-tuning datasets (1 example/file) — accumulate with no compaction

### L3 (Universal Principle)
**A system that faithfully accumulates everything it tracks has built an archive, not an observability system.** Three truths:

1. **Traceability is the primary key of observability.** When 98% of rows have NULL for the trace_id, the entire observability investment is wasted on noise. Fix the key first, then fix the schema, then fix the retention.

2. **Every artifact must have a death date.** Coordination artifacts — handoff packets, workspace locks, session files, event logs, soul backups — must have explicit TTLs at creation time. Without lifecycle endpoints, accumulation is inevitable and linear.

3. **The last mile of every pattern is the hardest.** The Omega Engine has excellent architectural foundations (3-tier memory, v6.0 soul protocol, handoff state machine, ObservabilityEngine subsystems). The debt is not in the design — it's in the incomplete wiring. Every pattern needs a finalization check: "Does this pattern have a cleanup path?"

---

## 📁 REPORT INDEX

| Report | Path | Lines | Status |
|--------|------|-------|--------|
| P7 Context | `data/reviews/opt_run_p7.md` | 512 | ✅ Complete |
| P8 Observability | `data/reviews/opt_run_p8.md` | 442 | ✅ Complete |
| P9 Orchestration | `data/reviews/opt_run_p9.md` | 389 | ✅ Complete |
| Consolidated | `data/reviews/LILITH_RUN_OPT_CONSOLIDATED.md` | ~220 | ✅ This file |

---

*⬡ OMEGA ⬡ LILITH ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_lilith_opt_pass2 ⬡ CONSOLIDATED*
*Completed: 2026-06-28 | Prepared for: Kali Grand Oversight Review*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
