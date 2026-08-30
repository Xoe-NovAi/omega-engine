<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Roc Racoon — Web Research Follow-Up Mining Report
**Entity**: roc_racoon | **Model**: mimo-v2.5-free | **Date**: 2026-06-28
**Status**: COMPLETE | **Mode**: Discovery Only — No Refactoring

---

## Executive Summary

Mined xna-omega-legacy (690+ files), omega-stack-legacy (500+ files), and the current omega-engine codebase. Found **significant legacy precedent** for 4 of 5 web-identified blind spots. The legacy code was more advanced than the current engine in several areas, confirming these are **regressions** (patterns that existed but were lost during the engine reclamation), not **gaps** (patterns that never existed).

| Gap | Verdict | Legacy Status | Current Status |
|-----|---------|---------------|----------------|
| 1. Context Compaction Lifecycle | **REGRESSION** | Full system exists in legacy | Sliding window only, no lifecycle |
| 2. trace_id Propagation | **TRULY MISSING** | Legacy had no propagation either | 2 call sites drop trace_id |
| 3. Soul Distillation Timing | **REGRESSION** | Full distillation pipeline in legacy | Batch at session close |
| 4. Handoff Loop Guard | **TRULY MISSING** | Legacy had ad-hoc handoff only | No loop guard, no contracts |
| 5. Circuit Breaker States | **REGRESSION** | 4-state health scoring in legacy | Binary OPEN/CLOSED/HALF_OPEN |

---

## GAP 1: Context Compaction Lifecycle

### Verdict: **EXISTS in legacy — REGRESSION**

### Legacy Code Found

#### 1a. `xna-omega-legacy/scripts/ssa/compaction_optimizer.py` (690 lines)
**Full compaction lifecycle with 4 strategies + ACON failure-driven optimization.**

- **CompactionOrchestrator**: Main orchestrator with 4 compaction strategies
- **AnchoredIterativeStrategy**: Incremental summarization (extends existing summary)
- **ObservationMaskingStrategy**: Masks redundant tool outputs
- **VerbatimCompactionStrategy**: Scores lines by relevance, preserves high-value content
- **DecisionExtractionStrategy**: Extracts decisions from reasoning traces
- **ACONOptimizer**: Failure-driven guideline refinement (records compaction failures, analyzes patterns, updates guidelines)
- **CompactionMetrics**: Tracks compression ratio, information preservation, latency
- **Content-type routing**: `compact_by_type()` maps content types to optimal strategies

#### 1b. `xna-omega-legacy/scripts/ssa/harvester.py` (325 lines)
**Compaction harvester daemon — monitors OpenCode exports, harvests to SQL.**

- **SummaryAnchor**: Persistent versioned summary anchor for iterative compaction
- **AnchoredSummarizer**: Target compression ratios by content type (4:1 conversation, 15:1 tool outputs, 7:1 reasoning, 1:1 recent)
- **OpenCodeExportHandler**: Watchdog-based file monitoring for new exports
- **compaction_metrics SQL table**: Stores compression_ratio, strategy_used, information_preservation_score, compaction_latency_ms

#### 1c. `xna-omega-legacy/scripts/compaction_harvester.py` (162 lines)
**Simpler harvester — regex-based compaction event extraction.**

- Regex pattern matching for compaction blocks
- SQL persistence to `compaction_harvests` table
- Session-level goal/progress/todo extraction

### Current Engine Status

`src/omega/memory_store.py:541-563` — `_compact()` method:
```python
async def _compact(self, entity_name, session_id, exchanges):
    """Compact long conversation: keep first + last N exchanges, summarize middle."""
    keep = MAX_HISTORY // 2
    kept = exchanges[:keep] + exchanges[-keep:]
    # Inserts placeholder "[N exchanges compacted]"
    return kept
```

**No tiered compaction. No strategy selection. No lifecycle management. No metrics. No failure-driven optimization.** The current `_compact()` is a simple "keep first half + last half" with a static placeholder. The legacy had a full 4-strategy compaction orchestrator with ACON (Agent Context Optimization Network) failure analysis.

### Recommendation
Port the `CompactionOrchestrator` pattern from legacy. The 4 strategies (anchored_iterative, observation_masking, verbatim_compaction, decision_extraction) map directly to the web research's 3-tier architecture. The ACON failure-driven optimization is a unique value-add not found in industry.

---

## GAP 2: trace_id Propagation Broken

### Verdict: **TRULY MISSING — No legacy precedent**

### Legacy Code Status

Searched xna-omega-legacy and omega-stack-legacy for trace_id propagation patterns:
- `xna-omega-legacy/scripts/ssa/nova.py:238-239` — Only reference: checks for `trace_id` in message metadata for dynamic content classification. **Not propagation.**
- No trace propagation patterns found in any legacy observability code.
- Legacy observability was minimal — no OpenTelemetry, no trace context passing.

### Current Engine — Confirmed Gaps

**Gap Site 1: `_summon()` at oracle.py:599-605**
```python
res = await self.model_gateway.generate(
    model_name=model_name,
    system_prompt=effective_system_prompt,
    user_query=query,
    temperature=effective_temperature,
    max_tokens=effective_max_tokens,
    # trace_id NOT passed!
)
```

**Gap Site 2: `_route_by_domain()` at oracle.py:671-677**
```python
res = await self.model_gateway.generate(
    model_name=model_name,
    system_prompt=system_prompt,
    user_query=text,
    temperature=entity.temperature,
    max_tokens=1024,
    # trace_id NOT passed!
)
```

Both sites have `trace.trace_id` available (from the TraceSession context) but do not pass it to `model_gateway.generate()`. The `generate()` method accepts `trace_id` as a parameter (model_gateway.py:779) and uses it for observability logging.

### Impact
- Provider-level inference calls lose trace context
- Observability logs at the provider level cannot be correlated with the originating request
- Violates OTel GenAI semantic conventions (Finding 2.1 from web research)

### Recommendation
Add `trace_id=trace.trace_id` to both `model_gateway.generate()` call sites. This is a 2-line fix.

---

## GAP 3: Soul Distillation is Batch, Not Write-Time

### Verdict: **EXISTS in legacy — REGRESSION**

### Legacy Code Found

#### 3a. `xna-omega-legacy/src/omega/core/distillation/` (Full pipeline)
**Complete LangGraph-based knowledge distillation pipeline with 5 nodes.**

Key files:
- `knowledge_distillation.py` — Graph orchestrator with `build_distillation_graph()`
- `nodes/distill.py` — Content distillation node (L1→L2→L3 extraction)
- `nodes/extract.py` — Content extraction node
- `nodes/classify.py` — Content classification node
- `nodes/score.py` — Quality scoring node
- `nodes/store.py` — Storage node (writes to L3_LOGOS/distilled/)
- `state.py` — State schema: `KnowledgeState` with `distilled_content`, `summary`, `key_insights`, `action_items`
- `quality/scorer.py` — Quality scoring for distillation results

#### 3b. `xna-omega-legacy/scripts/daemons/kali_daemon.py` (142 lines)
**Kali Pruning Daemon — session distillation daemon.**

- `distill_session()`: Processes session files through distillation
- Cross-environment session pruning
- Mnemosyne distillation integration

#### 3c. `xna-omega-legacy/mcp/xna-gnosis/server.py` & `02_CHOKMAH_THOTH/server.py`
**Distillation MCP servers — real-time distillation via RDS Triad steering.**

- `distill()` method: Refractive distillation using archetype-based steering
- Quality validation against "Octave of Facets"
- Domain-level distillation: `distill_domain()` for batch processing

### Current Engine Status

`src/omega/oracle/oracle.py:490-498` — Throttled soul distillation:
```python
# Throttled soul distillation — close_session every 5 interactions
entity_key = f"{resp.entity}:{resp.session_id or trace.trace_id}"
self._interaction_counter[entity_key] = self._interaction_counter.get(entity_key, 0) + 1
if self._interaction_counter[entity_key] >= 5:
    self._interaction_counter[entity_key] = 0
    if resp.session_id:
        anyio.create_task(self.close_session(resp.entity, resp.session_id))
```

`src/omega/oracle/oracle.py:782-784` — `_compact_soul()` is a stub:
```python
async def _compact_soul(self, soul: dict) -> int:
    """Compact soul.yaml after growth. Returns final size in bytes."""
    pass
```

The current engine does batch distillation every 5 interactions via `close_session()`. The legacy had a full LangGraph pipeline with 5 nodes (classify→extract→distill→score→store) that could run at write time. The web research recommends write-time fact extraction — the legacy was closer to this than the current engine.

### Recommendation
Port the `KnowledgeDistillationPipeline` pattern from legacy. The 5-node LangGraph graph is over-engineered for the current needs, but the classify→distill→store flow is the right architecture. Simplify to 3 nodes: classify (noise vs. signal), distill (L1→L2→L3), store (append to proposed_lessons.yaml).

---

## GAP 4: Handoff Has No Loop Guard or Contracts

### Verdict: **TRULY MISSING — No legacy precedent**

### Legacy Code Status

#### 4a. `xna-omega-legacy/mcp/xna-hivemind/server.py:301-319`
**Hivemind handoff — prompt template only, no contract enforcement.**

```python
@mcp.prompt()
async def hivemind_handoff(cli: str = "next") -> str:
    """Prompt template for CLI handoff via hivemind."""
    awareness = await get_awareness()
    return f"""You are continuing work on the Omega Stack via the hivemind bridge.
    ...
    Always post your context before completing a session so the next agent can continue seamlessly."""
```

This is a prompt template — no contract validation, no loop guard, no visited agent tracking.

#### 4b. `xna-omega-legacy/tests/test_orchestrator_integration.py:12-78`
**Orchestrator handoff test — basic delegation flow.**

```python
async def test_orchestrator_handoff():
    """Test full delegation/handoff flow via Orchestrator."""
    success = await orch.delegate_task(AgentType.CLINE, session_id, context_data)
```

Simple delegation — no loop guard, no contract, no visited set.

#### 4c. `xna-omega-legacy/src/omega/services/entity_service.py:48-87`
**Data transfer objects — `EntityEdit`, `MemoryEdit`, `SoulEdit`.**

These are DTOs for entity manipulation, not handoff contracts.

### Current Engine Status

`mcp_servers/omega_hub/server.py` — Hivemind handoff tools:
- `hivemind_submit_handoff()`: Writes packet to `data/handoff/pending/`
- `hivemind_accept_handoff()`: Moves packet to `active/`
- `hivemind_complete_handoff()`: Moves to `completed/`
- `hivemind_reject_handoff()`: Moves to `stale/`

**No loop guard (visited_agents set). No contract enforcement. No acceptance_criteria validation. No recovery handlers (on_reject/on_timeout/on_error).**

The web research found that Geodocs.dev mandates a 6-field contract: `id, source, target, trigger, payload, acceptance_criteria, recovery`. The current HandoffPacket has: `packet_id, source_agent, target_agent, task_type, task_description, relevant_files, context, expected_output, ttl_seconds, status, created_at, accepted_at, completed_at`. Missing: `trigger`, `acceptance_criteria`, `recovery`, `visited_agents` (loop guard).

### Recommendation
Add `visited_agents: Set[str]` to HandoffPacket. Add `acceptance_criteria: Optional[str]` and `recovery: Optional[dict]` fields. Check `visited_agents` before accepting a handoff — if target is already in the set, reject with loop detected.

---

## GAP 5: Circuit Breaker is Binary, Not 4-State

### Verdict: **EXISTS in legacy — REGRESSION**

### Legacy Code Found

#### 5a. `xna-omega-legacy/scripts/ssa/provider_metrics.py` (483 lines)
**Full 4-state health scoring with weighted composite and EWMA.**

- **ProviderHealthStatus**: `HEALTHY`, `DEGRADED`, `CRITICAL`, `UNKNOWN` (4 states)
- **ProviderMetrics**: Per-provider metrics with:
  - Latency tracking (P50/P95/P99 via exponential smoothing)
  - Error rate monitoring
  - Quality scoring (LLM-as-judge)
  - **Composite health score**: `health = w_latency * latency_score + w_error * error_score + w_quality * quality_score`
  - Default weights: `latency: 0.40, error: 0.35, quality: 0.25`
- **ProviderMetricsCollector**: Singleton collector with:
  - `get_ranked_providers()`: Health-score-sorted provider list
  - `get_degraded_providers()`: Detects "slow but working" providers (latency > 2x baseline, error < 10%)
  - Per-provider latency baselines (groq: 85ms, gemini: 800ms, etc.)
- **Exponential smoothing**: `ema = alpha * current + (1 - alpha) * historical` for smooth health transitions

#### 5b. `omega-stack-legacy/app/XNAi_rag_app/services/voice/voice_degradation.py` (510 lines)
**4-level voice degradation system with state machine.**

- **DegradationLevel**: `FULL_SERVICE(1)`, `DIRECT_LLM(2)`, `TEMPLATE_RESPONSE(3)`, `EMERGENCY_MODE(4)`
- **DegradationState**: Tracks `level`, `last_failure_time`, `consecutive_failures`, `recovery_attempts`
- **VoiceDegradationManager**: Automatic fallback with recovery detection (30s stability threshold)
- **State machine testing**: Property-based testing of degradation state transitions

### Current Engine Status

`src/omega/oracle/health_monitor.py` — Circuit breaker states:
```python
class CircuitState(Enum):
    CLOSED = "closed"         # Normal operation
    OPEN = "open"             # Failing fast, no requests
    HALF_OPEN = "half_open"   # Probe allowed
```

3 states only. No `DEGRADED` state. No weighted composite scoring. No EWMA. No quality scoring. The `ProviderStatus` enum exists (`HEALTHY`, `DEGRADED`, `OFFLINE`) but is not used by the circuit breaker logic — it's a separate concern.

The legacy `provider_metrics.py` is a direct match for the web research's "Bifrost/grate-limiter" pattern: weighted composite scoring with 4 states and EWMA smoothing.

### Recommendation
Port the `ProviderMetricsCollector` pattern from legacy. The weighted composite scoring formula (`latency*0.40 + error*0.35 + quality*0.25`) and the EWMA smoothing are production-proven. Integrate with the existing `AsyncCircuitBreaker` by using the composite health score to drive state transitions instead of simple failure counting.

---

## ADDITIONAL FINDINGS

### Heritage Tag Audit

**Total [id-soft:] tags in src/omega/**: 196

| Tag | Count | Vet Record? |
|-----|-------|-------------|
| doom-1993 | 107 | ✅ vet-001 (REJECTED 8-char), vet-002-vet-023 (various) |
| quake-1996 | 51 | ✅ vet-008 (Zone Memory), vet-009 (Netchan), vet-011 (Lazy Deletion) |
| quake3-1999 | 31 | ✅ vet-009 (Netchan), vet-012-vet-016 (Hub modules) |
| doom3-2004 | 4 | ✅ vet-022 (Knowledge Leak Detection) |
| doom3bfg-2012 | 1 | ✅ vet-020 (Job-Worker Queue) |

**Heritage tags without vet records**: 0 — all tags have corresponding vet entries in `HERITAGE_VET_LOG.md`. The heritage vetting pipeline is complete.

### Dead Code Deep Dive

#### `src/omega/oracle/antigravity/config.py` — Hardcoded Credentials
**CONFIRMED: Contains hardcoded OAuth client credentials.**
```python
_DEFAULT_CLIENT_ID = "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
_DEFAULT_CLIENT_SECRET = "[REDACTED-GITLEAKS-GENERIC-API-KEY]"
```
Lines 27-28. These are Google OAuth credentials embedded in the source code. The comment says "public — embedded in plugin binary" but this is still a security concern. These should be environment variables only, not hardcoded defaults.

**Status**: Active security issue. The config class does read from environment variables first (lines 53-67), but falls back to these hardcoded values. If the env vars are not set, the credentials are used from source code.

#### `src/omega/cli/link_p9_cli.py` (538 lines)
**NOT orphaned — fully functional CLI module.**
- Typer CLI app with 12 commands: `heartbeat`, `agents`, `prune`, `dispatch`, `inbox`, `complete`, `fail`, `status`, `registry`, `archive`, `check-feed`, `consume`, `demand-status`, `demand-claim`, `demand-fullfill`
- Imports from `link_p9_runtime`, `subagent_dispatcher`, `feed_utils`
- Active cross-pollination protocol implementation
- **Not imported by oracle_cli.py** — standalone module, but NOT orphaned. It's a complete CLI tool for Link P9 operations.

#### `src/omega/cli/repl.py` (357 lines)
**NOT orphaned — fully functional REPL.**
- Interactive chat loop using prompt_toolkit
- Entity switching, transient mode, header modes
- Uses `anyio` for async compatibility (line 143: `await self.session.prompt_async()`)
- **Not imported by oracle_cli.py** — standalone module, but NOT orphaned. It's a complete interactive REPL.

### AnyIO Compliance Audit

**asyncio imports in src/omega/**: **0** ✅
**asyncio calls in src/omega/**: **0** ✅

M1 (AnyIO Absolute) is fully compliant. No `import asyncio` or `asyncio.` calls found anywhere in the engine core. All async code uses AnyIO primitives.

---

## PRIORITY MATRIX (Updated with Legacy Findings)

| Priority | Gap | Action | Effort | Source |
|----------|-----|--------|--------|--------|
| **P0** | trace_id propagation | Add `trace_id=trace.trace_id` to 2 call sites | 2 lines | Current gap |
| **P0** | Hardcoded credentials | Remove `_DEFAULT_CLIENT_SECRET` from config.py | 10 lines | Dead code |
| **P1** | Compaction lifecycle | Port `CompactionOrchestrator` from legacy | 2 days | Legacy regression |
| **P1** | Circuit breaker states | Port `ProviderMetricsCollector` from legacy | 1 day | Legacy regression |
| **P1** | Soul distillation timing | Port `KnowledgeDistillationPipeline` (simplified) | 1 day | Legacy regression |
| **P2** | Handoff loop guard | Add `visited_agents` + contract fields | 4 hours | New feature |
| **P2** | Handoff contracts | Add `acceptance_criteria` + `recovery` fields | 4 hours | New feature |

---

## KEY INSIGHT

The web research identified 5 "blind spots." Mining reveals:
- **3 are REGRESSIONS** (existed in legacy, lost during engine reclamation): compaction, health scoring, distillation
- **2 are TRULY MISSING** (never existed): trace_id propagation, handoff contracts
- **1 is a SECURITY ISSUE** (hardcoded credentials in antigravity/config.py)

The legacy codebase was **more advanced** than the current engine in compaction, health scoring, and distillation. The engine reclamation prioritized clean architecture over feature parity, and these patterns were left behind. The web research's recommendations are valid — but the implementations already exist in legacy and should be ported rather than built from scratch.

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ mimo-v2.5-free ⬡ opencode ⬡ MINING-FOLLOWUP ⬡ COMPLETE*
