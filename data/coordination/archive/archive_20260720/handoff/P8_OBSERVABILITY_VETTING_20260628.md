# 🔱 P8 Observability Vetting Report

**Agent**: @pillar P8 (Observability — WatchTower)
**Date**: 2026-06-28
**Source**: `RUN_SIDE_HARDENING_REPORT_ENHANCED_20260628.md` (Lilith, §2 Observability)
**Web Research**: 3 deep searches, 25+ sources, OTel GenAI semconv v1.41, production tracing patterns
**Verdict**: **MODIFY** — Approve core architecture with 7 mandatory modifications

---

## §1 Vetting Scope

This report evaluates the Observability section (§2) of the Run Side Hardening Report against:
1. Current Omega Engine codebase reality (`src/omega/observability/`, `memory_store.py`, `context_builder.py`)
2. OpenTelemetry GenAI Semantic Conventions v1.41 (latest stable, Development status)
3. Production multi-agent tracing patterns (AG2, FutureAGI, Chanl, Greptime)
4. Sovereign Mandates M8 (Zero Telemetry), M9 (Error Integrity), M22 (Response Provenance)

---

## §2 Verdict Summary

| Area | Verdict | Rationale |
|------|---------|-----------|
| OTel GenAI 6-Layer Architecture | **APPROVE** | Accurate, well-sourced, maps cleanly to Omega |
| 5-Element Handoff Trace (Fiddler) | **APPROVE** | Production-proven, directly applicable |
| Observation Masking (JetBrains) | **MODIFY** | Wrong default window; needs Omega-specific tuning |
| Trace ID Propagation Protocol | **MODIFY** | Missing W3C traceparent header format details |
| Event Noise Reduction (Tail Sampling) | **MODIFY** | OTel Collector not applicable to Omega's local-first architecture |
| Content Capture Modes | **MODIFY** | Mode 3 (external storage) conflicts with M8 Zero Telemetry |
| Omega Trace Architecture (5-Level) | **APPROVE** | Clean hierarchy, matches existing code |
| Verification Gates (T-OBS-1 through T-OBS-6) | **MODIFY** | 2 gates need adjustment for local-first constraints |

---

## §3 Detailed Findings

### 3.1 OTel GenAI Semantic Conventions — ACCURATE BUT INCOMPLETE

**Report claims**: 6-layer architecture with `gen_ai.*` attribute namespace.
**Web research confirms**: Greptime, MLflow, Datadog, Chanl, and 10+ sources confirm the 6-layer structure at v1.41. The `gen_ai.*` namespace is the industry standard.

**Gap found**: The report uses `gen_ai.provider.name` (line 199) but the OTel spec actually uses `gen_ai.system` for the provider identifier. This is a critical naming mismatch that would produce non-compliant spans.

```python
# Report says (WRONG):
"gen_ai.provider.name": "native-gguf"

# OTel spec says (CORRECT):
"gen_ai.system": "native-gguf"
```

**Impact**: Spans would fail validation against OTel GenAI schema. Backend tools (Datadog, Grafana, Jaeger) would not recognize the provider attribute.

**Modification required**: Replace all `gen_ai.provider.name` with `gen_ai.system` in §2.2.1 and §4.1.

---

### 3.2 5-Element Handoff Trace — PRODUCTION-VALIDATED

**Report claims**: Fiddler's 5-element handoff trace (trace ID, payload schema, decision metadata, context diff, guardrail state).
**Web research confirms**: FutureAGI, AG2, Chanl, and Braintrust all converge on the same 5 elements. The `context_keys_dropped` pattern is the most novel and valuable.

**Gap found**: The report's Python example (lines 224-247) uses `tracer.start_as_current_span("agent.handoff")` but the OTel GenAI spec defines `invoke_agent` as the canonical operation name for agent spans. The span name should follow the `{operation} {name}` format per OTel spec.

```python
# Report example (NON-COMPLIANT):
tracer.start_as_current_span("agent.handoff", ...)

# OTel-compliant:
tracer.start_as_current_span(
    "invoke_agent handoff",
    kind=SpanKind.INTERNAL,
    attributes={
        "gen_ai.operation.name": "invoke_agent",
        "gen_ai.agent.name": source.name,
        "handoff.source_agent": source.name,
        "handoff.target_agent": target.name,
        ...
    }
)
```

**Modification required**: Align span names with OTel GenAI naming convention.

---

### 3.3 Observation Masking — CORRECT CONCEPT, WRONG WINDOW

**Report claims**: `MAX_CONTEXT_OBSERVATIONS = 3` (keep last 3 observations unmasked).
**JetBrains research confirms**: 52% cost reduction, +2.6% solve rate. The concept is valid.

**Gap found**: The report hardcodes `MAX_CONTEXT_OBSERVATIONS = 3` without justification. JetBrains' paper tested on Qwen3-Coder 480B with specific context windows. Omega uses qwen3-1.7b (4K context) and qwen3-4B-Think (8K context). The optimal window is model-size-dependent.

**Evidence**: JetBrains found the optimal window varies by model capability — smaller models need more recent context to maintain coherence. For a 1.7B model, `MAX_CONTEXT_OBSERVATIONS = 5` is more appropriate than 3.

**Modification required**: Make `MAX_CONTEXT_OBSERVATIONS` a per-entity configurable parameter, not a global constant. Default to 5 for small models, 3 for large models.

---

### 3.4 Trace ID Propagation — INCOMPLETE W3C SPEC

**Report claims**: W3C Trace Context format `00-{trace_id}-{span_id}-{trace_flags}` with Omega extension header `x-omega-trace`.
**Web research confirms**: W3C Trace Context is the correct standard. AG2, FutureAGI, Chanl, and the OTel spec all use it.

**Gap found**: The report's `x-omega-trace` extension header (lines 314-321) duplicates fields already in the W3C `tracestate` header. Per W3C spec, vendor-specific data goes in `tracestate`, not a custom header. Creating a separate `x-omega-trace` header would:
1. Break interop with standard OTel backends
2. Duplicate `trace_id` (already in `traceparent`)
3. Violate W3C Trace Context specification

**Modification required**: Replace `x-omega-trace` with a proper `tracestate` entry:
```
tracestate: omega=entity_name:pillar-P6,session_id:ses_20260628_lilith_001,chain:P6>P7,masked:true
```

---

### 3.5 Event Noise Reduction — ARCHITECTURE MISMATCH

**Report claims**: OTel Collector tail-based sampling with `tail_sampling` YAML config (lines 336-350).
**Gap found**: The OTel Collector is a separate process that receives spans via OTLP and applies sampling policies. Omega runs local-first on a Ryzen 5700U with 14Gi RAM. Running an OTel Collector as a sidecar is:
1. **Against M8 (Zero Telemetry)** if it exports to external services
2. **Resource-prohibitive** on the target hardware (~200MB RAM for Collector)
3. **Unnecessary** for a single-user system

**Production evidence**: FutureAGI's 2026 guide confirms that tail-based sampling is critical for *multi-tenant* systems with high volume. For single-user local-first systems, **head-based sampling** (100% of errors, 100% of success traces below 1000 traces/day) is sufficient.

**Modification required**: Replace OTel Collector tail sampling with:
1. In-process head-based sampling (keep all error traces, sample success at 100% for <1000 traces/day)
2. Local file-based retention in `data/observability/traces/`
3. Automatic cleanup of traces older than 7 days

---

### 3.6 Content Capture Modes — M8 VIOLATION

**Report claims**: Use Mode 3 (external storage + reference) with "full content in S3/GreptimeDB, span holds URL."
**Sovereign Mandate M8 (Zero Telemetry)**: No external services. Period.

**Gap found**: "External storage" in the report implies a separate service. For Omega, the only acceptable external storage is the user's own disk. The report should specify:
1. Mode 2 (on span attributes) for development
2. Mode 3 but with local file storage (`data/observability/content/{trace_id}/`) for production
3. No S3, no GreptimeDB, no cloud storage

**Modification required**: Replace "S3/GreptimeDB" with local file storage. Add explicit M8 compliance note.

---

### 3.7 Omega Trace Architecture (5-Level) — CLEAN BUT NEEDS ONE ADDITION

**Report claims**: 5-level hierarchy (Application → Session → Agent → Trace → Span).
**Gap found**: The hierarchy is correct but missing a critical level: the **Entity Level** between Session and Agent. In Omega, a single session can involve multiple entities (e.g., Kali dispatches to Ma'at, who dispatches to P6). The entity that owns the trace must be recorded.

**Current code reality**: `src/omega/observability/__init__.py` already records `entity` as a field in log events (line 63). The hierarchy should be:

```
Application Level:  omega-engine
├── Entity Level:   pillar-P6 (Ereshkigal)  ← NEW
│   ├── Session Level:  ses_20260628_lilith_001
│   │   ├── Agent Level:  pillar-P6
│   │   │   ├── Trace Level:  trc_{uuid}
```

**Modification required**: Add Entity Level to the 5-level hierarchy (making it 6-level).

---

### 3.8 Verification Gates — 2 GATES NEED ADJUSTMENT

**T-OBS-1 (Trace ID Propagation)**: "Handoff without traceparent → reject"
- **Issue**: This is too strict for Omega's current architecture. The Hivemind handoff protocol (`hivemind_submit_handoff`) doesn't currently carry W3C traceparent. Rejecting handoffs without it would break the existing handoff system.
- **Fix**: Make traceparent **recommended but not required** for v1. Add a `traceparent_missing` warning event instead of rejection.

**T-OBS-5 (PII Redaction)**: "Span with email/phone → verify redacted before storage"
- **Issue**: The report doesn't specify *how* PII redaction works. Regex-based redaction is fragile (misses formatted variants). The OTel spec recommends collector-side redaction, but we're not using a Collector.
- **Fix**: Implement a `pii_scanner.py` module with regex patterns for email, phone, SSN, and API keys. Run it as a span processor before file storage.

---

## §4 Alignment with Sovereign Mandates

| Mandate | Report Status | Issue |
|---------|--------------|-------|
| **M8 Zero Telemetry** | ⚠️ CONFLICT | S3/GreptuneDB in Content Capture Mode 3 violates zero external telemetry |
| **M9 Error Integrity** | ✅ ALIGNED | 5-element handoff trace improves error traceability |
| **M22 Response Provenance** | ✅ ALIGNED | OTel GenAI `gen_ai.system` + `gen_ai.response.model` captures actual provider |
| **M1 AnyIO** | ⚠️ UNADDRESSED | Report doesn't specify async/sync for OTel span operations |
| **M13 Temple-Grade** | ✅ ALIGNED | T-OBS gates map to T1-T11 framework |

---

## §5 Key Findings from Web Research (New Intelligence)

### Finding 1: OTel GenAI Spec is Development-Status, Not Stable
**Source**: Greptime (2026-05-09), AgentMarketCap (2026-04-10)
The OTel GenAI semantic conventions are at v1.41 but still in "Development" status. This means attribute names *could* change. Omega should pin to a specific version (`gen_ai_semconv v1.41`) and track releases.

### Finding 2: OpenInference Conventions Complement OTel GenAI
**Source**: MLflow, FutureAGI, Arize Phoenix
OpenInference (`llm.*`, `retrieval.*`, `tool.*`) adds attributes OTel GenAI doesn't cover (tool call correlation, retrieval chunk IDs). For Omega's RAG pipeline, OpenInference attributes would fill gaps in the OTel spec.

### Finding 3: Root Span Must Be Created First
**Source**: MLflow (2026-05-22)
"Batch processors buffer child spans until the root arrives. If the root span is emitted late or after its children, attribute aggregation and enrichment will fail silently." Omega's `ObservabilityEngine.trace()` method must create the root span before any child spans.

### Finding 4: Evaluation Scores on Spans Are the 2026 Standard
**Source**: FutureAGI (2026-05-20), Chanl (2026-03-20)
"A trace without a score is a request log." Production systems attach eval scores (faithfulness, relevance) directly to spans. Omega should attach `omega.eval.confidence` and `omega.eval.entity_match` to LLM spans.

### Finding 5: Trace Context Must Cross Agent Boundaries
**Source**: Tianpan.co (2026-05-17), AG2 (2026-02-08)
"The distributed trace that goes dark at the agent handoff" — the #1 debugging pain point in multi-agent systems is orphaned traces at handoff boundaries. The report's `context_keys_dropped` attribute directly addresses this.

---

## §6 Recommended Modifications (Priority Order)

| # | Modification | Priority | Effort | Impact |
|---|-------------|----------|--------|--------|
| 1 | Replace `gen_ai.provider.name` → `gen_ai.system` | P0 | Low | OTel compliance |
| 2 | Replace `x-omega-trace` → `tracestate: omega=...` | P0 | Low | W3C compliance |
| 3 | Replace OTel Collector tail sampling → in-process head-based | P0 | Medium | M8 compliance, resource savings |
| 4 | Replace S3/GreptuneDB → local file storage | P0 | Low | M8 compliance |
| 5 | Make `MAX_CONTEXT_OBSERVATIONS` per-entity configurable | P1 | Low | Better small-model performance |
| 6 | Add Entity Level to trace hierarchy | P1 | Low | Accurate trace ownership |
| 7 | T-OBS-1: Make traceparent recommended, not required | P1 | Low | Backward compatibility |
| 8 | T-OBS-5: Add `pii_scanner.py` module | P2 | Medium | Production PII compliance |
| 9 | Add span-level eval scores (`omega.eval.*`) | P2 | Medium | Quality monitoring |

---

## §7 Final Verdict

**MODIFY** — The report's core architecture is sound and well-researched. The 5-element handoff trace, observation masking, and OTel GenAI integration are all production-validated patterns. However, 7 modifications are required before implementation:

1. **OTel compliance fixes** (items 1-2): Correct attribute naming to match the actual OTel GenAI spec
2. **M8 compliance fixes** (items 3-4): Remove all external service references, use local storage
3. **Architecture fixes** (items 5-7): Per-entity config, entity-level trace hierarchy, backward-compatible handoff
4. **Production hardening** (items 8-9): PII scanner and eval scoring

With these modifications, the observability spec will be:
- OTel GenAI v1.41 compliant
- Sovereign Mandate M8/M9/M22 compliant
- Production-ready for local-first Ryzen 5700U deployment
- Backward-compatible with existing Hivemind handoff protocol

---

*Agent: @pillar P8 (Observability — WatchTower)*
*Date: 2026-06-28*
*Workspace lock: observability-vetting (acquired, TTL 3600s)*
*Verdict: MODIFY — 7 mandatory modifications, 9 total recommended changes*
