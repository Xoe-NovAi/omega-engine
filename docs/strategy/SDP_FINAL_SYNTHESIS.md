# 🔱 Sovereign Distillation Pipeline — Final Synthesis
## The Complete Architecture for Cloud+Local Cognitive Orchestration

**AP Token:** `AP-SDP-FINAL-SYNTHESIS-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ STRATEGY ⬡ FINAL-SYNTHESIS

**Date:** 2026-08-09
**Status:** CANONICAL — Master Reference Document
**Authors:** The Architect, Gemini 3.1 Pro, Claude Sonnet 4.6, Nemotron 3 Ultra, Laguna S 2.1, Roc Racoon, Researcher, John Carmack

---

## §1 Executive Summary

The **Sovereign Distillation Pipeline (SDP)** is a tripartite cognitive architecture that separates I/O, Synthesis, and Execution into distinct phases, routed to the models best suited for them. It evolved from 18 months of manual multi-model orchestration into a formally specified, hardware-aware, mathematically routable system.

**Key Insight:** The SDP is ~60% already built. The Omega Engine has been evolving toward this architecture since its inception. What's missing is correct data, correct queries, and correct wiring — not new subsystems.

**Key Correction:** Model context windows vary by free vs paid tiers of the same model name by up to 4×. The gauge must be keyed on model+tier, not model name alone.

---

## §2 Verified Model Context Windows (Ground Truth)

*From the Architect's personal experience, verified against live sessions.*

| Model | Context Window | Tier | Pool Type | Notes |
|---|---|---|---|---|
| **Nemotron 3 Ultra** | **1,000,000** | 4 | Daily (OCZ) | Primary scaffold for large context |
| **Laguna S 2.1 (free)** | **262,144** | 3 | Daily (OCZ/OR) | Best agentic scaffold per benchmark |
| **Laguna S 2.1 (paid)** | **1,048,576** | 4 | Daily (OCZ) | 4× free tier |
| **Longcat 2.0 (free)** | **1,000,000** | 4 | Daily (OCZ) | Free 1M context |
| **Nemotron 3 Super** | **262,144** | 3 | Daily (OCZ) | Mid-tier scaffold |
| **Gemini 3.1 Pro** | **1,048,576** | 4 | Weekly (AGY) | Primary AGY synthesizer |
| **Claude Sonnet 4.6** | **200,000** | 2 | Weekly (AGY) | Constitutional review, compliance |
| **Claude Opus 4.6** | **200,000** | 2 | Weekly (AGY) | Deepest code reasoning |
| **Gemini 3.6 Flash** | **1,000,000** | 4 | Weekly (AGY) | Fast AGY synthesis |
| **Qwen3-1.7B (local)** | 32,768 | 1 | Local (free) | Iris speculative decode, execution |
| **Llama-3.1-8B (local)** | 32,768–131,072 | 1 | Local (free) | Local executor |

**Critical Rule:** Free vs paid tiers of the *same model name* differ by up to 4×. The gauge must be keyed on model+tier, not model name alone.

---

## §3 The Three Phases (Formal Definition)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                SOVEREIGN DISTILLATION PIPELINE                          │
│                                                                         │
│  PHASE 1: SCAFFOLD          PHASE 2: SYNTHESIZE   PHASE 3: EXECUTE     │
│  ─────────────────          ─────────────────────  ───────────────      │
│  Cheap/Daily Model          AGY Frontier Model     Local/Cheap Model    │
│  • File reads               • Zero tool calls      • Follows RHP exactly│
│  • Grep / bash              • Pure reasoning        • Verifiable        │
│  • Context building         • Plan production      • Atomic steps       │
│  • Research synthesis       • L3 distillation      • No ambiguity       │
│  • Cross-model priming      • Schema output        • git apply + test   │
│                             ↑                                           │
│                    Switch happens HERE                                  │
│                    (before 80% Redzone)                                 │
└─────────────────────────────────────────────────────────────────────────┘
```

### Phase 1: Scaffold (I/O & Priming)
- **Models:** Nemotron 3 Ultra (1M), Laguna S 2.1 (262K), Longcat 2.0 (1M), Nemotron 3 Super (262K)
- **Pool:** Daily refresh (OpenCode Zen, OpenRouter)
- **Role:** Read files, run grep, build context, synthesize research, prime the context window
- **Exit Condition:** Context reaches 80% Redzone OR context is fully primed

### Phase 2: Synthesize (Frontier Intelligence)
- **Models:** Gemini 3.1 Pro (1M), Claude Sonnet 4.6 (200K), Claude Opus 4.6 (200K), Gemini 3.6 Flash (1M)
- **Pool:** Weekly (8 Google AGY accounts)
- **Role:** Pure reasoning over primed context. Zero tool calls. Produces structured Refactoring Manual.
- **Output:** Executable artifacts (unified diffs, exact commands) — NOT prose

### Phase 3: Execute (Mechanical Application)
- **Models:** Qwen3-1.7B, Llama-3.1-8B (local GGUF)
- **Pool:** Local (free, unlimited)
- **Role:** Execute the Refactoring Manual mechanically. `git apply` + `make test` + classify result.
- **Key Insight:** qwen3-1.7b has 0.65 quality but **0.954 factuality** — excellent verifier, catastrophic author.

---

## §4 Ground Truth: What Actually Exists

*Verified by reading actual code, not trusting specs.*

### ✅ Already Built (Don't Build — Wire It)

| Component | Location | LOC | Status | Action |
|---|---|---|---|---|
| **V-1 Vault** | `src/omega/vault/` | 2,039 | Complete | Import and wire |
| **Pool Tracker** | `pool_tracker.py` | 237 | Complete, dead code | Import and wire |
| **Dialectic Logger** | `dpo_logger.py` | — | `record_council()` exists | Extend schema |
| **Triage Router** | `triage_router.py` | — | Constraint filtering exists | Extend with SDP constraints |
| **Token Estimator** | `token_estimator.py` | — | tiktoken×1.3 SSOT | Use it (don't duplicate) |

### ❌ Missing (Build These)

| Component | Est. | Notes |
|---|---|---|
| **Context Gauge** | 4h | Use `tokens.total` from `message.data` JSON |
| **RHP (Recovery Halt Point)** | 2h | Rename from SSP to avoid M20 collision |
| **3 MCP Tools** | 4h | `get_context_pressure`, `write_rhp`, `request_agy_escalation` |

### ⚠️ Partially Built (Extend These)

| Component | Location | What's Missing |
|---|---|---|
| **config/models.yaml** | `config/models.yaml` | No cloud model entries, no tier/is_agy fields |
| **config/providers.yaml** | `config/providers.yaml` | Some windows wrong (Gemini 3.1 Pro listed as 2M) |
| **DPORecorder** | `dpo_logger.py` | Needs dialectic schema extension |

---

## §5 Critical Blockers (Must Fix Before Implementation)

| # | Blocker | Impact | Fix |
|---|---|---|---|
| **G-3** | No `tokens` column in `message` table | Code crashes on line 1 | Tokens live inside `data` JSON blob |
| **G-4** | Token accounting is **not additive** | Summing overcounts **~87×** (verified: session.tokens_input=22M vs latest message tokens.total=253K) | True load = `tokens.total` of **latest** assistant message (NOT session.tokens_input) |
| **§4** | 4 of 5 cloud windows wrong | Gauge reports wrong percentages | Use verified windows from §2 |

---

## §6 Quick Win Items (This Sprint)

*Ordered by leverage (impact / effort)*

| # | Item | Est. | Leverage | Owner |
|---|---|---|---|---|
| **QW-1** | Fix model context windows in config | 1h | CRITICAL | N3 |
| **QW-2** | Rewrite Context Gauge to use `tokens.total` | 2h | CRITICAL | N3 |
| **QW-3** | Add CI guard against token counting bug | 30min | HIGH | N10 |
| **QW-4** | Import and wire `pool_tracker.py` | 2h | HIGH | N3 |
| **QW-5** | Add cloud entries to `config/models.yaml` | 1h | HIGH | N3 |
| **QW-6** | Extend `TriageRouter` with SDP constraints | 4h | MEDIUM | N3 |
| **QW-7** | Extend `DPORecorder` with dialectic schema | 3h | MEDIUM | N3 |
| **QW-8** | Build Context Gauge (greenfield) | 4h | MEDIUM | N3 |
| **QW-9** | Build RHP halt artifact (greenfield) | 2h | MEDIUM | N3 |
| **QW-10** | Build 3 MCP tools (greenfield) | 4h | MEDIUM | N3 |

**Total: ~24 hours** for complete Phase 1 Context Gauge with all sub-gauges.

---

## §7 Next Steps (When We Return)

### Immediate (First Session Back)
1. **Run QW-1 through QW-5** (~7 hours) — Fix the data layer
2. **Verify the Context Gauge** works on live sessions
3. **Test the 80% Redzone** trigger on Nemotron 3 Ultra (1M window)

### Short-Term (This Month)
1. **Extend TriageRouter** with SDP constraints (C₁–C₄)
2. **Wire pool_tracker.py** into the routing logic
3. **Build the RHP halt artifact** and test it triggers correctly
4. **Implement Content-Addressed Evidence Manifest** (attestation protocol)

### Medium-Term (Next Quarter)
1. **Build the Auto-Router** (wrapper around existing pool_tracker + TriageRouter)
2. **Implement Predictive Routing** (look at ACTIVE_SPRINT.json to anticipate pool usage)
3. **Build the Dialectic Intelligence Flywheel** (capture cross-model synthesis for training data)
4. **Implement Ensemble Routing** (gate to <15% of escalations)

### Long-Term (Vision)
1. **Sovereignty as a Service** — portable `.omega` export bundle
2. **Community WAD Marketplace** — distribute capability bundles
3. **Training Data Generation** — every SDP execution becomes a training row
4. **Local Model Distillation** — distill combined AGY intelligence into better local models

---

## §8 The Deeper Truth

**The SDP is not a future architecture — it is the Omega Engine's existing architecture, waiting to be activated.**

The vault, the router, the logger, the pool tracker — they all exist. What's missing is:
1. **Correct data** (fix model windows in config)
2. **Correct queries** (use `tokens.total` not sum)
3. **Correct wiring** (import `pool_tracker.py`, extend `TriageRouter`)
4. **Correct interfaces** (Context Gauge, RHP, MCP tools)

The Omega Engine has been evolving toward this tripartite architecture since February 2025. We are not inventing — we are **revealing and activating** what already exists.

---

## §9 Reference Documents

| Document | Path | Purpose |
|---|---|---|
| **Protocol** | `docs/strategy/COGNITIVE_SCAFFOLDING_PROTOCOL.md` | Manual operations |
| **Manifesto** | `docs/research/R_SOVEREIGN_DISTILLATION_PIPELINE_MANIFESTO_20260809.md` | Philosophy |
| **Blueprint** | `docs/strategy/SDP_AUTOMATION_BLUEPRINT.md` | Phased engineering plan |
| **Impl Spec** | `docs/strategy/SDP_IMPLEMENTATION_SPEC.md` | Technical contracts |
| **Hardware Horizon** | `docs/strategy/SDP_HARDWARE_HORIZON_SPEC.md` | KV cache, SomaticState, energy |
| **Formal Routing** | `docs/strategy/SDP_FORMAL_ROUTING_SPEC.md` | Z3 verified constraints |
| **Model-Aware Gauge** | `docs/strategy/SDP_MODEL_AWARE_GAUGE_SPEC.md` | Dynamic window detection |
| **Failure Analysis** | `docs/strategy/SDP_FAILURE_MODE_ANALYSIS.md` | Resilience engineering |
| **Mining Report** | `data/entities/roc_racoon/workspace/mining_reports/SDP_INTEGRATION_MINING_REPORT_20260809.md` | Foundational research |
| **Knowledge Gaps** | `data/entities/researcher/workspace/research_reports/SDP_KNOWLEDGE_GAP_RESEARCH_20260809.md` | Gap research |
| **Systems Sweep** | `data/entities/roc_racoon/workspace/mining_reports/SDP_SYSTEMS_SWEEP_REPORT_20260809.md` | Systems sweep |
| **Duplicate Audit** | `data/entities/roc_racoon/workspace/mining_reports/SDP_DUPLICATE_GAP_AUDIT_20260809.md` | Duplicate & gap audit |
| **Carmack Review** | `data/entities/john_carmack/workspace/reviews/SDP_CARMACK_REVIEW_20260809.md` | Brutal review |
| **Session Ledger** | `data/coordination/AGY_SESSION_LEDGER.md` | Pool tracking |
| **This Document** | `docs/strategy/SDP_FINAL_SYNTHESIS.md` | Master reference |

---

*⬡ OMEGA ⬡ KALI ⬡ SDP-FINAL-SYNTHESIS ⬡ v1.0.0 ⬡ 2026-08-09*
*Produced by Gemini 3.1 Pro (synthesis layer) with corrections from the Architect*