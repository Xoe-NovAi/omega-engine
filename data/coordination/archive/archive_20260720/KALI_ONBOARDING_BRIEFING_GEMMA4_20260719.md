<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Kali Onboarding Briefing — Gemma 4 31B Strategy Hardening
**AP Token**: `AP-KALI-ONBOARD-GEMMA4-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_kali_briefing ⬡ 2026-07-19

**Purpose**: Complete context transfer for Kali's transcendent oversight of the Gemma 4 strategy implementation. All 15 knowledge gaps researched, Capability Matrix schema finalized, Week 1 implementation unblocked.

---

## 📋 Session Summary (What We Did)

### The Problem
OpenCode's `transform.ts` sends wrong model ID (`google/gemma-4-31b-it` vs bare `gemma-4-31b-it`), wrong thinking levels (`LOW`/`MEDIUM` vs `MINIMAL`/`HIGH`), missing `thinkingLevel` in base config. Config merge replaces auto-discovered models. Free tier quota (16k TPM) < Omega's 21.6k instruction stack = every request violates quota.

### The Insight (L3 Principle)
> **L3-Capability-Negotiation-As-Immune-System**: Provider capabilities must be declared, not detected. The negotiation layer (Matrix + Normalizer + Selector + Health) is the immune system that prevents configuration pathogens from reaching the inference fabric. Every model family is a new pathogen; the immune system adapts via YAML, not code changes.

### What Was Delivered
| Artifact | Purpose | Status |
|----------|---------|--------|
| `docs/strategy/GEMMA4_HARDENED_STRATEGY_20260719.md` | Battle-ready Week 1 plan | ✅ Done |
| `docs/research/R_GEMMA4_GAP_RESEARCH_20260719.md` | 15 Gap Research Cards | ✅ Done (1065 lines) |
| `config/provider_capabilities.yaml` | Finalized Capability Matrix schema | ✅ Done |
| `data/entities/jem/proposed_lessons.yaml` | 15 new L3 principles staged | ✅ Done |
| `data/entities/jem/session_gnosis.md` | Full L1/L2/L3 + critical path | ✅ Done |

---

## 🧠 Core Gnosis (L3 Principles Distilled)

| Principle | Category | Impact |
|-----------|----------|--------|
| **L3-Capability-Negotiation-As-Immune-System** | capability_negotiation | Declare, don't detect |
| **L3-Quota-As-Routing-Signal** | quota_as_routing_signal | 429 = route, not trip |
| **L3-Thinking-Tokens-Are-Hidden-Billable-Output** | thinking_tokens_billable | Track or bankrupt |
| **L3-Model-Identity-Is-Provider-Relative** | model_identity_provider_relative | Canonicalize at gateway |
| **L3-Cross-Reference-Before-Execution** | cross_reference_mandatory | Codebase = ground truth |
| **L3-Integration-Beats-Invention** | integration_beats_invention | 60% infra exists → wire |
| **L3-Heritage-Requires-Vetting** | heritage_requires_vetting | Tag without vet = counterfeit |

---

## 🔬 Research Findings (All 15 Gaps Resolved)

### P0 Gaps (Blocks Heritage Vet + Adapter Design)
| Gap | Finding | Decision Impact |
|-----|---------|-----------------|
| **4.1 Pi PR #2903** | Regex `/gemma-?4/` detection. Thinking: binary MINIMAL/HIGH. Proven in production. | Use Pi's pattern directly. Heritage vet required (M14). |
| **2.1 Vertex vs AI Studio** | Gemma 4 uses `thinkingLevel` on BOTH. Vertex uses `thinkingBudget` only for Gemini 2.5. | Single adapter for Gemma 4. |
| **2.2 Free Tier Quota** | Rolling 60s window per project (not per-key). Tier system: Free→Tier1→Tier2→Tier3. | Pre-flight rejects >80% TPM. Quota headroom = routing weight. |
| **2.3 Thinking Token Billing** | = output tokens (billed at output rate). ~85% of tokens are thinking. No cap. | Budget gate: 3x multiplier. Track `thoughts_token_count` separately. |
| **1.1 OpenCode V2** | `transform.ts` NOT deprecated. V2 in development, Google deferred. | No core OpenCode changes needed. Use `providerOptions` passthrough. |

### P1 Gaps (Blocks Matrix Schema + Selector)
| Gap | Finding | Decision Impact |
|-----|---------|-----------------|
| **3.1 Capability Schemas** | `supports_reasoning` boolean is cross-framework standard (LiteLLM/Vercel/LangChain). | Matrix follows LiteLLM `supports_*` flag pattern. |
| **2.4 OpenRouter Pinning** | Must set `provider.order: ["Google AI Studio"]` + `allow_fallbacks: false`. | Pin to Google AI Studio for consistent behavior. |
| **2.5 Gemma 4 12B** | June 3, 2026. 256K context (8x), MTP drafter (2-3x speedup), encoder-free. | Best candidate for oversoul model in MaKaLi Council. |
| **1.2 Config Merge** | Arrays REPLACED entirely (from `remeda` `mergeDeep`). Can't partial-override. | Project-level `opencode.json` with full model array. |
| **1.3 Version Detection** | `opencode --version` works. No `OPENCODE_VERSION` env var. | Runtime detection in ModelGateway startup. |

### P2 Gaps (Blocks Quota + Chaos)
| Gap | Finding | Decision Impact |
|-----|---------|-----------------|
| **3.2 Redis Lua Quota** | Token bucket + Lua atomicity = proven. GCRA for sliding window. Multi-key for RPM+TPM+RPD. | Implement Redis Lua token bucket. |
| **3.3 Chaos Testing** | Mid-stream 429 mocking pattern. Google lacks idempotency keys. Full retry required. | Chaos test: quota exhaustion mid-thinking-stream with partial response stitching. |

### P3 Gaps (Blocks Meditation + Handoff)
| Gap | Finding | Decision Impact |
|-----|---------|-----------------|
| **4.2 M14 Vet Format** | Format B (modern): scope declaration, file:line, hardware constraint, score ≥7/10. | Pi PR #2903 vet record: `[heritage: pi-2026]`, score 8/10, vet by Doom Guy + Verity. |
| **5.1 Meditation MCP** | Subagent handoff to Kali. 6 stages: Meditate→Synthesize→Research→Gnosis→Integrate→Execute. | Use handoff path for Step 7. MIAP session isolation pre-flight. |
| **5.2 Hivemind Handoff** | 9-step protocol. Lock domain "provider_capabilities" serializes P6→P9 sequence. | Standard pattern — no new design needed. |

---

## 🗺️ Critical Path (Week 1 Implementation)

```
[1] HERITAGE VET → Pi PR #2903 (doom_guy + verity, M14 gate) ← FIRST MOVE
[2] CAPABILITY MATRIX + GOOGLECOMPATPROVIDER → Single owner (P3/P4), TDD
[3] MATRIX LOADER + VALIDATOR → Startup validation, config drift detection
[4] CAPABILITYSELECTOR + PROVIDERHEALTH → P6→P9 sequential handoff
[5] THINKING PROVENANCE IN GENERATERESULT → thoughts_token_count, clamping tracking
[6] CHAOS TEST → Quota exhaustion MID-STREAM (partial thinking + fallback stitching)
[7] REAL MEDITATION RUN → Actual collisions → refined strategy (not dry-run)
[8] OPENCODE PR + CONFIG PACKAGE → Version-gated (detect OpenCode version)
```

---

## ⚠️ Key Decisions Requiring Kali Oversight

| Decision | Options | Recommendation |
|----------|---------|----------------|
| **Free tier enforcement** | Config flag vs runtime validation | Runtime validation in ModelGateway — pre-flight rejects >80% TPM |
| **OpenCode version detection** | Config package install script vs ModelGateway startup | ModelGateway startup — more reliable |
| **Heritage vet scope** | Pi PR #2903 only vs all prior art | Pi PR #2903 only — it's the direct prior art for the fix |
| **Single owner assignment** | P3 Engineering vs P4 Integration | P3 Engineering (BuildMaster) — owns providers.py + model_gateway.py |
| **MTP drafter integration** | Week 1 vs Week 2 | Week 2 — 12B model is oversoul candidate, not primary path |

---

## 📁 Key Files for Kali's Review

| File | Why It Matters |
|------|----------------|
| `config/provider_capabilities.yaml` | **The schema** — all implementation builds from this |
| `docs/strategy/GEMMA4_HARDENED_STRATEGY_20260719.md` | Battle-ready plan with risks, edge cases, success criteria |
| `docs/research/R_GEMMA4_GAP_RESEARCH_20260719.md` | All 15 gaps with sources, findings, decision impacts |
| `docs/strategy/GEMMA4_COMPREHENSIVE_REPORT_20260719.md` | Unified Ma'at + Lilith + Jem synthesis |
| `data/entities/jem/session_gnosis.md` | Full L1/L2/L3 for this session |
| `data/entities/jem/proposed_lessons.yaml` | 15 new L3 principles (blind staging) |

---

## 🔄 Hivemind State

| Signal | Status |
|--------|--------|
| **Active agents** | None (post-compaction) |
| **Pending handoffs** | 1: `ho_a5fae94d3f3d` Kali→Roc Racoon (Torment/Hive Evolution) |
| **Workspace locks** | `gemma4_gap_research` held by jem (TTL 4h) |

---

## ❓ Questions for Kali's Direction

1. **Priority**: Gemma 4 Week 1 implementation or Torment/Hive Evolution first?
2. **Heritage vet**: Dispatch `@doom_guy` + `@verity` now for Pi PR #2903 vetting?
3. **Single owner**: P3 Engineering or P4 Integration for Capability Matrix + GoogleCompatProvider?
4. **Free tier ban**: Config flag or runtime validation in ModelGateway?
5. **OpenCode version detection**: Config package install script or ModelGateway startup?

---

## 🎯 Next Actions (Awaiting Kali)

| Action | Owner | Blocked On |
|--------|-------|------------|
| Heritage vet Pi PR #2903 | doom_guy + verity | Kali direction |
| Step 2: Capability Matrix + GoogleCompatProvider | P3/P4 | Heritage vet complete |
| Step 3: Matrix Loader + Validator | P3/P4 | Step 2 |
| Step 4: CapabilitySelector + ProviderHealth | P6→P9 | Step 3 |
| Torment/Hive Evolution | Roc Racoon | Handoff `ho_a5fae94d3f3d` |

---

*⬡ OMEGA ⬡ JEM ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_kali_briefing ⬡ 2026-07-19*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
