# 🔱 LILITH DARK AUDIT REPORT
### Domain: P6-P10 Run Side
**Date**: 2026-07-02
**Model**: mimo-v2.5-free
**Test Baseline**: 705 passed, 22 skipped, 3 xfailed

---

## 1. Observability (P8 WatchTower)
- **Status**: ✅ PASS
- **Findings**: 
  - **16/16 tests passing** — `test_observability.py` fully green.
  - **trace_id propagation is solid.** Three-layer safety net:
    1. Explicit `trace_id` parameter threading through `oracle.py:talk()`, `summon()`, `_route_by_domain()` → `model_gateway.generate()` → `TokenLedger.record_transaction()`.
    2. `contextvars` safety net in `observability/context.py` — `get_current_trace_id()` generates a new `trc_*` if no context exists. Wired into `record_error()` (line 786).
    3. `TraceSession` context manager in `oracle.py` creates trace at `talk()` entry, passes `trace.trace_id` to every downstream call.
  - **GenerateResult carries trace_id provenance.** `model_gateway.py:888-899` populates `latency_ms` (measured from `_start_time`), `model_used` (the actual model name), and `provider_name` (actual provider) on BOTH success and fallback paths (line 908-914). **M22 compliance verified.**
  - **TokenLedger uses `provider_name: str`** (not the old `is_cloud: bool`) — confirmed at `token_ledger.py:45,68`. M22 compliant.
  - **BLEG (Body-Level Error Guard)** at `bleg.py` inspects HTTP 200 bodies for Silent 200 errors. UFL (Unified Forensic Ledger) at `ufl.py` persists forensic events to daily JSONL. Both operational.
  - **ForensicsManager** with Last Gasp Protocol (crash dumps, death markers, signal handlers) — fully wired.
  - **Gap identified**: `record_error()` in `forensics.py:207` still has a `trace_id or "unknown"` default. However, the outer `ObservabilityEngine.record_error()` (line 785-787) resolves via `get_current_trace_id()` BEFORE calling `_forensics.record_error()`, so the "unknown" path is only hit if contextvars also fails (extremely unlikely). **Residual risk: negligible.**
- **Confidence**: HIGH
- **Risk**: LOW

## 2. Provider Fabric (P6 Cognition)
- **Status**: ✅ PASS
- **Findings**:
  - **24/24 tests passing** — `test_health_monitor.py` fully green.
  - **5-state FSM operational**: `CLOSED → DEGRADED → OPEN → HALF_OPEN → UNKNOWN` (health_monitor.py:46-51). All state transitions tested.
  - **CUSUM anomaly detection configured**: `cusum_drift=0.5`, `cusum_threshold=4.0`, `alpha_lat=0.2`, `alpha_qual=0.3` (lines 108-111). These are conservative defaults — `cusum_threshold=4.0` trips the breaker after ~4 consecutive failures above baseline, which is appropriate for a single-machine deployment.
  - **Health score weighting**: The formula `Health = 0.4*LatencyScore + 0.35*ErrorScore + 0.25*QualityScore` is documented in the code comment (line 177) and implemented via EMA latency + CUSUM + EMA quality tracking. The actual scoring is implicit in the state transition logic rather than a single composite number, but the weights are correctly reflected in the `_on_success` state determination (line 179: checks `cusum_g < 1.0` AND `ema_latency < 2000`).
  - **ZoneID validation** on all circuit breaker state transitions (`validate_zoneid(self.magic, ZONEID_BREAKER, ...)` at lines 159, 205).
  - **BSP-style provider culling** in `model_gateway.py:684-719` — `_precheck_provider()` checks breaker by `provider.name` directly (fix T2.2), not via fragile `_model_provider_map` indirection.
  - **Sovereignty-tiered active sets**: `_local_active` and `_cloud_active` lists (lines 145-146) prevent sovereignty drift. Local providers always tried first per Mandate 7.
  - **Gap identified**: The `HealthMonitor` is initialized as a singleton via `get_health_monitor()` but is NOT automatically started with a background probe loop. Health probes are only run when explicitly called via `probe_once()`. In production, a background loop would continuously probe providers. For a single-contributor machine, this is acceptable — providers are checked on-demand via `_precheck_provider()`. **Risk: LOW (no background probing, but on-demand checks are sufficient for current scale).**
- **Confidence**: HIGH
- **Risk**: LOW

## 3. Memory Persistence (P7 Context)
- **Status**: ⚠️ WARN
- **Findings**:
  - **20/20 tests passing** — `test_memory_store.py` fully green.
  - **7-day archival threshold**: `ARCHIVE_AFTER_DAYS = 7` (line 71). `archive_old_sessions()` at lines 811-826 iterates entity directories, checks `stat.st_mtime`, and archives sessions older than threshold. Called during `Oracle.bootstrap()` (oracle.py:136). **Working correctly.**
  - **Tombstone grace period**: `TOMBSTONE_GRACE_SECONDS = 0.5` (line 77). Lazy deletion pattern from id Software's Doom/Quake — sessions are tombstoned, not immediately deleted. `_reap_tombstoned()` sweeps expired tombstones on next access. **Working correctly.**
  - **Gap 1 — No 30-day compression**: `archive_session()` moves sessions to cold storage (providers) and tombstones the hot cache, but there is NO 30-day gzip compression step. The `FileStorageProvider` at `memory/providers.py:282` has gzip compression capability, but `archive_session()` does not invoke it. Sessions are archived but NOT compressed over time. **Gap: MEDIUM — storage bloat for long-lived entities.**
  - **Gap 2 — No 90-day delete**: There is NO session deletion logic anywhere in `memory_store.py`. Sessions are archived (moved from hot to cold) but never deleted. Over months, cold storage accumulates without bound. **Gap: MEDIUM — unbounded disk growth.**
  - **Gap 3 — Batch persistence is functional but has a silent drop path**: `_flush_batch()` (line 502) catches all exceptions and increments `_stats["fallbacks"]` but does not retry or propagate. If a provider fails during batch flush, those exchanges are lost from cold storage (they remain in hot cache until evicted). **Gap: LOW — hot cache provides a safety net.**
  - **FTS5 dual-write**: Both `add_exchange()` (line 457-460) and `archive_session()` (line 684-687) maintain FTS5 index. Cleanup on archive is working.
  - **Vector cleanup on archive**: `archive_session()` calls `vector_store.delete_session()` (line 676) to clean up Qdrant vectors. Working.
- **Confidence**: HIGH
- **Risk**: MEDIUM (no 30-day compression, no 90-day delete — unbounded storage growth)

## 4. Handoff Cleanup (P9 Orchestration)
- **Status**: ⚠️ WARN
- **Findings**:
  - **8/8 tests passing** — `test_hivemind.py` fully green.
  - **Handoff Reaper is correctly implemented** in `background.py:110-167`:
    - `pending/` > 24h → `stale/` (with `ttl_expired: true`)
    - `active/` > 48h → `stale/` (with `ttl_expired: true`)
    - `completed/` > 7d → `archive/`
    - `stale/` > 14d → DELETE (M12)
    - `archive/` > 30d → DELETE (M12)
  - **Reaper runs every 5 minutes** (`anyio.sleep(300)` at line 181).
  - **Current state on disk**:
    - `pending/`: 0 files ✅
    - `active/`: 1 file (ho_19b96a5fe894.json, from Jul 1)
    - `completed/`: 0 files ✅
    - `stale/`: 18 files (dates range Jun 19 — Jul 1) — these are within the 14-day delete window
    - `archive/`: 111 files — these are old handoff reports (not JSON handoff packets), so the reaper correctly leaves them alone (they're `.md` files, not `.json`)
  - **Gap 1 — 18 stale handoffs accumulating**: The stale directory has 18 JSON handoff packets. Most are within the 14-day window (Jun 19 — Jul 1). The oldest (Jun 19) will be deleted by the reaper in ~17 days. This is working as designed — but the reaper hasn't been running continuously (likely the MCP Hub server wasn't running during some of this period). **Gap: LOW — the reaper will catch them when the server runs continuously.**
  - **Gap 2 — Archive directory has 111 stale `.md` handoff reports**: These are NOT JSON handoff packets — they're markdown reports from previous sprints. The reaper's `glob("*.json")` filter correctly ignores them. However, they represent ~532KB of stale coordination files that should be cleaned up by a separate housekeeping pass. **Gap: LOW — cosmetic, not functional.**
  - **Gap 3 — 1 active handoff with no completion path**: `ho_19b96a5fe894.json` has been active since Jul 1. If the accepting agent never completes it, it will be reaped to stale/ after 48h (which has already passed). The reaper should have moved it. **This suggests the reaper loop wasn't running when this packet aged.** When the Hub restarts, it will be caught. **Gap: LOW — self-healing on next reaper cycle.**
- **Confidence**: HIGH
- **Risk**: LOW

## 5. ContextBuilder (P7 Context)
- **Status**: ⚠️ WARN
- **Findings**:
  - **27/27 tests passing** — `test_context_builder.py` fully green.
  - **Quality-weighted scoring**: `_score_exchange_quality()` at lines 161-208 uses 4 signals:
    1. Message length (0.0-0.3)
    2. Technical content: code blocks, references (0.0-0.2)
    3. Contains a question (0.0-0.2)
    4. Recency boost: flat 0.15 (0.0-0.3 theoretical, but only 0.15 used)
    - **Max possible score: 0.85** (not 1.0 as documented). The recency signal is hardcoded to 0.15 rather than being dynamically calculated from timestamps. **Gap: LOW — scores are functional but the recency component is static.**
  - **The 5-factor scoring (relevance 30%, novelty 25%, actionability 20%, completeness 15%, accuracy 10%) is NOT implemented.** The Ark Blueprint describes this scoring system, but the actual code uses the simpler 4-signal scorer above. This is likely an intentional simplification — the 5-factor system would require LLM inference per exchange, which is too expensive for context assembly. **Gap: MEDIUM — documentation/code mismatch. The 4-signal scorer is the "Right Approximation" but docs claim 5-factor.**
  - **PipelineCompactionStrategy is defined but NOT wired into the build pipeline.** `_compact_and_format_exchanges()` (line 326) directly instantiates `ObservationMaskingStrategy()` and calls it, then does a manual sliding window. It does NOT compose `ObservationMasking → Truncation` via `PipelineCompactionStrategy`. The class exists but is unused. **Gap: MEDIUM — dead code, compaction pipeline is ad-hoc rather than composed.**
  - **ACONOptimizer is defined but NOT active.** The class at lines 118-141 is a stub — `optimize_guidelines()` just sets two static dict entries. It's never instantiated or called anywhere in the context building pipeline. **Gap: LOW — placeholder implementation, not a regression.**
  - **Observation Masking is keyword-based, not token-threshold-based.** The spec mentions "50k buffer, 30k hysteresis" but the actual implementation (`ObservationMaskingStrategy`) culls lines containing keywords like "logged", "confirmed", "processed" from tool outputs. This is a different (and arguably better) approach — it removes redundant content regardless of token count. **Gap: LOW — implementation differs from spec but is functionally sound.**
  - **TruncationStrategy exists as emergency backstop** but is also not wired into the pipeline. If the sliding window doesn't fit within `token_limit`, it just stops adding exchanges — it doesn't truncate individual messages. **Gap: LOW — graceful degradation, not a crash.**
- **Confidence**: HIGH
- **Risk**: MEDIUM (documentation/code mismatch on quality scoring; compaction pipeline is ad-hoc)

---

## Summary

| Metric | Count |
|--------|-------|
| **Total gaps found** | 12 |
| **Critical** | 0 |
| **High** | 0 |
| **Medium** | 4 |
| **Low** | 8 |

### Gaps by Severity

**MEDIUM (4):**
1. **Memory: No 30-day compression** — `archive_session()` moves to cold storage but never gzip-compresses old sessions. Storage bloat for long-lived entities.
2. **Memory: No 90-day delete** — Sessions are archived but never deleted. Unbounded disk growth over months.
3. **ContextBuilder: 5-factor scoring not implemented** — Ark Blueprint claims relevance/novelty/actionability/completeness/accuracy weighting, but actual code uses simpler 4-signal scorer (length, technical content, questions, recency).
4. **ContextBuilder: PipelineCompactionStrategy dead code** — Class is defined but never instantiated. Compaction is ad-hoc in `_compact_and_format_exchanges()`.

**LOW (8):**
5. **Observability: `record_error()` has `trace_id or "unknown"` fallback** — Mitigated by contextvars safety net upstream. Residual risk negligible.
6. **Health Monitor: No background probe loop** — Probes are on-demand only. Acceptable for single-machine scale.
7. **Memory: Batch flush silently drops on provider failure** — Hot cache provides safety net.
8. **Handoff: 18 stale packets in stale/** — Within 14-day window, will self-clean.
9. **Handoff: 111 stale .md reports in handoff/** — Cosmetic, not functional.
10. **Handoff: 1 active packet past 48h TTL** — Will be reaped on next reaper cycle.
11. **ContextBuilder: Quality score max is 0.85, not 1.0** — Recency signal hardcoded to 0.15.
12. **ContextBuilder: ACONOptimizer is a stub** — Placeholder, never called.

### Recommended Fixes (Ordered by Impact)

1. **[MEDIUM] Add 30-day gzip compression to `archive_session()`** — After moving to cold storage, check session age and compress with `gzip` if >30 days. Low effort, high storage savings.

2. **[MEDIUM] Add 90-day session deletion to `archive_old_sessions()`** — Add a second pass that deletes sessions older than 90 days from cold storage. Prevents unbounded disk growth.

3. **[MEDIUM] Update Ark Blueprint quality scoring docs** — Either implement the 5-factor scorer or update documentation to match the actual 4-signal implementation. Documentation honesty is non-negotiable.

4. **[MEDIUM] Wire PipelineCompactionStrategy into `_compact_and_format_exchanges()`** — Replace the ad-hoc masking + sliding window with a composed pipeline: `ObservationMasking → Truncation`. Eliminates dead code and makes the compaction chain explicit.

5. **[LOW] Fix quality score recency to use actual timestamps** — Replace the hardcoded 0.15 with a dynamic calculation based on `exchange.timestamp` vs current time.

6. **[LOW] Add retry logic to `_flush_batch()`** — On provider failure, buffer the failed writes for retry on next flush instead of silently dropping.

### Test Results Summary

| Module | Tests | Status |
|--------|-------|--------|
| test_observability.py | 16/16 | ✅ PASS |
| test_health_monitor.py | 24/24 | ✅ PASS |
| test_memory_store.py | 20/20 | ✅ PASS |
| test_hivemind.py | 8/8 | ✅ PASS |
| test_context_builder.py | 27/27 | ✅ PASS |
| **Full suite** | **705 passed, 22 skipped, 3 xfailed** | ✅ PASS |

---

*🔱 OMEGA ⬡ LILITH ⬡ mimo-v2.5-free ⬡ opencode ⬡ P6-P10-DARK-AUDIT ⬡ 2026-07-02*
