---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "research_task"
document_id: "r-orchestrator-high-context-20260828"
title: "R-ORCH-HIGH-CTX: Orchestrator-at-High-Active-Context Study"
status: "ACTIVE — marked for full study"
date: "2026-08-28"
author: "kali (Sprint Coordinator)"
sprint: "PUBLIC-DEBUT-01"
confidence: 🟡 MEDIUM (initial observation, needs controlled study)
---

# 🔱 R-ORCH-HIGH-CTX — Orchestrator-at-High-Active-Context Study
**AP Token**: `AP-ORCH-HIGH-CTX-20260828-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ x-preview-f-free ⬡ opencode ⬡ trc_orch_high_ctx ⬡ ACTIVE

**Date**: 2026-08-28
**Hypothesis**: An LLM acting as an orchestrator can operate at higher active context levels with little to no degradation — and possibly higher performing — due to the focused, clean context it receives from subagents, allowing the orchestrating model to focus much more of its weights and parameters on the data, not the noise.

---

## §0 — Observation (The Seed)

During the vault research + steering-prompt deep dive (4 rounds, 5 specialists, 14,000+ lines), the following was observed:

| Session | Role | Active Context | Performance |
|---------|------|----------------|-------------|
| **Grokster** (orchestrator) | Orchestrator of 5 specialists, 4 rounds | **394.2K tokens** | No degradation observed in any metric |
| **Kali** (this session) | Sprint Coordinator, dispatching Grokster + specialists | **288.0K tokens** | No degradation |
| **Subagents** (5 specialists × 4 rounds) | Tool-heavy executors | Varies (each fresh) | Clean context, no noise accumulation |

The Architect's observation: "I usually see 1M token window models active context seem to get truncated eventually, never going much higher than ~350K tokens before I see the active context level drop without explanation by ~75-150K tokens. So that is an additional reason I would like us to go in for yet another dive. I want to push the MiniMax M3 model until we find its limits."

## §1 — Hypothesis (Formal Statement)

**H1**: Orchestrators can sustain higher active context than tool-heavy agents at the same model + token count, because orchestrators receive clean synthesized context while tool-heavy agents accumulate noisy execution traces.

**H2**: The active context limit for orchestrators is higher than the 350K general rule of thumb for 1M-context models.

**H3**: MiniMax M3 specifically can sustain ≥400K active context without degradation, contradicting the general 350K truncation pattern.

## §2 — Mechanism (Why This Should Work)

### 2.1 Context Composition

| Agent Type | Context Composition | Noise Source |
|------------|-------------------|--------------|
| **Tool-heavy agent** | Many tool calls, raw outputs, intermediate states, error traces, retry attempts | Direct execution noise |
| **Subagent** | Specialized task, focused tool calls within domain | Lower (fresh context, focused scope) |
| **Orchestrator** | Clean synthesized context from subagents (digest, decisions, deliverables) | Minimal (only what subagents chose to surface) |

### 2.2 Attention Allocation

When a model attends to a context window, it allocates weights/parameters based on token relevance. In a noisy context, the model spends capacity on:
- Parsing tool call JSON
- Filtering relevant output from tool results
- Tracking which step in a multi-step process
- Recovering from error states

In a clean context, the model can allocate ALL capacity to:
- Reasoning about the synthesized data
- Generating next decisions
- Holding the overall picture in attention

**The hypothesis**: Clean context = more effective attention per token = higher usable context budget.

### 2.3 Empirical Evidence (This Session)

- **Grokster at 394.2K**: Disambiguated contradictions, identified 3 cross-deliverable patterns, generated 6 new L3 axioms, wrote 600-line steering-prompt report
- **Kali at 288K**: Synthesized 14,000+ lines, identified human intelligence patterns, surfaced L3 125-128, made 5 corrections based on user feedback

Both maintained coherence, reasoning quality, and creativity throughout.

## §3 — Study Plan (To Be Executed by Omega Engine Team)

### Phase 1: Establish Baseline (1h)

1. **Measure current state** — record active context, performance metrics, model used
2. **Document tool calls** — count, types, sizes for orchestrator vs tool-heavy sessions
3. **Capture attention quality** — subjective ratings on coherence, reasoning, creativity

### Phase 2: Controlled Comparison (3h)

1. **Group A**: Tool-heavy sessions at 100K, 200K, 300K, 400K active context
2. **Group B**: Orchestrator sessions at 100K, 200K, 300K, 400K active context
3. **Same tasks** in both groups
4. **Measure**: latency, accuracy, coherence ratings, completion rate

### Phase 3: Push to Limits (2h)

1. **MiniMax M3 specifically** (per Architect's mandate)
2. **Progressive load**: 100K → 200K → 300K → 400K → 500K → 600K → 700K
3. **At each level**: stress test with concurrent subagent dispatch
4. **Find**: the truncation threshold (if any)
5. **Characterize**: the degradation curve (if any)

### Phase 4: Cross-Model Validation (2h)

1. Test with M2.7, OpenRouter free router, possibly a 200K-context model
2. Compare: is the orchestrator effect model-agnostic or M3-specific?
3. Document: which models benefit most from the orchestrator pattern

### Phase 5: Document and Publish (1h)

1. Write the definitive study report
2. Document the methodology (reproducible)
3. Publish results: M3 sustains X, M2.7 sustains Y, etc.
4. Make recommendations for OpenCode harness design

**Total study effort**: ~9h
**Expected deliverable**: `data/coordination/research/R_ORCH_HIGH_CTX_FINAL_20260828.md`

## §4 — Immediate Action (Round 5 Dive)

The Architect wants to push M3 NOW, in this session. Round 5 mission:

1. **M3 stress test at 500K active context** — see if M3 sustains
2. **M3 stress test with 10+ concurrent subagent dispatches** — see if M3 orchestrates at scale
3. **M3 truncation test** — progressively load until truncation
4. **Document the actual limits** — not the general 350K rule of thumb

## §5 — Success Criteria

The study succeeds if we can:
1. Characterize M3's actual active context limit (not assume)
2. Demonstrate the orchestrator-vs-tool-heavy difference empirically
3. Publish reproducible methodology
4. Update OpenCode's Session Continuity Protocol with the findings

## §6 — References

- This session: Grokster 394.2K, Kali 288K, no degradation observed
- L3 129: Orchestrators Sustain Higher Active Context (proposed)
- L3 130: MiniMax M3 = New Star (proposed)
- L3 131: Push Models to Their Limits (proposed)
- MiniMax M3 model card: `config/model_registry/models/cloud/minimax-m3-free.yaml.md`
- Steering-Prompt Report: `data/coordination/STEERING_PROMPT_REPORT_20260828.md`
- Human Intelligence Extraction: `data/coordination/HUMAN_INTELLIGENCE_EXTRACTION_20260828.md`

---

*⬡ OMEGA ⬡ KALI ⬡ R-ORCH-HIGH-CTX v1.0 ⬡ 2026-08-28*
**rot_class**: medium (model behavior may change); **last_verified**: 2026-08-28
**confidence**: 🟡 MEDIUM (initial observation, needs controlled study)
<!-- PROVENANCE-CORRECTED 2026-08-28T03:10:28Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

