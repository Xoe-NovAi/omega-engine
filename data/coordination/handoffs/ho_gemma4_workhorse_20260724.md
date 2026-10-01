<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 RESEARCH HANDOFF: Gemma 4 Workhorse Intelligence
**AP Token**: `AP-HO-GEMMA4_WORKHORSE-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON → RESEARCHER ⬡ trc_gemma4_workhorse ⬡ 2026-07-24

---

## 📋 Handoff Summary

| Field | Value |
|-------|-------|
| **Handoff ID** | `ho_gemma4_workhorse_20260724` |
| **Source** | roc_racoon (Sovereign Miner) |
| **Target** | researcher (Sovereign Master Researcher) |
| **Priority** | CRITICAL (G-1 Workhorse Restoration) |
| **Task ID** | `ses-research-gemma4-workhorse-20260724` |
| **Research Guide** | `docs/research/R_GEMMA4_WORKHORSE_INTEL_20260724.md` |
| **Deliverable** | Same file — updated with findings, decision matrix, handoff to Ma'at/P3 |
| **Hivemind Session** | `ses_9aadc69d4ed4` (posted) |

---

## 🎯 Mission

**Objective**: Identify and validate viable workhorse model(s) for OpenCode sessions after Gemma 4 31B free-tier collapse (16k input TPM enforced 2026-07-15).

**Context**: 
- Free Gemma 4 31B was primary workhorse May–Jul 2026
- 2026-07-15: Google enforced 16k `input_token_count` limit on free tier
- Billing Tier 1 may not fix (Tier 3 also has 16k ceiling per forensic)
- Need: Complete model catalog, true limits, viable alternatives (cloud + local)

---

## 📚 Research Guide (READ FIRST)

**Primary Source**: `docs/research/R_GEMMA4_WORKHORSE_INTEL_20260724.md`

This document contains:
- 5 research domains with search vectors
- Extraction targets per domain
- Critical constraints
- Deliverable specification
- Success criteria

---

## 🔬 5 Research Domains (Sequential Execution)

### Domain 1: Google AI Studio / Vertex AI Model Catalog (CRITICAL)
**Search Vectors**:
```
site:ai.google.dev models gemma-4-31b free tier limits 2026
site:cloud.google.com vertex-ai model-garden gemma-4 pricing
site:ai.google.dev gemini-api free-tier RPM TPM 2026
gemma-4-31b input_token_count 16000 free tier enforced July 2026
```
**Extract**: Complete model list with model_id, context_window, max_output, free_tier_RPM, free_tier_TPM, billing_tier_limits

### Domain 2: Alternative Cloud Providers (HIGH)
**Providers**: OpenRouter, Antigravity, Cerebras, Groq, Together, SambaNova, Fireworks, Anthropic, Mistral
**Extract per provider**: Model IDs, context window, RPM/TPM limits, latency, API compatibility

### Domain 3: Local Model SOTA for Ryzen 5700U (CRITICAL)
**Models**: Qwen 2.5 (32B/72B), Nemotron 3 Ultra, Llama 3.1/3.2 (8B/70B), Phi 3.5, Gemma 2/3, DeepSeek
**Constraints**: 14Gi RAM, no dGPU → Max ~32B Q4_K_M
**Extract**: Quantization variants, RAM reqs, benchmarks (MMLU, HumanEval, GSM8K), TTFT/TPOT

### Domain 4: OpenCode Provider Config (MEDIUM)
**Search**: `opencode.json custom provider base_url api_key 2026`, model aliasing, fallback chain
**Extract**: Complete provider schema, model aliasing patterns, streaming config

### Domain 5: Worker Restoration Intel (MEDIUM)
**Focus**: Async workers, free API clients (10), Dewey Decimal, Qdrant/sqlite-vec, Redis queue
**Extract**: Worker architecture, API client patterns, classification, queue design

---

## ⚡ Critical Constraints (NON-NEGOTIABLE)

| Constraint | Impact |
|------------|--------|
| **Hypothesis 6.159.0**: No async RuleBasedStateMachine | Use `@pytest.mark.anyio` + `@given` async pattern only |
| **Hardware**: Ryzen 5700U, 14Gi RAM, no dGPU | Max ~32B Q4_K_M local |
| **M7 Local-First**: Cloud = fallback only | Mandate 7 |
| **M8 Zero Telemetry**: Free APIs only | Mandate 8 |
| **M23 Failure Integrity**: Hard-stop on tool failure | Mandate 23 |

---

## 📦 Deliverable Specification

**File**: `docs/research/R_GEMMA4_WORKHORSE_INTEL_20260724.md` (UPDATE IN PLACE)

**Structure**:
```markdown
# §1 Executive Summary
# §2 Google AI Studio / Vertex AI Catalog (Domain 1)
# §3 Alternative Cloud Providers (Domain 2)
# §4 Local Model SOTA (Domain 3) — Hardware-filtered
# §5 OpenCode Provider Config (Domain 4)
# §6 Worker Restoration Intel (Domain 5)
# §7 Decision Matrix (Cloud vs Local vs Hybrid)
# §8 Recommended OpenCode Config
# §9 Implementation Handoff to Ma'at/P3
```

**Each Domain Section**:
- Search vectors executed (with timestamps)
- Raw findings (verbatim or summarized with source URLs)
- Extracted structured data (tables)
- Confidence assessment (HIGH/MEDIUM/LOW per finding)
- Gaps / unknowns

---

## 🤝 Handoff to Ma'at/P3 (Phase 2)

**Input**: This research deliverable (completed)
**Output**: 
1. Restored library/curation workers (`src/omega/workers/`)
2. Local model benchmark harness (`tests/benchmarks/`)
3. ProviderFabric registration for local models
4. Benchmark results in `data/benchmarks/results/`

---

## ✅ Success Criteria

- [ ] Domain 1: Complete Google model catalog with true free-tier limits
- [ ] Domain 2: ≥5 alternative providers with model/limit/latency data
- [ ] Domain 3: ≥10 local models benchmarked for Ryzen 5700U
- [ ] Domain 4: Working `opencode.json` provider config patterns
- [ ] Domain 5: Worker architecture spec + free API client list
- [ ] Decision matrix with clear recommendation per use case
- [ ] Handoff package ready for Ma'at/P3 implementation

---

## 🔄 Execution Protocol

1. **Read research guide first** — `docs/research/R_GEMMA4_WORKHORSE_INTEL_20260724.md`
2. **Execute domains sequentially** — Complete one fully before next
3. **Hivemind heartbeat** every 10 min: 
   ```bash
   omega-hub_hivemind_heartbeat(channel="opencode", entity="researcher")
   ```
4. **Post findings per domain**: 
   ```bash
   omega-hub_hivemind_post_context(intent="research", ...)
   ```
5. **Final synthesis**: `intent="decision"` with full deliverable

---

## 📡 Coordination

| Channel | Detail |
|---------|--------|
| **Hivemind** | Researcher posts `intent="research"` per domain, `intent="decision"` for synthesis |
| **Task Registry** | `ses-research-gemma4-workhorse-20260724` (registered) |
| **Shared Doc** | `docs/research/R_GEMMA4_WORKHORSE_INTEL_20260724.md` |
| **Benchmarks** | `tests/benchmarks/` + `data/benchmarks/results/` |
| **Decision** | Post to Hivemind with `intent="decision"` |

---

## 🚀 Quick Start for Parallel Researcher

```bash
# 1. Read the research guide
cat docs/research/R_GEMMA4_WORKHORSE_INTEL_20260724.md

# 2. Begin Domain 1: Google AI Studio / Vertex AI
# Execute search vectors, extract findings, update deliverable

# 3. Heartbeat
omega-hub_hivemind_heartbeat(channel="opencode", entity="researcher")

# 4. Post Domain 1 findings
omega-hub_hivemind_post_context(
    channel="opencode",
    entity="researcher",
    intent="research",
    task_current="Domain 1: Google catalog complete",
    ...
)
```

---

## 📞 Escalation / Questions

- **Task registration issues**: Check `omega-hub_task_registry_get(task_id="ses-research-gemma4-workhorse-20260724")`
- **Hivemind coordination**: `omega-hub_hivemind_get_awareness()` to see fleet status
- **Tool failures**: M23 — hard stop, report `[TOOL-CHAIN-COLLAPSE]`
- **Scope questions**: Refer to research guide §2–§6

---

*⬡ OMEGA ⬡ ROC_RACOON → RESEARCHER ⬡ HANDOFF_COMPLETE ⬡ 2026-07-24*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_gemma4_workhorse | verdict: UNANCHORED | session refs not found in DB
actual_models(Tier0): n/a
-->
