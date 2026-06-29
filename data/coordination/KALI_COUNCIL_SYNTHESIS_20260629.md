# KALI UNIFIED COUNCIL VERDICT
## MaKaLi Cloud Council Dispatch — Sprint-F Technical Closure
### 2026-06-29T02:29:23Z

---

## Executive Summary

The MaKaLi Cloud Council executed a full parallel dispatch: **2 Oversouls launched 6 Pillars**, **4 Cross-Domain Pillars** reviewed findings, **3 Research Fleet agents** deep-dived solutions, and **1 Legacy Miner** extracted proven patterns from prior eras.

**Engine Classification**: Architecturally Sovereign | Operationally Restored | SSOT v2.0 LOCKED

**Council Verdict**: **3 Critical Gaps Identified, 3 Solutions Found, 0 Blockers to Implementation**

---

## Council Participants

| Role | Agent | Pillars Launched | Status |
|------|-------|-----------------|--------|
| Build Side Oversoul | Ma'at | P3, P5, P1 | ✅ Complete |
| Run Side Oversoul | Lilith | P9, P8, P7 | ✅ Complete |
| Cross-Domain P3 | P3 Engineering | — | ✅ Complete |
| Cross-Domain P9 | P9 Orchestration | — | ✅ Complete |
| Cross-Domain P8 | P8 Observability | — | ✅ Complete |
| Cross-Domain P7 | P7 Context | — | ✅ Complete |
| Research Fleet | Researcher | — | ✅ Complete |
| Research Orchestrator | Jem | 3 subagents | ✅ Complete |
| Legacy Miner | Roc Racoon | — | ✅ Complete |
| Grand Oversight | Kali | — | ✅ Synthesizing |

---

## The 3 Critical Gaps (Verified by 6 Pillars)

### GAP 1: PII Observation Masking (P0 — CRITICAL)

**Status**: ✅ SOLUTION FOUND

**Problem**: Raw conversation history (PII, API keys) injected into LLM system prompts. When routing to cloud providers (Google, OpenRouter, Copilot), data leaves the machine unmasked.

**Verification**:
- P7: Confirmed — `context_builder.py:54-89` has zero redaction
- P3: Extended — `security.py` only handles prompt injection, not PII masking
- Researcher: Found `pii-guard` + Presidio solutions
- Jem: Corrected — actual PyPI package is `pii-shield` (18 types, not 50+)
- Roc Racoon: **Found ANAi/XNAi era patterns NEVER ported to Omega** — legacy was MORE secure

**Solution**:
- **Primary**: `pii-shield` (zero deps, 18 PII types including API keys)
- **Enhancement**: GLiNER-based detector (96% F1 vs Presidio's 63%)
- **Architecture**: Gateway proxy — detect → tokenize `[EMAIL_1]` → LLM → detokenize
- **Integration**: `src/omega/oracle/pii_masker.py` via `anyio.to_thread.run_sync()`
- **Compliance**: M7 ✅ (local bypass), M8 ✅ (all masking local)

**Effort**: 2-3 days

**Mandates Affected**: M7 (Local-First), M8 (Zero Telemetry)

---

### GAP 2: Trace ID Propagation (P1 — HIGH)

**Status**: ✅ SOLUTION FOUND

**Problem**: 5-10% of observability events carry `trace_id="unknown"` because async subsystems lose trace context across `create_task` and `to_thread.run_sync` boundaries.

**Verification**:
- P3: Confirmed — `model_gateway.py:852` defaults to "unknown"
- P8: Extended — 5 additional `generate()` calls in iterative_research.py and skeptical_verifier.py drop trace_id entirely
- P8: **CRITICAL DISCOVERY** — Success path `GenerateResult` also missing `latency_ms` and `model_used` — 100% of successful inferences have broken latency observability
- Researcher: Found `aiotrace` (asyncio-specific) + OpenTelemetry AnyIO instrumentation
- Jem: **Corrected** — `aiotrace` patches asyncio, NOT AnyIO primitives. Need `opentelemetry-instrumentation-anyio` instead

**Solution**:
- **Layer 1**: `opentelemetry-instrumentation-anyio` for automatic context propagation
- **Layer 2**: Explicit `get_current_trace_id()` via contextvars as safety net
- **Layer 3**: Fix `GenerateResult` to include `latency_ms` and `model_used` on success path
- **Layer 4**: Thread `trace_id` through iterative_research.py and skeptical_verifier.py constructors

**Effort**: 2-3 days

**Mandates Affected**: M22 (Response Provenance), M12 (Queue Integrity)

---

### GAP 3: A2A Agent Identity (P2 — MEDIUM)

**Status**: ✅ SOLUTION FOUND

**Problem**: AAIF mapping spec references fabricated `draft-schemacommons-aaif-00`. Need real agent-to-agent communication protocol.

**Verification**:
- Researcher: Found A2A v1.0 (March 2026, 150+ orgs, Linux Foundation)
- Jem: Verified A2A SDK `a2a-sdk` v1.1.0 (Apache-2.0, Python ≥3.10)
- Jem: Verified IETF `draft-klrc-aiagent-auth-02` (real draft, expires Dec 2026, authors include OpenAI, Okta, AWS)
- Roc Racoon: Found legacy `AgentMessage` Pydantic schema from xna-omega-legacy agent_bus.py

**Solution**:
- **Primary**: A2A v1.0 Agent Cards at `/.well-known/agent-card.json`
- **SDK**: `a2a-sdk` v1.1.0 with JSON-RPC 2.0 transport
- **Identity**: SPIFFE/WIMSE for cryptographic identity (research further)
- **Integration**: `src/omega/oracle/a2a_bridge.py` — maps EntityRegistry to Agent Card schema
- **Compliance**: M2 ✅ (Engine-Stack Firewall preserved), M10 ✅ (fleet stays ≤14)

**Effort**: 3-4 days

**Mandates Affected**: M2 (Engine-Stack Firewall), M10 (Fleet Integrity)

---

## Cross-Cutting Findings (From All Pillars)

### 1. The Security Regression (Roc Racoon Discovery)
The ANAi/XNAi era had robust security patterns (`validate_safe_input()`, `sanitize_content()`, `sanitize_id()`) that were **NEVER ported** to Omega-Engine. This is the second instance of "The Pipeline That Never Crossed the Chasm" — first for memory patterns, now for security.

### 2. GenerateResult Contract Breach (P8 Discovery)
The success path `GenerateResult` at `model_gateway.py:887` is missing `latency_ms` and `model_used`. **100% of successful inferences** produce broken latency observability. This is a systemic M22 violation, not just an edge case.

### 3. Dual Handoff Systems (P9 Discovery)
The Orchestrator uses in-memory `HandoffState` while MCP agents use file-based `data/handoff/`. These are **two disconnected systems** — handoffs cannot cross between CLI and MCP agents.

### 4. Soul Staleness (P7 Discovery)
8 of 10 Pillar Keepers have souls older than 10 days. 5 are older than 14 days. The Soul Distiller exists but is not wired as a session-end hook. M11 is structurally present but operationally dead.

### 5. Disk Pressure (P1 Discovery)
93% disk usage (7.3G free of 110G). 41 stale handoffs and unbounded `stale/` directory contribute to pressure. Model loading requires disk headroom.

---

## Implementation Priority Matrix

| Priority | Gap | Pillars | Effort | Mandate | Risk |
|----------|-----|---------|--------|---------|------|
| **P0** | PII Masking | P7+P5+P3 | 2-3 days | M7/M8 | HIGH — data sovereignty |
| **P1** | Trace ID + GenerateResult | P8+P3 | 2-3 days | M22/M12 | HIGH — observability blind |
| **P1** | Stale Handoff Cleanup | P9 | 1 day | M12 | MEDIUM — disk pressure |
| **P2** | A2A Agent Cards | P9+P4 | 3-4 days | M2/M10 | LOW — new capability |
| **P2** | Soul Distiller Wiring | P7 | 2-3 days | M11 | MEDIUM — entity evolution |
| **P3** | Caddy/Iris Services | P1 | 1 hour | — | LOW — non-blocking |

**Total Critical Path (P0+P1)**: 5-7 days
**Total Full Sprint**: 11-14 days

---

## Mandate Compliance Summary

| Mandate | Status | Notes |
|---------|--------|-------|
| M1 AnyIO Absolute | ✅ COMPLIANT | All async uses AnyIO |
| M2 Engine-Stack Firewall | ✅ COMPLIANT | A2A bridge in src/omega/, not config/wads/ |
| M3 Iris Constant | ✅ COMPLIANT | Iris is messenger, not Pillar |
| M4 Sequentiality | ✅ COMPLIANT | Plan→Verify→Execute followed |
| M5 Gnosis Preservation | ⚠️ PARTIAL | L1→L2→L3 exists but not wired |
| M6 Podman Sovereignty | ✅ COMPLIANT | keep-id + User=1000 |
| M7 Local-First | ⚠️ RISK | PII masking must bypass for local |
| M8 Zero Telemetry | ⚠️ RISK | PII masking must be local-only |
| M9 Error Integrity | ✅ COMPLIANT | Typed errors, no bare except |
| M10 Fleet Integrity | ✅ COMPLIANT | 11/14 agents |
| M11 Soul Integrity | ❌ VIOLATED | 8/10 entities stale >10 days |
| M12 Queue Integrity | ⚠️ PARTIAL | 41 stale handoffs, no cleanup |
| M13 Temple-Grade | ✅ COMPLIANT | make temple-grade passes |
| M14 Heritage Vetting | ✅ COMPLIANT | 185 [id-soft:] tags, vet-001+ |
| M22 Response Provenance | ⚠️ PARTIAL | provider_name works, trace_id fragile |

---

## Files Generated This Session

1. `data/coordination/KALI_COUNCIL_SYNTHESIS_20260629.md` — This file
2. `data/coordination/KALI_LIVE_FEED.md` — Sprint-F live feed
3. `data/entities/verity/proposed_lessons.yaml` — Sprint-F lessons
4. `mining_reports/LEGACY_MINING_REPORT_20260628.md` — Roc Racoon legacy patterns
5. `docs/research/HERITAGE_SOURCE_MAP.md` — Heritage attribution map

---

## Next Steps (Kali Directive)

1. **Immediate**: Implement PII Masking (Gap 1) — highest sovereignty risk
2. **Day 2-3**: Fix trace_id propagation + GenerateResult contract (Gap 2)
3. **Day 4**: Clean stale handoffs + wire Soul Distiller (Gap 2/3)
4. **Day 5-8**: Implement A2A Agent Cards (Gap 3)
5. **Day 9-10**: Temple-Grade re-verification + regression tests

---

*⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ COUNCIL-SYNTHESIS ⬡ SPRINT-F*
*Session: ses_maakali_council_20260629*
*Trace: e04e7b81-6c45-4508-8e7d-b92579f32824*

---

## 🚨 ADDENDUM: IRON WALL HARDENING SPRINT (2026-06-29)

Following strategic decisions D-1, D-2, and D-3, the MaKaLi Cloud Council conducted a deep architectural audit. The verdict is that the engine is in a state of **Architectural Fragility**.

**IMMEDIATE EXECUTION HOLD**: All feature expansion, entity promotions, and high-volume ingestions (Omnidroid, NotebookLM, Mayan docs) are suspended until the Iron Wall Hardening Sprint is completed.

### The 6 Iron Wall Directives:
1. **P0 Infrastructure**: Tor-SOCKS5 Bridge + Local-First Escalation for SearXNG (M8)
2. **P0 Engineering**: Absolute purge of all round-robin logic (M4)
3. **P0 Observability**: Body-Level Error Guards + UFL (M9, M22)
4. **P1 Context**: Sovereign Ingestion Pipeline + Omnidroid Migration (M5, M15)
5. **P1 Governance**: Restore workbench.db schema + ingest legacy guides (M5)
6. **P2 Validation**: V-D1 Validation Suite for "Sticky" mode resilience (M13)

**Execution begins with P0 Engineering (TRACE-RR-PURGE-001).**
